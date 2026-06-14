from __future__ import annotations

from typing import Protocol
from uuid import UUID

from delivery_service.domain.models import Delivery


class DeliveryRepository(Protocol):
    def list_deliveries(self) -> list[Delivery]:
        ...

    def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        ...

    def get_by_order_id(self, order_id: UUID) -> Delivery | None:
        ...

    def add(self, delivery: Delivery) -> Delivery:
        ...

    def save(self, delivery: Delivery) -> Delivery:
        ...
