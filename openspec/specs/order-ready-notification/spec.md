## ADDED Requirements

### Requirement: Order ready terminal state
The Order domain model SHALL support a `READY` status as the kitchen-complete handoff state reachable from `PREPARING` via `mark_ready()`, with idempotency on repeat calls.

#### Scenario: Mark ready from preparing
- **WHEN** `mark_ready()` is called on an `Order` in status `PREPARING`
- **THEN** the order transitions to `READY`

#### Scenario: Mark ready is idempotent
- **WHEN** `mark_ready()` is called on an `Order` already in status `READY`
- **THEN** the method returns without error and the order status remains `READY`

#### Scenario: Ready can advance into delivery
- **WHEN** a valid delivery lifecycle event is received for an order in status `READY`
- **THEN** the order SHALL advance according to the delivery fulfillment state machine

#### Scenario: Mark ready raises on invalid status
- **WHEN** `mark_ready()` is called on an `Order` whose status is not `PREPARING` or `READY`
- **THEN** `InvalidOrderStatusTransitionError` is raised with the current and target statuses

### Requirement: Kitchen preparing event published
Kitchen service SHALL write a `KitchenTicketPreparing` outbox event when `start_preparing()` successfully transitions a ticket.

#### Scenario: Preparing event written atomically
- **WHEN** `start_preparing()` transitions a ticket to `PREPARING`
- **THEN** a `KitchenTicketPreparing` outbox event is written in the same transaction
- **AND** the event payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`

#### Scenario: Preparing event is idempotent
- **WHEN** `start_preparing()` is called on a ticket already `PREPARING`
- **THEN** no outbox event is written

### Requirement: Kitchen ready-for-pickup event published
Kitchen service SHALL write a `KitchenTicketReadyForPickup` outbox event when `mark_ready_for_pickup()` successfully transitions a ticket.

#### Scenario: Ready event written atomically
- **WHEN** `mark_ready_for_pickup()` transitions a ticket to `READY_FOR_PICKUP`
- **THEN** a `KitchenTicketReadyForPickup` outbox event is written in the same transaction
- **AND** the event payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`

#### Scenario: Ready event is idempotent
- **WHEN** `mark_ready_for_pickup()` is called on a ticket already `READY_FOR_PICKUP`
- **THEN** no outbox event is written

### Requirement: Order consumer handles preparation events
Order service SHALL consume `KitchenTicketPreparing` and `KitchenTicketReadyForPickup` events and call `mark_ready_order()` on the appropriate application service.

#### Scenario: Kitchen preparing event consumed
- **WHEN** `KitchenTicketPreparing` is received with a valid `order_id`
- **THEN** the order consumer acknowledges the message without changing order state (order already in `PREPARING`)

#### Scenario: Kitchen ready event consumed
- **WHEN** `KitchenTicketReadyForPickup` is received with a valid `order_id`
- **THEN** the order consumer calls `mark_ready_order()` and the order transitions to `READY`

#### Scenario: Malformed event acknowledged
- **WHEN** a kitchen preparation event is received with a missing or invalid `order_id`
- **THEN** the consumer logs the error at `ERROR` level and acknowledges the message to prevent requeue loops

### Requirement: Frontend displays order ready state
The frontend SHALL recognize `READY` as an active handoff order status and display a "Your order is ready for delivery handoff" message while polling continues for delivery orders.

#### Scenario: Polling continues at ready
- **WHEN** `GET /orders/:orderId` returns status `READY`
- **THEN** the frontend displays a ready handoff message
- **AND** continues polling for subsequent delivery statuses

#### Scenario: Ready status badge
- **WHEN** an order status is `READY`
- **THEN** the `StatusBadge` renders the status with a green colour variant

### Requirement: Event contracts documented
The event contracts for `KitchenTicketPreparing` and `KitchenTicketReadyForPickup` SHALL be documented.

#### Scenario: Contracts in place
- **WHEN** the events are implemented
- **THEN** each event is documented with exchange name, routing key, delivery guarantee, idempotency key, and a JSON envelope example
