## Why

The FTGO frontend already covers the core learning journey, but the experience still feels utilitarian in places: users have to infer system state from sparse screens, repeated actions do not always feel guided, and operations/kitchen views can be harder to scan than they need to be. Enhancing the UI experience will make the demo easier to understand, teach, and manually verify without changing backend behavior.

## What Changes

- Improve the application shell so primary routes, active state, consumer context, and cart/order cues are easier to scan across desktop and mobile.
- Add richer empty, loading, error, and success states to consumer, restaurant, order, kitchen, and operations views.
- Improve responsive layouts for restaurant browsing, cart confirmation, order history, kitchen tickets, and operations query results.
- Add status-forward visual treatment for order and ticket lifecycles, including clearer grouping, timestamps or identifiers where useful, and next-action affordances.
- Preserve the existing DDD service boundaries: all behavior remains in the frontend and shared frontend helpers unless an existing API already exposes the needed data.
- No breaking API, event, or routing-key changes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `ftgo-frontend`: Strengthen application-level frontend requirements for responsive navigation, state presentation, and consistent route experiences.
- `frontend-ux-polish`: Add user-facing polish requirements for empty/loading/error/success states, mobile ergonomics, and operational scanability.

## Impact

- Affected code: `frontend/src/App.jsx`, `frontend/src/index.css`, frontend route pages under `frontend/src/pages/`, reusable components under `frontend/src/components/`, and frontend tests near changed components.
- Affected APIs: none expected; the frontend should continue using existing functions in `frontend/src/lib/api.js`.
- Affected services: only the React frontend scaffold under `frontend/`; no Python microservice internals are expected to change.
- `libs/common/`: no changes expected.
- Events, routing keys, and idempotency keys: no new events, routing keys, or idempotency keys.
- Cross-service flow: none introduced; this change improves presentation of existing API-backed flows.
