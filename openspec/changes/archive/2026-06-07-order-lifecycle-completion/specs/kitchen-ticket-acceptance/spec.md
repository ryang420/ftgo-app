## MODIFIED Requirements

### Requirement: Publish kitchen ticket decision events
Kitchen service SHALL publish accepted, rejected, preparing, and ready-for-pickup ticket events through the transactional outbox using the `ftgo.events` exchange.

#### Scenario: Publish accepted event
- **WHEN** an unpublished `KitchenTicketAccepted` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.KitchenTicket.KitchenTicketAccepted`
- **AND** the payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`

#### Scenario: Publish rejected event
- **WHEN** an unpublished `KitchenTicketRejected` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.KitchenTicket.KitchenTicketRejected`
- **AND** the payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`
- **AND** `rejection_reason` is omitted when no reason is provided

#### Scenario: Publish preparing event
- **WHEN** a `KitchenTicket` transitions to `PREPARING` and the outbox entry is relayed
- **THEN** it is published with routing key `ftgo.KitchenTicket.KitchenTicketPreparing`
- **AND** the payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`

#### Scenario: Publish ready-for-pickup event
- **WHEN** a `KitchenTicket` transitions to `READY_FOR_PICKUP` and the outbox entry is relayed
- **THEN** it is published with routing key `ftgo.KitchenTicket.KitchenTicketReadyForPickup`
- **AND** the payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`

### Requirement: Order reacts to kitchen ticket decisions
Order service SHALL consume kitchen ticket accepted, rejected, preparing, and ready-for-pickup events and drive the order state machine.

#### Scenario: Accepted ticket begins preparing
- **WHEN** `KitchenTicketAccepted` is received for an order in status `APPROVED`
- **THEN** order service transitions the order to `PREPARING` and acknowledges the message

#### Scenario: Rejected ticket cancels order
- **WHEN** `KitchenTicketRejected` is received for an order in status `PENDING`, `APPROVED`, or `PREPARING`
- **THEN** order service transitions the order to `CANCELLED` and acknowledges the message

#### Scenario: Preparing ticket keeps order in progress
- **WHEN** `KitchenTicketPreparing` is received for an order in status `PREPARING`
- **THEN** order service acknowledges the message without changing order state

#### Scenario: Ready ticket marks order ready
- **WHEN** `KitchenTicketReadyForPickup` is received for an order in status `PREPARING`
- **THEN** order service transitions the order to `READY` and acknowledges the message

#### Scenario: Duplicate decision event
- **WHEN** a kitchen decision event is redelivered for an order already in the target status
- **THEN** order service treats the event as a duplicate and acknowledges it without changing state

### Requirement: Document kitchen decision contracts
The event contracts for `KitchenTicketAccepted`, `KitchenTicketRejected`, `KitchenTicketPreparing`, and `KitchenTicketReadyForPickup` SHALL be documented under `docs/contracts/`.

#### Scenario: Contracts updated
- **WHEN** the kitchen decision events are implemented
- **THEN** the event contract documentation includes exchange, routing key, delivery guarantee, idempotency key, and JSON envelope examples
