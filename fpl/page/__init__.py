"""The data file the web page reads (D278, D288). Takes the brief in, writes text out. No network."""
import json
from pathlib import Path

from fpl.page.parts import bench_call, header

PATH = Path(__file__).parents[2] / "web" / "public" / "brief.json"  # repo root, any working folder (D321)

PARTS = [header, bench_call]  # to switch a part on: add its file in fpl/page/parts/, add one line here


def build(data, feed, downloaded, explanation):
    """explanation: the lines explain.explain returned, or None when it did not run."""
    run = {"data": data, "feed": feed, "downloaded": downloaded, "explanation": explanation}
    return {p.__name__.rsplit(".", 1)[-1]: p.build(run) for p in PARTS}


def write(data, feed, downloaded, explanation, path=None):
    path = Path(path or PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(build(data, feed, downloaded, explanation), indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")
