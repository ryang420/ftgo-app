from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Order
from app.domain.repositories import OrderRepository
from app.infrastructure.db.mappers import to_domain_order, to_order_record
from app.infrastructure.db.models import OrderRecord


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def list_orders(self) -> list[Order]:
        statement = (
            select(OrderRecord)
            .options(selectinload(OrderRecord.line_items))
            .order_by(OrderRecord.created_at.desc())
        )
        return [to_domain_order(record) for record in self.session.scalars(statement).all()]

    def get_order(self, order_id: UUID) -> Order | None:
        statement = (
            select(OrderRecord)
            .options(selectinload(OrderRecord.line_items))
            .where(OrderRecord.id == order_id)
        )
        record = self.session.scalar(statement)
        if record is None:
            return None
        return to_domain_order(record)

    def add(self, order: Order) -> Order:
        record = to_order_record(order)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return self.get_order(record.id) or order
