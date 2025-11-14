from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from dbconnect import Base
from employee import Employee

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))  # who gave feedback
    rating = Column(Integer, nullable=False)  # 1 to 5
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", backref="feedbacks")
