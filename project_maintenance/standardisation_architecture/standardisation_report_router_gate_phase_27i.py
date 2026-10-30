"""
Programme 27I Completion Gate.

Validates the Standardisation Report Router.
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

from leaf_qt.standardisation.report_router import build_standardisation_report_router


def main() -> None:
    for rel in [
        "leaf_qt/standardisation/__init__.py",
        "leaf_qt/standardisation/inventory_model.py",
        "leaf_qt/standardisation/rule_registry.py",
        "leaf_qt/standardisation/scanner.py",
        "leaf_qt/standardisation/finding_report_owner.py",
        "leaf_qt/standardisation/compliance_classifier.py",
        "leaf_qt/standardisation/repair_plan_owner.py",
        "leaf_qt/standardisation/safety_gate.py",
        "leaf_qt/standardisation/dry_run_executor.py",
        "leaf_qt/standardisation/report_router.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    router = build_standardisation_report_router(ROOT)

    routed = router.route_report(
        report_id="standardisation_report_router_gate_phase_27i_routed_probe",
        title="LEAF Programme 27I Routed Probe",
        payload={
            "phase": "27I",
            "programme": "27",
            "purpose": "report_router_gate_probe",
            "expected_mutation_scope": "LEAF_Reports_only",
        },
    )

    routed_report = routed.as_dict()
    router_report = router.report()
    failures = []

    txt_path = ROOT / routed.txt_path
    json_path = ROOT / routed.json_path

    if routed_report["schema"] != "LEAF_STANDARDISATION_REPORT_ROUTER_PHASE_27I_V1":
        failures.append(f"schema mismatch: actual={routed_report['schema']}")

    if not txt_path.exists():
        failures.append(f"routed txt report missing: {routed.txt_path}")

    if not json_path.exists():
        failures.append(f"routed json report missing: {routed.json_path}")

    if not str(routed.txt_path).startswith("LEAF_Reports/standardisation_architecture/"):
        failures.append(f"txt path routed outside standardisation reports: {routed.txt_path}")

    if not str(routed.json_path).startswith("LEAF_Reports/standardisation_architecture/"):
        failures.append(f"json path routed outside standardisation reports: {routed.json_path}")

    if routed_report["mutation_scope"] != "LEAF_Reports_only":
        failures.append(f"mutation scope mismatch: {routed_report['mutation_scope']}")

    if routed_report["mutation_performed"] is not False:
        failures.append("report router must not report mutation_performed true")

    if router_report["deletion_performed"] is not False:
        failures.append("report router must not delete files")

    if router_report["archive_performed"] is not False:
        failures.append("report router must not archive files")

    if json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if payload.get("router", {}).get("mutation_performed") is not False:
            failures.append("routed JSON payload mutation flag invalid")
        if payload.get("router", {}).get("deletion_performed") is not False:
            failures.append("routed JSON payload deletion flag invalid")
        if payload.get("router", {}).get("archive_performed") is not False:
            failures.append("routed JSON payload archive flag invalid")

    final_report = {
        "schema": "LEAF_STANDARDISATION_REPORT_ROUTER_COMPLETION_PHASE_27I_V1",
        "routed_report": routed_report,
        "router_report": router_report,
        "gate": {
            "phase": "27I",
            "programme": "27",
            "passed": not failures,
            "failures": failures,
            "completion_notice": (
                "PROGRAMME_27I_STANDARDISATION_REPORT_ROUTER_COMPLETE"
                if not failures
                else "PROGRAMME_27I_STANDARDISATION_REPORT_ROUTER_FAILED"
            ),
            "next_phase": "27J Programme Completion Gate",
        },
    }

    gate_txt = REPORT_DIR / "standardisation_report_router_gate_phase_27i.txt"
    gate_json = REPORT_DIR / "standardisation_report_router_gate_phase_27i.json"

    gate_txt.write_text(
        "\n".join(
            [
                "LEAF Programme 27I Standardisation Report Router Gate",
                "====================================================",
                f"passed={not failures}",
                f"report_id={routed_report['report_id']}",
                f"txt_path={routed_report['txt_path']}",
                f"json_path={routed_report['json_path']}",
                f"report_dir={routed_report['report_dir']}",
                f"mutation_scope={routed_report['mutation_scope']}",
                f"mutation_performed={routed_report['mutation_performed']}",
                f"deletion_performed={router_report['deletion_performed']}",
                f"archive_performed={router_report['archive_performed']}",
                f"failures={len(failures)}",
                f"completion_notice={final_report['gate']['completion_notice']}",
                f"next_phase={final_report['gate']['next_phase']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    gate_json.write_text(json.dumps(final_report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_27I_STANDARDISATION_REPORT_ROUTER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={gate_txt.relative_to(ROOT)}")
        print(f"json={gate_json.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27I_STANDARDISATION_REPORT_ROUTER")
    print("schema=LEAF_STANDARDISATION_REPORT_ROUTER_PHASE_27I_V1")
    print(f"report_id={routed_report['report_id']}")
    print(f"txt_path={routed_report['txt_path']}")
    print(f"json_path={routed_report['json_path']}")
    print(f"report_dir={routed_report['report_dir']}")
    print(f"mutation_scope={routed_report['mutation_scope']}")
    print(f"mutation_performed={routed_report['mutation_performed']}")
    print(f"deletion_performed={router_report['deletion_performed']}")
    print(f"archive_performed={router_report['archive_performed']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27I_STANDARDISATION_REPORT_ROUTER_COMPLETE")
    print("next_phase=27J Programme Completion Gate")


if __name__ == "__main__":
    main()
