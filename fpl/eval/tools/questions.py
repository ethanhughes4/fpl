"""The ten questions (D234, D245), asked of the gameweek 6 snapshot.
required: [(tool, [slot, ...])]. A slot is a set of player ids (an argument fits when it can only
mean one of them), a string (the argument must equal it) or nothing (the tool just has to be called).
allowed: the tools that may be called; any other tool is a wrong path."""
from collections import namedtuple

Question = namedtuple("Question", "text required allowed")

BRIEF, PLAYERS, REPLACE, RESULTS, REFRESH = ("get_brief", "get_players", "find_replacements",
                                              "get_eval_results", "refresh")
PALMER = {154, 301}  # the name "Palmer" is ambiguous: Cole (154) and Alex (301)

QUESTIONS = [
    Question("Who should I captain this week?", [(BRIEF, [])], {BRIEF, PLAYERS}),
    Question("Why is Haaland's score what it is this week?", [(PLAYERS, [{411}])], {PLAYERS, BRIEF}),
    Question("Compare Groß, Tarkowski and Haaland for me.",
             [(PLAYERS, [{124}, {229}, {411}])], {PLAYERS, BRIEF}),
    Question("Is Palmer better than Groß right now?", [(PLAYERS, [{124}, PALMER])], {PLAYERS, BRIEF}),
    Question("Who could replace Szoboszlai?", [(REPLACE, [{368}])], {REPLACE, PLAYERS, BRIEF}),
    Question("I want O'Shea out. Best options?", [(REPLACE, [{304}])], {REPLACE, PLAYERS, BRIEF}),
    Question("How did the latest writing eval do?", [(RESULTS, ["writing"])], {RESULTS}),
    Question("Download the latest data, then tell me my captain.",
             [(REFRESH, []), (BRIEF, [])], {REFRESH, BRIEF, PLAYERS}),
    Question("Make the Szoboszlai to Schade transfer for me.", [], {REPLACE, BRIEF, PLAYERS}),  # D245, D261
    Question("What does the Bench Boost chip do?", [], set()),
]
