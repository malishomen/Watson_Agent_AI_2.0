from __future__ import annotations

import subprocess
from pathlib import Path


def run_tests(repo_root: str, test_cmd: str) -> tuple[bool, str]:
    repo = Path(repo_root)
    # Set PYTEST_DISABLE_PLUGIN_AUTOLOAD for stability
    import os
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    p = subprocess.run(test_cmd, shell=True, cwd=str(repo), capture_output=True, text=True, encoding="utf-8", env=env)
    out = (p.stdout or "") + (p.stderr or "")
    return (p.returncode == 0, out)


