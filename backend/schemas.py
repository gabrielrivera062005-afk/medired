"""
MEDIRED - Esquemas Pydantic (contratos de entrada/salida de la API).
"""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------
# Medicamento
# ---------------------------------------------------------------------
class MedicamentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_medicamento: int
    codigo_cum: Optional[str] = None
    codigo_ium: Optional[str] = None
    nombre: str
    principio_activo: str
    forma_farmaceutica: str
    concentracion: Optional[str] = None
    via_administracion: Optional[str] = None
    requiere_formula: bool
    activo: bool


class MedicamentoCreate(BaseModel):
    codigo_cum: Optional[str] = None
    codigo_ium: Optional[str] = None
    nombre: str
    principio_activo: str
    forma_farmaceutica: str
    concentracion: Optional[str] = None
    via_administracion: Optional[str] = None
    requiere_formula: bool = True


# ---------------------------------------------------------------------
# Sede
# ---------------------------------------------------------------------
class SedeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_sede: int
    id_eps: int
    nombre: str
    localidad: str
    direccion: str
    telefono: Optional[str] = None
    horario: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    activo: bool


# ---------------------------------------------------------------------
# Inventario / disponibilidad
# ---------------------------------------------------------------------
class DisponibilidadOut(BaseModel):
    """Respuesta de disponibilidad por sede para un medicamento."""
    id_inventario: int
    id_sede: int
    sede: str
    localidad: str
    cantidad_disponible: int
    stock_minimo: int
    estado: Literal["no_disponible", "critico", "bajo", "disponible"]
    fecha_actualizacion: datetime


class MovimientoEntradaSalida(BaseModel):
    """Body para POST /api/inventario/entrada y /api/inventario/salida."""
    id_medicamento: int
    id_sede: int
    cantidad: int = Field(gt=0)
    id_operador: Optional[int] = None
    fuente: str = "manual"


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimiento: int
    id_inventario: int
    tipo_movimiento: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    id_operador: Optional[int] = None
    fuente: str
    fecha_hora: datetime
