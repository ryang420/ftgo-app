from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class CreateMenuItemCommand:
    name: str
    price: Decimal
    description: str | None = None


@dataclass(slots=True)
class CreateRestaurantCommand:
    name: str
    slug: str
    cuisine: str
    menu_items: list[CreateMenuItemCommand] = field(default_factory=list)
