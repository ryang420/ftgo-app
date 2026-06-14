from uuid import uuid4

import pytest
from delivery_service.domain.models import (
    Delivery,
    DeliveryStatus,
    InvalidDeliveryStatusTransitionError,
)


def test_create_pending_delivery_records_order_and_address() -> None:
    order_id = uuid4()

    delivery = Delivery.create_pending(
        order_id=order_id,
        restaurant_id=7,
        delivery_address="123 Main St",
    )

    assert delivery.order_id == order_id
    assert delivery.restaurant_id == 7
    assert delivery.delivery_address == "123 Main St"
    assert delivery.status == DeliveryStatus.PENDING_ASSIGNMENT


def test_delivery_happy_path_transitions_to_delivered() -> None:
    delivery = Delivery.create_pending(
        order_id=uuid4(),
        restaurant_id=7,
        delivery_address="123 Main St",
    )

    delivery.assign("courier-001")
    assert delivery.status == DeliveryStatus.ASSIGNED
    assert delivery.courier_id == "courier-001"

    delivery.mark_picked_up()
    assert delivery.status == DeliveryStatus.PICKED_UP

    delivery.mark_delivered()
    assert delivery.status == DeliveryStatus.DELIVERED


def test_delivery_rejects_invalid_transition() -> None:
    delivery = Delivery.create_pending(
        order_id=uuid4(),
        restaurant_id=7,
        delivery_address="123 Main St",
    )

    with pytest.raises(InvalidDeliveryStatusTransitionError) as exc_info:
        delivery.mark_picked_up()

    assert exc_info.value.current == DeliveryStatus.PENDING_ASSIGNMENT
    assert exc_info.value.target == DeliveryStatus.PICKED_UP


def test_delivery_transitions_are_idempotent_for_target_status() -> None:
    delivery = Delivery.create_pending(
        order_id=uuid4(),
        restaurant_id=7,
        delivery_address="123 Main St",
    )

    delivery.assign("courier-001")
    delivery.assign("courier-001")
    assert delivery.status == DeliveryStatus.ASSIGNED
    assert delivery.courier_id == "courier-001"

    delivery.mark_picked_up()
    delivery.mark_picked_up()
    assert delivery.status == DeliveryStatus.PICKED_UP

    delivery.mark_delivered()
    delivery.mark_delivered()
    assert delivery.status == DeliveryStatus.DELIVERED
