# app/dao/actividad.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import ActividadTipo

# ---- TIPO ACTIVIDAD (ORM) ---------------------------------------------------
def dao_get_tipo_actividad(db: Session):
    """Return all rows from out_tipo_actividad."""
    return db.query(ActividadTipo).all()

# Backward-compatible alias
def dao_get_actividad_tipo(db: Session):
    return dao_get_tipo_actividad(db)

# ---- RUTA 1: /actividades/tipoActividad ------------------------------------
def dao_list_registros_por_persona_tipo(
    db: Session, id_persona: int, id_actividad: int, fecha: str | None
):
    sql = """
        SELECT *
        FROM out_registro_actividad
        WHERE per_persona_id = :idPersona
          AND out_tipo_actividad_id = :idActividad
    """
    params = {"idPersona": id_persona, "idActividad": id_actividad}
    if fecha:
        sql += " AND fecha = :fecha"
        params["fecha"] = fecha
    sql += " ORDER BY id DESC"
    return [dict(r) for r in db.execute(text(sql), params).mappings().all()]

# ---- RUTA 2: /actividades/filter -------------------------------------------
def dao_filtrar_registros(
    db: Session, id_persona: int | None, id_actividad: int | None, registro: str | None
):
    parts = ["SELECT * FROM out_registro_actividad WHERE 1=1"]
    params: dict = {}
    if id_persona is not None:
        parts.append("AND per_persona_id = :idPersona")
        params["idPersona"] = id_persona
    if id_actividad is not None:
        parts.append("AND out_tipo_actividad_id = :idActividad")
        params["idActividad"] = id_actividad
    if registro:
        parts.append("AND (fecha = :registro OR DATE(registro) = :registro)")
        params["registro"] = registro
    parts.append("ORDER BY id DESC")
    sql = text("\n".join(parts))
    return [dict(r) for r in db.execute(sql, params).mappings().all()]

# ---- RUTA 3: /actividades/create -------------------------------------------
def dao_crear_registro(
    db: Session, personal_id: int, tipo_act_id: int, fecha: str, hora: str,
    create_user: str, detalle: str = "Detalle no proporcionado"
):
    registro_dt = f"{fecha} {hora}:00"
    insert_sql = text("""
        INSERT INTO out_registro_actividad
            (out_tipo_actividad_id, per_persona_id, fecha, detalle, registro, create_user, create_date)
        VALUES
            (:idTipoAct, :personalId, :fecha, :detalle, :registro, :createUser, NOW())
    """)
    db.execute(insert_sql, {
        "idTipoAct": tipo_act_id,
        "personalId": personal_id,
        "fecha": fecha,
        "detalle": detalle,
        "registro": registro_dt,
        "createUser": create_user
    })
    # Return the last inserted id (MySQL)
    last_id = db.execute(text("SELECT LAST_INSERT_ID() AS id")).mappings().first()["id"]
    db.commit()
    return last_id

   # ---- RUTA 4: /registro-horas/index ----------------------------------------
def dao_filtrar_horas(
    db: Session,
    id_persona: int | None,
    estado: int | None,
    fecha_inicio: str | None,  # yyyy-MM-dd -> maps to 'dia'
    fecha_fin: str | None,     # yyyy-MM-dd -> maps to 'dia'
):
    parts = ["SELECT * FROM out_registro_horas WHERE 1=1"]
    params: dict = {}

    if id_persona is not None:
        parts.append("AND id_persona = :idPersona")
        params["idPersona"] = id_persona

    if estado is not None:
        parts.append("AND estado = :estado")
        params["estado"] = estado

    # Rango sobre la columna 'dia' (DATE)
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

# ---- DAO: crear registros de horas (Ruta 5) ----
from sqlalchemy import text

def dao_crear_registro_horas(db, id_proyecto: int, id_persona: int, actividades: list, dia: str, create_user: str):
    ids = []
    for item in actividades:
        sql = text("""
            INSERT INTO out_registro_horas (id_proyecto, id_persona, actividad, horas, dia, estado, create_user, create_date)
            VALUES (:idProyecto, :idPersona, :actividad, :horas, :dia, 1, :createUser, NOW())
        """)
        params = {
            "idProyecto": id_proyecto,
            "idPersona": id_persona,
            "actividad": item["actividad"],
            "horas": item["horas"],
            "dia": dia,
            "createUser": create_user,
        }
        result = db.execute(sql, params)
        ids.append(result.lastrowid)
    db.commit()
    return ids
