export default function EmptyState({ title = "Nothing here yet", message, action }) {
  return (
    <div className="rounded-[1.75rem] border border-orange-100 bg-white p-8 text-center shadow-sm">
      <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-orange-50 text-3xl">
        📭
      </div>
      <h3 className="text-lg font-semibold text-stone-800">{title}</h3>
      {message && (
        <p className="mt-2 text-sm leading-7 text-stone-500 max-w-md mx-auto">
          {message}
        </p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
