from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from restaurant_service.api.dependencies import get_restaurant_service
from restaurant_service.application.restaurants import RestaurantApplicationService
from restaurant_service.schemas.restaurant import (
    MenuItemCreate,
    MenuItemRead,
    RestaurantCreate,
    RestaurantRead,
    to_create_menu_item_command,
    to_create_restaurant_command,
    to_menu_item_read,
    to_restaurant_read,
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("", response_model=list[RestaurantRead])
def read_restaurants(
    service: Annotated[RestaurantApplicationService, Depends(get_restaurant_service)],
) -> list[RestaurantRead]:
    return [to_restaurant_read(restaurant) for restaurant in service.list_restaurants()]


@router.post("", response_model=RestaurantRead, status_code=status.HTTP_201_CREATED)
def create_restaurant_endpoint(
    payload: RestaurantCreate,
    service: Annotated[RestaurantApplicationService, Depends(get_restaurant_service)],
) -> RestaurantRead:
    command = to_create_restaurant_command(payload)
    try:
        return to_restaurant_read(service.create_restaurant(command))
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Restaurant slug already exists.",
        ) from exc


@router.get("/{restaurant_id}", response_model=RestaurantRead)
def read_restaurant(
    restaurant_id: int,
    service: Annotated[RestaurantApplicationService, Depends(get_restaurant_service)],
) -> RestaurantRead:
    restaurant = service.get_restaurant(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return to_restaurant_read(restaurant)


@router.get("/{restaurant_id}/menu-items", response_model=list[MenuItemRead], tags=["menu-items"])
def read_menu_items(
    restaurant_id: int,
    service: Annotated[RestaurantApplicationService, Depends(get_restaurant_service)],
) -> list[MenuItemRead]:
    restaurant = service.get_restaurant(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return [to_menu_item_read(menu_item) for menu_item in service.list_menu_items(restaurant_id)]


@router.post(
    "/{restaurant_id}/menu-items",
    response_model=MenuItemRead,
    status_code=status.HTTP_201_CREATED,
    tags=["menu-items"],
)
def create_menu_item_endpoint(
    restaurant_id: int,
    payload: MenuItemCreate,
    service: Annotated[RestaurantApplicationService, Depends(get_restaurant_service)],
) -> MenuItemRead:
    restaurant = service.get_restaurant(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    command = to_create_menu_item_command(payload)
    return to_menu_item_read(service.create_menu_item(restaurant_id, command))


@router.get(
    "/{restaurant_id}/menu-items/{menu_item_id}",
    response_model=MenuItemRead,
    tags=["menu-items"],
)
def read_menu_item(
    restaurant_id: int,
    menu_item_id: int,
    service: Annotated[RestaurantApplicationService, Depends(get_restaurant_service)],
) -> MenuItemRead:
    menu_item = service.get_menu_item(restaurant_id, menu_item_id)
    if menu_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found.")
    return to_menu_item_read(menu_item)
