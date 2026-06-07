## ADDED Requirements

### Requirement: Order summary read model
Order query service SHALL maintain a denormalized `OrderSummary` read model in its own database.

#### Scenario: Store order summary
- **WHEN** an `OrderCreated` event is processed for a new order
- **THEN** one `OrderSummary` row is created with order, consumer, restaurant, status, amount, address, and timestamp fields
- **AND** related line item rows are created for each event line item

### Requirement: Read model schema
Order query service SHALL manage its database schema through Alembic migrations.

#### Scenario: Apply initial migration
- **WHEN** migrations are applied to an empty `order_query_db`
- **THEN** the order summary and line item tables, indexes, constraints, and status enum are created

### Requirement: Event consumer
Order query service SHALL consume order lifecycle events from RabbitMQ and dispatch them to event handlers.

#### Scenario: Bind lifecycle events
- **WHEN** the event consumer starts
- **THEN** it declares the durable `ftgo.events` exchange and binds a durable queue to `OrderCreated`, `KitchenTicketCreated`, `KitchenTicketAccepted`, and `KitchenTicketRejected`

#### Scenario: Handle consumer failures
- **WHEN** event handling fails with a transient error
- **THEN** the message is not acknowledged so RabbitMQ can redeliver it

### Requirement: Handle order lifecycle events
Order query service SHALL update the read model from order and kitchen ticket events.

#### Scenario: Handle order created
- **WHEN** a valid `OrderCreated` event is received for a new order
- **THEN** the service creates an order summary and commits the unit of work

#### Scenario: Handle kitchen ticket created
- **WHEN** a `KitchenTicketCreated` event is received
- **THEN** the service acknowledges it without changing order summary status

#### Scenario: Handle kitchen ticket accepted
- **WHEN** a `KitchenTicketAccepted` event is received for an existing order summary
- **THEN** the service updates the order summary status to `PREPARING`

#### Scenario: Handle kitchen ticket rejected
- **WHEN** a `KitchenTicketRejected` event is received for an existing order summary
- **THEN** the service updates the order summary status to `CANCELLED`

### Requirement: Idempotent event handling
Order query service SHALL tolerate at-least-once delivery without corrupting the read model.

#### Scenario: Duplicate event
- **WHEN** the same supported event is delivered more than once
- **THEN** the service produces the same final read model state and acknowledges the duplicate

#### Scenario: Malformed event
- **WHEN** a malformed event or payload with invalid identifiers is received
- **THEN** the service logs the error and rejects or acknowledges according to whether the error is permanent

### Requirement: Query API
Order query service SHALL expose REST endpoints for querying order summaries.

#### Scenario: Fetch order by ID
- **WHEN** `GET /orders/{order_id}` is called for an existing order summary
- **THEN** the service returns that order summary with line items

#### Scenario: List orders by consumer
- **WHEN** `GET /orders?consumer_id={consumer_id}` is called
- **THEN** the service returns order summaries for that consumer sorted newest first

#### Scenario: List orders by status
- **WHEN** `GET /orders?status={status}` is called
- **THEN** the service returns order summaries with that status sorted newest first

### Requirement: DDD service structure
Order query service SHALL follow the same DDD layering and service structure used by the existing Python services.

#### Scenario: Service layout
- **WHEN** the order query service is implemented
- **THEN** its code is organized into `api`, `application`, `domain`, and `infrastructure` layers with persistence behind repository and unit-of-work ports
