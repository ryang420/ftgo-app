const ADDRESS_KEY = "ftgo_last_delivery_address";

export function readAddress() {
  try {
    const raw = localStorage.getItem(ADDRESS_KEY);
    return typeof raw === "string" ? raw : "";
  } catch {
    return "";
  }
}

export function writeAddress(address) {
  try {
    localStorage.setItem(ADDRESS_KEY, address);
  } catch {
    // localStorage unavailable — silently ignore
  }
}
