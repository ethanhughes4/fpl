from pathlib import Path

from fpl import brief, feed as feedmod
from fpl.explain import explain
from fpl.explain.checks import captain, close, length, warnings

DATA = Path(__file__).parent / "data"


def ctx(x):
    return {"data": brief.build(feedmod.load(str(DATA / f"example_{x}")))}


def test_a():
    c = ctx("a")
    assert captain.check("Hart is captain, 0.6 ahead of Marsh.", c) is None
    assert captain.check("Take Marsh.", c) is not None
    assert close.check("Hart over Marsh. Kemp 4.1, Fry 4.1, Orr 3.8.", c) is None
    assert close.check("Hart over Marsh, a clear pick.", c) is not None  # bench call missing
    assert close.check("Hart then Orr and Fry and Kemp.", c) is not None  # Marsh missing (D184)
    assert warnings.check("nothing to say", c) is None  # no warnings


def test_b():
    c = ctx("b")
    assert warnings.check("HART is injured, benched.", c) is None
    assert warnings.check("Marsh is captain.", c) == "it did not mention Hart, who has a warning"
    assert close.check("Marsh edges Innes by 0.1.", c) is None  # transfer not close: not required
    assert close.check("Marsh is captain.", c) is not None


def test_c():
    c = ctx("c")
    assert close.check("Hart over Marsh by 0.6. Kemp and Fry tie on 4.1.", c) is None
    assert close.check("Hart over Marsh by 0.6.", c) is not None
    assert close.check("Kemp and Fry tie.", c) is not None


def test_length():
    assert length.check("word " * 150, {}) is None
    assert length.check("word " * 151, {}) is not None


def test_live_explain_ignores_eval_only_failure():
    path = str(DATA / "example_b")
    f = feedmod.load(path)
    text = "Pick whoever."  # fails captain, warnings, close; passes numbers and names
    out = explain(brief.build(f), f, lambda *a: (text, None, "m"))
    assert out == ["Explanation", text]
