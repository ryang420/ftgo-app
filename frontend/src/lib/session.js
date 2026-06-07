const SESSION_KEY = "ftgo_consumer_session";
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function readSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (raw === null) return null;
    const parsed = JSON.parse(raw);
    if (
      parsed &&
      typeof parsed === "object" &&
      typeof parsed.consumer_id === "string" &&
      UUID_RE.test(parsed.consumer_id)
    ) {
      return {
        consumer_id: parsed.consumer_id,
        display_name: typeof parsed.display_name === "string" ? parsed.display_name : "",
      };
    }
    localStorage.removeItem(SESSION_KEY);
    return null;
  } catch {
    localStorage.removeItem(SESSION_KEY);
    return null;
  }
}

export function writeSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}
