export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="rounded-[1.75rem] border border-rose-200 bg-rose-50 p-6 text-sm leading-7 text-rose-800">
      <p className="font-medium">Something went wrong.</p>
      <p className="mt-2">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 rounded-full border border-rose-200 bg-white px-4 py-2 text-xs text-rose-700 transition hover:bg-rose-100"
        >
          Retry
        </button>
      )}
    </div>
  );
}
