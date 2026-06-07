import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ConsumerSetupModal from "./ConsumerSetupModal.jsx";
import { createConsumer } from "../lib/api.js";

const setSession = vi.fn();

vi.mock("../hooks/useConsumerSession.js", () => ({
  default: () => ({ setSession }),
}));

vi.mock("../lib/api.js", () => ({
  createConsumer: vi.fn(),
}));

describe("ConsumerSetupModal", () => {
  beforeEach(() => {
    setSession.mockClear();
    createConsumer.mockReset();
  });

  it("submits first name and last name in the consumer payload", async () => {
    const user = userEvent.setup();
    createConsumer.mockResolvedValue({
      id: "11111111-1111-4111-8111-111111111111",
    });

    render(<ConsumerSetupModal />);

    await user.type(screen.getByLabelText(/first name/i), "abc");
    await user.type(screen.getByLabelText(/last name/i), "test");
    await user.click(screen.getByRole("button", { name: /continue/i }));

    expect(createConsumer).toHaveBeenCalledWith(
      expect.objectContaining({
        first_name: "abc",
        last_name: "test",
      }),
    );
    expect(createConsumer.mock.calls[0][0].email).toMatch(/^abc\.test\..+@example\.com$/);
    expect(setSession).toHaveBeenCalledWith({
      consumer_id: "11111111-1111-4111-8111-111111111111",
      display_name: "abc test",
    });
  });

  it("does not call the backend when either name is blank", async () => {
    const user = userEvent.setup();

    render(<ConsumerSetupModal />);

    await user.type(screen.getByLabelText(/first name/i), "abc");
    await user.click(screen.getByRole("button", { name: /continue/i }));

    expect(createConsumer).not.toHaveBeenCalled();
    expect(await screen.findByText("First name and last name are required.")).toBeVisible();
  });
});
