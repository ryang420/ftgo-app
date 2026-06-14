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
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import EmptyState from "../components/EmptyState.jsx";

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

  useEffect(() => {
    fetchTickets();
  }, []);

  const makeHandler = (apiCall, targetStatus) => async (ticketId) => {
    setPendingTickets((prev) => new Set(prev).add(ticketId));
    setRowErrors((prev) => {
      const n = { ...prev };
      delete n[ticketId];
      return n;
    });
    try {
      await apiCall(ticketId);
      setTickets((prev) =>
        prev.map((t) =>
          t.id === ticketId ? { ...t, status: targetStatus } : t
        )
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
      setPendingTickets((prev) => {
        const n = new Set(prev);
        n.delete(ticketId);
        return n;
      });
    }
  };

  const handleAccept = makeHandler(acceptKitchenTicket, "ACCEPTED");
  const handleReject = makeHandler(rejectKitchenTicket, "CANCELLED");
  const handlePrepare = makeHandler(prepareKitchenTicket, "PREPARING");
  const handleReady = makeHandler(
    readyForPickupKitchenTicket,
    "READY_FOR_PICKUP"
  );

  const actionableTickets = tickets.filter(
    (t) => !TERMINAL_TICKET_STATUSES.has(t.status)
  );
  const readOnlyTickets = tickets.filter((t) =>
    TERMINAL_TICKET_STATUSES.has(t.status)
  );

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-stone-950">
          Kitchen Dashboard
        </h1>
        <button
          onClick={fetchTickets}
          className="rounded-full border border-stone-200 bg-white px-4 py-2 text-xs text-stone-700 transition hover:border-orange-200 hover:text-stone-950"
        >
          Refresh
        </button>
      </div>

      {globalError && (
        <div className="mb-4 flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <span>{globalError}</span>
          <button
            onClick={() => setGlobalError("")}
            className="text-rose-700 hover:text-rose-950"
          >
            ✕
          </button>
        </div>
      )}

      {status === "loading" && (
        <div className="space-y-4">
          <SkeletonBlock className="h-6 w-32" />
          <SkeletonBlock className="h-20 w-full" />
          <SkeletonBlock className="h-20 w-full" />
          <SkeletonBlock className="h-6 w-32" />
          <SkeletonBlock className="h-20 w-full" />
        </div>
      )}

      {status === "error" && (
        <ErrorMessage message={errorMsg} onRetry={fetchTickets} />
      )}

      {status === "success" && (
        <>
          {/* Actionable tickets */}
          <section className="mb-8">
            <div className="mb-3 flex items-center gap-3">
              <h2 className="text-lg font-medium text-stone-800">
                Needs Action
              </h2>
              {actionableTickets.length > 0 && (
                <span className="rounded-full bg-orange-100 px-2.5 py-0.5 text-xs font-medium text-orange-700">
                  {actionableTickets.length}
                </span>
              )}
            </div>
            {actionableTickets.length === 0 ? (
              <EmptyState
                title="All caught up"
                message="No tickets need action right now."
              />
            ) : (
              <div className="space-y-3">
                {actionableTickets.map((t) => (
                  <TicketRow
                    key={t.id}
                    ticket={t}
                    pending={pendingTickets.has(t.id)}
                    error={rowErrors[t.id]}
                    onAccept={() => handleAccept(t.id)}
                    onReject={() => handleReject(t.id)}
                    onPrepare={() => handlePrepare(t.id)}
                    onReady={() => handleReady(t.id)}
                  />
                ))}
              </div>
            )}
          </section>

          {/* Completed / terminal tickets */}
          <section>
            <div className="mb-3 flex items-center gap-3">
              <h2 className="text-lg font-medium text-stone-500">Completed</h2>
              {readOnlyTickets.length > 0 && (
                <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-xs font-medium text-stone-500">
                  {readOnlyTickets.length}
                </span>
              )}
            </div>
            {readOnlyTickets.length === 0 ? (
              <p className="text-sm text-stone-400">No completed tickets yet</p>
            ) : (
              <div className="space-y-3">
                {readOnlyTickets.map((t) => (
                  <div
                    key={t.id}
                    className="rounded-[1.5rem] border border-stone-200 bg-stone-50 p-4 opacity-70"
                  >
                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span className="font-mono text-xs text-stone-400">
                        {t.id?.slice(0, 8)}
                      </span>
                      <span className="text-stone-400">
                        Order {t.order_id?.slice(0, 8)}
                      </span>
                      <StatusBadge status={t.status} />
                      <span className="text-stone-400">
                        Restaurant {t.restaurant_id}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}

function TicketRow({
  ticket,
  pending,
  error,
  onAccept,
  onReject,
  onPrepare,
  onReady,
}) {
  return (
    <div className="rounded-[1.5rem] border border-orange-100 bg-white p-4 shadow-sm transition hover:border-orange-200">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="font-mono text-xs text-stone-500">
          {ticket.id?.slice(0, 8)}
        </span>
        <span className="text-stone-500">
          Order {ticket.order_id?.slice(0, 8)}
        </span>
        <StatusBadge status={ticket.status} />
        <span className="text-stone-500">
          Restaurant {ticket.restaurant_id}
        </span>

        <div className="ml-auto flex items-center gap-2">
          {pending && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs text-amber-700">
              <LoadingSpinner />
              Updating…
            </span>
          )}
          {!pending && ticket.status === "CREATE_PENDING" && (
            <>
              <button
                onClick={onAccept}
                className="rounded-full bg-green-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-green-500 transition"
              >
                Accept
              </button>
              <button
                onClick={onReject}
                className="rounded-full bg-rose-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-rose-500 transition"
              >
                Reject
              </button>
            </>
          )}
          {!pending && ticket.status === "ACCEPTED" && (
            <button
              onClick={onPrepare}
              className="rounded-full bg-blue-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-blue-500 transition"
            >
              Prepare
            </button>
          )}
          {!pending && ticket.status === "PREPARING" && (
            <button
              onClick={onReady}
              className="rounded-full bg-green-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-green-500 transition"
            >
              Ready for Pickup
            </button>
          )}
        </div>
      </div>
      {error && <p className="mt-2 text-xs text-rose-700">{error}</p>}
    </div>
  );
}
