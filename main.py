from fastapi import APIRouter, FastAPI
import feedback
from router import router
from dbconnect import Base, engine, create_tables
from organizationmodels import Organization
from employee import Employee
from attendance import Attendance
from feedback import Feedback
from document import Document



app=FastAPI(title = " KEKA Application ")


# ✅ Auto-create tables at startup
@app.on_event("startup")
def on_startup():
    print("Creating database tables...")
    create_tables()

app.include_router(router)
