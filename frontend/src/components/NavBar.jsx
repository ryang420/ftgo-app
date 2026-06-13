import { NavLink } from "react-router-dom";
import useConsumerSession from "../hooks/useConsumerSession.js";

export default function NavBar() {
  const { session, clearSession } = useConsumerSession();

  const linkClass = ({ isActive }) =>
    isActive
      ? "border-b border-orange-500 text-orange-700"
      : "text-stone-600 hover:text-stone-950";

  return (
    <nav className="sticky top-0 z-40 border-b border-orange-100 bg-white/85 shadow-sm backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-6 px-6 py-3">
        <NavLink to="/" className={linkClass} end>
          Restaurant List
        </NavLink>
        <NavLink to="/my-orders" className={linkClass}>
          My Orders
        </NavLink>
        <NavLink to="/kitchen" className={linkClass}>
          Kitchen
        </NavLink>
        <NavLink to="/operations" className={linkClass}>
          Operations
        </NavLink>
        <div className="ml-auto flex items-center gap-3">
          {session && (
            <span className="text-xs text-stone-500">
              {session.display_name || truncateId(session.consumer_id)}
            </span>
          )}
          <button
            onClick={clearSession}
            className="rounded-full border border-stone-200 bg-white px-3 py-1 text-xs text-stone-600 transition hover:border-orange-200 hover:text-stone-950"
          >
            Change consumer
          </button>
        </div>
      </div>
    </nav>
  );
}

function truncateId(id) {
  return id.slice(0, 8);
}
