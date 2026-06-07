import { createContext, useCallback, useEffect, useState } from "react";
import { readSession, writeSession, clearSession } from "../lib/session.js";

export const ConsumerSessionContext = createContext(null);

export function ConsumerSessionProvider({ children }) {
  const [session, setSessionState] = useState(() => readSession());

  useEffect(() => {
    const stored = readSession();
    setSessionState(stored);
  }, []);

  const setSession = useCallback((s) => {
    writeSession(s);
    setSessionState(s);
  }, []);

  const clear = useCallback(() => {
    clearSession();
    setSessionState(null);
  }, []);

  return (
    <ConsumerSessionContext.Provider value={{ session, setSession, clearSession: clear }}>
      {children}
    </ConsumerSessionContext.Provider>
  );
}
