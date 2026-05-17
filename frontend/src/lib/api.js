const DEFAULT_HEADERS = {
  Accept: "application/json",
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
