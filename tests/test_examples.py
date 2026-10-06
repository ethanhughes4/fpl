"""Hand-worked example weeks and the frozen golden brief.

The header line shows the deadline in local time, so it is checked for its
start only; every line below it must match the file exactly.
"""
from pathlib import Path

import pytest

from fpl.__main__ import main

DATA = Path(__file__).parent / "data"


def brief_below_header(folder, capsys):
    assert main(["--from", str(DATA / folder)]) == 0
    first, _, rest = capsys.readouterr().out.partition("\n")
    assert first.startswith("Gameweek 6 · deadline ")
    return rest


@pytest.mark.parametrize("name", ["a", "b", "c"])
def test_example(name, capsys):
    expected = (DATA / f"expected_{name}.txt").read_text(encoding="utf-8")
    assert brief_below_header(f"example_{name}", capsys) == expected


def test_golden(capsys):
    expected = (DATA / "golden.txt").read_text(encoding="utf-8")
    assert brief_below_header("snapshot", capsys) == expected


def test_example_c_header_counts_hand_entered_transfer(capsys):
    assert main(["--from", str(DATA / "example_c")]) == 0
    assert capsys.readouterr().out.splitlines()[0].endswith(" · includes 1 transfer entered by hand")
