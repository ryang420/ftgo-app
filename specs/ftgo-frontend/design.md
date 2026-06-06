# Design Document — FTGO Frontend

## Overview

This document covers the full technical design for expanding the FTGO React frontend from its
current restaurant-browsing-only state to the complete learner journey: consumer identity, cart
management, order placement, order tracking, kitchen ticket management, and operations order
queries.

The implementation is an in-place extension of the existing codebase. No new frameworks, state
management libraries, or build tools are introduced. All new patterns follow those already
established in `RestaurantListPage.jsx` and `RestaurantDetailPage.jsx`.

**Stack recap**: React 18, react-router-dom v6, Tailwind CSS v3, Vite 5, plain React state +
localStorage, no Redux.

---

## Architecture

### High-Level Data Flow

```
Browser
  └─ React SPA (Vite dev-server, port 5173)
       ├─ React Router v6 — client-side routing
       ├─ ConsumerSession — localStorage singleton (read/write via useConsumerSession hook)
       ├─ Cart state — local React state lifted into RestaurantDetailPage
       ├─ lib/api.js — all fetch calls (no component ever calls fetch directly)
       └─ Vite proxy ─→ API Gateway (localhost:8000)
            ├─ /restaurants  ─→ restaurant-service
            ├─ /consumers    ─→ consumer-service
            ├─ /orders       ─→ order-service (write) / order-query-service (read)
            └─ /kitchen      ─→ kitchen-service
```

### Page/Route Map

| Route | Page Component | Primary API calls |
|---|---|---|
| `/` | `RestaurantListPage` | `GET /restaurants` |
| `/restaurants/:restaurantId` | `RestaurantDetailPage` | `GET /restaurants/:id`, `GET /restaurants/:id/menu-items` |
| `/orders/:orderId` | `OrderStatusPage` | `GET /orders/:id` (polling) |
| `/my-orders` | `MyOrdersPage` | `GET /orders?consumer_id=` |
| `/kitchen` | `KitchenDashboardPage` | `GET /kitchen/tickets`, `POST /kitchen/tickets/:id/accept|reject` |
| `/operations` | `OperationsPage` | `GET /orders?status=` |
| `/orders/by-consumer` | `ConsumerLookupPage` | `GET /orders?consumer_id=` |

> **Route ordering note**: `/orders/by-consumer` must be declared **before** `/orders/:orderId`
> in the router definition so react-router-dom matches the literal segment first.

---

## Components and Interfaces

### Component Hierarchy

```
main.jsx
└─ BrowserRouter
   └─ ConsumerSessionProvider           (context — provides session + setSession)
      └─ App
         ├─ NavBar                       (persistent, all routes)
         │   ├─ NavLink (/)
         │   ├─ NavLink (/my-orders)
         │   ├─ NavLink (/kitchen)
         │   ├─ NavLink (/operations)
         │   └─ "Change consumer" button
         └─ Routes
              ├─ /                        → RestaurantListPage
              │     └─ RestaurantCard[]
              ├─ /restaurants/:id         → RestaurantDetailPage (augmented)
              │     ├─ MenuItemCard[]     (with "Add to cart" button)
              │     └─ CartPanel
              │          └─ CartItemRow[]
              ├─ /orders/:orderId         → OrderStatusPage
              │     └─ StatusBadge
              ├─ /my-orders              → MyOrdersPage
              │     └─ OrderRow[]
              │          └─ StatusBadge
              ├─ /kitchen                → KitchenDashboardPage
              │     ├─ KitchenTicketRow[] (actionable)
              │     └─ KitchenTicketRow[] (read-only)
              ├─ /operations             → OperationsPage
              │     └─ OrderRow[]
              │          └─ StatusBadge
              └─ /orders/by-consumer     → ConsumerLookupPage
                    └─ OrderRow[]
                         └─ StatusBadge
```

### Shared Components

#### `NavBar`
Props: none (reads session from context)

Renders a top navigation bar on every route. Contains four `NavLink` elements using
react-router-dom's `NavLink` component, which accepts a `className` callback to apply active
styling. Also renders the "Change consumer" button.

```jsx
// Active-state class pattern (react-router-dom v6)
<NavLink
  to="/my-orders"
  className={({ isActive }) =>
    isActive
      ? "border-b border-orange-400 text-orange-300"
      : "text-stone-300 hover:text-white"
  }
>
  My Orders
</NavLink>
```

#### `StatusBadge`
Props: `status: string`

Renders a coloured pill for an `OrderStatus` or `KitchenTicketStatus` value.

| Status | Tailwind classes |
|---|---|
| `PENDING` | `bg-amber-400/15 border-amber-300/20 text-amber-100` |
| `APPROVED` | `bg-blue-400/15 border-blue-300/20 text-blue-100` |
| `PREPARING` | `bg-orange-400/15 border-orange-300/20 text-orange-100` |
| `CANCELLED` | `bg-rose-500/10 border-rose-300/20 text-rose-100` |
| `ACCEPTED` | `bg-green-500/10 border-green-300/20 text-green-100` |
| `CREATE_PENDING` | `bg-stone-400/15 border-stone-300/20 text-stone-100` |
| fallback | `bg-stone-400/15 border-stone-300/20 text-stone-200` |

```jsx
const STATUS_CLASSES = {
  PENDING:        "bg-amber-400/15 border-amber-300/20 text-amber-100",
  APPROVED:       "bg-blue-400/15 border-blue-300/20 text-blue-100",
  PREPARING:      "bg-orange-400/15 border-orange-300/20 text-orange-100",
  CANCELLED:      "bg-rose-500/10 border-rose-300/20 text-rose-100",
  ACCEPTED:       "bg-green-500/10 border-green-300/20 text-green-100",
  CREATE_PENDING: "bg-stone-400/15 border-stone-300/20 text-stone-100",
};

function StatusBadge({ status }) {
  const cls = STATUS_CLASSES[status] ?? "bg-stone-400/15 border-stone-300/20 text-stone-200";
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}
```

#### `LoadingSpinner`
Props: none

A simple accessible spinner for inline use (inside buttons) and standalone use on pages.

```jsx
function LoadingSpinner() {
  return (
    <span
      role="status"
      aria-label="Loading"
      className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-orange-400 border-t-transparent"
    />
  );
}
```

#### `SkeletonBlock`
Props: `className?: string`

A pulsing placeholder rectangle for page-level skeleton loading states, matching the pattern
used in the existing pages.

```jsx
function SkeletonBlock({ className = "" }) {
  return (
    <div
      className={`animate-pulse rounded-[1.5rem] border border-white/10 bg-white/[0.045] ${className}`}
    />
  );
}
```

#### `ErrorMessage`
Props: `message: string, onRetry?: () => void`

Consistent error display for all pages. Shows the message string and, when `onRetry` is
provided, a "Retry" button.

```jsx
function ErrorMessage({ message, onRetry }) {
  return (
    <div className="rounded-[1.75rem] border border-rose-300/20 bg-rose-500/10 p-6 text-sm leading-7 text-rose-100">
      <p className="font-medium">Something went wrong.</p>
      <p className="mt-2">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 rounded-full border border-rose-300/20 bg-rose-500/10 px-4 py-2 text-xs hover:bg-rose-500/20"
        >
          Retry
        </button>
      )}
    </div>
  );
}
```

#### `OrderRow`
Props: `order: OrderSummary, onClick: () => void`

Shared row component used in `MyOrdersPage`, `OperationsPage`, and `ConsumerLookupPage`.
Formats and displays: truncated `order_id` (8 chars + copy button), `StatusBadge`, formatted
`total_amount`, `restaurant_id` (or `consumer_id` depending on context), and formatted
`created_at`.

Internal formatting utilities (pure functions, exported for testing):
- `formatOrderDate(isoString)` → `"YYYY-MM-DD HH:mm"` in local timezone using `Intl.DateTimeFormat`
- `formatAmount(amount, currency)` → `"12.50 USD"`
- `truncateId(id)` → first 8 characters

---

## Data Models

### ConsumerSession

Stored in `localStorage` under the key `"ftgo_consumer_session"`.

```ts
interface ConsumerSession {
  consumer_id: string;  // RFC 4122 UUID
  display_name: string; // may be empty string
}
```

Validation rule: `consumer_id` must match `/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i`

Utility functions in `lib/session.js`:
- `readSession()` → `ConsumerSession | null` — reads, validates, and returns session or null (clearing if malformed)
- `writeSession(session)` → `void` — serialises to localStorage
- `clearSession()` → `void` — removes the key

### Cart State

Kept in React `useState` inside `RestaurantDetailPage`.

```ts
interface CartItem {
  menu_item_id: string;
  name: string;
  unit_price: number;  // numeric, as returned by API
  quantity: number;    // 1–99 inclusive
}

interface CartState {
  restaurantId: string | null;
  items: CartItem[];
}
```

Cart operations (pure functions, exported for testing, in `lib/cart.js`):
- `addItem(cart, item)` → `CartState` — adds item or increments quantity
- `removeItem(cart, menuItemId)` → `CartState` — removes item entry
- `setQuantity(cart, menuItemId, qty)` → `CartState` — sets quantity (1–99) or removes if 0
- `cartTotal(cart)` → `number` — sum of `unit_price × quantity` for all items
- `isCartEmpty(cart)` → `boolean`
- `clearCart()` → `CartState` — returns an empty cart state

### API Response Types (for documentation clarity)

```ts
interface OrderSummary {
  order_id: string;
  consumer_id: string;
  restaurant_id: string;
  status: "PENDING" | "APPROVED" | "PREPARING" | "CANCELLED";
  currency: string;
  total_amount: string;  // decimal string, e.g. "12.50"
  delivery_address: string;
  created_at: string;    // ISO 8601
  updated_at: string;
  line_items: Array<{ menu_item_id: string; quantity: number; price?: string }>;
}

interface KitchenTicket {
  id: string;
  order_id: string;
  restaurant_id: string;
  status: "CREATE_PENDING" | "ACCEPTED" | "CANCELLED";
  line_items: Array<{ menu_item_id: string; quantity: number }>;
}
```

---

## State Management Approach

No external state library is used. State lives at the appropriate component scope:

| Concern | Location | Mechanism |
|---|---|---|
| Consumer identity | `ConsumerSessionContext` (React context) | `useState` + `localStorage` via `lib/session.js` |
| Cart | `RestaurantDetailPage` local state | `useState` with `lib/cart.js` pure functions |
| Page fetch state | Each page component | `useState` (`status`, `data`, `error`) |
| Kitchen ticket list | `KitchenDashboardPage` local state | `useState` + optimistic updates |
| Operations status filter | `OperationsPage` local state | `useState` |

### ConsumerSession Context

`ConsumerSessionContext` is provided at the root (wrapping all routes). It exposes:

```jsx
const ConsumerSessionContext = createContext(null);

// Value shape
{
  session: ConsumerSession | null,
  setSession: (s: ConsumerSession) => void,
  clearSession: () => void,
}
```

`main.jsx` wraps `<App />` with `<ConsumerSessionProvider>`. The provider reads the initial
session from `lib/session.js` on mount. `NavBar` reads `session` to conditionally show the
"Change consumer" button label. All pages that need `consumer_id` call `useContext(ConsumerSessionContext)`.

---

## Routing Architecture

Updated `App.jsx`:

```jsx
import { Navigate, Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import RestaurantListPage from "./pages/RestaurantListPage.jsx";
import RestaurantDetailPage from "./pages/RestaurantDetailPage.jsx";
import OrderStatusPage from "./pages/OrderStatusPage.jsx";
import MyOrdersPage from "./pages/MyOrdersPage.jsx";
import KitchenDashboardPage from "./pages/KitchenDashboardPage.jsx";
import OperationsPage from "./pages/OperationsPage.jsx";
import ConsumerLookupPage from "./pages/ConsumerLookupPage.jsx";
import ConsumerSetupModal from "./components/ConsumerSetupModal.jsx";
import { useConsumerSession } from "./hooks/useConsumerSession.js";

function App() {
  const { session } = useConsumerSession();

  return (
    <>
      <NavBar />
      {!session && <ConsumerSetupModal />}
      <Routes>
        {/* Literal segment before dynamic :orderId */}
        <Route path="/orders/by-consumer" element={<ConsumerLookupPage />} />
        <Route path="/orders/:orderId" element={<OrderStatusPage />} />
        <Route path="/my-orders" element={<MyOrdersPage />} />
        <Route path="/kitchen" element={<KitchenDashboardPage />} />
        <Route path="/operations" element={<OperationsPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantDetailPage />} />
        <Route path="/" element={<RestaurantListPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}
```

The `ConsumerSetupModal` is rendered as an overlay whenever `session` is null. It does not
block routing — users can still see the page beneath it — but it blocks interaction by rendering
as a modal overlay. This keeps the routing model simple and avoids guard redirects for most
pages. Exception: `MyOrdersPage` still performs an explicit redirect when session is null (Req
6.5), since the page has no meaning without a `consumer_id`.

---

## Cart State — Detailed Flow

Cart state is owned by `RestaurantDetailPage` as a `useState` call initialised to an empty
`CartState`. The cart is scoped to a single restaurant visit.

```
User flow:
1. Navigates to /restaurants/:restaurantId
2. RestaurantDetailPage initialises: cart = { restaurantId, items: [] }
3. Clicks "Add to cart" on MenuItemCard
   → calls addItem(cart, item) → new cart state (pure function)
   → setCart(newCart) — React re-renders CartPanel
4. CartPanel renders items + total (computed inline from lib/cart.js cartTotal())
5. User clicks "Place order" → OrderConfirmationDrawer opens (within same page)
   → shows DeliveryAddressInput + item summary
6. User confirms → POST /orders → on 201:
   → setCart(clearCart())
   → navigate("/orders/" + order_id)
```

**Cross-restaurant navigation warning**: `RestaurantDetailPage` registers a `useEffect` that
watches `restaurantId` param changes via react-router navigation. When the user attempts to
navigate to a *different* restaurant while cart is non-empty:
- A `useState` boolean `showClearCartDialog` is set to `true`
- The dialog renders with Confirm/Cancel
- On Confirm: `setCart(clearCart())`, then navigate proceeds
- On Cancel: navigation is blocked (use `navigate` with `replace: false` and hold the pending
  destination in a `pendingNavRef`)

Implementation note: blocking navigation in react-router v6 uses the `useBlocker` hook
(available since v6.7). If `useBlocker` is not available in the installed version, the
equivalent pattern is to store the attempted destination and render the dialog manually.

---

## Polling Strategy — Order Status Page

`OrderStatusPage` uses `setInterval` plus `AbortController` for per-request cancellation.

```jsx
useEffect(() => {
  let intervalId;
  let controller;

  const TERMINAL_STATUSES = new Set(["PREPARING", "CANCELLED"]);
  const POLL_INTERVAL_MS = 5000;

  async function fetchOrder() {
    controller = new AbortController();
    try {
      const data = await getOrder(orderId, { signal: controller.signal });
      setOrder(data);
      if (TERMINAL_STATUSES.has(data.status)) {
        clearInterval(intervalId);
      }
    } catch (err) {
      if (err.name === "AbortError") return;
      if (err.message.includes("404")) {
        setStatus("not_found");
        clearInterval(intervalId);
        return;
      }
      // Non-fatal: keep polling, display transient error
      setTransientError(err.message);
    }
  }

  fetchOrder(); // immediate first load
  intervalId = setInterval(fetchOrder, POLL_INTERVAL_MS);

  return () => {
    clearInterval(intervalId);
    controller?.abort(); // cancel any in-flight request on unmount
  };
}, [orderId]);
```

Key design decisions:
- Each poll creates a **new** `AbortController` so only the current in-flight request is
  cancelled on unmount, not future ones.
- The cleanup function (returned from `useEffect`) both clears the interval **and** aborts the
  current in-flight request — ensuring no state updates occur after unmount.
- A 404 response stops polling and shows "Order not found".
- A non-2xx, non-404 response shows a dismissible transient error but does **not** stop
  polling — the next interval tick will try again.

---

## API Client Design

All additions go into `frontend/src/lib/api.js`. No component ever calls `fetch` directly.

```js
const DEFAULT_HEADERS = {
  Accept: "application/json",
};

const JSON_HEADERS = {
  ...DEFAULT_HEADERS,
  "Content-Type": "application/json",
};

// ── Consumers ─────────────────────────────────────────────────────────────
export async function createConsumer(data) {
  const response = await fetch("/consumers", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to create consumer: ${response.status}`);
  }
  return response.json();
}

// ── Orders ────────────────────────────────────────────────────────────────
export async function placeOrder(data) {
  const response = await fetch("/orders", {
    method: "POST",
    headers: JSON_HEADERS,
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to place order: ${response.status}`);
  }
  return response.json();
}

export async function getOrder(orderId, { signal } = {}) {
  const response = await fetch(`/orders/${orderId}`, {
    headers: DEFAULT_HEADERS,
    signal,
  });
  if (!response.ok) {
    throw new Error(`Failed to load order: ${response.status}`);
  }
  return response.json();
}

export async function getOrdersByConsumer(consumerId, { signal } = {}) {
  const response = await fetch(`/orders?consumer_id=${encodeURIComponent(consumerId)}`, {
    headers: DEFAULT_HEADERS,
    signal,
  });
  if (!response.ok) {
    throw new Error(`Failed to load orders: ${response.status}`);
  }
  return response.json();
}

export async function getOrdersByStatus(status, { signal } = {}) {
  const response = await fetch(`/orders?status=${encodeURIComponent(status)}`, {
    headers: DEFAULT_HEADERS,
    signal,
  });
  if (!response.ok) {
    throw new Error(`Failed to load orders: ${response.status}`);
  }
  return response.json();
}

// ── Kitchen ───────────────────────────────────────────────────────────────
export async function getKitchenTickets({ signal } = {}) {
  const response = await fetch("/kitchen/tickets", {
    headers: DEFAULT_HEADERS,
    signal,
  });
  if (!response.ok) {
    throw new Error(`Failed to load kitchen tickets: ${response.status}`);
  }
  return response.json();
}

export async function acceptKitchenTicket(ticketId) {
  const response = await fetch(`/kitchen/tickets/${ticketId}/accept`, {
    method: "POST",
    headers: JSON_HEADERS,
  });
  if (!response.ok) {
    // Preserve raw response for 409 conflict handling in the caller
    const body = await response.json().catch(() => ({}));
    const err = new Error(`Failed to accept ticket: ${response.status}`);
    err.status = response.status;
    err.body = body;
    throw err;
  }
  return response.json();
}

export async function rejectKitchenTicket(ticketId) {
  const response = await fetch(`/kitchen/tickets/${ticketId}/reject`, {
    method: "POST",
    headers: JSON_HEADERS,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const err = new Error(`Failed to reject ticket: ${response.status}`);
    err.status = response.status;
    err.body = body;
    throw err;
  }
  return response.json();
}
```

Note on 409 handling: `acceptKitchenTicket` and `rejectKitchenTicket` throw an enriched `Error`
object carrying `.status` and `.body` fields. `KitchenDashboardPage` checks `err.status === 409`
to extract `current_status` and `target_status` for the inline error message.

---

## Kitchen Ticket — Optimistic UI

`KitchenDashboardPage` holds `tickets` in `useState`. Tickets are split into two derived
arrays at render time (no secondary state):

```js
const actionableTickets = tickets.filter(t => t.status === "CREATE_PENDING");
const readOnlyTickets   = tickets.filter(t => t.status !== "CREATE_PENDING");
```

When Accept is clicked for ticket `id`:

1. `pendingTickets` state (a `Set<string>`) adds `id` — disables both buttons for that row.
2. `POST /kitchen/tickets/:id/accept` is called.
3. **On 200**: `setTickets(tickets.map(t => t.id === id ? { ...t, status: "ACCEPTED" } : t))` —
   the ticket naturally flows from `actionableTickets` to `readOnlyTickets` on next render.
   `pendingTickets` removes `id`.
4. **On 409**: inline error state for that ticket is set with `{ current_status, target_status }`.
   `pendingTickets` removes `id` (re-enables buttons).
5. **On other non-2xx**: a global dismissible banner is shown. `pendingTickets` removes `id`
   (re-enables buttons).

Reject follows identical logic with `"CANCELLED"` as the target status.

This is purely **reactive UI update** (not classic optimistic update) — we wait for the 200
before moving the ticket. The in-flight disable-both-buttons state prevents double-submission
while keeping the ticket visible in its original section during the request.

---

## File / Folder Structure

```
frontend/src/
├── main.jsx                          (add ConsumerSessionProvider wrapper)
├── App.jsx                           (updated routing + NavBar + ConsumerSetupModal)
│
├── lib/
│   ├── api.js                        (extended — all fetch functions)
│   ├── session.js                    (NEW — readSession/writeSession/clearSession + validation)
│   └── cart.js                       (NEW — pure cart functions: addItem, removeItem, setQuantity, cartTotal)
│
├── hooks/
│   ├── useConsumerSession.js         (NEW — useContext(ConsumerSessionContext) shorthand)
│   └── useOrderPolling.js            (NEW — setInterval + AbortController hook extracted from OrderStatusPage)
│
├── context/
│   └── ConsumerSessionContext.jsx    (NEW — createContext + ConsumerSessionProvider)
│
├── components/
│   ├── NavBar.jsx                    (NEW — persistent top navigation)
│   ├── StatusBadge.jsx               (NEW — coloured status pill)
│   ├── LoadingSpinner.jsx            (NEW — accessible spinner)
│   ├── SkeletonBlock.jsx             (NEW — pulsing placeholder)
│   ├── ErrorMessage.jsx              (NEW — consistent error display with optional retry)
│   ├── OrderRow.jsx                  (NEW — shared order list row)
│   ├── CartPanel.jsx                 (NEW — cart summary panel in restaurant detail page)
│   ├── CartItemRow.jsx               (NEW — single cart item with quantity controls)
│   ├── ConsumerSetupModal.jsx        (NEW — overlay form for consumer identity creation)
│   ├── OrderConfirmationDrawer.jsx   (NEW — address + summary before POST /orders)
│   ├── RestaurantCard.jsx            (unchanged)
│   └── MenuItemCard.jsx              (augmented — adds "Add to cart" button)
│
└── pages/
    ├── RestaurantListPage.jsx        (unchanged)
    ├── RestaurantDetailPage.jsx      (augmented — cart state, Add-to-cart, CartPanel, OrderConfirmationDrawer)
    ├── OrderStatusPage.jsx           (NEW)
    ├── MyOrdersPage.jsx              (NEW)
    ├── KitchenDashboardPage.jsx      (NEW)
    ├── OperationsPage.jsx            (NEW)
    ├── ConsumerLookupPage.jsx        (NEW)
    └── NotFoundPage.jsx              (NEW)
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of
a system — essentially, a formal statement about what the system should do. Properties serve as
the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Malformed ConsumerSession always triggers form display

*For any* value stored in localStorage under `ftgo_consumer_session` that is not a valid JSON
object containing a non-empty UUID `consumer_id` (including null, empty string, invalid JSON,
JSON with missing `consumer_id`, and JSON with a non-UUID `consumer_id`), `readSession()` SHALL
return `null` and SHALL remove the key from localStorage.

**Validates: Requirements 1.2**

---

### Property 2: Valid ConsumerSession always suppresses the setup form

*For any* well-formed UUID string used as `consumer_id` in a `ConsumerSession` object, seeding
that value into localStorage before mount SHALL cause `readSession()` to return a non-null
`ConsumerSession` and cause `App` to skip the `ConsumerSetupModal`.

**Validates: Requirements 1.4**

---

### Property 3: POST /consumers non-2xx always keeps the form visible with an error

*For any* HTTP status code in the range 400–599, when `POST /consumers` is mocked to return
that status code, the `ConsumerSetupModal` SHALL remain visible, the submit button SHALL be
re-enabled, and a non-empty plain-string error message SHALL be displayed below the button.

**Validates: Requirements 1.5**

---

### Property 4: Price formatting always produces exactly 2 decimal places

*For any* non-negative finite number passed to `formatPrice`, the returned string SHALL contain
exactly one decimal point followed by exactly 2 digits, and SHALL begin with a currency symbol
(e.g. `$`). This holds for integers, decimals with 1 digit, decimals with more than 2 digits
(rounded), very large values, and zero.

**Validates: Requirements 2.2**

---

### Property 5: Cart total equals the sum of all line totals

*For any* collection of `CartItem` entries (including zero items, one item with any quantity
1–99, and multiple items with arbitrary quantities), `cartTotal(cart)` SHALL equal
`sum(item.unit_price × item.quantity for all items)`. Additionally, `addItem` followed by
`removeItem` for the same item SHALL return a cart equal to the original. `setQuantity` with
quantity `0` SHALL produce the same result as `removeItem`.

**Validates: Requirements 3.2, 3.3, 3.4**

---

### Property 6: Cart state is never written to localStorage

*For any* sequence of cart operations (`addItem`, `removeItem`, `setQuantity`, `clearCart`),
localStorage SHALL contain no key whose stringified value contains `CartItem` field names
(`menu_item_id`, `unit_price`, `quantity`) after the operations complete.

**Validates: Requirements 3.6**

---

### Property 7: POST /orders payload is correctly shaped for all valid inputs

*For any* combination of valid `consumer_id` UUID, `restaurant_id` UUID, non-empty
`delivery_address` string (up to 500 chars), and non-empty `CartItem[]` array, the JSON body
intercepted at `POST /orders` SHALL contain exactly the fields `consumer_id`, `restaurant_id`,
`currency` (always `"USD"`), `delivery_address`, and `line_items` where each entry has
`menu_item_id` and `quantity` matching the cart state. No extra fields SHALL be present.

**Validates: Requirements 4.2**

---

### Property 8: POST /orders non-2xx always keeps the order form submittable

*For any* HTTP status code in the range 400–599 (or a simulated network error), when
`POST /orders` is mocked to return that status, the `OrderConfirmationDrawer` SHALL remain
visible, the submit button SHALL be re-enabled, and a non-empty error message SHALL be
displayed within the drawer.

**Validates: Requirements 4.4**

---

### Property 9: StatusBadge applies correct colour class for every valid status

*For any* value in `{ PENDING, APPROVED, PREPARING, CANCELLED, ACCEPTED, CREATE_PENDING }`,
`StatusBadge` SHALL render a `<span>` whose `className` contains the Tailwind classes
specified in the design's colour mapping table, with no class from a different status's mapping
present.

**Validates: Requirements 5.2**

---

### Property 10: Polling is active during PENDING and APPROVED statuses

*For any* orderId, while the mocked `GET /orders/:orderId` continues to return a status of
`PENDING` or `APPROVED`, the number of fetch calls after `n × 5000 ms` (using fake timers)
SHALL equal `n + 1` (initial load + n interval ticks), up to any reasonable `n`.

**Validates: Requirements 5.3**

---

### Property 11: Polling stops immediately on any terminal status

*For any* orderId, when `GET /orders/:orderId` is mocked to return status `PREPARING` or
`CANCELLED` on poll tick `k`, no further fetch calls SHALL be made after tick `k`, regardless
of how many additional timer intervals are advanced.

**Validates: Requirements 5.4**

---

### Property 12: Unmount always cancels polling and in-flight requests

*For any* orderId and any elapsed time (0 ms through multiple poll intervals), unmounting
`OrderStatusPage` SHALL result in: (a) the `setInterval` being cleared (no further fetch calls
after unmount), and (b) the most-recent `AbortController`'s signal being aborted (no state
updates after unmount).

**Validates: Requirements 5.7**

---

### Property 13: Order row formatting functions are always correct

*For any* ISO 8601 date string `d`, `formatOrderDate(d)` SHALL return a string matching
`/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/`. *For any* decimal string `amount` and currency code
`currency`, `formatAmount(amount, currency)` SHALL return a string matching
`/^\d+\.\d{2} [A-Z]{3}$/`. *For any* UUID string `id`, `truncateId(id)` SHALL return exactly
the first 8 characters of `id`.

**Validates: Requirements 6.2, 8.5**

---

### Property 14: Ticket section assignment is correct for any mixture of ticket statuses

*For any* array of `KitchenTicket` objects with arbitrary `status` values, rendering
`KitchenDashboardPage` SHALL place every ticket with `status === "CREATE_PENDING"` in the
actionable section (with Accept and Reject buttons rendered) and every ticket with any other
status in the read-only section (with no action buttons rendered).

**Validates: Requirements 7.2**

---

### Property 15: Accept and Reject actions correctly transition ticket status and section

*For any* `KitchenTicket` with `status === "CREATE_PENDING"`, when the Accept button is clicked
and the mocked `POST /kitchen/tickets/:id/accept` returns `200`, the ticket SHALL appear in the
read-only section with `status === "ACCEPTED"` and no action buttons. Symmetrically, when
Reject is clicked and returns `200`, the ticket SHALL appear with `status === "CANCELLED"` and
no action buttons. In both cases the ticket SHALL NOT appear in the actionable section
afterward.

**Validates: Requirements 7.3, 7.4**

---

### Property 16: 409 conflict error always displays both status fields

*For any* pair of strings `(current_status, target_status)` returned in a `409` response body
from `POST /kitchen/tickets/:id/accept` or `reject`, the inline error message rendered adjacent
to that ticket row SHALL contain both the `current_status` string and the `target_status`
string.

**Validates: Requirements 7.5**

---

### Property 17: Status filter fetch uses the correct status parameter for all four values

*For any* selection of one of `{ PENDING, APPROVED, PREPARING, CANCELLED }` in the
`OperationsPage` filter control, the intercepted fetch URL SHALL equal
`/orders?status={selectedStatus}` with no additional query parameters.

**Validates: Requirements 8.3**

---

### Property 18: UUID validation rejects all non-RFC-4122 strings and accepts all valid ones

*For any* string that does not match
`/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i`, the
`ConsumerLookupPage` form submission SHALL be blocked and a "Please enter a valid UUID" error
SHALL be shown with no fetch call made. *For any* string that does match the pattern,
submission SHALL proceed and `GET /orders?consumer_id=` SHALL be called.

**Validates: Requirements 9.3**

---

### Property 19: All API functions throw an Error with the HTTP status code for any non-2xx response

*For any* API function in `lib/api.js` (`createConsumer`, `placeOrder`, `getOrder`,
`getOrdersByConsumer`, `getOrdersByStatus`, `getKitchenTickets`) and *for any* HTTP status code
`s` in the range 400–599, when `fetch` is mocked to return `{ ok: false, status: s }`, the
function SHALL throw an `Error` whose `.message` string contains the decimal string
representation of `s`.

**Validates: Requirements 11.2**

---

### Property 20: All POST API functions send Content-Type: application/json

*For any* call to `createConsumer`, `placeOrder`, `acceptKitchenTicket`, or
`rejectKitchenTicket`, the `Headers` object passed to `fetch` SHALL include
`Content-Type: application/json`.

**Validates: Requirements 11.4**

---

### Property 21: Error display text is always a plain string, never raw JSON

*For any* API error response body (including JSON objects, JSON arrays, plain strings, empty
bodies, and HTML error pages), the text rendered in `ErrorMessage` SHALL be a `typeof "string"`
value, not a stringified object literal (i.e. SHALL NOT match `/^\[object Object\]/` or
`/^\[.*\]$/`).

**Validates: Requirements 12.5**

---

## Error Handling

### Consistent Pattern

All pages follow the same three-state pattern established in `RestaurantListPage`:

```js
const [status, setStatus] = useState("idle" | "loading" | "success" | "error");
const [errorMessage, setErrorMessage] = useState("");
```

Error messages are always derived from the `Error.message` thrown by `lib/api.js` (which
includes the HTTP status code) or the literal string `"Network error"` when no response was
received. Components never inspect raw response bodies to build error strings.

### Error Categories

| Error type | Display | Polling / retries |
|---|---|---|
| Network failure (no response) | `ErrorMessage` with "Network error" | Retry control |
| 4xx client error | `ErrorMessage` with status code | Retry control |
| 404 specifically | "Not found" variant of `ErrorMessage` | No retry |
| 5xx server error | `ErrorMessage` with status code | Retry control |
| 409 conflict (kitchen) | Inline per-row message with `current_status`/`target_status` | Buttons re-enabled |
| Transient poll error (5xx during order polling) | Dismissible inline warning | Polling continues |

### Consumer Setup Error

When `POST /consumers` fails, the error is shown inline below the submit button within
`ConsumerSetupModal`. The modal is never dismissed until a successful `201` response is received.

---

## Testing Strategy

### Testing Framework Selection

No test framework is currently installed. The recommended addition is **Vitest** (co-located
with Vite, zero-config) paired with **@testing-library/react** for component tests and
**@testing-library/user-event** for interaction simulation. For property-based tests,
**fast-check** is the recommended library (TypeScript/JavaScript, fast, well-maintained).

Install (exact versions):
```
vitest@3.2.4
@testing-library/react@16.3.0
@testing-library/user-event@14.6.1
@testing-library/jest-dom@6.6.3
@vitest/coverage-v8@3.2.4
fast-check@3.23.2
jsdom@26.1.0
```

### Dual Testing Approach

**Unit/example tests** cover specific scenarios: loading states, error displays, routing
redirects, specific edge cases (empty cart, malformed session, 404 responses).

**Property-based tests** (via fast-check) cover universal properties that hold across all
inputs: formatting functions, cart arithmetic, session validation, API payload shapes, UUID
validation.

### Unit Testing Balance

Unit tests focus on:
- Component render states (loading, error, empty, success) with mocked API responses
- User interactions (click handlers, form submissions)
- Integration points (navigation after order placement, poll cancellation on unmount)
- Edge cases not covered by properties (404-specific messages, empty arrays)

Property tests focus on (minimum 100 iterations per test, via `fc.assert`):
- Pure library functions in `lib/session.js`, `lib/cart.js`, `lib/api.js`
- Formatting utilities in `OrderRow`
- StatusBadge colour mapping
- UUID validation logic
- API payload construction
- Polling lifecycle invariants (using fake timers)

### Property Test Tag Format

Each property test is annotated with a comment:

```js
// Feature: ftgo-frontend, Property N: <property_text>
```

### Test File Co-location

```
frontend/src/
├── lib/
│   ├── session.test.js    (Properties 1, 2, 21)
│   ├── cart.test.js       (Properties 5, 6)
│   └── api.test.js        (Properties 19, 20)
├── components/
│   ├── StatusBadge.test.jsx   (Property 9)
│   ├── OrderRow.test.jsx      (Property 13)
│   └── ErrorMessage.test.jsx  (Property 21, unit tests)
└── pages/
    ├── ConsumerSetupModal.test.jsx     (Properties 3, unit tests for 1.1, 1.6, 1.7)
    ├── RestaurantDetailPage.test.jsx   (Property 4, unit tests for 2.x)
    ├── OrderStatusPage.test.jsx        (Properties 10, 11, 12)
    ├── KitchenDashboardPage.test.jsx   (Properties 14, 15, 16, unit tests for 7.x)
    ├── OperationsPage.test.jsx         (Property 17, unit tests for 8.x)
    ├── ConsumerLookupPage.test.jsx     (Property 18, unit tests for 9.x)
    └── MyOrdersPage.test.jsx           (unit tests for 6.x)
```

### Property-Based Test Configuration

```js
// vitest.config.js addition
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.js"],
  },
});
```

Each `fc.assert` call uses `fc.property` with at least 100 runs (fast-check default is 100):

```js
// Feature: ftgo-frontend, Property 5: Cart total equals sum of line totals
it("cartTotal equals sum of line totals for any CartItem collection", () => {
  fc.assert(
    fc.property(
      fc.array(
        fc.record({
          menu_item_id: fc.uuid(),
          name: fc.string({ minLength: 1 }),
          unit_price: fc.float({ min: 0.01, max: 999.99, noNaN: true }),
          quantity: fc.integer({ min: 1, max: 99 }),
        }),
        { minLength: 0, maxLength: 20 }
      ),
      (items) => {
        const cart = { restaurantId: "r1", items };
        const expected = items.reduce((s, i) => s + i.unit_price * i.quantity, 0);
        expect(cartTotal(cart)).toBeCloseTo(expected, 5);
      }
    )
  );
});
```
