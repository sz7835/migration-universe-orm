# app/dao/registro_horas.py
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

# ----------------------------------------------------
# ROUTE 4: /registro-horas/index  (GET)
# Filtrar registros de horas en la tabla out_registro_horas
# ----------------------------------------------------
def dao_filtrar_horas(
    db: Session,
    id_persona: Optional[int],
    estado: Optional[int],
    fecha_inicio: Optional[str],  # yyyy-MM-dd -> column 'dia'
    fecha_fin: Optional[str],     # yyyy-MM-dd -> column 'dia'
) -> List[dict]:
    parts = ["SELECT * FROM out_registro_horas WHERE 1=1"]
    params: Dict[str, object] = {}

    if id_persona is not None:
        parts.append("AND id_persona = :idPersona")
        params["idPersona"] = id_persona

    if estado is not None:
        parts.append("AND estado = :estado")
        params["estado"] = estado

    if fecha_inicio and fecha_fin:
        parts.append("AND dia BETWEEN :fini AND :ffin")
        params["fini"] = fecha_inicio
        params["ffin"] = fecha_fin
    elif fecha_inicio:
        parts.append("AND dia >= :fini")
        params["fini"] = fecha_inicio
    elif fecha_fin:
        parts.append("AND dia <= :ffin")
        params["ffin"] = fecha_fin

    parts.append("ORDER BY id DESC")
    sql = text("\n".join(parts))
    rows = db.execute(sql, params).mappings().all()
    return [dict(r) for r in rows]


# ----------------------------------------------------
# ROUTE 5: /registro-horas/create  (POST)
# Crear registros de horas en la tabla out_registro_horas
# ----------------------------------------------------
def dao_crear_registro_horas(
    db: Session,
    id_persona: int,
    id_proyecto: int | str,
    dia: str,                       # 'yyyy-MM-dd'
    create_user: str,
    detalle: List[Dict[str, object]],  # e.g. [{"actividad":"Soporte","horas":3}]
) -> List[int]:
    inserted_ids: List[int] = []

    insert_sql = text("""
        INSERT INTO out_registro_horas
            (id_persona, id_proyecto, actividad, horas, estado, dia, create_user, create_date)
        VALUES
            (:id_persona, :id_proyecto, :actividad, :horas, :estado, :dia, :create_user, NOW())
    """)

    for item in detalle:
        params = {
            "id_persona": id_persona,
            "id_proyecto": id_proyecto,
            "actividad": str(item.get("actividad", "")),
            "horas": int(item.get("horas", 0)),
            "estado": 1,               # default activo
            "dia": dia,
            "create_user": create_user,
        }
        db.execute(insert_sql, params)
        new_id = db.execute(text("SELECT LAST_INSERT_ID() AS id")).scalar()
        inserted_ids.append(int(new_id))

    db.commit()
    return inserted_ids
