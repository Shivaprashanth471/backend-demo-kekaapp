# from dbconnect import Base, engine
# from organizationmodels import Organization

# print("Creating database tables...")
# Base.metadata.create_all(bind=engine)
# print("✅ Tables created successfully")

from dbconnect import Base, engine
from organizationmodels import Organization
from employee import Employee

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Done!")
