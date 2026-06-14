from uuid import uuid4

from delivery_service.api.dependencies import get_delivery_service
from delivery_service.domain.models import (
    Delivery,
    DeliveryStatus,
)
from delivery_service.main import app
from fastapi.testclient import TestClient


class _FakeDeliveryService:
    def __init__(self) -> None:
        self.delivery = Delivery.create_pending(
            order_id=uuid4(),
            restaurant_id=7,
            delivery_address="123 Main St",
        )

    def list_deliveries(self) -> list[Delivery]:
        return [self.delivery]

    def get_delivery(self, delivery_id):
        if delivery_id == self.delivery.id:
            return self.delivery
        return None

    def assign_courier(self, delivery_id, courier_id: str):
        delivery = self.get_delivery(delivery_id)
        if delivery is None:
            return None
        delivery.assign(courier_id)
        return delivery

    def mark_picked_up(self, delivery_id):
        delivery = self.get_delivery(delivery_id)
        if delivery is None:
            return None
        delivery.mark_picked_up()
        return delivery

    def mark_delivered(self, delivery_id):
        delivery = self.get_delivery(delivery_id)
        if delivery is None:
            return None
        delivery.mark_delivered()
        return delivery


def _client(fake_service: _FakeDeliveryService) -> TestClient:
    app.dependency_overrides[get_delivery_service] = lambda: fake_service
    return TestClient(app)


def test_list_deliveries_returns_delivery_representations() -> None:
    fake_service = _FakeDeliveryService()
    client = _client(fake_service)

    response = client.get("/deliveries")

    assert response.status_code == 200
    assert response.json()[0]["id"] == str(fake_service.delivery.id)
    assert response.json()[0]["status"] == "PENDING_ASSIGNMENT"
    app.dependency_overrides.clear()


def test_assign_pickup_and_deliver_delivery() -> None:
    fake_service = _FakeDeliveryService()
    client = _client(fake_service)
    delivery_id = fake_service.delivery.id

    assigned = client.post(f"/deliveries/{delivery_id}/assign", json={"courier_id": "courier-001"})
    picked_up = client.post(f"/deliveries/{delivery_id}/pickup")
    delivered = client.post(f"/deliveries/{delivery_id}/deliver")

    assert assigned.status_code == 200
    assert assigned.json()["status"] == "ASSIGNED"
    assert assigned.json()["courier_id"] == "courier-001"
    assert picked_up.status_code == 200
    assert picked_up.json()["status"] == "PICKED_UP"
    assert delivered.status_code == 200
    assert delivered.json()["status"] == "DELIVERED"
    app.dependency_overrides.clear()


def test_unknown_delivery_returns_404() -> None:
    fake_service = _FakeDeliveryService()
    client = _client(fake_service)

    response = client.post(f"/deliveries/{uuid4()}/pickup")

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_invalid_transition_returns_409() -> None:
    fake_service = _FakeDeliveryService()
    fake_service.delivery.status = DeliveryStatus.DELIVERED
    client = _client(fake_service)

    response = client.post(f"/deliveries/{fake_service.delivery.id}/pickup")

    assert response.status_code == 409
    assert response.json()["detail"]["current_status"] == "DELIVERED"
    assert response.json()["detail"]["target_status"] == "PICKED_UP"
    app.dependency_overrides.clear()


def test_blank_courier_id_returns_422() -> None:
    fake_service = _FakeDeliveryService()
    client = _client(fake_service)

    response = client.post(
        f"/deliveries/{fake_service.delivery.id}/assign",
        json={"courier_id": "  "},
    )

    assert response.status_code == 422
    app.dependency_overrides.clear()
