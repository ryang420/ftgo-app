# FTGO Frontend

## Purpose

The FTGO React + Vite + Tailwind single-page application providing the full learner journey: consumer identity, restaurant browsing, cart management, order placement, order tracking, kitchen dashboard, and operations views.

## Requirements

### Requirement: Consumer identity management
The frontend SHALL create, validate, persist, and clear a consumer session using local storage and the consumer API.

#### Scenario: Missing or malformed session
- **WHEN** the frontend loads without a valid stored consumer session
- **THEN** it displays the consumer setup form and clears malformed stored data

#### Scenario: Create consumer session
- **WHEN** the setup form is submitted with non-empty first name and last name
- **THEN** the frontend calls `POST /consumers` with non-empty `first_name`, non-empty `last_name`, and a generated unique `email`
- **AND** stores the returned `consumer_id` and display name before continuing to the main application

#### Scenario: Reject blank consumer name fields
- **WHEN** the setup form is submitted with a blank first name or blank last name
- **THEN** the frontend displays an inline validation error
- **AND** does not call `POST /consumers`

### Requirement: Restaurant browsing with cart
The frontend SHALL preserve restaurant browsing while adding menu item cart interactions for a single restaurant.

#### Scenario: Browse menu and add item
- **WHEN** a restaurant detail page loads with a valid consumer session
- **THEN** menu items are fetched and each item can be added to the cart

#### Scenario: Cart totals update
- **WHEN** cart items are added, removed, or have quantity changed
- **THEN** line totals and overall total are recalculated immediately without persisting cart data to local storage

### Requirement: Place order flow
The frontend SHALL let a consumer submit a cart as an order with delivery address details.

#### Scenario: Submit valid order
- **WHEN** the consumer confirms a non-empty cart with a valid delivery address
- **THEN** the frontend calls `POST /orders` with consumer, restaurant, currency, address, and line item data
- **AND** navigates to the new order status page after a `201` response

#### Scenario: Order submission failure
- **WHEN** order submission fails
- **THEN** the confirmation form remains visible and submittable for retry

### Requirement: Order status and history
The frontend SHALL display order status details, poll active orders, and list a consumer's order history.

#### Scenario: Poll active order
- **WHEN** an order status page shows `PENDING` or `APPROVED`
- **THEN** the frontend polls `GET /orders/{order_id}` every five seconds until a terminal status is reached

#### Scenario: List consumer orders
- **WHEN** `/my-orders` loads with a valid consumer session
- **THEN** the frontend calls `GET /orders?consumer_id={consumer_id}` and displays the returned order summaries

### Requirement: Kitchen dashboard
The frontend SHALL provide a kitchen dashboard for listing tickets and accepting or rejecting actionable tickets.

#### Scenario: Display actionable tickets
- **WHEN** `/kitchen` loads
- **THEN** the frontend fetches `GET /kitchen/tickets` and separates `CREATE_PENDING` tickets from read-only tickets

#### Scenario: Accept or reject ticket
- **WHEN** kitchen staff accept or reject a `CREATE_PENDING` ticket
- **THEN** the frontend calls the matching kitchen endpoint and moves the ticket to the read-only section after success

### Requirement: Operations order queries
The frontend SHALL provide operations views for order lookup by status and by consumer.

#### Scenario: Browse orders by status
- **WHEN** an operations user selects an order status filter
- **THEN** the frontend calls `GET /orders?status={status}` and displays the matching order summaries

#### Scenario: Lookup orders by consumer
- **WHEN** a user submits a valid consumer ID lookup
- **THEN** the frontend calls `GET /orders?consumer_id={consumer_id}` and displays the matching order summaries

### Requirement: Shared frontend infrastructure
The frontend SHALL use shared API, navigation, status, loading, and error components for the expanded journey.

#### Scenario: API calls use shared client
- **WHEN** frontend components need backend data
- **THEN** they call functions in `frontend/src/lib/api.js` rather than calling `fetch` directly

#### Scenario: Consistent routing and states
- **WHEN** users navigate through the app
- **THEN** the navigation, loading states, error states, and not-found route behave consistently across pages

### Requirement: Responsive application shell
The frontend SHALL provide a responsive application shell that exposes primary routes, active navigation state, and current consumer context without blocking the core user journey.

#### Scenario: Active route is visible
- **WHEN** a user navigates between restaurant browsing, my orders, kitchen, and operations routes
- **THEN** the application shell displays the active route distinctly from inactive routes

#### Scenario: Consumer context is visible
- **WHEN** a valid consumer session exists
- **THEN** the application shell displays the consumer display name or a concise fallback identifier

#### Scenario: Mobile navigation remains usable
- **WHEN** the application is rendered on a narrow viewport
- **THEN** primary navigation controls remain visible or wrap without horizontal scrolling

### Requirement: Consistent route state presentation
The frontend SHALL distinguish loading, empty, error, and success states across data-backed route pages.

#### Scenario: Loading state is explicit
- **WHEN** a route is waiting for API data
- **THEN** the route displays a loading state that preserves the surrounding page context

#### Scenario: Empty state is distinct from error state
- **WHEN** an API request succeeds with no records
- **THEN** the route displays an empty state that explains no matching records are available
- **AND** it does not display an error treatment

#### Scenario: Error state supports recovery
- **WHEN** an API request fails for a route that can refetch data
- **THEN** the route displays a readable error state with a retry affordance

### Requirement: Responsive workflow layouts
The frontend SHALL keep consumer, kitchen, and operations workflows readable and actionable across desktop and mobile viewports.

#### Scenario: Restaurant browsing adapts to viewport
- **WHEN** the restaurant list or detail page renders on desktop and mobile widths
- **THEN** restaurant, menu, and cart content are arranged without overlapping controls or horizontal scrolling

#### Scenario: Order and operations rows remain scannable
- **WHEN** order history, kitchen tickets, or operations query results render multiple records
- **THEN** each record shows its status and primary action or navigation affordance in a layout that remains scannable on narrow viewports
