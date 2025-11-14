from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from dbconnect import Base
from employee import Employee

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # where file is stored on disk
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", backref="documents")
