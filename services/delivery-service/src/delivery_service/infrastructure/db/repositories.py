from uuid import UUID

from common.outbox.models import OutboxMessageRecord
from sqlalchemy import select
from sqlalchemy.orm import Session

from delivery_service.application.outbox import OutboxEvent
from delivery_service.domain.models import Delivery
from delivery_service.domain.repositories import DeliveryRepository
from delivery_service.infrastructure.db.mappers import to_delivery_record, to_domain_delivery
from delivery_service.infrastructure.db.models import DeliveryRecord


class SqlAlchemyDeliveryRepository(DeliveryRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_deliveries(self) -> list[Delivery]:
        statement = select(DeliveryRecord).order_by(DeliveryRecord.created_at.desc())
        return [to_domain_delivery(record) for record in self.session.scalars(statement).all()]

    def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        record = self.session.get(DeliveryRecord, delivery_id)
        if record is None:
            return None
        return to_domain_delivery(record)

    def get_by_order_id(self, order_id: UUID) -> Delivery | None:
        statement = select(DeliveryRecord).where(DeliveryRecord.order_id == order_id)
        record = self.session.scalar(statement)
        if record is None:
            return None
        return to_domain_delivery(record)

    def add(self, delivery: Delivery) -> Delivery:
        record = to_delivery_record(delivery)
        self.session.add(record)
        self.session.flush()
        self.session.refresh(record)
        return self.get_by_id(record.id) or delivery

    def save(self, delivery: Delivery) -> Delivery:
        record = self.session.get(DeliveryRecord, delivery.id)
        if record is None:
            raise ValueError(f"Delivery {delivery.id} was not found")
        record.status = delivery.status
        record.courier_id = delivery.courier_id
        self.session.flush()
        self.session.refresh(record)
        return self.get_by_id(record.id) or delivery


class SqlAlchemyOutboxWriter:
    def __init__(self, session: Session):
        self.session = session

    def add(self, event: OutboxEvent) -> None:
        self.session.add(
            OutboxMessageRecord(
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                event_type=event.event_type,
                payload=event.payload,
            )
        )


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self.session = session

    def commit(self) -> None:
        self.session.commit()
