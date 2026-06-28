## ADDED Requirements

### Requirement: Delivery aggregate lifecycle
Delivery-service SHALL model deliveries as a domain aggregate with explicit status transitions and idempotent repeats.

#### Scenario: Create pending delivery
- **WHEN** delivery-service creates a delivery for a ready order
- **THEN** the delivery status is `PENDING_ASSIGNMENT`
- **AND** the delivery records `order_id`, `restaurant_id`, and `delivery_address`

#### Scenario: Assign delivery
- **WHEN** a courier is assigned to a delivery in status `PENDING_ASSIGNMENT`
- **THEN** the delivery status transitions to `ASSIGNED`
- **AND** the delivery records the `courier_id`

#### Scenario: Pickup delivery
- **WHEN** a delivery in status `ASSIGNED` is marked picked up
- **THEN** the delivery status transitions to `PICKED_UP`

#### Scenario: Complete delivery
- **WHEN** a delivery in status `PICKED_UP` is marked delivered
- **THEN** the delivery status transitions to `DELIVERED`

#### Scenario: Invalid delivery transition
- **WHEN** delivery-service is asked to perform an unsupported delivery status transition
- **THEN** it raises an invalid transition error containing the current and target statuses

### Requirement: Delivery created from ready kitchen ticket
Delivery-service SHALL consume `KitchenTicketReadyForPickup` and create one delivery per order.

#### Scenario: Ready ticket event carries delivery address
- **WHEN** kitchen-service publishes `KitchenTicketReadyForPickup`
- **THEN** the event payload includes `delivery_address` from the original order

#### Scenario: Ready ticket creates delivery
- **WHEN** delivery-service receives `KitchenTicketReadyForPickup` with a valid payload for an order that has no delivery
- **THEN** delivery-service creates a delivery in status `PENDING_ASSIGNMENT`
- **AND** writes a `DeliveryCreated` outbox event in the same transaction
- **AND** acknowledges the message

#### Scenario: Ready ticket is idempotent
- **WHEN** delivery-service receives a duplicate `KitchenTicketReadyForPickup` for an order that already has a delivery
- **THEN** delivery-service returns the existing delivery
- **AND** does not write a duplicate `DeliveryCreated` outbox event
- **AND** acknowledges the message

#### Scenario: Malformed ready ticket event acknowledged
- **WHEN** delivery-service receives `KitchenTicketReadyForPickup` with a missing or invalid `order_id`
- **THEN** delivery-service logs the error
- **AND** acknowledges the message to prevent a requeue loop

### Requirement: Delivery API operations
Delivery-service SHALL expose API operations for reading deliveries and advancing the delivery lifecycle.

#### Scenario: List deliveries
- **WHEN** `GET /deliveries` is called
- **THEN** delivery-service returns delivery summaries

#### Scenario: Get delivery
- **WHEN** `GET /deliveries/{delivery_id}` is called for an existing delivery
- **THEN** delivery-service returns the delivery representation

#### Scenario: Assign courier
- **WHEN** `POST /deliveries/{delivery_id}/assign` is called with a courier id for a delivery in status `PENDING_ASSIGNMENT`
- **THEN** delivery-service persists status `ASSIGNED`
- **AND** writes a `DeliveryAssigned` outbox event in the same transaction
- **AND** returns the delivery representation

#### Scenario: Mark picked up
- **WHEN** `POST /deliveries/{delivery_id}/pickup` is called for a delivery in status `ASSIGNED`
- **THEN** delivery-service persists status `PICKED_UP`
- **AND** writes a `DeliveryPickedUp` outbox event in the same transaction
- **AND** returns the delivery representation

#### Scenario: Mark delivered
- **WHEN** `POST /deliveries/{delivery_id}/deliver` is called for a delivery in status `PICKED_UP`
- **THEN** delivery-service persists status `DELIVERED`
- **AND** writes a `DeliveryDelivered` outbox event in the same transaction
- **AND** returns the delivery representation

#### Scenario: Invalid API transition
- **WHEN** a delivery lifecycle API is called for a delivery whose status cannot transition to the target status
- **THEN** delivery-service returns `409 Conflict`
- **AND** the response identifies the current and target statuses

### Requirement: Publish delivery lifecycle events
Delivery-service SHALL publish delivery lifecycle events through the transactional outbox using the `ftgo.events` exchange.

#### Scenario: Publish delivery created
- **WHEN** an unpublished `DeliveryCreated` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.Delivery.DeliveryCreated`
- **AND** the payload includes `delivery_id`, `order_id`, `restaurant_id`, `delivery_address`, and `status`

#### Scenario: Publish delivery assigned
- **WHEN** an unpublished `DeliveryAssigned` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.Delivery.DeliveryAssigned`
- **AND** the payload includes `delivery_id`, `order_id`, `courier_id`, and `status`

#### Scenario: Publish delivery picked up
- **WHEN** an unpublished `DeliveryPickedUp` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.Delivery.DeliveryPickedUp`
- **AND** the payload includes `delivery_id`, `order_id`, `courier_id`, and `status`

#### Scenario: Publish delivery delivered
- **WHEN** an unpublished `DeliveryDelivered` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.Delivery.DeliveryDelivered`
- **AND** the payload includes `delivery_id`, `order_id`, `courier_id`, and `status`

### Requirement: Order reacts to delivery events
Order-service SHALL consume delivery lifecycle events and drive the order state machine.

#### Scenario: Delivery created leaves order ready
- **WHEN** `DeliveryCreated` is received for an order in status `READY`
- **THEN** order-service acknowledges the message
- **AND** the order remains in status `READY`

#### Scenario: Delivery assigned updates order
- **WHEN** `DeliveryAssigned` is received for an order in status `READY`
- **THEN** order-service transitions the order to `DELIVERY_ASSIGNED`
- **AND** acknowledges the message

#### Scenario: Delivery picked up updates order
- **WHEN** `DeliveryPickedUp` is received for an order in status `DELIVERY_ASSIGNED`
- **THEN** order-service transitions the order to `OUT_FOR_DELIVERY`
- **AND** acknowledges the message

#### Scenario: Delivery delivered completes order
- **WHEN** `DeliveryDelivered` is received for an order in status `OUT_FOR_DELIVERY`
- **THEN** order-service transitions the order to `DELIVERED`
- **AND** acknowledges the message

#### Scenario: Duplicate delivery event
- **WHEN** a delivery event is redelivered for an order already in the target status
- **THEN** order-service treats the event as a duplicate
- **AND** acknowledges it without changing state

#### Scenario: Malformed delivery event acknowledged
- **WHEN** a delivery event is received with a missing or invalid `order_id`
- **THEN** order-service logs the error
- **AND** acknowledges the message to prevent a requeue loop

### Requirement: Frontend displays delivery progress
The frontend SHALL display delivery progress states and treat delivered orders as terminal.

#### Scenario: Delivery assigned status displayed
- **WHEN** `GET /orders/{order_id}` returns status `DELIVERY_ASSIGNED`
- **THEN** the frontend displays that a courier has been assigned
- **AND** continues polling

#### Scenario: Out for delivery status displayed
- **WHEN** `GET /orders/{order_id}` returns status `OUT_FOR_DELIVERY`
- **THEN** the frontend displays that the order is on the way
- **AND** continues polling

#### Scenario: Delivered status displayed
- **WHEN** `GET /orders/{order_id}` returns status `DELIVERED`
- **THEN** the frontend displays that the order has been delivered
- **AND** stops polling

### Requirement: Delivery contracts documented
Delivery lifecycle event contracts SHALL be documented under `docs/contracts/`.

#### Scenario: Delivery event contracts in place
- **WHEN** delivery lifecycle events are implemented
- **THEN** `DeliveryCreated`, `DeliveryAssigned`, `DeliveryPickedUp`, and `DeliveryDelivered` are documented with exchange, routing key, delivery guarantee, idempotency key, and JSON envelope examples

### Requirement: Place-order use case reaches delivered
The documented place-order use case SHALL include the delivery lifecycle after kitchen readiness.

#### Scenario: Place order documentation includes delivery
- **WHEN** the place-order use case is reviewed
- **THEN** it describes the flow from `READY` through delivery creation, assignment, pickup, and final `DELIVERED` status

#### Scenario: End-to-end test reaches delivered
- **WHEN** the local stack processes a valid order through kitchen readiness and delivery operations
- **THEN** the e2e test observes the order status become `DELIVERED`
