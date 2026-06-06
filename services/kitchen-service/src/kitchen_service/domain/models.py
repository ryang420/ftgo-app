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


class InvalidKitchenTicketStatusTransitionError(Exception):
    def __init__(self, current: KitchenTicketStatus, target: KitchenTicketStatus):
        self.current = current
        self.target = target
        super().__init__(f"Cannot transition kitchen ticket from {current.value} to {target.value}")


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

    def accept(self) -> None:
        if self.status == KitchenTicketStatus.ACCEPTED:
            return
        if self.status != KitchenTicketStatus.CREATE_PENDING:
            raise InvalidKitchenTicketStatusTransitionError(
                self.status, KitchenTicketStatus.ACCEPTED
            )
        self.status = KitchenTicketStatus.ACCEPTED

    def reject(self) -> None:
        if self.status == KitchenTicketStatus.CANCELLED:
            return
        if self.status != KitchenTicketStatus.CREATE_PENDING:
            raise InvalidKitchenTicketStatusTransitionError(
                self.status, KitchenTicketStatus.CANCELLED
            )
        self.status = KitchenTicketStatus.CANCELLED

    def start_preparing(self) -> None:
        if self.status == KitchenTicketStatus.PREPARING:
            return
        if self.status != KitchenTicketStatus.ACCEPTED:
            raise InvalidKitchenTicketStatusTransitionError(
                self.status, KitchenTicketStatus.PREPARING
            )
        self.status = KitchenTicketStatus.PREPARING

    def mark_ready_for_pickup(self) -> None:
        if self.status == KitchenTicketStatus.READY_FOR_PICKUP:
            return
        if self.status != KitchenTicketStatus.PREPARING:
            raise InvalidKitchenTicketStatusTransitionError(
                self.status, KitchenTicketStatus.READY_FOR_PICKUP
            )
        self.status = KitchenTicketStatus.READY_FOR_PICKUP

    @classmethod
    def create_pending(
        cls,
        *,
        order_id: uuid.UUID,
        restaurant_id: int,
        line_items: list[KitchenTicketLineItem],
    ) -> KitchenTicket:
        return cls(order_id=order_id, restaurant_id=restaurant_id, line_items=line_items)
