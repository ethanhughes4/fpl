import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import BenchCall from "./BenchCall";
import { sample } from "../sample";

test("shows the bench call sentence from the file", () => {
  render(<BenchCall brief={sample()} />);
  expect(screen.getByText("Bench call")).toBeTruthy();
  expect(screen.getByText(/^Calvert-Lewin starts at 2\.9\. Diop is the best.*close\.$/)).toBeTruthy();
});

test("shows nothing when there is no bench call", () => {
  const b = sample();
  b.bench_call.sentence = null;
  const { container } = render(<BenchCall brief={b} />);
  expect(container.innerHTML).toBe("");
});
