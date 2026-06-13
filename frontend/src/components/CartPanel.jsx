import { cartTotal, isCartEmpty } from "../lib/cart.js";
import CartItemRow from "./CartItemRow.jsx";

export default function CartPanel({ cart, onRemove, onQuantityChange, onPlaceOrder }) {
  const empty = isCartEmpty(cart);

  return (
    <div className="rounded-[2rem] border border-orange-100 bg-white p-6 shadow-card">
      <h2 className="mb-4 text-lg font-semibold text-stone-950">
        Your Cart{cart.items.length > 0 ? ` (${cart.items.length})` : ""}
      </h2>

      {empty ? (
        <p className="text-sm text-stone-500">No items yet</p>
      ) : (
        <div className="space-y-1">
          {cart.items.map((item) => (
            <CartItemRow
              key={item.menu_item_id}
              item={item}
              onRemove={onRemove}
              onQuantityChange={onQuantityChange}
            />
          ))}
        </div>
      )}

      <div className="mt-4 flex justify-between border-t border-orange-100 pt-4 text-sm">
        <span className="text-stone-600">Total</span>
        <span className="font-medium text-stone-950">${cartTotal(cart).toFixed(2)}</span>
      </div>

      <button
        onClick={onPlaceOrder}
        disabled={empty}
        className="mt-4 w-full rounded-full bg-orange-600 px-4 py-3 text-sm font-medium text-white hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        Place order
      </button>
      {empty && (
        <p className="mt-2 text-center text-xs text-stone-500">
          Cart is empty — add at least one item
        </p>
      )}
    </div>
  );
}
