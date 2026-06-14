from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class DeliveryStatus(StrEnum):
    PENDING_ASSIGNMENT = "PENDING_ASSIGNMENT"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class InvalidDeliveryStatusTransitionError(Exception):
    def __init__(self, current: DeliveryStatus, target: DeliveryStatus):
        self.current = current
        self.target = target
        super().__init__(f"Cannot transition delivery from {current.value} to {target.value}")


@dataclass(slots=True)
class Delivery:
    order_id: uuid.UUID
    restaurant_id: int
    delivery_address: str
    status: DeliveryStatus = DeliveryStatus.PENDING_ASSIGNMENT
    courier_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self) -> None:
        if not self.delivery_address or not self.delivery_address.strip():
            raise ValueError("Delivery address is required")
        if self.status in {
            DeliveryStatus.ASSIGNED,
            DeliveryStatus.PICKED_UP,
            DeliveryStatus.DELIVERED,
        } and not self.courier_id:
            raise ValueError("Courier id is required once a delivery is assigned")

    def assign(self, courier_id: str) -> None:
        normalized_courier_id = courier_id.strip()
        if not normalized_courier_id:
            raise ValueError("Courier id is required")
        if self.status == DeliveryStatus.ASSIGNED:
            if self.courier_id == normalized_courier_id:
                return
            raise InvalidDeliveryStatusTransitionError(
                self.status,
                DeliveryStatus.ASSIGNED,
            )
        if self.status != DeliveryStatus.PENDING_ASSIGNMENT:
            raise InvalidDeliveryStatusTransitionError(
                self.status,
                DeliveryStatus.ASSIGNED,
            )
        self.courier_id = normalized_courier_id
        self.status = DeliveryStatus.ASSIGNED

    def mark_picked_up(self) -> None:
        if self.status == DeliveryStatus.PICKED_UP:
            return
        if self.status != DeliveryStatus.ASSIGNED:
            raise InvalidDeliveryStatusTransitionError(
                self.status,
                DeliveryStatus.PICKED_UP,
            )
        self.status = DeliveryStatus.PICKED_UP

    def mark_delivered(self) -> None:
        if self.status == DeliveryStatus.DELIVERED:
            return
        if self.status != DeliveryStatus.PICKED_UP:
            raise InvalidDeliveryStatusTransitionError(
                self.status,
                DeliveryStatus.DELIVERED,
            )
        self.status = DeliveryStatus.DELIVERED

    @classmethod
    def create_pending(
        cls,
        *,
        order_id: uuid.UUID,
        restaurant_id: int,
        delivery_address: str,
    ) -> Delivery:
        return cls(
            order_id=order_id,
            restaurant_id=restaurant_id,
            delivery_address=delivery_address,
            status=DeliveryStatus.PENDING_ASSIGNMENT,
        )
