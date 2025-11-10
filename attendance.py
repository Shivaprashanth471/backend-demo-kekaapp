from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from dbconnect import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    check_in = Column(DateTime, default=datetime.now)
    check_out = Column(DateTime, nullable=True)

    employee = relationship("Employee", backref="attendance_records")
