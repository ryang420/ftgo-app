from uuid import UUID, uuid4

from kitchen_service.application.commands import (
    CreateKitchenTicketCommand,
    CreateKitchenTicketLineItemCommand,
)
from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.domain.models import KitchenTicket


class FakeKitchenTicketRepository:
    def __init__(self):
        self.tickets: list[KitchenTicket] = []

    def list_tickets(self) -> list[KitchenTicket]:
        return self.tickets

    def get_by_order_id(self, order_id: UUID) -> KitchenTicket | None:
        return next((ticket for ticket in self.tickets if ticket.order_id == order_id), None)

    def add(self, ticket: KitchenTicket) -> KitchenTicket:
        self.tickets.append(ticket)
        return ticket


def build_command(order_id: UUID) -> CreateKitchenTicketCommand:
    return CreateKitchenTicketCommand(
        order_id=order_id,
        restaurant_id=10,
        line_items=[
            CreateKitchenTicketLineItemCommand(
                menu_item_id=20,
                name="Beef Noodles",
                quantity=2,
            )
        ],
    )


def test_create_ticket_for_order_is_idempotent_by_order_id() -> None:
    repository = FakeKitchenTicketRepository()
    service = KitchenTicketApplicationService(repository)
    order_id = uuid4()

    first = service.create_ticket_for_order(build_command(order_id))
    second = service.create_ticket_for_order(build_command(order_id))

    assert first == second
    assert len(repository.tickets) == 1
    assert repository.tickets[0].order_id == order_id
    assert repository.tickets[0].line_items[0].name == "Beef Noodles"
