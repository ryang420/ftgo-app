const STATUS_CLASSES = {
  PENDING: "bg-amber-100 border-amber-200 text-amber-800",
  APPROVED: "bg-blue-100 border-blue-200 text-blue-800",
  PREPARING: "bg-orange-100 border-orange-200 text-orange-800",
  CANCELLED: "bg-rose-100 border-rose-200 text-rose-800",
  ACCEPTED: "bg-green-100 border-green-200 text-green-800",
  CREATE_PENDING: "bg-stone-100 border-stone-200 text-stone-700",
  READY: "bg-green-100 border-green-200 text-green-800",
};

export default function StatusBadge({ status }) {
  const cls =
    STATUS_CLASSES[status] ?? "bg-stone-100 border-stone-200 text-stone-700";
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}
