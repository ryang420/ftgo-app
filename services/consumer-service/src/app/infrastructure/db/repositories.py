from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.domain.models import ConsumerProfile
from app.domain.repositories import ConsumerRepository
from app.infrastructure.db.mappers import to_consumer_record, to_domain_consumer
from app.infrastructure.db.models import ConsumerProfileRecord


class SqlAlchemyConsumerRepository(ConsumerRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_consumers(self) -> list[ConsumerProfile]:
        statement = (
            select(ConsumerProfileRecord)
            .options(selectinload(ConsumerProfileRecord.addresses))
            .order_by(ConsumerProfileRecord.created_at.desc())
        )
        return [to_domain_consumer(record) for record in self.session.scalars(statement).all()]

    def get_consumer(self, consumer_id: str) -> ConsumerProfile | None:
        statement = (
            select(ConsumerProfileRecord)
            .options(selectinload(ConsumerProfileRecord.addresses))
            .where(ConsumerProfileRecord.id == consumer_id)
        )
        record = self.session.scalar(statement)
        if record is None:
            return None
        return to_domain_consumer(record)

    def add(self, consumer: ConsumerProfile) -> ConsumerProfile:
        record = to_consumer_record(consumer)
        try:
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        except SQLAlchemyError:
            self.session.rollback()
            raise
        return self.get_consumer(record.id) or consumer
