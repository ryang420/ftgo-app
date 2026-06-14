from functools import lru_cache

from common.config import BaseServiceSettings


class ApiGatewaySettings(BaseServiceSettings):
    service_name: str = "api-gateway"
    consumer_service_url: str = "http://localhost:8001"
    restaurant_service_url: str = "http://localhost:8002"
    order_service_url: str = "http://localhost:8003"
    kitchen_service_url: str = "http://localhost:8004"
    delivery_service_url: str = "http://localhost:8005"
    upstream_timeout_seconds: float = 10.0


@lru_cache
def get_settings() -> ApiGatewaySettings:
    return ApiGatewaySettings()
