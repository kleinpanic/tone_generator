import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(
    os.path.exists("/usr/local/bin/tone_generator"),
    reason="a system-wide install exists on this machine; the script would remove it",
)


def _copy_build_dir(tmp_path):
    shutil.copytree(REPO_ROOT / "build", tmp_path / "build")
    return tmp_path / "build" / "uninstall.sh"


def test_local_uninstall_succeeds(tmp_path):
    # Previously the script removed the local venv and then exited 1 with
    # "No installation detected" because no system-wide install existed.
    script = _copy_build_dir(tmp_path)
    (tmp_path / "venv").mkdir()
    result = subprocess.run(["bash", str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / "venv").exists()


def test_nothing_installed_reports_and_fails(tmp_path):
    script = _copy_build_dir(tmp_path)
    result = subprocess.run(["bash", str(script)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "No installation detected" in result.stdout
    assert "Starting local uninstallation" not in result.stdout
