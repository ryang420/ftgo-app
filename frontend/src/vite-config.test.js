// @vitest-environment node

import { describe, expect, it } from "vitest";
import config from "../vite.config.js";

describe("vite proxy routes", () => {
  it("keeps the kitchen SPA route out of the API proxy", () => {
    const proxy = config.server.proxy;

    expect(proxy).not.toHaveProperty("/kitchen");
    expect(proxy).toHaveProperty("/kitchen/tickets");
  });
});
