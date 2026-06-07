import { useState } from "react";
import { getOrdersByConsumer } from "../lib/api.js";
import OrderRow from "../components/OrderRow.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import { useNavigate } from "react-router-dom";

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

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
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="text-2xl font-semibold text-stone-100 mb-6">Consumer Lookup</h1>

      <form onSubmit={handleSubmit} className="mb-6 flex gap-3">
        <input
          type="text"
          value={uuid}
          onChange={(e) => setUuid(e.target.value)}
          placeholder="Consumer UUID"
          className="flex-1 rounded-full border border-white/10 bg-white/[0.045] px-5 py-3 text-sm text-stone-100 placeholder-stone-500 outline-none focus:border-orange-400/50"
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="rounded-full bg-orange-600 px-6 py-3 text-sm font-medium text-white hover:bg-orange-500 disabled:opacity-50 transition"
        >
          Lookup
        </button>
      </form>

      {inputError && <p className="mb-4 text-sm text-rose-400">{inputError}</p>}

      {status === "loading" && (
        <div className="text-center py-12"><LoadingSpinner /></div>
      )}

      {status === "error" && <ErrorMessage message={errorMsg} />}

      {status === "success" && orders.length === 0 && (
        <p className="text-sm text-stone-500">No orders found for this consumer</p>
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
    </div>
  );
}
