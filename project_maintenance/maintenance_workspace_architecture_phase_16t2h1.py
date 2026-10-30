from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE = "16T.2H.1"

PASS_STATUS = "PASS_MAINTENANCE_WORKSPACE_ARCHITECTURE_PHASE_16T2H1"
WARN_STATUS = "WARN_MAINTENANCE_WORKSPACE_ARCHITECTURE_PHASE_16T2H1"
FAIL_STATUS = "FAIL_MAINTENANCE_WORKSPACE_ARCHITECTURE_PHASE_16T2H1"

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = (
    "project_maintenance",
    "project_maintenance/audits",
    "project_maintenance/cleanup",
    "project_maintenance/verification",
    "project_maintenance/packaging",
    "project_maintenance/migration",
    "_leaf_artifacts",
    "_leaf_artifacts/reports",
    "_leaf_artifacts/zips",
    "_leaf_artifacts/exports",
    "_leaf_artifacts/logs",
    "_leaf_artifacts/allowlists",
    "_leaf_archive",
    "_leaf_archive/legacy_python",
    "_leaf_archive/legacy_reports",
    "_leaf_archive/legacy_scripts",
    "_leaf_archive/historical_snapshots",
)

PYTHON_PACKAGE_DIRS = (
    "project_maintenance",
    "project_maintenance/audits",
    "project_maintenance/cleanup",
    "project_maintenance/verification",
    "project_maintenance/packaging",
    "project_maintenance/migration",
)


def ensure_maintenance_workspace_architecture(root: str | Path = ROOT) -> dict[str, Any]:
    root_path = Path(root)

    created_dirs = []
    existing_dirs = []
    created_init_files = []
    existing_init_files = []

    for directory in REQUIRED_DIRECTORIES:
        path = root_path / directory
        if path.exists():
            existing_dirs.append(directory)
        else:
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(directory)

    for directory in PYTHON_PACKAGE_DIRS:
        init_path = root_path / directory / "__init__.py"
        if init_path.exists():
            existing_init_files.append(str(init_path.relative_to(root_path)))
        else:
            init_path.write_text("", encoding="utf-8")
            created_init_files.append(str(init_path.relative_to(root_path)))

    blockers = []
    warnings = []

    missing_dirs = [
        directory for directory in REQUIRED_DIRECTORIES
        if not (root_path / directory).is_dir()
    ]

    missing_init_files = [
        f"{directory}/__init__.py"
        for directory in PYTHON_PACKAGE_DIRS
        if not (root_path / directory / "__init__.py").is_file()
    ]

    if missing_dirs:
        blockers.append(f"Missing required directories: {', '.join(missing_dirs)}")

    if missing_init_files:
        blockers.append(f"Missing required package init files: {', '.join(missing_init_files)}")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "created_dirs": created_dirs,
        "existing_dirs": existing_dirs,
        "created_init_files": created_init_files,
        "existing_init_files": existing_init_files,
        "missing_dirs": missing_dirs,
        "missing_init_files": missing_init_files,
        "warnings": warnings,
        "blockers": blockers,
        "summary": (
            f"{len(REQUIRED_DIRECTORIES)} maintenance/artifact/archive directories verified; "
            f"{len(PYTHON_PACKAGE_DIRS)} Python package folders verified."
        ),
    }


def build_maintenance_workspace_architecture_report(root: str | Path = ROOT) -> str:
    audit = ensure_maintenance_workspace_architecture(root)

    lines = [
        "MAINTENANCE WORKSPACE ARCHITECTURE",
        "==================================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "REQUIRED DIRECTORY LAYOUT",
        "-------------------------",
    ]

    for directory in REQUIRED_DIRECTORIES:
        lines.append(f"- {directory}")

    lines.extend([
        "",
        "PYTHON PACKAGE DIRECTORIES",
        "--------------------------",
    ])

    for directory in PYTHON_PACKAGE_DIRS:
        lines.append(f"- {directory}/__init__.py")

    if audit["created_dirs"]:
        lines.extend(["", "CREATED DIRECTORIES", "-------------------"])
        lines.extend(f"- {directory}" for directory in audit["created_dirs"])

    if audit["created_init_files"]:
        lines.extend(["", "CREATED INIT FILES", "------------------"])
        lines.extend(f"- {path}" for path in audit["created_init_files"])

    if audit["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in audit["warnings"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only creates folders and __init__.py files. It does not delete or move project files.",
    ])

    return "\n".join(lines)


def write_maintenance_workspace_architecture_report(
    root: str | Path = ROOT,
    output_path: str | Path | None = None,
) -> Path:
    root_path = Path(root)
    report_dir = root_path / "_leaf_artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        output = report_dir / "MAINTENANCE_WORKSPACE_ARCHITECTURE_PHASE_16T2H1.txt"
    else:
        output = Path(output_path)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_maintenance_workspace_architecture_report(root_path), encoding="utf-8")
    return output


if __name__ == "__main__":
    report = write_maintenance_workspace_architecture_report()
    audit = ensure_maintenance_workspace_architecture()
    print(audit["status"])
    print(report)
