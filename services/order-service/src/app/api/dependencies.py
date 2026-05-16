from fastapi import Depends
from functools import lru_cache
from sqlalchemy.orm import Session

from app.application.orders import OrderApplicationService
from app.config import OrderServiceSettings
from app.infrastructure.db import get_db_session
from app.infrastructure.db.repositories import SqlAlchemyOrderRepository


@lru_cache
def get_settings() -> OrderServiceSettings:
    return OrderServiceSettings()


def get_order_service(session: Session = Depends(get_db_session)) -> OrderApplicationService:
    return OrderApplicationService(SqlAlchemyOrderRepository(session))
