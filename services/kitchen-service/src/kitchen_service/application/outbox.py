from dataclasses import dataclass
from typing import Any

from kitchen_service.domain.models import KitchenTicket


@dataclass(slots=True)
class OutboxEvent:
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict[str, Any]


def kitchen_ticket_created_event(ticket: KitchenTicket) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="KitchenTicket",
        aggregate_id=str(ticket.id),
        event_type="KitchenTicketCreated",
        payload={
            "ticket_id": str(ticket.id),
            "order_id": str(ticket.order_id),
            "restaurant_id": ticket.restaurant_id,
            "delivery_address": ticket.delivery_address,
            "status": ticket.status.value,
            "line_items": [
                {
                    "id": str(item.id),
                    "menu_item_id": item.menu_item_id,
                    "name": item.name,
                    "quantity": item.quantity,
                }
                for item in ticket.line_items
            ],
        },
    )


def kitchen_ticket_accepted_event(ticket: KitchenTicket) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="KitchenTicket",
        aggregate_id=str(ticket.id),
        event_type="KitchenTicketAccepted",
        payload={
            "ticket_id": str(ticket.id),
            "order_id": str(ticket.order_id),
            "restaurant_id": ticket.restaurant_id,
            "status": ticket.status.value,
        },
    )


def kitchen_ticket_rejected_event(
    ticket: KitchenTicket,
    rejection_reason: str | None = None,
) -> OutboxEvent:
    payload: dict[str, Any] = {
        "ticket_id": str(ticket.id),
        "order_id": str(ticket.order_id),
        "restaurant_id": ticket.restaurant_id,
        "status": ticket.status.value,
    }
    if rejection_reason is not None:
        payload["rejection_reason"] = rejection_reason
    return OutboxEvent(
        aggregate_type="KitchenTicket",
        aggregate_id=str(ticket.id),
        event_type="KitchenTicketRejected",
        payload=payload,
    )


def kitchen_ticket_preparing_event(ticket: KitchenTicket) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="KitchenTicket",
        aggregate_id=str(ticket.id),
        event_type="KitchenTicketPreparing",
        payload={
            "ticket_id": str(ticket.id),
            "order_id": str(ticket.order_id),
            "restaurant_id": ticket.restaurant_id,
            "status": ticket.status.value,
        },
    )


def kitchen_ticket_ready_for_pickup_event(ticket: KitchenTicket) -> OutboxEvent:
    return OutboxEvent(
        aggregate_type="KitchenTicket",
        aggregate_id=str(ticket.id),
        event_type="KitchenTicketReadyForPickup",
        payload={
            "ticket_id": str(ticket.id),
            "order_id": str(ticket.order_id),
            "restaurant_id": ticket.restaurant_id,
            "delivery_address": ticket.delivery_address,
            "status": ticket.status.value,
        },
    )
