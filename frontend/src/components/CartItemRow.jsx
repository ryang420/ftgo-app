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
        <span className="text-stone-200">{item.name}</span>
        <span className="ml-2 text-stone-500">${Number(item.unit_price).toFixed(2)}</span>
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={() => handleQtyChange(item.quantity - 1)}
          className="rounded-full border border-white/10 w-7 h-7 flex items-center justify-center text-stone-400 hover:text-white transition"
        >
          −
        </button>
        <span className="w-8 text-center text-stone-200 tabular-nums">{item.quantity}</span>
        <button
          onClick={() => handleQtyChange(item.quantity + 1)}
          className="rounded-full border border-white/10 w-7 h-7 flex items-center justify-center text-stone-400 hover:text-white transition"
        >
          +
        </button>
      </div>
      <span className="w-20 text-right tabular-nums text-stone-300">
        ${(item.unit_price * item.quantity).toFixed(2)}
      </span>
      <button
        onClick={() => onRemove(item.menu_item_id)}
        className="text-stone-500 hover:text-rose-400 transition text-xs"
      >
        ✕
      </button>
      {qtyError && <p className="text-xs text-rose-400 col-span-full">{qtyError}</p>}
    </div>
  );
}
