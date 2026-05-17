import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import MenuItemCard from "../components/MenuItemCard.jsx";
import { getRestaurant, getRestaurantMenuItems } from "../lib/api.js";

function RestaurantDetailPage() {
  const { restaurantId } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [status, setStatus] = useState("loading");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadRestaurantDetail() {
      setStatus("loading");
      setErrorMessage("");

      try {
        const [restaurantData, menuItemData] = await Promise.all([
          getRestaurant(restaurantId, { signal: controller.signal }),
          getRestaurantMenuItems(restaurantId, { signal: controller.signal }),
        ]);

        setRestaurant(restaurantData);
        setMenuItems(menuItemData);
        setStatus("success");
      } catch (error) {
        if (error.name === "AbortError") {
          return;
        }

        setErrorMessage(
          "Restaurant detail could not be loaded. Confirm api-gateway and restaurant-service are running and the restaurant ID exists.",
        );
        setStatus("error");
      }
    }

    loadRestaurantDetail();

    return () => controller.abort();
  }, [restaurantId]);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(251,146,60,0.22),_transparent_28%),linear-gradient(145deg,_#111111_0%,_#1c1917_48%,_#292524_100%)] px-5 py-6 text-sand sm:px-8 sm:py-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6">
          <Link
            to="/"
            className="inline-flex items-center rounded-full border border-white/10 bg-white/[0.05] px-4 py-2 text-sm text-stone-200 transition hover:border-orange-300/30 hover:bg-white/[0.08]"
          >
            Back to restaurants
          </Link>
        </div>

        {status === "loading" ? (
          <section className="space-y-6">
            <div className="h-52 animate-pulse rounded-[2rem] border border-white/10 bg-white/[0.045]" />
            <div className="grid gap-5 lg:grid-cols-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <div
                  key={index}
                  className="h-44 animate-pulse rounded-[1.5rem] border border-white/10 bg-white/[0.045]"
                />
              ))}
            </div>
          </section>
        ) : null}

        {status === "error" ? (
          <section className="rounded-[2rem] border border-rose-300/20 bg-rose-500/10 p-6 text-sm leading-7 text-rose-100">
            <p className="font-medium">Unable to load restaurant detail.</p>
            <p className="mt-2">{errorMessage}</p>
            <p className="mt-2 text-rose-100/80">
              Expected endpoints: <code>/restaurants/{restaurantId}</code> and{" "}
              <code>/restaurants/{restaurantId}/menu-items</code>
            </p>
          </section>
        ) : null}

        {status === "success" && restaurant ? (
          <>
            <header className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.05] px-6 py-8 shadow-card backdrop-blur sm:px-8 lg:px-10">
              <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
                <div className="space-y-5">
                  <p className="text-sm uppercase tracking-[0.35em] text-orange-300/80">
                    {restaurant.cuisine}
                  </p>
                  <h1 className="font-display text-4xl font-semibold leading-tight text-white sm:text-5xl lg:text-6xl">
                    {restaurant.name}
                  </h1>
                  <p className="max-w-2xl text-base leading-8 text-stone-300 sm:text-lg">
                    This detail page is wired directly to the current restaurant APIs,
                    so it can become the basis for menu selection and order creation
                    without reshaping the route model later.
                  </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
                  <div className="rounded-[1.5rem] border border-white/10 bg-black/15 p-5">
                    <p className="text-xs uppercase tracking-[0.25em] text-orange-200/80">
                      Restaurant ID
                    </p>
                    <p className="mt-3 text-lg font-medium text-white">{restaurant.id}</p>
                  </div>
                  <div className="rounded-[1.5rem] border border-white/10 bg-black/15 p-5">
                    <p className="text-xs uppercase tracking-[0.25em] text-orange-200/80">
                      Slug
                    </p>
                    <p className="mt-3 text-lg font-medium text-white">/{restaurant.slug}</p>
                  </div>
                  <div className="rounded-[1.5rem] border border-white/10 bg-black/15 p-5">
                    <p className="text-xs uppercase tracking-[0.25em] text-orange-200/80">
                      Menu size
                    </p>
                    <p className="mt-3 text-lg font-medium text-white">
                      {menuItems.length} items
                    </p>
                  </div>
                </div>
              </div>
            </header>

            <section className="mt-8">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.28em] text-orange-200/75">
                    Menu
                  </p>
                  <h2 className="mt-2 font-display text-3xl font-semibold text-white">
                    Available items
                  </h2>
                </div>
                <p className="max-w-xl text-sm leading-7 text-stone-300">
                  This section now reads from the dedicated menu endpoint instead of
                  relying only on the restaurant list payload.
                </p>
              </div>

              {menuItems.length === 0 ? (
                <div className="mt-6 rounded-[1.75rem] border border-white/10 bg-white/[0.045] p-6 text-sm leading-7 text-stone-200">
                  This restaurant exists, but no menu items have been created yet.
                </div>
              ) : (
                <div className="mt-6 grid gap-5 lg:grid-cols-2">
                  {menuItems.map((item) => (
                    <MenuItemCard key={item.id} item={item} />
                  ))}
                </div>
              )}
            </section>
          </>
        ) : null}
      </div>
    </main>
  );
}

export default RestaurantDetailPage;
