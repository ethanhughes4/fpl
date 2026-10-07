import type { Brief } from "../brief";
import "./Explanation.css";

export default function Explanation({ brief }: { brief: Brief }) {
  const e = brief.explanation;
  return (
    <section className="card explanation">
      <h2>Explanation</h2>
      {e.text !== null && <p className="explanation-text">{e.text}</p>}
      {e.message !== null && <p className="explanation-message muted">{e.message}</p>}
    </section>
  );
}
