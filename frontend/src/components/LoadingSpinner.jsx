import React from "react";

export default function LoadingSpinner() {
  return (
    <span
      role="status"
      aria-label="Loading"
      className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-orange-400 border-t-transparent"
    />
  );
}
