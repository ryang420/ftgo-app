import { useEffect, useState } from "react";
import RestaurantCard from "../components/RestaurantCard.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";
import SkeletonBlock from "../components/SkeletonBlock.jsx";
import EmptyState from "../components/EmptyState.jsx";
import { getRestaurants } from "../lib/api.js";

function RestaurantListPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");

  const loadRestaurants = async (signal) => {
    setStatus("loading");
    setErrorMessage("");

    try {
      const data = await getRestaurants({ signal });
      setRestaurants(data);
      setStatus("success");
    } catch (error) {
      if (error.name === "AbortError") return;
      setErrorMessage(
        "Restaurant API is not reachable yet. Start api-gateway and restaurant-service, then refresh."
      );
      setStatus("error");
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    loadRestaurants(controller.signal);
    return () => controller.abort();
  }, []);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(251,146,60,0.18),_transparent_26%),linear-gradient(135deg,_#fff7ed_0%,_#ffffff_48%,_#f8fafc_100%)] px-4 py-6 text-sand sm:px-8 sm:py-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="overflow-hidden rounded-[2rem] border border-orange-100 bg-white/85 px-4 py-6 shadow-card backdrop-blur sm:px-8 lg:px-10">
          <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
            <div className="space-y-5">
              <p className="text-sm uppercase tracking-[0.35em] text-orange-700">
                FTGO Marketplace
              </p>
              <h1 className="font-display text-3xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
                Find dinner fast from FTGO restaurant partners.
              </h1>
              <p className="max-w-2xl text-base leading-8 text-stone-600 sm:text-lg">
                Browse local menus, build a cart from a single restaurant, and
                follow each order from checkout to kitchen preparation in one
                streamlined demo.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                  Browse
                </p>
                <p className="mt-3 text-lg font-medium text-stone-950">
                  Explore partner restaurants
                </p>
              </div>
              <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                  Order
                </p>
                <p className="mt-3 text-lg font-medium text-stone-950">
                  Add menu favorites to your cart
                </p>
              </div>
              <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                  Track
                </p>
                <p className="mt-3 text-lg font-medium text-stone-950">
                  Watch kitchen status updates
                </p>
              </div>
            </div>
          </div>
        </header>

        <section className="mt-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.28em] text-orange-700">
                Restaurants
              </p>
              <h2 className="mt-2 font-display text-3xl font-semibold text-stone-950">
                Featured delivery partners
              </h2>
            </div>
            <p className="max-w-xl text-sm leading-7 text-stone-600">
              Choose a restaurant to view its current menu, then create an order
              when you are ready to check out.
            </p>
          </div>

          {status === "loading" && (
            <div className="mt-6 grid gap-5 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, index) => (
                <SkeletonBlock key={index} className="h-72" />
              ))}
            </div>
          )}

          {status === "error" && (
            <div className="mt-6">
              <ErrorMessage
                message={errorMessage}
                onRetry={() => loadRestaurants()}
              />
            </div>
          )}

          {status === "success" && restaurants.length === 0 && (
            <div className="mt-6">
              <EmptyState
                title="No restaurants available"
                message="Please check back after the marketplace has been refreshed."
              />
            </div>
          )}

          {status === "success" && restaurants.length > 0 && (
            <div className="mt-6 grid gap-5 lg:grid-cols-3">
              {restaurants.map((restaurant) => (
                <RestaurantCard key={restaurant.id} restaurant={restaurant} />
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

export default RestaurantListPage;
