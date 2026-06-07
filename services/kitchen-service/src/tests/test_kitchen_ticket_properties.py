"""Property-based tests for kitchen ticket outbox events and domain state machine.

Feature: kitchen-ticket-acceptance
Properties 1-6
"""

from uuid import UUID

from hypothesis import given, settings, strategies as st

from kitchen_service.application.outbox import (
    OutboxEvent,
    kitchen_ticket_accepted_event,
    kitchen_ticket_rejected_event,
)
from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.domain.models import (
    InvalidKitchenTicketStatusTransitionError,
    KitchenTicket,
    KitchenTicketLineItem,
    KitchenTicketStatus,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

line_item_st = st.builds(
    KitchenTicketLineItem,
    menu_item_id=st.integers(min_value=1),
    name=st.text(min_size=1, max_size=50),
    quantity=st.integers(min_value=1, max_value=100),
)

ticket_st = st.builds(
    KitchenTicket,
    order_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    line_items=st.lists(line_item_st, min_size=1, max_size=5),
    status=st.sampled_from(KitchenTicketStatus),
)

# Strategy: ticket in CREATE_PENDING status (for accept/reject happy-path tests)
ticket_create_pending_st = st.builds(
    KitchenTicket,
    order_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    line_items=st.lists(line_item_st, min_size=1, max_size=5),
    status=st.just(KitchenTicketStatus.CREATE_PENDING),
)

# Statuses that are invalid sources for accept (not CREATE_PENDING, not ACCEPTED)
_invalid_for_accept = [
    s for s in KitchenTicketStatus if s not in {KitchenTicketStatus.CREATE_PENDING, KitchenTicketStatus.ACCEPTED}
]

# Statuses that are invalid sources for reject (not CREATE_PENDING, not CANCELLED)
_invalid_for_reject = [
    s for s in KitchenTicketStatus if s not in {KitchenTicketStatus.CREATE_PENDING, KitchenTicketStatus.CANCELLED}
]

# Strategy: ticket in a status that is invalid for accept
ticket_invalid_for_accept_st = st.builds(
    KitchenTicket,
    order_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    line_items=st.lists(line_item_st, min_size=1, max_size=5),
    status=st.sampled_from(_invalid_for_accept) if _invalid_for_accept else st.none(),
)

# Strategy: ticket in a status that is invalid for reject
ticket_invalid_for_reject_st = st.builds(
    KitchenTicket,
    order_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    line_items=st.lists(line_item_st, min_size=1, max_size=5),
    status=st.sampled_from(_invalid_for_reject) if _invalid_for_reject else st.none(),
)

# Strategy: ticket in ACCEPTED status (for accept idempotency)
ticket_accepted_st = st.builds(
    KitchenTicket,
    order_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    line_items=st.lists(line_item_st, min_size=1, max_size=5),
    status=st.just(KitchenTicketStatus.ACCEPTED),
)

# Strategy: ticket in CANCELLED status (for reject idempotency)
ticket_cancelled_st = st.builds(
    KitchenTicket,
    order_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    line_items=st.lists(line_item_st, min_size=1, max_size=5),
    status=st.just(KitchenTicketStatus.CANCELLED),
)

# ---------------------------------------------------------------------------
# Fakes (in-memory, for application-level property tests)
# ---------------------------------------------------------------------------


class _FakeKitchenTicketRepository:
    def __init__(self):
        self.tickets: list[KitchenTicket] = []

    def list_tickets(self) -> list[KitchenTicket]:
        return self.tickets

    def get_by_id(self, ticket_id: UUID) -> KitchenTicket | None:
        return next((t for t in self.tickets if t.id == ticket_id), None)

    def get_by_order_id(self, order_id: UUID) -> KitchenTicket | None:
        return next((t for t in self.tickets if t.order_id == order_id), None)

    def add(self, ticket: KitchenTicket) -> KitchenTicket:
        self.tickets.append(ticket)
        return ticket

    def save(self, ticket: KitchenTicket) -> KitchenTicket:
        for i, existing in enumerate(self.tickets):
            if existing.id == ticket.id:
                self.tickets[i] = ticket
                return ticket
        raise ValueError(f"Ticket {ticket.id} not found")


class _FakeOutboxWriter:
    def __init__(self):
        self.events: list[OutboxEvent] = []

    def add(self, event: OutboxEvent) -> None:
        self.events.append(event)


class _FakeUnitOfWork:
    def __init__(self):
        self.committed = False

    def commit(self) -> None:
        self.committed = True


def _setup_service(
    ticket: KitchenTicket,
) -> tuple[KitchenTicketApplicationService, _FakeKitchenTicketRepository, _FakeOutboxWriter]:
    """Create a service wired with fakes and pre-seed the given ticket."""
    repo = _FakeKitchenTicketRepository()
    repo.add(ticket)
    outbox = _FakeOutboxWriter()
    uow = _FakeUnitOfWork()
    service = KitchenTicketApplicationService(repo, outbox, uow)
    return service, repo, outbox

# ---------------------------------------------------------------------------
# Property 6: Outbox event payload completeness
# ---------------------------------------------------------------------------


class TestOutboxEventPayloadCompleteness:
    """Property 6: Outbox event payloads contain all required fields."""

    @given(ticket_st)
    @settings(max_examples=100)
    def test_accepted_event_has_required_envelope_fields(self, ticket: KitchenTicket) -> None:
        event = kitchen_ticket_accepted_event(ticket)
        assert event.event_type == "KitchenTicketAccepted"
        assert event.aggregate_type == "KitchenTicket"
        assert event.aggregate_id == str(ticket.id)

    @given(ticket_st)
    @settings(max_examples=100)
    def test_accepted_event_payload_contains_all_required_keys(
        self, ticket: KitchenTicket
    ) -> None:
        event = kitchen_ticket_accepted_event(ticket)
        assert event.payload["ticket_id"] == str(ticket.id)
        assert event.payload["order_id"] == str(ticket.order_id)
        assert event.payload["restaurant_id"] == ticket.restaurant_id
        assert event.payload["status"] == ticket.status.value

    @given(ticket_st)
    @settings(max_examples=100)
    def test_rejected_event_has_required_envelope_fields(self, ticket: KitchenTicket) -> None:
        event = kitchen_ticket_rejected_event(ticket)
        assert event.event_type == "KitchenTicketRejected"
        assert event.aggregate_type == "KitchenTicket"
        assert event.aggregate_id == str(ticket.id)

    @given(ticket_st)
    @settings(max_examples=100)
    def test_rejected_event_payload_contains_all_required_keys(
        self, ticket: KitchenTicket
    ) -> None:
        event = kitchen_ticket_rejected_event(ticket)
        assert event.payload["ticket_id"] == str(ticket.id)
        assert event.payload["order_id"] == str(ticket.order_id)
        assert event.payload["restaurant_id"] == ticket.restaurant_id
        assert event.payload["status"] == ticket.status.value

    @given(ticket_st)
    @settings(max_examples=100)
    def test_rejected_event_omits_rejection_reason_when_not_provided(
        self, ticket: KitchenTicket
    ) -> None:
        event = kitchen_ticket_rejected_event(ticket)
        assert "rejection_reason" not in event.payload

    @given(ticket_st, st.text(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_rejected_event_includes_rejection_reason_when_provided(
        self, ticket: KitchenTicket, reason: str
    ) -> None:
        event = kitchen_ticket_rejected_event(ticket, rejection_reason=reason)
        assert event.payload["rejection_reason"] == reason

    @given(ticket_st)
    @settings(max_examples=100)
    def test_rejected_event_with_none_reason_omits_key(
        self, ticket: KitchenTicket
    ) -> None:
        event = kitchen_ticket_rejected_event(ticket, rejection_reason=None)
        assert "rejection_reason" not in event.payload

    @given(ticket_st)
    @settings(max_examples=100)
    def test_accepted_event_payload_has_exactly_four_keys(
        self, ticket: KitchenTicket
    ) -> None:
        event = kitchen_ticket_accepted_event(ticket)
        assert set(event.payload.keys()) == {
            "ticket_id", "order_id", "restaurant_id", "status"
        }


# ---------------------------------------------------------------------------
# Property 3: Invalid transitions raise an error (domain-level)
# ---------------------------------------------------------------------------


class TestInvalidTransitionsRaiseError:
    """Property 3: Invalid transitions raise InvalidKitchenTicketStatusTransitionError."""

    @given(ticket_invalid_for_accept_st)
    @settings(max_examples=100)
    def test_accept_raises_on_invalid_status(self, ticket: KitchenTicket) -> None:
        try:
            ticket.accept()
            assert False, f"Expected InvalidKitchenTicketStatusTransitionError for status {ticket.status}"
        except InvalidKitchenTicketStatusTransitionError as exc:
            assert exc.target == KitchenTicketStatus.ACCEPTED
            assert exc.current == ticket.status

    @given(ticket_invalid_for_reject_st)
    @settings(max_examples=100)
    def test_reject_raises_on_invalid_status(self, ticket: KitchenTicket) -> None:
        try:
            ticket.reject()
            assert False, f"Expected InvalidKitchenTicketStatusTransitionError for status {ticket.status}"
        except InvalidKitchenTicketStatusTransitionError as exc:
            assert exc.target == KitchenTicketStatus.CANCELLED
            assert exc.current == ticket.status


# ---------------------------------------------------------------------------
# Property 1: Accept idempotency — no duplicate outbox events (application-level)
# ---------------------------------------------------------------------------


class TestAcceptIdempotency:
    """Property 1: Accept idempotency — no duplicate outbox events."""

    @given(ticket_accepted_st)
    @settings(max_examples=100)
    def test_accept_on_accepted_ticket_produces_no_outbox_event(
        self, ticket: KitchenTicket
    ) -> None:
        service, _repo, outbox = _setup_service(ticket)
        result = service.accept_ticket(ticket.id)

        assert result is not None
        assert result.status == KitchenTicketStatus.ACCEPTED
        assert len(outbox.events) == 0


# ---------------------------------------------------------------------------
# Property 2: Reject idempotency — no duplicate outbox events (application-level)
# ---------------------------------------------------------------------------


class TestRejectIdempotency:
    """Property 2: Reject idempotency — no duplicate outbox events."""

    @given(ticket_cancelled_st)
    @settings(max_examples=100)
    def test_reject_on_cancelled_ticket_produces_no_outbox_event(
        self, ticket: KitchenTicket
    ) -> None:
        service, _repo, outbox = _setup_service(ticket)
        result = service.reject_ticket(ticket.id)

        assert result is not None
        assert result.status == KitchenTicketStatus.CANCELLED
        assert len(outbox.events) == 0


# ---------------------------------------------------------------------------
# Property 4: Accepting a CREATE_PENDING ticket produces exactly one outbox event
# ---------------------------------------------------------------------------


class TestAcceptProducesOutboxEvent:
    """Property 4: Accepting CREATE_PENDING produces exactly one KitchenTicketAccepted event."""

    @given(ticket_create_pending_st)
    @settings(max_examples=100)
    def test_accept_on_create_pending_produces_one_outbox_event(
        self, ticket: KitchenTicket
    ) -> None:
        service, _repo, outbox = _setup_service(ticket)
        result = service.accept_ticket(ticket.id)

        assert result is not None
        assert result.status == KitchenTicketStatus.ACCEPTED
        assert len(outbox.events) == 1
        assert outbox.events[0].event_type == "KitchenTicketAccepted"
        assert outbox.events[0].aggregate_id == str(ticket.id)
        assert outbox.events[0].payload["ticket_id"] == str(ticket.id)


# ---------------------------------------------------------------------------
# Property 5: Rejecting a CREATE_PENDING ticket produces exactly one outbox event
# ---------------------------------------------------------------------------


class TestRejectProducesOutboxEvent:
    """Property 5: Rejecting CREATE_PENDING produces exactly one KitchenTicketRejected event."""

    @given(ticket_create_pending_st)
    @settings(max_examples=100)
    def test_reject_on_create_pending_produces_one_outbox_event(
        self, ticket: KitchenTicket
    ) -> None:
        service, _repo, outbox = _setup_service(ticket)
        result = service.reject_ticket(ticket.id)

        assert result is not None
        assert result.status == KitchenTicketStatus.CANCELLED
        assert len(outbox.events) == 1
        assert outbox.events[0].event_type == "KitchenTicketRejected"
        assert outbox.events[0].aggregate_id == str(ticket.id)
        assert outbox.events[0].payload["ticket_id"] == str(ticket.id)

    @given(ticket_create_pending_st, st.text(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_reject_with_reason_includes_it_in_payload(
        self, ticket: KitchenTicket, reason: str
    ) -> None:
        service, _repo, outbox = _setup_service(ticket)
        result = service.reject_ticket(ticket.id, rejection_reason=reason)

        assert result is not None
        assert result.status == KitchenTicketStatus.CANCELLED
        assert outbox.events[0].payload["rejection_reason"] == reason

    @given(ticket_create_pending_st)
    @settings(max_examples=100)
    def test_reject_without_reason_omits_key_from_payload(
        self, ticket: KitchenTicket
    ) -> None:
        service, _repo, outbox = _setup_service(ticket)
        result = service.reject_ticket(ticket.id, rejection_reason=None)

        assert result is not None
        assert result.status == KitchenTicketStatus.CANCELLED
        assert "rejection_reason" not in outbox.events[0].payload
