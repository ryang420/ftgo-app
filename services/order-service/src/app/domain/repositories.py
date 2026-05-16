from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.models import Order


class OrderRepository(Protocol):
    def list_orders(self) -> list[Order]:
        ...

    def get_order(self, order_id: UUID) -> Order | None:
        ...

    def add(self, order: Order) -> Order:
        ...
