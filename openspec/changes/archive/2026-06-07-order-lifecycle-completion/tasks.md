# Implementation Plan: Order Lifecycle Completion

## Overview

Complete the order lifecycle by publishing `KitchenTicketPreparing` and `KitchenTicketReadyForPickup` events from kitchen-service, consuming them in order-service to drive the Order to a `READY` terminal state, and updating the frontend to display the ready notification.

---

## Tasks

- [x] 1. Add outbox event builders for preparing and ready-for-pickup
  - In `services/kitchen-service/src/kitchen_service/application/outbox.py`:
  - [x] 1.1 Add `kitchen_ticket_preparing_event(ticket)` builder
    - `event_type="KitchenTicketPreparing"`, `aggregate_type="KitchenTicket"`
    - Payload: `ticket_id`, `order_id`, `restaurant_id`, `status`
    - _Requirements: order-ready-notification 2.1_
  - [x] 1.2 Add `kitchen_ticket_ready_for_pickup_event(ticket)` builder
    - `event_type="KitchenTicketReadyForPickup"`, `aggregate_type="KitchenTicket"`
    - Payload: `ticket_id`, `order_id`, `restaurant_id`, `status`
    - _Requirements: order-ready-notification 3.1_

- [x] 2. Fix `start_preparing()` and `mark_ready_for_pickup()` to write outbox events
  - In `services/kitchen-service/src/kitchen_service/application/tickets.py`:
  - [x] 2.1 Fix `start_preparing()` — add outbox write
    - Add idempotency guard: if ticket already `PREPARING`, return early without outbox event
    - After `ticket.start_preparing()`, call `self.outbox.add(kitchen_ticket_preparing_event(saved))` before commit
    - Import `kitchen_ticket_preparing_event` from outbox
    - _Requirements: order-ready-notification 2.1, 2.2_
  - [x] 2.2 Fix `mark_ready_for_pickup()` — add outbox write
    - Add idempotency guard: if ticket already `READY_FOR_PICKUP`, return early without outbox event
    - After `ticket.mark_ready_for_pickup()`, call `self.outbox.add(kitchen_ticket_ready_for_pickup_event(saved))` before commit
    - Import `kitchen_ticket_ready_for_pickup_event` from outbox
    - _Requirements: order-ready-notification 3.1, 3.2_

- [x] 3. Checkpoint — Ensure kitchen-service tests pass
  - Run `uv run pytest services/kitchen-service/src/tests/ -v` and fix any failures

- [x] 4. Add `READY` to `Order` domain and add `mark_ready()` transition
  - In `services/order-service/src/order_service/domain/models.py`:
  - [x] 4.1 Add `READY = "READY"` to `OrderStatus` StrEnum
    - _Requirements: order-ready-notification 1.1_
  - [x] 4.2 Add `mark_ready()` method to `Order`
    - Idempotent: return silently if already `READY`
    - Raise `InvalidOrderStatusTransitionError` if status is not `PREPARING` or `READY`
    - Set `self.status = OrderStatus.READY`
    - _Requirements: order-ready-notification 1.1, 1.2, 1.3_

- [x] 5. Add `mark_ready_order()` to `OrderLifecycleApplicationService`
  - In `services/order-service/src/order_service/application/lifecycle.py`:
  - [x] 5.1 Add `mark_ready_order(order_id)` method following same pattern as `approve_order()`
    - Return `None` if order not found; call `order.mark_ready()`, save, commit
    - _Requirements: order-ready-notification 4.2_

- [x] 6. Extend `order-service` consumer with preparing and ready handlers
  - In `services/order-service/src/order_service/consumer.py`:
  - [x] 6.1 Add `handle_kitchen_ticket_preparing()` async handler
    - Use `message.process(requeue=False)`
    - Validate `order_id` presence and UUID format; log `ERROR` and return on malformed payload
    - Call `service.mark_ready_order()` only if in appropriate state; otherwise just ack
    - Log `WARNING` and return on `None` (order not found)
    - Catch `InvalidOrderStatusTransitionError`, log `ERROR`, return
    - _Requirements: order-ready-notification 4.1_
  - [x] 6.2 Add `handle_kitchen_ticket_ready()` async handler
    - Same pattern as above, calls `service.mark_ready_order(order_id)`
    - _Requirements: order-ready-notification 4.2_
  - [x] 6.3 Declare and bind two new durable queues in `consume()`
    - `order.kitchen-ticket-preparing` bound to `ftgo.KitchenTicket.KitchenTicketPreparing`
    - `order.kitchen-ticket-ready` bound to `ftgo.KitchenTicket.KitchenTicketReadyForPickup`
    - _Requirements: order-ready-notification 4.1, 4.2_

- [x] 7. Checkpoint — Ensure order-service tests pass
  - Run `uv run pytest services/order-service/src/tests/ -v` and fix any failures

- [x] 8. Add Alembic migration for `READY` enum value
  - Create `services/order-service/migrations/versions/0006_add_ready_to_order_status.py`
  - `upgrade()`: `op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'READY'")`
  - `downgrade()`: `pass`
  - _Requirements: order-ready-notification 1.1_

- [x] 9. Document new event contracts
  - Append `KitchenTicketPreparing` and `KitchenTicketReadyForPickup` to `docs/contracts/events.md`
  - Each entry: exchange `ftgo.events`, routing key, delivery at-least-once, idempotency key `ticket_id`, JSON envelope example
  - _Requirements: kitchen-ticket-acceptance (modified), order-ready-notification 6.1_

- [x] 10. Update frontend for `READY` order status
  - [x] 10.1 Add `READY` to terminal statuses in `frontend/src/hooks/useOrderPolling.js`
    - Add to `TERMINAL_STATUSES` set
    - _Requirements: order-ready-notification 5.1_
  - [x] 10.2 Update `frontend/src/pages/OrderStatusPage.jsx` for ready message
    - Show "Your order is ready for pickup!" when status is `READY`
    - _Requirements: order-ready-notification 5.1_
  - [x] 10.3 Add `READY` colour to `frontend/src/components/StatusBadge.jsx`
    - `READY`: `bg-green-500/10 border-green-300/20 text-green-100`
    - _Requirements: order-ready-notification 5.2_

- [x] 11. Final checkpoint — Ensure all tests pass
  - Run `uv run pytest services/kitchen-service/src/tests/ services/order-service/src/tests/ -v`
  - Run `cd frontend && npx vite build` to verify build
  - Fix any failures before marking complete

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "2.2"] },
    { "id": 2, "tasks": ["4.1", "4.2"] },
    { "id": 3, "tasks": ["5.1", "8"] },
    { "id": 4, "tasks": ["6.1", "6.2"] },
    { "id": 5, "tasks": ["6.3", "9", "10.1", "10.2", "10.3"] }
  ]
}
```
