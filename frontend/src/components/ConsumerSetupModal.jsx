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

export default function ConsumerSetupModal({ mode = "modal" }) {
  const { setSession } = useConsumerSession();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dismissed, setDismissed] = useState(false);

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

  if (mode === "banner" && dismissed) return null;

  if (mode === "banner") {
    return (
      <div className="sticky top-0 z-40 border-b border-orange-200 bg-orange-50/95 backdrop-blur">
        <div className="relative mx-auto flex max-w-5xl flex-wrap items-center gap-4 px-6 py-3 pr-14">
          <span className="text-sm text-orange-800">
            🍜 Welcome! Enter your name to start ordering
          </span>
          <form onSubmit={handleSubmit} className="flex items-center gap-2 flex-1">
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value.slice(0, 100))}
              placeholder="First name"
              maxLength={100}
              required
              className="w-28 rounded-full border border-orange-200 bg-white px-3 py-1.5 text-xs text-stone-900 placeholder-stone-400 outline-none focus:border-orange-500"
            />
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value.slice(0, 100))}
              placeholder="Last name"
              maxLength={100}
              required
              className="w-28 rounded-full border border-orange-200 bg-white px-3 py-1.5 text-xs text-stone-900 placeholder-stone-400 outline-none focus:border-orange-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-full bg-orange-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-orange-500 disabled:opacity-50 flex items-center gap-1"
            >
              {loading && <LoadingSpinner />}
              {loading ? "..." : "Continue"}
            </button>
          </form>
          <button
            onClick={() => setDismissed(true)}
            className="absolute right-6 top-4 text-sm text-stone-500 transition hover:text-stone-950"
          >
            ✕
          </button>
        </div>
        {error && <div className="mx-auto max-w-5xl px-6 pb-2 text-xs text-rose-700">{error}</div>}
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/35 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-[2rem] border border-orange-100 bg-white p-8 shadow-2xl">
        <h2 className="text-xl font-semibold text-stone-950">Welcome to FTGO</h2>
        <p className="mt-2 text-sm text-stone-600">
          Enter your name to get started.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <label className="block">
            <span className="mb-2 block text-xs font-medium text-stone-700">First name</span>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value.slice(0, 100))}
              placeholder="First name"
              maxLength={100}
              required
              className="w-full rounded-full border border-stone-200 bg-white px-5 py-3 text-sm text-stone-900 placeholder-stone-400 outline-none focus:border-orange-500"
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-xs font-medium text-stone-700">Last name</span>
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value.slice(0, 100))}
              placeholder="Last name"
              maxLength={100}
              required
              className="w-full rounded-full border border-stone-200 bg-white px-5 py-3 text-sm text-stone-900 placeholder-stone-400 outline-none focus:border-orange-500"
            />
          </label>
          {error && <p className="text-sm text-rose-700">{error}</p>}
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
