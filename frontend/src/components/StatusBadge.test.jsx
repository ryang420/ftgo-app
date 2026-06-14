import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import StatusBadge from "./StatusBadge.jsx";

describe("StatusBadge", () => {
  it("renders the status label", () => {
    render(<StatusBadge status="PENDING" />);
    expect(screen.getByText("Pending")).toBeVisible();
  });

  it("renders kitchen-specific status labels", () => {
    render(<StatusBadge status="CREATE_PENDING" />);
    expect(screen.getByText("New")).toBeVisible();
  });

  it("renders READY_FOR_PICKUP label", () => {
    render(<StatusBadge status="READY_FOR_PICKUP" />);
    expect(screen.getByText("Ready for Pickup")).toBeVisible();
  });

  it("falls back to raw status for unknown values", () => {
    render(<StatusBadge status="UNKNOWN_STATUS" />);
    expect(screen.getByText("UNKNOWN_STATUS")).toBeVisible();
  });

  it("applies distinct classes for different statuses", () => {
    const { container: c1 } = render(<StatusBadge status="CANCELLED" />);
    const { container: c2 } = render(<StatusBadge status="PENDING" />);

    const span1 = c1.querySelector("span");
    const span2 = c2.querySelector("span");
    expect(span1.className).not.toBe(span2.className);
  });
});
