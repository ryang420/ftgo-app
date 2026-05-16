import RestaurantCard from "../components/RestaurantCard.jsx";
import { featuredRestaurants } from "../data/restaurants.js";

function RestaurantListPage() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(251,146,60,0.24),_transparent_24%),linear-gradient(135deg,_#111111_0%,_#1c1917_52%,_#292524_100%)] px-5 py-6 text-sand sm:px-8 sm:py-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <header className="overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.05] px-6 py-8 shadow-card backdrop-blur sm:px-8 lg:px-10">
          <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
            <div className="space-y-5">
              <p className="text-sm uppercase tracking-[0.35em] text-orange-300/80">
                FTGO Marketplace
              </p>
              <h1 className="font-display text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
                Start with restaurant discovery, then grow into menu and order flows.
              </h1>
              <p className="max-w-2xl text-base leading-8 text-stone-300 sm:text-lg">
                This page is the best first slice for the current backend shape because
                the restaurant domain already exposes list and detail endpoints that map
                naturally to a browsable customer experience.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              <div className="rounded-[1.5rem] border border-white/10 bg-black/15 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-200/80">
                  First API target
                </p>
                <p className="mt-3 text-lg font-medium text-white">GET /restaurants</p>
              </div>
              <div className="rounded-[1.5rem] border border-white/10 bg-black/15 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-200/80">
                  Next route
                </p>
                <p className="mt-3 text-lg font-medium text-white">
                  /restaurants/:restaurantId
                </p>
              </div>
              <div className="rounded-[1.5rem] border border-white/10 bg-black/15 p-5">
                <p className="text-xs uppercase tracking-[0.25em] text-orange-200/80">
                  After that
                </p>
                <p className="mt-3 text-lg font-medium text-white">Create order flow</p>
              </div>
            </div>
          </div>
        </header>

        <section className="mt-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.28em] text-orange-200/75">
                Restaurants
              </p>
              <h2 className="mt-2 font-display text-3xl font-semibold text-white">
                Featured delivery partners
              </h2>
            </div>
            <p className="max-w-xl text-sm leading-7 text-stone-300">
              Temporary mock data is wired in for now so we can shape the page and
              component model before swapping the source to the real restaurant
              service.
            </p>
          </div>

          <div className="mt-6 grid gap-5 lg:grid-cols-3">
            {featuredRestaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

export default RestaurantListPage;
