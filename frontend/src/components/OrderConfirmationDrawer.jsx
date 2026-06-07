import { useState } from "react";
import { placeOrder } from "../lib/api.js";
import { cartTotal } from "../lib/cart.js";
import LoadingSpinner from "./LoadingSpinner.jsx";

export default function OrderConfirmationDrawer({
  cart,
  restaurantName,
  consumerId,
  restaurantId,
  onClose,
  onOrderPlaced,
}) {
  const [address, setAddress] = useState("");
  const [addressError, setAddressError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAddressError("");
    setSubmitError("");

    if (!address.trim()) {
      setAddressError("Delivery address is required");
      return;
    }

    setLoading(true);
    try {
      const data = await placeOrder({
        consumer_id: consumerId,
        restaurant_id: restaurantId,
        currency: "USD",
        delivery_address: address.trim(),
        line_items: cart.items.map((item) => ({
          menu_item_id: item.menu_item_id,
          quantity: item.quantity,
        })),
      });
      onOrderPlaced(data.id);
    } catch (err) {
      setSubmitError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-[2rem] border border-white/10 bg-stone-900 p-8 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-stone-100">Confirm Order</h2>
          <button onClick={onClose} className="text-stone-500 hover:text-white transition text-lg">✕</button>
        </div>

        <div className="mb-4 p-4 rounded-[1.25rem] bg-white/[0.045] text-sm">
          <p className="text-stone-400">Restaurant: <span className="text-stone-200">{restaurantName}</span></p>
          <p className="text-stone-400 mt-2">Total items: <span className="text-stone-200">{cart.items.length}</span></p>
          <div className="mt-2 space-y-1">
            {cart.items.map((item) => (
              <p key={item.menu_item_id} className="text-stone-500 text-xs">
                {item.name} × {item.quantity}
              </p>
            ))}
          </div>
          <p className="mt-3 text-stone-400">
            Total: <span className="text-stone-200 font-medium">${cartTotal(cart).toFixed(2)}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-stone-400">Delivery address</label>
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value.slice(0, 500))}
              maxLength={500}
              placeholder="Enter your delivery address"
              className="mt-1 w-full rounded-full border border-white/10 bg-white/[0.045] px-5 py-3 text-sm text-stone-100 placeholder-stone-500 outline-none focus:border-orange-400/50"
            />
            {addressError && <p className="mt-1 text-xs text-rose-400">{addressError}</p>}
          </div>

          {submitError && (
            <p className="text-sm text-rose-400">{submitError}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-orange-600 px-4 py-3 text-sm font-medium text-white hover:bg-orange-500 disabled:opacity-50 transition flex items-center justify-center gap-2"
          >
            {loading && <LoadingSpinner />}
            {loading ? "Placing order..." : "Confirm & Place Order"}
          </button>
        </form>
      </div>
    </div>
  );
}
