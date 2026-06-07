from uuid import UUID

from kitchen_service.application.commands import CreateKitchenTicketCommand
from kitchen_service.application.outbox import (
    kitchen_ticket_accepted_event,
    kitchen_ticket_created_event,
    kitchen_ticket_rejected_event,
)
from kitchen_service.application.ports import OutboxWriter, UnitOfWork
from kitchen_service.domain.models import (
    KitchenTicket,
    KitchenTicketLineItem,
    KitchenTicketStatus,
)
from kitchen_service.domain.repositories import KitchenTicketRepository


class KitchenTicketApplicationService:
    def __init__(
        self,
        ticket_repository: KitchenTicketRepository,
        outbox: OutboxWriter,
        unit_of_work: UnitOfWork,
    ):
        self.ticket_repository = ticket_repository
        self.outbox = outbox
        self.unit_of_work = unit_of_work

    def list_tickets(self) -> list[KitchenTicket]:
        return self.ticket_repository.list_tickets()

    def create_ticket_for_order(self, command: CreateKitchenTicketCommand) -> KitchenTicket:
        existing = self.ticket_repository.get_by_order_id(command.order_id)
        if existing is not None:
            return existing

        ticket = KitchenTicket.create_pending(
            order_id=command.order_id,
            restaurant_id=command.restaurant_id,
            line_items=[
                KitchenTicketLineItem(
                    menu_item_id=item.menu_item_id,
                    name=item.name,
                    quantity=item.quantity,
                )
                for item in command.line_items
            ],
        )
        saved_ticket = self.ticket_repository.add(ticket)
        self.outbox.add(kitchen_ticket_created_event(saved_ticket))
        self.unit_of_work.commit()
        return saved_ticket

    def accept_ticket(self, ticket_id: UUID) -> KitchenTicket | None:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if ticket is None:
            return None
        if ticket.status == KitchenTicketStatus.ACCEPTED:
            return ticket
        ticket.accept()
        saved = self.ticket_repository.save(ticket)
        self.outbox.add(kitchen_ticket_accepted_event(saved))
        self.unit_of_work.commit()
        return saved

    def reject_ticket(
        self, ticket_id: UUID, rejection_reason: str | None = None
    ) -> KitchenTicket | None:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if ticket is None:
            return None
        if ticket.status == KitchenTicketStatus.CANCELLED:
            return ticket
        ticket.reject()
        saved = self.ticket_repository.save(ticket)
        self.outbox.add(kitchen_ticket_rejected_event(saved, rejection_reason))
        self.unit_of_work.commit()
        return saved

    def start_preparing(self, ticket_id: UUID) -> KitchenTicket | None:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if ticket is None:
            return None
        ticket.start_preparing()
        saved = self.ticket_repository.save(ticket)
        self.unit_of_work.commit()
        return saved

    def mark_ready_for_pickup(self, ticket_id: UUID) -> KitchenTicket | None:
        ticket = self.ticket_repository.get_by_id(ticket_id)
        if ticket is None:
            return None
        ticket.mark_ready_for_pickup()
        saved = self.ticket_repository.save(ticket)
        self.unit_of_work.commit()
        return saved
