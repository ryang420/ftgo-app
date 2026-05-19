# kitchen-service

Owns ticket creation, kitchen workflow, and meal preparation state changes.

Current scope:

- Consumes `OrderCreated` from RabbitMQ.
- Creates one idempotent kitchen ticket per order.
- Exposes `GET /kitchen/tickets` on port `8004` during local development.
