function formatPrice(price) {
  const amount = Number(price);

  if (Number.isNaN(amount)) {
    return price;
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export default function MenuItemCard({ item, onAddToCart, sessionExists = false }) {
  return (
    <article className="rounded-[1.5rem] border border-white/10 bg-white/[0.045] p-5 transition hover:border-orange-300/30 hover:bg-white/[0.07]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl font-semibold text-white">{item.name}</h3>
          <p className="mt-2 text-sm text-stone-400">Menu item ID: {item.id}</p>
        </div>
        <span className="rounded-full border border-orange-300/20 bg-orange-400/10 px-3 py-1 text-sm font-medium text-orange-100">
          {formatPrice(item.price)}
        </span>
      </div>

      <p className="mt-4 text-sm leading-7 text-stone-300">
        {item.description || "No description yet. This menu item is available through the restaurant service."}
      </p>

      <button
        onClick={() => onAddToCart?.(item)}
        disabled={!sessionExists}
        className={`mt-4 w-full rounded-full px-4 py-2 text-sm font-medium transition ${
          sessionExists
            ? "bg-orange-600 text-white hover:bg-orange-500"
            : "bg-stone-800 text-stone-500 cursor-not-allowed"
        }`}
      >
        Add to cart
      </button>
    </article>
  );
}
