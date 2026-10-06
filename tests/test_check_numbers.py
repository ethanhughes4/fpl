from fpl.explain.checks import numbers

BLOCK = "Captain: Hart 7.9 (a 4-point hit)\nPrice 6.9m  Chance 25%  Gameweek 6\nGain -4"


def chk(text):
    return numbers.check(text, {"block": BLOCK})


def test_good():
    assert chk("Hart scores 7.9, a 4-point hit, costing 6.9m, in gameweek 6 at 25%.") is None


def test_sign_and_m_ignored():
    assert chk("A 4-point hit.") is None
    assert chk("He costs 6.9m.") is None


def test_no_numbers():
    assert chk("Nothing here.") is None


def test_bad():
    assert chk("Hart scores 7.4 this week.") == "it quoted 7.4, which is not in the brief"


def test_first_bad_reported():
    assert "8.1" in chk("7.9 then 8.1 then 7.4")


def test_live_flag():
    assert numbers.LIVE is True and numbers.NAME == "numbers"
