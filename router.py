# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/ping")

# def getping():
#     return {"ping": "pong from shiva"}

from fastapi import APIRouter, Depends, HTTPException, params ,UploadFile, File
from sqlalchemy.orm import Session
from dbconnect import get_db
from organizationmodels import Organization
from employee import Employee
from attendance import Attendance
from datetime import datetime
from feedback import Feedback
import os
from document import Document

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # create folder if not exists

router = APIRouter()

@router.get("/ping")
def getping():
    return {"ping": "pong from shiva"}


# Create Organization
@router.post("/add/organizations")
def create_organization(org: dict, db: Session = Depends(get_db)):
    existing = db.query(Organization).filter(Organization.email == org.get("email")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this email already exists")

    new_org = Organization(
        name=org.get("name"),
        address=org.get("address"),
        email=org.get("email"),
        contact_number=org.get("contact_number")
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return {"message": "Organization created successfully", "data": {"id": new_org.id, "name": new_org.name}}


# List all Organizations
@router.get("/organizations")
def get_organizations(db: Session = Depends(get_db)):
    print("Fetching organizations...")
    orgs = db.query(Organization).all()
    return [{"id": o.id, "name": o.name, "email": o.email, "address": o.address} for o in orgs]


# ------------------ EMPLOYEE APIs ------------------
@router.post("/add/employees")
def create_employee(emp: dict, db: Session = Depends(get_db)):
    # Validate organization exists
    org = db.query(Organization).filter(Organization.id == emp.get("organization_id")).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check duplicate email
    existing = db.query(Employee).filter(Employee.email == emp.get("email")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    new_emp = Employee(
        name=emp.get("name"),
        email=emp.get("email"),
        designation=emp.get("designation"),
        organization_id=emp.get("organization_id")
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return {"message": "Employee created successfully", "data": {"id": new_emp.id, "name": new_emp.name}}


@router.get("/employees")
def get_employees(db: Session = Depends(get_db), organization_id: int = None, name: str = None):
    filter = []
    print("Fetching employees...", organization_id, "params")
    if organization_id:
        filter.append(Employee.organization_id == organization_id)
    if name:
        filter.append(Employee.name.ilike(f"%{name}%"))
    query =  db.query(Employee).filter(*filter)
    employees = query.all()
    return [
        {
            "id": e.id,
            "name": e.name,
            "email": e.email,
            "designation": e.designation,
            "organization_id": e.organization_id
        }
        for e in employees
    ]



# ------------------ ATTENDANCE APIs ------------------

@router.post("/attendance/checkin")
def employee_checkin(data: dict, db: Session = Depends(get_db)):
    emp_id = data.get("employee_id")

    # validate employee
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # check if already checked in and not checked out
    existing = (
        db.query(Attendance)
        .filter(Attendance.employee_id == emp_id, Attendance.check_out == None)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Employee already checked in and not checked out")

    record = Attendance(employee_id=emp_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": f"{emp.name} checked in at {record.check_in}"}


@router.post("/attendance/checkout")
def employee_checkout(data: dict, db: Session = Depends(get_db)):
    emp_id = data.get("employee_id")

    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # find today's open attendance record
    record = (
        db.query(Attendance)
        .filter(Attendance.employee_id == emp_id, Attendance.check_out == None)
        .first()
    )
    if not record:
        raise HTTPException(status_code=400, detail="No active check-in found")

    record.check_out = datetime.now()
    db.commit()
    db.refresh(record)
    return {"message": f"{emp.name} checked out at {record.check_out}"}


@router.get("/attendance")
def get_all_attendance(db: Session = Depends(get_db)):
    records = db.query(Attendance).all()
    return [
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "check_in": r.check_in,
            "check_out": r.check_out,
        }
        for r in records
    ]


@router.get("/attendance/{employee_id}")
def get_employee_attendance(employee_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter(Attendance.employee_id == employee_id).all()
    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found for this employee")
    return [
        {
            "id": r.id,
            "check_in": r.check_in,
            "check_out": r.check_out,
        }
        for r in records
    ]

# ------------------ GET ATTENDANCE HISTORY FOR EMPLOYEE ------------------
@router.get("/attendance/history/{employee_id}")
def attendance_history(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    records = db.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.check_in.desc()).all()
    return {
        "employee_id": emp.id,
        "employee_name": emp.name,
        "total_records": len(records),
        "attendance": [
            {
                "check_in": r.check_in,
                "check_out": r.check_out
            } for r in records
        ]
    }

# ------------------ FEEDBACK APIs ------------------

# Submit Feedback
@router.post("/feedback")
def submit_feedback(data: dict, db: Session = Depends(get_db)):
    emp_id = data.get("employee_id")
    rating = data.get("rating")
    comments = data.get("comments", "")

    # Validation
    if not emp_id or not rating:
        raise HTTPException(status_code=400, detail="employee_id and rating are required")
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    feedback = Feedback(employee_id=emp_id, rating=rating, comments=comments)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return {"message": "Feedback submitted successfully", "feedback_id": feedback.id}


# Get all feedbacks
@router.get("/feedback")
def get_all_feedback(db: Session = Depends(get_db)):
    feedbacks = db.query(Feedback).all()
    return [
        {
            "id": f.id,
            "employee_id": f.employee_id,
            "employee_name": f.employee.name,
            "rating": f.rating,
            "comments": f.comments,
            "created_at": f.created_at
        }
        for f in feedbacks
    ]


# Get feedback by employee
@router.get("/feedback/{employee_id}")
def get_feedback_by_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    feedbacks = db.query(Feedback).filter(Feedback.employee_id == employee_id).all()
    return [
        {
            "rating": f.rating,
            "comments": f.comments,
            "created_at": f.created_at
        }
        for f in feedbacks
    ]



UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # create folder if not exists

# ------------------ DOCUMENT UPLOAD ------------------
@router.post("/documents/upload")
def upload_document(employee_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # validate employee
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Save file to disk
    file_location = os.path.join(UPLOAD_FOLDER, f"{employee_id}_{file.filename}")
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # Save record in DB
    doc = Document(employee_id=employee_id, file_name=file.filename, file_path=file_location)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"message": "Document uploaded successfully", "document_id": doc.id}


# ------------------ LIST DOCUMENTS ------------------
@router.get("/documents/{employee_id}")
def get_documents(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    docs = db.query(Document).filter(Document.employee_id == employee_id).all()
    return [
        {
            "id": d.id,
            "file_name": d.file_name,
            "uploaded_at": d.uploaded_at
        }
        for d in docs
    ]


# ------------------ DOWNLOAD DOCUMENT ------------------
from fastapi.responses import FileResponse

@router.get("/documents/download/{doc_id}")
def download_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(path=doc.file_path, filename=doc.file_name)