from common.db import build_engine, build_session_factory

from app.config import OrderServiceSettings


def create_engine_and_session_factory(settings: OrderServiceSettings):
    engine = build_engine(settings.database_url, echo=settings.sql_echo)
    session_factory = build_session_factory(engine)
    return engine, session_factory
