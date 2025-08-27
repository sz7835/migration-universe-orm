from fastapi import FastAPI
from app.api.routers.catalogo import router as catalogo_router, router_horas as registro_horas_router

app = FastAPI(title="migration-universe-orm")

app.include_router(catalogo_router)        # /actividades/*
app.include_router(registro_horas_router)  # /registro-horas/*

@app.get("/")
def root():
    return {"ok": True}
