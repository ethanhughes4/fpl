from fpl import download as dl
from fpl.mcp import session
from fpl.mcp.tools import get_brief, refresh
from tests.test_mcp_session import NOW, SNAP, Fake, raw  # noqa: F401


def test_two_refreshes_make_two_folders_and_brief_uses_newest(raw):
    fake = Fake()
    session.start(download=fake, now=NOW)
    a = refresh.tool()
    b = refresh.tool()
    assert "Downloaded to data/raw/2026-10-06-gw06." in a
    assert "Downloaded to data/raw/2026-10-06-gw06-2." in b
    assert sorted(p.name for p in raw.iterdir()) == ["2026-10-06-gw06", "2026-10-06-gw06-2"]
    get_brief.tool()
    assert len(fake.calls) == 2 and session.folder_name() == "2026-10-06-gw06-2"


def test_feed_down_keeps_old_folder(raw):
    session.start(download=Fake(), now=NOW)
    refresh.tool()
    session.start(download=Fake(), now=NOW)
    get_brief.tool()
    session._s["download"] = Fake(dl.FeedError(503))
    assert refresh.tool() == "Could not reach FPL (HTTP 503). Try again later or use --from <folder>"
    assert session.folder_name() == "2026-10-06-gw06"
    assert get_brief.tool().startswith("Data downloaded ")


def test_from_never_downloads(raw):
    fake = Fake()
    session.start(SNAP, download=fake, now=NOW)
    out = refresh.tool()
    assert out.startswith("Data downloaded ") and out.endswith("Serving a saved folder; nothing downloaded.")
    assert fake.calls == [] and session.folder_name() == SNAP.name
