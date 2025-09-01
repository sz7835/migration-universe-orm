from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.dao.ticket_services import (
    dao_actualizar_ticket,
    dao_derivar_ticket,
    dao_reasignar_area_servicio, 
)

router = APIRouter(prefix="/ticket", tags=["ticket-services"])

# Route 16: Edit ticket by ID
# Updates priority, catalog service, description, and audit fields if available
@router.put("/update/{idTicket}", status_code=status.HTTP_200_OK)
def editar_ticket(
    idTicket: int,
    usuario: str,
    idPrioridad: int,
    idCatalogoServicio: int,
    descripcion: str,
    db: Session = Depends(get_db),
):
    result = dao_actualizar_ticket(
        db=db,
        id_ticket=idTicket,
        usuario=usuario,
        id_prioridad=idPrioridad,
        id_catalogo_servicio=idCatalogoServicio,
        descripcion=descripcion,
    )
    if not result["updated"]:
        raise HTTPException(status_code=404, detail="Ticket no encontrado o sin cambios")
    return {"mensaje": "Ticket actualizado correctamente", "resultado": result}

# -------------------------
# RUTA 17: Derivar/Asignar ticket a otro usuario
# POST /ticket/usuario/asignar?usuario=bsayan&idTicket=918&asignar=186
# -------------------------
@router.post("/usuario/asignar", status_code=status.HTTP_200_OK)
def derivar_ticket(
    usuario: str,              # usuario que realiza la acción
    idTicket: int,             # id del ticket
    asignar: int,              # id del nuevo usuario asignado
    db: Session = Depends(get_db),
):
    result = dao_derivar_ticket(
        db=db,
        id_ticket=idTicket,
        usuario=usuario,
        nuevo_usuario_id=asignar,
    )

    if not result["exists"]:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if not result["updated"]:
        # rowcount==0 -> el valor ya era el mismo
        return {
            "mensaje": "Sin cambios (ya estaba asignado a ese usuario)",
            "resultado": result,
        }

    return {
        "mensaje": "Ticket derivado correctamente",
        "resultado": result,
    }

    # -------------------------
# RUTA 18: Reasignar área y servicio
# POST /ticket/reassign/{idTicket}
# -------------------------
@router.post("/reassign/{idTicket}", status_code=status.HTTP_200_OK)
def reasignar_area_servicio(
    idTicket: int,
    idAreaDestino: int = Form(...),
    idCatalogoServicio: int = Form(...),
    usuEditado: str = Form(...),
    db: Session = Depends(get_db),
):
    result = dao_reasignar_area_servicio(
        db=db,
        id_ticket=idTicket,
        area_destino=idAreaDestino,
        catalogo_servicio=idCatalogoServicio,
        usuario=usuEditado,
    )

    if not result["exists"]:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    if not result["updated"]:
        return {
            "mensaje": "Sin cambios (ya tenía esos valores)",
            "resultado": result,
        }

    return {
        "mensaje": "Ticket reasignado correctamente",
        "resultado": result,
    }
