"""
Programme 27A Completion Gate.

Validates the Standardisation Inventory Model.
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

from leaf_qt.standardisation.inventory_model import (
    StandardisationArea,
    build_standardisation_inventory_model,
)


def main() -> None:
    for rel in [
        "leaf_qt/standardisation/__init__.py",
        "leaf_qt/standardisation/inventory_model.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    model = build_standardisation_inventory_model()
    report = model.report()
    failures = list(report["validation_failures"])

    expected_areas = {area.value for area in StandardisationArea}
    actual_areas = {
        area for area, count in report["area_counts"].items() if count > 0
    }

    if actual_areas != expected_areas:
        failures.append(f"area coverage mismatch: expected={sorted(expected_areas)}, actual={sorted(actual_areas)}")

    if report["item_count"] != 9:
        failures.append(f"expected item_count=9, actual={report['item_count']}")

    report["gate"] = {
        "phase": "27A",
        "programme": "27",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_27A_STANDARDISATION_INVENTORY_MODEL_COMPLETE"
            if not failures
            else "PROGRAMME_27A_STANDARDISATION_INVENTORY_MODEL_FAILED"
        ),
        "next_phase": "27B Standardisation Rule Registry",
    }

    txt_path = REPORT_DIR / "standardisation_inventory_model_gate_phase_27a.txt"
    json_path = REPORT_DIR / "standardisation_inventory_model_gate_phase_27a.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 27A Standardisation Inventory Model Gate",
                "======================================================",
                f"passed={not failures}",
                f"inventory_id={report['inventory_id']}",
                f"item_count={report['item_count']}",
                f"areas={','.join(sorted(actual_areas))}",
                f"failures={len(failures)}",
                f"completion_notice={report['gate']['completion_notice']}",
                f"next_phase={report['gate']['next_phase']}",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if failures:
        print("FAIL_PHASE_27A_STANDARDISATION_INVENTORY_MODEL")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_27A_STANDARDISATION_INVENTORY_MODEL")
    print("schema=LEAF_STANDARDISATION_INVENTORY_MODEL_PHASE_27A_V1")
    print(f"inventory_id={report['inventory_id']}")
    print(f"item_count={report['item_count']}")
    print(f"areas={','.join(sorted(actual_areas))}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_27A_STANDARDISATION_INVENTORY_MODEL_COMPLETE")
    print("next_phase=27B Standardisation Rule Registry")


if __name__ == "__main__":
    main()
