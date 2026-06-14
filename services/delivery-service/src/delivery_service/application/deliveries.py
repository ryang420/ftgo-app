from uuid import UUID

from delivery_service.application.outbox import (
    delivery_assigned_event,
    delivery_created_event,
    delivery_delivered_event,
    delivery_picked_up_event,
)
from delivery_service.application.ports import OutboxWriter, UnitOfWork
from delivery_service.domain.models import Delivery, DeliveryStatus
from delivery_service.domain.repositories import DeliveryRepository


class DeliveryApplicationService:
    def __init__(
        self,
        delivery_repository: DeliveryRepository,
        outbox: OutboxWriter,
        unit_of_work: UnitOfWork,
    ):
        self.delivery_repository = delivery_repository
        self.outbox = outbox
        self.unit_of_work = unit_of_work

    def list_deliveries(self) -> list[Delivery]:
        return self.delivery_repository.list_deliveries()

    def get_delivery(self, delivery_id: UUID) -> Delivery | None:
        return self.delivery_repository.get_by_id(delivery_id)

    def create_delivery_for_ready_order(self, payload: dict[str, object]) -> Delivery:
        order_id = UUID(str(payload["order_id"]))
        existing = self.delivery_repository.get_by_order_id(order_id)
        if existing is not None:
            return existing

        delivery = Delivery.create_pending(
            order_id=order_id,
            restaurant_id=int(payload["restaurant_id"]),
            delivery_address=str(payload["delivery_address"]),
        )
        saved = self.delivery_repository.add(delivery)
        self.outbox.add(delivery_created_event(saved))
        self.unit_of_work.commit()
        return saved

    def assign_courier(self, delivery_id: UUID, courier_id: str) -> Delivery | None:
        delivery = self.delivery_repository.get_by_id(delivery_id)
        if delivery is None:
            return None
        if delivery.status == DeliveryStatus.ASSIGNED and delivery.courier_id == courier_id.strip():
            return delivery
        delivery.assign(courier_id)
        saved = self.delivery_repository.save(delivery)
        self.outbox.add(delivery_assigned_event(saved))
        self.unit_of_work.commit()
        return saved

    def mark_picked_up(self, delivery_id: UUID) -> Delivery | None:
        delivery = self.delivery_repository.get_by_id(delivery_id)
        if delivery is None:
            return None
        if delivery.status == DeliveryStatus.PICKED_UP:
            return delivery
        delivery.mark_picked_up()
        saved = self.delivery_repository.save(delivery)
        self.outbox.add(delivery_picked_up_event(saved))
        self.unit_of_work.commit()
        return saved

    def mark_delivered(self, delivery_id: UUID) -> Delivery | None:
        delivery = self.delivery_repository.get_by_id(delivery_id)
        if delivery is None:
            return None
        if delivery.status == DeliveryStatus.DELIVERED:
            return delivery
        delivery.mark_delivered()
        saved = self.delivery_repository.save(delivery)
        self.outbox.add(delivery_delivered_event(saved))
        self.unit_of_work.commit()
        return saved
