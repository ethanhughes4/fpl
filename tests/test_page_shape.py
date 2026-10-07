"""The sample has exactly the fields web/src/brief.ts lists, at every level (D323)."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
BRIEF_TS = ROOT / "web" / "src" / "brief.ts"
SAMPLE = ROOT / "tests" / "data" / "brief-sample.json"
BLOCK = re.compile(r"export interface (\w+) \{\n(.*?)\n\}", re.S)
FIELD = re.compile(r"\s*(\w+): (.+);")


def interfaces(text):
    """{name: {field: type}} from plain interface blocks, one field per line."""
    out = {}
    for name, body in BLOCK.findall(text):
        out[name] = {}
        for line in body.splitlines():
            m = FIELD.fullmatch(line)
            assert m, f"{name}: cannot read line {line!r}"
            out[name][m[1]] = m[2]
    return out


def mismatches(value, type_name, types, where):
    """Every place the value's fields differ from the interface, following arrays and nesting."""
    if type_name not in types:
        return []
    if not isinstance(value, dict):
        return [f"{where}: expected an object for {type_name}"]
    want, got = set(types[type_name]), set(value)
    out = [f"{where}: missing {f}" for f in sorted(want - got)]
    out += [f"{where}: extra {f}" for f in sorted(got - want)]
    for f in sorted(want & got):
        t = types[type_name][f].replace(" | null", "")
        items = value[f] if t.endswith("[]") and isinstance(value[f], list) else [value[f]]
        for i, item in enumerate(items):
            if item is not None:
                out += mismatches(item, t.removesuffix("[]"), types, f"{where}.{f}[{i}]")
    return out


def test_reader_sees_every_field():
    types = interfaces("export interface A {\n  b: B[];\n  c: string | null;\n}\n\n"
                       "export interface B {\n  d: string;\n}")
    assert types == {"A": {"b": "B[]", "c": "string | null"}, "B": {"d": "string"}}
    assert mismatches({"b": [{"d": "x", "e": 1}], "c": None}, "A", types, "A") == ["A.b[0]: extra e"]
    assert mismatches({"b": [{}]}, "A", types, "A") == ["A: missing c", "A.b[0]: missing d"]


def test_sample_matches_brief_ts():
    types = interfaces(BRIEF_TS.read_text(encoding="utf-8").replace("\r\n", "\n"))
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    assert mismatches(sample, "Brief", types, "Brief") == []
