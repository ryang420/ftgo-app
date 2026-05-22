from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from order_service.application.commands import CreateOrderCommand, CreateOrderLineItemCommand
from order_service.application.errors import (
    ConsumerNotFoundError,
    MenuItemNotFoundError,
    RestaurantNotFoundError,
)
from order_service.application.lifecycle import OrderLifecycleApplicationService
from order_service.application.orders import OrderApplicationService
from order_service.application.outbox import OutboxEvent
from order_service.application.ports import MenuItemSnapshot
from order_service.domain.models import Order, OrderLineItem, OrderStatus


class FakeOrderRepository:
    def __init__(self):
        self.orders: list[Order] = []

    def list_orders(self) -> list[Order]:
        return self.orders

    def get_order(self, order_id: UUID) -> Order | None:
        return next((order for order in self.orders if order.id == order_id), None)

    def add(self, order: Order) -> Order:
        self.orders.append(order)
        return order

    def save(self, order: Order) -> Order:
        for index, existing in enumerate(self.orders):
            if existing.id == order.id:
                self.orders[index] = order
                return order
        raise ValueError(f"Order {order.id} was not found")


class FakeRestaurantCatalog:
    def __init__(self, *, mismatch_menu_item: bool = False):
        self.mismatch_menu_item = mismatch_menu_item

    async def ensure_restaurant_exists(self, restaurant_id: int) -> None:
        if restaurant_id != 10:
            raise RestaurantNotFoundError(restaurant_id)

    async def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItemSnapshot:
        if restaurant_id != 10:
            raise MenuItemNotFoundError(restaurant_id, menu_item_id)
        if self.mismatch_menu_item:
            # Return a menu item that belongs to a different restaurant
            snapshot = MenuItemSnapshot(
                id=menu_item_id,
                restaurant_id=999,
                name="Beef Noodles",
                price=Decimal("28.00"),
            )
        else:
            snapshot = MenuItemSnapshot(
                id=menu_item_id,
                restaurant_id=restaurant_id,
                name="Beef Noodles",
                price=Decimal("28.00"),
            )
        if snapshot.restaurant_id != restaurant_id:
            raise MenuItemNotFoundError(restaurant_id, menu_item_id)
        return snapshot


class FakeConsumerRegistry:
    def __init__(self, *, existing_consumer_ids: set[UUID] | None = None):
        self.existing_consumer_ids = existing_consumer_ids or set()

    async def ensure_consumer_exists(self, consumer_id: UUID) -> None:
        if consumer_id not in self.existing_consumer_ids:
            raise ConsumerNotFoundError(consumer_id)


class FakeOutboxWriter:
    def __init__(self):
        self.events: list[OutboxEvent] = []

    def add(self, event: OutboxEvent) -> None:
        self.events.append(event)


class FakeUnitOfWork:
    def __init__(self):
        self.committed = False

    def commit(self) -> None:
        self.committed = True


def _build_command(
    consumer_id: UUID,
    restaurant_id: int = 10,
    delivery_address: str = "123 Main St",
) -> CreateOrderCommand:
    return CreateOrderCommand(
        consumer_id=consumer_id,
        restaurant_id=restaurant_id,
        currency="usd",
        delivery_address=delivery_address,
        line_items=[CreateOrderLineItemCommand(menu_item_id=20, quantity=2)],
    )


@pytest.mark.asyncio
async def test_create_order_uses_restaurant_catalog_menu_snapshot() -> None:
    repository = FakeOrderRepository()
    consumer_id = uuid4()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    service = OrderApplicationService(
        repository,
        FakeRestaurantCatalog(),
        FakeConsumerRegistry(existing_consumer_ids={consumer_id}),
        outbox,
        unit_of_work,
    )

    order = await service.create_order(_build_command(consumer_id))

    assert order.status == OrderStatus.PENDING
    assert order.restaurant_id == 10
    assert order.currency == "USD"
    assert order.delivery_address == "123 Main St"
    assert order.total_amount == Decimal("56.00")
    assert order.line_items[0].menu_item_id == 20
    assert order.line_items[0].name == "Beef Noodles"
    assert order.line_items[0].unit_price == Decimal("28.00")
    assert repository.orders == [order]
    assert unit_of_work.committed is True
    assert len(outbox.events) == 1
    assert outbox.events[0].aggregate_type == "Order"
    assert outbox.events[0].aggregate_id == str(order.id)
    assert outbox.events[0].event_type == "OrderCreated"
    assert outbox.events[0].payload["order_id"] == str(order.id)
    assert outbox.events[0].payload["consumer_id"] == str(consumer_id)
    assert outbox.events[0].payload["restaurant_id"] == 10
    assert outbox.events[0].payload["total_amount"] == "56.00"
    assert outbox.events[0].payload["delivery_address"] == "123 Main St"
    assert outbox.events[0].payload["line_items"][0]["name"] == "Beef Noodles"


@pytest.mark.asyncio
async def test_create_order_rejects_unknown_consumer() -> None:
    repository = FakeOrderRepository()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    service = OrderApplicationService(
        repository,
        FakeRestaurantCatalog(),
        FakeConsumerRegistry(),
        outbox,
        unit_of_work,
    )

    with pytest.raises(ConsumerNotFoundError):
        await service.create_order(_build_command(uuid4()))

    assert repository.orders == []
    assert outbox.events == []
    assert unit_of_work.committed is False


def test_approve_order_transitions_pending_order_to_approved() -> None:
    repository = FakeOrderRepository()
    unit_of_work = FakeUnitOfWork()
    order = Order.create_pending(
        consumer_id=uuid4(),
        restaurant_id=10,
        currency="USD",
        delivery_address="123 Main St",
        line_items=[
            OrderLineItem(
                menu_item_id=20,
                name="Beef Noodles",
                quantity=2,
                unit_price=Decimal("28.00"),
            )
        ],
    )
    repository.add(order)
    service = OrderLifecycleApplicationService(repository, unit_of_work)

    approved = service.approve_order(order.id)

    assert approved is not None
    assert approved.status == OrderStatus.APPROVED
    assert unit_of_work.committed is True


def test_approve_order_is_idempotent_for_already_approved_order() -> None:
    repository = FakeOrderRepository()
    unit_of_work = FakeUnitOfWork()
    order = Order.create_pending(
        consumer_id=uuid4(),
        restaurant_id=10,
        currency="USD",
        delivery_address="123 Main St",
        line_items=[
            OrderLineItem(
                menu_item_id=20,
                name="Beef Noodles",
                quantity=2,
                unit_price=Decimal("28.00"),
            )
        ],
    )
    order.approve()
    repository.add(order)
    service = OrderLifecycleApplicationService(repository, unit_of_work)

    approved = service.approve_order(order.id)

    assert approved is not None
    assert approved.status == OrderStatus.APPROVED
    assert unit_of_work.committed is True


@pytest.mark.asyncio
async def test_create_order_rejects_unknown_restaurant() -> None:
    repository = FakeOrderRepository()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    consumer_id = uuid4()
    service = OrderApplicationService(
        repository,
        FakeRestaurantCatalog(),
        FakeConsumerRegistry(existing_consumer_ids={consumer_id}),
        outbox,
        unit_of_work,
    )

    with pytest.raises(RestaurantNotFoundError):
        await service.create_order(_build_command(consumer_id, restaurant_id=99))

    assert repository.orders == []
    assert outbox.events == []
    assert unit_of_work.committed is False


@pytest.mark.asyncio
async def test_create_order_rejects_menu_item_from_wrong_restaurant() -> None:
    repository = FakeOrderRepository()
    consumer_id = uuid4()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    service = OrderApplicationService(
        repository,
        FakeRestaurantCatalog(mismatch_menu_item=True),
        FakeConsumerRegistry(existing_consumer_ids={consumer_id}),
        outbox,
        unit_of_work,
    )

    with pytest.raises(MenuItemNotFoundError):
        await service.create_order(_build_command(consumer_id))

    assert repository.orders == []
    assert outbox.events == []
    assert unit_of_work.committed is False


@pytest.mark.asyncio
async def test_create_order_rejects_empty_delivery_address() -> None:
    repository = FakeOrderRepository()
    consumer_id = uuid4()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    service = OrderApplicationService(
        repository,
        FakeRestaurantCatalog(),
        FakeConsumerRegistry(existing_consumer_ids={consumer_id}),
        outbox,
        unit_of_work,
    )

    with pytest.raises(ValueError, match="Delivery address is required"):
        await service.create_order(
            _build_command(consumer_id, delivery_address="   ")
        )

    assert repository.orders == []
    assert outbox.events == []
    assert unit_of_work.committed is False
