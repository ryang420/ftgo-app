const STATUS_CLASSES = {
  CREATE_PENDING: "bg-stone-100 border-stone-200 text-stone-700",
  PENDING: "bg-amber-100 border-amber-200 text-amber-800",
  APPROVED: "bg-blue-100 border-blue-200 text-blue-800",
  ACCEPTED: "bg-green-100 border-green-200 text-green-800",
  PREPARING: "bg-orange-100 border-orange-200 text-orange-800",
  READY: "bg-green-100 border-green-200 text-green-800",
  DELIVERY_ASSIGNED: "bg-blue-100 border-blue-200 text-blue-800",
  OUT_FOR_DELIVERY: "bg-sky-100 border-sky-200 text-sky-800",
  DELIVERED: "bg-emerald-100 border-emerald-200 text-emerald-800",
  READY_FOR_PICKUP: "bg-emerald-100 border-emerald-200 text-emerald-800",
  CANCELLED: "bg-rose-100 border-rose-200 text-rose-800",
};

const STATUS_LABELS = {
  CREATE_PENDING: "New",
  PENDING: "Pending",
  APPROVED: "Approved",
  ACCEPTED: "Accepted",
  PREPARING: "Preparing",
  READY: "Ready",
  DELIVERY_ASSIGNED: "Delivery Assigned",
  OUT_FOR_DELIVERY: "Out for Delivery",
  DELIVERED: "Delivered",
  READY_FOR_PICKUP: "Ready for Pickup",
  CANCELLED: "Cancelled",
};

export default function StatusBadge({ status }) {
  const cls =
    STATUS_CLASSES[status] ?? "bg-stone-100 border-stone-200 text-stone-700";
  const label = STATUS_LABELS[status] ?? status;
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-medium ${cls}`}
    >
      {label}
    </span>
  );
}
