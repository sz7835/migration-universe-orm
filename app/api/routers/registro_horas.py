from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.db import get_db
from app.dao.registro_horas import dao_filtrar_horas, dao_crear_registro_horas, dao_listar_proyectos_por_persona

router = APIRouter(prefix="/registro-horas", tags=["registro-horas"])

# Pydantic models
class HorasDetalleItem(BaseModel):
    actividad: str
    horas: int | str

class CrearHorasBody(BaseModel):
    idProyecto: int | str
    idPersona: int
    detalle: List[HorasDetalleItem]
    dia: str                  # yyyy-MM-dd
    createUser: str


# ROUTE 4: Filtra registros de horas
# Example: GET /registro-horas/index?idPersona=285&estado=1&fechaIniciof=2025-08-12&fechaFin=2025-08-12
@router.get("/index")
def filtrar_horas(
    idPersona: Optional[int] = None,
    estado: Optional[int] = None,
    fechaIniciof: Optional[str] = None,
    fechaFin: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return dao_filtrar_horas(db, idPersona, estado, fechaIniciof, fechaFin)


# ROUTE 5: Crear registros de horas
# Example: POST /registro-horas/create
@router.post("/create")
def crear_horas(body: CrearHorasBody, db: Session = Depends(get_db)):
    ids = dao_crear_registro_horas(
        db=db,
        id_persona=body.idPersona,
        id_proyecto=body.idProyecto,
        dia=body.dia,
        create_user=body.createUser,
        detalle=[{"actividad": d.actividad, "horas": d.horas} for d in body.detalle],
    )
    return {"status": "ok", "inserted": len(ids), "ids": ids}
    
# ROUTE 6: Lista proyectos por persona (POST)
# Ejemplo: POST /registro-horas/mostrarProyecto?idPersona=8
@router.post("/mostrarProyecto")
def mostrar_proyecto(
    idPersona: int,
    activos: bool = True,
    db: Session = Depends(get_db),
):
    return dao_listar_proyectos_por_persona(db, idPersona, solo_activos=activos)