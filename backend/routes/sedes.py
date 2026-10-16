"""
MEDIRED - Fase 2: sedes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Sede
from schemas import SedeOut

router = APIRouter(prefix="/api/sedes", tags=["sedes"])


@router.get("", response_model=list[SedeOut])
def listar_sedes(
    localidad: str | None = Query(None, description="Filtrar por localidad de Bogotá"),
    solo_activas: bool = True,
    db: Session = Depends(get_db),
):
    """GET /api/sedes - listar sedes, opcionalmente filtradas por localidad."""
    query = db.query(Sede)
    if solo_activas:
        query = query.filter(Sede.activo.is_(True))
    if localidad:
        query = query.filter(Sede.localidad.ilike(f"%{localidad}%"))
    return query.order_by(Sede.nombre).all()


@router.get("/{id_sede}", response_model=SedeOut)
def obtener_sede(id_sede: int, db: Session = Depends(get_db)):
    """GET /api/sedes/{id} - detalle de una sede."""
    sede = db.get(Sede, id_sede)
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    return sede
