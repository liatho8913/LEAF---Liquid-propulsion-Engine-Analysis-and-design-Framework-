from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PASS_BANNER = "PASS_PHASE_16U5_SOLVER_STATUS_ACCESS_WRAPPERS"

FILES = [
    Path("leaf_qt/structured_status_access.py"),
    Path("leaf_qt/solver_status_access.py"),
    Path("project_maintenance/test_solver_status_access_phase_16u5.py"),
]


def run_completion() -> dict:
    missing = [str(path) for path in FILES if not path.exists()]

    test = subprocess.run(
        [sys.executable, "project_maintenance/test_solver_status_access_phase_16u5.py"],
        text=True,
        capture_output=True,
    )

    passed = not missing and test.returncode == 0 and PASS_BANNER in test.stdout

    return {
        "phase": "16U.5",
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U5_SOLVER_STATUS_ACCESS_WRAPPERS",
        "missing": missing,
        "test_returncode": test.returncode,
        "test_stdout": test.stdout.strip(),
        "test_stderr": test.stderr.strip(),
        "phase_16u5_solver_status_access_wrappers_complete": passed,
    }


if __name__ == "__main__":
    result = run_completion()
    print(result["status"])
    if result["test_stdout"]:
        print(result["test_stdout"])
    if result["test_stderr"]:
        print(result["test_stderr"])
    if result["missing"]:
        print("missing=", result["missing"])
    if not result["phase_16u5_solver_status_access_wrappers_complete"]:
        raise SystemExit(1)
