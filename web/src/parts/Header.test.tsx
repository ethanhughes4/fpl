import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Header from "./Header";
import { sample } from "../sample";

test("shows team, gameweek and deadline from the file", () => {
  render(<Header brief={sample()} />);
  expect(screen.getByText("Ethans Team")).toBeTruthy();
  expect(screen.getByText("Gameweek 6")).toBeTruthy();
  expect(screen.getByText("Deadline Sat 10 Oct 12:00")).toBeTruthy();
});
