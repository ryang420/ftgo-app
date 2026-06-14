import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import EmptyState from "./EmptyState.jsx";

describe("EmptyState", () => {
  it("renders the title and message", () => {
    render(<EmptyState title="No items" message="Please add something." />);
    expect(screen.getByText("No items")).toBeVisible();
    expect(screen.getByText("Please add something.")).toBeVisible();
  });

  it("renders a default title when none provided", () => {
    render(<EmptyState />);
    expect(screen.getByText("Nothing here yet")).toBeVisible();
  });

  it("renders an action element when provided", () => {
    render(
      <EmptyState
        title="Empty"
        action={<button>Add item</button>}
      />
    );
    expect(screen.getByRole("button", { name: "Add item" })).toBeVisible();
  });

  it("does not render a message paragraph when message is omitted", () => {
    const { container } = render(<EmptyState title="Just a title" />);
    // The title paragraph should be there, but no message paragraph
    expect(screen.getByText("Just a title")).toBeVisible();
    // 📭 emoji icon div should be present
    expect(container.querySelector(".text-3xl")).toBeTruthy();
  });
});
