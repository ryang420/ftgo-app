"""Property-based tests for kitchen ticket outbox events and domain state machine.

Feature: kitchen-ticket-acceptance
"""

from hypothesis import given, settings, strategies as st

from kitchen_service.application.outbox import (
    kitchen_ticket_accepted_event,
    kitchen_ticket_rejected_event,
)
from kitchen_service.domain.models import (
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
