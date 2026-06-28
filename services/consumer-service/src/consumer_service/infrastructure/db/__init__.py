"""Database hooks for consumer-service."""

from consumer_service.infrastructure.db.session import (
    Base,
    SessionLocal,
    engine,
    get_db_session,
    init_db,
)

__all__ = ["Base", "SessionLocal", "engine", "get_db_session", "init_db"]
