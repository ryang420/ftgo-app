from app.domain.models import Order, OrderLineItem
from app.infrastructure.db.models import OrderLineItemRecord, OrderRecord


def to_domain_order(record: OrderRecord) -> Order:
    return Order(
        id=record.id,
        consumer_id=record.consumer_id,
        restaurant_id=record.restaurant_id,
        status=record.status,
        currency=record.currency,
        line_items=[
            OrderLineItem(
                id=item.id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in record.line_items
        ],
    )


def to_order_record(order: Order) -> OrderRecord:
    record = OrderRecord(
        id=order.id,
        consumer_id=order.consumer_id,
        restaurant_id=order.restaurant_id,
        status=order.status,
        currency=order.currency,
        total_amount=order.total_amount,
    )
    record.line_items = [
        OrderLineItemRecord(
            id=item.id,
            menu_item_id=item.menu_item_id,
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in order.line_items
    ]
    return record
