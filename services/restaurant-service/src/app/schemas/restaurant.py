from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0)


class MenuItemRead(MenuItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    cuisine: str = Field(min_length=1, max_length=120)
    menu_items: list[MenuItemCreate] = Field(default_factory=list)


class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    cuisine: str
    menu_items: list[MenuItemRead] = Field(default_factory=list)
