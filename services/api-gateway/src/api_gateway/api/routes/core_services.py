from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from api_gateway.api.dependencies import get_upstream_proxy
from api_gateway.infrastructure.upstream import UpstreamProxy

router = APIRouter(tags=["gateway"])


@router.api_route("/consumers", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@router.api_route("/consumers/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_consumers(
    request: Request,
    proxy: Annotated[UpstreamProxy, Depends(get_upstream_proxy)],
    path: str = "",
) -> Response:
    return await proxy.forward(request, service_key="consumers", path=path)


@router.api_route("/restaurants", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@router.api_route("/restaurants/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_restaurants(
    request: Request,
    proxy: Annotated[UpstreamProxy, Depends(get_upstream_proxy)],
    path: str = "",
) -> Response:
    return await proxy.forward(request, service_key="restaurants", path=path)


@router.api_route("/orders", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@router.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_orders(
    request: Request,
    proxy: Annotated[UpstreamProxy, Depends(get_upstream_proxy)],
    path: str = "",
) -> Response:
    return await proxy.forward(request, service_key="orders", path=path)
