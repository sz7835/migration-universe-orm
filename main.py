# main.py (project root)
from fastapi import FastAPI

app = FastAPI(title="Migration Universe ORM")

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI running"}
