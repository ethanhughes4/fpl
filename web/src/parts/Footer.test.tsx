import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Footer from "./Footer";
import { sample } from "../sample";

test("shows the download time, notes and eval lines from the file", () => {
  const brief = sample();
  render(<Footer brief={brief} />);
  expect(screen.getByText(brief.footer.downloaded)).toBeTruthy();
  for (const n of brief.footer.notes) expect(screen.getByText(n)).toBeTruthy();
  for (const e of brief.footer.evals) expect(screen.getByText(e)).toBeTruthy();
  expect(screen.getByText(/^Data downloaded /)).toBeTruthy();
  expect(screen.queryByText(/PASS|FAIL/)).toBeNull();
});

test("shows a changed note and a missing eval as the file says", () => {
  const brief = sample();
  brief.footer.notes = ["includes 1 transfer entered by hand"];
  brief.footer.evals = ["Scoring eval: no results yet"];
  render(<Footer brief={brief} />);
  expect(screen.getByText("includes 1 transfer entered by hand")).toBeTruthy();
  expect(screen.getByText("Scoring eval: no results yet")).toBeTruthy();
});
