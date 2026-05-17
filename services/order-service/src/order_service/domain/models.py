from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from decimal import Decimal


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass(slots=True)
class OrderLineItem:
    menu_item_id: uuid.UUID
    name: str
    quantity: int
    unit_price: Decimal
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(slots=True)
class Order:
    consumer_id: uuid.UUID
    restaurant_id: uuid.UUID
    currency: str
    line_items: list[OrderLineItem]
    status: OrderStatus = OrderStatus.PENDING
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        self.currency = self.currency.upper()
        if not self.line_items:
            raise ValueError("An order must contain at least one line item")

    @property
    def total_amount(self) -> Decimal:
        return sum((item.subtotal() for item in self.line_items), start=Decimal("0.00"))

    @classmethod
    def create_pending(
        cls,
        *,
        consumer_id: uuid.UUID,
        restaurant_id: uuid.UUID,
        currency: str,
        line_items: list[OrderLineItem],
    ) -> Order:
        return cls(
            consumer_id=consumer_id,
            restaurant_id=restaurant_id,
            currency=currency,
            line_items=line_items,
            status=OrderStatus.PENDING,
        )
