from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    PREPARING = "PREPARING"
    READY = "READY"


class InvalidOrderStatusTransitionError(Exception):
    def __init__(self, current: OrderStatus, target: OrderStatus):
        self.current = current
        self.target = target
        super().__init__(f"Cannot transition order from {current.value} to {target.value}")


@dataclass(slots=True)
class OrderLineItem:
    menu_item_id: int
    name: str
    quantity: int
    unit_price: Decimal
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(slots=True)
class Order:
    consumer_id: uuid.UUID
    restaurant_id: int
    currency: str
    delivery_address: str
    line_items: list[OrderLineItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        self.currency = self.currency.upper()
        if not self.line_items:
            raise ValueError("An order must contain at least one line item")
        if not self.delivery_address or not self.delivery_address.strip():
            raise ValueError("Delivery address is required")

    @property
    def total_amount(self) -> Decimal:
        return sum((item.subtotal() for item in self.line_items), start=Decimal("0.00"))

    def approve(self) -> None:
        if self.status == OrderStatus.APPROVED:
            return
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.APPROVED)
        self.status = OrderStatus.APPROVED

    def reject(self) -> None:
        if self.status == OrderStatus.REJECTED:
            return
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.REJECTED)
        self.status = OrderStatus.REJECTED

    def mark_ready(self) -> None:
        if self.status == OrderStatus.READY:
            return
        if self.status != OrderStatus.PREPARING:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.READY)
        self.status = OrderStatus.READY

    def begin_preparing(self) -> None:
        if self.status == OrderStatus.PREPARING:
            return
        if self.status not in {OrderStatus.APPROVED, OrderStatus.PREPARING}:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.PREPARING)
        self.status = OrderStatus.PREPARING

    def cancel(self) -> None:
        if self.status == OrderStatus.CANCELLED:
            return
        if self.status not in {OrderStatus.PENDING, OrderStatus.APPROVED, OrderStatus.PREPARING}:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.CANCELLED)
        self.status = OrderStatus.CANCELLED

    @classmethod
    def create_pending(
        cls,
        *,
        consumer_id: uuid.UUID,
        restaurant_id: int,
        currency: str,
        delivery_address: str,
        line_items: list[OrderLineItem],
    ) -> Order:
        return cls(
            consumer_id=consumer_id,
            restaurant_id=restaurant_id,
            currency=currency,
            delivery_address=delivery_address,
            line_items=line_items,
            status=OrderStatus.PENDING,
        )
