# Local Development

The default local infrastructure runs in Docker Compose.

## Start Infrastructure

```bash
make infra-up
```

Postgres listens on `localhost:15432` with:

- user: `ftgo`
- password: `ftgo`
- databases: `consumer_db`, `restaurant_db`, `order_db`, `kitchen_db`

RabbitMQ listens on:

- AMQP: `localhost:5672`
- management UI: `http://localhost:15672`

## Run Migrations

```bash
make migrate
```

Migration targets run from each service directory so Alembic resolves that
service's `migrations/` folder and `src/` package path correctly.

## Start Core Services

To start the full local stack in one command:

```bash
make dev-up
```

This starts Docker infrastructure, runs migrations, starts the core HTTP services,
`order-service` outbox relay, and `kitchen-service` OrderCreated consumer in the
background, and writes logs to `.runtime/logs/`.

To stop the full local stack:

```bash
make dev-down
```

For manual service-by-service startup:

```bash
make run-consumer
make run-restaurant
make run-order
make run-api-gateway
```

The API gateway forwards:

- `/consumers` to `consumer-service`
- `/restaurants` to `restaurant-service`
- `/orders` to `order-service`

`kitchen-service` listens on `http://localhost:8004` and exposes
`/kitchen/tickets` for the current asynchronous ticket projection.

## Reset Infrastructure

If the Postgres volume was created before the service databases were added,
reset the Docker volumes so the init scripts run again:

```bash
make infra-reset
make infra-up
```
