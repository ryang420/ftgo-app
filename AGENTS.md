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
- Verify service behavior with pytest, for example `uv run pytest tests/e2e`.
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

- Treat `openspec/` as the project spec workspace.
- Active feature work lives under `openspec/changes/<change-name>/`.
- Current accepted capabilities live under `openspec/specs/`.
- For active changes, use OpenSpec's proposal-first flow:
  1. Draft or update `proposal.md` with motivation, behavior, and acceptance criteria.
  2. Draft or update `design.md` only after the proposal is clear.
  3. Draft or update `tasks.md` only after design is clear.
  4. Implement only from `tasks.md`, starting with the earliest unchecked task or dependency wave.
- Before implementing a change, read all available files in its `openspec/changes/<change-name>/` folder and identify blockers.
- If a change has only `proposal.md`, do not implement it yet unless the user explicitly asks to skip the design/tasks stages.
- When behavior changes during implementation, update the relevant OpenSpec change and contract docs in the same change.
- Keep task checkboxes current as work is completed.

## Testing And Quality

- Prefer `uv run pytest` for Python tests.
- Prefer `uv run ruff check` for linting.
- Add focused tests near the service being changed when touching application or domain behavior.
- For cross-service behavior, prefer root-level `tests/e2e` pytest tests over ad hoc manual checks.
