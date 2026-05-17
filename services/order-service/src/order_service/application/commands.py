from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class CreateOrderLineItemCommand:
    menu_item_id: int
    quantity: int


@dataclass(slots=True)
class CreateOrderCommand:
    consumer_id: UUID
    restaurant_id: int
    currency: str
    line_items: list[CreateOrderLineItemCommand]
