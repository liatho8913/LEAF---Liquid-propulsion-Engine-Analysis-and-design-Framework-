from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_architecture_completion_phase_17k import (
    SCHEMA,
    build_repository_architecture_completion_certificate,
)
from project_maintenance.repository_architecture.roadmap_status_artifact_owner import RoadmapStatusArtifactOwner

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17k"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_completion_phase_17k.py",
    ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_completion_gate_phase_17k.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    certificate = build_repository_architecture_completion_certificate(ROOT)
    failures.extend(certificate.get("failures", []))

    summary = certificate.get("summary", {})

    if certificate.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if certificate.get("programme_completed") is not True:
        failures.append("programme_not_completed")

    if summary.get("artifacts_present") != summary.get("artifacts_required"):
        failures.append("required_artifacts_missing")

    if summary.get("schemas_valid") != summary.get("artifacts_required"):
        failures.append("required_artifact_schemas_invalid")

    if summary.get("health_status") != "PASS":
        failures.append("repository_health_not_pass")

    if summary.get("ready_for_next_programme") is not True:
        failures.append("not_ready_for_next_programme")

    cert_path = OUT / "repository_architecture_completion_certificate_phase_17k.json"
    gate_json = OUT / "repository_architecture_completion_gate_phase_17k.json"
    gate_txt = OUT / "repository_architecture_completion_gate_phase_17k.txt"

    certificate["passed"] = not failures
    certificate["failures"] = failures
    certificate["completion_notice"] = (
        "PHASE_17K_COMPLETE_REPOSITORY_ARCHITECTURE_PROGRAMME_SIGNED_OFF"
        if not failures else
        "PHASE_17K_BLOCKED"
    )

    cert_path.write_text(json.dumps(certificate, indent=2), encoding="utf-8")

    roadmap_paths = {"json": "", "report": ""}

    if not failures:
        owner = RoadmapStatusArtifactOwner(ROOT)
        roadmap_status = owner.build_status(
            current_major_feature="Repository Architecture Completion",
            current_phase="17K",
            previous_completed_feature="17J Repository Health Monitor",
            current_goal="Close out the repository architecture programme and hand over to Workspace Architecture and the user-facing resource system.",
            completed=certificate["repository_architecture_completed_phases"],
            active_constraints=[
                "No automatic delete, archive, or relocation execution.",
                "Repository architecture is now a foundation layer, not the user-facing product.",
                "Developer-facing infrastructure and user-facing assets remain separate architecture domains.",
                "User-facing resources require obvious canonical homes near the project root.",
                "Future workspace development must build on the repository ownership graph, universal index, semantic graph, relocation dry-run plan, and health monitor.",
            ],
            remaining_work=[
                "18A User Resource Canonical Folder System",
                "18B Workspace Resource Registry",
                "18C Project/Design/Report/Export Ownership Layer",
                "18D Workspace Navigation Model",
                "18E Workspace Architecture Completion",
            ],
            next_phase="18A_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM",
            safety_locks=certificate["safety_locks"],
            metrics={
                "artifacts_required": summary.get("artifacts_required", 0),
                "artifacts_present": summary.get("artifacts_present", 0),
                "schemas_valid": summary.get("schemas_valid", 0),
                "health_score": summary.get("health_score", 0),
                "health_status": summary.get("health_status", "UNKNOWN"),
                "programme_completed": summary.get("programme_completed", False),
            },
        )
        roadmap_paths = owner.write_status(roadmap_status)

    result = {
        "phase": "17K",
        "feature": "REPOSITORY_ARCHITECTURE_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": certificate.get("schema"),
        "summary": summary,
        "failures": failures,
        "completion_notice": certificate["completion_notice"],
        "certificate_json": cert_path.relative_to(ROOT).as_posix(),
        "roadmap_json": roadmap_paths["json"],
        "roadmap_report": roadmap_paths["report"],
        "next_phase": "18A_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 17K REPOSITORY ARCHITECTURE COMPLETION",
        "===================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme_completed={summary.get('programme_completed')}",
        f"artifacts_required={summary.get('artifacts_required')}",
        f"artifacts_present={summary.get('artifacts_present')}",
        f"schemas_valid={summary.get('schemas_valid')}",
        f"health_score={summary.get('health_score')}",
        f"health_status={summary.get('health_status')}",
        f"ready_for_next_programme={summary.get('ready_for_next_programme')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"certificate_json={result['certificate_json']}",
        f"roadmap_json={result['roadmap_json']}",
        f"roadmap_report={result['roadmap_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_17K_REPOSITORY_ARCHITECTURE_COMPLETION" if result["passed"] else "FAIL_PHASE_17K_REPOSITORY_ARCHITECTURE_COMPLETION")
    print(f"schema={result['schema']}")
    print(f"programme_completed={summary.get('programme_completed')}")
    print(f"artifacts_required={summary.get('artifacts_required')}")
    print(f"artifacts_present={summary.get('artifacts_present')}")
    print(f"schemas_valid={summary.get('schemas_valid')}")
    print(f"health_score={summary.get('health_score')}")
    print(f"health_status={summary.get('health_status')}")
    print(f"ready_for_next_programme={summary.get('ready_for_next_programme')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"certificate_json={result['certificate_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"roadmap_report={result['roadmap_report']}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
