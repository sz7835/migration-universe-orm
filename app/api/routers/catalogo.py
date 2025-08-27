# app/api/routers/catalogo.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db  # <- from app/core/db.py

router = APIRouter(tags=["catalogo"])

# 📌 Ruta 1: /actividades/tipoActividad
# ✅ Implementada y probada en Postman (v1.5)
@router.get("/actividades/tipoActividad")
def get_actividad_tipo(
    idActividad: str | None = None,
    idPersona: str | None = None,
    registro: str | None = None,
    db: Session = Depends(get_db),
):
    """
    GET /actividades/tipoActividad?idActividad=1&idPersona=9&registro=2024-02-26
    - idActividad: 1 (use 9 for 'all')
    - idPersona: required
    - registro: YYYY-MM-DD
    """
    try:
        if not idActividad or not idPersona or not registro:
            raise HTTPException(status_code=400, detail="Missing one or more required parameters")

        sql = text("""
            SELECT *
            FROM out_registro_actividad
            WHERE per_persona_id = :id_persona
              AND (:id_actividad = '9' OR out_tipo_actividad_id = :id_actividad)
              AND DATE(registro) = :registro_date
        """)
        rows = db.execute(sql, {
            "id_persona": idPersona,
            "id_actividad": idActividad,
            "registro_date": registro
        }).fetchall()

        return [dict(r._mapping) for r in rows]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
