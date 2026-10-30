from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE = "16T.3A"

PASS_STATUS = "PASS_VERIFICATION_ARCHITECTURE_PHASE_16T3A"
FAIL_STATUS = "FAIL_VERIFICATION_ARCHITECTURE_PHASE_16T3A"

ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"

VERIFICATION_ROOT = ROOT / "verification"

REQUIRED_DIRECTORIES = (
    "verification",
    "verification/development_tests",
    "verification/regression",
    "verification/integration",
    "verification/engineering",
    "verification/engineering/regen",
    "verification/engineering/materials",
    "verification/engineering/coatings",
    "verification/engineering/thermal",
    "verification/engineering/geometry",
    "verification/engineering/optimisation",
    "verification/engineering/manufacturing",
    "verification/benchmarks",
    "verification/benchmarks/real_engines",
    "verification/certification",
    "verification/certification/rl10",
    "verification/certification/rs25",
    "verification/certification/raptor",
    "verification/certification/merlin",
    "verification/certification/be4",
    "verification/ui",
    "verification/production_gates",
)

PACKAGE_DIRECTORIES = REQUIRED_DIRECTORIES


def ensure_verification_architecture(root: str | Path = ROOT) -> dict[str, Any]:
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

    for directory in PACKAGE_DIRECTORIES:
        init_path = root_path / directory / "__init__.py"
        if init_path.exists():
            existing_init_files.append(f"{directory}/__init__.py")
        else:
            init_path.write_text("", encoding="utf-8")
            created_init_files.append(f"{directory}/__init__.py")

    missing_dirs = [
        directory for directory in REQUIRED_DIRECTORIES
        if not (root_path / directory).is_dir()
    ]

    missing_init_files = [
        f"{directory}/__init__.py"
        for directory in PACKAGE_DIRECTORIES
        if not (root_path / directory / "__init__.py").is_file()
    ]

    blockers = []

    if missing_dirs:
        blockers.append(f"Missing verification directories: {', '.join(missing_dirs)}")

    if missing_init_files:
        blockers.append(f"Missing verification package files: {', '.join(missing_init_files)}")

    status = FAIL_STATUS if blockers else PASS_STATUS

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
        "blockers": blockers,
        "warnings": [],
        "summary": (
            f"{len(REQUIRED_DIRECTORIES)} verification directories verified; "
            f"{len(PACKAGE_DIRECTORIES)} package markers verified."
        ),
    }


def verification_domain_manifest() -> dict[str, Any]:
    return {
        "development_tests": {
            "purpose": "Short-lived developer sanity checks and temporary diagnostics.",
            "retention": "Can be archived or removed after replacement by regression tests.",
        },
        "regression": {
            "purpose": "Permanent tests proving previous bugs and completed phases remain fixed.",
            "retention": "Never casually delete.",
        },
        "integration": {
            "purpose": "Tests proving modules communicate correctly.",
            "retention": "Keep while subsystem remains active.",
        },
        "engineering": {
            "purpose": "Physics, thermal, material, geometry, manufacturing, and optimisation validation.",
            "retention": "Permanent engineering verification.",
        },
        "benchmarks": {
            "purpose": "Comparison against known reference behaviour and public reference values.",
            "retention": "Permanent benchmark suite.",
        },
        "certification": {
            "purpose": "Real-engine and external reference validation cases.",
            "retention": "Permanent certification evidence.",
        },
        "ui": {
            "purpose": "GUI wiring, panel presence, callback, and interface behaviour checks.",
            "retention": "Keep while UI path is active.",
        },
        "production_gates": {
            "purpose": "Final sign-off gates that decide whether a feature is complete.",
            "retention": "Permanent release/sign-off evidence.",
        },
    }


def build_verification_architecture_report(root: str | Path = ROOT) -> str:
    audit = ensure_verification_architecture(root)
    manifest = verification_domain_manifest()

    lines = [
        "VERIFICATION ARCHITECTURE FOUNDATION",
        "====================================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "VERIFICATION DOMAINS",
        "--------------------",
    ]

    for name, info in manifest.items():
        lines.append(f"- {name}")
        lines.append(f"    purpose: {info['purpose']}")
        lines.append(f"    retention: {info['retention']}")

    lines.extend(["", "REQUIRED DIRECTORY LAYOUT", "-------------------------"])

    for directory in REQUIRED_DIRECTORIES:
        lines.append(f"- {directory}")

    if audit["created_dirs"]:
        lines.extend(["", "CREATED DIRECTORIES", "-------------------"])
        lines.extend(f"- {directory}" for directory in audit["created_dirs"])

    if audit["created_init_files"]:
        lines.extend(["", "CREATED PACKAGE MARKERS", "-----------------------"])
        lines.extend(f"- {path}" for path in audit["created_init_files"])

    if audit["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in audit["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only creates the verification architecture. It does not move, delete, or rewrite existing tests.",
    ])

    return "\n".join(lines)


def write_verification_architecture_report(root: str | Path = ROOT) -> Path:
    root_path = Path(root)
    report_dir = root_path / "_leaf_artifacts" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    output = report_dir / "VERIFICATION_ARCHITECTURE_PHASE_16T3A.txt"
    output.write_text(build_verification_architecture_report(root_path), encoding="utf-8")
    return output


if __name__ == "__main__":
    output = write_verification_architecture_report()
    audit = ensure_verification_architecture()
    print(audit["status"])
    print(output)
