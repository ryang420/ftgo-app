from dataclasses import dataclass
from typing import Any

from delivery_service.domain.models import Delivery


@dataclass(slots=True)
class OutboxEvent:
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict[str, Any]


def delivery_created_event(delivery: Delivery) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="Delivery",
        aggregate_id=str(delivery.id),
        event_type="DeliveryCreated",
        payload={
            "delivery_id": str(delivery.id),
            "order_id": str(delivery.order_id),
            "restaurant_id": delivery.restaurant_id,
            "delivery_address": delivery.delivery_address,
            "status": delivery.status.value,
        },
    )


def delivery_assigned_event(delivery: Delivery) -> OutboxEvent:
    return _delivery_courier_event(delivery, "DeliveryAssigned")


def delivery_picked_up_event(delivery: Delivery) -> OutboxEvent:
    return _delivery_courier_event(delivery, "DeliveryPickedUp")


def delivery_delivered_event(delivery: Delivery) -> OutboxEvent:
    return _delivery_courier_event(delivery, "DeliveryDelivered")


def _delivery_courier_event(delivery: Delivery, event_type: str) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="Delivery",
        aggregate_id=str(delivery.id),
        event_type=event_type,
        payload={
            "delivery_id": str(delivery.id),
            "order_id": str(delivery.order_id),
            "courier_id": delivery.courier_id,
            "status": delivery.status.value,
        },
    )
