from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from dbconnect import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    designation = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # relationship (optional, helps with joins)
    organization = relationship("Organization", backref="employees")
