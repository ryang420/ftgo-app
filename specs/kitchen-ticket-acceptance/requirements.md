# Requirements Document

## Introduction

This feature adds the kitchen ticket acceptance flow to the FTGO application. After a kitchen ticket is created (status `CREATE_PENDING`), kitchen staff must be able to **accept** or **reject** it through `kitchen-service`. Each action publishes a domain event via the transactional outbox. `order-service` consumes those events and drives the `Order` state machine forward: an accepted ticket transitions the order to `PREPARING`; a rejected ticket transitions the order to `CANCELLED`. Idempotency is preserved throughout at-least-once delivery.

---

## Glossary

- **KitchenTicket**: A domain entity in `kitchen-service` that tracks the kitchen's view of a single order. Identified by a UUID (`ticket_id`).
- **Order**: A domain entity in `order-service` that owns the authoritative lifecycle of a customer order. Identified by a UUID (`order_id`).
- **Kitchen_Service**: The `kitchen-service` Python microservice, responsible for managing kitchen ticket state.
- **Order_Service**: The `order-service` Python microservice, responsible for managing order state.
- **KitchenTicketDomainService**: The domain object inside `kitchen-service` that enforces valid `KitchenTicket` state transitions.
- **OrderDomainModel**: The `Order` domain entity inside `order-service` that enforces valid `Order` state transitions.
- **Outbox**: The transactional outbox table inside each service's database. Events written here are committed atomically with domain state changes and later relayed to RabbitMQ.
- **Outbox_Relay**: The background process that polls the Outbox and publishes its messages to RabbitMQ.
- **KitchenTicketAccepted**: The domain event published by `kitchen-service` when a kitchen ticket is accepted.
- **KitchenTicketRejected**: The domain event published by `kitchen-service` when a kitchen ticket is rejected.
- **Kitchen_Consumer**: The RabbitMQ consumer inside `order-service` that handles kitchen ticket events.
- **CREATE_PENDING**: Initial `KitchenTicket` status set when the ticket is first created in response to an `OrderCreated` event.
- **ACCEPTED**: `KitchenTicket` status after kitchen staff accept the ticket.
- **CANCELLED**: `KitchenTicket` status after kitchen staff reject the ticket.
- **APPROVED**: `Order` status set when `KitchenTicketCreated` is consumed (existing, unchanged).
- **PREPARING**: New `Order` status set when `KitchenTicketAccepted` is consumed.

---

## Requirements

### Requirement 1: Accept a Kitchen Ticket via HTTP

**User Story:** As a kitchen staff member, I want to accept a kitchen ticket through a REST endpoint, so that the kitchen can signal readiness to prepare the order.

#### Acceptance Criteria

1. WHEN a `POST /kitchen/tickets/{ticket_id}/accept` request is received and the ticket exists with status `CREATE_PENDING`, THE Kitchen_Service SHALL transition the `KitchenTicket` status to `ACCEPTED`, persist the change and a `KitchenTicketAccepted` outbox entry in the same database transaction, and return `200` with a JSON body containing at minimum `ticket_id` (UUID string) and `status` (`ACCEPTED`).
2. WHEN a `POST /kitchen/tickets/{ticket_id}/accept` request is received and the ticket does not exist, THE Kitchen_Service SHALL return HTTP `404`.
3. IF a `POST /kitchen/tickets/{ticket_id}/accept` request is received and the ticket status is already `ACCEPTED`, THEN THE Kitchen_Service SHALL return `200` with the current ticket representation without writing a duplicate outbox entry.
4. IF a `POST /kitchen/tickets/{ticket_id}/accept` request is received and the ticket status is any value other than `CREATE_PENDING` or `ACCEPTED`, THEN THE Kitchen_Service SHALL return HTTP `409` with a JSON error body that includes the current ticket status and the attempted transition target.
5. IF the database transaction in criterion 1 fails, THEN THE Kitchen_Service SHALL return HTTP `500` and leave the `KitchenTicket` status and the Outbox unchanged.

---

### Requirement 2: Reject a Kitchen Ticket via HTTP

**User Story:** As a kitchen staff member, I want to reject a kitchen ticket through a REST endpoint, so that the kitchen can signal it cannot fulfil the order.

#### Acceptance Criteria

1. WHEN a `POST /kitchen/tickets/{ticket_id}/reject` request is received and the ticket exists with status `CREATE_PENDING`, THE Kitchen_Service SHALL transition the `KitchenTicket` status to `CANCELLED`, persist the change and a `KitchenTicketRejected` outbox entry in the same database transaction, and return `200` with a JSON body containing at minimum `ticket_id` (UUID string) and `status` (`CANCELLED`).
2. WHEN a `POST /kitchen/tickets/{ticket_id}/reject` request is received and the ticket does not exist, THE Kitchen_Service SHALL return HTTP `404`.
3. IF a `POST /kitchen/tickets/{ticket_id}/reject` request is received and the ticket status is already `CANCELLED`, THEN THE Kitchen_Service SHALL return `200` with the current ticket representation without writing a duplicate outbox entry.
4. IF a `POST /kitchen/tickets/{ticket_id}/reject` request is received and the ticket status is any value other than `CREATE_PENDING` or `CANCELLED`, THEN THE Kitchen_Service SHALL return HTTP `409` with a JSON error body that includes the current ticket status and the attempted transition target.
5. IF the database transaction in criterion 1 fails, THEN THE Kitchen_Service SHALL return HTTP `500` and leave the `KitchenTicket` status and the Outbox unchanged.

---

### Requirement 3: KitchenTicketDomainService Enforces Ticket State Transitions

**User Story:** As a developer, I want the `KitchenTicket` domain model to be the single source of truth for valid status transitions, so that business rules cannot be bypassed by callers.

#### Acceptance Criteria

1. THE KitchenTicketDomainService SHALL enforce that only the following status transitions are valid: `CREATE_PENDING → ACCEPTED`, `CREATE_PENDING → CANCELLED`, `ACCEPTED → PREPARING`, `PREPARING → READY_FOR_PICKUP`.
2. IF a caller attempts to transition a `KitchenTicket` from a status that is not a valid source for the requested target (excluding the idempotent-repeat case in criterion 3), THEN THE KitchenTicketDomainService SHALL raise `InvalidKitchenTicketStatusTransitionError` containing the current and target statuses.
3. IF a caller transitions a `KitchenTicket` to its current status (idempotent repeat), THEN THE KitchenTicketDomainService SHALL complete without raising an error and the `KitchenTicket` status field SHALL remain unchanged.

---

### Requirement 4: Publish KitchenTicketAccepted Event

**User Story:** As a developer, I want `kitchen-service` to publish a `KitchenTicketAccepted` event after a ticket is accepted, so that downstream services can react to the acceptance.

#### Acceptance Criteria

1. WHEN a `KitchenTicket` is successfully transitioned to `ACCEPTED`, THE Kitchen_Service SHALL write a `KitchenTicketAccepted` event to the Outbox in the same database transaction as the status update.
2. WHEN the Outbox_Relay reads an unpublished `KitchenTicketAccepted` outbox entry, THE Kitchen_Service SHALL publish the event to the `ftgo.events` exchange with routing key `ftgo.KitchenTicket.KitchenTicketAccepted`. The message envelope SHALL include `event_type`, `aggregate_type`, `aggregate_id`, `occurred_at`, and a `payload` object containing `ticket_id` (used as idempotency key by consumers), `order_id`, `restaurant_id`, and `status`.
3. THE Outbox_Relay SHALL mark the outbox entry as published after receiving a broker acknowledgement from RabbitMQ.
4. IF an unpublished `KitchenTicketAccepted` outbox entry (where `published_at` is unset) is re-selected by the Outbox_Relay, THEN THE Outbox_Relay SHALL re-publish the message without inserting a new outbox row.

---

### Requirement 5: Publish KitchenTicketRejected Event

**User Story:** As a developer, I want `kitchen-service` to publish a `KitchenTicketRejected` event after a ticket is rejected, so that downstream services can react to the rejection.

#### Acceptance Criteria

1. WHEN a `KitchenTicket` is successfully transitioned to `CANCELLED` via the reject operation, THE Kitchen_Service SHALL write a `KitchenTicketRejected` event to the Outbox in the same database transaction as the status update.
2. WHEN the Outbox_Relay reads an unpublished `KitchenTicketRejected` outbox entry, THE Kitchen_Service SHALL publish the event to the `ftgo.events` exchange with routing key `ftgo.KitchenTicket.KitchenTicketRejected`. The message envelope SHALL include `event_type`, `aggregate_type`, `aggregate_id`, `occurred_at`, and a `payload` object containing `ticket_id`, `order_id`, `restaurant_id`, `status`, and an optional `rejection_reason` string.
3. THE Outbox_Relay SHALL mark the outbox entry as published after receiving a broker acknowledgement from RabbitMQ.
4. IF an unpublished `KitchenTicketRejected` outbox entry (where `published_at` is unset) is re-selected by the Outbox_Relay, THEN THE Outbox_Relay SHALL re-publish the message without inserting a new outbox row.

---

### Requirement 6: Order_Service Transitions Order to PREPARING on KitchenTicketAccepted

**User Story:** As a developer, I want `order-service` to move an order to `PREPARING` when `KitchenTicketAccepted` is received, so that the order lifecycle reflects the kitchen's decision.

#### Acceptance Criteria

1. WHEN a `KitchenTicketAccepted` message is delivered to the Kitchen_Consumer, THE Order_Service SHALL look up the `Order` by the `order_id` in the event payload and call `begin_preparing()` on the `OrderDomainModel`.
2. WHEN `begin_preparing()` is called on an `Order` in status `APPROVED`, THE OrderDomainModel SHALL transition the order status to `PREPARING` and commit the change in a single unit of work with all-or-nothing semantics.
3. WHEN a `KitchenTicketAccepted` message is delivered and the `Order` is already in status `PREPARING`, THE Order_Service SHALL treat the event as a duplicate, skip the update, and acknowledge the message.
4. WHEN a `KitchenTicketAccepted` message is delivered and the `Order` is not found, THE Order_Service SHALL log a warning at `WARNING` level and acknowledge the message without retrying.
5. IF a `KitchenTicketAccepted` message is delivered and the `OrderDomainModel` raises `InvalidOrderStatusTransitionError` (i.e., Order status is neither `APPROVED` nor `PREPARING`), THEN THE Order_Service SHALL log the error at `ERROR` level and acknowledge the message to prevent requeue loops.
6. IF the database write in criterion 2 fails, THEN THE Order_Service SHALL NOT acknowledge the message, allowing RabbitMQ to redeliver it, and SHALL log the error at `ERROR` level.

---

### Requirement 7: Order_Service Transitions Order to CANCELLED on KitchenTicketRejected

**User Story:** As a developer, I want `order-service` to cancel an order when `KitchenTicketRejected` is received, so that consumers are notified the order cannot proceed.

#### Acceptance Criteria

1. WHEN a `KitchenTicketRejected` message is delivered to the Kitchen_Consumer, THE Order_Service SHALL look up the `Order` by the `order_id` in the event payload and call `cancel()` on the `OrderDomainModel`.
2. IF `cancel()` is called on an `Order` in status `APPROVED` or `PENDING`, THEN THE OrderDomainModel SHALL transition the order status to `CANCELLED` and commit the change in a single unit of work.
3. WHEN a `KitchenTicketRejected` message is delivered and the `Order` is already in status `CANCELLED`, THE Order_Service SHALL treat the event as a duplicate, skip the update, and acknowledge the message.
4. WHEN a `KitchenTicketRejected` message is delivered and the `Order` is not found, THE Order_Service SHALL log a warning at `WARNING` level and acknowledge the message without retrying.
5. IF a `KitchenTicketRejected` message is delivered and the `OrderDomainModel` raises `InvalidOrderStatusTransitionError`, THEN THE Order_Service SHALL log the error at `ERROR` level and acknowledge the message to prevent requeue loops.

---

### Requirement 8: Order Domain State Machine Owns PREPARING Status

**User Story:** As a developer, I want the `Order` domain model to enforce the `PREPARING` state transition, so that no external caller can bypass the state machine.

#### Acceptance Criteria

1. WHEN `begin_preparing()` is called on an `Order` in status `APPROVED`, THE OrderDomainModel SHALL transition the `Order` status to `PREPARING` and the observable post-condition SHALL be `order.status == PREPARING`.
2. IF `begin_preparing()` is called on an `Order` whose status is `PREPARING`, THEN THE OrderDomainModel SHALL complete without raising an error and without altering the order status.
3. IF `begin_preparing()` is called on an `Order` whose status is not `APPROVED` or `PREPARING`, THEN THE OrderDomainModel SHALL raise `InvalidOrderStatusTransitionError` containing the current and target statuses.
4. THE OrderDomainModel SHALL enforce that `cancel()` is a valid transition when the `Order` status is `PENDING`, `APPROVED`, or `PREPARING`, resulting in status `CANCELLED`.

---

### Requirement 9: Event Consumer Idempotency

**User Story:** As a developer, I want both event consumers in `order-service` to be idempotent, so that duplicate deliveries from RabbitMQ do not corrupt order state.

#### Acceptance Criteria

1. WHEN the Kitchen_Consumer receives a `KitchenTicketAccepted` message with an `order_id` for an `Order` already in status `PREPARING`, THE Order_Service SHALL acknowledge the message and take no further action.
2. WHEN the Kitchen_Consumer receives a `KitchenTicketRejected` message with an `order_id` for an `Order` already in status `CANCELLED`, THE Order_Service SHALL acknowledge the message and take no further action.
3. THE Kitchen_Consumer SHALL fetch the `Order` by `order_id` from the event payload and inspect its current status before invoking any domain method, using `order_id` as the idempotency key.
4. IF the event payload is missing `order_id` or contains a value that is not a valid UUID, THEN THE Kitchen_Consumer SHALL log the malformed event at `ERROR` level and acknowledge the message to prevent requeue loops.

---

### Requirement 10: Event Contracts Documented

**User Story:** As a developer, I want the new event contracts to be documented under `docs/contracts/events.md`, so that all teams share a single source of truth for event shapes.

#### Acceptance Criteria

1. THE project SHALL document the `KitchenTicketAccepted` event in `docs/contracts/events.md` with: exchange name, routing key, delivery guarantee, idempotency key (`ticket_id`), and a JSON envelope example that includes `event_type`, `aggregate_type`, `aggregate_id`, `occurred_at`, and a `payload` object with `ticket_id`, `order_id`, `restaurant_id`, and `status`.
2. THE project SHALL document the `KitchenTicketRejected` event in `docs/contracts/events.md` with: exchange name, routing key, delivery guarantee, idempotency key (`ticket_id`), optional `rejection_reason` field in the payload, and a JSON envelope example that includes `event_type`, `aggregate_type`, `aggregate_id`, `occurred_at`, and a `payload` object with `ticket_id`, `order_id`, `restaurant_id`, `status`, and `rejection_reason`.
3. IF a `KitchenTicketRejected` event is published without a `rejection_reason`, THEN the `rejection_reason` field SHALL be omitted from the payload (not set to `null`).
