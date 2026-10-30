"""
Programme 27C Completion Gate.

Validates the read-only Standardisation Scanner.
"""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "standardisation_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

from leaf_qt.standardisation.scanner import build_standardisation_scanner


def main() -> None:
    for rel in [
        "leaf_qt/standardisation/__init__.py",
        "leaf_qt/standardisation/inventory_model.py",
        "leaf_qt/standardisation/rule_registry.py",
        "leaf_qt/standardisation/scanner.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    scanner = build_standardisation_scanner(ROOT)
    result = scanner.scan()
    report = result.as_dict()

    failures = []

    if report["schema"] != "LEAF_STANDARDISATION_SCANNER_PHASE_27C_V1":
        failures.append(f"schema mismatch: actual={report['schema']}")

    if report["mutation_performed"] is not False:
        failures.append("standardisation scanner must not mutate the repository")

    if report["scanned_python_files"] <= 0:
        failures.append("scanner did not scan any Python files")

    required_paths = [
        "leaf_qt/workflow",
        "leaf_qt/standardisation",
        "LEAF_Reports",
    ]

    for rel in required_paths:
        if not (ROOT / rel).exists():
            failures.append(f"required path missing before scanner sign-off: {rel}")

    finding_counts = report["finding_counts"]

    report["gate"] = {
        "phase": "27C",
        "programme": "27",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_27C_STANDARDISATION_SCANNER_COMPLETE"
            if not failures
            else "PROGRAMME_27C_STANDARDISATION_SCANNER_FAILED"
        ),
        "next_phase": "27D Standardisation Finding Report Owner",
    }

    txt_path = REPORT_DIR / "standardisation_scanner_gate_phase_27c.txt"
    json_path = REPORT_DIR / "standardisation_scanner_gate_phase_27c.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27C Standardisation Scanner Gate",
                "==============================================",
                f"passed={not failures}",
                f"root={report['root']}",
                f"scanned_python_files={report['scanned_python_files']}",
                f"scanned_report_files={report['scanned_report_files']}",
                f"info_findings={finding_counts['INFO']}",
                f"warning_findings={finding_counts['WARNING']}",
                f"error_findings={finding_counts['ERROR']}",
                f"mutation_performed={report['mutation_performed']}",
                f"failures={len(failures)}",
                f"completion_notice={report['gate']['completion_notice']}",
                f"next_phase={report['gate']['next_phase']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_27C_STANDARDISATION_SCANNER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27C_STANDARDISATION_SCANNER")
    print("schema=LEAF_STANDARDISATION_SCANNER_PHASE_27C_V1")
    print(f"scanned_python_files={report['scanned_python_files']}")
    print(f"scanned_report_files={report['scanned_report_files']}")
    print(f"info_findings={finding_counts['INFO']}")
    print(f"warning_findings={finding_counts['WARNING']}")
    print(f"error_findings={finding_counts['ERROR']}")
    print(f"mutation_performed={report['mutation_performed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27C_STANDARDISATION_SCANNER_COMPLETE")
    print("next_phase=27D Standardisation Finding Report Owner")


if __name__ == "__main__":
    main()
