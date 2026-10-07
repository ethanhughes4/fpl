// The shape of web/public/brief.json, written by `python -m fpl` (D323).
// Plain interface blocks, one field per line, no optional fields: tests/test_page_shape.py
// reads this file by pattern and checks the sample has exactly these fields.

export interface Brief {
  header: Header;
  pitch: Pitch;
}

export interface Header {
  team: string;
  gameweek: string;
  deadline: string;
}

export interface Pitch {
  rows: Row[];
  bench: BenchPlayer[];
}

export interface Row {
  players: Player[];
}

export interface Player {
  name: string;
  next: string;
  six: string;
  role: string | null;
  doubt: string | null;
}

export interface BenchPlayer {
  label: string;
  name: string;
  next: string;
  six: string;
  role: string | null;
  doubt: string | null;
}
