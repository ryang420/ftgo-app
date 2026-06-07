import { useEffect, useState } from "react";
import {
  getKitchenTickets,
  acceptKitchenTicket,
  rejectKitchenTicket,
  prepareKitchenTicket,
  readyForPickupKitchenTicket,
} from "../lib/api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

const TERMINAL_TICKET_STATUSES = new Set(["READY_FOR_PICKUP", "CANCELLED"]);

export default function KitchenDashboardPage() {
  const [tickets, setTickets] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [pendingTickets, setPendingTickets] = useState(new Set());
  const [rowErrors, setRowErrors] = useState({});
  const [globalError, setGlobalError] = useState("");

  const fetchTickets = async () => {
    setStatus("loading");
    setErrorMsg("");
    try {
      const data = await getKitchenTickets();
      setTickets(data);
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message);
      setStatus("error");
    }
  };

  useEffect(() => { fetchTickets(); }, []);

  const makeHandler = (apiCall, targetStatus) => async (ticketId) => {
    setPendingTickets((prev) => new Set(prev).add(ticketId));
    setRowErrors((prev) => { const n = { ...prev }; delete n[ticketId]; return n; });
    try {
      await apiCall(ticketId);
      setTickets((prev) =>
        prev.map((t) => (t.id === ticketId ? { ...t, status: targetStatus } : t))
      );
    } catch (err) {
      if (err.status === 409) {
        setRowErrors((prev) => ({
          ...prev,
          [ticketId]: `Conflict: ${err.body?.current_status || "?"} → ${err.body?.target_status || "?"}`,
        }));
      } else {
        setGlobalError(err.message);
      }
    } finally {
      setPendingTickets((prev) => { const n = new Set(prev); n.delete(ticketId); return n; });
    }
  };

  const handleAccept = makeHandler(acceptKitchenTicket, "ACCEPTED");
  const handleReject = makeHandler(rejectKitchenTicket, "CANCELLED");
  const handlePrepare = makeHandler(prepareKitchenTicket, "PREPARING");
  const handleReady = makeHandler(readyForPickupKitchenTicket, "READY_FOR_PICKUP");

  const actionableTickets = tickets.filter(
    (t) => !TERMINAL_TICKET_STATUSES.has(t.status)
  );
  const readOnlyTickets = tickets.filter((t) =>
    TERMINAL_TICKET_STATUSES.has(t.status)
  );

  if (status === "loading") {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12 text-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12">
        <ErrorMessage message={errorMsg} onRetry={fetchTickets} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-stone-100">Kitchen Dashboard</h1>
        <button
          onClick={fetchTickets}
          className="rounded-full border border-white/10 px-4 py-2 text-xs text-stone-300 hover:text-white hover:border-white/20 transition"
        >
          Refresh
        </button>
      </div>

      {globalError && (
        <div className="mb-4 rounded-xl border border-rose-300/20 bg-rose-500/10 p-3 text-sm text-rose-100 flex justify-between items-center">
          <span>{globalError}</span>
          <button onClick={() => setGlobalError("")} className="text-rose-300 hover:text-rose-100">✕</button>
        </div>
      )}

      <section className="mb-8">
        <h2 className="text-lg font-medium text-stone-200 mb-3">Actionable</h2>
        {actionableTickets.length === 0 ? (
          <p className="text-sm text-stone-500">No tickets at the moment</p>
        ) : (
          <div className="space-y-3">
            {actionableTickets.map((t) => (
              <div
                key={t.id}
                className="rounded-[1.5rem] border border-white/10 bg-white/[0.035] p-4"
              >
                <div className="flex flex-wrap items-center gap-3 text-sm">
                  <span className="font-mono text-xs text-stone-400">{t.id?.slice(0, 8)}</span>
                  <span className="text-stone-500">Order {t.order_id?.slice(0, 8)}</span>
                  <StatusBadge status={t.status} />
                  <span className="text-stone-500">Restaurant {t.restaurant_id}</span>
                  <div className="ml-auto flex gap-2">
                    {t.status === "CREATE_PENDING" && (
                      <>
                        <button
                          onClick={() => handleAccept(t.id)}
                          disabled={pendingTickets.has(t.id)}
                          className="rounded-full bg-green-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-green-500 disabled:opacity-50 transition"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleReject(t.id)}
                          disabled={pendingTickets.has(t.id)}
                          className="rounded-full bg-rose-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-rose-500 disabled:opacity-50 transition"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {t.status === "ACCEPTED" && (
                      <button
                        onClick={() => handlePrepare(t.id)}
                        disabled={pendingTickets.has(t.id)}
                        className="rounded-full bg-blue-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-blue-500 disabled:opacity-50 transition"
                      >
                        Prepare
                      </button>
                    )}
                    {t.status === "PREPARING" && (
                      <button
                        onClick={() => handleReady(t.id)}
                        disabled={pendingTickets.has(t.id)}
                        className="rounded-full bg-green-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-green-500 disabled:opacity-50 transition"
                      >
                        Ready for Pickup
                      </button>
                    )}
                  </div>
                </div>
                {rowErrors[t.id] && (
                  <p className="mt-2 text-xs text-rose-400">{rowErrors[t.id]}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-medium text-stone-200 mb-3">Completed</h2>
        {readOnlyTickets.length === 0 ? (
          <p className="text-sm text-stone-500">No tickets</p>
        ) : (
          <div className="space-y-3">
            {readOnlyTickets.map((t) => (
              <div
                key={t.id}
                className="rounded-[1.5rem] border border-white/10 bg-white/[0.025] p-4"
              >
                <div className="flex flex-wrap items-center gap-3 text-sm">
                  <span className="font-mono text-xs text-stone-500">{t.id?.slice(0, 8)}</span>
                  <span className="text-stone-500">Order {t.order_id?.slice(0, 8)}</span>
                  <StatusBadge status={t.status} />
                  <span className="text-stone-500">Restaurant {t.restaurant_id}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
