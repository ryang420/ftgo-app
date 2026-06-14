import { useState } from "react";
import { getOrdersByConsumer } from "../lib/api.js";
import OrderRow from "../components/OrderRow.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import EmptyState from "../components/EmptyState.jsx";
import { useNavigate } from "react-router-dom";

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export default function ConsumerLookupPage() {
  const [uuid, setUuid] = useState("");
  const [inputError, setInputError] = useState("");
  const [orders, setOrders] = useState([]);
  const [status, setStatus] = useState("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setInputError("");
    if (!UUID_RE.test(uuid)) {
      setInputError("Please enter a valid UUID");
      return;
    }
    setStatus("loading");
    setErrorMsg("");
    try {
      const data = await getOrdersByConsumer(uuid);
      setOrders(data);
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message);
      setStatus("error");
    }
  };

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-semibold text-stone-950">
        Consumer Lookup
      </h1>

      <form onSubmit={handleSubmit} className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          value={uuid}
          onChange={(e) => setUuid(e.target.value)}
          placeholder="Consumer UUID"
          className="min-w-0 flex-1 rounded-full border border-stone-200 bg-white px-5 py-3 text-sm text-stone-900 placeholder-stone-400 outline-none focus:border-orange-500"
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="rounded-full bg-orange-600 px-6 py-3 text-sm font-medium text-white hover:bg-orange-500 disabled:opacity-50 transition"
        >
          Lookup
        </button>
      </form>

      {inputError && <p className="mb-4 text-sm text-rose-700">{inputError}</p>}

      {status === "idle" && (
        <EmptyState
          title="Look up consumer orders"
          message="Enter a consumer UUID to view their order history."
        />
      )}

      {status === "loading" && (
        <div className="space-y-3">
          <SkeletonBlock className="h-16 w-full" />
          <SkeletonBlock className="h-16 w-full" />
          <SkeletonBlock className="h-16 w-full" />
        </div>
      )}

      {status === "error" && (
        <ErrorMessage message={errorMsg} />
      )}

      {status === "success" && orders.length === 0 && (
        <EmptyState
          title="No orders found"
          message="This consumer has no orders yet."
        />
      )}

      {status === "success" && orders.length > 0 && (
        <div className="space-y-3">
          {orders.map((o) => (
            <OrderRow
              key={o.id}
              order={o}
              onClick={() => navigate(`/orders/${o.id}`)}
            />
          ))}
        </div>
      )}
    </main>
  );
}
