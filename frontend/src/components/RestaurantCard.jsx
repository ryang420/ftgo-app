import { Link } from "react-router-dom";

function RestaurantCard({ restaurant }) {
  const menuItemCount = restaurant.menu_items.length;

  return (
    <article className="group overflow-hidden rounded-[1.75rem] border border-orange-100 bg-white p-5 shadow-card transition duration-300 hover:-translate-y-1 hover:border-orange-200">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-orange-700">
            {restaurant.cuisine}
          </p>
          <h2 className="mt-3 font-display text-2xl font-semibold text-sand">
            {restaurant.name}
          </h2>
        </div>
        <span className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-medium text-orange-700">
          {menuItemCount} items
        </span>
      </div>

      <p className="mt-4 text-sm leading-7 text-stone-600">
        {menuItemCount > 0
          ? `Includes ${restaurant.menu_items
              .slice(0, 3)
              .map((item) => item.name)
              .join(", ")}${menuItemCount > 3 ? ", and more." : "."}`
          : "Menu items have not been added yet, but the restaurant profile is already live."}
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        {[restaurant.cuisine, `${menuItemCount} menu items`].map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs text-stone-600"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-between gap-4 text-sm text-stone-600">
        <p className="max-w-[12rem] text-stone-500">
          View today&apos;s menu and start a fresh cart for this restaurant.
        </p>
        <Link
          to={`/restaurants/${restaurant.id}`}
          className="shrink-0 rounded-full bg-orange-500 px-4 py-2 font-medium text-white transition group-hover:bg-orange-400"
        >
          View menu
        </Link>
      </div>
    </article>
  );
}

export default RestaurantCard;
