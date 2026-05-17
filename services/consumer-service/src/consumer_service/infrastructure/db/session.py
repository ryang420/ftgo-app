from collections.abc import Generator

from common.db import Base, build_engine, build_session_factory
from sqlalchemy.orm import Session

from consumer_service.config import get_settings
from . import models  # noqa: F401

settings = get_settings()
engine = build_engine(settings.database_url, echo=settings.sql_echo)
SessionLocal = build_session_factory(engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
