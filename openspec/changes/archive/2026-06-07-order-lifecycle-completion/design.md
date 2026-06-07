# Design Document — Order Lifecycle Completion

## Context

The kitchen-ticket-acceptance feature (now archived) implemented accept/reject for kitchen tickets. Kitchen staff can also call `/prepare` and `/ready-for-pickup` on tickets — those API routes and domain methods exist — but no outbox events are published for those transitions. The order-service consumer only handles `KitchenTicketCreated`, `KitchenTicketAccepted`, and `KitchenTicketRejected`. Without events and consumer handlers for the preparation stages, the Order stays stuck at `PREPARING` indefinitely. The frontend treats `PREPARING` as a terminal state and shows "Your order is being prepared" with no ready notification.

This design completes the loop by (a) publishing outbox events from kitchen-service for the `PREPARING` and `READY_FOR_PICKUP` ticket transitions, (b) consuming those events in order-service to drive the Order to a new `READY` terminal state, and (c) updating the frontend to display the ready notification.

## Goals / Non-Goals

**Goals:**
- Publish `KitchenTicketPreparing` and `KitchenTicketReadyForPickup` events from kitchen-service via the transactional outbox
- Consume those events in order-service and transition the Order to `READY`
- Add `READY` as a terminal Order status with a `mark_ready()` domain method
- Update the frontend polling to stop at `READY` with a "ready for pickup" message

**Non-Goals:**
- No new kitchen API endpoints (existing `/prepare` and `/ready-for-pickup` are reused)
- No changes to the Order state machine beyond adding `READY`
- No new outbox infrastructure — reuses existing `OutboxRelay` and `MessagePublisher`
- No delivery-service integration at this stage (that is a future feature)

## Decisions

### Decision 1: `KitchenTicketPreparing` event is fire-and-forget

The `KitchenTicketPreparing` event (routing key `ftgo.KitchenTicket.KitchenTicketPreparing`) is published but the order-service consumer acknowledges it without changing state. The order is already in `PREPARING` from the earlier `KitchenTicketAccepted` handler.

**Rationale**: Keeps the event contract consistent (every ticket transition has a corresponding event) without requiring the Order to have a distinct "kitchen is prepping" state. This also enables future consumers (e.g., a notification service) to react to the preparing event.

**Alternative considered**: Skipping the preparing event entirely. Rejected because it breaks the pattern of one-event-per-transition and prevents future extensibility.

### Decision 2: `READY` is terminal, not `COMPLETED`

The new Order status is `READY`, not `COMPLETED` or `DELIVERED`. Delivery is a separate concern (delivery-service is scaffolded but not implemented).

**Rationale**: `READY` accurately describes the state when kitchen work is done. `COMPLETED`/`DELIVERED` imply a delivery step that doesn't exist yet.

### Decision 3: `mark_ready()` follows the existing transition pattern

```python
def mark_ready(self) -> None:
    if self.status == OrderStatus.READY:
        return
    if self.status != OrderStatus.PREPARING:
        raise InvalidOrderStatusTransitionError(self.status, OrderStatus.READY)
    self.status = OrderStatus.READY
```

Same pattern as `approve()`, `begin_preparing()`, and `cancel()`.

### Decision 4: Consumer handlers follow the existing pattern

Both new handlers use `message.process(requeue=False)` so commit failures cause nack/requeue, while domain errors (missing order, invalid transition) ack to prevent requeue loops. This matches the `handle_kitchen_ticket_accepted` pattern exactly.

## Architecture

```
Kitchen staff clicks "Prepare"
         │
         ▼
POST /kitchen/tickets/{id}/prepare
         │
   start_preparing()
         │
   ticket → PREPARING
   outbox.add(KitchenTicketPreparing)
   commit
         │
   OutboxRelay → RabbitMQ
   routing key: ftgo.KitchenTicket.KitchenTicketPreparing
         │
   order-service consumer
         │
   handle_kitchen_ticket_preparing()
   → order is already PREPARING → ack (no-op)
         │
Kitchen staff clicks "Ready for pickup"
         │
         ▼
POST /kitchen/tickets/{id}/ready-for-pickup
         │
   mark_ready_for_pickup()
         │
   ticket → READY_FOR_PICKUP
   outbox.add(KitchenTicketReadyForPickup)
   commit
         │
   OutboxRelay → RabbitMQ
   routing key: ftgo.KitchenTicket.KitchenTicketReadyForPickup
         │
   order-service consumer
         │
   handle_kitchen_ticket_ready()
   → order.begin_preparing() already done, call mark_ready_order()
   → order → READY  (terminal)
         │
         ▼
   Frontend polling stops
   "Your order is ready for pickup!"
```

## Data Models

### New OrderStatus value

```python
class OrderStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    PREPARING = "PREPARING"
    READY = "READY"  # new terminal state
```

### New outbox event payloads

**KitchenTicketPreparing** (routing key: `ftgo.KitchenTicket.KitchenTicketPreparing`):

```json
{
  "event_type": "KitchenTicketPreparing",
  "aggregate_type": "KitchenTicket",
  "aggregate_id": "<ticket-id>",
  "occurred_at": "<iso8601>",
  "payload": {
    "ticket_id": "<ticket-id>",
    "order_id": "<order-id>",
    "restaurant_id": 1,
    "status": "PREPARING"
  }
}
```

**KitchenTicketReadyForPickup** (routing key: `ftgo.KitchenTicket.KitchenTicketReadyForPickup`):

```json
{
  "event_type": "KitchenTicketReadyForPickup",
  "aggregate_type": "KitchenTicket",
  "aggregate_id": "<ticket-id>",
  "occurred_at": "<iso8601>",
  "payload": {
    "ticket_id": "<ticket-id>",
    "order_id": "<order-id>",
    "restaurant_id": 1,
    "status": "READY_FOR_PICKUP"
  }
}
```

## Files Changed

| File | Change |
|------|--------|
| `kitchen-service/…/application/outbox.py` | Add `kitchen_ticket_preparing_event()` and `kitchen_ticket_ready_for_pickup_event()` builders |
| `kitchen-service/…/application/tickets.py` | Add outbox writes in `start_preparing()` and `mark_ready_for_pickup()` with idempotency guards |
| `order-service/…/domain/models.py` | Add `READY` to `OrderStatus`; add `mark_ready()` method to `Order` |
| `order-service/…/application/lifecycle.py` | Add `mark_ready_order()` method |
| `order-service/…/consumer.py` | Add `handle_kitchen_ticket_preparing()` and `handle_kitchen_ticket_ready()` handlers; bind two new queues |
| `order-service/migrations/versions/0006_add_ready_to_order_status.py` | New Alembic migration |
| `frontend/src/hooks/useOrderPolling.js` | Add `READY` to terminal statuses |
| `frontend/src/pages/OrderStatusPage.jsx` | Show "Your order is ready for pickup!" for `READY` |
| `frontend/src/components/StatusBadge.jsx` | Add `READY` colour mapping |
| `docs/contracts/events.md` | Document two new events |

## Error Handling

### Consumer handlers

| Condition | Action |
|-----------|--------|
| `order_id` missing or invalid UUID | Log ERROR, ack message |
| Order not found | Log WARNING, ack message |
| `InvalidOrderStatusTransitionError` raised | Log ERROR, ack message |
| DB commit failure | Exception escapes `message.process(requeue=False)` → nack + requeue |

## Correctness Properties

### Property 1: start_preparing writes exactly one outbox event
*For any* `KitchenTicket` in `ACCEPTED` status, calling `start_preparing()` must produce exactly one `KitchenTicketPreparing` outbox event and transition status to `PREPARING`.

### Property 2: start_preparing is idempotent (no duplicate outbox)
*For any* `KitchenTicket` already in `PREPARING` status, calling `start_preparing()` must not add any new entry to the outbox.

### Property 3: mark_ready_for_pickup writes exactly one outbox event
*For any* `KitchenTicket` in `PREPARING` status, calling `mark_ready_for_pickup()` must produce exactly one `KitchenTicketReadyForPickup` outbox event and transition status to `READY_FOR_PICKUP`.

### Property 4: mark_ready_for_pickup is idempotent
*For any* `KitchenTicket` already in `READY_FOR_PICKUP` status, calling `mark_ready_for_pickup()` must not add any new entry to the outbox.

### Property 5: Order mark_ready state machine correctness
*For any* `Order` in `PREPARING` status, `mark_ready()` must transition to `READY`; for `READY` it must be a no-op; for any other status it must raise `InvalidOrderStatusTransitionError`.

### Property 6: READY is terminal for polling
The frontend polling hook must include `READY` in its terminal statuses set alongside `PREPARING` and `CANCELLED`.
