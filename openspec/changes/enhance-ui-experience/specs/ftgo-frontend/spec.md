## ADDED Requirements

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
