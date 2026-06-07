import { useEffect, useRef, useState } from "react";
import { getOrder } from "../lib/api.js";

const TERMINAL_STATUSES = new Set(["PREPARING", "CANCELLED", "READY"]);
const POLL_INTERVAL_MS = 5000;

export default function useOrderPolling(orderId) {
  const [order, setOrder] = useState(null);
  const [status, setStatus] = useState("loading");
  const [transientError, setTransientError] = useState("");
  const intervalRef = useRef(null);
  const controllerRef = useRef(null);

  useEffect(() => {
    async function fetchOrder() {
      controllerRef.current?.abort();
      controllerRef.current = new AbortController();
      try {
        const data = await getOrder(orderId, { signal: controllerRef.current.signal });
        setOrder(data);
        setStatus("success");
        setTransientError("");
        if (TERMINAL_STATUSES.has(data.status)) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } catch (err) {
        if (err.name === "AbortError") return;
        if (err.message.includes("404")) {
          setStatus("not_found");
          clearInterval(intervalRef.current);
          intervalRef.current = null;
          return;
        }
        setTransientError(err.message);
      }
    }

    fetchOrder();
    intervalRef.current = setInterval(fetchOrder, POLL_INTERVAL_MS);

    return () => {
      clearInterval(intervalRef.current);
      controllerRef.current?.abort();
    };
  }, [orderId]);

  const dismissTransientError = () => setTransientError("");

  return { order, status, transientError, dismissTransientError };
}
