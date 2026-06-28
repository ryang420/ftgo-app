## MODIFIED Requirements

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

### Requirement: Frontend displays order ready state
The frontend SHALL recognize `READY` as an active handoff order status and display a "Your order is ready for delivery handoff" message while polling continues for delivery orders.

#### Scenario: Polling continues at ready
- **WHEN** `GET /orders/:orderId` returns status `READY`
- **THEN** the frontend displays a ready handoff message
- **AND** continues polling for subsequent delivery statuses

#### Scenario: Ready status badge
- **WHEN** an order status is `READY`
- **THEN** the `StatusBadge` renders the status with a green colour variant
