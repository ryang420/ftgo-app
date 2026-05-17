from dataclasses import dataclass
from typing import Any

from order_service.domain.models import Order


@dataclass(slots=True)
class OutboxEvent:
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict[str, Any]


def order_created_event(order: Order) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="Order",
        aggregate_id=str(order.id),
        event_type="OrderCreated",
        payload={
            "order_id": str(order.id),
            "consumer_id": str(order.consumer_id),
            "restaurant_id": order.restaurant_id,
            "status": order.status.value,
            "currency": order.currency,
            "total_amount": str(order.total_amount),
            "line_items": [
                {
                    "id": str(item.id),
                    "menu_item_id": item.menu_item_id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                }
                for item in order.line_items
            ],
        },
    )
