import { useEffect, useState } from "react";
import RestaurantCard from "../components/RestaurantCard.jsx";
import { getRestaurants } from "../lib/api.js";

function RestaurantListPage() {
  const [restaurants, setRestaurants] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadRestaurants() {
      setStatus("loading");
      setErrorMessage("");

      try {
        const data = await getRestaurants({ signal: controller.signal });
        setRestaurants(data);
        setStatus("success");
      } catch (error) {
        if (error.name === "AbortError") {
          return;
        }

        setErrorMessage(
          "Restaurant API is not reachable yet. Start api-gateway and restaurant-service, then refresh.",
        );
        setStatus("error");
      }
    }

    loadRestaurants();

    return () => controller.abort();
  }, []);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(251,146,60,0.18),_transparent_26%),linear-gradient(135deg,_#fff7ed_0%,_#ffffff_48%,_#f8fafc_100%)] px-5 py-6 text-sand sm:px-8 sm:py-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="overflow-hidden rounded-[2rem] border border-orange-100 bg-white/85 px-6 py-8 shadow-card backdrop-blur sm:px-8 lg:px-10">
          <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
            <div className="space-y-5">
              <p className="text-sm uppercase tracking-[0.35em] text-orange-700">
                FTGO Marketplace
              </p>
              <h1 className="font-display text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
                Find dinner fast from FTGO restaurant partners.
              </h1>
              <p className="max-w-2xl text-base leading-8 text-stone-600 sm:text-lg">
                Browse local menus, build a cart from a single restaurant, and follow
                each order from checkout to kitchen preparation in one streamlined demo.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              <div className="rounded-[1.5rem] border border-orange-100 bg-orange-50/70 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-700">
                  Browse
                </p>
                <p className="mt-3 text-lg font-medium text-stone-950">Explore partner restaurants</p>
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
                <p className="mt-3 text-lg font-medium text-stone-950">Watch kitchen status updates</p>
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
              Choose a restaurant to view its current menu, then create an order when
              you are ready to check out.
            </p>
          </div>

          {status === "loading" ? (
            <div className="mt-6 grid gap-5 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, index) => (
                <div
                  key={index}
                  className="h-72 animate-pulse rounded-[1.75rem] border border-orange-100 bg-orange-100/70"
                />
              ))}
            </div>
          ) : null}

          {status === "error" ? (
            <div className="mt-6 rounded-[1.75rem] border border-rose-200 bg-rose-50 p-6 text-sm leading-7 text-rose-800">
              <p className="font-medium">Unable to load restaurants.</p>
              <p className="mt-2">{errorMessage}</p>
              <p className="mt-2 text-rose-700">
                Expected gateway route: <code>http://localhost:8000/restaurants</code>
              </p>
            </div>
          ) : null}

          {status === "success" && restaurants.length === 0 ? (
            <div className="mt-6 rounded-[1.75rem] border border-orange-100 bg-white p-6 text-sm leading-7 text-stone-700 shadow-sm">
              No restaurants are available right now. Please check back after the
              marketplace has been refreshed.
            </div>
          ) : null}

          {status === "success" && restaurants.length > 0 ? (
            <div className="mt-6 grid gap-5 lg:grid-cols-3">
              {restaurants.map((restaurant) => (
                <RestaurantCard key={restaurant.id} restaurant={restaurant} />
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </main>
  );
}

export default RestaurantListPage;
