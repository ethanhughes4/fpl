import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Warnings from "./Warnings";
import { sample } from "../sample";

test("shows a row with name, chance and news", () => {
  render(<Warnings brief={sample()} />);
  expect(screen.getByText("Warnings")).toBeTruthy();
  expect(screen.getByText("João Pedro")).toBeTruthy();
  expect(screen.getByText("75%")).toBeTruthy();
  expect(screen.getByText("Knee injury - 75% chance of playing")).toBeTruthy();
});

test("shows the empty line when there are none", () => {
  const b = sample();
  b.warnings = { rows: [], empty: "Warnings: none" };
  render(<Warnings brief={b} />);
  expect(screen.getByText("Warnings: none")).toBeTruthy();
  expect(screen.queryByText("Warnings")).toBeNull();
});
