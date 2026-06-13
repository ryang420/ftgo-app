## Context

The FTGO frontend is a React + Vite + Tailwind single-page application. It already supports consumer setup, restaurant browsing, cart management, order placement, order tracking, kitchen ticket actions, and operations queries. The current implementation has useful route pages and shared components, but the visual hierarchy, route state feedback, empty states, and mobile ergonomics are still lightweight.

This change is frontend-local. It should not alter the Python microservice DDD layering, domain models, repositories, outbox relay, RabbitMQ events, or `libs/common/`. Existing service APIs remain the integration boundary through `frontend/src/lib/api.js`.

## Goals / Non-Goals

**Goals:**

- Make the main application shell easier to understand through clearer navigation, active state, consumer identity, and route context.
- Improve state communication across loading, empty, error, and success paths.
- Make consumer, kitchen, and operations workflows easier to scan and operate on desktop and mobile.
- Reuse existing frontend component patterns and API client functions.
- Add focused frontend tests for behavior that can regress without visual inspection.

**Non-Goals:**

- No backend API changes.
- No database, migration, outbox, RabbitMQ, or event contract changes.
- No new external frontend dependencies unless implementation reveals a strong need.
- No redesign that turns the learning app into a marketing page or changes the core FTGO flow.

## Decisions

### Keep the change inside the frontend boundary

The implementation should update `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/App.jsx`, `frontend/src/index.css`, and nearby frontend tests. Backend services continue to expose the same API contracts.

Alternative considered: add backend response fields to power richer UI. This is deferred because the requested experience improvements can be achieved using existing order, restaurant, consumer, and ticket payloads.

### Promote reusable UI states instead of page-specific one-offs

Loading, empty, error, and success treatments should be made consistent through existing shared components such as `LoadingSpinner`, `ErrorMessage`, `StatusBadge`, `OrderRow`, and any small new frontend-only components that emerge from repeated patterns.

Alternative considered: style each route independently. That would be fast initially but would make the demo less consistent and harder to maintain.

### Preserve route-level workflows while improving scanability

Restaurant browsing, order history, order status, kitchen dashboard, operations status filters, and consumer lookup should keep their existing routes and API calls. The polish should improve headings, grouping, affordances, responsive grids, form states, and action placement.

Alternative considered: consolidate operations and kitchen into a single admin surface. That would change the information architecture beyond the requested UI enhancement.

### Treat mobile as a first-class layout

The implementation should avoid horizontal overflow, cramped controls, and sticky elements that obscure content on small screens. Toolbars and filters should wrap or stack predictably, and action buttons should remain reachable.

Alternative considered: optimize only the desktop learning-demo experience. This would keep the fastest path but would leave common local testing and teaching scenarios awkward on small screens.

## Service Impact

| Area | Domain | Application | API/consumer | Infrastructure |
| --- | --- | --- | --- | --- |
| `frontend/` | Not applicable | React route/component state and presentation only | Continue consuming existing API client functions in `frontend/src/lib/api.js` | Vite/Tailwind build and tests only |
| `consumer-service` | No change | No change | No change | No change |
| `restaurant-service` | No change | No change | No change | No change |
| `order-service` | No change | No change | No change | No change |
| `kitchen-service` | No change | No change | No change | No change |
| `api-gateway` | No change | No change | No change | No change |
| `libs/common/` | No change | No change | No change | No change |

## Error Handling

| UI route or handler | Existing failure source | Required user-facing behavior |
| --- | --- | --- |
| Restaurant list/detail loaders | Restaurant API request failure | Show a readable error state with retry where the page can refetch. |
| Cart/order confirmation | Order creation failure | Keep the confirmation form open, preserve entered address and cart state, and allow retry. |
| Order status/history loaders | Order API request failure | Show a readable error state with retry or navigation back to a stable route. |
| Kitchen ticket actions | Kitchen API request or mutation failure | Keep the ticket visible, show the failure near the affected action area, and allow retry. |
| Operations status/consumer queries | Order query failure or empty result | Distinguish empty results from errors and keep filter/query controls usable. |

## Events And Contracts

No new events, routing keys, idempotency keys, or outbox payloads are introduced.

Existing event payload shapes remain owned by the backend services and documented contract files. This change only changes how existing API data is presented in the frontend.

## Correctness Properties

- Navigation shows the active route and remains usable at desktop and mobile widths.
- Each data-backed page has distinct loading, error, empty, and success states.
- Mutating actions never hide retry paths after failure.
- Existing API calls continue to flow through `frontend/src/lib/api.js`; route components do not introduce direct `fetch` calls.
- Cart, consumer session, order polling, ticket action, and operations filtering behavior remains compatible with the current `ftgo-frontend` requirements.
- Frontend tests cover critical interaction behavior where state changes are not obvious from static rendering.

## Risks / Trade-offs

- Visual polish can drift into broad redesign → Keep changes tied to specified route states, scanability, and responsive behavior.
- Component extraction can create premature abstraction → Extract only repeated UI state patterns or shared route chrome.
- Browser-level visual verification may be limited by local environment browser availability → Use Vitest/component tests for behavior and run build/lint checks; use browser testing only if a browser binary is available.
- Empty or sparse backend seed data can make UI states hard to validate manually → Ensure empty states are explicit and testable without relying on full infrastructure.

## Migration Plan

1. Implement frontend-only changes behind existing routes and API calls.
2. Run focused frontend tests and build checks.
3. Roll back by reverting frontend component/page changes; no data migration or backend rollback is required.

## Open Questions

- Should the implementation add visual regression tooling later, or keep verification to component tests and manual local browser review for now?
- Should operations and kitchen scanability use compact table-like rows or enriched cards on desktop? The default implementation should follow existing component style and choose the denser layout where repeated operational scanning matters.
