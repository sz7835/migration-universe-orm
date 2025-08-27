from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db

router = APIRouter(prefix="/actividades", tags=["actividades"])

# This endpoint returns actividades filtered by persona, actividad, and optional fecha.
# It matches the spec: GET /actividades/tipoActividad with query parameters.
@router.get("/tipoActividad")
def get_tipo_actividad(idPersona: int, idActividad: int, fecha: str | None = None, db: Session = Depends(get_db)):
    sql = """
        SELECT *
        FROM out_registro_actividad
        WHERE per_persona_id = :idPersona
          AND out_tipo_actividad_id = :idActividad
    """
    params = {"idPersona": idPersona, "idActividad": idActividad}

    if fecha:
        sql += " AND fecha = :fecha"
        params["fecha"] = fecha

    sql += " ORDER BY id DESC"
    rows = db.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]
