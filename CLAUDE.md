# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FTGO is a Python microservices learning monorepo implementing the food-delivery case study from _Microservice Patterns_. It uses FastAPI, SQLAlchemy, RabbitMQ, and PostgreSQL with a DDD-first service architecture. The frontend is a React + Tailwind CSS scaffold under `frontend/`.

## Development Commands

- **Sync workspace**: `make sync` (runs `uv sync --all-packages`)
- **Lint**: `uv run ruff check`
- **Run tests**: `uv run pytest` (add `-k <pattern>` for a single test)
- **Type check**: `uv run mypy`

### Infrastructure

- `make infra-up` — start Postgres (`localhost:15432`) and RabbitMQ (`localhost:5672`, mgmt `:15672`)
- `make infra-down` — stop infrastructure
- `make infra-reset` — stop and remove volumes
- `make migrate` — run Alembic migrations for all services with databases

### Running the Stack

- `make dev-up` — start infra, migrate, start all core services + outbox relays + event consumers (logs in `.runtime/logs/`)
- `make dev-down` — stop everything
- `make run-consumer` / `make run-restaurant` / `make run-order` / `make run-api-gateway` — start individual services
- `make run-order-relay` — start only the order outbox relay
- `uv run pytest tests/e2e` — verify cross-service end-to-end flows

### Frontend

```bash
cd frontend && npm install && npm run dev
```

## Architecture

### Service Layout (DDD)

Each service follows this dependency direction: `api` → `application` → `domain`. `domain` is pure Python with no framework imports. `infrastructure` implements ports declared by `domain`/`application`.

```
service/
  pyproject.toml
  migrations/
  src/<package>/
    api/             # FastAPI routes + dependencies (DI wiring)
    application/     # Use-case orchestration, commands, ports (Protocols)
    domain/          # Pure entities, value objects, repository Protocols
    infrastructure/  # ORM models, repo impls, HTTP clients, messaging adapters
    schemas/         # Pydantic request/response DTOs
```

`order-service` is the reference implementation. `kitchen-service` follows the same pattern. Other services are scaffolds to be migrated toward this structure.

### Services and Ports

| Service | Port | Purpose |
|---------|------|---------|
| api-gateway | 8000 | Proxies `/consumers`, `/restaurants`, `/orders`, `/kitchen` |
| consumer-service | 8001 | Consumer CRUD |
| restaurant-service | 8002 | Restaurant + menu item CRUD |
| order-service | 8003 | Order lifecycle, owns the order state machine |
| kitchen-service | 8004 | Kitchen ticket creation from orders |

### Placed-Order Flow (the main implemented use case)

1. Client POSTs order to api-gateway → order-service
2. order-service validates consumer (HTTP to consumer-service) and restaurant/menu items (HTTP to restaurant-service)
3. On success, order-service persists the order + an `OrderCreated` outbox message **in the same DB transaction** (transactional outbox)
4. A separate **outbox relay** process polls the `outbox_messages` table and publishes to RabbitMQ (`ftgo.events`, routing key `ftgo.Order.OrderCreated`)
5. kitchen-service's event consumer receives `OrderCreated`, creates a kitchen ticket idempotently, and writes a `KitchenTicketCreated` outbox message
6. kitchen-service's outbox relay publishes `KitchenTicketCreated` to RabbitMQ
7. order-service's event consumer receives it and calls `order.approve()`, transitioning the order from `PENDING` to `APPROVED`

### Key Patterns

- **Transactional outbox**: Domain events are written to an `outbox_messages` table in the same transaction as the aggregate. A separate relay process polls and publishes them. This guarantees at-least-once delivery.
- **Port/Adapter**: Domain defines `Protocol` classes (e.g., `OrderRepository`, `RestaurantCatalog`). Infrastructure provides concrete implementations (e.g., `SqlAlchemyOrderRepository`, `HttpRestaurantCatalog`). DI wiring happens in `api/dependencies.py`.
- **Settings**: Each service defines a Pydantic `BaseSettings` subclass with `FTGO_` env prefix. Settings are cached via `@lru_cache` in dependencies.
- **Database per service**: Each service has its own Postgres database (`order_db`, `kitchen_db`, `consumer_db`, `restaurant_db`) in the same Postgres instance. No shared tables.
- **Idempotency**: Order creation uses an `Idempotency-Key` header (in-memory cache, 1hr). Event consumers check `message_id` and aggregate state before acting.

### Shared Library (`libs/common/`)

Technical primitives only — no service-specific domain logic:
- `common.config` — `BaseServiceSettings` (pydantic-settings, `FTGO_` prefix)
- `common.db` — SQLAlchemy engine/session factories, declarative `Base`
- `common.api` — FastAPI app factory with `/health` endpoint
- `common.outbox` — `OutboxMessageRecord` ORM model, `OutboxRelay` (poll + publish)
- `common.messaging` — `MessagePublisher` (aio_pika, topic exchange, persistent delivery)

### Order State Machine

States: `PENDING` → `APPROVED` | `REJECTED` | `CANCELLED`. Transitions are methods on the `Order` domain model (`approve()`, `reject()`, `cancel()`). `APPROVED` orders can be cancelled; `REJECTED`/`CANCELLED` are terminal for their paths. Idempotent: calling `approve()` on an already-approved order is a no-op.

### Tests

- `tests/contract/` — contract tests
- `tests/integration/` — integration tests
- `tests/e2e/` — end-to-end tests
- Each service also has `src/tests/` for unit/domain tests
- pytest runs with `asyncio_mode = "auto"` and `--import-mode=importlib`

### Code Conventions

- Keep `libs/common/` limited to shared technical utilities
- Follow the DDD layering from `order-service`: domain models are plain Python dataclasses, repository/port abstractions use `Protocol`, ORM models live in `infrastructure/db/models.py`
- Use the transactional outbox pattern for cross-service events
- Document API and event contracts under `docs/contracts/` when behavior changes
- Prefer root-level `tests/e2e` pytest tests for verifying cross-service flows over ad hoc manual checks
