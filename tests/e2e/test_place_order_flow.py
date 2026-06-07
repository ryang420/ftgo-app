from __future__ import annotations

import os
import time
from collections.abc import Callable
from uuid import uuid4

import httpx
import pytest

GATEWAY_URL = os.getenv("FTGO_API_GATEWAY_URL", "http://localhost:8000")
POLL_INTERVAL_SECONDS = 1.0
POLL_TIMEOUT_SECONDS = 20.0


@pytest.fixture(scope="module")
def gateway_client() -> httpx.Client:
    client = httpx.Client(base_url=GATEWAY_URL, timeout=10.0)
    try:
        response = client.get("/health")
    except httpx.HTTPError as exc:
        client.close()
        pytest.skip(f"API gateway is not reachable at {GATEWAY_URL}: {exc}")

    if response.status_code != 200:
        client.close()
        pytest.skip(
            f"API gateway health check failed at {GATEWAY_URL}: "
            f"{response.status_code} {response.text}"
        )

    yield client
    client.close()


def assert_success(response: httpx.Response) -> httpx.Response:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        pytest.fail(
            f"{response.request.method} {response.request.url} returned "
            f"{response.status_code}: {response.text}"
        )
        raise exc
    return response


def wait_until(description: str, predicate: Callable[[], dict | None]) -> dict:
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            result = predicate()
        except Exception as exc:  # noqa: BLE001 - include transient poll failures in assertion.
            last_error = exc
        else:
            if result is not None:
                return result
        time.sleep(POLL_INTERVAL_SECONDS)

    detail = f" Last error: {last_error}" if last_error is not None else ""
    pytest.fail(f"Timed out waiting for {description}.{detail}")


def create_consumer(client: httpx.Client, run_id: str) -> dict:
    response = client.post(
        "/consumers",
        json={
            "email": f"alice.{run_id}@example.com",
            "first_name": "Alice",
            "last_name": "Wang",
            "phone_number": "+8613800000000",
            "addresses": [
                {
                    "label": "home",
                    "street1": "123 Main St",
                    "city": "Shanghai",
                    "state": "Shanghai",
                    "postal_code": "200000",
                    "country": "CN",
                }
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_restaurant(client: httpx.Client, run_id: str) -> dict:
    response = client.post(
        "/restaurants",
        json={
            "name": f"Noodle House {run_id}",
            "slug": f"noodle-house-{run_id}",
            "cuisine": "Chinese",
            "menu_items": [
                {
                    "name": "Beef Noodles",
                    "description": "Classic bowl",
                    "price": "28.00",
                }
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_order(
    client: httpx.Client,
    *,
    run_id: str,
    consumer_id: str,
    restaurant_id: int,
    menu_item_id: int,
) -> dict:
    response = client.post(
        "/orders",
        headers={"Idempotency-Key": f"pytest-place-order-{run_id}"},
        json={
            "consumer_id": consumer_id,
            "restaurant_id": restaurant_id,
            "currency": "USD",
            "delivery_address": "123 Main St, Shanghai, 200000",
            "line_items": [
                {
                    "menu_item_id": menu_item_id,
                    "quantity": 2,
                }
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def find_ticket_for_order(client: httpx.Client, order_id: str) -> dict | None:
    response = assert_success(client.get("/kitchen/tickets"))
    for ticket in response.json():
        if ticket["order_id"] == order_id:
            return ticket
    return None


def get_order_when_approved(client: httpx.Client, order_id: str) -> dict | None:
    response = assert_success(client.get(f"/orders/{order_id}"))
    order = response.json()
    return order if order["status"] == "APPROVED" else None


def test_place_order_creates_kitchen_ticket_and_approves_order(
    gateway_client: httpx.Client,
) -> None:
    run_id = uuid4().hex

    consumer = create_consumer(gateway_client, run_id)
    restaurant = create_restaurant(gateway_client, run_id)
    menu_item = restaurant["menu_items"][0]

    order = create_order(
        gateway_client,
        run_id=run_id,
        consumer_id=consumer["id"],
        restaurant_id=restaurant["id"],
        menu_item_id=menu_item["id"],
    )

    assert order["consumer_id"] == consumer["id"]
    assert order["restaurant_id"] == restaurant["id"]
    assert order["status"] == "PENDING"
    assert order["currency"] == "USD"
    assert order["line_items"][0]["name"] == "Beef Noodles"
    assert order["line_items"][0]["quantity"] == 2

    ticket = wait_until(
        f"kitchen ticket creation for order {order['id']}",
        lambda: find_ticket_for_order(gateway_client, order["id"]),
    )

    assert ticket["order_id"] == order["id"]
    assert ticket["restaurant_id"] == restaurant["id"]
    assert ticket["status"] == "CREATE_PENDING"
    assert ticket["line_items"][0]["name"] == "Beef Noodles"
    assert ticket["line_items"][0]["quantity"] == 2

    approved_order = wait_until(
        f"order {order['id']} to transition to APPROVED",
        lambda: get_order_when_approved(gateway_client, order["id"]),
    )

    assert approved_order["id"] == order["id"]
    assert approved_order["status"] == "APPROVED"
