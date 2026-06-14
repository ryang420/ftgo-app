import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import ErrorMessage from "./ErrorMessage.jsx";

describe("ErrorMessage", () => {
  it("renders the error message", () => {
    render(<ErrorMessage message="Something broke" />);
    expect(screen.getByText("Something went wrong.")).toBeVisible();
    expect(screen.getByText("Something broke")).toBeVisible();
  });

  it("does not render a retry button when onRetry is omitted", () => {
    render(<ErrorMessage message="No retry" />);
    expect(screen.queryByRole("button", { name: "Retry" })).toBeNull();
  });

  it("renders a retry button and calls onRetry when clicked", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(<ErrorMessage message="Retry me" onRetry={onRetry} />);

    const retryButton = screen.getByRole("button", { name: "Retry" });
    expect(retryButton).toBeVisible();

    await user.click(retryButton);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
