import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import OrderConfirmationDrawer from "./OrderConfirmationDrawer.jsx";
import { placeOrder } from "../lib/api.js";

vi.mock("../lib/api.js", () => ({
  placeOrder: vi.fn(),
}));

const cart = {
  items: [
    { menu_item_id: "1", name: "Pizza", unit_price: 12.0, quantity: 2 },
  ],
};

describe("OrderConfirmationDrawer", () => {
  beforeEach(() => {
    placeOrder.mockReset();
  });

  it("prevents submission when address is empty", async () => {
    const user = userEvent.setup();
    render(
      <OrderConfirmationDrawer
        cart={cart}
        restaurantName="Test"
        consumerId="c1"
        restaurantId="r1"
        onClose={vi.fn()}
        onOrderPlaced={vi.fn()}
      />
    );

    // Clear the pre-filled address (from localStorage mock)
    const input = screen.getByPlaceholderText("Enter your delivery address");
    await user.clear(input);

    await user.click(screen.getByRole("button", { name: /confirm & place order/i }));
    expect(screen.getByText("Delivery address is required")).toBeVisible();
    expect(placeOrder).not.toHaveBeenCalled();
  });

  it("disables the submit button and shows loading state during submission", async () => {
    const user = userEvent.setup();
    // Make placeOrder never resolve to keep the loading state
    placeOrder.mockReturnValue(new Promise(() => {}));

    render(
      <OrderConfirmationDrawer
        cart={cart}
        restaurantName="Test"
        consumerId="c1"
        restaurantId="r1"
        onClose={vi.fn()}
        onOrderPlaced={vi.fn()}
      />
    );

    const input = screen.getByPlaceholderText("Enter your delivery address");
    await user.clear(input);
    await user.type(input, "123 Main St");

    const submitButton = screen.getByRole("button", { name: /confirm & place order/i });
    await user.click(submitButton);

    // Button should now show loading text and be disabled
    expect(screen.getByText("Placing order...")).toBeVisible();
    expect(submitButton).toBeDisabled();
  });
});
