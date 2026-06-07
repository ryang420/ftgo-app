import { cartTotal, isCartEmpty } from "../lib/cart.js";
import CartItemRow from "./CartItemRow.jsx";

export default function CartPanel({ cart, onRemove, onQuantityChange, onPlaceOrder }) {
  const empty = isCartEmpty(cart);

  return (
    <div className="rounded-[2rem] border border-white/10 bg-white/[0.035] p-6">
      <h2 className="text-lg font-semibold text-stone-100 mb-4">Your Cart</h2>

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

      <div className="mt-4 pt-4 border-t border-white/10 flex justify-between text-sm">
        <span className="text-stone-400">Total</span>
        <span className="text-stone-200 font-medium">${cartTotal(cart).toFixed(2)}</span>
      </div>

      <button
        onClick={onPlaceOrder}
        disabled={empty}
        className="mt-4 w-full rounded-full bg-orange-600 px-4 py-3 text-sm font-medium text-white hover:bg-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        Place order
      </button>
      {empty && (
        <p className="mt-2 text-xs text-stone-500 text-center">
          Cart is empty — add at least one item
        </p>
      )}
    </div>
  );
}
