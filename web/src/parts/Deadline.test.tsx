import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import Deadline from "./Deadline";
import { Page } from "../App";
import { sample } from "../sample";

test("no banner before the deadline", () => {
  render(<Deadline brief={sample()} />);
  expect(screen.queryByRole("alert")).toBeNull();
});

test("banner after the deadline, and the header still shows", () => {
  vi.setSystemTime(new Date("2026-10-10T10:00:01Z"));
  render(<Page brief={sample()} />);
  expect(screen.getByRole("alert").textContent).toBe("Gameweek 6's deadline has passed. Run python -m fpl.");
  expect(screen.getByText("Gameweek 6")).toBeTruthy();
});
