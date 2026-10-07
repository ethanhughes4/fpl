import type { Brief } from "../brief";
import "./Captain.css";

export default function Captain({ brief }: { brief: Brief }) {
  const c = brief.captain;
  return (
    <section className="card captain">
      <div className="captain-head">
        <h2>Captain</h2>
        {c.close && <span className="captain-tag">Close call</span>}
      </div>
      <div className="captain-row">
        <span className="captain-name">{c.captain}</span>
        <span className="num captain-score">{c.captain_score}</span>
      </div>
      <div className="captain-row muted">
        <span>Vice: {c.vice}</span>
        <span className="num">{c.vice_score}</span>
      </div>
      <p className="captain-sentence muted">{c.sentence}</p>
    </section>
  );
}
