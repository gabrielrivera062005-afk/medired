"""
MEDIRED - Conexión a la base de datos (SQLAlchemy).
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DATABASE_URL, DB_SCHEMA

engine = create_engine(
    DATABASE_URL,
    # Fija el search_path del schema "medired" en cada conexión
    connect_args={"options": f"-csearch_path={DB_SCHEMA}"},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Todas las tablas de los modelos quedan asociadas al schema medired
metadata = MetaData(schema=DB_SCHEMA)
Base = declarative_base(metadata=metadata)


def get_db():
    """Dependencia de FastAPI: entrega una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
