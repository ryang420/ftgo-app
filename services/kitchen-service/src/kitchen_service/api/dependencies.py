from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.infrastructure.db import get_db_session
from kitchen_service.infrastructure.db.repositories import (
    SqlAlchemyKitchenTicketRepository,
    SqlAlchemyOutboxWriter,
    SqlAlchemyUnitOfWork,
)


def get_ticket_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> KitchenTicketApplicationService:
    return KitchenTicketApplicationService(
        ticket_repository=SqlAlchemyKitchenTicketRepository(session),
        outbox=SqlAlchemyOutboxWriter(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )
