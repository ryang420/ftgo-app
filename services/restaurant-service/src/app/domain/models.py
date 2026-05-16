from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class MenuItem:
    name: str
    price: Decimal
    description: str | None = None
    restaurant_id: int | None = None
    id: int | None = None


@dataclass(slots=True)
class Restaurant:
    name: str
    slug: str
    cuisine: str
    menu_items: list[MenuItem] = field(default_factory=list)
    id: int | None = None
