from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import StrEnum


class KitchenTicketStatus(StrEnum):
    CREATE_PENDING = "CREATE_PENDING"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class KitchenTicketLineItem:
    menu_item_id: int
    name: str
    quantity: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(slots=True)
class KitchenTicket:
    order_id: uuid.UUID
    restaurant_id: int
    line_items: list[KitchenTicketLineItem]
    status: KitchenTicketStatus = KitchenTicketStatus.CREATE_PENDING
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.line_items:
            raise ValueError("A kitchen ticket must contain at least one line item")

    @classmethod
    def create_pending(
        cls,
        *,
        order_id: uuid.UUID,
        restaurant_id: int,
        line_items: list[KitchenTicketLineItem],
    ) -> KitchenTicket:
        return cls(order_id=order_id, restaurant_id=restaurant_id, line_items=line_items)
