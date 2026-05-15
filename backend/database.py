import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# In production, use environment variables. For MVP, we default to a local Postgres instance.
# Format: postgresql://<username>:<password>@<host>:<port>/<db_name>
DATABASE_URL = "postgresql://sarveshsharma@localhost:5432/gradeops"
# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False, # Set to True to see raw SQL queries in the console for debugging
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()

# Dependency to get a database session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()