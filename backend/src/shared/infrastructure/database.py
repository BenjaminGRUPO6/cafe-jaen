"""Conexión a la base de datos compartida por todos los módulos."""

from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import Session, sessionmaker

# Cada módulo registra sus tablas en este metadata (ver */infrastructure/persistence/tables.py)
metadata = MetaData()


def create_db_engine(database_url: str) -> Engine:
    # check_same_thread solo aplica a SQLite (pruebas y desarrollo local)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
