import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
load_dotenv()


# Database Credentials
POSTGRES_USER = os.getenv("POSTGRES_USER", "cyclops_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Cl0p3s_C1")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cyclops_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5435")


# Connection String
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


# Connection Pool
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Builder Class for SQLAlchemy
Base = declarative_base()


# Open Sessions Feature
def get_db():
    """Database session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()