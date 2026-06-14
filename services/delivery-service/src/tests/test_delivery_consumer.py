from uuid import uuid4

import pytest
from delivery_service.consumer import build_delivery_payload


def test_build_delivery_payload_extracts_ready_ticket_fields() -> None:
    order_id = uuid4()
    envelope = {
        "payload": {
            "order_id": str(order_id),
            "restaurant_id": 7,
            "delivery_address": "123 Main St",
        }
    }

    payload = build_delivery_payload(envelope)

    assert payload == {
        "order_id": str(order_id),
        "restaurant_id": 7,
        "delivery_address": "123 Main St",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"order_id": "not-a-uuid", "restaurant_id": 7, "delivery_address": "123 Main St"},
        {"order_id": str(uuid4()), "restaurant_id": 7},
    ],
)
def test_build_delivery_payload_rejects_malformed_payload(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        build_delivery_payload({"payload": payload})
