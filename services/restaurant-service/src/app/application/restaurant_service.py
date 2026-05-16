from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import MenuItem, Restaurant
from app.schemas.restaurant import MenuItemCreate, RestaurantCreate


def list_restaurants(session: Session) -> list[Restaurant]:
    statement = select(Restaurant).options(selectinload(Restaurant.menu_items)).order_by(Restaurant.id)
    return list(session.scalars(statement))


def create_restaurant(session: Session, payload: RestaurantCreate) -> Restaurant:
    restaurant = Restaurant(name=payload.name, slug=payload.slug, cuisine=payload.cuisine)
    restaurant.menu_items = [
        MenuItem(name=item.name, description=item.description, price=item.price)
        for item in payload.menu_items
    ]
    session.add(restaurant)
    session.commit()
    session.refresh(restaurant)
    return restaurant


def get_restaurant(session: Session, restaurant_id: int) -> Restaurant | None:
    statement = (
        select(Restaurant)
        .options(selectinload(Restaurant.menu_items))
        .where(Restaurant.id == restaurant_id)
    )
    return session.scalar(statement)


def list_menu_items(session: Session, restaurant_id: int) -> list[MenuItem]:
    statement = (
        select(MenuItem)
        .where(MenuItem.restaurant_id == restaurant_id)
        .order_by(MenuItem.id)
    )
    return list(session.scalars(statement))


def create_menu_item(
    session: Session,
    restaurant: Restaurant,
    payload: MenuItemCreate,
) -> MenuItem:
    menu_item = MenuItem(
        restaurant_id=restaurant.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    session.add(menu_item)
    session.commit()
    session.refresh(menu_item)
    return menu_item


def get_menu_item(session: Session, restaurant_id: int, menu_item_id: int) -> MenuItem | None:
    statement = select(MenuItem).where(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.id == menu_item_id,
    )
    return session.scalar(statement)
