# Place Order Use Case

This is the first end-to-end FTGO use case.

## Flow

1. Create a consumer.
2. Create a restaurant with menu items.
3. Create an order through the API gateway.
4. `order-service` validates the consumer with `consumer-service`.
5. `order-service` validates the restaurant and menu item with `restaurant-service`.
6. `order-service` stores a pending order using the menu snapshot returned by `restaurant-service`.
7. `order-service` records an `OrderCreated` event in its transactional outbox in the same database transaction.
8. `order-service` outbox relay publishes `OrderCreated` to RabbitMQ.
9. `kitchen-service` consumes `OrderCreated` and creates a kitchen ticket idempotently.
10. `kitchen-service` records and publishes `KitchenTicketCreated`.
11. `order-service` consumes `KitchenTicketCreated` and transitions the order to `APPROVED`.

## Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Gateway as api-gateway
    participant Consumer as consumer-service
    participant Restaurant as restaurant-service
    participant Order as order-service
    participant OrderDB as order_db
    participant Relay as order outbox relay
    participant RabbitMQ
    participant KitchenConsumer as kitchen OrderCreated consumer
    participant Kitchen as kitchen-service
    participant KitchenDB as kitchen_db
    participant KitchenRelay as kitchen outbox relay
    participant OrderConsumer as order KitchenTicketCreated consumer

    Client->>Gateway: POST /orders
    Gateway->>Order: Forward POST /orders
    Order->>Consumer: GET /consumers/{consumer_id}
    Consumer-->>Order: Consumer exists
    Order->>Restaurant: GET /restaurants/{restaurant_id}
    Restaurant-->>Order: Restaurant exists
    Order->>Restaurant: GET /restaurants/{restaurant_id}/menu-items/{menu_item_id}
    Restaurant-->>Order: Menu item snapshot
    Order->>OrderDB: Insert order + line items + OrderCreated outbox message
    OrderDB-->>Order: Commit
    Order-->>Gateway: 201 OrderRead
    Gateway-->>Client: 201 OrderRead

    loop Poll unpublished outbox messages
        Relay->>OrderDB: SELECT unpublished OrderCreated
        OrderDB-->>Relay: Outbox message
        Relay->>RabbitMQ: Publish ftgo.Order.OrderCreated
        Relay->>OrderDB: Mark outbox message published
    end

    RabbitMQ-->>KitchenConsumer: Deliver OrderCreated
    KitchenConsumer->>Kitchen: create_ticket_for_order(order_id)
    Kitchen->>KitchenDB: Find ticket by order_id
    alt Ticket does not exist
        Kitchen->>KitchenDB: Insert kitchen ticket + line items + KitchenTicketCreated outbox
        KitchenDB-->>Kitchen: Commit
    else Duplicate event
        KitchenDB-->>Kitchen: Existing ticket
    end
    Kitchen-->>KitchenConsumer: Kitchen ticket
    KitchenConsumer-->>RabbitMQ: Ack message

    loop Poll unpublished kitchen outbox messages
        KitchenRelay->>KitchenDB: SELECT unpublished KitchenTicketCreated
        KitchenDB-->>KitchenRelay: Outbox message
        KitchenRelay->>RabbitMQ: Publish ftgo.KitchenTicket.KitchenTicketCreated
        KitchenRelay->>KitchenDB: Mark outbox message published
    end

    RabbitMQ-->>OrderConsumer: Deliver KitchenTicketCreated
    OrderConsumer->>Order: approve_order(order_id)
    Order->>OrderDB: Update order status to APPROVED
    OrderDB-->>Order: Commit
    OrderConsumer-->>RabbitMQ: Ack message
```

## Example

If the local stack is running, verify the full flow with:

```bash
uv run pytest tests/e2e/test_place_order_flow.py
```

Or run the steps manually:

Create a consumer:

```bash
curl -s -X POST http://localhost:8000/consumers \
  -H 'content-type: application/json' \
  -d '{
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Wang",
    "addresses": [{
      "label": "home",
      "street1": "123 Main St",
      "city": "Shanghai",
      "state": "Shanghai",
      "postal_code": "200000",
      "country": "CN"
    }]
  }'
```

Create a restaurant:

```bash
curl -s -X POST http://localhost:8000/restaurants \
  -H 'content-type: application/json' \
  -d '{
    "name": "Noodle House",
    "slug": "noodle-house",
    "cuisine": "Chinese",
    "menu_items": [{
      "name": "Beef Noodles",
      "description": "Classic bowl",
      "price": "28.00"
    }]
  }'
```

Create an order:

```bash
curl -s -X POST http://localhost:8000/orders \
  -H 'content-type: application/json' \
  -H 'Idempotency-Key: order-alice-001' \
  -d '{
    "consumer_id": "<consumer-id>",
    "restaurant_id": 1,
    "currency": "USD",
    "delivery_address": "123 Main St, Shanghai, 200000",
    "line_items": [{
      "menu_item_id": 1,
      "quantity": 2
    }]
  }'
```

The order response includes the menu item name and price from `restaurant-service`.
If the consumer, restaurant, or menu item does not exist, `order-service` rejects
the order instead of storing an invalid reference.
When the order is accepted, the order row and its `OrderCreated` outbox message
are committed together so downstream services can consume the event later.

After the event is published and consumed, the kitchen ticket can be queried:

```bash
curl -s http://localhost:8000/kitchen/tickets | python -m json.tool
```

To verify the whole flow:

```bash
uv run pytest tests/e2e/test_place_order_flow.py
```

## Order Status Model

`order-service` owns the order lifecycle. Other services do not update order
rows directly; they publish domain events and `order-service` decides the valid
state transition.

Current states:

- `PENDING`: order was accepted and is waiting for downstream progress.
- `APPROVED`: kitchen ticket was created and the order can continue.
- `REJECTED`: order cannot proceed.
- `CANCELLED`: order was cancelled before completion.

State transitions are implemented on the `Order` domain model, for example
`approve()`, `reject()`, and `cancel()`. Repeated events are treated
idempotently where safe, such as approving an already approved order.

Future states should be added by extending the domain state machine first, then
updating the database enum migration and event consumers. This keeps status
rules in one place instead of spreading string assignments across APIs,
repositories, and message handlers.

### Idempotency

Pass `Idempotency-Key` header to avoid duplicate orders on network retries.
The key is scoped to the consumer and cached in-memory for 1 hour.
