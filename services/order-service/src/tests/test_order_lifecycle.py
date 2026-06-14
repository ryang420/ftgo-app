from decimal import Decimal
from uuid import UUID, uuid4

from order_service.application.lifecycle import OrderLifecycleApplicationService
from order_service.domain.models import Order, OrderLineItem, OrderStatus


class _FakeOrderRepository:
    def __init__(self, order: Order | None = None) -> None:
        self.order = order

    def list_orders(self) -> list[Order]:
        return [self.order] if self.order is not None else []

    def get_order(self, order_id: UUID) -> Order | None:
        if self.order is not None and self.order.id == order_id:
            return self.order
        return None

    def add(self, order: Order) -> Order:
        self.order = order
        return order

    def save(self, order: Order) -> Order:
        self.order = order
        return order


class _FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


def _order(status: OrderStatus) -> Order:
    return Order(
        consumer_id=uuid4(),
        restaurant_id=10,
        currency="USD",
        delivery_address="123 Main St",
        line_items=[
            OrderLineItem(
                menu_item_id=20,
                name="Beef Noodles",
                quantity=1,
                unit_price=Decimal("12.00"),
            )
        ],
        status=status,
    )


def test_lifecycle_marks_delivery_assigned() -> None:
    order = _order(OrderStatus.READY)
    uow = _FakeUnitOfWork()
    service = OrderLifecycleApplicationService(_FakeOrderRepository(order), uow)

    result = service.mark_delivery_assigned_order(order.id)

    assert result is not None
    assert result.status == OrderStatus.DELIVERY_ASSIGNED
    assert uow.commits == 1


def test_lifecycle_marks_out_for_delivery() -> None:
    order = _order(OrderStatus.DELIVERY_ASSIGNED)
    uow = _FakeUnitOfWork()
    service = OrderLifecycleApplicationService(_FakeOrderRepository(order), uow)

    result = service.mark_out_for_delivery_order(order.id)

    assert result is not None
    assert result.status == OrderStatus.OUT_FOR_DELIVERY
    assert uow.commits == 1


def test_lifecycle_marks_delivered() -> None:
    order = _order(OrderStatus.OUT_FOR_DELIVERY)
    uow = _FakeUnitOfWork()
    service = OrderLifecycleApplicationService(_FakeOrderRepository(order), uow)

    result = service.mark_delivered_order(order.id)

    assert result is not None
    assert result.status == OrderStatus.DELIVERED
    assert uow.commits == 1
