from functools import lru_cache

from api_gateway.config import ApiGatewaySettings, get_settings
from api_gateway.infrastructure.upstream import UpstreamProxy


@lru_cache
def get_upstream_proxy() -> UpstreamProxy:
    settings: ApiGatewaySettings = get_settings()
    return UpstreamProxy(
        timeout_seconds=settings.upstream_timeout_seconds,
        upstreams={
            "consumers": settings.consumer_service_url,
            "restaurants": settings.restaurant_service_url,
            "orders": settings.order_service_url,
        },
    )
