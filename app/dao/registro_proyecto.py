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
