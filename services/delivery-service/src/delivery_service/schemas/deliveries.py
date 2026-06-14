from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from delivery_service.domain.models import Delivery, DeliveryStatus


class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    restaurant_id: int
    delivery_address: str
    status: DeliveryStatus
    courier_id: str | None = None


class AssignCourierRequest(BaseModel):
    courier_id: str

    @field_validator("courier_id")
    @classmethod
    def courier_id_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Courier id is required")
        return normalized


def to_delivery_read(delivery: Delivery) -> DeliveryRead:
    return DeliveryRead(
        id=delivery.id,
        order_id=delivery.order_id,
        restaurant_id=delivery.restaurant_id,
        delivery_address=delivery.delivery_address,
        status=delivery.status,
        courier_id=delivery.courier_id,
    )
