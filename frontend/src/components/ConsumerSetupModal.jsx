import React from "react";
import { useState } from "react";
import { createConsumer } from "../lib/api.js";
import useConsumerSession from "../hooks/useConsumerSession.js";
import LoadingSpinner from "./LoadingSpinner.jsx";

function emailPart(value) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ".")
    .replace(/^\.+|\.+$/g, "");
}

function uniqueEmail(firstName, lastName) {
  const base = [emailPart(firstName), emailPart(lastName)].filter(Boolean).join(".");
  const token =
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `${base || "consumer"}.${token}@example.com`;
}

export default function ConsumerSetupModal() {
  const { setSession } = useConsumerSession();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const trimmedFirstName = firstName.trim();
    const trimmedLastName = lastName.trim();
    if (!trimmedFirstName || !trimmedLastName) {
      setError("First name and last name are required.");
      return;
    }

    setLoading(true);
    try {
      const displayName = `${trimmedFirstName} ${trimmedLastName}`;
      const data = await createConsumer({
        first_name: trimmedFirstName,
        last_name: trimmedLastName,
        email: uniqueEmail(trimmedFirstName, trimmedLastName),
      });
      setSession({
        consumer_id: data.id,
        display_name: displayName,
      });
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-[2rem] border border-white/10 bg-stone-900 p-8 shadow-2xl">
        <h2 className="text-xl font-semibold text-stone-100">Welcome to FTGO</h2>
        <p className="mt-2 text-sm text-stone-400">
          Enter your name to get started.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <label className="block">
            <span className="mb-2 block text-xs font-medium text-stone-300">First name</span>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value.slice(0, 100))}
              placeholder="First name"
              maxLength={100}
              required
              className="w-full rounded-full border border-white/10 bg-white/[0.045] px-5 py-3 text-sm text-stone-100 placeholder-stone-500 outline-none focus:border-orange-400/50"
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-xs font-medium text-stone-300">Last name</span>
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value.slice(0, 100))}
              placeholder="Last name"
              maxLength={100}
              required
              className="w-full rounded-full border border-white/10 bg-white/[0.045] px-5 py-3 text-sm text-stone-100 placeholder-stone-500 outline-none focus:border-orange-400/50"
            />
          </label>
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-orange-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-orange-500 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading && <LoadingSpinner />}
            {loading ? "Creating..." : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}
