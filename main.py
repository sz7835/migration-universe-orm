from fastapi import FastAPI
from app.api.routers.catalogo import router as catalogo_router

app = FastAPI(title="migration-universe-orm")

# IMPORTANT: no extra prefix here unless you want /api/...
app.include_router(catalogo_router)

@app.get("/")
def root():
    return {"ok": True}
