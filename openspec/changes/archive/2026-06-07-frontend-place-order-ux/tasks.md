# Implementation Plan: Frontend Place-Order UX Polish

## Overview

Six UX fixes to the place-order flow: add-to-cart feedback, browse-first consumer entry, cross-restaurant navigation warning, address memory, order status navigation, and UI polish. Frontend-only, no backend changes.

---

## Tasks

- [x] 1. Add-to-cart inline counter feedback
  - In `frontend/src/components/MenuItemCard.jsx`:
  - [x] 1.1 Accept new `cartQuantity` prop (default 0)
    - When `cartQuantity > 0`, render inline +/- counter instead of "Add to cart" button
    - Counter shows `− {qty} +` with green background flash on mount
    - Decrement to 0 reverts to "Add to cart" button
    - _Requirements: frontend-ux-polish 1.1, 1.2, 1.3_
  - In `frontend/src/pages/RestaurantDetailPage.jsx`:
  - [x] 1.2 Pass `cartQuantity` prop to each `MenuItemCard`
    - Derive quantity from cart items map: `cart.items.find(i => i.menu_item_id === String(item.id))?.quantity || 0`
    - _Requirements: frontend-ux-polish 1.2_

- [x] 2. Browse-first consumer entry
  - In `frontend/src/components/ConsumerSetupModal.jsx`:
  - [x] 2.1 Add dismissible banner mode
    - Support `mode="banner"` prop: render as top bar instead of full-screen overlay
    - Banner has dismiss button (✕); sets `dismissed` state
    - On form submit: same behavior as modal (creates consumer, sets session)
    - _Requirements: frontend-ux-polish 2.1, 2.3_
  - In `frontend/src/App.jsx`:
  - [x] 2.2 Render banner when session is null (instead of blocking modal)
    - Show `ConsumerSetupModal mode="banner"` in App layout
    - Keep the existing modal as fallback when user clicks "Add to cart" without session
    - _Requirements: frontend-ux-polish 2.1, 2.2_

- [x] 3. Cross-restaurant cart navigation warning
  - In `frontend/src/pages/RestaurantDetailPage.jsx`:
  - [x] 3.1 Show confirmation dialog when navigating to different restaurant with non-empty cart
    - Track pending navigation with `useRef`
    - Render inline dialog: "Your cart will be cleared. Continue?" with Confirm/Cancel
    - On Confirm: clear cart, navigate. On Cancel: stay on current page
    - _Requirements: frontend-ux-polish 3.1, 3.2, 3.3_

- [x] 4. Delivery address memory
  - [x] 4.1 Create `frontend/src/lib/address.js`
    - `readAddress()` → returns saved address string or `""`
    - `writeAddress(address)` → saves to localStorage key `"ftgo_last_delivery_address"`
    - _Requirements: frontend-ux-polish 4.1, 4.2_
  - In `frontend/src/components/OrderConfirmationDrawer.jsx`:
  - [x] 4.2 Pre-fill address from localStorage and save on successful order
    - Initialize `address` state from `readAddress()`
    - After successful `placeOrder`, call `writeAddress(address)`
    - _Requirements: frontend-ux-polish 4.1, 4.2_

- [x] 5. Order status page navigation links
  - In `frontend/src/pages/OrderStatusPage.jsx`:
  - [x] 5.1 Add navigation links below order details
    - "Back to restaurants" Link to `/`
    - "My Orders" Link to `/my-orders`
    - _Requirements: frontend-ux-polish 5.1_

- [x] 6. UI polish
  - In `frontend/src/components/MenuItemCard.jsx`:
  - [x] 6.1 Remove "Menu item ID: {id}" line from card display
    - _Requirements: frontend-ux-polish 6.1_
  - In `frontend/src/components/CartPanel.jsx`:
  - [x] 6.2 Show item count badge in header ("Your Cart (3)")
    - _Requirements: frontend-ux-polish 6.2_

- [x] 7. Final checkpoint
  - Run `cd frontend && npx vite build` to verify build
  - Manually verify: add-to-cart feedback, banner dismiss, nav warning, address pre-fill

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["4.1"] },
    { "id": 1, "tasks": ["1.1", "1.2", "2.1", "6.1", "6.2"] },
    { "id": 2, "tasks": ["2.2", "3.1", "4.2", "5.1"] }
  ]
}
```
