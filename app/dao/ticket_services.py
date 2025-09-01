from sqlalchemy import text

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
