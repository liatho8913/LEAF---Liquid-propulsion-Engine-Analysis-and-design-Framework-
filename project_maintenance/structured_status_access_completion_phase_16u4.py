from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PASS_BANNER = "PASS_PHASE_16U4_STRUCTURED_STATUS_ACCESS_LAYER"

FILES = [
    Path("leaf_qt/structured_status_access.py"),
    Path("project_maintenance/test_structured_status_access_phase_16u4.py"),
]


def run_completion() -> dict:
    missing = [str(path) for path in FILES if not path.exists()]
    test = subprocess.run(
        [sys.executable, "project_maintenance/test_structured_status_access_phase_16u4.py"],
        text=True,
        capture_output=True,
    )

    passed = not missing and test.returncode == 0 and PASS_BANNER in test.stdout

    return {
        "phase": "16U.4",
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U4_STRUCTURED_STATUS_ACCESS_LAYER",
        "missing": missing,
        "test_returncode": test.returncode,
        "test_stdout": test.stdout.strip(),
        "test_stderr": test.stderr.strip(),
        "phase_16u4_structured_status_access_layer_complete": passed,
    }


if __name__ == "__main__":
    result = run_completion()
    print(result["status"])
    if result["missing"]:
        print("missing=", result["missing"])
    if result["test_stdout"]:
        print(result["test_stdout"])
    if result["test_stderr"]:
        print(result["test_stderr"])
    if not result["phase_16u4_structured_status_access_layer_complete"]:
        raise SystemExit(1)
