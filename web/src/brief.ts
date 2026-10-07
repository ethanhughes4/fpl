// The shape of web/public/brief.json, written by `python -m fpl` (D323).
// Plain interface blocks, one field per line, no optional fields: tests/test_page_shape.py
// reads this file by pattern and checks the sample has exactly these fields.

export interface Brief {
  header: Header;
  transfers: Transfers;
}

export interface Header {
  team: string;
  gameweek: string;
  deadline: string;
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
