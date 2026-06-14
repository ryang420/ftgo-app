import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import NavBar from "./NavBar.jsx";

const clearSession = vi.fn();

vi.mock("../hooks/useConsumerSession.js", () => ({
  default: () => ({
    session: { consumer_id: "abc12345-1234-4234-8234-123456789abc", display_name: "Test User" },
    clearSession,
  }),
}));

function renderWithRouter(initialRoute = "/") {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <NavBar />
    </MemoryRouter>
  );
}

describe("NavBar", () => {
  beforeEach(() => {
    clearSession.mockClear();
  });

  it("renders navigation links", () => {
    renderWithRouter();
    expect(screen.getByText("Restaurants")).toBeVisible();
    expect(screen.getByText("My Orders")).toBeVisible();
    expect(screen.getByText("Kitchen")).toBeVisible();
    expect(screen.getByText("Operations")).toBeVisible();
  });

  it("shows consumer display name when session exists", () => {
    renderWithRouter();
    expect(screen.getByText("Test User")).toBeVisible();
  });

  it("renders Change button", () => {
    renderWithRouter();
    expect(screen.getByText("Change")).toBeVisible();
  });

  it("calls clearSession when Change is clicked", async () => {
    const user = userEvent.setup();
    renderWithRouter();
    await user.click(screen.getByText("Change"));
    expect(clearSession).toHaveBeenCalledTimes(1);
  });
});
