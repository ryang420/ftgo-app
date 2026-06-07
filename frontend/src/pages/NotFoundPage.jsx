import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-4xl font-semibold text-stone-100">Page not found</h1>
      <p className="text-stone-400">The page you are looking for does not exist.</p>
      <Link
        to="/"
        className="rounded-full bg-orange-600 px-6 py-2 text-sm font-medium text-white hover:bg-orange-500 transition"
      >
        Back to Restaurant List
      </Link>
    </div>
  );
}
