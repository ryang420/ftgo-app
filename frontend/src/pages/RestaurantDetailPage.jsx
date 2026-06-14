import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MenuItemCard from "../components/MenuItemCard.jsx";
import CartPanel from "../components/CartPanel.jsx";
import OrderConfirmationDrawer from "../components/OrderConfirmationDrawer.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import EmptyState from "../components/EmptyState.jsx";
import useConsumerSession from "../hooks/useConsumerSession.js";
import { getRestaurant, getRestaurantMenuItems } from "../lib/api.js";
import {
  addItem,
  clearCart,
  isCartEmpty,
  removeItem,
  setQuantity,
} from "../lib/cart.js";

function RestaurantDetailPage() {
  const { restaurantId } = useParams();
  const navigate = useNavigate();
  const { session } = useConsumerSession();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const [cart, setCart] = useState(() => clearCart());
  const [showDrawer, setShowDrawer] = useState(false);
  const [pendingNav, setPendingNav] = useState(null);

  const loadRestaurantDetail = async (signal) => {
    setStatus("loading");
    setErrorMessage("");

    try {
      const [restaurantData, menuItemData] = await Promise.all([
        getRestaurant(restaurantId, { signal }),
        getRestaurantMenuItems(restaurantId, { signal }),
      ]);

      setRestaurant(restaurantData);
      setMenuItems(menuItemData);
      setStatus("success");
    } catch (error) {
      if (error.name === "AbortError") return;
      setErrorMessage(
        "Restaurant detail could not be loaded. Confirm api-gateway and restaurant-service are running and the restaurant ID exists."
      );
      setStatus("error");
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    loadRestaurantDetail(controller.signal);
    setCart(clearCart());
    return () => controller.abort();
  }, [restaurantId]);

  const handleAddToCart = (item) => {
    if (item._decrement) {
      const newQty = item._currentQty - 1;
      if (newQty <= 0) {
        setCart((prev) => removeItem(prev, String(item.id)));
      } else {
        setCart((prev) => setQuantity(prev, String(item.id), newQty));
      }
      return;
    }
    const cartItem = {
      menu_item_id: String(item.id),
      name: item.name,
      unit_price: Number(item.price),
    };
    setCart((prev) => addItem(prev, cartItem));
  };

  const handleRemove = (menuItemId) => {
    setCart((prev) => removeItem(prev, menuItemId));
  };

  const handleQuantityChange = (menuItemId, qty) => {
    setCart((prev) => setQuantity(prev, menuItemId, qty));
  };

  const navigateTo = (to) => {
    if (!isCartEmpty(cart)) {
      setPendingNav(to);
    } else {
      navigate(to);
    }
  };

  const confirmNav = () => {
    setCart(clearCart());
    setPendingNav(null);
    if (pendingNav) navigate(pendingNav);
  };

  const cancelNav = () => {
    setPendingNav(null);
  };

  const getCartQty = (itemId) => {
    const found = cart.items.find((i) => i.menu_item_id === String(itemId));
    return found ? found.quantity : 0;
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(251,146,60,0.18),_transparent_28%),linear-gradient(145deg,_#fff7ed_0%,_#ffffff_52%,_#f8fafc_100%)] px-4 py-6 sm:px-8 sm:py-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6">
          <button
            onClick={() => navigateTo("/")}
            className="inline-flex items-center rounded-full border border-orange-100 bg-white px-4 py-2 text-sm text-stone-700 shadow-sm transition hover:border-orange-200 hover:text-stone-950"
          >
            ← Back to restaurants
          </button>
        </div>

        {status === "loading" && (
          <section className="space-y-6">
            <SkeletonBlock className="h-52" />
            <div className="grid gap-5 lg:grid-cols-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-44" />
              ))}
            </div>
          </section>
        )}

        {status === "error" && (
          <ErrorMessage
            message={errorMessage}
            onRetry={() => loadRestaurantDetail()}
          />
        )}

        {pendingNav && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/35 backdrop-blur-sm">
            <div className="w-full max-w-sm rounded-[2rem] border border-orange-100 bg-white p-8 text-center shadow-2xl">
              <p className="text-sm text-stone-700">
                Your cart will be cleared if you leave this restaurant.
              </p>
              <div className="mt-4 flex gap-3 justify-center">
                <button
                  onClick={cancelNav}
                  className="rounded-full border border-stone-200 px-5 py-2 text-xs text-stone-600 transition hover:border-orange-200 hover:text-stone-950"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmNav}
                  className="rounded-full bg-orange-600 px-5 py-2 text-xs font-medium text-white hover:bg-orange-500 transition"
                >
                  Continue
                </button>
              </div>
            </div>
          </div>
        )}

        {status === "success" && restaurant && (
          <>
            <header className="overflow-hidden rounded-[2rem] border border-orange-100 bg-white/85 px-4 py-6 shadow-card backdrop-blur sm:px-8 lg:px-10">
              <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
                <div className="space-y-5">
                  <p className="text-sm uppercase tracking-[0.35em] text-orange-700">
                    {restaurant.cuisine}
                  </p>
                  <h1 className="font-display text-3xl font-semibold leading-tight text-stone-950 sm:text-5xl lg:text-6xl">
                    {restaurant.name}
                  </h1>
                </div>
                <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
                  <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                    <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                      Cuisine
                    </p>
                    <p className="mt-3 text-lg font-medium text-stone-950">
                      {restaurant.cuisine}
                    </p>
                  </div>
                  <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                    <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                      Menu
                    </p>
                    <p className="mt-3 text-lg font-medium text-stone-950">
                      {menuItems.length} items available
                    </p>
                  </div>
                  <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                    <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                      Checkout
                    </p>
                    <p className="mt-3 text-lg font-medium text-stone-950">
                      Order from this restaurant only
                    </p>
                  </div>
                </div>
              </div>
            </header>

            <section className="mt-8">
              <div className="mb-6">
                <p className="text-sm uppercase tracking-[0.28em] text-orange-700">
                  Menu
                </p>
                <h2 className="mt-2 font-display text-3xl font-semibold text-stone-950">
                  Available items
                </h2>
              </div>

              <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
                <div>
                  {menuItems.length === 0 ? (
                    <EmptyState
                      title="No menu items"
                      message="This restaurant has no menu items available right now."
                    />
                  ) : (
                    <div className="grid gap-5 lg:grid-cols-1 xl:grid-cols-2">
                      {menuItems.map((item) => (
                        <MenuItemCard
                          key={item.id}
                          item={item}
                          onAddToCart={handleAddToCart}
                          sessionExists={!!session}
                          cartQuantity={getCartQty(item.id)}
                        />
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <CartPanel
                    cart={cart}
                    onRemove={handleRemove}
                    onQuantityChange={handleQuantityChange}
                    onPlaceOrder={() => setShowDrawer(true)}
                  />
                </div>
              </div>
            </section>
          </>
        )}

        {showDrawer && session && (
          <OrderConfirmationDrawer
            cart={cart}
            restaurantName={restaurant?.name || "Restaurant"}
            consumerId={session.consumer_id}
            restaurantId={restaurantId}
            onClose={() => setShowDrawer(false)}
            onOrderPlaced={(orderId) => {
              setCart(clearCart());
              setShowDrawer(false);
              navigate(`/orders/${orderId}`);
            }}
          />
        )}
      </div>
    </main>
  );
}

export default RestaurantDetailPage;
