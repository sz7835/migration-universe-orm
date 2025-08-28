from fastapi import FastAPI
from app.api.routers.actividades import router as actividades_router
from app.api.routers.health import router as health_router

app = FastAPI(title="migration-universe-orm")

app.include_router(actividades_router)  # /actividades/*
app.include_router(health_router)       # /health
