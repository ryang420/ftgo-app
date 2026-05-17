from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from order_service.application.commands import CreateOrderCommand, CreateOrderLineItemCommand
from order_service.application.errors import ConsumerNotFoundError
from order_service.application.ports import MenuItemSnapshot
from order_service.application.orders import OrderApplicationService
from order_service.domain.models import Order, OrderStatus


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


class FakeRestaurantCatalog:
    async def ensure_restaurant_exists(self, restaurant_id: int) -> None:
        assert restaurant_id == 10

    async def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItemSnapshot:
        assert restaurant_id == 10
        return MenuItemSnapshot(
            id=menu_item_id,
            restaurant_id=restaurant_id,
            name="Beef Noodles",
            price=Decimal("28.00"),
        )


class FakeConsumerRegistry:
    def __init__(self, *, existing_consumer_ids: set[UUID] | None = None):
        self.existing_consumer_ids = existing_consumer_ids or set()

    async def ensure_consumer_exists(self, consumer_id: UUID) -> None:
        if consumer_id not in self.existing_consumer_ids:
            raise ConsumerNotFoundError(consumer_id)


@pytest.mark.asyncio
async def test_create_order_uses_restaurant_catalog_menu_snapshot() -> None:
    repository = FakeOrderRepository()
    consumer_id = uuid4()
    service = OrderApplicationService(
        repository,
        FakeRestaurantCatalog(),
        FakeConsumerRegistry(existing_consumer_ids={consumer_id}),
    )

    order = await service.create_order(
        CreateOrderCommand(
            consumer_id=consumer_id,
            restaurant_id=10,
            currency="usd",
            line_items=[CreateOrderLineItemCommand(menu_item_id=20, quantity=2)],
        )
    )

    assert order.status == OrderStatus.PENDING
    assert order.restaurant_id == 10
    assert order.currency == "USD"
    assert order.total_amount == Decimal("56.00")
    assert order.line_items[0].menu_item_id == 20
    assert order.line_items[0].name == "Beef Noodles"
    assert order.line_items[0].unit_price == Decimal("28.00")
    assert repository.orders == [order]


@pytest.mark.asyncio
async def test_create_order_rejects_unknown_consumer() -> None:
    repository = FakeOrderRepository()
    service = OrderApplicationService(repository, FakeRestaurantCatalog(), FakeConsumerRegistry())

    with pytest.raises(ConsumerNotFoundError):
        await service.create_order(
            CreateOrderCommand(
                consumer_id=uuid4(),
                restaurant_id=10,
                currency="usd",
                line_items=[CreateOrderLineItemCommand(menu_item_id=20, quantity=2)],
            )
        )

    assert repository.orders == []
