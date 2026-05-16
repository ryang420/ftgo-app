from decimal import Decimal

from pydantic import BaseModel, Field

from app.application.commands import CreateMenuItemCommand, CreateRestaurantCommand
from app.domain.models import MenuItem, Restaurant


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0)


class MenuItemRead(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str | None = None
    price: Decimal


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    cuisine: str = Field(min_length=1, max_length=120)
    menu_items: list[MenuItemCreate] = Field(default_factory=list)


class RestaurantRead(BaseModel):
    id: int
    name: str
    slug: str
    cuisine: str
    menu_items: list[MenuItemRead] = Field(default_factory=list)


def _require_id(value: int | None, field_name: str) -> int:
    if value is None:
        raise ValueError(f"{field_name} must be set on persisted objects")
    return value


def to_create_menu_item_command(payload: MenuItemCreate) -> CreateMenuItemCommand:
    return CreateMenuItemCommand(
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )


def to_create_restaurant_command(payload: RestaurantCreate) -> CreateRestaurantCommand:
    return CreateRestaurantCommand(
        name=payload.name,
        slug=payload.slug,
        cuisine=payload.cuisine,
        menu_items=[to_create_menu_item_command(item) for item in payload.menu_items],
    )


def to_menu_item_read(menu_item: MenuItem) -> MenuItemRead:
    return MenuItemRead(
        id=_require_id(menu_item.id, "menu_item.id"),
        restaurant_id=_require_id(menu_item.restaurant_id, "menu_item.restaurant_id"),
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
    )


def to_restaurant_read(restaurant: Restaurant) -> RestaurantRead:
    return RestaurantRead(
        id=_require_id(restaurant.id, "restaurant.id"),
        name=restaurant.name,
        slug=restaurant.slug,
        cuisine=restaurant.cuisine,
        menu_items=[to_menu_item_read(item) for item in restaurant.menu_items],
    )
