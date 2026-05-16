from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True)
class ConsumerAddress:
    label: str
    street1: str
    city: str
    state: str
    postal_code: str
    country: str = "US"
    street2: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        self.country = self.country.upper()


@dataclass(slots=True)
class ConsumerProfile:
    email: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    addresses: list[ConsumerAddress] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime | None = None
    updated_at: datetime | None = None
