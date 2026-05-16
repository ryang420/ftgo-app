from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class CreateOrderLineItemCommand:
    menu_item_id: UUID
    name: str
    quantity: int
    unit_price: Decimal


@dataclass(slots=True)
class CreateOrderCommand:
    consumer_id: UUID
    restaurant_id: UUID
    currency: str
    line_items: list[CreateOrderLineItemCommand]
