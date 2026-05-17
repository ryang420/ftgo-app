from fastapi import Depends
from functools import lru_cache
from sqlalchemy.orm import Session

from order_service.application.orders import OrderApplicationService
from order_service.config import OrderServiceSettings
from order_service.infrastructure.db import get_db_session
from order_service.infrastructure.db.repositories import SqlAlchemyOrderRepository


@lru_cache
def get_settings() -> OrderServiceSettings:
    return OrderServiceSettings()


def get_order_service(session: Session = Depends(get_db_session)) -> OrderApplicationService:
    return OrderApplicationService(SqlAlchemyOrderRepository(session))
