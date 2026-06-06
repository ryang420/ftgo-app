from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CreateKitchenTicketLineItemCommand:
    menu_item_id: int
    name: str
    quantity: int


@dataclass(slots=True)
class CreateKitchenTicketCommand:
    order_id: UUID
    restaurant_id: int
    line_items: list[CreateKitchenTicketLineItemCommand]


@dataclass(slots=True)
class AcceptKitchenTicketCommand:
    ticket_id: UUID


@dataclass(slots=True)
class RejectKitchenTicketCommand:
    ticket_id: UUID
    rejection_reason: str | None = None
