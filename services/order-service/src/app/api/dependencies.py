from functools import lru_cache

from app.application.orders import OrderApplicationService
from app.config import OrderServiceSettings


@lru_cache
def get_settings() -> OrderServiceSettings:
    return OrderServiceSettings()


def get_order_service() -> OrderApplicationService:
    return OrderApplicationService()
