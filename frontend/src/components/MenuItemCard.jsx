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

export default function MenuItemCard({ item, onAddToCart, sessionExists = false, cartQuantity = 0 }) {
  const hasCartQuantity = cartQuantity > 0;

  return (
    <article className="rounded-[1.5rem] border border-orange-100 bg-white p-5 shadow-sm transition hover:border-orange-200 hover:shadow-card">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl font-semibold text-stone-950">{item.name}</h3>
          {item.description && (
            <p className="mt-2 text-sm leading-7 text-stone-600">{item.description}</p>
          )}
        </div>
        <span className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-sm font-medium text-orange-700">
          {formatPrice(item.price)}
        </span>
      </div>

      {!hasCartQuantity ? (
        <button
          onClick={() => onAddToCart?.(item)}
          disabled={!sessionExists}
          className={`mt-4 w-full rounded-full px-4 py-2 text-sm font-medium transition ${
            sessionExists
              ? "bg-orange-600 text-white hover:bg-orange-500"
              : "bg-stone-100 text-stone-400 cursor-not-allowed"
          }`}
        >
          Add to cart
        </button>
      ) : (
        <div className="mt-4 flex items-center justify-center gap-3 rounded-full bg-green-100 px-4 py-2 text-green-800 transition-colors">
          <button
            onClick={() => onAddToCart?.({ ...item, _decrement: true, _currentQty: cartQuantity })}
            className="flex h-6 w-6 items-center justify-center transition hover:text-green-950"
          >
            −
          </button>
          <span className="min-w-[1.5rem] text-center text-sm font-medium tabular-nums">
            {cartQuantity}
          </span>
          <button
            onClick={() => onAddToCart?.(item)}
            className="flex h-6 w-6 items-center justify-center transition hover:text-green-950"
          >
            +
          </button>
        </div>
      )}
    </article>
  );
}
