from uuid import UUID, uuid4

import pytest

from kitchen_service.application.commands import (
    CreateKitchenTicketCommand,
    CreateKitchenTicketLineItemCommand,
)
from kitchen_service.application.outbox import OutboxEvent
from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.domain.models import (
    InvalidKitchenTicketStatusTransitionError,
    KitchenTicket,
    KitchenTicketLineItem,
    KitchenTicketStatus,
)


class FakeKitchenTicketRepository:
    def __init__(self):
        self.tickets: list[KitchenTicket] = []

    def list_tickets(self) -> list[KitchenTicket]:
        return self.tickets

    def get_by_id(self, ticket_id: UUID) -> KitchenTicket | None:
        return next((t for t in self.tickets if t.id == ticket_id), None)

    def get_by_order_id(self, order_id: UUID) -> KitchenTicket | None:
        return next((ticket for ticket in self.tickets if ticket.order_id == order_id), None)

    def add(self, ticket: KitchenTicket) -> KitchenTicket:
        self.tickets.append(ticket)
        return ticket

    def save(self, ticket: KitchenTicket) -> KitchenTicket:
        for index, existing in enumerate(self.tickets):
            if existing.id == ticket.id:
                self.tickets[index] = ticket
                return ticket
        raise ValueError(f"Kitchen ticket {ticket.id} was not found")


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


def _create_ticket(order_id: UUID | None = None) -> tuple[
    KitchenTicket, FakeKitchenTicketRepository, FakeOutboxWriter, FakeUnitOfWork
]:
    repository = FakeKitchenTicketRepository()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)
    ticket = service.create_ticket_for_order(build_command(order_id or uuid4()))
    return ticket, repository, outbox, unit_of_work


def test_create_ticket_for_order_is_idempotent_by_order_id() -> None:
    repository = FakeKitchenTicketRepository()
    outbox = FakeOutboxWriter()
    unit_of_work = FakeUnitOfWork()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)
    order_id = uuid4()

    first = service.create_ticket_for_order(build_command(order_id))
    second = service.create_ticket_for_order(build_command(order_id))

    assert first == second
    assert len(repository.tickets) == 1
    assert repository.tickets[0].order_id == order_id
    assert repository.tickets[0].line_items[0].name == "Beef Noodles"
    assert unit_of_work.committed is True
    assert len(outbox.events) == 1
    assert outbox.events[0].event_type == "KitchenTicketCreated"
    assert outbox.events[0].payload["order_id"] == str(order_id)


def test_accept_ticket_transitions_from_create_pending() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)

    result = service.accept_ticket(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.ACCEPTED
    assert unit_of_work.committed is True


def test_accept_ticket_is_idempotent() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)

    service.accept_ticket(ticket.id)
    result = service.accept_ticket(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.ACCEPTED


def test_accept_ticket_returns_none_for_unknown_ticket() -> None:
    repository = FakeKitchenTicketRepository()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), FakeUnitOfWork())

    result = service.accept_ticket(uuid4())

    assert result is None


def test_start_preparing_transitions_from_accepted() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)
    service.accept_ticket(ticket.id)

    result = service.start_preparing(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.PREPARING


def test_start_preparing_is_idempotent() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)
    service.accept_ticket(ticket.id)
    service.start_preparing(ticket.id)

    result = service.start_preparing(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.PREPARING


def test_start_preparing_fails_if_not_accepted() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)

    with pytest.raises(InvalidKitchenTicketStatusTransitionError):
        service.start_preparing(ticket.id)


def test_mark_ready_for_pickup_transitions_from_preparing() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)
    service.accept_ticket(ticket.id)
    service.start_preparing(ticket.id)

    result = service.mark_ready_for_pickup(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.READY_FOR_PICKUP


def test_mark_ready_for_pickup_is_idempotent() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)
    service.accept_ticket(ticket.id)
    service.start_preparing(ticket.id)
    service.mark_ready_for_pickup(ticket.id)

    result = service.mark_ready_for_pickup(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.READY_FOR_PICKUP


def test_mark_ready_for_pickup_fails_if_not_preparing() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)

    with pytest.raises(InvalidKitchenTicketStatusTransitionError):
        service.mark_ready_for_pickup(ticket.id)


def test_full_kitchen_ticket_lifecycle() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), unit_of_work)

    assert ticket.status == KitchenTicketStatus.CREATE_PENDING

    accepted = service.accept_ticket(ticket.id)
    assert accepted is not None
    assert accepted.status == KitchenTicketStatus.ACCEPTED

    preparing = service.start_preparing(ticket.id)
    assert preparing is not None
    assert preparing.status == KitchenTicketStatus.PREPARING

    ready = service.mark_ready_for_pickup(ticket.id)
    assert ready is not None
    assert ready.status == KitchenTicketStatus.READY_FOR_PICKUP


# ---------------------------------------------------------------------------
# Task 4.1: Unit tests for accept_ticket / reject_ticket outbox behaviour
# ---------------------------------------------------------------------------


def test_accept_ticket_writes_outbox_event() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    outbox = FakeOutboxWriter()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)

    result = service.accept_ticket(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.ACCEPTED
    assert len(outbox.events) == 1
    assert outbox.events[0].event_type == "KitchenTicketAccepted"
    assert outbox.events[0].aggregate_id == str(ticket.id)
    assert outbox.events[0].payload["ticket_id"] == str(ticket.id)


def test_accept_ticket_already_accepted_no_outbox_event() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    outbox = FakeOutboxWriter()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)
    service.accept_ticket(ticket.id)  # first accept

    outbox.events.clear()
    result = service.accept_ticket(ticket.id)  # second accept (idempotent)

    assert result is not None
    assert result.status == KitchenTicketStatus.ACCEPTED
    assert len(outbox.events) == 0


def test_reject_ticket_transitions_to_cancelled() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    outbox = FakeOutboxWriter()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)

    result = service.reject_ticket(ticket.id)

    assert result is not None
    assert result.status == KitchenTicketStatus.CANCELLED
    assert len(outbox.events) == 1
    assert outbox.events[0].event_type == "KitchenTicketRejected"
    assert outbox.events[0].aggregate_id == str(ticket.id)
    assert outbox.events[0].payload["ticket_id"] == str(ticket.id)


def test_reject_ticket_already_cancelled_no_outbox_event() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    outbox = FakeOutboxWriter()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)
    service.reject_ticket(ticket.id)  # first reject

    outbox.events.clear()
    result = service.reject_ticket(ticket.id)  # second reject (idempotent)

    assert result is not None
    assert result.status == KitchenTicketStatus.CANCELLED
    assert len(outbox.events) == 0


def test_reject_ticket_returns_none_for_unknown_ticket() -> None:
    repository = FakeKitchenTicketRepository()
    service = KitchenTicketApplicationService(repository, FakeOutboxWriter(), FakeUnitOfWork())

    result = service.reject_ticket(uuid4())

    assert result is None


def test_reject_event_includes_rejection_reason() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    outbox = FakeOutboxWriter()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)

    service.reject_ticket(ticket.id, rejection_reason="Out of stock")

    assert outbox.events[0].payload["rejection_reason"] == "Out of stock"


def test_reject_event_omits_rejection_reason_key() -> None:
    ticket, repository, _outbox, unit_of_work = _create_ticket()
    outbox = FakeOutboxWriter()
    service = KitchenTicketApplicationService(repository, outbox, unit_of_work)

    service.reject_ticket(ticket.id, rejection_reason=None)

    assert "rejection_reason" not in outbox.events[0].payload
