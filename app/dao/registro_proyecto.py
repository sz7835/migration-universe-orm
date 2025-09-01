from sqlalchemy import text

# DAO Route 10: filter projects (auto-detects description column).
# Returns list[dict] with matching projects.
def dao_filtrar_proyectos(db, id_consultor: int, proyecto_descripcion: str | None, estado: int | None):
    # detect DB/schema name
    schema_row = db.execute(text("SELECT DATABASE() AS db")).fetchone()
    schema = schema_row[0] if schema_row else None

    # try common description column names, pick the first that exists
    candidates = ["proyecto_descripcion", "descripcion", "proyecto", "nombre", "detalle", "titulo"]
    desc_col = None
    for col in candidates:
        exists = db.execute(
            text("""
                SELECT 1
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = :schema
                  AND TABLE_NAME   = 'out_registro_proyecto'
                  AND COLUMN_NAME  = :col
                LIMIT 1
            """),
            {"schema": schema, "col": col},
        ).fetchone()
        if exists:
            desc_col = col
            break

    # if nothing matched, don't alias/select a bad column; also ignore the desc filter
    if desc_col is None:
        desc_select = "rp.id"                     # harmless placeholder so SELECT compiles
        proyecto_descripcion = None               # disable LIKE filter
    else:
        desc_select = f"rp.{desc_col}"

    # build optional filters
    desc_clause   = f"AND {desc_select} LIKE :desc" if proyecto_descripcion else ""
    estado_clause = "AND rp.estado = :estado" if estado is not None else ""

    sql = f"""
        SELECT
            rp.id,
            rp.id_persona                       AS id_consultor,
            {desc_select}                       AS proyecto_descripcion,
            rp.estado,
            rp.create_user,
            rp.create_date,
            rp.update_user,
            rp.update_date
        FROM out_registro_proyecto rp
        WHERE rp.id_persona = :id_consultor
          {desc_clause}
          {estado_clause}
        ORDER BY rp.id DESC
    """

    params = {"id_consultor": id_consultor}
    if proyecto_descripcion:
        params["desc"] = f"%{proyecto_descripcion}%"
    if estado is not None:
        params["estado"] = estado

    rows = db.execute(text(sql), params).fetchall()
    return [dict(r._mapping) for r in rows]

from sqlalchemy import text

# DAO Route 11: create project (auto-detects column names).
# Returns dict of the inserted row (or at least the new id).
def dao_crear_proyecto(db, id_consultor: int, codigo: str, proyecto_descripcion: str, create_user: str) -> dict:
    # detect DB/schema name
    schema_row = db.execute(text("SELECT DATABASE() AS db")).fetchone()
    schema = schema_row[0] if schema_row else None

    # helper to check if a column exists
    def col_exists(col: str) -> bool:
        row = db.execute(
            text("""
                SELECT 1
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = :schema
                  AND TABLE_NAME   = 'out_registro_proyecto'
                  AND COLUMN_NAME  = :col
                LIMIT 1
            """),
            {"schema": schema, "col": col},
        ).fetchone()
        return row is not None

    # detect which columns to use
    desc_candidates = ["proyecto_descripcion", "descripcion", "proyecto", "nombre", "detalle", "titulo"]
    desc_col = next((c for c in desc_candidates if col_exists(c)), None)
    if not desc_col:
        raise ValueError("No se encontró una columna de descripción en out_registro_proyecto.")

    uses_id_persona  = col_exists("id_persona")
    uses_id_consult  = col_exists("id_consultor")
    has_codigo       = col_exists("codigo")
    has_create_user  = col_exists("create_user")
    has_create_date  = col_exists("create_date")
    has_estado       = col_exists("estado")

    # dynamic INSERT
    cols, vals, params = [], [], {}

    if uses_id_persona:
        cols += ["id_persona"]; vals += [":idc"]; params["idc"] = id_consultor
    elif uses_id_consult:
        cols += ["id_consultor"]; vals += [":idc"]; params["idc"] = id_consultor
    else:
        raise ValueError("La tabla no tiene ni id_persona ni id_consultor.")

    cols += [desc_col]; vals += [":desc"]; params["desc"] = proyecto_descripcion

    if has_codigo:
        cols += ["codigo"]; vals += [":codigo"]; params["codigo"] = codigo

    if has_estado:
        cols += ["estado"]; vals += [":estado"]; params["estado"] = 1  # default activo

    if has_create_user:
        cols += ["create_user"]; vals += [":cuser"]; params["cuser"] = create_user

    if has_create_date:
        cols += ["create_date"]; vals += ["CURRENT_TIMESTAMP"]

    sql = f"INSERT INTO out_registro_proyecto ({', '.join(cols)}) VALUES ({', '.join(vals)})"
    result = db.execute(text(sql), params)
    db.commit()
    new_id = result.lastrowid

    # read back for echo
    sel_cols = [
        "rp.id",
        ("rp.id_persona AS id_consultor" if uses_id_persona else "rp.id_consultor AS id_consultor"),
        f"rp.{desc_col} AS proyecto_descripcion",
    ]
    if has_codigo:      sel_cols.append("rp.codigo")
    if has_estado:      sel_cols.append("rp.estado")
    if has_create_user: sel_cols.append("rp.create_user")
    if has_create_date: sel_cols.append("rp.create_date")

    row = db.execute(
        text(f"SELECT {', '.join(sel_cols)} FROM out_registro_proyecto rp WHERE rp.id = :id"),
        {"id": new_id},
    ).fetchone()

    return dict(row._mapping) if row else {"id": new_id}

    from sqlalchemy import text

# DAO Route 12: hard delete project (removes row permanently).
# Returns dict with status and number of affected rows.
def dao_eliminar_proyecto(db, id_proyecto: int) -> dict:
    result = db.execute(
        text("DELETE FROM out_registro_proyecto WHERE id = :id"),
        {"id": id_proyecto},
    )
    db.commit()
    return {"deleted": result.rowcount > 0, "affected": result.rowcount}