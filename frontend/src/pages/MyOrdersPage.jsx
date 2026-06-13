import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getOrdersByConsumer } from "../lib/api.js";
import useConsumerSession from "../hooks/useConsumerSession.js";
import OrderRow from "../components/OrderRow.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

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

  useEffect(() => { fetchOrders(); }, [session]);

  if (!session) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-12">
        <p className="text-center text-stone-500">Redirecting...</p>
      </div>
    );
  }

  if (status === "loading") {
    return (
      <div className="mx-auto max-w-4xl px-6 py-8 space-y-3">
        <SkeletonBlock className="h-8 w-48" />
        <SkeletonBlock className="h-16 w-full" />
        <SkeletonBlock className="h-16 w-full" />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="mx-auto max-w-4xl px-6 py-8">
        <ErrorMessage message={errorMsg} onRetry={fetchOrders} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="mb-6 text-2xl font-semibold text-stone-950">My Orders</h1>
      {orders.length === 0 ? (
        <p className="text-sm text-stone-500">No orders yet</p>
      ) : (
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
