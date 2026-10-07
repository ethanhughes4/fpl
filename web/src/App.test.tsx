import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { BROKEN, NO_FILE, PARTS, Page, load } from "./App";
import { sample } from "./sample";

function serve(status: number, body: string, type: string) {
  vi.stubGlobal("fetch", async () => new Response(body, { status, headers: { "content-type": type } }));
}

test("no file: says to run python -m fpl", async () => {
  serve(404, "", "text/plain");
  expect(await load()).toEqual({ kind: "message", text: NO_FILE });
});

test("Vite's index.html in place of a missing file counts as no file", async () => {
  serve(200, "<!doctype html>", "text/html");
  expect(await load()).toEqual({ kind: "message", text: NO_FILE });
});

test("bad JSON: could not be read", async () => {
  serve(200, "{not json", "application/json");
  expect(await load()).toEqual({ kind: "message", text: BROKEN });
});

test("a good file loads", async () => {
  serve(200, JSON.stringify(sample()), "application/json");
  expect(await load()).toEqual({ kind: "ok", brief: sample() });
});

test("a missing part shows only the could-not-read message", () => {
  vi.spyOn(console, "error").mockImplementation(() => {});
  const { header: _, ...broken } = sample();
  render(<Page brief={broken as never} />);
  expect(screen.getByText(BROKEN)).toBeTruthy();
});

test("every part draws from the sample", () => {
  render(<Page brief={sample()} />);
  expect(PARTS.length).toBeGreaterThan(0);
  expect(screen.queryByText(BROKEN)).toBeNull();
  expect(screen.getByText("Gameweek 6")).toBeTruthy();
});
