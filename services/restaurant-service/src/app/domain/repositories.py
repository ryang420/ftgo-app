from __future__ import annotations

from typing import Protocol

from app.domain.models import MenuItem, Restaurant


class RestaurantRepository(Protocol):
    def list_restaurants(self) -> list[Restaurant]:
        ...

    def get_restaurant(self, restaurant_id: int) -> Restaurant | None:
        ...

    def add(self, restaurant: Restaurant) -> Restaurant:
        ...


class MenuItemRepository(Protocol):
    def list_menu_items(self, restaurant_id: int) -> list[MenuItem]:
        ...

    def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItem | None:
        ...

    def add(self, menu_item: MenuItem) -> MenuItem:
        ...
