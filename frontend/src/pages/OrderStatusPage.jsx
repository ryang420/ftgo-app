import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getOrder } from "../lib/api.js";
import StatusBadge from "../components/StatusBadge.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

const TERMINAL_STATUSES = new Set(["PREPARING", "CANCELLED"]);
const POLL_INTERVAL_MS = 5000;

export default function OrderStatusPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [status, setStatus] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [transientError, setTransientError] = useState("");

  useEffect(() => {
    let intervalId;
    let controller;

    async function fetchOrder() {
      controller = new AbortController();
      try {
        const data = await getOrder(orderId, { signal: controller.signal });
        setOrder(data);
        setStatus("success");
        setTransientError("");
        if (TERMINAL_STATUSES.has(data.status)) {
          clearInterval(intervalId);
        }
      } catch (err) {
        if (err.name === "AbortError") return;
        if (err.message.includes("404")) {
          setStatus("not_found");
          clearInterval(intervalId);
          return;
        }
        setTransientError(err.message);
      }
    }

    fetchOrder();
    intervalId = setInterval(fetchOrder, POLL_INTERVAL_MS);

    return () => {
      clearInterval(intervalId);
      controller?.abort();
    };
  }, [orderId]);

  if (status === "loading") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-12 space-y-4">
        <SkeletonBlock className="h-8 w-48" />
        <SkeletonBlock className="h-6 w-32" />
        <SkeletonBlock className="h-32 w-full" />
      </div>
    );
  }

  if (status === "not_found") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-12">
        <ErrorMessage message="Order not found" />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="mx-auto max-w-2xl px-6 py-12">
        <ErrorMessage message={errorMsg} onRetry={() => { setStatus("loading"); setErrorMsg(""); }} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-8">
      <h1 className="text-2xl font-semibold text-stone-100 mb-6">
        Order {order?.id?.slice(0, 8)}
      </h1>

      {transientError && (
        <div className="mb-4 rounded-xl border border-amber-300/20 bg-amber-500/10 p-3 text-sm text-amber-100 flex justify-between items-center">
          <span>{transientError}</span>
          <button onClick={() => setTransientError("")} className="text-amber-300 hover:text-amber-100">✕</button>
        </div>
      )}

      {order && (
        <div className="rounded-[2rem] border border-white/10 bg-white/[0.035] p-6 space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-sm text-stone-400">Status:</span>
            <StatusBadge status={order.status} />
            {order.status === "PREPARING" && (
              <p className="text-sm text-green-400">Your order is being prepared</p>
            )}
            {order.status === "CANCELLED" && (
              <p className="text-sm text-rose-400">Your order has been cancelled</p>
            )}
            {order.status === "READY" && (
              <p className="text-sm text-green-400">Your order is ready for pickup!</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-stone-500">Order ID:</span> <span className="text-stone-200 font-mono text-xs">{order.id}</span></div>
            <div><span className="text-stone-500">Restaurant:</span> <span className="text-stone-200">{order.restaurant_id}</span></div>
            <div><span className="text-stone-500">Total:</span> <span className="text-stone-200">{Number(order.total_amount).toFixed(2)} {order.currency}</span></div>
            <div><span className="text-stone-500">Created:</span> <span className="text-stone-200">{new Date(order.created_at).toLocaleString()}</span></div>
            <div className="col-span-2"><span className="text-stone-500">Delivery:</span> <span className="text-stone-200">{order.delivery_address}</span></div>
          </div>

          {order.line_items && order.line_items.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-stone-300 mb-2">Items</h3>
              <div className="space-y-2">
                {order.line_items.map((item, i) => (
                  <div key={i} className="flex justify-between text-sm text-stone-400">
                    <span>{item.name} × {item.quantity}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mt-6 flex gap-4">
        <Link
          to="/"
          className="rounded-full border border-white/10 px-5 py-2 text-sm text-stone-300 hover:text-white hover:border-white/20 transition"
        >
          ← Back to restaurants
        </Link>
        <Link
          to="/my-orders"
          className="rounded-full border border-white/10 px-5 py-2 text-sm text-stone-300 hover:text-white hover:border-white/20 transition"
        >
          My Orders
        </Link>
      </div>
    </div>
  );
}
