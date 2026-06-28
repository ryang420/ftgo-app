## 1. Delivery-Service Domain And Persistence

- [x] 1.1 Add `DeliveryStatus`, `Delivery`, delivery line-free aggregate fields, and invalid transition errors under `services/delivery-service/src/delivery_service/domain/`.
- [x] 1.2 Add delivery repository and unit-of-work protocols matching the existing service port patterns.
- [x] 1.3 Add SQLAlchemy delivery and outbox ORM models plus mappers.
- [x] 1.4 Add delivery-service session setup and concrete repository/unit-of-work implementations.
- [x] 1.5 Add Alembic migration for deliveries, delivery status enum, unique `order_id`, and delivery outbox messages.
- [x] 1.6 Add delivery domain tests for valid transitions, invalid transitions, and idempotent repeats.

## 2. Delivery-Service Application And Events

- [x] 2.1 Add delivery outbox event builders for `DeliveryCreated`, `DeliveryAssigned`, `DeliveryPickedUp`, and `DeliveryDelivered`.
- [x] 2.2 Add application service method to create a delivery from `KitchenTicketReadyForPickup` payload idempotently by `order_id`.
- [x] 2.3 Add application service methods for assign courier, mark picked up, and mark delivered with outbox writes in the same unit of work.
- [x] 2.4 Add application tests proving each successful transition writes exactly one matching outbox event.
- [x] 2.5 Add application tests proving duplicate ready-ticket and duplicate lifecycle commands do not write duplicate outbox events.

## 3. Delivery-Service API, Relay, And Consumer

- [x] 3.1 Add Pydantic delivery schemas for reads and assign requests.
- [x] 3.2 Add API routes for `GET /deliveries`, `GET /deliveries/{delivery_id}`, `POST /deliveries/{delivery_id}/assign`, `POST /deliveries/{delivery_id}/pickup`, and `POST /deliveries/{delivery_id}/deliver`.
- [x] 3.3 Map not found responses to `404`, invalid transitions to `409`, and invalid assign payloads to `422`.
- [x] 3.4 Add RabbitMQ consumer binding for `ftgo.KitchenTicket.KitchenTicketReadyForPickup`.
- [x] 3.5 Add delivery outbox relay using the existing common relay/publisher pattern.
- [x] 3.6 Wire delivery-service FastAPI dependencies and startup module exports consistently with other services.
- [x] 3.7 Add delivery-service route and consumer tests for happy path, malformed event ack behavior, and duplicate event idempotency.
- [x] 3.8 Propagate `delivery_address` through kitchen ticket creation and `KitchenTicketReadyForPickup`.

## 4. Order-Service Delivery Status Integration

- [x] 4.1 Add `DELIVERY_ASSIGNED`, `OUT_FOR_DELIVERY`, and `DELIVERED` to the order domain status enum.
- [x] 4.2 Add `mark_delivery_assigned()`, `mark_out_for_delivery()`, and `mark_delivered()` domain transition methods with duplicate target-state idempotency.
- [x] 4.3 Add order-service domain property tests for valid, invalid, and duplicate delivery transitions.
- [x] 4.4 Add order lifecycle application service methods for delivery assigned, out for delivery, and delivered.
- [x] 4.5 Add Alembic migration adding the new order status enum values.
- [x] 4.6 Update order schemas/mappers if needed so new statuses serialize through existing API responses.

## 5. Order-Service Delivery Event Consumers

- [x] 5.1 Add handler for `DeliveryCreated` that validates `order_id`, acknowledges valid messages, and leaves the order in `READY`.
- [x] 5.2 Add handler for `DeliveryAssigned` that transitions `READY -> DELIVERY_ASSIGNED`.
- [x] 5.3 Add handler for `DeliveryPickedUp` that transitions `DELIVERY_ASSIGNED -> OUT_FOR_DELIVERY`.
- [x] 5.4 Add handler for `DeliveryDelivered` that transitions `OUT_FOR_DELIVERY -> DELIVERED`.
- [x] 5.5 Bind durable queues to `ftgo.Delivery.DeliveryCreated`, `ftgo.Delivery.DeliveryAssigned`, `ftgo.Delivery.DeliveryPickedUp`, and `ftgo.Delivery.DeliveryDelivered`.
- [x] 5.6 Add consumer tests for malformed payloads, missing orders, invalid transitions, duplicate events, and successful transitions.

## 6. Gateway, Frontend, And Documentation

- [x] 6.1 Add api-gateway upstream configuration and route forwarding for `/deliveries`.
- [x] 6.2 Update frontend API helpers for delivery routes if the UI or tests need manual delivery controls.
- [x] 6.3 Update frontend polling terminal statuses so `READY`, `DELIVERY_ASSIGNED`, and `OUT_FOR_DELIVERY` continue polling while `DELIVERED`, `CANCELLED`, and `REJECTED` stop polling.
- [x] 6.4 Update `StatusBadge` and order status copy for `READY`, `DELIVERY_ASSIGNED`, `OUT_FOR_DELIVERY`, and `DELIVERED`.
- [x] 6.5 Update `docs/contracts/events.md` with delivery event contracts and payload examples.
- [x] 6.6 Update `docs/use-cases/place-order.md` so the flow and state model continue from kitchen readiness through delivery completion.

## 7. End-To-End Verification

- [x] 7.1 Add or extend e2e tests to create an order, advance the kitchen ticket to ready, create/observe delivery creation, assign courier, mark picked up, mark delivered, and assert final order status `DELIVERED`.
- [x] 7.2 Run `uv run pytest services/delivery-service/src/tests/ -v`.
- [x] 7.3 Run `uv run pytest services/order-service/src/tests/ -v`.
- [x] 7.4 Run `uv run pytest services/api-gateway/src/tests/ -v`.
- [x] 7.5 Run `uv run pytest tests/e2e/test_place_order_flow.py -v`.
- [x] 7.6 Run frontend build verification with `cd frontend && npm run build`.
- [x] 7.7 Run `uv run ruff check`.
