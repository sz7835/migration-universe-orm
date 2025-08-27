import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

# Either set DATABASE_URL directly in .env, or let these vars build it:
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "Delt@2023")  # '@' is fine here
DB_HOST = os.getenv("DB_HOST", "161.132.202.110")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "deltanet")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = URL.create(
        "mysql+pymysql",
        username=DB_USER,
        password=DB_PASS,   # handles '@' safely (no %40 needed)
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
