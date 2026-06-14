from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from delivery_service.application.deliveries import DeliveryApplicationService
from delivery_service.infrastructure.db import get_db_session
from delivery_service.infrastructure.db.repositories import (
    SqlAlchemyDeliveryRepository,
    SqlAlchemyOutboxWriter,
    SqlAlchemyUnitOfWork,
)


def get_delivery_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> DeliveryApplicationService:
    return DeliveryApplicationService(
        delivery_repository=SqlAlchemyDeliveryRepository(session),
        outbox=SqlAlchemyOutboxWriter(session),
        unit_of_work=SqlAlchemyUnitOfWork(session),
    )
