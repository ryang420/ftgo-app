## ADDED Requirements

### Requirement: Accept kitchen tickets
Kitchen staff SHALL be able to accept a `CREATE_PENDING` kitchen ticket through the kitchen API, persist the accepted status, and write a `KitchenTicketAccepted` outbox event in the same transaction.

#### Scenario: Accept pending ticket
- **WHEN** `POST /kitchen/tickets/{ticket_id}/accept` is called for an existing ticket with status `CREATE_PENDING`
- **THEN** the ticket status is persisted as `ACCEPTED`
- **AND** exactly one `KitchenTicketAccepted` event is written to the outbox
- **AND** the API returns `200` with the current ticket representation

#### Scenario: Accept is idempotent
- **WHEN** `POST /kitchen/tickets/{ticket_id}/accept` is called for an existing ticket with status `ACCEPTED`
- **THEN** the API returns `200`
- **AND** no duplicate outbox event is written

#### Scenario: Accept invalid status
- **WHEN** accepting a ticket whose status is neither `CREATE_PENDING` nor `ACCEPTED`
- **THEN** the API returns `409` with the current status and attempted target status

### Requirement: Reject kitchen tickets
Kitchen staff SHALL be able to reject a `CREATE_PENDING` kitchen ticket through the kitchen API, persist the cancelled status, and write a `KitchenTicketRejected` outbox event in the same transaction.

#### Scenario: Reject pending ticket
- **WHEN** `POST /kitchen/tickets/{ticket_id}/reject` is called for an existing ticket with status `CREATE_PENDING`
- **THEN** the ticket status is persisted as `CANCELLED`
- **AND** exactly one `KitchenTicketRejected` event is written to the outbox
- **AND** the API returns `200` with the current ticket representation

#### Scenario: Reject is idempotent
- **WHEN** `POST /kitchen/tickets/{ticket_id}/reject` is called for an existing ticket with status `CANCELLED`
- **THEN** the API returns `200`
- **AND** no duplicate outbox event is written

#### Scenario: Reject invalid status
- **WHEN** rejecting a ticket whose status is neither `CREATE_PENDING` nor `CANCELLED`
- **THEN** the API returns `409` with the current status and attempted target status

### Requirement: Kitchen ticket state machine
The kitchen ticket domain model SHALL enforce valid status transitions and idempotent repeats.

#### Scenario: Valid kitchen ticket transitions
- **WHEN** the domain is asked to perform `CREATE_PENDING -> ACCEPTED`, `CREATE_PENDING -> CANCELLED`, `ACCEPTED -> PREPARING`, or `PREPARING -> READY_FOR_PICKUP`
- **THEN** the transition succeeds and updates the ticket status

#### Scenario: Invalid kitchen ticket transition
- **WHEN** the domain is asked to perform an unsupported transition
- **THEN** it raises `InvalidKitchenTicketStatusTransitionError` containing the current and target statuses

### Requirement: Publish kitchen ticket decision events
Kitchen service SHALL publish accepted and rejected ticket events through the transactional outbox using the `ftgo.events` exchange.

#### Scenario: Publish accepted event
- **WHEN** an unpublished `KitchenTicketAccepted` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.KitchenTicket.KitchenTicketAccepted`
- **AND** the payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`

#### Scenario: Publish rejected event
- **WHEN** an unpublished `KitchenTicketRejected` outbox entry is relayed
- **THEN** it is published with routing key `ftgo.KitchenTicket.KitchenTicketRejected`
- **AND** the payload includes `ticket_id`, `order_id`, `restaurant_id`, and `status`
- **AND** `rejection_reason` is omitted when no reason is provided

### Requirement: Order reacts to kitchen ticket decisions
Order service SHALL consume kitchen ticket accepted and rejected events and drive the order state machine.

#### Scenario: Accepted ticket begins preparing
- **WHEN** `KitchenTicketAccepted` is received for an order in status `APPROVED`
- **THEN** order service transitions the order to `PREPARING` and acknowledges the message

#### Scenario: Rejected ticket cancels order
- **WHEN** `KitchenTicketRejected` is received for an order in status `PENDING`, `APPROVED`, or `PREPARING`
- **THEN** order service transitions the order to `CANCELLED` and acknowledges the message

#### Scenario: Duplicate decision event
- **WHEN** a kitchen decision event is redelivered for an order already in the target status
- **THEN** order service treats the event as a duplicate and acknowledges it without changing state

### Requirement: Document kitchen decision contracts
The event contracts for `KitchenTicketAccepted` and `KitchenTicketRejected` SHALL be documented under `docs/contracts/`.

#### Scenario: Contracts updated
- **WHEN** the kitchen decision events are implemented
- **THEN** the event contract documentation includes exchange, routing key, delivery guarantee, idempotency key, and JSON envelope examples
