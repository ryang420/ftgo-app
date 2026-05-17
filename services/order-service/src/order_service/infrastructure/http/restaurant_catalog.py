from decimal import Decimal

import httpx

from order_service.application.errors import MenuItemNotFoundError, RestaurantNotFoundError
from order_service.application.ports import MenuItemSnapshot, RestaurantCatalog


class HttpRestaurantCatalog(RestaurantCatalog):
    def __init__(self, *, base_url: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds)

    async def ensure_restaurant_exists(self, restaurant_id: int) -> None:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/restaurants/{restaurant_id}")

        if response.status_code == 404:
            raise RestaurantNotFoundError(restaurant_id)
        response.raise_for_status()

    async def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItemSnapshot:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/restaurants/{restaurant_id}/menu-items/{menu_item_id}"
            )

        if response.status_code == 404:
            raise MenuItemNotFoundError(restaurant_id, menu_item_id)
        response.raise_for_status()

        payload = response.json()
        return MenuItemSnapshot(
            id=payload["id"],
            restaurant_id=payload["restaurant_id"],
            name=payload["name"],
            price=Decimal(str(payload["price"])),
        )
