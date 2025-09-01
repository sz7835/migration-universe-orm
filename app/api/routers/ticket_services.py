from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.dao.ticket_services import dao_actualizar_ticket

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
