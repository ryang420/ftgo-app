from uuid import UUID

from order_service.application.commands import CreateOrderCommand
from order_service.application.outbox import order_created_event
from order_service.application.ports import (
    ConsumerRegistry,
    OutboxWriter,
    RestaurantCatalog,
    UnitOfWork,
)
from order_service.domain.models import Order, OrderLineItem
from order_service.domain.repositories import OrderRepository


class OrderApplicationService:
    def __init__(
        self,
        order_repository: OrderRepository,
        restaurant_catalog: RestaurantCatalog,
        consumer_registry: ConsumerRegistry,
        outbox: OutboxWriter,
        unit_of_work: UnitOfWork,
    ):
        self.order_repository = order_repository
        self.restaurant_catalog = restaurant_catalog
        self.consumer_registry = consumer_registry
        self.outbox = outbox
        self.unit_of_work = unit_of_work

    def list_orders(self) -> list[Order]:
        return self.order_repository.list_orders()

    def get_order(self, order_id: UUID) -> Order | None:
        return self.order_repository.get_order(order_id)

    async def create_order(self, command: CreateOrderCommand) -> Order:
        await self.consumer_registry.ensure_consumer_exists(command.consumer_id)
        await self.restaurant_catalog.ensure_restaurant_exists(command.restaurant_id)
        menu_items = [
            await self.restaurant_catalog.get_menu_item(command.restaurant_id, item.menu_item_id)
            for item in command.line_items
        ]
        order = Order.create_pending(
            consumer_id=command.consumer_id,
            restaurant_id=command.restaurant_id,
            currency=command.currency,
            delivery_address=command.delivery_address,
            line_items=[
                OrderLineItem(
                    menu_item_id=menu_item.id,
                    name=menu_item.name,
                    quantity=item.quantity,
                    unit_price=menu_item.price,
                )
                for item, menu_item in zip(command.line_items, menu_items, strict=True)
            ],
        )
        saved_order = self.order_repository.add(order)
        self.outbox.add(order_created_event(saved_order))
        self.unit_of_work.commit()
        return saved_order
