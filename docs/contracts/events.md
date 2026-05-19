# Event Contracts

## OrderCreated

Published by `order-service` when an order is accepted and stored.

- Exchange: `ftgo.events`
- Routing key: `ftgo.Order.OrderCreated`
- Delivery: at least once
- Idempotency key for consumers: `message_id` or `payload.order_id`

Envelope:

```json
{
  "event_type": "OrderCreated",
  "aggregate_type": "Order",
  "aggregate_id": "<order-id>",
  "payload": {
    "order_id": "<order-id>",
    "consumer_id": "<consumer-id>",
    "restaurant_id": 1,
    "status": "PENDING",
    "currency": "USD",
    "total_amount": "56.00",
    "delivery_address": "123 Main St, Shanghai, 200000",
    "line_items": [
      {
        "id": "<order-line-item-id>",
        "menu_item_id": 20,
        "name": "Beef Noodles",
        "quantity": 2,
        "unit_price": "28.00"
      }
    ]
  },
  "occurred_at": "2026-05-19T12:00:00+00:00"
}
```
