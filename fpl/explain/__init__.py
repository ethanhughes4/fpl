from pathlib import Path

from fpl.claude import AskError
from fpl.explain import block, check

WRITER_MODEL = "haiku"
WRITER_TIMEOUT = 120  # D176, raised by D194: a real call took 62 s
MAX_WORDS = 150


def writer_prompt():
    text = (Path(__file__).parent / "writer.txt").read_text(encoding="utf-8")
    return text.replace("{max_words}", str(MAX_WORDS))


def explain(data, feed, ask):
    """Returns the lines to print. No retry (D146)."""
    blk = block.build(data, feed)
    try:
        text = ask(blk, writer_prompt(), WRITER_MODEL, WRITER_TIMEOUT)[0].strip()
    except AskError as e:
        return [f"Explanation skipped: {e.reason}."]
    reason = check.run(text, {"data": data, "feed": feed, "block": blk}, live_only=True)
    if reason:
        return [f"Explanation skipped: {reason}."]
    return ["Explanation", text]
