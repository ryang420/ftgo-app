## Why

The order lifecycle is incomplete. After a kitchen ticket is accepted and the order transitions to `PREPARING`, the chain breaks. Kitchen staff can call `/prepare` and `/ready-for-pickup` on tickets but no domain events are published and no order transitions occur. The frontend polls forever at `PREPARING` with no "ready" state. Consumers never learn when their food is ready. This completes the final leg of the order journey.

## What Changes

- **kitchen-service**: Publish `KitchenTicketPreparing` and `KitchenTicketReadyForPickup` outbox events when tickets transition through the preparation stages
- **order-service**: Consume those events and drive the `Order` state machine to a new `READY` terminal state
- **Order domain**: Add `READY` status and `mark_ready()` transition; `READY` is terminal (no further transitions)
- **Event contracts**: Document two new events with routing keys, payload shapes, and idempotency keys
- **Alembic migration**: Add `READY` to the `order_status` PostgreSQL enum
- **Frontend**: Extend polling to treat `READY` as terminal with a "Your order is ready for pickup!" message

## Capabilities

### New Capabilities
- `order-ready-notification`: The kitchen-service SHALL publish events when a ticket enters preparation and when it is ready for pickup. The order-service SHALL consume those events and transition the Order to a READY terminal state. The frontend SHALL display a "ready for pickup" notification.

### Modified Capabilities
- `kitchen-ticket-acceptance`: Extending the existing kitchen decision flow to include the full preparation pipeline. The `start_preparing()` and `mark_ready_for_pickup()` application service methods SHALL write outbox events (currently missing). Order consumer SHALL bind two new routing keys and handle the corresponding events.

## Impact

| Layer | Impact |
|-------|--------|
| **kitchen-service** | `application/outbox.py` — two new event builders. `application/tickets.py` — outbox writes in `start_preparing()` and `mark_ready_for_pickup()`. No API changes. |
| **order-service** | `domain/models.py` — new `READY` status + `mark_ready()` transition. `application/lifecycle.py` — new `mark_ready_order()` method. `consumer.py` — two new handlers + two new queue bindings. `migrations/` — new Alembic migration. |
| **docs** | `docs/contracts/events.md` — two new event contract entries |
| **frontend** | `hooks/useOrderPolling.js` — add `READY` to terminal statuses. `pages/OrderStatusPage.jsx` — show "ready" message. |
| **libs/common/** | No changes |
