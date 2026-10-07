import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Header from "./Header";
import Pitch from "./Pitch";
import { sample } from "../sample";

const chip = (name: string) => screen.getByText(name).closest(".chip") as HTMLElement;

test("captain filled, vice outlined, doubtful dashed", () => {
  render(<Pitch brief={sample()} />);
  expect(chip("Groß").className).toContain("chip-captain");
  expect(chip("Groß").textContent).toContain("CAPTAIN");
  expect(chip("Tarkowski").className).toContain("chip-vice");
  expect(chip("Tarkowski").textContent).toContain("VICE");
  expect(chip("João Pedro").className).toContain("chip-doubt");
  expect(chip("João Pedro").textContent).toContain("75% to play");
});

test("goalkeeper row first, bench in order", () => {
  const { container } = render(<Pitch brief={sample()} />);
  expect(container.querySelector(".pitch-row")?.textContent).toContain("Verbruggen");
  expect(container.querySelector(".bench-row")?.textContent).toMatch(/GKKinsky.*1stDiop.*2nd.*3rd/);
});

test("the switch changes pitch and bench scores only", () => {
  const brief = sample();
  const { container } = render(<><Header brief={brief} /><Pitch brief={brief} /></>);
  const header = container.querySelector("header")!.textContent;
  const all = () => [...container.querySelectorAll(".chip-score")].map((e) => e.textContent);
  const players = [...brief.pitch.rows.flatMap((r) => r.players), ...brief.pitch.bench];
  expect(all()).toEqual(players.map((p) => p.next));
  fireEvent.click(screen.getByText("Next 6 gameweeks"));
  expect(all()).toEqual(players.map((p) => p.six));
  expect(container.querySelector("header")!.textContent).toBe(header);
  expect(container.querySelector(".chip-tag")!.textContent).toBe("");
  fireEvent.click(screen.getByText("Next gameweek"));
  expect(all()).toEqual(players.map((p) => p.next));
});
