import { useState } from "react";
import { placeOrder } from "../lib/api.js";
import { cartTotal } from "../lib/cart.js";
import { readAddress, writeAddress } from "../lib/address.js";
import LoadingSpinner from "./LoadingSpinner.jsx";

export default function OrderConfirmationDrawer({
  cart,
  restaurantName,
  consumerId,
  restaurantId,
  onClose,
  onOrderPlaced,
}) {
  const [address, setAddress] = useState(() => readAddress());
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
      writeAddress(address.trim());
      onOrderPlaced(data.id);
    } catch (err) {
      setSubmitError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/35 backdrop-blur-sm">
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-[2rem] border border-orange-100 bg-white p-8 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-stone-950">Confirm Order</h2>
          <button onClick={onClose} className="text-lg text-stone-500 transition hover:text-stone-950">✕</button>
        </div>

        <div className="mb-4 rounded-[1.25rem] border border-orange-100 bg-orange-50/70 p-4 text-sm">
          <p className="text-stone-600">Restaurant: <span className="text-stone-950">{restaurantName}</span></p>
          <p className="mt-2 text-stone-600">Total items: <span className="text-stone-950">{cart.items.length}</span></p>
          <div className="mt-2 space-y-1">
            {cart.items.map((item) => (
              <p key={item.menu_item_id} className="text-xs text-stone-500">
                {item.name} × {item.quantity}
              </p>
            ))}
          </div>
          <p className="mt-3 text-stone-600">
            Total: <span className="font-medium text-stone-950">${cartTotal(cart).toFixed(2)}</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm text-stone-700">Delivery address</label>
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value.slice(0, 500))}
              maxLength={500}
              placeholder="Enter your delivery address"
              className="mt-1 w-full rounded-full border border-stone-200 bg-white px-5 py-3 text-sm text-stone-900 placeholder-stone-400 outline-none focus:border-orange-500"
            />
            {addressError && <p className="mt-1 text-xs text-rose-700">{addressError}</p>}
          </div>

          {submitError && (
            <p className="text-sm text-rose-700">{submitError}</p>
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
