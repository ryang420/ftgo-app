from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.models import Order, OrderLineItem, OrderStatus
from app.schemas.orders import OrderCreate


class OrderApplicationService:
    """Temporary in-process order use cases until persistence wiring is added."""

    def list_orders(self) -> list[Order]:
        sample_order = Order(
            id=uuid4(),
            consumer_id=uuid4(),
            restaurant_id=uuid4(),
            status=OrderStatus.PENDING,
            currency="USD",
            total_amount=Decimal("24.00"),
            line_items=[
                OrderLineItem(
                    id=uuid4(),
                    menu_item_id=uuid4(),
                    name="Sample Burger",
                    quantity=2,
                    unit_price=Decimal("12.00"),
                )
            ],
        )
        return [sample_order]

    def get_order(self, order_id: UUID) -> Order:
        return Order(
            id=order_id,
            consumer_id=uuid4(),
            restaurant_id=uuid4(),
            status=OrderStatus.PENDING,
            currency="USD",
            total_amount=Decimal("18.00"),
            line_items=[
                OrderLineItem(
                    id=uuid4(),
                    menu_item_id=uuid4(),
                    name="Sample Fries",
                    quantity=1,
                    unit_price=Decimal("6.00"),
                ),
                OrderLineItem(
                    id=uuid4(),
                    menu_item_id=uuid4(),
                    name="Sample Wrap",
                    quantity=1,
                    unit_price=Decimal("12.00"),
                ),
            ],
        )

    def create_order(self, payload: OrderCreate) -> Order:
        line_items = [
            OrderLineItem(
                id=uuid4(),
                menu_item_id=item.menu_item_id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in payload.line_items
        ]
        total_amount = sum(
            (item.unit_price * item.quantity for item in payload.line_items),
            start=Decimal("0.00"),
        )
        return Order(
            id=uuid4(),
            consumer_id=payload.consumer_id,
            restaurant_id=payload.restaurant_id,
            status=OrderStatus.PENDING,
            currency=payload.currency,
            total_amount=total_amount,
            line_items=line_items,
        )
