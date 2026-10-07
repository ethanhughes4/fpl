import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import Tiles from "./Tiles";
import { sample } from "../sample";

test("shows bank, free transfers and formation from the file", () => {
  render(<Tiles brief={sample()} />);
  expect(screen.getByText("Bank").nextSibling?.textContent).toBe("0.0m");
  expect(screen.getByText("Free transfers").nextSibling?.textContent).toBe("4");
  expect(screen.getByText("Formation").nextSibling?.textContent).toBe("3-4-3");
});
