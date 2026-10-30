from __future__ import annotations

from pathlib import Path
import ast
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"

PROTECTED = {
    "leaf_qt/module_engine/module_definition.py",
    "leaf_qt/module_engine/module_discovery_engine.py",
    "leaf_qt/module_engine/module_contract.py",
    "leaf_qt/module_engine/module_contract_builder.py",
    "leaf_qt/module_engine/module_verification.py",
    "leaf_qt/module_engine/module_verification_builder.py",
    "leaf_qt/module_engine/module_runtime_manifest.py",
    "leaf_qt/module_engine/module_runtime_integrator.py",
    "leaf_qt/module_engine/module_migration.py",
    "leaf_qt/module_engine/nozzle_migration_adapter.py",
    "leaf_qt/module_engine/nozzle_behaviour_preservation.py",
    "leaf_qt/module_engine/nozzle_capability_discovery.py",
    "leaf_qt/module_engine/nozzle_legacy_reference_audit.py",
}

ONE_OFF_PATTERNS = (
    "phase_31",
    "phase_32",
)

KEEP_PATTERNS = (
    "completion_gate",
    "programme_32_completion_gate",
)


def imports_in_file(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return set()

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    return imports


def module_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    python_files = sorted(
        path for path in ROOT.rglob("*.py")
        if ".venv" not in path.parts
        and "__pycache__" not in path.parts
        and ".git" not in path.parts
    )

    module_imports = {
        module_name(path): imports_in_file(path)
        for path in python_files
    }

    imported_modules = set().union(*module_imports.values()) if module_imports else set()

    candidates = []

    for path in python_files:
        rel = path.relative_to(ROOT).as_posix()
        name = path.name.lower()

        if rel in PROTECTED:
            continue

        if not rel.startswith("project_maintenance/modular_engine_architecture/"):
            continue

        if not any(pattern in name for pattern in ONE_OFF_PATTERNS):
            continue

        if any(pattern in name for pattern in KEEP_PATTERNS):
            keep_reason = "completion gate retained as programme evidence"
        else:
            keep_reason = ""

        mod = module_name(path)
        imported = mod in imported_modules

        candidates.append({
            "path": rel,
            "module": mod,
            "imported_elsewhere": imported,
            "recommended_action": "KEEP" if imported or keep_reason else "DELETE_AFTER_ARCHIVE",
            "reason": keep_reason or (
                "imported elsewhere" if imported else "one-off phase script; report already preserves evidence"
            ),
        })

    delete_after_archive = [
        item for item in candidates
        if item["recommended_action"] == "DELETE_AFTER_ARCHIVE"
    ]

    keep = [
        item for item in candidates
        if item["recommended_action"] == "KEEP"
    ]

    result = {
        "schema": "LEAF_CONTROLLED_LEGACY_REDUCTION_PLANNING_PHASE_33B_V1",
        "programme": "Programme 33",
        "phase": "33B",
        "purpose": "Controlled simplification planning only.",
        "python_files_scanned": len(python_files),
        "protected_files": sorted(PROTECTED),
        "candidate_count": len(candidates),
        "delete_after_archive_count": len(delete_after_archive),
        "keep_count": len(keep),
        "candidates": candidates,
        "execution_performed": False,
        "files_deleted": [],
        "engineering_behaviour_changed": False,
        "completion_notice": "PHASE_33B_CONTROLLED_LEGACY_REDUCTION_PLANNING_COMPLETE",
        "next_phase": "33C — Controlled Legacy Reduction Execution",
    }

    json_path = REPORT_DIR / "phase_33b_controlled_legacy_reduction_planning.json"
    txt_path = REPORT_DIR / "phase_33b_controlled_legacy_reduction_planning.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF Programme 33B — Controlled Legacy Reduction Planning",
        "=" * 68,
        "",
        f"python_files_scanned={len(python_files)}",
        f"candidate_count={len(candidates)}",
        f"delete_after_archive_count={len(delete_after_archive)}",
        f"keep_count={len(keep)}",
        "execution_performed=False",
        "files_deleted=0",
        "engineering_behaviour_changed=False",
        "",
        "DELETE_AFTER_ARCHIVE candidates:",
    ]

    for item in delete_after_archive:
        lines.append(f"- {item['path']}")

    lines.extend([
        "",
        "KEEP candidates:",
    ])

    for item in keep:
        lines.append(f"- {item['path']} | reason={item['reason']}")

    lines.extend([
        "",
        "Protected active infrastructure:",
    ])

    for path in sorted(PROTECTED):
        lines.append(f"- {path}")

    lines.extend([
        "",
        "completion_notice=PHASE_33B_CONTROLLED_LEGACY_REDUCTION_PLANNING_COMPLETE",
        "next_phase=33C — Controlled Legacy Reduction Execution",
    ])

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PASS_PHASE_33B_CONTROLLED_LEGACY_REDUCTION_PLANNING")
    print(f"python_files_scanned={len(python_files)}")
    print(f"candidate_count={len(candidates)}")
    print(f"delete_after_archive_count={len(delete_after_archive)}")
    print(f"keep_count={len(keep)}")
    print("execution_performed=False")
    print("files_deleted=0")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_33B_CONTROLLED_LEGACY_REDUCTION_PLANNING_COMPLETE")
    print("next_phase=33C — Controlled Legacy Reduction Execution")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
