from uuid import UUID, uuid4

from delivery_service.application.deliveries import DeliveryApplicationService
from delivery_service.application.outbox import OutboxEvent
from delivery_service.domain.models import Delivery, DeliveryStatus


class _FakeDeliveryRepository:
    def __init__(self) -> None:
        self.deliveries: list[Delivery] = []

    def list_deliveries(self) -> list[Delivery]:
        return self.deliveries

    def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        return next((delivery for delivery in self.deliveries if delivery.id == delivery_id), None)

    def get_by_order_id(self, order_id: UUID) -> Delivery | None:
        return next(
            (delivery for delivery in self.deliveries if delivery.order_id == order_id),
            None,
        )

    def add(self, delivery: Delivery) -> Delivery:
        self.deliveries.append(delivery)
        return delivery

    def save(self, delivery: Delivery) -> Delivery:
        for index, existing in enumerate(self.deliveries):
            if existing.id == delivery.id:
                self.deliveries[index] = delivery
                return delivery
        raise ValueError(f"Delivery {delivery.id} not found")


class _FakeOutboxWriter:
    def __init__(self) -> None:
        self.events: list[OutboxEvent] = []

    def add(self, event: OutboxEvent) -> None:
        self.events.append(event)


class _FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


def _service() -> tuple[
    DeliveryApplicationService,
    _FakeDeliveryRepository,
    _FakeOutboxWriter,
    _FakeUnitOfWork,
]:
    repo = _FakeDeliveryRepository()
    outbox = _FakeOutboxWriter()
    uow = _FakeUnitOfWork()
    return DeliveryApplicationService(repo, outbox, uow), repo, outbox, uow


def _ready_payload(order_id: UUID | None = None) -> dict[str, object]:
    return {
        "order_id": str(order_id or uuid4()),
        "restaurant_id": 7,
        "delivery_address": "123 Main St",
    }


def test_create_delivery_for_ready_order_writes_created_event() -> None:
    service, repo, outbox, uow = _service()
    payload = _ready_payload()

    delivery = service.create_delivery_for_ready_order(payload)

    assert delivery.status == DeliveryStatus.PENDING_ASSIGNMENT
    assert repo.get_by_order_id(delivery.order_id) == delivery
    assert [event.event_type for event in outbox.events] == ["DeliveryCreated"]
    assert uow.commits == 1


def test_create_delivery_for_ready_order_is_idempotent_by_order_id() -> None:
    service, _repo, outbox, uow = _service()
    order_id = uuid4()
    payload = _ready_payload(order_id)

    first = service.create_delivery_for_ready_order(payload)
    second = service.create_delivery_for_ready_order(payload)

    assert second == first
    assert [event.event_type for event in outbox.events] == ["DeliveryCreated"]
    assert uow.commits == 1


def test_delivery_lifecycle_commands_write_one_event_each() -> None:
    service, _repo, outbox, uow = _service()
    delivery = service.create_delivery_for_ready_order(_ready_payload())

    assigned = service.assign_courier(delivery.id, "courier-001")
    assert assigned is not None and assigned.status == DeliveryStatus.ASSIGNED

    picked_up = service.mark_picked_up(delivery.id)
    assert picked_up is not None and picked_up.status == DeliveryStatus.PICKED_UP

    delivered = service.mark_delivered(delivery.id)
    assert delivered is not None and delivered.status == DeliveryStatus.DELIVERED
    assert [event.event_type for event in outbox.events] == [
        "DeliveryCreated",
        "DeliveryAssigned",
        "DeliveryPickedUp",
        "DeliveryDelivered",
    ]
    assert uow.commits == 4


def test_duplicate_lifecycle_commands_do_not_write_duplicate_events() -> None:
    service, _repo, outbox, uow = _service()
    delivery = service.create_delivery_for_ready_order(_ready_payload())

    service.assign_courier(delivery.id, "courier-001")
    service.assign_courier(delivery.id, "courier-001")
    service.mark_picked_up(delivery.id)
    service.mark_picked_up(delivery.id)
    service.mark_delivered(delivery.id)
    service.mark_delivered(delivery.id)

    assert [event.event_type for event in outbox.events] == [
        "DeliveryCreated",
        "DeliveryAssigned",
        "DeliveryPickedUp",
        "DeliveryDelivered",
    ]
    assert uow.commits == 4
