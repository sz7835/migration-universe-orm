from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.core.db import get_db
from app.dao.registro_proyecto import dao_filtrar_proyectos

router = APIRouter(prefix="/registro-proyecto", tags=["registro-proyecto"])


# Route 10: GET /registro-proyecto/index?idConsultor=8&proyectoDescripcion=&estado=9
# Filters projects by consultant, optional description, and optional status.
@router.get("/index")
def filtrar_proyectos(
    idConsultor: int,
    proyectoDescripcion: Optional[str] = None,
    estado: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return dao_filtrar_proyectos(
        db=db,
        id_consultor=idConsultor,
        proyecto_descripcion=proyectoDescripcion,
        estado=estado,
    )