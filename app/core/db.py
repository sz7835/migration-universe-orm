from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

# Fail fast if not configured
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not configured")

# Engine + session factory (PyMySQL is used via the URL)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # drop dead connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for future ORM models (even if you use raw SQL today)
Base = declarative_base()

def get_db():
    """FastAPI dependency: yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: tiny health check
def ping_db() -> int:
    from sqlalchemy import text
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar()
