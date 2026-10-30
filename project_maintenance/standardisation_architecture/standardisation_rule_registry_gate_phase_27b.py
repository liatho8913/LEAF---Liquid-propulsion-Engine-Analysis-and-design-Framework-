"""
Programme 27B Completion Gate.

Validates the Standardisation Rule Registry.
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

from leaf_qt.standardisation.inventory_model import StandardisationArea
from leaf_qt.standardisation.rule_registry import (
    StandardisationRule,
    StandardisationRuleRegistry,
    StandardisationRuleSeverity,
    build_default_standardisation_rule_registry,
)


def main() -> None:
    for rel in [
        "leaf_qt/standardisation/__init__.py",
        "leaf_qt/standardisation/inventory_model.py",
        "leaf_qt/standardisation/rule_registry.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    registry = build_default_standardisation_rule_registry()
    report = registry.report()
    failures = list(report["validation_failures"])

    expected_areas = {area.value for area in StandardisationArea}
    actual_areas = {area for area, count in report["area_counts"].items() if count > 0}

    if actual_areas != expected_areas:
        failures.append(
            f"area coverage mismatch: expected={sorted(expected_areas)}, actual={sorted(actual_areas)}"
        )

    if report["rule_count"] != 9:
        failures.append(f"expected rule_count=9, actual={report['rule_count']}")

    if report["severity_counts"]["BLOCKING"] < 4:
        failures.append("expected at least four BLOCKING standardisation rules")

    duplicate_rejected = False
    try:
        registry.register(
            StandardisationRule(
                rule_id="schema_has_named_version",
                area=StandardisationArea.SCHEMA,
                title="Duplicate",
                description="Duplicate rule test.",
            )
        )
    except ValueError:
        duplicate_rejected = True

    if not duplicate_rejected:
        failures.append("duplicate rule registration was not rejected")

    incomplete_registry = StandardisationRuleRegistry("incomplete_test")
    incomplete_registry.register(
        StandardisationRule(
            rule_id="only_schema",
            area=StandardisationArea.SCHEMA,
            title="Only Schema",
            description="Coverage failure test.",
        )
    )

    incomplete_failures = incomplete_registry.validate()
    if not any("missing areas" in failure for failure in incomplete_failures):
        failures.append("incomplete registry did not report missing area coverage")

    report["gate"] = {
        "phase": "27B",
        "programme": "27",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_27B_STANDARDISATION_RULE_REGISTRY_COMPLETE"
            if not failures
            else "PROGRAMME_27B_STANDARDISATION_RULE_REGISTRY_FAILED"
        ),
        "next_phase": "27C Standardisation Scanner",
    }

    txt_path = REPORT_DIR / "standardisation_rule_registry_gate_phase_27b.txt"
    json_path = REPORT_DIR / "standardisation_rule_registry_gate_phase_27b.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27B Standardisation Rule Registry Gate",
                "====================================================",
                f"passed={not failures}",
                f"registry_id={report['registry_id']}",
                f"rule_count={report['rule_count']}",
                f"areas={','.join(sorted(actual_areas))}",
                f"blocking_rules={report['severity_counts']['BLOCKING']}",
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
        print("FAIL_PHASE_27B_STANDARDISATION_RULE_REGISTRY")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27B_STANDARDISATION_RULE_REGISTRY")
    print("schema=LEAF_STANDARDISATION_RULE_REGISTRY_PHASE_27B_V1")
    print(f"registry_id={report['registry_id']}")
    print(f"rule_count={report['rule_count']}")
    print(f"areas={','.join(sorted(actual_areas))}")
    print(f"blocking_rules={report['severity_counts']['BLOCKING']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27B_STANDARDISATION_RULE_REGISTRY_COMPLETE")
    print("next_phase=27C Standardisation Scanner")


if __name__ == "__main__":
    main()
