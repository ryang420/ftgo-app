export function addItem(cart, item) {
  const existing = cart.items.find((i) => i.menu_item_id === item.menu_item_id);
  if (existing) {
    const newQty = Math.min(existing.quantity + 1, 99);
    return {
      ...cart,
      items: cart.items.map((i) =>
        i.menu_item_id === item.menu_item_id ? { ...i, quantity: newQty } : i
      ),
    };
  }
  return {
    ...cart,
    items: [...cart.items, { ...item, quantity: 1 }],
  };
}

export function removeItem(cart, menuItemId) {
  return {
    ...cart,
    items: cart.items.filter((i) => i.menu_item_id !== menuItemId),
  };
}

export function setQuantity(cart, menuItemId, qty) {
  if (qty === 0) return removeItem(cart, menuItemId);
  if (qty < 1 || qty > 99) return cart;
  const existing = cart.items.find((i) => i.menu_item_id === menuItemId);
  if (!existing) return cart;
  return {
    ...cart,
    items: cart.items.map((i) =>
      i.menu_item_id === menuItemId ? { ...i, quantity: qty } : i
    ),
  };
}

export function cartTotal(cart) {
  return cart.items.reduce((sum, item) => sum + item.unit_price * item.quantity, 0);
}

export function isCartEmpty(cart) {
  return cart.items.length === 0;
}

export function clearCart() {
  return { restaurantId: null, items: [] };
}
