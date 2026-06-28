## ADDED Requirements

### Requirement: Add-to-cart interaction feedback
The frontend SHALL provide immediate visual confirmation when an item is added to the cart.

#### Scenario: Button transforms on add
- **WHEN** the user clicks "Add to cart" on a menu item
- **THEN** the button transforms into an inline +/- quantity counter showing the current quantity
- **AND** the counter background briefly flashes green to confirm the action

#### Scenario: Counter reflects cart state
- **WHEN** a menu item is already in the cart with quantity N
- **THEN** the item card SHALL render the inline +/- counter (not the "Add to cart" button)

#### Scenario: Counter removed when quantity reaches zero
- **WHEN** the user decrements a counter from 1 to 0
- **THEN** the counter reverts to the "Add to cart" button

### Requirement: Browse-first consumer entry
The frontend SHALL allow users to browse restaurants before creating a consumer identity.

#### Scenario: Banner shown when no session
- **WHEN** no valid consumer session exists
- **THEN** a dismissible top banner SHALL prompt the user to enter their name
- **AND** the restaurant list SHALL remain visible and interactive beneath it

#### Scenario: Add-to-cart prompts setup
- **WHEN** a user without a session clicks "Add to cart"
- **THEN** the consumer setup banner SHALL highlight or re-appear with a call-to-action

#### Scenario: Banner dismissed
- **WHEN** the user dismisses the banner or creates a session
- **THEN** the banner SHALL be hidden and all add-to-cart buttons SHALL be enabled

### Requirement: Cross-restaurant cart navigation warning
The frontend SHALL warn users before discarding cart contents when navigating to a different restaurant.

#### Scenario: Warning shown on cross-restaurant navigation
- **WHEN** the user navigates to a different restaurant while the cart is non-empty
- **THEN** a confirmation dialog SHALL warn that the cart will be cleared

#### Scenario: Confirmation clears cart
- **WHEN** the user confirms navigation in the dialog
- **THEN** the cart SHALL be cleared and navigation SHALL proceed

#### Scenario: Cancellation preserves cart
- **WHEN** the user cancels the dialog
- **THEN** the cart SHALL remain unchanged and the user SHALL stay on the current page

### Requirement: Delivery address memory
The frontend SHALL remember the last-used delivery address.

#### Scenario: Address pre-filled on repeat orders
- **WHEN** a user has previously placed an order with a delivery address
- **THEN** the OrderConfirmationDrawer SHALL pre-fill the address field with the last-used value

#### Scenario: Address persisted across sessions
- **WHEN** a new order is placed with a delivery address
- **THEN** the address SHALL be saved to localStorage for future pre-filling

### Requirement: Order status page navigation
The OrderStatusPage SHALL provide navigation links back to the main app.

#### Scenario: Navigation links rendered
- **WHEN** the OrderStatusPage renders
- **THEN** it SHALL display links to "Back to restaurants" and "My Orders"

### Requirement: UI polish
The frontend SHALL remove developer-facing identifiers from consumer-facing views and show relevant status indicators.

#### Scenario: Menu item ID hidden
- **WHEN** a MenuItemCard renders
- **THEN** it SHALL NOT display "Menu item ID: N" to the user

#### Scenario: Cart count in header
- **WHEN** the cart is non-empty on the restaurant detail page
- **THEN** the CartPanel header SHALL display the total item count

### Requirement: Polished user-facing state surfaces
The frontend SHALL provide user-facing copy and visual treatment for important empty, loading, error, and success states instead of leaving sparse or developer-oriented screens.

#### Scenario: Restaurant list empty state
- **WHEN** the restaurant list loads successfully with no restaurants
- **THEN** the page displays an empty state that explains no restaurants are available

#### Scenario: Order history empty state
- **WHEN** a consumer with a valid session has no returned orders
- **THEN** the My Orders page displays an empty state with a clear path back to restaurant browsing

#### Scenario: Order placement success state
- **WHEN** an order is created successfully
- **THEN** the transition to order status includes clear confirmation that the order was placed

### Requirement: Operational scanability
The frontend SHALL make kitchen and operations records easy to scan by grouping records and emphasizing actionable status.

#### Scenario: Kitchen tickets grouped by actionability
- **WHEN** the kitchen dashboard loads tickets with mixed statuses
- **THEN** actionable tickets are visually separated from read-only or completed tickets
- **AND** each actionable ticket exposes accept and reject actions without hiding ticket status

#### Scenario: Operations filters show selected context
- **WHEN** an operations user selects a status filter
- **THEN** the selected status is visually distinct
- **AND** the result area communicates whether it is loading, empty, failed, or showing records for that selected status

#### Scenario: Status treatment is consistent
- **WHEN** orders or tickets render in consumer, kitchen, or operations views
- **THEN** equivalent statuses use consistent labels and visual emphasis across views

### Requirement: Form and action feedback
The frontend SHALL keep form submissions and button actions understandable during pending, failed, and completed states.

#### Scenario: Pending form submission disables duplicate action
- **WHEN** a user submits a form or mutation-backed action
- **THEN** the triggering action indicates progress and prevents duplicate submissions until the request resolves

#### Scenario: Failed form submission preserves input
- **WHEN** a form submission fails
- **THEN** user-entered input remains available for correction or retry

#### Scenario: Completed action updates local view state
- **WHEN** a kitchen ticket action or order-related action succeeds
- **THEN** the visible view updates to reflect the new state without requiring a full page reload
