import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Migration Universe ORM")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Optional: allow parts if you don't use a full DATABASE_URL
if not DATABASE_URL:
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "")
    user = os.getenv("DB_USER", "")
    pwd  = os.getenv("DB_PASSWORD", "")
    if name and user:
        DATABASE_URL = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}"

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8085"))
