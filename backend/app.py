"""
MEDIRED - App principal (FastAPI).

Ejecutar en desarrollo:
    uvicorn app:app --reload

Documentación interactiva (Swagger UI) en:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from routes import medicamentos, sedes, inventario

app = FastAPI(
    title="MEDIRED API",
    description="Plataforma interoperable para consulta, gestión y "
                 "trazabilidad de medicamentos (piloto Nueva EPS - Bogotá).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(medicamentos.router)
app.include_router(sedes.router)
app.include_router(inventario.router)


@app.get("/", tags=["health"])
def root():
    """Health check simple."""
    return {"status": "ok", "servicio": "MEDIRED API", "version": "0.1.0"}
