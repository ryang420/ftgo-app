# FTGO Python Monorepo Scaffold

## Service Design Rules

- One service, one bounded context, one deployment unit
- Each service keeps its own schema and migrations
- Cross-service communication uses HTTP or events, not shared tables
- Shared library contains technical primitives only

## Standard Service Layout

```text
service-name/
  pyproject.toml
  src/
    app/
      main.py
      api/
      application/
      domain/
      infrastructure/
      schemas/
    tests/
```

## Suggested Implementation Order

1. consumer-service
2. restaurant-service
3. order-service
4. api-gateway
5. accounting-service
6. kitchen-service
7. delivery-service
8. order-query-service

## Shared Library Boundaries

- `common.config`: configuration and settings
- `common.logging`: logging setup
- `common.messaging`: event envelope and broker abstractions
- `common.outbox`: outbox primitives
- `common.auth`: auth helpers
- `common.db`: SQLAlchemy bootstrap
- `common.observability`: tracing and metrics setup
- `common.testkit`: reusable test helpers
