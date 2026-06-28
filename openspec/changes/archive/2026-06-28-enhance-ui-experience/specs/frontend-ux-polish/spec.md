## ADDED Requirements

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
