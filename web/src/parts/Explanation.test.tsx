import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Explanation from "./Explanation";
import { Page } from "../App";
import { sample } from "../sample";

test("shows the sample's message", () => {
  render(<Explanation brief={sample()} />);
  expect(screen.getByText("No explanation for this run.")).toBeTruthy();
});

test("shows the text", () => {
  const b = sample();
  b.explanation = { text: "Captain Groß at 7.9.", message: null };
  render(<Explanation brief={b} />);
  expect(screen.getByText("Captain Groß at 7.9.")).toBeTruthy();
  expect(screen.queryByText("No explanation for this run.")).toBeNull();
});

test("shows the skipped reason", () => {
  const b = sample();
  b.explanation = { text: null, message: "Explanation skipped: timed out." };
  render(<Explanation brief={b} />);
  expect(screen.getByText("Explanation skipped: timed out.")).toBeTruthy();
});

test("the rest of the page still shows when skipped", () => {
  const b = sample();
  b.explanation = { text: null, message: "Explanation skipped: timed out." };
  render(<Page brief={b} />);
  expect(screen.getByText("Explanation skipped: timed out.")).toBeTruthy();
  expect(screen.getByText("Gameweek 6")).toBeTruthy();
});
