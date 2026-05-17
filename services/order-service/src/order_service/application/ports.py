from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID


@dataclass(slots=True)
class MenuItemSnapshot:
    id: int
    restaurant_id: int
    name: str
    price: Decimal


class RestaurantCatalog(Protocol):
    async def ensure_restaurant_exists(self, restaurant_id: int) -> None:
        ...

    async def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItemSnapshot:
        ...


class ConsumerRegistry(Protocol):
    async def ensure_consumer_exists(self, consumer_id: UUID) -> None:
        ...
