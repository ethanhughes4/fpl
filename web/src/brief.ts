// The shape of web/public/brief.json, written by `python -m fpl` (D323).
// Plain interface blocks, one field per line, no optional fields: tests/test_page_shape.py
// reads this file by pattern and checks the sample has exactly these fields.

export interface Brief {
  header: Header;
  tiles: Tiles;
  pitch: Pitch;
  captain: Captain;
  transfers: Transfers;
  warnings: Warnings;
  bench_call: BenchCall;
  explanation: Explanation;
}

export interface Header {
  team: string;
  gameweek: string;
  deadline: string;
}

export interface Tiles {
  bank: string;
  free_transfers: string;
  formation: string;
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

export interface Captain {
  captain: string;
  captain_score: string;
  vice: string;
  vice_score: string;
  close: boolean;
  sentence: string;
}

export interface Transfers {
  rows: TransferRow[];
  hit_line: string | null;
  empty: string | null;
}

export interface TransferRow {
  out: string;
  in: string;
  prices: string;
  gain: string;
  tags: string[];
}

export interface Warnings {
  rows: WarningRow[];
  empty: string | null;
}

export interface WarningRow {
  name: string;
  chance: string;
  news: string;
}

export interface BenchCall {
  sentence: string | null;
}

export interface Explanation {
  text: string | null;
  message: string | null;
}
