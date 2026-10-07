import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="brief.cmd is Windows only")


def test_python_failure_stops_before_npm(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    marker = tmp_path / "npm-started"
    (bin_dir / "npm.cmd").write_text(f'@echo started> "{marker}"\r\n')
    empty = tmp_path / "snap"
    shutil.copytree(ROOT / "tests" / "data" / "snapshot", empty)
    (empty / "fixtures.json").unlink()
    env = dict(os.environ, PATH=f"{bin_dir};{os.environ['PATH']}", BRIEF_NO_PAUSE="1")
    r = subprocess.run(
        ["cmd", "/c", str(ROOT / "brief.cmd"), "--from", str(empty)],
        cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode != 0
    assert "Missing file: fixtures.json" in r.stdout
    assert not marker.exists()
