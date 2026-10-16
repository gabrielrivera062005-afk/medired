"""
MEDIRED - Modelos SQLAlchemy (mapean 1 a 1 las tablas de database/schema.sql).

Solo se modelan aquí las tablas que usan las Fases 1-4 del backend
(medicamentos, sedes, inventario, movimientos, usuario para operador).
Las demás tablas (solicitud, reserva, entrega, alerta, historial_auditoria)
se agregan cuando lleguemos a esas fases, con el mismo patrón.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, Numeric, TIMESTAMP,
    ForeignKey, CheckConstraint, UniqueConstraint, text,
)
from sqlalchemy.orm import relationship

from database import Base


class EPS(Base):
    __tablename__ = "eps"

    id_eps = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    nit = Column(String(20))
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=text("NOW()"))

    sedes = relationship("Sede", back_populates="eps")


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True)
    id_eps = Column(Integer, ForeignKey("eps.id_eps"))
    documento = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    email = Column(String(150), unique=True)
    telefono = Column(String(20))
    rol = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        CheckConstraint(
            "rol IN ('paciente','operador_inventario','administrador','analista')",
            name="usuario_rol_check",
        ),
    )


class Medicamento(Base):
    __tablename__ = "medicamento"

    id_medicamento = Column(Integer, primary_key=True)
    codigo_cum = Column(String(30))
    codigo_ium = Column(String(30))
    nombre = Column(String(200), nullable=False)
    principio_activo = Column(String(200), nullable=False)
    forma_farmaceutica = Column(String(60), nullable=False)
    concentracion = Column(String(50))
    via_administracion = Column(String(50))
    requiere_formula = Column(Boolean, nullable=False, default=True)
    activo = Column(Boolean, nullable=False, default=True)

    inventarios = relationship("Inventario", back_populates="medicamento")


class Sede(Base):
    __tablename__ = "sede"

    id_sede = Column(Integer, primary_key=True)
    id_eps = Column(Integer, ForeignKey("eps.id_eps"), nullable=False)
    nombre = Column(String(150), nullable=False)
    localidad = Column(String(80), nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(String(20))
    horario = Column(String(100))
    latitud = Column(Numeric(9, 6))
    longitud = Column(Numeric(9, 6))
    activo = Column(Boolean, nullable=False, default=True)

    eps = relationship("EPS", back_populates="sedes")
    inventarios = relationship("Inventario", back_populates="sede")


class Inventario(Base):
    __tablename__ = "inventario"

    id_inventario = Column(Integer, primary_key=True)
    id_medicamento = Column(Integer, ForeignKey("medicamento.id_medicamento"), nullable=False)
    id_sede = Column(Integer, ForeignKey("sede.id_sede"), nullable=False)
    cantidad_disponible = Column(Integer, nullable=False, default=0)
    cantidad_reservada = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=0)
    fecha_actualizacion = Column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        UniqueConstraint("id_medicamento", "id_sede", name="inventario_med_sede_unique"),
    )

    medicamento = relationship("Medicamento", back_populates="inventarios")
    sede = relationship("Sede", back_populates="inventarios")
    movimientos = relationship("MovimientoInventario", back_populates="inventario")


class MovimientoInventario(Base):
    __tablename__ = "movimiento_inventario"

    id_movimiento = Column(BigInteger, primary_key=True)
    id_inventario = Column(Integer, ForeignKey("inventario.id_inventario"), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)
    cantidad = Column(Integer, nullable=False)
    stock_anterior = Column(Integer, nullable=False)
    stock_nuevo = Column(Integer, nullable=False)
    id_solicitud = Column(Integer, ForeignKey("solicitud.id_solicitud"), nullable=True)
    id_operador = Column(Integer, ForeignKey("usuario.id_usuario"))
    fuente = Column(String(100), nullable=False, default="manual")
    fecha_hora = Column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        CheckConstraint(
            "tipo_movimiento IN ('entrada','salida','reserva','liberacion_reserva','ajuste')",
            name="movimiento_tipo_check",
        ),
        CheckConstraint("cantidad > 0", name="movimiento_cantidad_check"),
    )

    inventario = relationship("Inventario", back_populates="movimientos")


class Solicitud(Base):
    """Modelo mínimo: solo lo necesario para la FK de movimiento_inventario.
    Se completa en la Fase 5 (solicitudes/reservas/entregas)."""
    __tablename__ = "solicitud"

    id_solicitud = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_sede = Column(Integer, ForeignKey("sede.id_sede"), nullable=False)
    tipo_entrega = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    fecha_solicitud = Column(TIMESTAMP, server_default=text("NOW()"))
