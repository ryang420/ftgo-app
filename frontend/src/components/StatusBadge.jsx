const STATUS_CLASSES = {
  PENDING: "bg-amber-400/15 border-amber-300/20 text-amber-100",
  APPROVED: "bg-blue-400/15 border-blue-300/20 text-blue-100",
  PREPARING: "bg-orange-400/15 border-orange-300/20 text-orange-100",
  CANCELLED: "bg-rose-500/10 border-rose-300/20 text-rose-100",
  ACCEPTED: "bg-green-500/10 border-green-300/20 text-green-100",
  CREATE_PENDING: "bg-stone-400/15 border-stone-300/20 text-stone-100",
  READY: "bg-green-500/10 border-green-300/20 text-green-100",
};

export default function StatusBadge({ status }) {
  const cls =
    STATUS_CLASSES[status] ?? "bg-stone-400/15 border-stone-300/20 text-stone-200";
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}
