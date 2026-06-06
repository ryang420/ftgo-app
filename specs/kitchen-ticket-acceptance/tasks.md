# Implementation Plan: Kitchen Ticket Acceptance

## Overview

Implement the kitchen ticket acceptance flow across `kitchen-service` and `order-service`. Kitchen staff can accept or reject a ticket via two REST endpoints. Each operation drives a domain state transition, writes a domain event to the transactional outbox atomically, and publishes it to RabbitMQ. `order-service` consumes both events and drives the `Order` state machine forward: accepted → `PREPARING`, rejected → `CANCELLED`.

## Tasks

- [ ] 1. Add `reject()` method to `KitchenTicket` domain model
  - In `services/kitchen-service/src/kitchen_service/domain/models.py`, add a `reject()` method to `KitchenTicket` following the same guard pattern as `accept()`: return silently if already `CANCELLED`, raise `InvalidKitchenTicketStatusTransitionError` if status is not `CREATE_PENDING`, otherwise set `status = CANCELLED`
  - _Requirements: 2.1, 3.1, 3.2, 3.3_

- [ ] 2. Add outbox event builders and new commands for accept/reject
  - [ ] 2.1 Add `kitchen_ticket_accepted_event()` and `kitchen_ticket_rejected_event()` builder functions to `services/kitchen-service/src/kitchen_service/application/outbox.py`
    - `kitchen_ticket_accepted_event` payload: `ticket_id`, `order_id`, `restaurant_id`, `status`
    - `kitchen_ticket_rejected_event` payload: same fields plus optional `rejection_reason` (omit key entirely when `None`)
    - _Requirements: 4.2, 5.2_

  - [ ] 2.2 Add `AcceptKitchenTicketCommand` and `RejectKitchenTicketCommand` dataclasses to `services/kitchen-service/src/kitchen_service/application/commands.py`
    - `AcceptKitchenTicketCommand(ticket_id: UUID)`
    - `RejectKitchenTicketCommand(ticket_id: UUID, rejection_reason: str | None = None)`
    - _Requirements: 1.1, 2.1_

  - [ ]* 2.3 Write property test for outbox event payload completeness (Property 6)
    - **Property 6: Outbox event payloads contain all required fields**
    - For any `KitchenTicket`, `kitchen_ticket_accepted_event(ticket)` must produce an `OutboxEvent` with `event_type="KitchenTicketAccepted"`, `aggregate_type="KitchenTicket"`, `aggregate_id=str(ticket.id)`, and payload containing `ticket_id`, `order_id`, `restaurant_id`, `status`
    - `kitchen_ticket_rejected_event(ticket)` must produce `event_type="KitchenTicketRejected"` with the same required fields; `rejection_reason` appears in payload only when provided
    - Use `@given(st.builds(KitchenTicket, order_id=st.uuids(), restaurant_id=st.integers(min_value=1), line_items=st.lists(..., min_size=1)))` in a new file `services/kitchen-service/src/tests/test_kitchen_ticket_properties.py`
    - **Validates: Requirements 4.2, 5.2, 10.1, 10.2, 10.3**

- [ ] 3. Fix `accept_ticket()` and add `reject_ticket()` in application service
  - [ ] 3.1 Fix `accept_ticket()` in `services/kitchen-service/src/kitchen_service/application/tickets.py` to write to the outbox
    - Add idempotency guard: if ticket is already `ACCEPTED`, return early without adding outbox event
    - After `ticket.accept()`, call `self.outbox.add(kitchen_ticket_accepted_event(saved))` before commit
    - _Requirements: 1.1, 1.3, 4.1_

  - [ ] 3.2 Add `reject_ticket(ticket_id, rejection_reason=None)` method to `KitchenTicketApplicationService`
    - Return `None` for unknown ticket
    - Idempotency guard: if status already `CANCELLED`, return early without adding outbox event
    - Call `ticket.reject()`, save, add `kitchen_ticket_rejected_event(saved, rejection_reason)` to outbox, commit
    - _Requirements: 2.1, 2.2, 2.3, 5.1_

  - [ ]* 3.3 Write property test for accept idempotency (Property 1)
    - **Property 1: Accept idempotency — no duplicate outbox events**
    - For any `KitchenTicket` already in `ACCEPTED` status, calling `accept_ticket()` must not add any entry to `FakeOutboxWriter`, and status must remain `ACCEPTED`
    - Add to `services/kitchen-service/src/tests/test_kitchen_ticket_properties.py`
    - **Validates: Requirements 1.3**

  - [ ]* 3.4 Write property test for reject idempotency (Property 2)
    - **Property 2: Reject idempotency — no duplicate outbox events**
    - For any `KitchenTicket` already in `CANCELLED` status, calling `reject_ticket()` must not add any entry to `FakeOutboxWriter`, and status must remain `CANCELLED`
    - Add to `services/kitchen-service/src/tests/test_kitchen_ticket_properties.py`
    - **Validates: Requirements 2.3**

  - [ ]* 3.5 Write property test for invalid transitions raise error (Property 3)
    - **Property 3: Invalid transitions raise an error**
    - For any `KitchenTicket` whose status is not `CREATE_PENDING` or `ACCEPTED`, calling `ticket.accept()` must raise `InvalidKitchenTicketStatusTransitionError`
    - For any `KitchenTicket` whose status is not `CREATE_PENDING` or `CANCELLED`, calling `ticket.reject()` must raise `InvalidKitchenTicketStatusTransitionError`
    - Add to `services/kitchen-service/src/tests/test_kitchen_ticket_properties.py`
    - **Validates: Requirements 1.4, 2.4, 3.1, 3.2**

  - [ ]* 3.6 Write property test for accept producing exactly one outbox event (Property 4)
    - **Property 4: Accepting a CREATE_PENDING ticket produces exactly one outbox event**
    - For any `KitchenTicket` in `CREATE_PENDING` status with any `order_id`, `restaurant_id`, and line items, calling `accept_ticket()` must result in exactly one `KitchenTicketAccepted` outbox event and ticket status `ACCEPTED`
    - Add to `services/kitchen-service/src/tests/test_kitchen_ticket_properties.py`
    - **Validates: Requirements 1.1, 4.1**

  - [ ]* 3.7 Write property test for reject producing exactly one outbox event (Property 5)
    - **Property 5: Rejecting a CREATE_PENDING ticket produces exactly one outbox event**
    - For any `KitchenTicket` in `CREATE_PENDING` status with any `order_id`, `restaurant_id`, and line items, calling `reject_ticket()` must result in exactly one `KitchenTicketRejected` outbox event and ticket status `CANCELLED`
    - Add to `services/kitchen-service/src/tests/test_kitchen_ticket_properties.py`
    - **Validates: Requirements 2.1, 5.1**

- [ ] 4. Add unit tests for kitchen-service accept/reject application service
  - Add to `services/kitchen-service/src/tests/test_kitchen_tickets.py` (extend existing file):
  - [ ]* 4.1 Write unit tests for `accept_ticket()` outbox behavior and `reject_ticket()`
    - `test_accept_ticket_writes_outbox_event`: `CREATE_PENDING` → one `KitchenTicketAccepted` in `FakeOutboxWriter`
    - `test_accept_ticket_already_accepted_no_outbox_event`: calling on `ACCEPTED` ticket → `FakeOutboxWriter` stays empty
    - `test_reject_ticket_transitions_to_cancelled`: `CREATE_PENDING` → one `KitchenTicketRejected` event
    - `test_reject_ticket_already_cancelled_no_outbox_event`: idempotency check
    - `test_reject_ticket_returns_none_for_unknown_ticket`
    - `test_reject_event_includes_rejection_reason`: when `rejection_reason` provided, appears in payload
    - `test_reject_event_omits_rejection_reason_key`: when not provided, key is absent from payload
    - _Requirements: 1.1, 1.3, 2.1, 2.3, 4.1, 5.1, 5.2_

- [ ] 5. Checkpoint — Ensure all kitchen-service unit and property tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Add `POST /{ticket_id}/accept` fix and `POST /{ticket_id}/reject` endpoint to kitchen-service API
  - In `services/kitchen-service/src/kitchen_service/api/routes/tickets.py`:
  - [ ] 6.1 Update the existing `/accept` route's 409 error response body to include `current_status` and `target_status` fields (access via `exc.current` and `exc.target`)
    - _Requirements: 1.4_

  - [ ] 6.2 Add `POST /{ticket_id}/reject` route using `service.reject_ticket(ticket_id)` with the same 404/409 pattern; 409 body must include `current_status` and `target_status`
    - _Requirements: 2.1, 2.2, 2.4_

- [ ] 7. Add `PREPARING` to `Order` domain and extend `cancel()`
  - In `services/order-service/src/order_service/domain/models.py`:
  - [ ] 7.1 Add `PREPARING = "PREPARING"` to `OrderStatus` StrEnum
    - _Requirements: 8.1_

  - [ ] 7.2 Add `begin_preparing()` method to `Order`
    - Idempotent: return silently if already `PREPARING`
    - Raise `InvalidOrderStatusTransitionError` if status is not `APPROVED` or `PREPARING`
    - Set `self.status = OrderStatus.PREPARING`
    - _Requirements: 6.2, 8.1, 8.2, 8.3_

  - [ ] 7.3 Extend `cancel()` to accept `PREPARING` as a valid source status
    - Change the guard from `{PENDING, APPROVED}` to `{PENDING, APPROVED, PREPARING}`
    - _Requirements: 7.2, 8.4_

  - [ ]* 7.4 Write property test for `begin_preparing` state machine correctness (Property 7)
    - **Property 7: Order begin_preparing state machine correctness**
    - For any `Order` in `APPROVED` status, `begin_preparing()` must transition to `PREPARING`; for `PREPARING` it must be a no-op; for any other status it must raise `InvalidOrderStatusTransitionError`
    - Create `services/order-service/src/tests/test_order_domain_properties.py` with `@given(st.builds(Order, ...))`
    - **Validates: Requirements 6.2, 8.1, 8.2, 8.3**

  - [ ]* 7.5 Write property test for `cancel()` accepting PREPARING source (Property 8)
    - **Property 8: Order cancel accepts PREPARING as a valid source status**
    - For any `Order` in `PENDING`, `APPROVED`, or `PREPARING` status, `cancel()` must transition to `CANCELLED`; for `CANCELLED` it must be idempotent; for `REJECTED` it must raise `InvalidOrderStatusTransitionError`
    - Add to `services/order-service/src/tests/test_order_domain_properties.py`
    - **Validates: Requirements 7.2, 8.4**

- [ ] 8. Add unit tests for `Order` domain changes
  - Add to `services/order-service/src/tests/test_place_order.py` (extend existing file):
  - [ ]* 8.1 Write unit tests for `begin_preparing()` and extended `cancel()`
    - `test_begin_preparing_transitions_from_approved`: `APPROVED` → `PREPARING`
    - `test_begin_preparing_is_idempotent`: calling twice stays `PREPARING`
    - `test_begin_preparing_raises_on_invalid_status`: raises for `PENDING`, `REJECTED`, `CANCELLED`
    - `test_cancel_accepts_preparing_as_source`: `PREPARING` → `CANCELLED`
    - _Requirements: 6.2, 7.2, 8.1, 8.2, 8.3, 8.4_

- [ ] 9. Add `begin_preparing_order()` and `cancel_order()` to `OrderLifecycleApplicationService`
  - In `services/order-service/src/order_service/application/lifecycle.py`:
  - [ ] 9.1 Add `begin_preparing_order(order_id)` method following the same pattern as `approve_order()`
    - Return `None` if order not found; call `order.begin_preparing()`, save, commit
    - _Requirements: 6.1, 6.2_

  - [ ] 9.2 Add `cancel_order(order_id)` method following the same pattern
    - Return `None` if order not found; call `order.cancel()`, save, commit
    - _Requirements: 7.1_

- [ ] 10. Extend `order-service` consumer to handle `KitchenTicketAccepted` and `KitchenTicketRejected`
  - In `services/order-service/src/order_service/consumer.py`:
  - [ ] 10.1 Add `handle_kitchen_ticket_accepted()` async handler
    - Use `message.process(requeue=False)` so commit failures propagate as nack/requeue
    - Validate `order_id` presence and UUID format; log `ERROR` and ack (return) on malformed payload
    - Call `service.begin_preparing_order(order_id)`; log `WARNING` and return on `None` (not found); catch `InvalidOrderStatusTransitionError`, log `ERROR`, return
    - _Requirements: 6.1, 6.3, 6.4, 6.5, 6.6, 9.1, 9.3, 9.4_

  - [ ] 10.2 Add `handle_kitchen_ticket_rejected()` async handler following the same pattern
    - Call `service.cancel_order(order_id)` instead
    - _Requirements: 7.1, 7.3, 7.4, 7.5, 9.2, 9.3, 9.4_

  - [ ] 10.3 Declare and bind two new durable queues in `consume()` setup
    - `order.kitchen-ticket-accepted` bound to `ftgo.KitchenTicket.KitchenTicketAccepted`
    - `order.kitchen-ticket-rejected` bound to `ftgo.KitchenTicket.KitchenTicketRejected`
    - _Requirements: 6.1, 7.1_

- [ ] 11. Checkpoint — Ensure all order-service unit and property tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Add Alembic migration to extend `order_status` PostgreSQL enum
  - Create `services/order-service/migrations/versions/0005_add_preparing_to_order_status.py`
  - Set `transaction_per_migration = False` (or use `op.execute()` outside a transaction block) since `ALTER TYPE … ADD VALUE` cannot run inside a PostgreSQL transaction
  - `upgrade()`: `op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'PREPARING'")`
  - `downgrade()`: `pass` (removing an enum value requires full type recreation; defer to rollback plan)
  - _Requirements: 8.1_

- [ ] 13. Document `KitchenTicketAccepted` and `KitchenTicketRejected` event contracts
  - Append both events to `docs/contracts/events.md` following the existing format
  - `KitchenTicketAccepted`: exchange `ftgo.events`, routing key `ftgo.KitchenTicket.KitchenTicketAccepted`, delivery at-least-once, idempotency key `ticket_id`, JSON envelope with `event_type`, `aggregate_type`, `aggregate_id`, `occurred_at`, payload with `ticket_id`, `order_id`, `restaurant_id`, `status`
  - `KitchenTicketRejected`: same structure, routing key `ftgo.KitchenTicket.KitchenTicketRejected`, payload also includes optional `rejection_reason` (omit key when absent)
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 14. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests use Hypothesis (`@given`) with `st.builds()` strategies; place in separate `test_*_properties.py` files
- All unit tests use fakes/in-memory implementations — no real DB or RabbitMQ
- The Alembic migration (task 12) uses `ALTER TYPE … ADD VALUE IF NOT EXISTS` which must run outside a transaction block in PostgreSQL
- `KitchenTicketRead` already includes `id`, `order_id`, `restaurant_id`, `status`, and `line_items` — the response schema needs no changes; `ticket_id` maps to the `id` field in the response
- The existing `/accept` route (task 6.1) only needs its 409 body enriched — the method signature and response model are already correct

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1", "2.1", "2.2"] },
    { "id": 1, "tasks": ["2.3", "3.1", "3.2"] },
    { "id": 2, "tasks": ["3.3", "3.4", "3.5", "3.6", "3.7", "4.1"] },
    { "id": 3, "tasks": ["6.1", "6.2", "7.1"] },
    { "id": 4, "tasks": ["7.2", "7.3"] },
    { "id": 5, "tasks": ["7.4", "7.5", "8.1", "9.1", "9.2"] },
    { "id": 6, "tasks": ["10.1", "10.2"] },
    { "id": 7, "tasks": ["10.3", "12", "13"] }
  ]
}
```
