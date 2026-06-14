from delivery_service.domain.models import Delivery
from delivery_service.infrastructure.db.models import DeliveryRecord


def to_domain_delivery(record: DeliveryRecord) -> Delivery:
    return Delivery(
        id=record.id,
        order_id=record.order_id,
        restaurant_id=record.restaurant_id,
        delivery_address=record.delivery_address,
        status=record.status,
        courier_id=record.courier_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def to_delivery_record(delivery: Delivery) -> DeliveryRecord:
    return DeliveryRecord(
        id=delivery.id,
        order_id=delivery.order_id,
        restaurant_id=delivery.restaurant_id,
        delivery_address=delivery.delivery_address,
        status=delivery.status,
        courier_id=delivery.courier_id,
    )
