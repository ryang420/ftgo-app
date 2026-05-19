from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.infrastructure.db import get_db_session
from kitchen_service.infrastructure.db.repositories import SqlAlchemyKitchenTicketRepository


def get_ticket_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> KitchenTicketApplicationService:
    return KitchenTicketApplicationService(SqlAlchemyKitchenTicketRepository(session))
