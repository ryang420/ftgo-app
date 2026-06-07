# Requirements Document

## Introduction

`order-query-service` is the CQRS read side for orders in the FTGO application.
It subscribes to order lifecycle events published to RabbitMQ by `order-service`
and `kitchen-service`, maintains a denormalized `OrderSummary` read model in its
own dedicated PostgreSQL database (`order_query_db`), and exposes a FastAPI REST
API for querying orders by ID, by consumer, and by status. The service never
writes to `order-service`'s database; all state derives exclusively from consumed
domain events. At-least-once delivery is handled through idempotent event
processing.

---

## Glossary

- **Order_Query_Service**: The `order-query-service` Python microservice that
  owns the CQRS read side for orders.
- **OrderSummary**: The denormalized, query-optimised view entity stored in
  `order_query_db`. One row per order. Fields: `order_id`, `consumer_id`,
  `restaurant_id`, `status`, `currency`, `total_amount`, `delivery_address`,
  `created_at`, `updated_at`, and a related collection of `OrderSummaryLineItem`
  records.
- **OrderSummaryLineItem**: A child record of `OrderSummary`. Fields:
  `line_item_id`, `order_id`, `menu_item_id`, `name`, `quantity`, `unit_price`.
- **Event_Consumer**: The background process inside `order-query-service` that
  connects to RabbitMQ, subscribes to the `ftgo.events` topic exchange, and
  dispatches incoming event messages to the appropriate handler.
- **Event_Handler**: An application-layer function inside `order-query-service`
  that interprets one event type and updates the `OrderSummary` read model
  accordingly.
- **OrderSummaryRepository**: The port (abstract interface) declared by the
  domain/application layer and implemented by SQLAlchemy infrastructure. Provides
  `add`, `get_by_id`, `update_status`, `list_by_consumer`, and `list_by_status`
  operations.
- **Unit_Of_Work**: The SQLAlchemy session wrapper that commits or rolls back a
  single database transaction spanning one event-handling operation.
- **OrderCreated**: Domain event published by `order-service` when a new order is
  stored. Routing key: `ftgo.Order.OrderCreated`.
- **KitchenTicketCreated**: Domain event published by `kitchen-service` when a
  kitchen ticket is created for an order. Routing key:
  `ftgo.KitchenTicket.KitchenTicketCreated`.
- **KitchenTicketAccepted**: Domain event published by `kitchen-service` when a
  kitchen ticket is accepted. Routing key:
  `ftgo.KitchenTicket.KitchenTicketAccepted`.
- **KitchenTicketRejected**: Domain event published by `kitchen-service` when a
  kitchen ticket is rejected. Routing key:
  `ftgo.KitchenTicket.KitchenTicketRejected`.
- **PENDING**: `OrderSummary` status mirroring the initial order status emitted
  in `OrderCreated`.
- **APPROVED**: `OrderSummary` status set after `KitchenTicketCreated` is
  consumed (matching the order-service lifecycle in the current codebase).
- **PREPARING**: `OrderSummary` status set when `KitchenTicketAccepted` is
  consumed.
- **CANCELLED**: `OrderSummary` status set when `KitchenTicketRejected` is
  consumed.
- **Idempotency_Key**: A stable, per-event identifier used to detect and discard
  duplicate deliveries. For `OrderCreated` the key is `payload.order_id`; for
  kitchen ticket events the key is `payload.order_id`.
- **API_Gateway**: The nginx-based gateway through which clients reach the
  `order-query-service` REST endpoints.

---

## Requirements

### Requirement 1: OrderSummary Read Model

**User Story:** As a developer, I want a denormalized `OrderSummary` view stored
in `order_query_db`, so that queries can be served without joining across multiple
services or databases.

#### Acceptance Criteria (Requirement 1)

1. THE Order_Query_Service SHALL maintain one `OrderSummary` row per unique
   `order_id` in `order_query_db`, containing `order_id`, `consumer_id`,
   `restaurant_id`, `status`, `currency`, `total_amount`, `delivery_address`,
   `created_at`, and `updated_at`.
2. THE Order_Query_Service SHALL maintain one `OrderSummaryLineItem` row per line
   item of each order, containing `line_item_id`, `order_id`, `menu_item_id`,
   `name`, `quantity`, and `unit_price`, associated with the parent `OrderSummary`
   via `order_id`.
3. THE Order_Query_Service SHALL store all `OrderSummary` and
   `OrderSummaryLineItem` records in the `order_query_db` database and SHALL NOT
   read from or write to any other service's database.
4. WHEN a new `OrderSummary` row is created, THE Order_Query_Service SHALL set
   both `created_at` and `updated_at` to the current wall-clock timestamp at the
   time of the insert.
5. THE OrderSummaryRepository SHALL provide `add`, `get_by_id`, `update_status`,
   `list_by_consumer`, and `list_by_status` operations as the sole persistence
   interface for the `OrderSummary` aggregate. `get_by_id` SHALL return `None`
   when no matching row exists; `update_status` SHALL raise a not-found error when
   the `order_id` does not exist.
6. WHEN an existing `OrderSummary` row is updated, THE Order_Query_Service SHALL
   set `updated_at` to the current wall-clock timestamp at the time of the update
   and SHALL NOT change `created_at`.

---

### Requirement 2: Database Schema and Migrations

**User Story:** As a developer, I want the read model schema managed by Alembic,
so that schema changes are version-controlled and reproducible.

#### Acceptance Criteria (Requirement 2)

1. THE Order_Query_Service SHALL manage the `order_query_db` schema exclusively
   through Alembic migrations stored under
   `services/order-query-service/migrations/`.
2. WHEN the `order_summaries` table is created, THE Order_Query_Service SHALL
   define it with columns: `order_id` (UUID, primary key), `consumer_id` (UUID,
   indexed), `restaurant_id` (integer, indexed), `status` (PostgreSQL enum
   `order_summary_status` with values `PENDING`, `APPROVED`, `PREPARING`,
   `CANCELLED`, indexed), `currency` (char(3)), `total_amount` (numeric(10,2)),
   `delivery_address` (varchar(500)), `created_at` (timestamp with time zone,
   non-null), and `updated_at` (timestamp with time zone, non-null).
3. WHEN the `order_summary_line_items` table is created, THE Order_Query_Service
   SHALL define it with columns: `id` (UUID, primary key), `order_id` (UUID,
   foreign key → `order_summaries.order_id` with `ON DELETE CASCADE`),
   `menu_item_id` (integer), `name` (varchar(255)), `quantity` (integer, with
   `CHECK (quantity >= 1)`), and `unit_price` (numeric(10,2)).
4. WHEN the initial Alembic migration is applied to an empty database, THE
   Order_Query_Service SHALL create both tables with all indexes, constraints, and
   the `ON DELETE CASCADE` behavior specified in criteria 2 and 3.

---

### Requirement 3: RabbitMQ Event Consumer

**User Story:** As a developer, I want a RabbitMQ consumer background process in
`order-query-service`, so that the service receives order lifecycle events and
keeps the read model up to date.

#### Acceptance Criteria (Requirement 3)

1. WHEN `order-query-service` starts its Event_Consumer, THE Event_Consumer SHALL
   declare the `ftgo.events` topic exchange as durable, declare a durable queue
   named `order-query.order-events`, and bind it with routing keys
   `ftgo.Order.OrderCreated`, `ftgo.KitchenTicket.KitchenTicketCreated`,
   `ftgo.KitchenTicket.KitchenTicketAccepted`, and
   `ftgo.KitchenTicket.KitchenTicketRejected`.
2. WHILE the Event_Consumer is running and connected to RabbitMQ, THE
   Event_Consumer SHALL dispatch each incoming message to the Event_Handler
   corresponding to the message's `event_type` field in the envelope.
3. WHEN an Event_Handler completes successfully, THE Event_Consumer SHALL
   acknowledge the message to RabbitMQ.
4. IF an incoming message contains a valid envelope but the `event_type` value is
   not one of the four bound event types, THEN THE Event_Consumer SHALL log the
   `event_type` value at `WARNING` level, acknowledge the message, and take no
   further action.
5. IF an Event_Handler raises an exception identified as transient (e.g., database
   connectivity failure), THEN THE Event_Consumer SHALL NOT acknowledge the
   message, allowing RabbitMQ to redeliver it, and SHALL log the error at `ERROR`
   level. IF the exception is identified as permanent (e.g., data integrity
   violation, malformed payload), THEN THE Event_Consumer SHALL reject the message
   without requeue and log at `ERROR` level.
6. IF the connection to RabbitMQ is lost, THEN THE Event_Consumer SHALL attempt
   to reconnect with a delay of 3 to 30 seconds between attempts (using
   exponential backoff), log each reconnection attempt at `WARNING` level, and
   terminate the process with a non-zero exit code after 30 failed attempts.
7. WHEN the Event_Consumer process receives `SIGINT` or `SIGTERM`, THE
   Event_Consumer SHALL finish processing the in-flight message (if any), stop
   consuming new messages, and exit with status code `0` within 30 seconds.

---

### Requirement 4: Handle OrderCreated Event

**User Story:** As a developer, I want `order-query-service` to create an
`OrderSummary` when an `OrderCreated` event is received, so that newly placed
orders are immediately queryable via the read model.

#### Acceptance Criteria (Requirement 4)

1. WHEN an `OrderCreated` event is received and no `OrderSummary` with the
   matching `order_id` exists, THE Event_Handler SHALL create a new `OrderSummary`
   row with fields populated from the event payload (`order_id`, `consumer_id`,
   `restaurant_id`, `status`, `currency`, `total_amount`, `delivery_address`, and
   `created_at` set to the current wall-clock timestamp), create the corresponding
   `OrderSummaryLineItem` rows from `payload.line_items` (mapping `id` →
   `line_item_id`, `menu_item_id`, `name`, `quantity`, `unit_price`), then commit
   the Unit_Of_Work.
2. WHEN an `OrderCreated` event is received and an `OrderSummary` with the same
   `order_id` already exists, THE Event_Handler SHALL skip the insert, roll back
   the Unit_Of_Work, and acknowledge the message without modifying existing rows.
3. IF the database commit in criterion 1 fails due to any error that is not a
   data-integrity or constraint-violation error (transient error), THEN THE
   Event_Handler SHALL roll back the Unit_Of_Work and raise the exception so the
   Event_Consumer withholds the acknowledgement.
4. THE Event_Handler SHALL use `payload.order_id` as the Idempotency_Key for
   duplicate detection of `OrderCreated` events.

---

### Requirement 5: Handle KitchenTicketCreated Event

**User Story:** As a developer, I want `order-query-service` to acknowledge
`KitchenTicketCreated` events without altering the order status, so that the
consumer pipeline stays in sync with the event stream even when no status change
is required.

#### Acceptance Criteria (Requirement 5)

1. WHEN a `KitchenTicketCreated` event is received and an `OrderSummary` with the
   matching `order_id` exists, THE Event_Handler SHALL leave all `OrderSummary`
   fields unchanged and acknowledge the message.
2. WHEN a `KitchenTicketCreated` event is received and no `OrderSummary` with the
   matching `order_id` exists, THE Event_Handler SHALL log a warning at `WARNING`
   level with the `order_id` value and acknowledge the message without creating a
   new `OrderSummary` row.
3. THE Event_Handler SHALL use `payload.order_id` as the Idempotency_Key for
   duplicate detection of `KitchenTicketCreated` events; any redelivery of the
   same message SHALL result in the same no-op outcome as the first delivery.

---

### Requirement 6: Handle KitchenTicketAccepted Event

**User Story:** As a developer, I want `order-query-service` to update the order
status to `PREPARING` when a `KitchenTicketAccepted` event is received, so that
the read model reflects that the kitchen has accepted the order.

#### Acceptance Criteria (Requirement 6)

1. WHEN a `KitchenTicketAccepted` event is received and the `OrderSummary` for
   the matching `order_id` exists with a status other than `PREPARING`, THE
   Event_Handler SHALL update the `OrderSummary` `status` field to `PREPARING`,
   update `updated_at` to the current wall-clock timestamp, and commit the
   Unit_Of_Work.
2. WHEN a `KitchenTicketAccepted` event is received and the `OrderSummary` for
   the matching `order_id` already has status `PREPARING`, THE Event_Handler SHALL
   treat the message as a duplicate, skip the update, and acknowledge the message.
3. WHEN a `KitchenTicketAccepted` event is received and no `OrderSummary` with
   the matching `order_id` exists, THE Event_Handler SHALL log a warning at
   `WARNING` level and acknowledge the message without creating a new
   `OrderSummary` row.
4. THE Event_Handler SHALL use `payload.order_id` as the Idempotency_Key for
   duplicate detection of `KitchenTicketAccepted` events.
5. IF the database commit in criterion 1 fails due to a transient error, THEN THE
   Event_Handler SHALL roll back the Unit_Of_Work and raise the exception so the
   Event_Consumer withholds the acknowledgement.

---

### Requirement 7: Handle KitchenTicketRejected Event

**User Story:** As a developer, I want `order-query-service` to update the order
status to `CANCELLED` when a `KitchenTicketRejected` event is received, so that
the read model reflects that the order cannot proceed.

#### Acceptance Criteria (Requirement 7)

1. WHEN a `KitchenTicketRejected` event is received and the `OrderSummary` for
   the matching `order_id` exists with a status other than `CANCELLED`, THE
   Event_Handler SHALL update the `OrderSummary` `status` field to `CANCELLED`,
   update `updated_at` to the current wall-clock timestamp, and commit the
   Unit_Of_Work.
2. WHEN a `KitchenTicketRejected` event is received and the `OrderSummary` for
   the matching `order_id` already has status `CANCELLED`, THE Event_Handler SHALL
   treat the message as a duplicate, skip the update, and acknowledge the message.
3. WHEN a `KitchenTicketRejected` event is received and no `OrderSummary` with
   the matching `order_id` exists, THE Event_Handler SHALL log a warning at
   `WARNING` level and acknowledge the message without creating a new
   `OrderSummary` row.
4. THE Event_Handler SHALL use `payload.order_id` as the Idempotency_Key for
   duplicate detection of `KitchenTicketRejected` events.

---

### Requirement 8: Malformed Event Handling

**User Story:** As a developer, I want the Event_Consumer to safely discard
unrecognised or malformed events, so that bad messages do not block the consumer
queue or crash the service.

#### Acceptance Criteria (Requirement 8)

1. IF an incoming message body cannot be parsed as a valid JSON object, THEN THE
   Event_Consumer SHALL log the raw message body (truncated to 1,000 characters)
   at `ERROR` level, acknowledge the message, and take no further action.
2. IF an incoming message contains a valid JSON envelope but the `event_type`
   field is absent or holds an unrecognised value, THEN THE Event_Consumer SHALL
   log the `event_type` value (or note its absence) at `WARNING` level,
   acknowledge the message, and take no further action.
3. IF a recognised event's `payload` is missing a required field or contains a
   field with an invalid type or format as defined by the event contract in
   `docs/contracts/events.md`, THEN THE Event_Consumer SHALL log the validation
   error at `ERROR` level (including the field name and nature of the violation),
   acknowledge the message, and take no further action.
4. IF acknowledging the message to RabbitMQ fails after the Event_Consumer has
   already processed it, THEN THE Event_Consumer SHALL retry the acknowledgement
   up to 3 times at `ERROR` log level before raising an exception, without
   reprocessing the event payload.

---

### Requirement 9: Query API — Fetch Single Order

**User Story:** As a consumer client, I want to fetch a single order summary by
its ID via the API gateway, so that I can display the current status and details
of a specific order.

#### Acceptance Criteria (Requirement 9)

1. WHEN a `GET /orders/{order_id}` request is received and an `OrderSummary` with
   the matching `order_id` exists, THE Order_Query_Service SHALL return HTTP `200`
   with a JSON body containing `order_id` (UUID string), `consumer_id` (UUID
   string), `restaurant_id` (integer), `status` (string), `currency` (string),
   `total_amount` (string representation of decimal), `delivery_address` (string),
   `created_at` (ISO 8601 UTC), `updated_at` (ISO 8601 UTC), and a `line_items`
   array where each element contains `line_item_id` (UUID string), `menu_item_id`
   (integer), `name` (string), `quantity` (integer), and `unit_price` (string
   representation of decimal).
2. WHEN a `GET /orders/{order_id}` request is received and no `OrderSummary` with
   the matching `order_id` exists, THE Order_Query_Service SHALL return HTTP `404`
   with a JSON body containing an `error` field describing the missing resource.
3. IF the `order_id` path parameter is not a valid UUID, THEN THE
   Order_Query_Service SHALL return HTTP `422` with a JSON validation error body.
4. IF the `order_query_db` is unavailable when a `GET /orders/{order_id}` request
   is received, THEN THE Order_Query_Service SHALL return HTTP `503` with a JSON
   error body.

---

### Requirement 10: Query API — List Orders by Consumer

**User Story:** As a consumer client, I want to list all orders belonging to a
specific consumer, so that I can show a consumer's order history.

#### Acceptance Criteria (Requirement 10)

1. WHEN a `GET /orders?consumer_id={id}` request is received and one or more
   `OrderSummary` rows with the matching `consumer_id` exist, THE
   Order_Query_Service SHALL return HTTP `200` with a JSON array of up to 100
   `OrderSummary` objects ordered by `created_at` descending. Each element SHALL
   contain `order_id` (UUID string), `consumer_id` (UUID string), `restaurant_id`
   (integer), `status` (string), `currency` (string), `total_amount` (string),
   `delivery_address` (string), `created_at` (ISO 8601 UTC), `updated_at` (ISO
   8601 UTC), and a `line_items` array as defined in Requirement 9 criterion 1.
2. WHEN a `GET /orders?consumer_id={id}` request is received and no
   `OrderSummary` rows with the matching `consumer_id` exist, THE
   Order_Query_Service SHALL return HTTP `200` with an empty JSON array.
3. IF the `consumer_id` query parameter is not a valid UUID, THEN THE
   Order_Query_Service SHALL return HTTP `422` with a JSON validation error body.
4. IF `GET /orders` is called without any filter parameter (`consumer_id` or
   `status`), THEN THE Order_Query_Service SHALL return HTTP `422` with a JSON
   error body indicating that at least one filter parameter is required.

---

### Requirement 11: Query API — List Orders by Status

**User Story:** As an operations user, I want to filter orders by their current
status, so that I can monitor all orders in a given lifecycle state.

#### Acceptance Criteria (Requirement 11)

1. WHEN a `GET /orders?status={status}` request is received and one or more
   `OrderSummary` rows with the matching `status` exist, THE Order_Query_Service
   SHALL return HTTP `200` with a JSON array of up to 100 `OrderSummary` objects
   ordered by `created_at` descending in the same shape described in Requirement
   10, criterion 1.
2. WHEN a `GET /orders?status={status}` request is received and no
   `OrderSummary` rows with the matching `status` exist, THE Order_Query_Service
   SHALL return HTTP `200` with an empty JSON array.
3. IF the `status` query parameter is not one of the valid `OrderSummary` status
   values (`PENDING`, `APPROVED`, `PREPARING`, `CANCELLED`), THEN THE
   Order_Query_Service SHALL return HTTP `422` with a JSON validation error body.

---

### Requirement 12: Event Consumer Idempotency

**User Story:** As a developer, I want every Event_Handler to be idempotent with
respect to duplicate RabbitMQ deliveries, so that redelivered messages do not
corrupt the `OrderSummary` read model.

#### Acceptance Criteria (Requirement 12)

1. IF the same `OrderCreated` message is processed more than once, THEN THE
   Event_Consumer SHALL produce exactly one `OrderSummary` row with the same
   `order_id`, `status`, `consumer_id`, `total_amount`, and `line_items` as the
   first delivery.
2. IF the same `KitchenTicketCreated` message is processed more than once, THEN
   THE Event_Consumer SHALL leave the `OrderSummary` `status` unchanged after the
   first processing, producing no additional changes on subsequent deliveries.
3. IF the same `KitchenTicketAccepted` message is processed more than once, THEN
   THE Event_Consumer SHALL leave the `OrderSummary` `status` equal to `PREPARING`
   regardless of how many times it is processed.
4. IF the same `KitchenTicketRejected` message is processed more than once, THEN
   THE Event_Consumer SHALL leave the `OrderSummary` `status` equal to `CANCELLED`
   regardless of how many times it is processed.
5. THE `order_summaries` table SHALL enforce a database-level unique constraint on
   `order_id` to prevent concurrent duplicate insertions from bypassing
   application-level idempotency checks.
6. THE Event_Consumer SHALL use `payload.order_id` as the Idempotency_Key for all
   four event types.

---

### Requirement 13: DDD Layering and Service Structure

**User Story:** As a developer, I want `order-query-service` to follow the same
DDD layering rules as `order-service`, so that the codebase remains consistent
and maintainable.

#### Acceptance Criteria (Requirement 13)

1. THE Order_Query_Service SHALL organise its source code under
   `services/order-query-service/src/order_query_service/` with the sub-packages
   `api`, `application`, `domain`, and `infrastructure`, following the layout
   defined in `docs/architecture/ddd-principles.md`.
2. THE Order_Query_Service domain module SHALL contain plain Python objects
   (`OrderSummary`, `OrderSummaryLineItem`, and `OrderSummaryRepository` port)
   and SHALL NOT import from `fastapi`, `sqlalchemy`, `aio_pika`, or any other
   infrastructure library.
3. THE Order_Query_Service application module SHALL orchestrate event-handling use
   cases through the `OrderSummaryRepository` port and SHALL NOT import ORM
   models, HTTP response objects, or broker client objects directly.
4. THE Order_Query_Service infrastructure module SHALL contain the SQLAlchemy ORM
   models, mappers, repository implementations, and the `Event_Consumer` wiring,
   and SHALL be the only layer allowed to depend on `sqlalchemy`, `aio_pika`, and
   `common` database utilities.
5. THE Order_Query_Service API module SHALL contain FastAPI route definitions and
   Pydantic response schemas and SHALL NOT contain domain business logic.
