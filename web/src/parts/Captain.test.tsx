import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Captain from "./Captain";
import { sample } from "../sample";

test("shows captain, vice, the tag and the sentence from the file", () => {
  render(<Captain brief={sample()} />);
  expect(screen.getByText("Groß")).toBeTruthy();
  expect(screen.getByText("7.9")).toBeTruthy();
  expect(screen.getByText("Vice: Tarkowski")).toBeTruthy();
  expect(screen.getByText("Close call")).toBeTruthy();
  expect(screen.getByText(/Gap of 0.7 for next gameweek/)).toBeTruthy();
});

test("no tag when the call is not close", () => {
  const b = sample();
  b.captain.close = false;
  render(<Captain brief={b} />);
  expect(screen.queryByText("Close call")).toBeNull();
});
