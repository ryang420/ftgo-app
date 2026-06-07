const DEFAULT_HEADERS = {
  Accept: "application/json",
};

const JSON_HEADERS = {
  ...DEFAULT_HEADERS,
  "Content-Type": "application/json",
};

export async function getRestaurants({ signal } = {}) {
  const response = await fetch("/restaurants", {
    headers: DEFAULT_HEADERS,
    signal,
  });

  if (!response.ok) {
    throw new Error(`Failed to load restaurants: ${response.status}`);
  }

  return response.json();
}

export async function getRestaurant(restaurantId, { signal } = {}) {
  const response = await fetch(`/restaurants/${restaurantId}`, {
    headers: DEFAULT_HEADERS,
    signal,
  });

  if (!response.ok) {
    throw new Error(`Failed to load restaurant: ${response.status}`);
  }

  return response.json();
}

export async function getRestaurantMenuItems(restaurantId, { signal } = {}) {
  const response = await fetch(`/restaurants/${restaurantId}/menu-items`, {
    headers: DEFAULT_HEADERS,
    signal,
  });

  if (!response.ok) {
    throw new Error(`Failed to load menu items: ${response.status}`);
  }

  return response.json();
}

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

export async function prepareKitchenTicket(ticketId) {
  const response = await fetch(`/kitchen/tickets/${ticketId}/prepare`, {
    method: "POST",
    headers: JSON_HEADERS,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const err = new Error(`Failed to prepare ticket: ${response.status}`);
    err.status = response.status;
    err.body = body;
    throw err;
  }
  return response.json();
}

export async function readyForPickupKitchenTicket(ticketId) {
  const response = await fetch(`/kitchen/tickets/${ticketId}/ready-for-pickup`, {
    method: "POST",
    headers: JSON_HEADERS,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const err = new Error(`Failed to mark ticket ready: ${response.status}`);
    err.status = response.status;
    err.body = body;
    throw err;
  }
  return response.json();
}
