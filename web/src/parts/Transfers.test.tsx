import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Transfers from "./Transfers";
import { sample } from "../sample";

test("shows the rows, prices and gains from the file", () => {
  render(<Transfers brief={sample()} />);
  expect(screen.getByText("Not made yet")).toBeTruthy();
  expect(screen.getByText("Szoboszlai → Schade")).toBeTruthy();
  expect(screen.getByText("6.9m → 6.2m")).toBeTruthy();
  expect(screen.getByText("+14.7")).toBeTruthy();
  expect(screen.getByText("O'Shea → Davis")).toBeTruthy();
});

test("shows tags and the hit line", () => {
  const b = sample();
  b.transfers.rows[0].tags = ["−4 hit", "bench, half gain"];
  b.transfers.hit_line = "Hit: -4 points";
  render(<Transfers brief={b} />);
  expect(screen.getByText("−4 hit")).toBeTruthy();
  expect(screen.getByText("bench, half gain")).toBeTruthy();
  expect(screen.getByText("Hit: -4 points")).toBeTruthy();
});

test("with no transfer it shows the empty line and hides the tag", () => {
  const b = sample();
  b.transfers.rows = [];
  b.transfers.empty = "No transfer worth making. Save your 3 free transfers — you'll have 4 free next week.";
  render(<Transfers brief={b} />);
  expect(screen.getByText(b.transfers.empty)).toBeTruthy();
  expect(screen.queryByText("Not made yet")).toBeNull();
});
