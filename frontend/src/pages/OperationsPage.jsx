import { useEffect, useState } from "react";
import { getOrdersByStatus } from "../lib/api.js";
import { useNavigate } from "react-router-dom";
import OrderRow from "../components/OrderRow.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import EmptyState from "../components/EmptyState.jsx";

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

  useEffect(() => {
    fetchOrders(selectedStatus);
  }, [selectedStatus]);

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-semibold text-stone-950">
        Operations
      </h1>

      <div className="mb-6">
        <p className="mb-3 text-sm text-stone-500">Filter by status</p>
        <div className="flex flex-wrap gap-2">
          {STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => setSelectedStatus(s)}
              className={`rounded-full px-4 py-1.5 text-xs font-medium transition ${
                selectedStatus === s
                  ? "bg-orange-600 text-white shadow-sm"
                  : "border border-stone-200 bg-white text-stone-700 hover:border-orange-200 hover:text-stone-950"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {viewStatus === "loading" && (
        <div className="space-y-3">
          <SkeletonBlock className="h-16 w-full" />
          <SkeletonBlock className="h-16 w-full" />
          <SkeletonBlock className="h-16 w-full" />
        </div>
      )}

      {viewStatus === "error" && (
        <ErrorMessage
          message={errorMsg}
          onRetry={() => fetchOrders(selectedStatus)}
        />
      )}

      {viewStatus === "success" && orders.length === 0 && (
        <EmptyState
          title={`No ${selectedStatus.toLowerCase()} orders`}
          message="There are no orders with this status right now."
        />
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
    </main>
  );
}
