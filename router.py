# from fastapi import APIRouter

# router = APIRouter()

# @router.get("/ping")

# def getping():
#     return {"ping": "pong from shiva"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dbconnect import get_db
from organizationmodels import Organization
from employee import Employee
from attendance import Attendance
from datetime import datetime

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
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
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
