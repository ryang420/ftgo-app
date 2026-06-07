# Requirements Document

## Introduction

This feature extends the existing FTGO React frontend (React 18, react-router-dom v6, Tailwind CSS,
Vite) from its current restaurant-browsing-only state to cover the full FTGO learner journey. Four
areas are added:

1. **Place Order flow** — consumer identity creation, restaurant and menu browsing, an in-page cart,
   and order submission.
2. **Order Status & History** — a consumer's own orders listed from the CQRS read side, with live
   status badges that poll for changes.
3. **Kitchen Dashboard** — a dedicated view for kitchen staff to list open tickets and accept or
   reject each one.
4. **Order Query views** — an operations page for browsing all orders filtered by status, and a
   consumer lookup page.

All new pages must follow the existing dark stone/orange Tailwind palette. Every network call goes
through the Vite dev-proxy (`/restaurants`, `/orders`, `/consumers`, `/kitchen`) to the API Gateway
at `http://localhost:8000`.

---

## Glossary

- **Frontend**: The React + Vite + Tailwind single-page application located under `frontend/`.
- **API_Gateway**: The nginx gateway at `http://localhost:8000` that routes requests to backend microservices.
- **Consumer**: A person who places orders. Identified by a UUID (`consumer_id`). Created via `POST /consumers`.
- **Consumer_Service**: The backend microservice that creates and retrieves consumer records.
- **Restaurant**: A food vendor entity returned by `GET /restaurants` and `GET /restaurants/:id`.
- **Restaurant_Service**: The backend microservice that serves restaurant and menu-item data.
- **MenuItem**: A single item offered by a restaurant. Returned in `GET /restaurants/:id/menu-items`.
- **Cart**: An in-memory, client-side collection of `CartItem` entries accumulated before order submission.
- **CartItem**: One entry in the Cart, containing `menu_item_id`, `name`, `unit_price`, and `quantity`.
- **Order**: An order entity tracked by `order-service` and projected into the CQRS read model.
- **Order_Service**: The backend microservice that accepts `POST /orders` and owns the write side of order state.
- **Order_Query_Service**: The CQRS read-side microservice exposing `GET /orders/:id`, `GET /orders?consumer_id=`, and `GET /orders?status=`.
- **OrderSummary**: The read model object returned by `Order_Query_Service`. Fields: `order_id`, `consumer_id`, `restaurant_id`, `status`, `currency`, `total_amount`, `delivery_address`, `created_at`, `updated_at`, `line_items[]`.
- **OrderStatus**: The lifecycle state of an order. Valid values: `PENDING`, `APPROVED`, `PREPARING`, `CANCELLED`.
- **KitchenTicket**: A ticket entity in `kitchen-service` representing the kitchen's view of an order.
- **Kitchen_Service**: The backend microservice exposing kitchen ticket endpoints.
- **KitchenTicketStatus**: The lifecycle state of a kitchen ticket. Values relevant to the frontend: `CREATE_PENDING`, `ACCEPTED`, `CANCELLED`.
- **Vite_Proxy**: The Vite dev-server proxy that forwards `/restaurants`, `/orders`, `/consumers`, and `/kitchen` requests to the API Gateway.
- **ConsumerSession**: Client-side storage (localStorage) holding the current consumer's `consumer_id` and display name across page reloads. A ConsumerSession is **valid** when it contains a non-empty `consumer_id` string that is a well-formed UUID.
- **StatusBadge**: A coloured UI label component that renders an `OrderStatus` string with a consistent colour-coded style.
- **DeliveryAddress**: A free-text string supplied by the consumer when placing an order.

---

## Requirements

### Requirement 1: Consumer Identity Management

**User Story:** As a first-time visitor, I want to create or recall a consumer identity in the app,
so that my orders are associated with a stable `consumer_id` that persists across reloads.

#### Acceptance Criteria

1. WHEN the Frontend loads and no `ConsumerSession` is stored in localStorage, THE Frontend SHALL
   display a consumer setup form prompting for first name and last name (each max 100
   characters).
2. WHEN the Frontend loads and localStorage contains a `ConsumerSession` key whose value is not
   a valid JSON object with a non-empty `consumer_id` UUID string, THE Frontend SHALL treat
   the session as absent, clear the malformed entry, and display the consumer setup form.
3. WHEN the consumer submits the setup form with non-empty first name and last name, THE Frontend
   SHALL call `POST /consumers` with a JSON body compatible with `consumer-service`, including
   non-empty `first_name`, non-empty `last_name`, and a generated unique `email`. Upon a `201`
   response, THE Frontend SHALL persist the returned `consumer_id` and display name into
   localStorage as the `ConsumerSession`.
4. IF the consumer attempts to submit the setup form with a blank first name or blank last name,
   THEN THE Frontend SHALL display an inline validation error and SHALL NOT call `POST /consumers`.
5. WHEN the Frontend loads and a valid `ConsumerSession` is present in localStorage, THE Frontend
   SHALL skip the consumer setup form and proceed directly to the main application.
6. IF `POST /consumers` returns a non-`2xx` response, THEN THE Frontend SHALL display an inline
   error message below the submit button and keep the consumer setup form visible and
   submittable.
7. THE Frontend SHALL provide a "Change consumer" control in the top navigation bar that clears
   the `ConsumerSession` from localStorage and returns the user to the consumer setup form.
8. WHILE the `POST /consumers` request is in-flight, THE Frontend SHALL disable the submit
   button and display a loading indicator within or adjacent to the button to prevent duplicate
   submissions.

---

### Requirement 2: Restaurant Browsing (Existing + Augmented)

**User Story:** As a consumer, I want to browse restaurants and view their menus in the same
dark-themed UI, so that I can choose what to order.

#### Acceptance Criteria

1. THE Frontend SHALL continue to serve `GET /restaurants` on the `/` route as the restaurant
   list page, preserving the existing dark stone/orange Tailwind styling.
2. WHEN a consumer navigates to `/restaurants/:restaurantId`, THE Frontend SHALL call
   `GET /restaurants/:restaurantId/menu-items` and display each menu item's name and price
   (formatted as a non-negative decimal with exactly 2 decimal places) in the order returned
   by the API.
3. WHEN the menu items are loading, THE Frontend SHALL display a skeleton or spinner in place of
   the menu item list.
4. IF `GET /restaurants/:restaurantId/menu-items` returns a non-`2xx` response, THEN THE
   Frontend SHALL display an error message within the restaurant detail page that communicates
   that menu items could not be loaded, without navigating away.
5. WHEN a valid `ConsumerSession` exists, THE Frontend SHALL display an enabled "Add to cart"
   button for each menu item on the restaurant detail page.
6. WHEN no valid `ConsumerSession` exists, THE Frontend SHALL render the "Add to cart" button
   for each menu item in a disabled state (visible but non-interactive).
7. WHEN `GET /restaurants/:restaurantId/menu-items` returns an empty array, THE Frontend SHALL
   display a "No menu items available" message in place of the menu item list.
8. IF `GET /restaurants` returns a non-`2xx` response on the restaurant list page, THEN THE
   Frontend SHALL display an error message that communicates the restaurants could not be
   loaded.

---

### Requirement 3: Cart Management

**User Story:** As a consumer, I want to build a cart of items from a single restaurant before
submitting my order, so that I can review and adjust my selection.

#### Acceptance Criteria

1. WHEN a consumer clicks "Add to cart" for a menu item, THE Frontend SHALL add one unit of that
   item to the Cart, or increment its quantity by one if the item is already present.
2. WHILE the consumer is on a restaurant detail page with one or more CartItems, THE Frontend
   SHALL display a visible cart summary panel showing each `CartItem`'s name, quantity, unit
   price, and computed line total (`unit_price × quantity`), plus the overall cart total.
   WHEN the Cart is empty, THE Frontend SHALL display the cart summary panel in a zero-item
   empty state (total of $0.00).
3. WHEN a consumer changes the quantity of a `CartItem` to zero or clicks a remove control for
   that item, THE Frontend SHALL remove that item from the Cart.
4. WHEN any CartItem is added, removed, or has its quantity changed, THE Frontend SHALL
   immediately recompute and display the cart total as the sum of `(unit_price × quantity)` for
   all remaining `CartItem` entries.
5. IF a consumer navigates to a different restaurant's detail page while the Cart contains items
   from a different restaurant, THEN THE Frontend SHALL display a warning dialog before allowing
   navigation, informing the consumer that the Cart will be cleared. WHEN the consumer confirms,
   THE Frontend SHALL clear the Cart and proceed with navigation. WHEN the consumer cancels,
   THE Frontend SHALL keep the Cart contents unchanged and remain on the current page.
6. THE Frontend SHALL keep Cart state in React component state and SHALL NOT persist the Cart
   to localStorage or any external store.
7. WHEN the Cart is empty, THE Frontend SHALL disable the "Place order" button and display a
   "Cart is empty — add at least one item" message adjacent to the button.
8. WHEN a consumer attempts to set a CartItem's quantity to a value outside the range 1–99
   inclusive, THE Frontend SHALL reject the input, restore the previous valid quantity, and
   display an inline validation message indicating that quantity must be between 1 and 99.

---

### Requirement 4: Place Order Submission

**User Story:** As a consumer, I want to submit my cart as an order with a delivery address, so
that the kitchen receives my request.

#### Acceptance Criteria

1. WHEN a consumer clicks "Place order" with a non-empty Cart, THE Frontend SHALL display a
   delivery address input field (required, max 500 characters) and a confirmation summary
   showing the restaurant name, each item name with its quantity, and the total item count
   before final submission.
2. WHEN the consumer confirms submission, THE Frontend SHALL call `POST /orders` with a JSON
   body containing `consumer_id` (from `ConsumerSession`), `restaurant_id` (from the current
   restaurant), `currency` set to `"USD"`, `delivery_address` (from the input), and
   `line_items` array where each entry contains `menu_item_id` and `quantity`.
3. WHEN `POST /orders` returns `201`, THE Frontend SHALL clear the Cart, display a success
   notification containing the new `order_id`, and navigate the consumer to the order status
   page at `/orders/:orderId`.
4. IF `POST /orders` returns a non-`2xx` response or no response is received due to a network
   or timeout failure, THEN THE Frontend SHALL display an error message within the order
   confirmation view and keep the form submittable for retry.
5. WHILE the `POST /orders` request is in-flight, THE Frontend SHALL disable the submit button
   and show a loading indicator to prevent duplicate order submissions.
6. IF the delivery address field is empty when the consumer attempts to submit, THEN THE
   Frontend SHALL display an inline validation error on the delivery address field and SHALL NOT
   submit the request.
7. WHEN a consumer clicks "Place order" with an empty Cart, THE Frontend SHALL NOT display the
   delivery address or confirmation form, and SHALL display an inline error message indicating
   that at least one item is required.

---

### Requirement 5: Order Status Page

**User Story:** As a consumer, I want to view the live status of a specific order, so that I can
track it from placement through preparation.

#### Acceptance Criteria

1. WHEN the Frontend renders `/orders/:orderId`, THE Frontend SHALL call
   `GET /orders/:orderId` against the `Order_Query_Service` and display the `OrderSummary`
   fields: `order_id`, `status`, `restaurant_id`, `total_amount`, `delivery_address`,
   `created_at`, and `line_items`.
2. THE Frontend SHALL render the `OrderStatus` value using the `StatusBadge` component with
   distinct colours per status: `PENDING` — amber, `APPROVED` — blue, `PREPARING` — orange,
   `CANCELLED` — red.
3. WHILE the `OrderStatus` is `PENDING` or `APPROVED`, THE Frontend SHALL poll
   `GET /orders/:orderId` every 5 seconds and update the displayed status without a full page
   reload.
4. WHEN the polled `OrderStatus` value is `PREPARING`, THE Frontend SHALL stop polling and
   display the message "Your order is being prepared". WHEN the `OrderStatus` is `CANCELLED`,
   THE Frontend SHALL stop polling and display the message "Your order has been cancelled".
5. IF `GET /orders/:orderId` returns `404`, THEN THE Frontend SHALL display an "Order not
   found" message and stop polling.
6. IF `GET /orders/:orderId` returns a non-`2xx`, non-`404` response, THEN THE Frontend SHALL
   display a visible error message element indicating the request failed, and SHALL continue
   polling on the next interval without crashing the page.
7. WHEN the consumer navigates away from `/orders/:orderId`, THE Frontend SHALL cancel any
   in-flight poll request and clear the polling interval.

---

### Requirement 6: Consumer Order History

**User Story:** As a consumer, I want to see a list of all my past orders, so that I can review
their statuses and re-visit individual orders.

#### Acceptance Criteria

1. WHEN the Frontend renders `/my-orders`, THE Frontend SHALL call
   `GET /orders?consumer_id={consumer_id}` using the `consumer_id` from `ConsumerSession`
   and display the returned `OrderSummary` list.
2. THE Frontend SHALL display each order in the list with: `order_id` truncated to its first 8
   characters with a copy-to-clipboard control, `status` as a `StatusBadge`, `total_amount`
   formatted as `{amount_2dp} {currency_code}` (e.g. `12.50 USD`), `restaurant_id`, and
   `created_at` formatted as `YYYY-MM-DD HH:mm` in the consumer's local timezone.
3. WHEN a consumer clicks an order row, THE Frontend SHALL navigate to `/orders/:orderId`.
4. WHEN the `GET /orders?consumer_id=` response is an empty array, THE Frontend SHALL display
   a "No orders yet" message.
5. IF the `ConsumerSession` is missing when `/my-orders` is loaded, THEN THE Frontend SHALL
   redirect the consumer to the consumer setup form.
6. IF `GET /orders?consumer_id=` returns a non-`2xx` response, THEN THE Frontend SHALL display
   an error message indicating that orders could not be loaded and provide a retry control that
   re-issues the same `GET /orders?consumer_id=` request.

---

### Requirement 7: Kitchen Dashboard

**User Story:** As a kitchen staff member, I want a dashboard that lists all open kitchen tickets,
so that I can accept or reject each one in a single view.

#### Acceptance Criteria

1. WHEN the Frontend renders `/kitchen`, THE Frontend SHALL call `GET /kitchen/tickets` and,
   while the request is in-flight, display a loading indicator. Upon success, THE Frontend
   SHALL display all returned tickets with their `ticket_id`, `order_id`, `restaurant_id`,
   and `status`.
2. THE Frontend SHALL render tickets with status `CREATE_PENDING` in an actionable section
   showing Accept and Reject buttons; tickets with other statuses SHALL be shown in a separate
   read-only section below with no action buttons.
3. WHEN a kitchen staff member clicks the "Accept" button for a `CREATE_PENDING` ticket, THE
   Frontend SHALL call `POST /kitchen/tickets/:ticket_id/accept` and, upon a `200` response,
   move that ticket row to the read-only section with status `ACCEPTED` and no action buttons,
   without a full page reload.
4. WHEN a kitchen staff member clicks the "Reject" button for a `CREATE_PENDING` ticket, THE
   Frontend SHALL call `POST /kitchen/tickets/:ticket_id/reject` and, upon a `200` response,
   move that ticket row to the read-only section with status `CANCELLED` and no action buttons,
   without a full page reload.
5. IF `POST /kitchen/tickets/:ticket_id/accept` or `POST /kitchen/tickets/:ticket_id/reject`
   returns `409`, THEN THE Frontend SHALL display an inline error message adjacent to that
   ticket row containing the `current_status` and `target_status` values from the response
   body.
6. IF `POST /kitchen/tickets/:ticket_id/accept` or `POST /kitchen/tickets/:ticket_id/reject`
   returns a non-`2xx`, non-`409` response, THEN THE Frontend SHALL display a dismissible
   error banner and re-enable the action buttons for that ticket.
7. WHILE an accept or reject request for a specific ticket is in-flight, THE Frontend SHALL
   disable both the Accept and Reject buttons for that ticket row to prevent double submission.
8. THE Frontend SHALL provide a manual "Refresh" control on the kitchen dashboard that
   re-fetches `GET /kitchen/tickets` (showing a loading indicator during the fetch) and
   replaces the entire displayed list with the response.
9. IF `GET /kitchen/tickets` returns a non-`2xx` response, THEN THE Frontend SHALL display an
   error message and provide a retry control.
10. WHEN `GET /kitchen/tickets` returns an empty array, THE Frontend SHALL display a "No
    tickets at the moment" message in the actionable section.

---

### Requirement 8: Order Query — Browse by Status (Operations View)

**User Story:** As an operations user, I want to filter all orders by status, so that I can
monitor the current pipeline at each lifecycle stage.

#### Acceptance Criteria

1. WHEN the Frontend renders the operations page, THE Frontend SHALL default the status filter
   to `PENDING`, call `GET /orders?status=PENDING`, and display a loading indicator while the
   request is in-flight.
2. THE Frontend SHALL display a status filter control containing exactly four options:
   `PENDING`, `APPROVED`, `PREPARING`, and `CANCELLED`.
3. WHEN an operations user selects a different status from the filter control, THE Frontend
   SHALL re-fetch `GET /orders?status={newStatus}` and replace the displayed list.
4. WHILE a `GET /orders?status=` request is in-flight, THE Frontend SHALL display a loading
   indicator in the results area.
5. THE Frontend SHALL display each order row with: `order_id` truncated to its first 8
   characters, `status` as a `StatusBadge`, `total_amount` formatted as `{amount_2dp}
   {currency_code}`, `consumer_id` truncated to its first 8 characters, and `created_at`
   formatted as `YYYY-MM-DD HH:mm` in the local timezone.
6. WHEN an operations user clicks an order row, THE Frontend SHALL navigate to
   `/orders/:orderId`.
7. WHEN the response is an empty array for the selected status, THE Frontend SHALL display a
   "No orders with this status" message.
8. IF `GET /orders?status=` returns a non-`2xx` response, THEN THE Frontend SHALL display an
   error message and provide a retry control that re-issues the same request.

---

### Requirement 9: Order Query — Lookup by Consumer ID

**User Story:** As an operations user, I want to look up all orders belonging to a specific
consumer by UUID, so that I can investigate a consumer's order history.

#### Acceptance Criteria

1. WHEN the Frontend renders `/orders/by-consumer`, THE Frontend SHALL display a search form
   with a `consumer_id` UUID input field and a submit button.
2. WHEN the operations user submits a value that matches the RFC 4122 UUID format
   (8-4-4-4-12 hexadecimal characters separated by hyphens), THE Frontend SHALL call
   `GET /orders?consumer_id={uuid}` and display the results where each row shows `order_id`
   (first 8 characters), `consumer_id` (first 8 characters), `status` as a `StatusBadge`,
   and `created_at` formatted as `YYYY-MM-DD HH:mm` in the local timezone.
3. IF the submitted value does not match the RFC 4122 UUID format, THEN THE Frontend SHALL
   display an inline validation error on the input field stating "Please enter a valid UUID"
   and SHALL NOT submit the request.
4. WHEN `GET /orders?consumer_id=` returns an empty array, THE Frontend SHALL display a
   "No orders found for this consumer" message.
5. IF `GET /orders?consumer_id=` returns a non-`2xx` response, THEN THE Frontend SHALL display
   an error message and keep all form fields enabled with the last-entered UUID value preserved,
   allowing re-submission.

---

### Requirement 10: Navigation and Routing

**User Story:** As any user, I want clear top-level navigation so that I can reach each section of
the app without manually typing URLs.

#### Acceptance Criteria

1. THE Frontend SHALL define the following client-side routes: `/` (restaurant list),
   `/restaurants/:restaurantId` (restaurant detail + menu + cart), `/orders/:orderId` (order
   status), `/my-orders` (consumer order history), `/kitchen` (kitchen dashboard),
   `/operations` (operations order query view), `/orders/by-consumer` (consumer lookup).
2. THE Frontend SHALL render a persistent top navigation bar on all routes containing labelled
   links to: Restaurant List (`/`), My Orders (`/my-orders`), Kitchen (`/kitchen`), and
   Operations (`/operations`).
3. WHEN the active route matches a navigation link's path, THE Frontend SHALL apply a
   distinguishable visual active state (e.g. underline or highlight) to that link.
4. WHEN the active route does not match any navigation link's path, THE Frontend SHALL apply no
   active state to any navigation link.
5. THE Frontend SHALL render a "Page not found" message with a link back to `/` for any URL not
   matching the defined routes.
6. THE Frontend SHALL apply the same dark stone/orange colour tokens used on the existing
   restaurant pages to all new pages and components, such that no new page introduces colours
   outside the established palette.

---

### Requirement 11: API Client Abstraction

**User Story:** As a developer, I want all backend calls encapsulated in `frontend/src/lib/api.js`,
so that components never call `fetch` directly and the API surface is easy to audit.

#### Acceptance Criteria

1. THE Frontend SHALL add the following functions to `frontend/src/lib/api.js`:
   `createConsumer(data)`, `placeOrder(data)`, `getOrder(orderId)`,
   `getOrdersByConsumer(consumerId)`, `getOrdersByStatus(status)`,
   `getKitchenTickets()`, `acceptKitchenTicket(ticketId)`, `rejectKitchenTicket(ticketId)`.
2. WHEN any API function receives a non-`2xx` HTTP response, THE Frontend SHALL throw an
   `Error` object whose `message` contains the HTTP status code and a description of the
   failed resource (e.g. `"Failed to load order: 404"`), consistent with the existing pattern
   in `api.js`.
3. THE Frontend SHALL pass `AbortSignal` support via an options object to `getOrder`,
   `getOrdersByConsumer`, `getOrdersByStatus`, and `getKitchenTickets`, so that callers can
   cancel in-flight requests.
4. THE Frontend SHALL set the `Content-Type: application/json` header on all `POST` requests
   in addition to the existing `Accept: application/json` default header.

---

### Requirement 12: Error and Loading State Consistency

**User Story:** As a user, I want consistent loading and error feedback across all new pages, so
that I always know when data is being fetched and what went wrong.

#### Acceptance Criteria

1. THE Frontend SHALL display a loading indicator (spinner or skeleton) on every page from the
   moment a primary data fetch is initiated until a response (success or error) is received.
2. THE Frontend SHALL display an error message in a consistent error component whenever a
   primary data fetch fails; the error message SHALL include the failed URL and the HTTP status
   code (or "Network error" when no response was received).
3. THE Frontend SHALL provide a "Retry" control on every error state that re-triggers the
   failing fetch.
4. WHILE any mutating request (POST) is in-flight, THE Frontend SHALL disable the triggering
   control (button) to prevent duplicate submissions.
5. THE Frontend SHALL NOT render a raw JSON object or array as the visible error message; error
   text displayed to the user SHALL be a plain string derived from the HTTP status code and
   the response `detail` field where available.
