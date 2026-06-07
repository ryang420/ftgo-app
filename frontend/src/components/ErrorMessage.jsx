export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="rounded-[1.75rem] border border-rose-300/20 bg-rose-500/10 p-6 text-sm leading-7 text-rose-100">
      <p className="font-medium">Something went wrong.</p>
      <p className="mt-2">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 rounded-full border border-rose-300/20 bg-rose-500/10 px-4 py-2 text-xs hover:bg-rose-500/20"
        >
          Retry
        </button>
      )}
    </div>
  );
}
