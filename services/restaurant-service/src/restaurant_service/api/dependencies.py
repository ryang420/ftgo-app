from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from restaurant_service.application.restaurants import RestaurantApplicationService
from restaurant_service.infrastructure.db import get_db_session
from restaurant_service.infrastructure.db.repositories import SqlAlchemyMenuItemRepository, SqlAlchemyRestaurantRepository


def get_restaurant_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> RestaurantApplicationService:
    return RestaurantApplicationService(
        restaurant_repository=SqlAlchemyRestaurantRepository(session),
        menu_item_repository=SqlAlchemyMenuItemRepository(session),
    )
