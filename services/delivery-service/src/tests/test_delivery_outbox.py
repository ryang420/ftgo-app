from uuid import uuid4

from delivery_service.application.outbox import (
    delivery_assigned_event,
    delivery_created_event,
    delivery_delivered_event,
    delivery_picked_up_event,
)
from delivery_service.domain.models import Delivery


def test_delivery_created_event_contains_handoff_payload() -> None:
    delivery = Delivery.create_pending(
        order_id=uuid4(),
        restaurant_id=7,
        delivery_address="123 Main St",
    )

    event = delivery_created_event(delivery)

    assert event.aggregate_type == "Delivery"
    assert event.aggregate_id == str(delivery.id)
    assert event.event_type == "DeliveryCreated"
    assert event.payload == {
        "delivery_id": str(delivery.id),
        "order_id": str(delivery.order_id),
        "restaurant_id": 7,
        "delivery_address": "123 Main St",
        "status": "PENDING_ASSIGNMENT",
    }


def test_delivery_lifecycle_events_contain_courier_payload() -> None:
    delivery = Delivery.create_pending(
        order_id=uuid4(),
        restaurant_id=7,
        delivery_address="123 Main St",
    )
    delivery.assign("courier-001")

    assigned = delivery_assigned_event(delivery)
    assert assigned.event_type == "DeliveryAssigned"
    assert assigned.payload["delivery_id"] == str(delivery.id)
    assert assigned.payload["order_id"] == str(delivery.order_id)
    assert assigned.payload["courier_id"] == "courier-001"
    assert assigned.payload["status"] == "ASSIGNED"

    delivery.mark_picked_up()
    picked_up = delivery_picked_up_event(delivery)
    assert picked_up.event_type == "DeliveryPickedUp"
    assert picked_up.payload["status"] == "PICKED_UP"

    delivery.mark_delivered()
    delivered = delivery_delivered_event(delivery)
    assert delivered.event_type == "DeliveryDelivered"
    assert delivered.payload["status"] == "DELIVERED"
