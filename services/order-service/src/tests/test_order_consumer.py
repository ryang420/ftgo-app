from uuid import uuid4

import pytest
from order_service.consumer import extract_order_id


def test_extract_order_id_returns_uuid() -> None:
    order_id = uuid4()

    result = extract_order_id(
        {"payload": {"order_id": str(order_id)}},
        event_type="DeliveryAssigned",
    )

    assert result == order_id


@pytest.mark.parametrize("payload", [{}, {"order_id": "not-a-uuid"}])
def test_extract_order_id_rejects_malformed_payload(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        extract_order_id({"payload": payload}, event_type="DeliveryAssigned")
