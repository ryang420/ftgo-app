# DDD Principles For FTGO Services

This repository uses a DDD-first service template.

## Dependency Direction

- `api` depends on `application`
- `application` depends on `domain`
- `domain` depends on nothing from `fastapi`, `sqlalchemy`, or message brokers
- `infrastructure` depends on `domain` and implements ports declared by `domain` or `application`

## Required Rules

- Domain entities and value objects must be plain Python objects
- Domain modules must not import ORM base classes, sessions, HTTP objects, or broker clients
- Application services must orchestrate use cases through repository or unit-of-work abstractions
- API schemas are transport DTOs and must not be passed directly into domain logic
- ORM models live under `infrastructure/db/models.py`
- Mapping between domain objects and persistence models lives in infrastructure
- Migrations must import infrastructure persistence models, not domain entities

## Recommended Service Layout

```text
service-name/
  src/app/
    api/
      dependencies.py
      routes/
    application/
      commands.py
      queries.py
      services.py
    domain/
      models.py
      repositories.py
      services.py
      events.py
    infrastructure/
      db/
        models.py
        mappers.py
        repositories.py
        session.py
      messaging/
```

## Current Reference Implementation

- `order-service` is the reference DDD sample in this repository
- New services should copy the dependency direction and repository adapter approach used there
- Existing services such as `consumer-service` and `restaurant-service` should be migrated toward the same pattern before their domains become more complex
