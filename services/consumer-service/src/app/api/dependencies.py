from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.consumer_service import ConsumerApplicationService
from app.infrastructure.db import get_db_session
from app.infrastructure.db.repositories import SqlAlchemyConsumerRepository


def get_consumer_service(
    session: Session = Depends(get_db_session),
) -> ConsumerApplicationService:
    return ConsumerApplicationService(SqlAlchemyConsumerRepository(session))
