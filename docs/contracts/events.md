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

## KitchenTicketCreated

Published by `kitchen-service` when an `OrderCreated` event has produced a
kitchen ticket.

- Exchange: `ftgo.events`
- Routing key: `ftgo.KitchenTicket.KitchenTicketCreated`
- Delivery: at least once
- Idempotency key for consumers: `message_id` or `payload.ticket_id`
- Order-side idempotency key: `payload.order_id`

Envelope:

```json
{
  "event_type": "KitchenTicketCreated",
  "aggregate_type": "KitchenTicket",
  "aggregate_id": "<ticket-id>",
  "payload": {
    "ticket_id": "<ticket-id>",
    "order_id": "<order-id>",
    "restaurant_id": 1,
    "status": "CREATE_PENDING",
    "line_items": [
      {
        "id": "<ticket-line-item-id>",
        "menu_item_id": 20,
        "name": "Beef Noodles",
        "quantity": 2
      }
    ]
  },
  "occurred_at": "2026-05-21T12:00:00+00:00"
}
```

## KitchenTicketAccepted

Published by `kitchen-service` when kitchen staff accept a ticket.

- Exchange: `ftgo.events`
- Routing key: `ftgo.KitchenTicket.KitchenTicketAccepted`
- Delivery: at least once
- Idempotency key for consumers: `message_id` or `payload.ticket_id`
- Order-side idempotency key: `payload.order_id`

Envelope:

```json
{
  "event_type": "KitchenTicketAccepted",
  "aggregate_type": "KitchenTicket",
  "aggregate_id": "<ticket-id>",
  "payload": {
    "ticket_id": "<ticket-id>",
    "order_id": "<order-id>",
    "restaurant_id": 1,
    "status": "ACCEPTED"
  },
  "occurred_at": "2026-06-07T12:00:00+00:00"
}
```

## KitchenTicketRejected

Published by `kitchen-service` when kitchen staff reject a ticket.

- Exchange: `ftgo.events`
- Routing key: `ftgo.KitchenTicket.KitchenTicketRejected`
- Delivery: at least once
- Idempotency key for consumers: `message_id` or `payload.ticket_id`
- Order-side idempotency key: `payload.order_id`

Envelope (with rejection reason):

```json
{
  "event_type": "KitchenTicketRejected",
  "aggregate_type": "KitchenTicket",
  "aggregate_id": "<ticket-id>",
  "payload": {
    "ticket_id": "<ticket-id>",
    "order_id": "<order-id>",
    "restaurant_id": 1,
    "status": "CANCELLED",
    "rejection_reason": "Out of stock"
  },
  "occurred_at": "2026-06-07T12:00:00+00:00"
}
```

When no `rejection_reason` is provided, the key is omitted from the payload entirely (not set to `null`).
