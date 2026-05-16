from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.restaurants import RestaurantApplicationService
from app.infrastructure.db import get_db_session
from app.infrastructure.db.repositories import SqlAlchemyMenuItemRepository, SqlAlchemyRestaurantRepository


def get_restaurant_service(session: Session = Depends(get_db_session)) -> RestaurantApplicationService:
    return RestaurantApplicationService(
        restaurant_repository=SqlAlchemyRestaurantRepository(session),
        menu_item_repository=SqlAlchemyMenuItemRepository(session),
    )
