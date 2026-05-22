from uuid import UUID

from common.outbox.models import OutboxMessageRecord
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from kitchen_service.application.outbox import OutboxEvent
from kitchen_service.domain.models import KitchenTicket
from kitchen_service.domain.repositories import KitchenTicketRepository
from kitchen_service.infrastructure.db.mappers import to_domain_ticket, to_ticket_record
from kitchen_service.infrastructure.db.models import KitchenTicketRecord


class SqlAlchemyKitchenTicketRepository(KitchenTicketRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_tickets(self) -> list[KitchenTicket]:
        statement = (
            select(KitchenTicketRecord)
            .options(selectinload(KitchenTicketRecord.line_items))
            .order_by(KitchenTicketRecord.created_at.desc())
        )
        return [to_domain_ticket(record) for record in self.session.scalars(statement).all()]

    def get_by_order_id(self, order_id: UUID) -> KitchenTicket | None:
        statement = (
            select(KitchenTicketRecord)
            .options(selectinload(KitchenTicketRecord.line_items))
            .where(KitchenTicketRecord.order_id == order_id)
        )
        record = self.session.scalar(statement)
        if record is None:
            return None
        return to_domain_ticket(record)

    def add(self, ticket: KitchenTicket) -> KitchenTicket:
        record = to_ticket_record(ticket)
        self.session.add(record)
        self.session.flush()
        self.session.refresh(record)
        return self.get_by_order_id(record.order_id) or ticket


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
