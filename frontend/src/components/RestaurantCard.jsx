function RestaurantCard({ restaurant }) {
  return (
    <article className="group overflow-hidden rounded-[1.75rem] border border-white/10 bg-white/[0.045] p-5 shadow-card transition duration-300 hover:-translate-y-1 hover:border-orange-300/30 hover:bg-white/[0.08]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-orange-200/75">
            {restaurant.cuisine}
          </p>
          <h2 className="mt-3 font-display text-2xl font-semibold text-sand">
            {restaurant.name}
          </h2>
        </div>
        <span className="rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">
          {restaurant.status}
        </span>
      </div>

      <p className="mt-4 text-sm leading-7 text-stone-300">{restaurant.description}</p>

      <div className="mt-6 flex flex-wrap gap-2">
        {restaurant.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-white/10 bg-black/15 px-3 py-1 text-xs text-stone-200"
          >
            {tag}
          </span>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-between text-sm text-stone-300">
        <div className="space-y-1">
          <p>{restaurant.eta}</p>
          <p>{restaurant.deliveryNote}</p>
        </div>
        <button
          type="button"
          className="rounded-full bg-orange-500 px-4 py-2 font-medium text-white transition group-hover:bg-orange-400"
        >
          View menu
        </button>
      </div>
    </article>
  );
}

export default RestaurantCard;
