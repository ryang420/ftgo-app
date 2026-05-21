import pytest
from api_gateway.api.dependencies import get_upstream_proxy
from api_gateway.infrastructure.upstream import UpstreamProxy
from api_gateway.main import app
from fastapi import Response
from fastapi.testclient import TestClient


class StubProxy(UpstreamProxy):
    def __init__(self):
        self.calls: list[tuple[str, str, str]] = []

    async def forward(self, request, *, service_key: str, path: str = ""):
        self.calls.append((service_key, path, request.method))
        return Response(
            content=f'{{"service":"{service_key}","path":"{path}"}}',
            media_type="application/json",
        )


@pytest.fixture
def stub_proxy() -> StubProxy:
    proxy = StubProxy()
    app.dependency_overrides[get_upstream_proxy] = lambda: proxy
    yield proxy
    app.dependency_overrides.clear()


def test_routes_to_consumer_service(stub_proxy: StubProxy) -> None:
    response = TestClient(app).get("/consumers/abc")

    assert response.status_code == 200
    assert response.json() == {"service": "consumers", "path": "abc"}
    assert stub_proxy.calls == [("consumers", "abc", "GET")]


def test_routes_to_restaurant_service(stub_proxy: StubProxy) -> None:
    response = TestClient(app).post("/restaurants/42/menu-items", json={"name": "Soup"})

    assert response.status_code == 200
    assert response.json() == {"service": "restaurants", "path": "42/menu-items"}
    assert stub_proxy.calls == [("restaurants", "42/menu-items", "POST")]


def test_routes_to_order_service(stub_proxy: StubProxy) -> None:
    response = TestClient(app).get("/orders?limit=10")

    assert response.status_code == 200
    assert response.json() == {"service": "orders", "path": ""}
    assert stub_proxy.calls == [("orders", "", "GET")]


def test_routes_to_kitchen_service(stub_proxy: StubProxy) -> None:
    response = TestClient(app).get("/kitchen/tickets")

    assert response.status_code == 200
    assert response.json() == {"service": "kitchen", "path": "tickets"}
    assert stub_proxy.calls == [("kitchen", "tickets", "GET")]
