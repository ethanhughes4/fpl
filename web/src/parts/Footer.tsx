import type { Brief } from "../brief";
import "./Footer.css";

export default function Footer({ brief }: { brief: Brief }) {
  const f = brief.footer;
  return (
    <footer className="footer muted">
      <div className="footer-notes">
        {f.notes.map((n, i) => (
          <div key={i}>{n}</div>
        ))}
        <div>{f.downloaded}</div>
      </div>
      <div className="footer-evals">
        {f.evals.map((e, i) => (
          <div key={i}>{e}</div>
        ))}
      </div>
    </footer>
  );
}
