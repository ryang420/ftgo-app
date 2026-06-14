import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getOrder } from "../lib/api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import EmptyState from "../components/EmptyState.jsx";

const TERMINAL_STATUSES = new Set(["DELIVERED", "CANCELLED", "REJECTED"]);
const POLL_INTERVAL_MS = 5000;

export default function OrderStatusPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [status, setStatus] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [transientError, setTransientError] = useState("");

  const fetchOrder = async (signal) => {
    try {
      const data = await getOrder(orderId, { signal });
      setOrder(data);
      setStatus("success");
      setTransientError("");
      return data;
    } catch (err) {
      if (err.name === "AbortError") return null;
      if (err.message.includes("404")) {
        setStatus("not_found");
        return null;
      }
      setTransientError(err.message);
      return null;
    }
  };

  useEffect(() => {
    let active = true;
    let intervalId;

    const poll = async () => {
      const data = await fetchOrder();
      if (!active || !data) return;
      if (TERMINAL_STATUSES.has(data.status)) {
        clearInterval(intervalId);
      }
    };

    // Initial fetch
    const controller = new AbortController();
    fetchOrder(controller.signal).then((data) => {
      if (active && data && TERMINAL_STATUSES.has(data.status)) {
        clearInterval(intervalId);
      }
    });

    intervalId = setInterval(() => {
      const ctrl = new AbortController();
      poll().catch(() => {});
    }, POLL_INTERVAL_MS);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [orderId]);

  if (status === "loading") {
    return (
      <main className="mx-auto max-w-2xl px-4 py-12 sm:px-6 space-y-4">
        <SkeletonBlock className="h-8 w-48" />
        <SkeletonBlock className="h-6 w-32" />
        <SkeletonBlock className="h-32 w-full" />
      </main>
    );
  }

  if (status === "not_found") {
    return (
      <main className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <EmptyState
          title="Order not found"
          message="The order you're looking for doesn't exist or may have been removed."
          action={
            <div className="flex flex-wrap justify-center gap-3">
              <Link
                to="/"
                className="rounded-full border border-stone-200 bg-white px-5 py-2 text-sm text-stone-700 transition hover:border-orange-200 hover:text-stone-950"
              >
                ← Back to restaurants
              </Link>
              <Link
                to="/my-orders"
                className="rounded-full bg-orange-600 px-5 py-2 text-sm font-medium text-white hover:bg-orange-500 transition"
              >
                My Orders
              </Link>
            </div>
          }
        />
      </main>
    );
  }

  if (status === "error") {
    return (
      <main className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <ErrorMessage
          message={errorMsg}
          onRetry={() => {
            setStatus("loading");
            setErrorMsg("");
          }}
        />
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-semibold text-stone-950">
        Order {order?.id?.slice(0, 8)}
      </h1>

      {transientError && (
        <div className="mb-4 flex items-center justify-between rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          <span>{transientError}</span>
          <button
            onClick={() => setTransientError("")}
            className="text-amber-700 hover:text-amber-950"
          >
            ✕
          </button>
        </div>
      )}

      {order && (
        <div className="space-y-4 rounded-[2rem] border border-orange-100 bg-white p-6 shadow-card">
          <div className="flex items-center gap-3">
            <span className="text-sm text-stone-600">Status:</span>
            <StatusBadge status={order.status} />
            {order.status === "PREPARING" && (
              <p className="text-sm text-green-700">
                Your order is being prepared
              </p>
            )}
            {order.status === "CANCELLED" && (
              <p className="text-sm text-rose-700">
                Your order has been cancelled
              </p>
            )}
            {order.status === "READY" && (
              <p className="text-sm text-green-700">
                Your order is ready for delivery handoff
              </p>
            )}
            {order.status === "DELIVERY_ASSIGNED" && (
              <p className="text-sm text-blue-700">
                A courier has been assigned
              </p>
            )}
            {order.status === "OUT_FOR_DELIVERY" && (
              <p className="text-sm text-blue-700">
                Your order is on the way
              </p>
            )}
            {order.status === "DELIVERED" && (
              <p className="text-sm text-green-700">
                Your order has been delivered
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-stone-500">Order ID:</span>{" "}
              <span className="font-mono text-xs text-stone-800">
                {order.id}
              </span>
            </div>
            <div>
              <span className="text-stone-500">Restaurant:</span>{" "}
              <span className="text-stone-800">{order.restaurant_id}</span>
            </div>
            <div>
              <span className="text-stone-500">Total:</span>{" "}
              <span className="text-stone-800">
                {Number(order.total_amount).toFixed(2)} {order.currency}
              </span>
            </div>
            <div>
              <span className="text-stone-500">Created:</span>{" "}
              <span className="text-stone-800">
                {order.created_at
                  ? new Date(order.created_at).toLocaleString()
                  : "—"}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-stone-500">Delivery:</span>{" "}
              <span className="text-stone-800">{order.delivery_address}</span>
            </div>
          </div>

          {order.line_items && order.line_items.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-medium text-stone-700">
                Items
              </h3>
              <div className="space-y-2">
                {order.line_items.map((item, i) => (
                  <div
                    key={i}
                    className="flex justify-between text-sm text-stone-600"
                  >
                    <span>
                      {item.name} × {item.quantity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-4">
        <Link
          to="/"
          className="rounded-full border border-stone-200 bg-white px-5 py-2 text-sm text-stone-700 transition hover:border-orange-200 hover:text-stone-950"
        >
          ← Back to restaurants
        </Link>
        <Link
          to="/my-orders"
          className="rounded-full border border-stone-200 bg-white px-5 py-2 text-sm text-stone-700 transition hover:border-orange-200 hover:text-stone-950"
        >
          My Orders
        </Link>
      </div>
    </main>
  );
}
