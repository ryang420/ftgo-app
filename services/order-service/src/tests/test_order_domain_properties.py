"""Property-based tests for Order domain state machine.

Feature: kitchen-ticket-acceptance
Properties 7-8
"""

from decimal import Decimal
from uuid import uuid4

from hypothesis import given, settings
from hypothesis import strategies as st
from order_service.domain.models import (
    InvalidOrderStatusTransitionError,
    Order,
    OrderLineItem,
    OrderStatus,
)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_line_item_st = st.builds(
    OrderLineItem,
    menu_item_id=st.integers(min_value=1),
    name=st.text(min_size=1, max_size=50),
    quantity=st.integers(min_value=1, max_value=100),
    unit_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000.00"), places=2),
)

_address_st = st.text(min_size=1, max_size=100).filter(lambda s: s.strip() != "")

_order_base = dict(
    consumer_id=st.uuids(),
    restaurant_id=st.integers(min_value=1, max_value=10_000),
    currency=st.sampled_from(["USD", "EUR", "CNY"]),
    delivery_address=_address_st,
    line_items=st.lists(_line_item_st, min_size=1, max_size=5),
)

# Strategy: Order in APPROVED status (for begin_preparing happy path)
order_approved_st = st.builds(Order, **_order_base, status=st.just(OrderStatus.APPROVED))

# Strategy: Order in PREPARING status (for begin_preparing idempotency)
order_preparing_st = st.builds(Order, **_order_base, status=st.just(OrderStatus.PREPARING))

# Statuses invalid for begin_preparing (not APPROVED, not PREPARING)
_invalid_for_begin_preparing = [
    s
    for s in OrderStatus
    if s not in {OrderStatus.APPROVED, OrderStatus.PREPARING}
]

# Strategy: Order in a status invalid for begin_preparing
order_invalid_for_begin_preparing_st = st.builds(
    Order,
    **_order_base,
    status=st.sampled_from(_invalid_for_begin_preparing),
)

# Statuses that are valid sources for cancel (PENDING, APPROVED, PREPARING)
_valid_for_cancel = [
    s
    for s in OrderStatus
    if s in {OrderStatus.PENDING, OrderStatus.APPROVED, OrderStatus.PREPARING}
]

# Strategy: Order in a status valid for cancel
order_cancellable_st = st.builds(
    Order,
    **_order_base,
    status=st.sampled_from(_valid_for_cancel),
)

# Strategy: Order in CANCELLED status (for cancel idempotency)
order_cancelled_st = st.builds(Order, **_order_base, status=st.just(OrderStatus.CANCELLED))

# Strategy: Order in REJECTED status (cancel should raise)
order_rejected_st = st.builds(Order, **_order_base, status=st.just(OrderStatus.REJECTED))


# ---------------------------------------------------------------------------
# Property 7: Order begin_preparing state machine correctness
# ---------------------------------------------------------------------------


class TestBeginPreparingStateMachine:
    """Property 7: begin_preparing transitions APPROVED→PREPARING, idempotent on PREPARING,
    raises on all other statuses."""

    @given(order_approved_st)
    @settings(max_examples=100)
    def test_begin_preparing_from_approved_transitions_to_preparing(
        self, order: Order
    ) -> None:
        order.begin_preparing()
        assert order.status == OrderStatus.PREPARING

    @given(order_preparing_st)
    @settings(max_examples=100)
    def test_begin_preparing_is_idempotent_on_preparing(self, order: Order) -> None:
        original_id = order.id
        order.begin_preparing()
        assert order.status == OrderStatus.PREPARING
        assert order.id == original_id

    @given(order_invalid_for_begin_preparing_st)
    @settings(max_examples=100)
    def test_begin_preparing_raises_on_invalid_status(self, order: Order) -> None:
        try:
            order.begin_preparing()
            raise AssertionError(
                f"Expected InvalidOrderStatusTransitionError for status {order.status}"
            )
        except InvalidOrderStatusTransitionError as exc:
            assert exc.target == OrderStatus.PREPARING
            assert exc.current == order.status


# ---------------------------------------------------------------------------
# Property 8: Order cancel accepts PREPARING as a valid source
# ---------------------------------------------------------------------------


class TestCancelAcceptsPreparing:
    """Property 8: cancel transitions PENDING/APPROVED/PREPARING→CANCELLED,
    idempotent on CANCELLED, raises on REJECTED."""

    @given(order_cancellable_st)
    @settings(max_examples=100)
    def test_cancel_from_valid_source_transitions_to_cancelled(self, order: Order) -> None:
        order.cancel()
        assert order.status == OrderStatus.CANCELLED

    @given(order_cancelled_st)
    @settings(max_examples=100)
    def test_cancel_is_idempotent_on_cancelled(self, order: Order) -> None:
        order.cancel()
        assert order.status == OrderStatus.CANCELLED

    @given(order_rejected_st)
    @settings(max_examples=100)
    def test_cancel_raises_on_rejected(self, order: Order) -> None:
        try:
            order.cancel()
            raise AssertionError(
                f"Expected InvalidOrderStatusTransitionError for status {order.status}"
            )
        except InvalidOrderStatusTransitionError as exc:
            assert exc.target == OrderStatus.CANCELLED
            assert exc.current == OrderStatus.REJECTED


def _order_with_status(status: OrderStatus) -> Order:
    return Order(
        consumer_id=uuid4(),
        restaurant_id=10,
        currency="USD",
        delivery_address="123 Main St",
        line_items=[
            OrderLineItem(
                menu_item_id=20,
                name="Beef Noodles",
                quantity=1,
                unit_price=Decimal("12.00"),
            )
        ],
        status=status,
    )


def test_delivery_status_happy_path_reaches_delivered() -> None:
    order = _order_with_status(OrderStatus.READY)

    order.mark_delivery_assigned()
    assert order.status == OrderStatus.DELIVERY_ASSIGNED

    order.mark_out_for_delivery()
    assert order.status == OrderStatus.OUT_FOR_DELIVERY

    order.mark_delivered()
    assert order.status == OrderStatus.DELIVERED


def test_delivery_status_transitions_are_idempotent_for_target_status() -> None:
    order = _order_with_status(OrderStatus.READY)

    order.mark_delivery_assigned()
    order.mark_delivery_assigned()
    assert order.status == OrderStatus.DELIVERY_ASSIGNED

    order.mark_out_for_delivery()
    order.mark_out_for_delivery()
    assert order.status == OrderStatus.OUT_FOR_DELIVERY

    order.mark_delivered()
    order.mark_delivered()
    assert order.status == OrderStatus.DELIVERED


def test_delivery_status_transition_rejects_out_of_order_event() -> None:
    order = _order_with_status(OrderStatus.READY)

    try:
        order.mark_out_for_delivery()
        raise AssertionError("Expected InvalidOrderStatusTransitionError")
    except InvalidOrderStatusTransitionError as exc:
        assert exc.current == OrderStatus.READY
        assert exc.target == OrderStatus.OUT_FOR_DELIVERY
