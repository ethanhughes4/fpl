import type { Brief } from "../brief";
import "./Transfers.css";

export default function Transfers({ brief }: { brief: Brief }) {
  const t = brief.transfers;
  return (
    <section className="card transfers">
      <div className="transfers-head">
        <h2>Suggested transfers</h2>
        {t.empty === null && <span className="muted transfers-made">Not made yet</span>}
      </div>
      {t.empty !== null && <p className="muted">{t.empty}</p>}
      {t.rows.map((r, i) => (
        <div className="transfers-row" key={i}>
          <div>
            <div className="transfers-names">{r.out} → {r.in}</div>
            <div className="muted transfers-prices">{r.prices}</div>
            {r.tags.map((tag) => <span className="transfers-tag" key={tag}>{tag}</span>)}
          </div>
          <div className="transfers-gain">
            <div className="num">{r.gain}</div>
            <div className="muted transfers-over">over 6 GW</div>
          </div>
        </div>
      ))}
      {t.hit_line !== null && <p className="muted">{t.hit_line}</p>}
    </section>
  );
}
