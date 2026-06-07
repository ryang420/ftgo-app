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

    def begin_preparing_order(self, order_id: UUID) -> Order | None:
        order = self.order_repository.get_order(order_id)
        if order is None:
            return None
        order.begin_preparing()
        saved_order = self.order_repository.save(order)
        self.unit_of_work.commit()
        return saved_order

    def cancel_order(self, order_id: UUID) -> Order | None:
        order = self.order_repository.get_order(order_id)
        if order is None:
            return None
        order.cancel()
        saved_order = self.order_repository.save(order)
        self.unit_of_work.commit()
        return saved_order

    def mark_ready_order(self, order_id: UUID) -> Order | None:
        order = self.order_repository.get_order(order_id)
        if order is None:
            return None
        order.mark_ready()
        saved_order = self.order_repository.save(order)
        self.unit_of_work.commit()
        return saved_order
