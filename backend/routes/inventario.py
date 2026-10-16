"""
MEDIRED - Fases 3 y 4: disponibilidad, entradas, salidas y movimientos.

Nota importante: el schema.sql tiene un TRIGGER (fn_aplicar_movimiento) que
calcula stock_anterior/stock_nuevo y actualiza inventario.cantidad_disponible
automáticamente cuando se inserta una fila en movimiento_inventario. Por eso
aquí el backend NO recalcula el stock a mano: solo inserta el movimiento y
dejamos que la base de datos aplique la regla de negocio (así se evita
duplicar lógica entre backend y BD, y la trazabilidad queda garantizada
incluso si alguien inserta un movimiento directamente en la BD).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Inventario, MovimientoInventario, Medicamento
from schemas import DisponibilidadOut, MovimientoEntradaSalida, MovimientoOut

router = APIRouter(prefix="/api/inventario", tags=["inventario"])


@router.get("/{id_medicamento}", response_model=list[DisponibilidadOut])
def disponibilidad_por_medicamento(id_medicamento: int, db: Session = Depends(get_db)):
    """GET /api/inventario/{medicamento_id} - disponibilidad por sede.

    Usa la vista vw_disponibilidad definida en schema.sql, que ya calcula
    el estado (no_disponible / critico / bajo / disponible).
    """
    med = db.get(Medicamento, id_medicamento)
    if not med:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")

    rows = db.execute(
        text("""
            SELECT i.id_inventario, v.id_sede, v.sede, v.localidad,
                   v.cantidad_disponible, v.stock_minimo, v.estado,
                   i.fecha_actualizacion
            FROM medired.vw_disponibilidad v
            JOIN medired.inventario i
              ON i.id_medicamento = v.id_medicamento AND i.id_sede = v.id_sede
            WHERE v.id_medicamento = :id_medicamento
            ORDER BY v.cantidad_disponible DESC
        """),
        {"id_medicamento": id_medicamento},
    ).mappings().all()

    return list(rows)


def _obtener_o_lanzar_inventario(db: Session, id_medicamento: int, id_sede: int) -> Inventario:
    inv = (
        db.query(Inventario)
        .filter(
            Inventario.id_medicamento == id_medicamento,
            Inventario.id_sede == id_sede,
        )
        .first()
    )
    if not inv:
        raise HTTPException(
            status_code=404,
            detail="No existe registro de inventario para ese medicamento en esa sede. "
                   "Debe crearse primero (ej. mediante el panel de administración).",
        )
    return inv


@router.post("/entrada", response_model=MovimientoOut, status_code=201)
def registrar_entrada(payload: MovimientoEntradaSalida, db: Session = Depends(get_db)):
    """POST /api/inventario/entrada - registrar entrada de stock."""
    inv = _obtener_o_lanzar_inventario(db, payload.id_medicamento, payload.id_sede)

    mov = MovimientoInventario(
        id_inventario=inv.id_inventario,
        tipo_movimiento="entrada",
        cantidad=payload.cantidad,
        stock_anterior=0,  # el trigger de la BD sobreescribe este valor
        stock_nuevo=0,     # el trigger de la BD sobreescribe este valor
        id_operador=payload.id_operador,
        fuente=payload.fuente,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return mov


@router.post("/salida", response_model=MovimientoOut, status_code=201)
def registrar_salida(payload: MovimientoEntradaSalida, db: Session = Depends(get_db)):
    """POST /api/inventario/salida - registrar salida/dispensación de stock.

    La base de datos rechaza (vía trigger) una salida mayor al disponible,
    devolviendo un error 400 con el detalle.
    """
    inv = _obtener_o_lanzar_inventario(db, payload.id_medicamento, payload.id_sede)

    mov = MovimientoInventario(
        id_inventario=inv.id_inventario,
        tipo_movimiento="salida",
        cantidad=payload.cantidad,
        stock_anterior=0,
        stock_nuevo=0,
        id_operador=payload.id_operador,
        fuente=payload.fuente,
    )
    db.add(mov)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc.orig)) from exc
    db.refresh(mov)
    return mov


@router.get("/movimientos/{id_medicamento}", response_model=list[MovimientoOut])
def historial_movimientos(
    id_medicamento: int,
    id_sede: int | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """GET /api/inventario/movimientos/{medicamento_id} - historial de trazabilidad."""
    query = (
        db.query(MovimientoInventario)
        .join(Inventario, MovimientoInventario.id_inventario == Inventario.id_inventario)
        .filter(Inventario.id_medicamento == id_medicamento)
    )
    if id_sede:
        query = query.filter(Inventario.id_sede == id_sede)
    return (
        query.order_by(MovimientoInventario.fecha_hora.desc())
        .limit(limit)
        .all()
    )
