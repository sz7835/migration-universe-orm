# app/core/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use your existing MySQL URL from .env or hardcode temporarily.
# Example (adjust to your credentials):
# mysql+pymysql://user:pass@host:3306/deltanet
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Delt%402023@161.132.202.110:3306/deltanet")

# Recommended engine params for MySQL + SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that yields a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
