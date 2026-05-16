from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.restaurant_service import (
    create_menu_item,
    create_restaurant,
    get_menu_item,
    get_restaurant,
    list_menu_items,
    list_restaurants,
)
from app.infrastructure.db.session import get_db_session
from app.schemas.restaurant import MenuItemCreate, MenuItemRead, RestaurantCreate, RestaurantRead

router = APIRouter(prefix="/restaurants", tags=["restaurants"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=list[RestaurantRead])
def read_restaurants(session: DbSession) -> list[RestaurantRead]:
    return list_restaurants(session)


@router.post("", response_model=RestaurantRead, status_code=status.HTTP_201_CREATED)
def create_restaurant_endpoint(payload: RestaurantCreate, session: DbSession) -> RestaurantRead:
    try:
        return create_restaurant(session, payload)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Restaurant slug already exists.",
        ) from exc


@router.get("/{restaurant_id}", response_model=RestaurantRead)
def read_restaurant(restaurant_id: int, session: DbSession) -> RestaurantRead:
    restaurant = get_restaurant(session, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return restaurant


@router.get("/{restaurant_id}/menu-items", response_model=list[MenuItemRead], tags=["menu-items"])
def read_menu_items(restaurant_id: int, session: DbSession) -> list[MenuItemRead]:
    restaurant = get_restaurant(session, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return list_menu_items(session, restaurant_id)


@router.post(
    "/{restaurant_id}/menu-items",
    response_model=MenuItemRead,
    status_code=status.HTTP_201_CREATED,
    tags=["menu-items"],
)
def create_menu_item_endpoint(
    restaurant_id: int,
    payload: MenuItemCreate,
    session: DbSession,
) -> MenuItemRead:
    restaurant = get_restaurant(session, restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found.")
    return create_menu_item(session, restaurant, payload)


@router.get(
    "/{restaurant_id}/menu-items/{menu_item_id}",
    response_model=MenuItemRead,
    tags=["menu-items"],
)
def read_menu_item(restaurant_id: int, menu_item_id: int, session: DbSession) -> MenuItemRead:
    menu_item = get_menu_item(session, restaurant_id, menu_item_id)
    if menu_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found.")
    return menu_item
