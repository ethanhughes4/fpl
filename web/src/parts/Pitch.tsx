import { useState } from "react";
import type { Brief, Player } from "../brief";
import "./Pitch.css";

type Span = "next" | "six";

function Chip({ p, span, label }: { p: Player; span: Span; label: string }) {
  const cls = ["chip", p.role === "CAPTAIN" ? "chip-captain" : "", p.role === "VICE" ? "chip-vice" : "",
    p.doubt ? "chip-doubt" : ""].join(" ");
  return (
    <div className={cls}>
      <div className="chip-tag">{label}</div>
      <div className="chip-name">{p.name}</div>
      <div className="chip-score num">{p[span]}</div>
    </div>
  );
}

export default function Pitch({ brief }: { brief: Brief }) {
  const [span, setSpan] = useState<Span>("next");
  const { rows, bench } = brief.pitch;
  const tab = (s: Span, text: string) => (
    <button className={s === span ? "tab tab-on" : "tab"} aria-pressed={s === span} onClick={() => setSpan(s)}>
      {text}
    </button>
  );
  return (
    <section className="card pitch-card">
      <div className="pitch-head">
        <h2>Starting eleven</h2>
        <div className="tabs">
          {tab("next", "Next gameweek")}
          {tab("six", "Next 6 gameweeks")}
        </div>
      </div>
      <div className="pitch">
        {rows.map((row, i) => (
          <div className="pitch-row" key={i}>
            {row.players.map((p) => <Chip key={p.name} p={p} span={span} label={p.role ?? p.doubt ?? ""} />)}
          </div>
        ))}
      </div>
      <div className="bench">
        <div className="bench-title muted">BENCH, IN ORDER</div>
        <div className="bench-row">
          {bench.map((b) => <Chip key={b.name} p={b} span={span} label={b.doubt ?? b.label} />)}
        </div>
      </div>
    </section>
  );
}
