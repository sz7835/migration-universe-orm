# main.py
from fastapi import FastAPI
from app.api.routers.catalogo import router as catalogo_router

app = FastAPI(title="Migration Universe ORM")

@app.get("/")
def root():
    return {"status": "ok", "message": "FastAPI running"}

# Register routers (keeps original Flask-style paths)
app.include_router(catalogo_router)

