from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE = "16T.2N"

PASS_STATUS = "PASS_TEST_FILE_CLEANLINESS_PLAN_PHASE_16T2N"
WARN_STATUS = "WARN_TEST_FILE_CLEANLINESS_PLAN_PHASE_16T2N"
FAIL_STATUS = "FAIL_TEST_FILE_CLEANLINESS_PLAN_PHASE_16T2N"

ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
PLAN_DIR = ROOT / "_leaf_artifacts" / "allowlists"

KEEP_REGRESSION_TEST = "KEEP_REGRESSION_TEST"
MOVE_TO_VERIFICATION = "MOVE_TO_VERIFICATION"
GENERATED_SAMPLE_CAN_REMOVE = "GENERATED_SAMPLE_CAN_REMOVE"
KEEP_IN_PLACE = "KEEP_IN_PLACE"
REVIEW = "REVIEW"

TEST_TARGET_DIR = ROOT / "project_maintenance" / "verification"
LEAF_TEST_TARGET_DIR = ROOT / "leaf_qt" / "tests"

GENERATED_TEST_FILENAMES = {
    "test_export_registry_sample.txt",
}

PROTECTED_TEST_PREFIXES = (
    "test_regen_",
    "test_material_",
    "test_coating_",
    "test_foundation_",
    "test_real_engine_",
    "test_benchmark_",
    "test_export_",
    "test_maintenance_",
    "test_codebase_",
    "test_repository_",
    "test_reference_",
    "test_verified_",
    "test_allowlist_",
)


def _iter_test_like_files() -> list[Path]:
    candidates = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        rel_parts = path.relative_to(ROOT).parts

        if any(part in {".git", ".venv", "venv", "__pycache__", "_leaf_archive", "LEAF_UPLOAD"} for part in rel_parts):
            continue

        name = path.name

        if name.startswith("test_") and path.suffix == ".py":
            candidates.append(path)

        if name in GENERATED_TEST_FILENAMES:
            candidates.append(path)

    return sorted(candidates)


def classify_test_file(path: Path) -> tuple[str, str, str]:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name

    if name in GENERATED_TEST_FILENAMES:
        return GENERATED_SAMPLE_CAN_REMOVE, rel, "Generated sample export file used only by registry test."

    if "/project_maintenance/verification/" in f"/{rel}":
        return KEEP_IN_PLACE, rel, "Already located in maintenance verification folder."

    if rel.startswith("project_maintenance/") and name.startswith("test_"):
        target = (TEST_TARGET_DIR / name).relative_to(ROOT).as_posix()
        return MOVE_TO_VERIFICATION, target, "Maintenance test should live in project_maintenance/verification."

    if rel.startswith("leaf_qt/") and name.startswith(PROTECTED_TEST_PREFIXES):
        return KEEP_REGRESSION_TEST, rel, "LEAF subsystem regression test; keep for future validation."

    if name.startswith(PROTECTED_TEST_PREFIXES):
        return KEEP_REGRESSION_TEST, rel, "Root-level regression test; keep until dedicated test package migration."

    if name.startswith("test_"):
        return REVIEW, rel, "Test file requires manual review before moving or removal."

    return REVIEW, rel, "Unclassified test-like file."


def build_test_file_cleanliness_plan() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    TEST_TARGET_DIR.mkdir(parents=True, exist_ok=True)
    LEAF_TEST_TARGET_DIR.mkdir(parents=True, exist_ok=True)

    actions = []
    counts = {
        KEEP_REGRESSION_TEST: 0,
        MOVE_TO_VERIFICATION: 0,
        GENERATED_SAMPLE_CAN_REMOVE: 0,
        KEEP_IN_PLACE: 0,
        REVIEW: 0,
    }

    for path in _iter_test_like_files():
        action, target, reason = classify_test_file(path)
        counts[action] += 1
        actions.append(
            {
                "source": path.relative_to(ROOT).as_posix(),
                "action": action,
                "target": target,
                "reason": reason,
            }
        )

    warnings = []
    blockers = []

    if counts[REVIEW]:
        warnings.append(f"{counts[REVIEW]} test-like files require manual review.")

    if counts[GENERATED_SAMPLE_CAN_REMOVE]:
        warnings.append(f"{counts[GENERATED_SAMPLE_CAN_REMOVE]} generated test sample files can be removed after backup.")

    if counts[MOVE_TO_VERIFICATION]:
        warnings.append(f"{counts[MOVE_TO_VERIFICATION]} maintenance test files should be relocated to verification.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "counts": counts,
        "actions": actions,
        "warnings": warnings,
        "blockers": blockers,
        "summary": f"{len(actions)} test-like files classified for cleanliness.",
    }


def build_test_file_cleanliness_report() -> str:
    plan = build_test_file_cleanliness_plan()

    lines = [
        "TEST FILE CLEANLINESS PLAN",
        "==========================",
        f"Phase: {plan['phase']}",
        f"Status: {plan['status']}",
        f"Passed: {plan['passed']}",
        f"Summary: {plan['summary']}",
        "",
        "ACTION COUNTS",
        "-------------",
    ]

    for key, value in plan["counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "CLASSIFIED TEST FILES", "---------------------"])

    for item in plan["actions"]:
        lines.append(
            f"- {item['action']}: {item['source']} -> {item['target']} :: {item['reason']}"
        )

    if plan["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in plan["warnings"])

    if plan["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in plan["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only classifies test files. It does not delete or move files.",
    ])

    return "\n".join(lines)


def write_test_file_cleanliness_plan() -> tuple[Path, Path]:
    plan = build_test_file_cleanliness_plan()

    report_path = REPORT_DIR / "TEST_FILE_CLEANLINESS_PLAN_PHASE_16T2N.txt"
    plan_path = PLAN_DIR / "TEST_FILE_CLEANLINESS_PLAN_PHASE_16T2N.tsv"

    report_path.write_text(build_test_file_cleanliness_report(), encoding="utf-8")

    rows = ["action\tsource\ttarget\treason"]
    for item in plan["actions"]:
        rows.append(f"{item['action']}\t{item['source']}\t{item['target']}\t{item['reason']}")

    plan_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    return plan_path, report_path


if __name__ == "__main__":
    plan_path, report_path = write_test_file_cleanliness_plan()
    plan = build_test_file_cleanliness_plan()
    print(plan["status"])
    print(plan_path)
    print(report_path)
