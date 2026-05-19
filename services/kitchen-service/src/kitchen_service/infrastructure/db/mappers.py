from kitchen_service.domain.models import KitchenTicket, KitchenTicketLineItem
from kitchen_service.infrastructure.db.models import (
    KitchenTicketLineItemRecord,
    KitchenTicketRecord,
)


def to_domain_ticket(record: KitchenTicketRecord) -> KitchenTicket:
    return KitchenTicket(
        id=record.id,
        order_id=record.order_id,
        restaurant_id=record.restaurant_id,
        status=record.status,
        line_items=[
            KitchenTicketLineItem(
                id=item.id,
                menu_item_id=item.menu_item_id,
                name=item.name,
                quantity=item.quantity,
            )
            for item in record.line_items
        ],
    )


def to_ticket_record(ticket: KitchenTicket) -> KitchenTicketRecord:
    record = KitchenTicketRecord(
        id=ticket.id,
        order_id=ticket.order_id,
        restaurant_id=ticket.restaurant_id,
        status=ticket.status,
    )
    record.line_items = [
        KitchenTicketLineItemRecord(
            id=item.id,
            menu_item_id=item.menu_item_id,
            name=item.name,
            quantity=item.quantity,
        )
        for item in ticket.line_items
    ]
    return record
