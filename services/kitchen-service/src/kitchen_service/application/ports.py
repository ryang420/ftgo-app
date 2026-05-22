from typing import Protocol

from kitchen_service.application.outbox import OutboxEvent


class OutboxWriter(Protocol):
    def add(self, event: OutboxEvent) -> None:
        ...


class UnitOfWork(Protocol):
    def commit(self) -> None:
        ...
