import { useState } from "react";
import { NavLink } from "react-router-dom";
import useConsumerSession from "../hooks/useConsumerSession.js";

const linkClass = ({ isActive }) =>
  `rounded-full px-4 py-1.5 text-sm font-medium transition ${
    isActive
      ? "bg-orange-100 text-orange-800"
      : "text-stone-600 hover:bg-stone-100 hover:text-stone-950"
  }`;

export default function NavBar() {
  const { session, clearSession } = useConsumerSession();
  const [open, setOpen] = useState(false);

  const links = (
    <>
      <NavLink to="/" className={linkClass} end onClick={() => setOpen(false)}>
        Restaurants
      </NavLink>
      <NavLink
        to="/my-orders"
        className={linkClass}
        onClick={() => setOpen(false)}
      >
        My Orders
      </NavLink>
      <NavLink
        to="/kitchen"
        className={linkClass}
        onClick={() => setOpen(false)}
      >
        Kitchen
      </NavLink>
      <NavLink
        to="/operations"
        className={linkClass}
        onClick={() => setOpen(false)}
      >
        Operations
      </NavLink>
    </>
  );

  return (
    <nav className="sticky top-0 z-40 border-b border-orange-100 bg-white/85 shadow-sm backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-2.5 sm:px-6">
        {/* Desktop nav links */}
        <div className="hidden flex-wrap items-center gap-1.5 sm:flex">
          {links}
        </div>

        {/* Mobile hamburger */}
        <button
          onClick={() => setOpen(!open)}
          className="flex h-9 w-9 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-600 transition hover:border-orange-200 sm:hidden"
          aria-label="Toggle navigation"
        >
          {open ? "✕" : "☰"}
        </button>

        {/* Consumer info + actions */}
        <div className="ml-auto flex items-center gap-3">
          {session && (
            <span className="hidden text-xs text-stone-500 sm:inline">
              {session.display_name || session.consumer_id.slice(0, 8)}
            </span>
          )}
          <button
            onClick={clearSession}
            className="rounded-full border border-stone-200 bg-white px-3 py-1 text-xs text-stone-600 transition hover:border-orange-200 hover:text-stone-950"
          >
            Change
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {open && (
        <div className="flex flex-col gap-1 border-t border-orange-100 bg-white px-4 py-3 sm:hidden">
          {links}
          {session && (
            <div className="mt-1 border-t border-stone-100 pt-2 text-xs text-stone-500">
              {session.display_name || session.consumer_id.slice(0, 8)}
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
