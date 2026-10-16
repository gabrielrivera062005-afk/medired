"""
MEDIRED - Configuración del backend.

Lee la conexión a PostgreSQL desde variables de entorno, con valores por
defecto pensados para pgAdmin/PostgreSQL local (ajusta según tu instalación).
"""

import os

DB_USER = os.getenv("MEDIRED_DB_USER", "postgres")
DB_PASSWORD = os.getenv("MEDIRED_DB_PASSWORD", "postgres")
DB_HOST = os.getenv("MEDIRED_DB_HOST", "localhost")
DB_PORT = os.getenv("MEDIRED_DB_PORT", "5432")
DB_NAME = os.getenv("MEDIRED_DB_NAME", "MEDIRED")  # el nombre que le diste en pgAdmin

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# El schema.sql crea todo bajo el schema "medired" (no "public")
DB_SCHEMA = "medired"

# CORS: en desarrollo se permite el frontend local (ajustar en producción)
CORS_ORIGINS = os.getenv(
    "MEDIRED_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")
