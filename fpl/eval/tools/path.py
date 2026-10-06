"""Reads stream-json events: which tools were called with what, what they printed, and whether
the path was right (D245). Takes data in, gives values out; nothing is downloaded."""
import json

from fpl import manual

PREFIX = "mcp__fpl__"


def calls(events):
    """[(tool, args)] in order, from the assistant tool_use blocks. Tools of other servers are kept
    under their full name, so the allowed check fails them."""
    out = []
    for e in events:
        if e.get("type") != "assistant":
            continue
        for b in (e.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                out.append((b["name"].removeprefix(PREFIX), b.get("input") or {}))
    return out


def outputs(events):
    """The text of every tool result. The SDK sends a string as {"result": "<text>"}; unwrapped."""
    out = []
    for e in events:
        content = (e.get("message") or {}).get("content") if e.get("type") == "user" else None
        for b in content if isinstance(content, list) else []:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                c = b.get("content")
                if isinstance(c, list):
                    c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
                try:
                    c = json.loads(c)["result"]
                except (ValueError, TypeError, KeyError):
                    pass
                out.append(str(c))
    return out


def _ids(arg, pool):
    """Every player id the argument could mean: an id, or each player the name fits (D229)."""
    text = str(arg).strip()
    if text.isdigit():
        return {int(text)}
    return {e["id"] for e in manual.matches(text, pool)}


def _values(args):
    for v in args.values():
        yield from v if isinstance(v, list) else [v]


def _fits(slot, values, pool):
    if isinstance(slot, str):
        return slot in values
    return any(ids and ids <= slot for ids in (_ids(v, pool) for v in values))


def check(question, made, pool):
    """-> (right, reason). Every required tool called with every slot met (across calls, any order),
    and no tool outside the allowed set."""
    for tool, args in made:
        if tool not in question.allowed:
            return False, f"called {tool}, which is not allowed"
    for tool, slots in question.required:
        values = [v for t, a in made if t == tool for v in _values(a)]
        if not any(t == tool for t, _ in made):
            return False, f"never called {tool}"
        for slot in slots:
            if not _fits(slot, values, pool):
                return False, f"{tool} was not given {slot}"
    return True, ""
