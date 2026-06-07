# Implementation Plan: FTGO Frontend

## Overview

Expand the existing React + Vite + Tailwind frontend from restaurant-browsing-only to the full
FTGO learner journey. Implementation follows a layered approach: test infrastructure and pure
utilities first, then shared components, consumer identity, cart/ordering, order tracking,
kitchen dashboard, operations views, and finally the 404 fallback. All code is JavaScript (JSX
where React components). No new frameworks beyond the test stack listed below.

---

## Tasks

- [x] 1. Install test framework and configure Vitest
  - [x] 1.1 Add test dependencies to `frontend/package.json`
    - Add to `devDependencies`: `"vitest": "3.2.4"`, `"@testing-library/react": "16.3.0"`,
      `"@testing-library/user-event": "14.6.1"`, `"@testing-library/jest-dom": "6.6.3"`,
      `"@vitest/coverage-v8": "3.2.4"`, `"fast-check": "3.23.2"`, `"jsdom": "26.1.0"`
    - Add scripts: `"test": "vitest --run"` and `"test:watch": "vitest"`
    - _Requirements: 12.1 (test infrastructure for all pages)_
  - [x] 1.2 Create `frontend/vitest.config.js`
    - Set `test.environment` to `"jsdom"`, `test.globals` to `true`,
      `test.setupFiles` to `["./src/test/setup.js"]`
    - _Requirements: 12.1_
  - [x] 1.3 Create `frontend/src/test/setup.js`
    - Import `@testing-library/jest-dom` to extend Vitest matchers
    - _Requirements: 12.1_

- [x] 2. Implement pure library utilities
  - [x] 2.1 Create `frontend/src/lib/session.js`
    - Implement `readSession()`, `writeSession(session)`, `clearSession()` using
      `localStorage` key `"ftgo_consumer_session"`
    - UUID validation regex: `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i`
    - `readSession()` must clear malformed entries and return `null`
    - _Requirements: 1.2, 1.3, 1.4_
  - [ ]* 2.2 Write property tests for `session.js` (`frontend/src/lib/session.test.js`)
    - **Property 1: Malformed ConsumerSession always triggers null return**
    - **Property 2: Valid ConsumerSession always returns non-null**
    - **Validates: Requirements 1.2, 1.4**
    - Use `fc.string()`, `fc.uuid()`, and arbitrary objects as arbitrary inputs
  - [x] 2.3 Create `frontend/src/lib/cart.js`
    - Implement `addItem(cart, item)`, `removeItem(cart, menuItemId)`,
      `setQuantity(cart, menuItemId, qty)`, `cartTotal(cart)`,
      `isCartEmpty(cart)`, `clearCart()`
    - All functions are pure (no side-effects, no localStorage writes)
    - `setQuantity` with qty `0` behaves identically to `removeItem`
    - Quantity range enforcement: 1–99 (clamp or reject values outside range)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.8_
  - [ ]* 2.4 Write property tests for `cart.js` (`frontend/src/lib/cart.test.js`)
    - **Property 5: Cart total equals sum of all line totals**
    - **Property 6: Cart state is never written to localStorage**
    - **Validates: Requirements 3.2, 3.3, 3.4, 3.6**
    - Also test: `addItem` then `removeItem` returns a cart equal to the original;
      `setQuantity(0)` equals `removeItem`
  - [x] 2.5 Extend `frontend/src/lib/api.js` with 8 new functions
    - Add `createConsumer(data)`, `placeOrder(data)`, `getOrder(orderId, { signal })`,
      `getOrdersByConsumer(consumerId, { signal })`, `getOrdersByStatus(status, { signal })`,
      `getKitchenTickets({ signal })`, `acceptKitchenTicket(ticketId)`,
      `rejectKitchenTicket(ticketId)`
    - `acceptKitchenTicket` and `rejectKitchenTicket` must attach `.status` and `.body` to the
      thrown `Error` for 409 conflict handling
    - All POST functions must send `Content-Type: application/json`
    - Add `/kitchen` proxy entry to `frontend/vite.config.js`
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  - [ ]* 2.6 Write property tests for `api.js` (`frontend/src/lib/api.test.js`)
    - **Property 19: All API functions throw Error with HTTP status code for any non-2xx**
    - **Property 20: All POST API functions send Content-Type: application/json**
    - **Validates: Requirements 11.2, 11.4**
    - Mock `fetch` globally; iterate over status codes 400–599

- [x] 3. Build shared UI components
  - [x] 3.1 Create `frontend/src/components/StatusBadge.jsx`
    - Render a `<span>` with `rounded-full border px-3 py-1 text-xs font-medium` plus the
      per-status Tailwind classes defined in the design's colour mapping table
    - Fallback to `bg-stone-400/15 border-stone-300/20 text-stone-200` for unknown statuses
    - _Requirements: 5.2, 10.6_
  - [ ]* 3.2 Write property test for `StatusBadge` (`frontend/src/components/StatusBadge.test.jsx`)
    - **Property 9: StatusBadge applies correct colour class for every valid status**
    - **Validates: Requirements 5.2**
    - Use `fc.constantFrom("PENDING", "APPROVED", "PREPARING", "CANCELLED", "ACCEPTED", "CREATE_PENDING")`
  - [x] 3.3 Create `frontend/src/components/ErrorMessage.jsx`
    - Props: `message: string`, `onRetry?: () => void`
    - Render rose-tinted container with "Something went wrong." heading, message text, and
      optional Retry button
    - Message must always be a plain string (never render raw JSON)
    - _Requirements: 12.2, 12.3, 12.5_
  - [ ] 3.4 Write unit tests for `ErrorMessage` (`frontend/src/components/ErrorMessage.test.jsx`)
    - Test: renders message, renders Retry button only when `onRetry` provided,
      clicking Retry calls `onRetry`, never renders `[object Object]`
    - _Requirements: 12.2, 12.3, 12.5_
  - [x] 3.5 Create `frontend/src/components/LoadingSpinner.jsx`
    - Render accessible `<span role="status" aria-label="Loading">` with spin animation
    - _Requirements: 12.1_
  - [x] 3.6 Create `frontend/src/components/SkeletonBlock.jsx`
    - Props: `className?: string`
    - Render animate-pulse placeholder rectangle matching existing page skeleton patterns
    - _Requirements: 2.3, 12.1_
  - [x] 3.7 Create `frontend/src/components/OrderRow.jsx`
    - Props: `order: OrderSummary`, `onClick: () => void`
    - Export pure formatting utilities: `formatOrderDate(isoString)`, `formatAmount(amount, currency)`, `truncateId(id)`
    - `formatOrderDate` → `"YYYY-MM-DD HH:mm"` local timezone via `Intl.DateTimeFormat`
    - `formatAmount` → `"12.50 USD"` pattern
    - `truncateId` → first 8 characters
    - Render: truncated `order_id` with copy-to-clipboard button, `StatusBadge`, formatted
      `total_amount`, `restaurant_id`/`consumer_id`, formatted `created_at`
    - _Requirements: 6.2, 8.5, 9.2_
  - [ ]* 3.8 Write property test for `OrderRow` formatting (`frontend/src/components/OrderRow.test.jsx`)
    - **Property 13: Order row formatting functions are always correct**
    - **Validates: Requirements 6.2, 8.5**
    - Test `formatOrderDate`, `formatAmount`, `truncateId` against regex patterns
      `/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/`, `/^\d+\.\d{2} [A-Z]{3}$/`, exact 8-char output

- [x] 4. Implement consumer identity layer
  - [x] 4.1 Create `frontend/src/context/ConsumerSessionContext.jsx`
    - Export `ConsumerSessionContext` (`createContext(null)`) and `ConsumerSessionProvider`
    - Provider reads initial session from `readSession()` on mount
    - Expose `{ session, setSession, clearSession }` as context value
    - `setSession` writes to localStorage via `writeSession`, then updates state
    - `clearSession` removes from localStorage via `clearSession()`, then nulls state
    - _Requirements: 1.3, 1.4, 1.6_
  - [x] 4.2 Create `frontend/src/hooks/useConsumerSession.js`
    - Return `useContext(ConsumerSessionContext)`; throw if used outside provider
    - _Requirements: 1.4, 1.6_
  - [x] 4.3 Create `frontend/src/components/ConsumerSetupModal.jsx`
    - Render as a fixed full-screen overlay (modal) when `session === null`
    - First name and last name inputs (free-text, max 100 chars each)
    - On submit: call `createConsumer({ first_name, last_name, email })` with non-empty
      names and a generated unique email, persist 201 response `consumer_id` + display name
      via `setSession`, dismiss modal
    - If either name is blank, show an inline validation error and do not call `POST /consumers`
    - Show inline error below submit button on non-2xx; keep modal visible and re-enable button
    - Disable submit + show `LoadingSpinner` while request is in-flight
    - _Requirements: 1.1, 1.3, 1.5, 1.7_
  - [ ]* 4.4 Write property tests for `ConsumerSetupModal` (`frontend/src/components/ConsumerSetupModal.test.jsx`)
    - **Property 3: POST /consumers non-2xx always keeps form visible with error**
    - **Validates: Requirements 1.5**
    - Use `fc.integer({ min: 400, max: 599 })` to parameterise status codes
    - Also write unit tests for: form displays on null session (1.1), loading state (1.7)
  - [x] 4.5 Create `frontend/src/components/NavBar.jsx`
    - Four `NavLink` elements with active-state class callback:
      active → `border-b border-orange-400 text-orange-300`,
      inactive → `text-stone-300 hover:text-white`
    - Links: Restaurant List (`/`), My Orders (`/my-orders`), Kitchen (`/kitchen`), Operations (`/operations`)
    - "Change consumer" button that calls `clearSession()` from context
    - _Requirements: 1.6, 10.1, 10.2, 10.3, 10.4_
  - [x] 4.6 Update `frontend/src/main.jsx` — wrap `<App />` with `<ConsumerSessionProvider>`
    - Import and wrap: `<BrowserRouter><ConsumerSessionProvider><App /></ConsumerSessionProvider></BrowserRouter>`
    - _Requirements: 1.3, 1.4_
  - [x] 4.7 Update `frontend/src/App.jsx` — add all routes, NavBar, and ConsumerSetupModal
    - Import and render `<NavBar />` above `<Routes>`
    - Render `{!session && <ConsumerSetupModal />}` after NavBar
    - Add routes in this order: `/orders/by-consumer`, `/orders/:orderId`, `/my-orders`,
      `/kitchen`, `/operations`, `/restaurants/:restaurantId`, `/`, `*` (NotFoundPage)
    - Replace the existing `<Navigate to="/" replace />` catch-all with `<NotFoundPage />`
    - _Requirements: 10.1, 10.2, 10.5_

- [x] 5. Implement Restaurant detail augmentation and cart
  - [x] 5.1 Augment `frontend/src/components/MenuItemCard.jsx` — add "Add to cart" button
    - Accept new props: `onAddToCart: (item) => void`, `sessionExists: boolean`
    - Render enabled "Add to cart" button when `sessionExists === true`
    - Render disabled "Add to cart" button when `sessionExists === false`
    - _Requirements: 2.2, 2.5, 2.6_
  - [ ]* 5.2 Write property test for `MenuItemCard` price formatting
    - **Property 4: Price formatting always produces exactly 2 decimal places**
    - **Validates: Requirements 2.2**
    - Use `fc.float({ min: 0, max: 100000, noNaN: true })` to test formatting output
  - [x] 5.3 Create `frontend/src/components/CartItemRow.jsx`
    - Props: `item: CartItem`, `onRemove: (menuItemId) => void`,
      `onQuantityChange: (menuItemId, qty) => void`
    - Render item name, quantity controls (+/−), unit price, line total
    - Reject quantity inputs outside 1–99; restore previous value and show inline error
    - _Requirements: 3.2, 3.3, 3.8_
  - [x] 5.4 Create `frontend/src/components/CartPanel.jsx`
    - Props: `cart: CartState`, `onRemove`, `onQuantityChange`, `onPlaceOrder: () => void`
    - Render CartItemRow list, overall total via `cartTotal()`, "Place order" button
    - Disable "Place order" + show "Cart is empty — add at least one item" when cart is empty
    - Always visible on restaurant detail page (empty state when no items)
    - _Requirements: 3.2, 3.4, 3.7_
  - [x] 5.5 Create `frontend/src/components/OrderConfirmationDrawer.jsx`
    - Props: `cart: CartState`, `restaurantName: string`, `consumerId: string`,
      `restaurantId: string`, `onClose: () => void`, `onOrderPlaced: (orderId) => void`
    - Delivery address input (required, max 500 chars); validate on submit
    - Summary: restaurant name, each item name + quantity, total item count
    - On submit: call `placeOrder({ consumer_id, restaurant_id, currency: "USD", delivery_address, line_items })`
    - On 201: call `onOrderPlaced(order_id)` (parent navigates to `/orders/:orderId`)
    - On non-2xx or network error: show error message within drawer, re-enable submit button
    - Disable submit + show `LoadingSpinner` while in-flight
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  - [ ]* 5.6 Write property tests for `OrderConfirmationDrawer` (`frontend/src/pages/RestaurantDetailPage.test.jsx`)
    - **Property 7: POST /orders payload is correctly shaped for all valid inputs**
    - **Property 8: POST /orders non-2xx always keeps the order form submittable**
    - **Validates: Requirements 4.2, 4.4**
    - Use `fc.uuid()`, `fc.string()`, and `fc.array(...)` for cart items
  - [x] 5.7 Augment `frontend/src/pages/RestaurantDetailPage.jsx` — wire cart state
    - Add `cart` state via `useState({ restaurantId, items: [] })` using `lib/cart.js`
    - Pass `onAddToCart` and `sessionExists` to each `MenuItemCard`
    - Render `<CartPanel>` next to the menu list
    - Handle cross-restaurant navigation warning with `useBlocker` (or manual pendingNav ref)
    - Render `<OrderConfirmationDrawer>` when user clicks "Place order"
    - On order placed: `setCart(clearCart())`, `navigate("/orders/" + orderId)`
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6, 4.1, 4.3_

- [x] 6. Implement order tracking pages
  - [x] 6.1 Create `frontend/src/hooks/useOrderPolling.js`
    - Accept `orderId` param; encapsulate `setInterval` + `AbortController` polling logic
    - Return `{ order, status, transientError, dismissTransientError }`
    - Poll every 5000 ms; stop on terminal status `PREPARING` or `CANCELLED`
    - Stop on 404; keep polling on other non-2xx (set transient error)
    - Clean up interval and abort in-flight request on unmount
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 5.7_
  - [ ]* 6.2 Write property tests for `useOrderPolling` (`frontend/src/pages/OrderStatusPage.test.jsx`)
    - **Property 10: Polling is active during PENDING and APPROVED statuses**
    - **Property 11: Polling stops immediately on any terminal status**
    - **Property 12: Unmount always cancels polling and in-flight requests**
    - **Validates: Requirements 5.3, 5.4, 5.7**
    - Use Vitest fake timers (`vi.useFakeTimers()`) and mocked `fetch`
  - [x] 6.3 Create `frontend/src/pages/OrderStatusPage.jsx`
    - Consume `useOrderPolling(orderId)` from `useParams()`
    - Display: `order_id`, `StatusBadge`, `restaurant_id`, `total_amount`, `delivery_address`,
      `created_at`, `line_items`
    - Show "Your order is being prepared" when status is `PREPARING`
    - Show "Your order has been cancelled" when status is `CANCELLED`
    - Show `LoadingSpinner` / skeleton on initial load
    - Show `ErrorMessage` for errors; "Order not found" specifically for 404
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  - [x] 6.4 Create `frontend/src/pages/MyOrdersPage.jsx`
    - Redirect to `/` (which shows `ConsumerSetupModal`) when `session === null`
    - Call `getOrdersByConsumer(session.consumer_id)` on mount
    - Display `OrderRow` list; "No orders yet" when empty array
    - Clicking row navigates to `/orders/:orderId`
    - Show `SkeletonBlock` while loading; `ErrorMessage` with retry on non-2xx
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  - [ ] 6.5 Write unit tests for `MyOrdersPage` (`frontend/src/pages/MyOrdersPage.test.jsx`)
    - Test: redirects when no session, loading state, empty array message, error + retry,
      row click navigates correctly
    - _Requirements: 6.4, 6.5, 6.6_

- [x] 7. Implement Kitchen Dashboard
  - [x] 7.1 Create `frontend/src/pages/KitchenDashboardPage.jsx`
    - Fetch `GET /kitchen/tickets` on mount; show `LoadingSpinner` during fetch
    - Derive `actionableTickets` (status `CREATE_PENDING`) and `readOnlyTickets`
      at render time from single `tickets` state array — no secondary state
    - Render Accept + Reject buttons for actionable tickets; none for read-only
    - Accept click: add to `pendingTickets` Set, POST accept, on 200 update status in
      `tickets` array to `ACCEPTED`, remove from pending
    - Reject click: same pattern, update to `CANCELLED`
    - 409 response: set inline per-row error with `current_status` + `target_status`
    - Other non-2xx: show dismissible global error banner, re-enable buttons
    - Show "No tickets at the moment" in actionable section when array is empty
    - Provide manual "Refresh" button that re-fetches and replaces full list
    - Show `ErrorMessage` with retry if `GET /kitchen/tickets` fails
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10_
  - [ ]* 7.2 Write property tests for `KitchenDashboardPage` (`frontend/src/pages/KitchenDashboardPage.test.jsx`)
    - **Property 14: Ticket section assignment is correct for any mixture of ticket statuses**
    - **Property 15: Accept and Reject actions correctly transition ticket status and section**
    - **Property 16: 409 conflict error always displays both status fields**
    - **Validates: Requirements 7.2, 7.3, 7.4, 7.5**
    - Use `fc.array(fc.record({ id: fc.uuid(), status: fc.constantFrom("CREATE_PENDING", "ACCEPTED", "CANCELLED") }))`
  - [ ] 7.3 Write unit tests for `KitchenDashboardPage` (`frontend/src/pages/KitchenDashboardPage.test.jsx`)
    - Test: loading state, error + retry, empty list message, Refresh button, in-flight
      button disabling (7.7), global banner on non-409 error
    - _Requirements: 7.1, 7.6, 7.7, 7.8, 7.9, 7.10_

- [x] 8. Implement Operations and Consumer Lookup pages
  - [x] 8.1 Create `frontend/src/pages/OperationsPage.jsx`
    - Default status filter `PENDING`; fetch `GET /orders?status=PENDING` on mount
    - Render four-option filter control: `PENDING`, `APPROVED`, `PREPARING`, `CANCELLED`
    - On filter change: re-fetch `GET /orders?status={newStatus}`, replace list
    - Show `LoadingSpinner` in results area during fetch
    - Render `OrderRow` list; "No orders with this status" when empty
    - Clicking row navigates to `/orders/:orderId`
    - Show `ErrorMessage` with retry on non-2xx
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  - [ ]* 8.2 Write property test for `OperationsPage` (`frontend/src/pages/OperationsPage.test.jsx`)
    - **Property 17: Status filter fetch uses the correct status parameter for all four values**
    - **Validates: Requirements 8.3**
    - Intercept `fetch` and assert URL equals `/orders?status={selectedStatus}`
  - [ ] 8.3 Write unit tests for `OperationsPage` (`frontend/src/pages/OperationsPage.test.jsx`)
    - Test: defaults to PENDING, loading indicator, empty message, error + retry, row click
    - _Requirements: 8.1, 8.4, 8.7, 8.8_
  - [x] 8.4 Create `frontend/src/pages/ConsumerLookupPage.jsx`
    - UUID input field + submit button; validate RFC 4122 format before fetching
    - Show "Please enter a valid UUID" inline error and suppress fetch on invalid input
    - On valid submit: call `getOrdersByConsumer(uuid)` and display `OrderRow` list
    - "No orders found for this consumer" when empty array
    - On non-2xx: show error, keep field enabled with last-entered value preserved
    - Show `LoadingSpinner` while fetch is in-flight
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  - [ ]* 8.5 Write property test for `ConsumerLookupPage` (`frontend/src/pages/ConsumerLookupPage.test.jsx`)
    - **Property 18: UUID validation rejects all non-RFC-4122 strings and accepts all valid ones**
    - **Validates: Requirements 9.3**
    - Use `fc.string()` for invalid inputs and `fc.uuid()` for valid inputs
  - [ ] 8.6 Write unit tests for `ConsumerLookupPage` (`frontend/src/pages/ConsumerLookupPage.test.jsx`)
    - Test: initial empty form, loading state, empty results message, non-2xx error preserves
      field value
    - _Requirements: 9.1, 9.4, 9.5_

- [x] 9. Add NotFoundPage and final integration
  - [x] 9.1 Create `frontend/src/pages/NotFoundPage.jsx`
    - Render "Page not found" message and a `Link` back to `/`
    - Apply dark stone/orange palette consistent with all other pages
    - _Requirements: 10.5, 10.6_
  - [ ]* 9.2 Write property test for `ErrorMessage` raw-JSON guard (`frontend/src/components/ErrorMessage.test.jsx`)
    - **Property 21: Error display text is always a plain string, never raw JSON**
    - **Validates: Requirements 12.5**
    - Use `fc.anything()` serialised via `JSON.stringify`; assert rendered text never matches
      `/^\[object Object\]/` or `/^\[.*\]$/`

- [x] 10. Final checkpoint — Ensure all tests pass
  - Run `cd frontend && npm run test` (or `npx vitest --run`) and confirm all test suites pass.
  - Fix any failures before marking this task complete.
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery.
- Non-optional test sub-tasks (unit tests without `*`) MUST be implemented.
- All code is JavaScript / JSX — the design uses a specific language (not pseudocode), so no
  language prompt is needed.
- Each task references specific requirements for traceability.
- Property tests use fast-check `fc.assert` with a minimum of 100 iterations.
- Each property test must include the comment annotation:
  `// Feature: ftgo-frontend, Property N: <property_text>`
- The `/orders/by-consumer` route MUST be declared before `/orders/:orderId` in `App.jsx`.
- `acceptKitchenTicket` / `rejectKitchenTicket` enrich thrown `Error` objects with `.status`
  and `.body` for 409 conflict handling — callers must check `err.status === 409`.
- Cart state is never persisted; only `ConsumerSession` goes to localStorage.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1", "2.3", "2.5"] },
    { "id": 2, "tasks": ["2.2", "2.4", "2.6", "3.1", "3.3", "3.5", "3.6", "3.7"] },
    { "id": 3, "tasks": ["3.2", "3.4", "3.8", "4.1"] },
    { "id": 4, "tasks": ["4.2", "4.3"] },
    { "id": 5, "tasks": ["4.4", "4.5", "4.6"] },
    { "id": 6, "tasks": ["4.7", "5.1", "5.3"] },
    { "id": 7, "tasks": ["5.2", "5.4"] },
    { "id": 8, "tasks": ["5.5", "6.1"] },
    { "id": 9, "tasks": ["5.6", "5.7", "6.2", "6.3"] },
    { "id": 10, "tasks": ["6.4", "7.1", "8.1", "8.4"] },
    { "id": 11, "tasks": ["6.5", "7.2", "7.3", "8.2", "8.3", "8.5", "8.6", "9.1"] },
    { "id": 12, "tasks": ["9.2"] }
  ]
}
```
