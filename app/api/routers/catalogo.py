# app/api/routers/catalogo.py
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db

router = APIRouter(prefix="/actividades", tags=["actividades"])

#ROUTE 1 This endpoint returns actividades filtered by persona, actividad, and optional fecha.
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


# Dev note: Spec route 2. Flexible filter by persona, tipo y fecha (param 'registro' yyyy-MM-dd).
# Example: GET /actividades/filter?idPersona=8&idActividad=1&registro=2025-07-10
@router.get("/filter")
def filter_actividades(idPersona: Optional[int] = None,
                       idActividad: Optional[int] = None,
                       registro: Optional[str] = None,
                       db: Session = Depends(get_db)):
    base = ["SELECT * FROM out_registro_actividad WHERE 1=1"]
    params = {}
    if idPersona is not None:
        base.append("AND per_persona_id = :idPersona")
        params["idPersona"] = idPersona
    if idActividad is not None:
        base.append("AND out_tipo_actividad_id = :idActividad")
        params["idActividad"] = idActividad
    if registro:
        # match both date column 'fecha' and date part of 'registro' datetime
        base.append("AND (fecha = :registro OR DATE(registro) = :registro)")
        params["registro"] = registro
    base.append("ORDER BY id DESC")
    sql = text("\n".join(base))
    rows = db.execute(sql, params).mappings().all()
    return [dict(r) for r in rows]