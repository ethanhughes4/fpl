import { Component, useEffect, useState, type ComponentType, type ReactNode } from "react";
import type { Brief } from "./brief";
import Deadline from "./parts/Deadline";
import Header from "./parts/Header";
import Tiles from "./parts/Tiles";
import Pitch from "./parts/Pitch";
import Captain from "./parts/Captain";
import Transfers from "./parts/Transfers";
import Warnings from "./parts/Warnings";
import BenchCall from "./parts/BenchCall";
import Explanation from "./parts/Explanation";

type Slot = "top" | "main" | "side" | "bottom";

// Each part of the page: where it goes, and the component that draws it.
// To switch a component on: add its file in parts/, add one line here.
export const PARTS: [Slot, ComponentType<{ brief: Brief }>][] = [
  ["top", Deadline],
  ["top", Header],
  ["top", Tiles],
  ["main", Pitch],
  ["side", Captain],
  ["side", Transfers],
  ["side", Warnings],
  ["side", BenchCall],
  ["bottom", Explanation],
];

export const NO_FILE = "No brief yet. Run python -m fpl."; // D299
export const BROKEN = "Brief file could not be read. Run python -m fpl again."; // D301

type State = { kind: "loading" } | { kind: "message"; text: string } | { kind: "ok"; brief: Brief };

export async function load(): Promise<State> {
  let res: Response;
  try {
    res = await fetch("/brief.json", { cache: "no-store" });
  } catch {
    return { kind: "message", text: NO_FILE };
  }
  // Vite answers a missing file with its index.html page, not a 404: only JSON counts as a file.
  if (!res.ok || !res.headers.get("content-type")?.includes("json")) {
    return { kind: "message", text: NO_FILE };
  }
  try {
    const brief = await res.json();
    if (typeof brief !== "object" || brief === null || Array.isArray(brief)) throw new Error();
    return { kind: "ok", brief };
  } catch {
    return { kind: "message", text: BROKEN };
  }
}

// An error boundary: a React component that catches any crash while drawing what is inside it.
// A file with a missing field crashes a part, and this shows only the D301 message instead.
class Guard extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? <p className="message">{BROKEN}</p> : this.props.children;
  }
}

export function Page({ brief }: { brief: Brief }) {
  const slot = (s: Slot) =>
    PARTS.filter(([at]) => at === s).map(([, Part], i) => <Part key={i} brief={brief} />);
  return (
    <Guard>
      <main className="page">
        <div className="slot-top">{slot("top")}</div>
        <div className="slot-main">{slot("main")}</div>
        <div className="slot-side">{slot("side")}</div>
        <div className="slot-bottom">{slot("bottom")}</div>
      </main>
    </Guard>
  );
}

export default function App() {
  const [state, setState] = useState<State>({ kind: "loading" });
  useEffect(() => {
    load().then(setState);
  }, []);
  if (state.kind === "loading") return null;
  if (state.kind === "message") return <p className="message">{state.text}</p>;
  return <Page brief={state.brief} />;
}
