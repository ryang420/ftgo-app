from uuid import uuid4

from delivery_service.domain.models import Delivery, DeliveryStatus
from delivery_service.infrastructure.db.mappers import to_delivery_record, to_domain_delivery


def test_delivery_mapper_round_trips_domain_fields() -> None:
    delivery = Delivery(
        id=uuid4(),
        order_id=uuid4(),
        restaurant_id=12,
        delivery_address="123 Main St",
        status=DeliveryStatus.ASSIGNED,
        courier_id="courier-001",
    )

    record = to_delivery_record(delivery)
    mapped = to_domain_delivery(record)

    assert mapped.id == delivery.id
    assert mapped.order_id == delivery.order_id
    assert mapped.restaurant_id == delivery.restaurant_id
    assert mapped.delivery_address == delivery.delivery_address
    assert mapped.status == DeliveryStatus.ASSIGNED
    assert mapped.courier_id == "courier-001"
