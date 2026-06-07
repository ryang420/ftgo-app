from uuid import UUID

from pydantic import BaseModel, ConfigDict

from kitchen_service.domain.models import (
    KitchenTicket,
    KitchenTicketLineItem,
    KitchenTicketStatus,
)


class KitchenTicketLineItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    menu_item_id: int
    name: str
    quantity: int


class KitchenTicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    restaurant_id: int
    status: KitchenTicketStatus
    line_items: list[KitchenTicketLineItemRead]


def to_line_item_read(line_item: KitchenTicketLineItem) -> KitchenTicketLineItemRead:
    return KitchenTicketLineItemRead(
        id=line_item.id,
        menu_item_id=line_item.menu_item_id,
        name=line_item.name,
        quantity=line_item.quantity,
    )


class RejectTicketRequest(BaseModel):
    rejection_reason: str | None = None


def to_ticket_read(ticket: KitchenTicket) -> KitchenTicketRead:
    return KitchenTicketRead(
        id=ticket.id,
        order_id=ticket.order_id,
        restaurant_id=ticket.restaurant_id,
        status=ticket.status,
        line_items=[to_line_item_read(item) for item in ticket.line_items],
    )
