import type { Brief } from "../brief";
import "./Tiles.css";

export default function Tiles({ brief }: { brief: Brief }) {
  const t = brief.tiles;
  const tiles: [string, string][] = [
    ["Bank", t.bank],
    ["Free transfers", t.free_transfers],
    ["Formation", t.formation],
  ];
  return (
    <div className="tiles">
      {tiles.map(([label, value]) => (
        <div className="tile" key={label}>
          <div className="tile-label muted">{label}</div>
          <div className="tile-value">{value}</div>
        </div>
      ))}
    </div>
  );
}
