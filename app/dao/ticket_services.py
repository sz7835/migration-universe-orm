from typing import Optional, List
from sqlalchemy import text
from sqlalchemy.orm import Session

TABLE_TICKETS = "tkt_ticket_principal"

# DAO Route 16: update ticket information
# Updates priority, catalog service, description, and audit fields if present
def dao_actualizar_ticket(
    db, 
    id_ticket: int,
    usuario: str,
    id_prioridad: int,
    id_catalogo_servicio: int,
    descripcion: str,
) -> dict:
    schema = (db.execute(text("SELECT DATABASE() AS db")).fetchone() or [None])[0]

    cols = [r[0] for r in db.execute(
        text("""
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
        """),
        {"schema": schema, "table": TABLE_TICKETS},
    ).fetchall()]

    low = {c.lower(): c for c in cols}

    update_user_col = None
    for cand in ("update_user", "usuario_update", "usuario_modifica", "usr_update", "user_update"):
        if cand in low: update_user_col = low[cand]; break

    update_date_col = None
    for cand in ("update_date", "fecha_update", "fecha_modifica", "f_update", "updated_at"):
        if cand in low: update_date_col = low[cand]; break

    setters = [
        "prioridad_id = :p",
        "catalogo_servicio_id = :c",
        "descripcion = :d",
    ]
    params = {"p": id_prioridad, "c": id_catalogo_servicio, "d": descripcion, "id": id_ticket}

    if update_user_col:
        setters.append(f"{update_user_col} = :u")
        params["u"] = usuario
    if update_date_col:
        setters.append(f"{update_date_col} = CURRENT_TIMESTAMP")

    sql = f"UPDATE {TABLE_TICKETS} SET {', '.join(setters)} WHERE id = :id"
    res = db.execute(text(sql), params)
    db.commit()
    return {"updated": res.rowcount > 0, "affected": res.rowcount, "audit_cols": {"user": update_user_col, "date": update_date_col}}

# -------------------------
# DAO RUTA 17: derivar/asignar ticket a otro usuario
# Cambia el usuario asignado (usuario_servicio_id) y registra auditoría.
# -------------------------
def dao_derivar_ticket(
    db: Session,
    id_ticket: int,
    usuario: str,           # quien ejecuta la acción
    nuevo_usuario_id: int,  # a quién se asigna
) -> dict:
    schema = (db.execute(text("SELECT DATABASE() AS db")).fetchone() or [None])[0]

    # ¿Existe el ticket?
    exists_row = db.execute(
        text(f"SELECT id FROM {TABLE_TICKETS} WHERE id = :id"),
        {"id": id_ticket},
    ).fetchone()

    if not exists_row:
        return {"exists": False, "updated": False, "affected": 0, "schema": schema}

    # Detectar nombres de columnas de auditoría si existen
    update_user_col = "update_user"
    update_date_col = "update_date"

    try:
        col_check = db.execute(text(f"SHOW COLUMNS FROM {TABLE_TICKETS}")).fetchall()
        columns = {row[0] for row in col_check}
    except Exception:
        columns = set()

    setters = ["usuario_servicio_id = :nuevo"]  # <<--- columna asignada en tu tabla
    params = {"id": id_ticket, "nuevo": nuevo_usuario_id}

    if update_user_col in columns:
        setters.append(f"{update_user_col} = :u")
        params["u"] = usuario

    if update_date_col in columns:
        setters.append(f"{update_date_col} = CURRENT_TIMESTAMP")

    sql = f"UPDATE {TABLE_TICKETS} SET {', '.join(setters)} WHERE id = :id"
    res = db.execute(text(sql), params)
    db.commit()

    return {
        "exists": True,
        "updated": res.rowcount > 0,   # 0 si ya estaba asignado a ese usuario
        "affected": res.rowcount,
        "changed_columns": ["usuario_servicio_id"] + (
            [update_user_col] if update_user_col in columns else []
        ) + (
            [update_date_col] if update_date_col in columns else []
        ),
        "schema": schema,
    }

# -------------------------
# DAO RUTA 18: Reasignar área y servicio de un ticket
# -------------------------
def dao_reasignar_area_servicio(
    db: Session,
    id_ticket: int,
    area_destino: int,
    catalogo_servicio: int,
    usuario: str,
) -> dict:
    schema = (db.execute(text("SELECT DATABASE() AS db")).fetchone() or [None])[0]

    # ¿Existe el ticket?
    exists_row = db.execute(
        text(f"SELECT id FROM {TABLE_TICKETS} WHERE id = :id"),
        {"id": id_ticket},
    ).fetchone()

    if not exists_row:
        return {"exists": False, "updated": False, "affected": 0, "schema": schema}

    # Auditoría
    update_user_col = "update_user"
    update_date_col = "update_date"

    try:
        col_check = db.execute(text(f"SHOW COLUMNS FROM {TABLE_TICKETS}")).fetchall()
        columns = {row[0] for row in col_check}
    except Exception:
        columns = set()

    setters = [
        "area_destino_id = :area",
        "catalogo_servicio_id = :servicio",
    ]
    params = {"id": id_ticket, "area": area_destino, "servicio": catalogo_servicio}

    if update_user_col in columns:
        setters.append(f"{update_user_col} = :u")
        params["u"] = usuario

    if update_date_col in columns:
        setters.append(f"{update_date_col} = CURRENT_TIMESTAMP")

    sql = f"UPDATE {TABLE_TICKETS} SET {', '.join(setters)} WHERE id = :id"
    res = db.execute(text(sql), params)
    db.commit()

    return {
        "exists": True,
        "updated": res.rowcount > 0,
        "affected": res.rowcount,
        "changed_columns": ["area_destino_id", "catalogo_servicio_id"]
            + ([update_user_col] if update_user_col in columns else [])
            + ([update_date_col] if update_date_col in columns else []),
        "schema": schema,
    }

# -------------------------
# DAO RUTA 19: Reabrir ticket (cambiar estado y registrar auditoría)
# -------------------------
def dao_reabrir_ticket(
    db: Session,
    id_ticket: int,
    usuario: str,
    estado_id: int,
    descripcion: str,
) -> dict:
    schema = (db.execute(text("SELECT DATABASE() AS db")).fetchone() or [None])[0]

    exists_row = db.execute(
        text(f"SELECT id FROM {TABLE_TICKETS} WHERE id = :id"),
        {"id": id_ticket},
    ).fetchone()

    if not exists_row:
        return {"exists": False, "updated": False, "affected": 0, "schema": schema}

    # columnas esperadas
    update_user_col = "update_user"
    update_date_col = "update_date"

    try:
        col_check = db.execute(text(f"SHOW COLUMNS FROM {TABLE_TICKETS}")).fetchall()
        columns = {row[0] for row in col_check}
    except Exception:
        columns = set()

    setters = [
        "estado_id = :estado",
        "descripcion = :desc"
    ]
    params = {"id": id_ticket, "estado": estado_id, "desc": descripcion}

    if update_user_col in columns:
        setters.append(f"{update_user_col} = :u")
        params["u"] = usuario

    if update_date_col in columns:
        setters.append(f"{update_date_col} = CURRENT_TIMESTAMP")

    sql = f"UPDATE {TABLE_TICKETS} SET {', '.join(setters)} WHERE id = :id"
    res = db.execute(text(sql), params)
    db.commit()

    return {
        "exists": True,
        "updated": res.rowcount > 0,
        "affected": res.rowcount,
        "changed_columns": ["estado_id","descripcion"]
            + ([update_user_col] if update_user_col in columns else [])
            + ([update_date_col] if update_date_col in columns else []),
        "schema": schema,
    }

# -------------------------
# DAO RUTA 20: Campos de filtro tickets
# Devuelve lista de columnas clave de la tabla principal
# -------------------------
def dao_campos_filtro_tickets(db: Session) -> dict:
    schema = (db.execute(text("SELECT DATABASE() AS db")).fetchone() or [None])[0]

    # Obtenemos las columnas de la tabla de tickets
    columnas = db.execute(
        text(f"SHOW COLUMNS FROM {TABLE_TICKETS}")
    ).fetchall()

    # Armamos lista simple con nombres de campos
    campos = [col[0] for col in columnas]

    return {
        "schema": schema,
        "tabla": TABLE_TICKETS,
        "campos": campos
    }
