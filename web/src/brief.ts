// The shape of web/public/brief.json, written by `python -m fpl` (D323).
// Plain interface blocks, one field per line, no optional fields: tests/test_page_shape.py
// reads this file by pattern and checks the sample has exactly these fields.

export interface Brief {
  header: Header;
  tiles: Tiles;
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
