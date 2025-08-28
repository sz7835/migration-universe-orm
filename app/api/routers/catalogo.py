from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dao.actividad import (
    dao_list_registros_por_persona_tipo,
    dao_filtrar_registros,
    dao_crear_registro,
    dao_crear_registro_horas,   
    dao_filtrar_horas,
    dao_listar_proyectos_por_persona,          
)

router = APIRouter(prefix="/actividades", tags=["actividades"])
router_horas = APIRouter(prefix="/registro-horas", tags=["registro-horas"])  # <-- SPEC prefix


class HorasDetalleItem(BaseModel):
    actividad: str
    horas: int | str

class CrearHorasBody(BaseModel):
    idProyecto: int | str
    idPersona: int
    detalle: List[HorasDetalleItem]
    dia: str                  # yyyy-MM-dd
    createUser: str

# ROUTE 1: matches spec. Returns registros by persona/tipo and optional fecha.
# Example: GET /actividades/tipoActividad?idPersona=8&idActividad=1&fecha=2025-07-10
@router.get("/tipoActividad")
@router.get("/registro")  # alias for backward compatibility
def get_tipo_actividad(idPersona: int, idActividad: int, fecha: Optional[str] = None,
                       db: Session = Depends(get_db)):
    return dao_list_registros_por_persona_tipo(db, idPersona, idActividad, fecha)

# ROUTE 2: spec. Flexible filter (idPersona, idActividad, registro=yyyy-MM-dd)
# Example: GET /actividades/filter?idPersona=8&idActividad=1&registro=2025-07-10
@router.get("/filter")
def filter_actividades(idPersona: Optional[int] = None,
                       idActividad: Optional[int] = None,
                       registro: Optional[str] = None,
                       db: Session = Depends(get_db)):
    return dao_filtrar_registros(db, idPersona, idActividad, registro)

# ROUTE 3: spec. Create new activity via query params (POST).
# Example: POST /actividades/create?personalId=8&idTipoAct=1&hora=14:00&fecha=2025-07-10&createUser=bsayan&detalle=texto
@router.post("/create")
def create_actividad(personalId: int, idTipoAct: int, hora: str, fecha: str,
                     createUser: str, detalle: Optional[str] = None,
                     db: Session = Depends(get_db)):
    last_id = dao_crear_registro(
        db, personal_id=personalId, tipo_act_id=idTipoAct, fecha=fecha,
        hora=hora, create_user=createUser,
        detalle=detalle or "Detalle no proporcionado"
    )
    return {"status": "ok", "id": last_id, "message": "Actividad creada correctamente"}

# ROUTE 4: Filtra registros de horas por persona, estado y rango de fechas.
# Ejemplo: GET /actividades/registro-horas/index?idPersona=8&estado=9&fechaIniciof=2025-07-10&fechaFin=2025-07-10
@router.get("/registro-horas/index")
def filtrar_horas(
    idPersona: int | None = None,
    estado: int | None = None,
    fechaIniciof: str | None = None,
    fechaFin: str | None = None,
    db: Session = Depends(get_db),
):
    return dao_filtrar_horas(db, idPersona, estado, fechaIniciof, fechaFin)

    # ---- ROUTE 5: POST /registro-horas/create ----
@router_horas.post("/create")
def crear_registro_horas(payload: CrearHorasBody, db: Session = Depends(get_db)):
    if not payload.detalle:
        raise HTTPException(status_code=400, detail="detalle no puede estar vacío")

    ids = dao_crear_registro_horas(
        db,
        id_proyecto=int(payload.idProyecto),
        id_persona=payload.idPersona,
        actividades=[{"actividad": d.actividad, "horas": int(d.horas)} for d in payload.detalle],
        dia=payload.dia,
        create_user=payload.createUser,
    )
    return {"status": "ok", "ids": ids, "message": "Registros de horas creados correctamente"}

# ---- ROUTE 6: POST /registro-horas/mostrarProyecto ----
# Ejemplo: POST /registro-horas/mostrarProyecto?idPersona=8
@router_horas.post("/mostrarProyecto")
def mostrar_proyectos(idPersona: int, db: Session = Depends(get_db)):
    data = dao_listar_proyectos_por_persona(db, idPersona)
    return {"status": "ok", "total": len(data), "data": data}