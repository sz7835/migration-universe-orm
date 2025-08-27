from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import get_db, Base, engine

# If you later add ORM models, this keeps metadata in sync (no-op for raw SQL).
Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["catalogo"])

# -----------------------------
# Ruta 1: /actividades/tipoActividad
# -----------------------------
@router.get("/actividades/tipoActividad")
def get_actividad_tipo(idActividad: str | None = None,
                       idPersona: str | None = None,
                       registro: str | None = None,
                       db: Session = Depends(get_db)):
    try:
        if not idActividad or not idPersona or not registro:
            raise HTTPException(status_code=400, detail="Missing one or more required parameters")

        sql = text("""
            SELECT *
            FROM out_registro_actividad
            WHERE per_persona_id = :id_persona
              AND out_tipo_actividad_id = :id_actividad
              AND DATE(registro) = :registro_date
        """)
        result = db.execute(sql, {
            'id_persona': idPersona,
            'id_actividad': idActividad,
            'registro_date': registro
        }).fetchall()

        return [dict(row._mapping) for row in result]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))