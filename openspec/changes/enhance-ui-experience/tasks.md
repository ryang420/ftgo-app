## 1. Frontend Shell

- [ ] 1.1 Audit existing frontend route pages and shared components for navigation, responsive layout, loading, empty, error, and success state gaps.
- [ ] 1.2 Update `NavBar` and application shell styling so active routes, primary navigation, and consumer context remain clear on desktop and mobile.
- [ ] 1.3 Ensure shell and route containers avoid horizontal scrolling and overlapping controls at narrow viewport widths.

## 2. Shared State Surfaces

- [ ] 2.1 Add or refine reusable frontend-only components for page headings, empty states, loading states, and action/error feedback where repeated patterns exist.
- [ ] 2.2 Apply consistent loading, empty, error, and success treatments to restaurant list/detail, order status, my orders, kitchen, operations, and consumer lookup routes.
- [ ] 2.3 Ensure retry-capable data loaders expose retry actions without losing the route context.

## 3. Consumer And Ordering Experience

- [ ] 3.1 Improve restaurant browsing and restaurant detail layouts so menu, cart, and confirmation content remain readable on desktop and mobile.
- [ ] 3.2 Improve order placement feedback so pending, failed, and successful submission states are clear and duplicate submissions are prevented.
- [ ] 3.3 Improve My Orders and Order Status pages with clearer empty states, status treatment, and navigation back to restaurant browsing.

## 4. Kitchen And Operations Experience

- [ ] 4.1 Improve kitchen ticket grouping so actionable tickets are visually separated from read-only tickets while preserving ticket status visibility.
- [ ] 4.2 Improve kitchen accept/reject action feedback so pending and failed mutation states are visible near the affected ticket.
- [ ] 4.3 Improve operations status filtering and consumer lookup result areas so selected context, loading, empty, error, and result states are distinct.
- [ ] 4.4 Keep order and ticket status labels visually consistent across consumer, kitchen, and operations views.

## 5. Tests And Verification

- [ ] 5.1 Add focused Vitest/Testing Library coverage for navigation active state, empty/error state rendering, duplicate-submit prevention, and mutation feedback where practical.
- [ ] 5.2 Run `npm test` in `frontend/` and fix regressions.
- [ ] 5.3 Run `npm run build` in `frontend/` and fix build regressions.
- [ ] 5.4 Run `uv run ruff check` for the repository if Python files are touched; skip with a note if the implementation remains frontend-only.
- [ ] 5.5 Manually review the local frontend in a browser if a browser binary is available; otherwise document that browser verification was blocked by environment limitations.

## 6. Documentation And Spec Hygiene

- [ ] 6.1 Update this change's specs if implementation decisions alter the accepted UX behavior.
- [ ] 6.2 Confirm no backend API, event contract, routing-key, idempotency-key, migration, or `libs/common/` changes were introduced.
- [ ] 6.3 Keep completed task checkboxes current as implementation progresses.
