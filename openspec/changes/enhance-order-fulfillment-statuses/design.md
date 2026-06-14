## Context

The current place-order flow is implemented through `READY`: `order-service` creates the order, `kitchen-service` creates and advances a kitchen ticket, and `order-service` marks the order `READY` when the ticket reaches `READY_FOR_PICKUP`. The delivery-service is currently a scaffold, so the customer-facing order lifecycle stops before delivery assignment, pickup, and final delivery.

This change extends the same DDD and transactional outbox pattern already used by `order-service` and `kitchen-service`. `delivery-service` owns delivery state and publishes delivery events. `order-service` remains the single owner of order rows and decides which delivery events produce valid order status transitions.

## Goals / Non-Goals

**Goals:**

- Implement a delivery aggregate and service flow in `delivery-service`.
- Create an idempotent delivery when a ready kitchen ticket event is received.
- Publish delivery lifecycle events through the delivery transactional outbox.
- Extend the order state machine with `DELIVERY_ASSIGNED`, `OUT_FOR_DELIVERY`, and `DELIVERED`.
- Update API gateway, frontend status display, e2e tests, use-case docs, and event contracts.

**Non-Goals:**

- No courier matching, routing optimization, ETA calculation, payment settlement, or accounting integration.
- No multi-stop courier route model.
- No real-time push notifications; frontend continues to poll.
- No domain logic added to `libs/common/`.

## Decisions

### Decision 1: delivery-service owns delivery state

`delivery-service` will add its own `Delivery` aggregate, repository port, unit of work, SQLAlchemy models, migrations, API routes, consumer, and outbox relay. This mirrors the existing service layering:

- `domain`: `Delivery`, `DeliveryStatus`, transition rules.
- `application`: command methods and outbox event builders.
- `api`: delivery endpoints for local operations.
- `infrastructure`: SQLAlchemy persistence and messaging.

Alternative considered: store delivery status directly on `Order`. Rejected because delivery assignment and pickup are a separate business capability, and the repository already has a delivery-service scaffold.

### Decision 2: READY is the handoff state, DELIVERED is terminal

`READY` remains the state produced by kitchen readiness. It is no longer the final customer fulfillment state for delivery orders. Delivery events move the order through:

```text
READY -> DELIVERY_ASSIGNED -> OUT_FOR_DELIVERY -> DELIVERED
```

`DELIVERED` is terminal. Duplicate calls to each transition are idempotent when the order is already in the target state.

Alternative considered: rename `READY` to `READY_FOR_DELIVERY`. Rejected because `READY` already exists in code, migrations, contracts, and frontend behavior.

### Decision 3: DeliveryCreated does not change order status

When `delivery-service` consumes `KitchenTicketReadyForPickup`, it creates a delivery and publishes `DeliveryCreated`. `order-service` may consume and log that event, but the order remains `READY` until a courier is assigned.

Alternative considered: add a `DELIVERY_PENDING` order status. Rejected for this slice because `READY` already communicates that the order is waiting for fulfillment handoff, and adding another passive waiting state would make the first delivery increment larger without improving user-visible behavior.

### Decision 4: delivery APIs are operator-oriented test controls

The first delivery APIs are intentionally simple:

- `GET /deliveries`
- `GET /deliveries/{delivery_id}`
- `POST /deliveries/{delivery_id}/assign`
- `POST /deliveries/{delivery_id}/pickup`
- `POST /deliveries/{delivery_id}/deliver`

They enable local demos and e2e tests without modeling courier accounts yet. The assign endpoint accepts a string `courier_id` so a later courier-service can replace it without changing the order lifecycle events.

### Decision 5: use explicit delivery events

Delivery event payloads include both `delivery_id` and `order_id` so order-service can idempotently update by order id while other consumers can deduplicate by delivery id.

**DeliveryCreated**

```json
{
  "event_type": "DeliveryCreated",
  "aggregate_type": "Delivery",
  "aggregate_id": "<delivery-id>",
  "payload": {
    "delivery_id": "<delivery-id>",
    "order_id": "<order-id>",
    "restaurant_id": 1,
    "delivery_address": "123 Main St, Shanghai, 200000",
    "status": "PENDING_ASSIGNMENT"
  },
  "occurred_at": "2026-06-13T12:00:00+00:00"
}
```

**DeliveryAssigned**

```json
{
  "event_type": "DeliveryAssigned",
  "aggregate_type": "Delivery",
  "aggregate_id": "<delivery-id>",
  "payload": {
    "delivery_id": "<delivery-id>",
    "order_id": "<order-id>",
    "courier_id": "courier-001",
    "status": "ASSIGNED"
  },
  "occurred_at": "2026-06-13T12:05:00+00:00"
}
```

**DeliveryPickedUp**

```json
{
  "event_type": "DeliveryPickedUp",
  "aggregate_type": "Delivery",
  "aggregate_id": "<delivery-id>",
  "payload": {
    "delivery_id": "<delivery-id>",
    "order_id": "<order-id>",
    "courier_id": "courier-001",
    "status": "PICKED_UP"
  },
  "occurred_at": "2026-06-13T12:20:00+00:00"
}
```

**DeliveryDelivered**

```json
{
  "event_type": "DeliveryDelivered",
  "aggregate_type": "Delivery",
  "aggregate_id": "<delivery-id>",
  "payload": {
    "delivery_id": "<delivery-id>",
    "order_id": "<order-id>",
    "courier_id": "courier-001",
    "status": "DELIVERED"
  },
  "occurred_at": "2026-06-13T12:35:00+00:00"
}
```

## Service Design

### delivery-service

`DeliveryStatus` values:

- `PENDING_ASSIGNMENT`
- `ASSIGNED`
- `PICKED_UP`
- `DELIVERED`
- `CANCELLED`

Valid transitions:

- create from ready order -> `PENDING_ASSIGNMENT`
- assign courier -> `ASSIGNED`
- pickup -> `PICKED_UP`
- deliver -> `DELIVERED`

`Delivery` stores `id`, `order_id`, `restaurant_id`, `delivery_address`, `status`, optional `courier_id`, and timestamps. The repository enforces uniqueness by `order_id` so redelivered `KitchenTicketReadyForPickup` messages return the existing delivery without duplicate outbox events.

`KitchenTicketReadyForPickup` must include `delivery_address`. The address is copied from the original `OrderCreated` event into the kitchen ticket snapshot when the ticket is created, then republished on the ready-for-pickup event. This keeps delivery creation event-driven and avoids a synchronous delivery-service call back into order-service.

### order-service

Add status values:

- `DELIVERY_ASSIGNED`
- `OUT_FOR_DELIVERY`
- `DELIVERED`

Add domain methods:

- `mark_delivery_assigned()`: `READY -> DELIVERY_ASSIGNED`
- `mark_out_for_delivery()`: `DELIVERY_ASSIGNED -> OUT_FOR_DELIVERY`
- `mark_delivered()`: `OUT_FOR_DELIVERY -> DELIVERED`

Application service methods follow `mark_ready_order()`: load by id, call the domain transition, save, commit, return saved order or `None`.

### api-gateway and frontend

The gateway forwards `/deliveries` routes to delivery-service. The frontend adds delivery labels and progress copy for `DELIVERY_ASSIGNED`, `OUT_FOR_DELIVERY`, and `DELIVERED`, and stops polling only when an order reaches `DELIVERED`, `CANCELLED`, or `REJECTED`.

## Error Handling

### Delivery API routes

| Condition | Response |
| --- | --- |
| Delivery id not found | `404 Not Found` |
| Invalid delivery transition | `409 Conflict` with current and target statuses |
| Missing or blank courier id on assign | `422 Unprocessable Entity` |
| Valid idempotent repeat | `200 OK` with current delivery |

### delivery-service consumer

| Condition | Action |
| --- | --- |
| Missing or invalid `order_id` | Log `ERROR`, ack message |
| Missing required payload fields | Log `ERROR`, ack message |
| Existing delivery for order | Return existing delivery, ack message, no duplicate outbox |
| Database commit failure | Let exception escape message context so message is retried |

### order-service delivery event consumers

| Condition | Action |
| --- | --- |
| Missing or invalid `order_id` | Log `ERROR`, ack message |
| Order not found | Log `WARNING`, ack message |
| Invalid transition | Log `ERROR`, ack message |
| Database commit failure | Let exception escape message context so message is retried |

## Correctness Properties

1. Creating a delivery from a ready ticket is idempotent by `order_id` and writes at most one `DeliveryCreated` outbox event.
2. Assigning a delivery writes exactly one `DeliveryAssigned` event when transitioning from `PENDING_ASSIGNMENT` to `ASSIGNED`, and writes no duplicate event for repeated assignment with the same courier.
3. Pickup writes exactly one `DeliveryPickedUp` event when transitioning from `ASSIGNED` to `PICKED_UP`.
4. Delivery completion writes exactly one `DeliveryDelivered` event when transitioning from `PICKED_UP` to `DELIVERED`.
5. Order transition methods reject out-of-order delivery events and are idempotent for duplicate target-state events.
6. The e2e flow can create an order, advance kitchen to ready, create a delivery, assign it, pick it up, deliver it, and observe final order status `DELIVERED`.

## Risks / Trade-offs

- Delivery events can arrive before order-service has marked the order `READY` -> consumers log invalid transitions and ack, which may drop a legitimate event. Mitigation: bind delivery creation to `KitchenTicketReadyForPickup`, which is also what drives `READY`, and keep e2e tests exercising event order. A future inbox/retry table can make this fully robust.
- Delivery assignment uses a free-form `courier_id` -> enough for learning and tests, but not a real courier domain. Mitigation: document courier-service as out of scope.
- PostgreSQL enum additions are not easily reversible -> migrations should follow the existing enum migration pattern with no destructive downgrade.
- Frontend currently has duplicated polling logic -> update both the hook and status page in this change, then consider consolidation separately if it becomes noisy.

## Migration Plan

1. Add delivery-service tables and outbox table migration.
2. Add order-service enum migration for new order statuses.
3. Deploy consumers after migrations so new events have target tables and enum values available.
4. Update API gateway and frontend after backend routes are available.
5. Rollback strategy: stop delivery-service consumers/relays and frontend delivery UI first. Existing orders can still stop at `READY`; enum values remain in the database.

## Open Questions

- Should a future courier-service own courier availability and assignment? This change keeps assignment manual.
- Should delivery cancellation be surfaced to order-service as a new final status? This change only models the happy-path delivery completion plus existing order cancellation.
