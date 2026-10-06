from types import SimpleNamespace

from fpl.eval import __main__ as cli, report
from tests.evalfeed import make_eval, write_folder


def run(tmp_path, capsys, data=None, **kw):
    folder = write_folder(data or make_eval(), tmp_path / "f")
    for name in kw.get("remove", []):
        (folder / name).unlink()
    code = cli.main(["--from", str(folder)], results=tmp_path / "results")
    return code, capsys.readouterr().out, folder


def test_from_prints_header_and_saves(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(report, "commit", lambda: "abc1234")
    code, out, folder = run(tmp_path, capsys)
    assert code == 0
    assert "Gameweeks: 2-5 (4 of 5 finished; GW1 skipped)" in out
    assert f"Folder: {folder}" in out and "Commit: abc1234" in out
    assert "Few gameweeks: small differences are likely noise." in out
    assert "Injury news is not replayed, so 'mine' has an advantage the formulas don't." in out
    assert "captain current  captain shrink  captain mine  captain best" in out
    saved = list((tmp_path / "results").glob("*-abc1234.txt"))
    assert len(saved) == 1
    text = saved[0].read_text(encoding="utf-8")
    assert text.strip() in out and text.rstrip().splitlines()[-1].startswith("Total")


def test_commit_dirty_and_unknown(monkeypatch):
    def fake(args, **kw):
        return SimpleNamespace(returncode=1 if "diff" in args else 0, stdout="abc1234\n")

    monkeypatch.setattr(report.subprocess, "run", fake)
    assert report.commit() == "abc1234-dirty"

    def gone(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(report.subprocess, "run", gone)
    assert report.commit() == "unknown"


def test_same_name_is_overwritten(tmp_path):
    report.save("one", "abc", tmp_path)
    p = report.save("two", "abc-dirty", tmp_path)
    q = report.save("three", "abc", tmp_path)
    assert p.name.endswith("-abc-dirty.txt") and q.read_text() == "three\n"
    assert len(list(tmp_path.iterdir())) == 2


def test_missing_live_file_named(tmp_path, capsys):
    code, out, _ = run(tmp_path, capsys, remove=["live-gw03.json"])
    assert code == 1 and "Missing file: live-gw03.json" in out


def test_no_finished_gameweeks(tmp_path, capsys):
    code, out, _ = run(tmp_path, capsys, make_eval(gws=0))
    assert code == 0 and "No finished gameweeks to replay." in out


def test_no_picks_for_a_gameweek_is_skipped_and_said(tmp_path, capsys):
    code, out, _ = run(tmp_path, capsys, remove=["picks-gw03.json"])
    assert code == 0
    assert "GW3 no picks" in out and "Gameweeks: 2,4,5 (3 of 5 finished" in out
