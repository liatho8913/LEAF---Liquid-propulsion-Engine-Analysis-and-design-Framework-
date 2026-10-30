from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE = "16T.3B"

PASS_STATUS = "PASS_VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B"
WARN_STATUS = "WARN_VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B"
FAIL_STATUS = "FAIL_VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B"

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
PLAN_DIR = ROOT / "_leaf_artifacts" / "allowlists"

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "_leaf_archive",
    "_leaf_artifacts",
    "LEAF_UPLOAD",
    "dist",
    "build",
}

DOMAIN_TARGETS = {
    "development_tests": "verification/development_tests",
    "regression": "verification/regression",
    "integration": "verification/integration",
    "engineering_regen": "verification/engineering/regen",
    "engineering_materials": "verification/engineering/materials",
    "engineering_coatings": "verification/engineering/coatings",
    "engineering_thermal": "verification/engineering/thermal",
    "engineering_geometry": "verification/engineering/geometry",
    "engineering_optimisation": "verification/engineering/optimisation",
    "engineering_manufacturing": "verification/engineering/manufacturing",
    "benchmarks_real_engines": "verification/benchmarks/real_engines",
    "certification": "verification/certification",
    "ui": "verification/ui",
    "production_gates": "verification/production_gates",
    "review": "verification/development_tests",
}


def _skip(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)


def iter_test_files() -> list[Path]:
    out = []

    for path in ROOT.rglob("test_*.py"):
        if path.is_file() and not _skip(path):
            out.append(path)

    return sorted(out)


def classify_test_domain(path: Path) -> tuple[str, str]:
    path = Path(path)
    absolute_path = path if path.is_absolute() else ROOT / path

    try:
        rel = absolute_path.relative_to(ROOT).as_posix()
    except ValueError:
        rel = path.as_posix()

    name = path.name.lower()

    if "/project_maintenance/" in f"/{rel}":
        return "development_tests", "Maintenance/developer infrastructure test."

    if "real_engine" in name or "benchmark" in name:
        return "benchmarks_real_engines", "Real-engine or benchmark verification."

    if "certification" in name or "rl10" in name or "rs25" in name or "raptor" in name or "merlin" in name or "be4" in name:
        return "certification", "Reference/certification-style engine validation."

    if "ui" in name or "viewer" in name or "window" in name or "button" in name or "canvas" in name or "panel" in name:
        return "ui", "GUI/viewer/panel/callback verification."

    if "master_gate" in name or "completion_gate" in name or "signoff" in name or "production" in name:
        return "production_gates", "Completion/sign-off/production gate."

    if "integration" in name or "bridge" in name or "binding" in name or "handover" in name:
        return "integration", "Integration or bridge verification."

    if "material" in name:
        return "engineering_materials", "Material engineering verification."

    if "coating" in name or "bond_coat" in name:
        return "engineering_coatings", "Coating/bond-coat engineering verification."

    if "thermal" in name or "heat" in name or "temperature" in name:
        return "engineering_thermal", "Thermal engineering verification."

    if "geometry" in name or "nozzle" in name or "station" in name or "channel" in name or "rib" in name:
        return "engineering_geometry", "Geometry/station/channel engineering verification."

    if "optimisation" in name or "optimization" in name or "candidate" in name or "mutation" in name or "ranking" in name or "selection" in name:
        return "engineering_optimisation", "Optimisation/candidate/ranking verification."

    if "manufacturability" in name or "manufacturing" in name:
        return "engineering_manufacturing", "Manufacturing/manufacturability verification."

    if "regen" in name:
        return "engineering_regen", "Regenerative cooling engineering verification."

    if "phase_" in name or "post16" in name:
        return "regression", "Phase/post-phase regression check."

    return "review", "Could not confidently classify; manual review required."


def build_verification_test_classification_map() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    PLAN_DIR.mkdir(parents=True, exist_ok=True)

    actions = []
    counts: dict[str, int] = {key: 0 for key in DOMAIN_TARGETS}

    for path in iter_test_files():
        domain, reason = classify_test_domain(path)
        target_root = DOMAIN_TARGETS[domain]
        target = f"{target_root}/{path.name}"

        counts[domain] = counts.get(domain, 0) + 1

        actions.append(
            {
                "source": path.relative_to(ROOT).as_posix(),
                "domain": domain,
                "target": target,
                "reason": reason,
            }
        )

    blockers = []
    warnings = []

    if counts.get("review", 0):
        warnings.append(f"{counts['review']} tests require manual review.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "test_count": len(actions),
        "counts": counts,
        "actions": actions,
        "warnings": warnings,
        "blockers": blockers,
        "summary": f"{len(actions)} test files classified into verification domains.",
    }


def build_verification_test_classification_report() -> str:
    mapping = build_verification_test_classification_map()

    lines = [
        "VERIFICATION TEST CLASSIFICATION MAP",
        "====================================",
        f"Phase: {mapping['phase']}",
        f"Status: {mapping['status']}",
        f"Passed: {mapping['passed']}",
        f"Summary: {mapping['summary']}",
        "",
        "DOMAIN COUNTS",
        "-------------",
    ]

    for key, value in mapping["counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "CLASSIFIED TESTS", "----------------"])

    for item in mapping["actions"]:
        lines.append(
            f"- {item['domain']}: {item['source']} -> {item['target']} :: {item['reason']}"
        )

    if mapping["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in mapping["warnings"])

    if mapping["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in mapping["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only classifies tests. It does not move, delete, or rewrite files.",
    ])

    return "\n".join(lines)


def write_verification_test_classification_map() -> tuple[Path, Path]:
    mapping = build_verification_test_classification_map()

    report_path = REPORT_DIR / "VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B.txt"
    plan_path = PLAN_DIR / "VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B.tsv"

    report_path.write_text(build_verification_test_classification_report(), encoding="utf-8")

    rows = ["domain\tsource\ttarget\treason"]
    for item in mapping["actions"]:
        rows.append(f"{item['domain']}\t{item['source']}\t{item['target']}\t{item['reason']}")

    plan_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    return plan_path, report_path


if __name__ == "__main__":
    plan_path, report_path = write_verification_test_classification_map()
    mapping = build_verification_test_classification_map()
    print(mapping["status"])
    print(plan_path)
    print(report_path)
