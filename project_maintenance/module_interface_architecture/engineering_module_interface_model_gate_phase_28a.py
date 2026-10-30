"""
Programme 28A Completion Gate.

Validates the Engineering Module Interface Model.
"""

from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPORT_DIR = ROOT / "LEAF_Reports" / "module_interface_architecture"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

from leaf_qt.module_interface.interface_model import (
    EngineeringModuleCapability,
    EngineeringModuleDependency,
    EngineeringModuleInterfaceStatus,
    EngineeringModuleSurface,
    build_engineering_module_interface,
)


def main() -> None:
    for rel in [
        "leaf_qt/module_interface/__init__.py",
        "leaf_qt/module_interface/interface_model.py",
    ]:
        py_compile.compile(str(ROOT / rel), doraise=True)

    interface = build_engineering_module_interface(
        module_id="regen_demonstration_module",
        title="Regenerative Cooling Demonstration Module Interface",
        status=EngineeringModuleInterfaceStatus.READY,
        dependencies=(
            EngineeringModuleDependency(
                dependency_id="platform_services",
                provides=("regen.workflow", "regen.report", "regen.validation"),
                requires=("workflow.platform", "runtime.platform", "storage.platform"),
                optional=("notification.platform",),
                reason="Regen demonstration module must integrate with completed platform services.",
            ),
        ),
        metadata={"gate": "28A"},
    )

    report = interface.report()
    failures = list(report["validation_failures"])

    expected_surfaces = sorted(surface.value for surface in EngineeringModuleSurface)
    if report["surfaces"] != expected_surfaces:
        failures.append(f"surface coverage mismatch: expected={expected_surfaces}, actual={report['surfaces']}")

    if report["missing_required_surfaces"]:
        failures.append(f"missing surfaces: {report['missing_required_surfaces']}")

    if report["capability_count"] != 9:
        failures.append(f"expected capability_count=9, actual={report['capability_count']}")

    if report["dependency_report"]["dependency_count"] != 1:
        failures.append("expected one dependency declaration")

    partial = build_engineering_module_interface(
        module_id="partial_module",
        title="Partial Module",
        capabilities=(
            EngineeringModuleCapability(
                surface=EngineeringModuleSurface.MODEL,
                capability_id="only_model",
                title="Only Model",
                description="Intentional partial interface for gate validation.",
            ),
        ),
    )

    partial_failures = partial.validate()
    if not any("missing required module surfaces" in failure for failure in partial_failures):
        failures.append("partial interface did not report missing required surfaces")

    bad_dependency = EngineeringModuleDependency(
        dependency_id="bad_dependency",
        provides=("a",),
        requires=("shared",),
        optional=("shared",),
        reason="Overlap test.",
    )

    if not any("overlapping" in failure for failure in bad_dependency.validate()):
        failures.append("dependency overlap validation did not trigger")

    report["gate"] = {
        "phase": "28A",
        "programme": "28",
        "passed": not failures,
        "failures": failures,
        "completion_notice": (
            "PROGRAMME_28A_ENGINEERING_MODULE_INTERFACE_MODEL_COMPLETE"
            if not failures
            else "PROGRAMME_28A_ENGINEERING_MODULE_INTERFACE_MODEL_FAILED"
        ),
        "next_phase": "28B Engineering Module Registry",
    }

    txt_path = REPORT_DIR / "engineering_module_interface_model_gate_phase_28a.txt"
    json_path = REPORT_DIR / "engineering_module_interface_model_gate_phase_28a.json"

    txt_path.write_text(
        "\n".join(
            [
                "LEAF Programme 28A Engineering Module Interface Model Gate",
                "=========================================================",
                f"passed={not failures}",
                f"module_id={report['module_id']}",
                f"status={report['status']}",
                f"surface_count={report['surface_count']}",
                f"surfaces={','.join(report['surfaces'])}",
                f"capability_count={report['capability_count']}",
                f"dependency_count={report['dependency_report']['dependency_count']}",
                f"missing_required_surfaces={len(report['missing_required_surfaces'])}",
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
        print("FAIL_PHASE_28A_ENGINEERING_MODULE_INTERFACE_MODEL")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_28A_ENGINEERING_MODULE_INTERFACE_MODEL")
    print("schema=LEAF_ENGINEERING_MODULE_INTERFACE_MODEL_PHASE_28A_V1")
    print(f"module_id={report['module_id']}")
    print(f"status={report['status']}")
    print(f"surface_count={report['surface_count']}")
    print(f"surfaces={','.join(report['surfaces'])}")
    print(f"capability_count={report['capability_count']}")
    print(f"dependency_count={report['dependency_report']['dependency_count']}")
    print(f"missing_required_surfaces={len(report['missing_required_surfaces'])}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PROGRAMME_28A_ENGINEERING_MODULE_INTERFACE_MODEL_COMPLETE")
    print("next_phase=28B Engineering Module Registry")


if __name__ == "__main__":
    main()
