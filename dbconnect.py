# import psycopg2

# try:
#     connection = psycopg2.connect(
#         dbname="mydb",
#         user="admin",
#         password="admin123",
#         host="localhost",
#         port="5432"
#     )
#     cursor = connection.cursor()
#     print("Database connection established.")
# except Exception as e:
#     print(f"An error occurred while connecting to the database: {e}")


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Step 4.1: Create connection string (like a website URL)
DATABASE_URL = "postgresql://admin:admin123@localhost:5432/mydb"
#               postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME

# Step 4.2: Create engine (this is the actual connection to database)
engine = create_engine(DATABASE_URL)

# Step 4.3: Create SessionLocal (this will help us talk to database in each request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Step 4.4: Create Base (all your database tables will inherit from this)
Base = declarative_base()

# Step 4.5: This function gives us a database session for each API request
def get_db():
    db = SessionLocal()  # Open connection
    try:
        yield db  # Use the connection
    finally:
        db.close()  # Always close connection when done

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
