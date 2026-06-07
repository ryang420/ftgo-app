## Why

The place-order flow works functionally but has poor interaction design. Add-to-cart gives zero visual feedback, the consumer setup modal blocks all browsing, the cart clears silently on navigation, delivery addresses must be retyped every order, and the order status page is a dead-end after placing an order. These friction points make the app feel unpolished and break user flow.

## What Changes

- **Add-to-cart inline feedback**: Button transforms into an inline +/- quantity counter on click, with brief green flash confirmation
- **Browse-first consumer setup**: Replace blocking modal with a dismissible top banner; users can explore restaurants before creating an identity
- **Cross-restaurant cart warning**: Show confirmation dialog before clearing cart when navigating to a different restaurant
- **Address memory**: Persist last delivery address to localStorage and pre-fill on next order
- **Order status navigation**: Add "Back to restaurants" and "My Orders" links so the page is not a dead-end
- **UI polish**: Remove developer-facing "Menu item ID" from cards, show cart count badge in header

## Capabilities

### New Capabilities
- `frontend-ux-polish`: Add-to-cart feedback, browse-first consumer entry, cart navigation warnings, address memory, and order status navigation links. Frontend-only changes with no backend impact.

### Modified Capabilities
None — no backend changes, no spec-level requirement changes to existing capabilities.

## Impact

| Layer | Impact |
|-------|--------|
| `frontend/src/components/` | MenuItemCard (+/- counter), ConsumerSetupModal (banner mode), CartPanel (sticky, badge) |
| `frontend/src/pages/` | RestaurantDetailPage (nav warning), OrderStatusPage (nav links), App.jsx (banner wiring) |
| `frontend/src/lib/` | New `address.js` (localStorage persistence) |
| Backend | No changes |
| `libs/common/` | No changes |
