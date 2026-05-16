from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import MenuItem, Restaurant
from app.domain.repositories import MenuItemRepository, RestaurantRepository
from app.infrastructure.db.mappers import (
    to_domain_menu_item,
    to_domain_restaurant,
    to_menu_item_record,
    to_restaurant_record,
)
from app.infrastructure.db.models import MenuItemRecord, RestaurantRecord


class SqlAlchemyRestaurantRepository(RestaurantRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_restaurants(self) -> list[Restaurant]:
        statement = (
            select(RestaurantRecord)
            .options(selectinload(RestaurantRecord.menu_items))
            .order_by(RestaurantRecord.id)
        )
        return [to_domain_restaurant(record) for record in self.session.scalars(statement).all()]

    def get_restaurant(self, restaurant_id: int) -> Restaurant | None:
        statement = (
            select(RestaurantRecord)
            .options(selectinload(RestaurantRecord.menu_items))
            .where(RestaurantRecord.id == restaurant_id)
        )
        record = self.session.scalar(statement)
        if record is None:
            return None
        return to_domain_restaurant(record)

    def add(self, restaurant: Restaurant) -> Restaurant:
        record = to_restaurant_record(restaurant)
        self.session.add(record)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(record)
        return self.get_restaurant(record.id) or restaurant


class SqlAlchemyMenuItemRepository(MenuItemRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_menu_items(self, restaurant_id: int) -> list[MenuItem]:
        statement = (
            select(MenuItemRecord)
            .where(MenuItemRecord.restaurant_id == restaurant_id)
            .order_by(MenuItemRecord.id)
        )
        return [to_domain_menu_item(record) for record in self.session.scalars(statement).all()]

    def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItem | None:
        statement = select(MenuItemRecord).where(
            MenuItemRecord.restaurant_id == restaurant_id,
            MenuItemRecord.id == menu_item_id,
        )
        record = self.session.scalar(statement)
        if record is None:
            return None
        return to_domain_menu_item(record)

    def add(self, menu_item: MenuItem) -> MenuItem:
        record = to_menu_item_record(menu_item)
        self.session.add(record)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(record)
        return self.get_menu_item(record.restaurant_id, record.id) or menu_item
