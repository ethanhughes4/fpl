import type { Brief } from "../brief";
import "./Warnings.css";

export default function Warnings({ brief }: { brief: Brief }) {
  const w = brief.warnings;
  return (
    <section className="card warnings">
      {w.empty !== null ? (
        <p className="muted">{w.empty}</p>
      ) : (
        <>
          <h2>Warnings</h2>
          {w.rows.map((r) => (
            <div className="warnings-row" key={r.name}>
              <span className="warnings-name">{r.name}</span>
              <span className="num warnings-chance">{r.chance}</span>
              <span className="warnings-news muted">{r.news}</span>
            </div>
          ))}
        </>
      )}
    </section>
  );
}
