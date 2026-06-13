import { useState } from "react";

export default function CartItemRow({ item, onRemove, onQuantityChange }) {
  const [qtyError, setQtyError] = useState("");

  const handleQtyChange = (newQty) => {
    setQtyError("");
    const qty = Number(newQty);
    if (qty < 1 || qty > 99) {
      setQtyError("Qty must be 1–99");
      return;
    }
    onQuantityChange(item.menu_item_id, qty);
  };

  return (
    <div className="flex items-center gap-3 py-2 text-sm">
      <div className="flex-1">
        <span className="text-stone-900">{item.name}</span>
        <span className="ml-2 text-stone-500">${Number(item.unit_price).toFixed(2)}</span>
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={() => handleQtyChange(item.quantity - 1)}
          className="flex h-7 w-7 items-center justify-center rounded-full border border-stone-200 text-stone-500 transition hover:border-orange-200 hover:text-stone-950"
        >
          −
        </button>
        <span className="w-8 text-center tabular-nums text-stone-900">{item.quantity}</span>
        <button
          onClick={() => handleQtyChange(item.quantity + 1)}
          className="flex h-7 w-7 items-center justify-center rounded-full border border-stone-200 text-stone-500 transition hover:border-orange-200 hover:text-stone-950"
        >
          +
        </button>
      </div>
      <span className="w-20 text-right tabular-nums text-stone-700">
        ${(item.unit_price * item.quantity).toFixed(2)}
      </span>
      <button
        onClick={() => onRemove(item.menu_item_id)}
        className="text-stone-500 hover:text-rose-400 transition text-xs"
      >
        ✕
      </button>
      {qtyError && <p className="col-span-full text-xs text-rose-700">{qtyError}</p>}
    </div>
  );
}
