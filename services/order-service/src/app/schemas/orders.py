from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import OrderStatus


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
