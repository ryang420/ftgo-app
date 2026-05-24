from __future__ import annotations

from typing import Protocol
from uuid import UUID

from kitchen_service.domain.models import KitchenTicket


class KitchenTicketRepository(Protocol):
    def list_tickets(self) -> list[KitchenTicket]:
        ...

    def get_by_id(self, ticket_id: UUID) -> KitchenTicket | None:
        ...

    def get_by_order_id(self, order_id: UUID) -> KitchenTicket | None:
        ...

    def add(self, ticket: KitchenTicket) -> KitchenTicket:
        ...

    def save(self, ticket: KitchenTicket) -> KitchenTicket:
        ...
