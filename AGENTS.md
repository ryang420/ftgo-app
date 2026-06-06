# AGENTS.md

## Project Context

- This repository is a Python-first FTGO microservices learning monorepo.
- Services live under `services/`; shared technical utilities live under `libs/common/`.
- `order-service` is the current reference implementation for DDD-style service structure.
- Local infrastructure is defined in `deploy/docker-compose/docker-compose.yml`.
- The main implemented flow is documented in `docs/use-cases/place-order.md`.

## Development Commands

- Use `uv` for Python workspace tasks.
- Run `make sync` after dependency changes.
- Start local Postgres and RabbitMQ with `make infra-up`.
- Run core migrations with `make migrate`.
- Start the core local stack with `make dev-up`; stop it with `make dev-down`.
- Verify the order flow with `make demo-place-order` or `make e2e-place-order`.
- Run individual services with the existing `make run-*` targets.

## Code Conventions

- Keep service internals aligned with the existing DDD layering:
  `api`, `application`, `domain`, and `infrastructure`.
- Keep `libs/common/` limited to shared technical utilities, not service-specific domain logic.
- Prefer repository and port/protocol patterns already used by `order-service`.
- Keep database writes that belong to one business operation inside one unit of work.
- Use the transactional outbox pattern for cross-service events.
- Keep API and event contracts documented under `docs/contracts/` when behavior changes.

## Spec Driven Development

- Treat `specs/` as the project spec workspace.
- Each feature spec lives at `specs/<feature-name>/` and should contain:
  `requirements.md`, `design.md`, and `tasks.md`.
- Use `requirements-first` flow:
  1. Draft or update `requirements.md` with user stories and acceptance criteria.
  2. Draft or update `design.md` only after requirements are clear.
  3. Draft or update `tasks.md` only after design is clear.
  4. Implement only from `tasks.md`, starting with the earliest unchecked task or dependency wave.
- Before implementing a feature, read all three spec files when present and identify blockers.
- If a spec has only `requirements.md`, do not implement it yet unless the user explicitly asks to skip the design/tasks stages.
- When behavior changes during implementation, update the relevant spec and contract docs in the same change.
- Keep task checkboxes current as work is completed.

## Testing And Quality

- Prefer `uv run pytest` for Python tests.
- Prefer `uv run ruff check` for linting.
- Add focused tests near the service being changed when touching application or domain behavior.
- For cross-service behavior, prefer the existing demo/e2e scripts over ad hoc manual checks.
