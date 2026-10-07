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


def test_failures_lists_every_bad_number_once():
    assert numbers.failures("7.9 then 8.1, 7.4 and 8.1 again", {"block": BLOCK}) == ["8.1", "7.4"]
    assert numbers.failures("7.9", {"block": BLOCK}) == []


def test_list_markers_at_line_start_ignored():
    """D263: "2." and "3)" numbering a line are not quoted numbers; the same digits elsewhere are."""
    assert chk("1. Hart 7.9\n2. Gain -4\n  3) Chance 25%") is None
    assert chk("Price 6.9m\n12. Hart") is None
    assert numbers.failures("Point 2. Done.\n2.Hart 3.", {"block": BLOCK}) == ["2", "3"]


def test_thousands_separators_one_number_either_form():
    """D264: "113,590" is 113590; the block may print either form."""
    assert numbers.failures("113,590 tokens", {"block": "Total tokens: 113590"}) == []
    assert numbers.failures("113590 tokens", {"block": "Total tokens: 113,590"}) == []
    assert numbers.failures("113,590 tokens", {"block": "113 and 590"}) == ["113,590"]
    assert numbers.failures("1,234.5 and 7,9", {"block": "1234.5 7 9"}) == []  # "7,9" is two numbers


def test_live_flag():
    assert numbers.LIVE is True and numbers.NAME == "numbers"
