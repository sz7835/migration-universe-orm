# app/models/registry.py
# Defines the ORM model for the out_registro_proyecto table used by Route 6.

from sqlalchemy import Column, Integer, String, DateTime

# IMPORTANT:
# Reuse the SAME Base you already use for your other models.
# If your Base lives somewhere else, change this import to match your project.
# Example alternatives you might already have:
#   from .base import Base
#   from .db import Base
#   from .models import Base
from .actividad_tipo import Base  # <-- adjust if your Base is defined in a different file


class OutRegistroProyecto(Base):
    """
    ORM mapping for MySQL table: out_registro_proyecto

    Columns expected by your routes/DAO:
      - id               (PK)
      - id_persona       (int, not null)
      - codigo           (varchar ~50)
      - descripcion      (varchar ~255)
      - estado           (int)
      - create_user      (varchar ~50)
      - create_date      (datetime)
      - update_user      (varchar ~50)
      - update_date      (datetime)
    """
    __tablename__ = "out_registro_proyecto"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_persona = Column(Integer, nullable=False)
    codigo = Column(String(50))
    descripcion = Column(String(255))
    estado = Column(Integer)
    create_user = Column(String(50))
    create_date = Column(DateTime)
    update_user = Column(String(50))
    update_date = Column(DateTime)
