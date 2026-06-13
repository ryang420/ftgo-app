import StatusBadge from "./StatusBadge.jsx";

export function formatOrderDate(isoString) {
  if (!isoString) return "—";
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return "—";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatAmount(amount, currency) {
  return `${Number(amount).toFixed(2)} ${currency}`;
}

export function truncateId(id) {
  return id.slice(0, 8);
}

export default function OrderRow({ order, onClick, showConsumerId = false }) {
  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(order.id).catch(() => {});
  };

  return (
    <div
      onClick={onClick}
      className="cursor-pointer rounded-[1.75rem] border border-orange-100 bg-white p-5 shadow-sm transition hover:border-orange-200 hover:shadow-card"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter") onClick(); }}
    >
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <button
          onClick={handleCopy}
          className="font-mono text-xs text-stone-500 transition hover:text-stone-950"
          title="Copy order ID"
        >
          {truncateId(order.id)}
        </button>
        <StatusBadge status={order.status} />
        <span className="tabular-nums text-stone-800">
          {formatAmount(order.total_amount, order.currency)}
        </span>
        <span className="text-xs text-stone-500">
          {showConsumerId ? `Consumer ${truncateId(order.consumer_id)}` : `Restaurant ${order.restaurant_id}`}
        </span>
        <span className="ml-auto text-xs text-stone-500">
          {formatOrderDate(order.created_at)}
        </span>
      </div>
    </div>
  );
}
