from uuid import UUID

from app.application.commands import CreateOrderCommand
from app.domain.models import Order, OrderLineItem
from app.domain.repositories import OrderRepository


class OrderApplicationService:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def list_orders(self) -> list[Order]:
        return self.order_repository.list_orders()

    def get_order(self, order_id: UUID) -> Order | None:
        return self.order_repository.get_order(order_id)

    def create_order(self, command: CreateOrderCommand) -> Order:
        order = Order.create_pending(
            consumer_id=command.consumer_id,
            restaurant_id=command.restaurant_id,
            currency=command.currency,
            line_items=[
                OrderLineItem(
                    menu_item_id=item.menu_item_id,
                    name=item.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in command.line_items
            ],
        )
        return self.order_repository.add(order)
