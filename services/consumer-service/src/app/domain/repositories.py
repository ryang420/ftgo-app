from __future__ import annotations

from typing import Protocol

from app.domain.models import ConsumerProfile


class ConsumerRepository(Protocol):
    def list_consumers(self) -> list[ConsumerProfile]:
        ...

    def get_consumer(self, consumer_id: str) -> ConsumerProfile | None:
        ...

    def add(self, consumer: ConsumerProfile) -> ConsumerProfile:
        ...
