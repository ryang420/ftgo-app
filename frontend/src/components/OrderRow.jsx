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
      className="cursor-pointer rounded-[1.75rem] border border-white/10 bg-white/[0.035] p-5 transition hover:bg-white/[0.06]"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter") onClick(); }}
    >
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <button
          onClick={handleCopy}
          className="font-mono text-xs text-stone-400 hover:text-stone-200 transition"
          title="Copy order ID"
        >
          {truncateId(order.id)}
        </button>
        <StatusBadge status={order.status} />
        <span className="text-stone-200 tabular-nums">
          {formatAmount(order.total_amount, order.currency)}
        </span>
        <span className="text-stone-500 text-xs">
          {showConsumerId ? `Consumer ${truncateId(order.consumer_id)}` : `Restaurant ${order.restaurant_id}`}
        </span>
        <span className="ml-auto text-stone-500 text-xs">
          {formatOrderDate(order.created_at)}
        </span>
      </div>
    </div>
  );
}
