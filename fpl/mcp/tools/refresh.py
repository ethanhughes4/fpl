from fpl.mcp import session

DESCRIPTION = (
    "Download the latest FPL data into a new folder and say when and for which gameweek. "
    "Use only when asked for fresh data. Takes no arguments."
)


def tool() -> str:
    def body(feed):
        if session.fixed():
            return "Serving a saved folder; nothing downloaded."
        return f"Downloaded to data/raw/{session.folder_name()}."
    return session.reply(body, fresh=True)
