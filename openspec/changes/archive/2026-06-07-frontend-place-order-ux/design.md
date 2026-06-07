# Design Document — Frontend Place-Order UX Polish

## Context

The place-order flow (ftgo-frontend + order-lifecycle-completion) is functionally complete. However, several interaction design issues make the user experience feel rough: no add-to-cart feedback, blocking consumer setup modal, silent cart clearing, no address memory, and dead-end order status page. This design addresses six high-impact UX fixes without changing any backend code.

## Goals / Non-Goals

**Goals:**
- Instant visual feedback when adding items to cart (button → counter transition)
- Users can browse restaurants before creating a consumer identity
- Warn before clearing cart on cross-restaurant navigation
- Remember delivery address between orders
- Order status page links back to restaurants and my-orders
- Remove developer-facing "Menu item ID" noise

**Non-Goals:**
- No backend changes
- No new npm dependencies
- No two-step order confirmation (deferred to future iteration)
- No sticky cart panel CSS overhaul (deferred)
- No cart state persistence across page reloads

## Decisions

### Decision 1: Button transforms to inline counter

When an item is added to cart, the "Add to cart" button on `MenuItemCard` transforms into an inline `+/−` quantity counter. This gives instant confirmation — the user sees the button change to show "− 2 +" right where they clicked. A brief CSS transition (green background flash) provides the micro-interaction confirmation.

**Rationale**: This is the standard pattern used by food delivery apps (DoorDash, UberEats). The counter stays on the item card as long as quantity > 0. Decrementing to 0 reverts to the button.

**Alternative**: Toast notification. Rejected because it requires an additional component and the user's attention shifts away from the menu.

### Decision 2: Consumer setup as a banner, not a modal

Replace the full-screen blocking modal with a top banner bar. The banner is dismissible (✕). When dismissed, the user can browse restaurants freely. Clicking "Add to cart" without a session re-opens the banner. The banner auto-hides when a session is created.

**Rationale**: The current modal prevents any exploration before committing identity. A banner lets curious users see what's available first — more like the real-world experience of walking into a food court before deciding what to order.

### Decision 3: Address saved to localStorage

Use `localStorage` key `"ftgo_last_delivery_address"` to persist the last address. Read on mount of `OrderConfirmationDrawer`, write on successful order placement.

**Rationale**: Simple, no backend changes. Matches the existing `ConsumerSession` localStorage pattern.

### Decision 4: Navigation warning via `window.confirm` or state flag

The simplest approach: a state flag `showNavWarning` in `RestaurantDetailPage`. When the user clicks a link to another restaurant (`restaurantId` param changes), check if cart is non-empty. If so, show an inline confirmation before proceeding. Implementation via React Router's `useBlocker` or a manual pending-nav ref.

## Files Changed

| File | Change |
|------|--------|
| `MenuItemCard.jsx` | Accept `cartQuantity` prop; render counter or button |
| `ConsumerSetupModal.jsx` | Dual-mode: banner + modal via `mode` prop |
| `CartPanel.jsx` | Show item count badge in header |
| `RestaurantDetailPage.jsx` | Cross-restaurant warning logic; pass `cartQuantity` to MenuItemCard |
| `OrderConfirmationDrawer.jsx` | Read/write address from localStorage |
| `OrderStatusPage.jsx` | Add "Back to restaurants" and "My Orders" links |
| `App.jsx` | Wire consumer banner alongside modal |
| `lib/address.js` (new) | `readAddress()`, `writeAddress(address)` |
