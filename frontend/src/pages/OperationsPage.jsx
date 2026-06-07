import { useEffect, useState } from "react";
import { getOrdersByStatus } from "../lib/api.js";
import { useNavigate } from "react-router-dom";
import OrderRow from "../components/OrderRow.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

const STATUSES = ["PENDING", "APPROVED", "PREPARING", "CANCELLED"];

export default function OperationsPage() {
  const [selectedStatus, setSelectedStatus] = useState("PENDING");
  const [orders, setOrders] = useState([]);
  const [viewStatus, setViewStatus] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();

  const fetchOrders = async (status) => {
    setViewStatus("loading");
    setErrorMsg("");
    try {
      const data = await getOrdersByStatus(status);
      setOrders(data);
      setViewStatus("success");
    } catch (err) {
      setErrorMsg(err.message);
      setViewStatus("error");
    }
  };

  useEffect(() => { fetchOrders(selectedStatus); }, [selectedStatus]);

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="text-2xl font-semibold text-stone-100 mb-6">Operations</h1>

      <div className="flex gap-2 mb-6">
        {STATUSES.map((s) => (
          <button
            key={s}
            onClick={() => setSelectedStatus(s)}
            className={`rounded-full px-4 py-1.5 text-xs font-medium transition ${
              selectedStatus === s
                ? "bg-orange-600 text-white"
                : "border border-white/10 text-stone-300 hover:text-white"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {viewStatus === "loading" && (
        <div className="text-center py-12"><LoadingSpinner /></div>
      )}

      {viewStatus === "error" && (
        <ErrorMessage message={errorMsg} onRetry={() => fetchOrders(selectedStatus)} />
      )}

      {viewStatus === "success" && orders.length === 0 && (
        <p className="text-sm text-stone-500">No orders with this status</p>
      )}

      {viewStatus === "success" && orders.length > 0 && (
        <div className="space-y-3">
          {orders.map((o) => (
            <OrderRow
              key={o.id}
              order={o}
              onClick={() => navigate(`/orders/${o.id}`)}
              showConsumerId
            />
          ))}
        </div>
      )}
    </div>
  );
}
