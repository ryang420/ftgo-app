import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getOrdersByConsumer } from "../lib/api.js";
import useConsumerSession from "../hooks/useConsumerSession.js";
import OrderRow from "../components/OrderRow.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import EmptyState from "../components/EmptyState.jsx";

export default function MyOrdersPage() {
  const { session } = useConsumerSession();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  const fetchOrders = async () => {
    if (!session) return;
    setStatus("loading");
    setErrorMsg("");
    try {
      const data = await getOrdersByConsumer(session.consumer_id);
      setOrders(data);
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message);
      setStatus("error");
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [session]);

  if (!session) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <EmptyState
          title="No consumer session"
          message="Please set up a consumer identity to view your orders."
          action={
            <Link
              to="/"
              className="inline-flex rounded-full bg-orange-600 px-5 py-2 text-sm font-medium text-white hover:bg-orange-500 transition"
            >
              Go to restaurants
            </Link>
          }
        />
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-semibold text-stone-950">My Orders</h1>

      {status === "loading" && (
        <div className="space-y-3">
          <SkeletonBlock className="h-8 w-48" />
          <SkeletonBlock className="h-16 w-full" />
          <SkeletonBlock className="h-16 w-full" />
          <SkeletonBlock className="h-16 w-full" />
        </div>
      )}

      {status === "error" && (
        <ErrorMessage message={errorMsg} onRetry={fetchOrders} />
      )}

      {status === "success" && orders.length === 0 && (
        <EmptyState
          title="No orders yet"
          message="Place your first order from the restaurant list to see it here."
          action={
            <Link
              to="/"
              className="inline-flex rounded-full bg-orange-600 px-5 py-2 text-sm font-medium text-white hover:bg-orange-500 transition"
            >
              Browse restaurants
            </Link>
          }
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
