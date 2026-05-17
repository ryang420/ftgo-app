from fastapi import Depends
from functools import lru_cache
from sqlalchemy.orm import Session

from order_service.application.orders import OrderApplicationService
from order_service.config import OrderServiceSettings
from order_service.infrastructure.db import get_db_session
from order_service.infrastructure.db.repositories import SqlAlchemyOrderRepository
from order_service.infrastructure.http.consumer_registry import HttpConsumerRegistry
from order_service.infrastructure.http.restaurant_catalog import HttpRestaurantCatalog


@lru_cache
def get_settings() -> OrderServiceSettings:
    return OrderServiceSettings()


def get_order_service(session: Session = Depends(get_db_session)) -> OrderApplicationService:
    settings = get_settings()
    return OrderApplicationService(
        order_repository=SqlAlchemyOrderRepository(session),
        restaurant_catalog=HttpRestaurantCatalog(
            base_url=settings.restaurant_service_url,
            timeout_seconds=settings.upstream_timeout_seconds,
        ),
        consumer_registry=HttpConsumerRegistry(
            base_url=settings.consumer_service_url,
            timeout_seconds=settings.upstream_timeout_seconds,
        ),
    )
