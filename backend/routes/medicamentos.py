"""
MEDIRED - Fase 1: catálogo de medicamentos.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import Medicamento
from schemas import MedicamentoOut, MedicamentoCreate

router = APIRouter(prefix="/api/medicamentos", tags=["medicamentos"])


@router.get("", response_model=list[MedicamentoOut])
def buscar_medicamentos(
    q: Optional[str] = Query(None, description="Busca por nombre o principio activo"),
    solo_activos: bool = True,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """GET /api/medicamentos?q=acetaminofen - buscar/listar medicamentos."""
    query = db.query(Medicamento)
    if solo_activos:
        query = query.filter(Medicamento.activo.is_(True))
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Medicamento.nombre.ilike(like), Medicamento.principio_activo.ilike(like))
        )
    return query.order_by(Medicamento.nombre).offset(offset).limit(limit).all()


@router.get("/{id_medicamento}", response_model=MedicamentoOut)
def obtener_medicamento(id_medicamento: int, db: Session = Depends(get_db)):
    """GET /api/medicamentos/{id} - detalle de un medicamento."""
    med = db.get(Medicamento, id_medicamento)
    if not med:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")
    return med


@router.post("", response_model=MedicamentoOut, status_code=201)
def crear_medicamento(payload: MedicamentoCreate, db: Session = Depends(get_db)):
    """POST /api/medicamentos - registrar un medicamento en el catálogo.

    Uso típico: cargar catálogo desde datos abiertos INVIMA/SISMED
    (ver database/README.md), no para captura manual masiva.
    """
    nuevo = Medicamento(**payload.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
