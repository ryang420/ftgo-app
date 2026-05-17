from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from order_service.domain.models import Order, OrderLineItem, OrderStatus


class OrderLineItemCreate(BaseModel):
    menu_item_id: UUID
    name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(gt=0)


class OrderCreate(BaseModel):
    consumer_id: UUID
    restaurant_id: UUID
    currency: str = Field(default="USD", min_length=3, max_length=3)
    line_items: list[OrderLineItemCreate] = Field(min_length=1)


class OrderLineItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    menu_item_id: UUID
    name: str
    quantity: int
    unit_price: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    consumer_id: UUID
    restaurant_id: UUID
    status: OrderStatus
    currency: str
    total_amount: Decimal
    line_items: list[OrderLineItemRead]


def to_order_line_item_read(line_item: OrderLineItem) -> OrderLineItemRead:
    return OrderLineItemRead(
        id=line_item.id,
        menu_item_id=line_item.menu_item_id,
        name=line_item.name,
        quantity=line_item.quantity,
        unit_price=line_item.unit_price,
    )


def to_order_read(order: Order) -> OrderRead:
    return OrderRead(
        id=order.id,
        consumer_id=order.consumer_id,
        restaurant_id=order.restaurant_id,
        status=order.status,
        currency=order.currency,
        total_amount=order.total_amount,
        line_items=[to_order_line_item_read(item) for item in order.line_items],
    )
