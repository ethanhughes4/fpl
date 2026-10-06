from fpl.explain.checks import names

FEED = {"bootstrap": {
    "elements": [
        {"web_name": "Hart", "first_name": "Sam", "second_name": "Hart"},
        {"web_name": "Salah", "first_name": "Mohamed", "second_name": "Salah"},
        {"web_name": "João Pedro", "first_name": "João", "second_name": "Pedro Junior"},
        {"web_name": "Pedro Neto", "first_name": "Pedro", "second_name": "Lomba Neto"},
        {"web_name": "Wood", "first_name": "Will", "second_name": "Wood"},
    ],
    "teams": [{"name": "Arsenal", "short_name": "ARS"}, {"name": "Spurs", "short_name": "TOT"},
              {"name": "Newcastle", "short_name": "NEW"}],
}}
BLOCK = "Captain: Hart 7.9\nJoão Pedro 5.0 (ARS)\nArsenal"


def chk(text):
    return names.check(text, {"feed": FEED, "block": BLOCK})


def test_allowed_passes():
    assert chk("Hart is captain and Sam Hart plays for Arsenal.") is None


def test_feed_name_not_in_block_fails():
    assert chk("Salah would be better.") == "it named Salah, who is not in the brief"


def test_accents_and_case():
    assert chk("JOAO PEDRO starts.") is None


def test_pedro_case():
    # "Pedro Neto" is another player; "João Pedro" must not trip on "Pedro"
    assert chk("João Pedro starts.") is None
    assert chk("Pedro Neto starts.") == "it named Pedro Neto, who is not in the brief"


def test_club_fails():
    assert "Spurs" in chk("They face Spurs.")
    assert "TOT" in chk("They face TOT.")


def test_ordinary_words_pass():
    # D190: lower-case words are not names; a club code counts only in capitals
    assert chk("You will have a new free transfer; wood and tot are words.") is None
    assert chk("They face New next week.") is None


def test_capitalised_names_fail():
    assert "Wood" in chk("Bring in Wood.")
    assert "Will" in chk("Ask Will.")
    assert "NEW" in chk("They face NEW.")


def test_whole_words_only():
    assert chk("Hartley is irrelevant, a salahood too.") is None


def test_unknown_name_passes():
    assert chk("Haaland would be better.") is None


def test_live_flag():
    assert names.LIVE is True and names.NAME == "names"


def test_club_code_in_block_allows_club():
    block = BLOCK + "\nnext opponent TOT (A)"
    ctx = {"feed": FEED, "block": block}
    assert names.check("Away at TOT, then Spurs again.", ctx) is None
    assert "NEW" in names.check("They face NEW.", ctx)
