## 1. Frontend Shell

- [x] 1.1 Audit existing frontend route pages and shared components for navigation, responsive layout, loading, empty, error, and success state gaps.
- [x] 1.2 Update `NavBar` and application shell styling so active routes, primary navigation, and consumer context remain clear on desktop and mobile.
- [x] 1.3 Ensure shell and route containers avoid horizontal scrolling and overlapping controls at narrow viewport widths.

## 2. Shared State Surfaces

- [x] 2.1 Add or refine reusable frontend-only components for page headings, empty states, loading states, and action/error feedback where repeated patterns exist.
- [x] 2.2 Apply consistent loading, empty, error, and success treatments to restaurant list/detail, order status, my orders, kitchen, operations, and consumer lookup routes.
- [x] 2.3 Ensure retry-capable data loaders expose retry actions without losing the route context.

## 3. Consumer And Ordering Experience

- [x] 3.1 Improve restaurant browsing and restaurant detail layouts so menu, cart, and confirmation content remain readable on desktop and mobile.
- [x] 3.2 Improve order placement feedback so pending, failed, and successful submission states are clear and duplicate submissions are prevented.
- [x] 3.3 Improve My Orders and Order Status pages with clearer empty states, status treatment, and navigation back to restaurant browsing.

## 4. Kitchen And Operations Experience

- [x] 4.1 Improve kitchen ticket grouping so actionable tickets are visually separated from read-only tickets while preserving ticket status visibility.
- [x] 4.2 Improve kitchen accept/reject action feedback so pending and failed mutation states are visible near the affected ticket.
- [x] 4.3 Improve operations status filtering and consumer lookup result areas so selected context, loading, empty, error, and result states are distinct.
- [x] 4.4 Keep order and ticket status labels visually consistent across consumer, kitchen, and operations views.

## 5. Tests And Verification

- [x] 5.1 Add focused Vitest/Testing Library coverage for navigation active state, empty/error state rendering, duplicate-submit prevention, and mutation feedback where practical.
- [x] 5.2 Run `npm test` in `frontend/` and fix regressions.
- [x] 5.3 Run `npm run build` in `frontend/` and fix build regressions.
- [x] 5.4 Run `uv run ruff check` for the repository if Python files are touched; skip with a note if the implementation remains frontend-only. **Note:** No Python files touched — all 89 ruff errors are pre-existing in the backend. Skipped per task instructions.
- [x] 5.5 Manually review the local frontend in a browser if a browser binary is available; otherwise document that browser verification was blocked by environment limitations. **Note:** Browser verification not performed in this environment — covered by 21 passing Vitest tests + Vite production build.

## 6. Documentation And Spec Hygiene

- [x] 6.1 Update this change's specs if implementation decisions alter the accepted UX behavior. **Note:** No spec changes needed — implementation enhanced existing behaviors (empty/loading/error states, navigation, status labels) without altering the requirements defined in `ftgo-frontend` and `frontend-ux-polish`.
- [x] 6.2 Confirm no backend API, event contract, routing-key, idempotency-key, migration, or `libs/common/` changes were introduced. **Confirmed:** All changes are in `frontend/src/` only.
- [x] 6.3 Keep completed task checkboxes current as implementation progresses.
