## Why

The current place-order journey reaches `READY` after kitchen preparation, but it does not model the delivery handoff or final customer fulfillment states such as delivery in progress and delivered. This leaves the FTGO flow short of the end-to-end lifecycle implied by the delivery-service scaffold and makes order status polling stop before the customer receives the order.

## What Changes

- Add delivery fulfillment after kitchen readiness:
  - `order-service` SHALL support `READY`, `DELIVERY_ASSIGNED`, `OUT_FOR_DELIVERY`, and `DELIVERED` as the post-kitchen fulfillment path.
  - `delivery-service` SHALL own delivery aggregate state and publish delivery lifecycle events through the transactional outbox.
  - `delivery-service` SHALL consume `KitchenTicketReadyForPickup` to create an idempotent delivery for the order.
  - `order-service` SHALL consume delivery events and drive the order state machine.
- Add initial delivery APIs for local learning and tests:
  - list/get deliveries
  - assign courier
  - mark picked up / out for delivery
  - mark delivered
- Add event contracts:
  - `DeliveryCreated`, routing key `ftgo.Delivery.DeliveryCreated`, idempotency key `payload.order_id`
  - `DeliveryAssigned`, routing key `ftgo.Delivery.DeliveryAssigned`, idempotency key `payload.delivery_id`
  - `DeliveryPickedUp`, routing key `ftgo.Delivery.DeliveryPickedUp`, idempotency key `payload.delivery_id`
  - `DeliveryDelivered`, routing key `ftgo.Delivery.DeliveryDelivered`, idempotency key `payload.delivery_id`
- Update `docs/use-cases/place-order.md` so the documented flow matches the implemented lifecycle beyond kitchen readiness.
- Update frontend polling/status display so `DELIVERED` is terminal and intermediate delivery states remain visible.

### Cross-Service Flow

```mermaid
sequenceDiagram
    autonumber
    participant KitchenRelay as kitchen outbox relay
    participant RabbitMQ
    participant DeliveryConsumer as delivery KitchenTicketReadyForPickup consumer
    participant Delivery as delivery-service
    participant DeliveryDB as delivery_db
    participant DeliveryRelay as delivery outbox relay
    participant OrderConsumer as order delivery event consumer
    participant Order as order-service
    participant OrderDB as order_db

    KitchenRelay->>RabbitMQ: Publish ftgo.KitchenTicket.KitchenTicketReadyForPickup
    RabbitMQ-->>DeliveryConsumer: Deliver KitchenTicketReadyForPickup
    DeliveryConsumer->>Delivery: create_delivery_for_ready_order(order_id)
    Delivery->>DeliveryDB: Insert delivery + DeliveryCreated outbox message
    DeliveryDB-->>Delivery: Commit
    DeliveryConsumer-->>RabbitMQ: Ack message

    DeliveryRelay->>RabbitMQ: Publish ftgo.Delivery.DeliveryCreated
    RabbitMQ-->>OrderConsumer: Deliver DeliveryCreated
    OrderConsumer->>Order: confirm_delivery_requested(order_id)
    Order->>OrderDB: Keep order READY; record lifecycle event/log only if needed
    OrderConsumer-->>RabbitMQ: Ack message

    Delivery->>DeliveryDB: assign courier + DeliveryAssigned outbox message
    DeliveryRelay->>RabbitMQ: Publish ftgo.Delivery.DeliveryAssigned
    RabbitMQ-->>OrderConsumer: Deliver DeliveryAssigned
    OrderConsumer->>Order: mark_delivery_assigned(order_id)
    Order->>OrderDB: Update order status to DELIVERY_ASSIGNED

    Delivery->>DeliveryDB: mark picked up + DeliveryPickedUp outbox message
    DeliveryRelay->>RabbitMQ: Publish ftgo.Delivery.DeliveryPickedUp
    RabbitMQ-->>OrderConsumer: Deliver DeliveryPickedUp
    OrderConsumer->>Order: mark_out_for_delivery(order_id)
    Order->>OrderDB: Update order status to OUT_FOR_DELIVERY

    Delivery->>DeliveryDB: mark delivered + DeliveryDelivered outbox message
    DeliveryRelay->>RabbitMQ: Publish ftgo.Delivery.DeliveryDelivered
    RabbitMQ-->>OrderConsumer: Deliver DeliveryDelivered
    OrderConsumer->>Order: mark_delivered(order_id)
    Order->>OrderDB: Update order status to DELIVERED
```

## Capabilities

### New Capabilities

- `order-delivery-fulfillment`: Delivery-service creates and advances delivery records from ready kitchen tickets, publishes delivery events, and order-service reflects delivery progress through final `DELIVERED` status.

### Modified Capabilities

- `order-ready-notification`: `READY` is no longer the final customer fulfillment state when delivery fulfillment is enabled; it becomes the handoff point from kitchen readiness to delivery creation, while `DELIVERED` becomes the terminal status for delivery orders.

## Impact

- **delivery-service**: Add DDD layers mirroring `order-service`/`kitchen-service`: domain delivery model, repository/UnitOfWork ports, SQLAlchemy models/migrations, application service, API routes, RabbitMQ consumer, outbox relay, and tests.
- **order-service**: Extend `OrderStatus`, domain transitions, lifecycle application service, database enum migration, schemas, and RabbitMQ consumer bindings for delivery lifecycle events.
- **api-gateway**: Proxy delivery API routes for local end-to-end use.
- **frontend**: Display delivery progress states and stop polling only at final states (`DELIVERED`, `CANCELLED`, `REJECTED`).
- **docs**: Update `docs/use-cases/place-order.md` and `docs/contracts/events.md` with delivery lifecycle behavior and event contracts.
- **tests**: Add focused domain/application tests for delivery-service, order-service transition tests, and e2e coverage from place order through delivered.
- **libs/common/**: No domain changes; reuse existing shared technical outbox, messaging, DB, and API utilities.
