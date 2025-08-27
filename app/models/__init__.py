# app/models/__init__.py
# Re-export Base and models for convenient imports across the app.

from .actividad_tipo import Base, ActividadTipo

__all__ = ["Base", "ActividadTipo"]
