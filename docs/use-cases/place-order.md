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
        Kitchen->>KitchenDB: Insert kitchen ticket + line items
        KitchenDB-->>Kitchen: Commit
    else Duplicate event
        KitchenDB-->>Kitchen: Existing ticket
    end
    Kitchen-->>KitchenConsumer: Kitchen ticket
    KitchenConsumer-->>RabbitMQ: Ack message
```

## Example

If the local stack is running, execute the full flow with:

```bash
make demo-place-order
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
make e2e-place-order
```

### Idempotency

Pass `Idempotency-Key` header to avoid duplicate orders on network retries.
The key is scoped to the consumer and cached in-memory for 1 hour.
