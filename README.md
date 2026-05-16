# FTGO Python Microservices Monorepo

This repository is a Python-first learning implementation of the FTGO case
study from _Microservice Patterns_.

## Goals

- Learn service decomposition around a realistic business domain
- Practice Python microservice engineering with FastAPI and SQLAlchemy
- Implement core distributed system patterns such as Saga, Outbox, and CQRS
- Keep the project approachable enough for iterative learning

## Repository Layout

- `services/`: runnable microservices and gateway
- `libs/common/`: shared technical utilities only
- `frontend/`: React + Tailwind CSS frontend scaffold
- `deploy/docker-compose/`: local infrastructure for development
- `docs/`: architecture notes, ADRs, APIs, and diagrams
- `tests/`: cross-service contract, integration, and end-to-end tests

## Initial Service Set

- `api-gateway`
- `consumer-service`
- `restaurant-service`
- `order-service`
- `kitchen-service`
- `delivery-service`
- `accounting-service`
- `order-query-service`

## Next Milestones

1. Define API and event contracts for consumer, restaurant, and order flows
2. Add a shared database bootstrap package and per-service migrations
3. Implement the first end-to-end order creation flow
4. Introduce Outbox publishing and Saga orchestration

## Frontend Bootstrap

The repository now includes a standalone React frontend scaffold under
`frontend/`.

```bash
cd frontend
npm install
npm run dev
```
