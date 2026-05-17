from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from consumer_service.application.consumer_service import ConsumerApplicationService
from consumer_service.infrastructure.db import get_db_session
from consumer_service.infrastructure.db.repositories import SqlAlchemyConsumerRepository


def get_consumer_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ConsumerApplicationService:
    return ConsumerApplicationService(SqlAlchemyConsumerRepository(session))
