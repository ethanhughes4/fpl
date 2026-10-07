// The page tests' data: tests/data/brief-sample.json, made by `python -m tests.make_sample`.
// sample() gives a fresh copy, so a test can change a field without touching the others.
import data from "../../tests/data/brief-sample.json";
import type { Brief } from "./brief";

export const sample = (): Brief => structuredClone(data) as Brief;
