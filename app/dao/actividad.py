# app/dao/actividad.py
from sqlalchemy.orm import Session
from app.models import ActividadTipo

def dao_get_tipo_actividad(db: Session):
    """
    Preferred name: returns all rows from out_tipo_actividad.
    """
    return db.query(ActividadTipo).all()

# Backward-compatible alias so either import works.
def dao_get_actividad_tipo(db: Session):
    return dao_get_tipo_actividad(db)
