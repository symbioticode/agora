import os
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def test_api_connectivity_script_refuses_without_explicit_opt_in():
    environment = os.environ.copy()
    environment.pop("RUN_API", None)
    result = subprocess.run(
        [sys.executable, "test_api_keys.py"],
        cwd=REPO,
        env=environment,
        text=True,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "RUN_API=1" in result.stderr
