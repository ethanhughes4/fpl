// Runs before every page test: a fake clock before the sample's deadline (D339),
// and a clean page after each test.
import { afterEach, beforeEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

export const BEFORE_DEADLINE = new Date("2026-10-07T12:00:00Z");

beforeEach(() => {
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(BEFORE_DEADLINE);
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
