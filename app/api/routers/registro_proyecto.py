from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.db import get_db
from app.dao.registro_proyecto import (
    dao_filtrar_proyectos,
    dao_crear_proyecto,
    dao_eliminar_proyecto,    
)

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

    # Ruta 11: Crear un nuevo proyecto
# Método: POST /registro-proyecto/save
@router.post("/save", status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    idConsultor: int,
    codigo: str,
    proyectoDescripcion: str,
    createUser: str,
    db: Session = Depends(get_db),
):
    try:
        creado = dao_crear_proyecto(
            db=db,
            id_consultor=idConsultor,
            codigo=codigo,
            proyecto_descripcion=proyectoDescripcion,
            create_user=createUser,
        )
        return {"mensaje": "Proyecto creado correctamente", "proyecto": creado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

   # Ruta 12: Eliminar un proyecto
# Método: PUT /registro-proyecto/delete
@router.put("/delete")
def eliminar_proyecto(
    idProyecto: int,
    db: Session = Depends(get_db),
):
    result = dao_eliminar_proyecto(db=db, id_proyecto=idProyecto)
    if not result["deleted"]:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"mensaje": "Proyecto eliminado correctamente", "resultado": result}