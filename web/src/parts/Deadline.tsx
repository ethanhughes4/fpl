import type { Brief } from "../brief";
import "./Deadline.css";

// The one comparison the page makes: the file's deadline against the clock (D300).
export default function Deadline({ brief }: { brief: Brief }) {
  const d = brief.deadline;
  if (Date.now() < new Date(d.utc).getTime()) return null;
  return <div className="deadline-banner" role="alert">{d.passed}</div>;
}
