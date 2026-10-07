import type { Brief } from "../brief";
import "./BenchCall.css";

export default function BenchCall({ brief }: { brief: Brief }) {
  const s = brief.bench_call.sentence;
  if (s === null) return null;
  return (
    <section className="card bench-call">
      <h2>Bench call</h2>
      <p className="muted">{s}</p>
    </section>
  );
}
