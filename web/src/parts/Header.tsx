import type { Brief } from "../brief";
import "./Header.css";

export default function Header({ brief }: { brief: Brief }) {
  const h = brief.header;
  return (
    <header className="header">
      <div className="header-team muted">{h.team}</div>
      <h1 className="header-gw">{h.gameweek}</h1>
      <div className="header-deadline muted">{h.deadline}</div>
    </header>
  );
}
