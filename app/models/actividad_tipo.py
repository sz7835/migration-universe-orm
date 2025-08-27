# app/models/actividad_tipo.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ActividadTipo(Base):
    """
    Maps to MySQL table: out_tipo_actividad (id, nombre)
    """
    __tablename__ = "out_tipo_actividad"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
