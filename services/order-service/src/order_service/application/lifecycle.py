from uuid import UUID

from order_service.application.ports import UnitOfWork
from order_service.domain.models import Order
from order_service.domain.repositories import OrderRepository


class OrderLifecycleApplicationService:
    def __init__(self, order_repository: OrderRepository, unit_of_work: UnitOfWork):
        self.order_repository = order_repository
        self.unit_of_work = unit_of_work

    def approve_order(self, order_id: UUID) -> Order | None:
        order = self.order_repository.get_order(order_id)
        if order is None:
            return None
        order.approve()
        saved_order = self.order_repository.save(order)
        self.unit_of_work.commit()
        return saved_order
