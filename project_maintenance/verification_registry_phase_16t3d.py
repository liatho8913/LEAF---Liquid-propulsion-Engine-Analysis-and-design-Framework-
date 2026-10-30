from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


PHASE = "16T.3D"

PASS_STATUS = "PASS_VERIFICATION_REGISTRY_PHASE_16T3D"
WARN_STATUS = "WARN_VERIFICATION_REGISTRY_PHASE_16T3D"
FAIL_STATUS = "FAIL_VERIFICATION_REGISTRY_PHASE_16T3D"

ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
REGISTRY_DIR = ROOT / "_leaf_artifacts" / "verification"
REGISTRY_PATH = REGISTRY_DIR / "verification_registry_phase_16t3d.json"

CLASSIFICATION_MAP = ROOT / "_leaf_artifacts" / "allowlists" / "VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B.tsv"

PERMANENT_DOMAINS = {
    "regression",
    "integration",
    "engineering_regen",
    "engineering_materials",
    "engineering_coatings",
    "engineering_thermal",
    "engineering_geometry",
    "engineering_optimisation",
    "engineering_manufacturing",
    "benchmarks_real_engines",
    "certification",
    "ui",
    "production_gates",
}

DOMAIN_SUBSYSTEMS = {
    "development_tests": "Maintenance / Development",
    "regression": "Regression",
    "integration": "Integration",
    "engineering_regen": "Regenerative Cooling",
    "engineering_materials": "Materials",
    "engineering_coatings": "Coatings",
    "engineering_thermal": "Thermal",
    "engineering_geometry": "Geometry",
    "engineering_optimisation": "Optimisation",
    "engineering_manufacturing": "Manufacturing",
    "benchmarks_real_engines": "Real Engine Benchmarks",
    "certification": "Certification",
    "ui": "User Interface",
    "production_gates": "Production Gates",
    "review": "Manual Review",
}


def _load_classification_rows() -> list[dict[str, str]]:
    if not CLASSIFICATION_MAP.exists():
        return []

    rows: list[dict[str, str]] = []

    with CLASSIFICATION_MAP.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(
                {
                    "domain": row.get("domain", "review"),
                    "source": row.get("source", ""),
                    "target": row.get("target", ""),
                    "reason": row.get("reason", ""),
                }
            )

    return rows


def _phase_tag(filename: str) -> str:
    patterns = [
        r"phase_(\d+[a-z]?\d*[a-z]?)",
        r"post(\d+[a-z]?\d*)",
        r"_(\d+[a-z]\d*[a-z]?)",
    ]

    lower = filename.lower()

    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            return match.group(1).upper()

    return "UNSPECIFIED"


def _lifecycle(domain: str, filename: str) -> str:
    name = filename.lower()

    if domain == "development_tests":
        return "DEVELOPMENT"

    if domain == "review":
        return "REVIEW"

    if "master_gate" in name or "completion_gate" in name or "signoff" in name or "production" in name:
        return "PRODUCTION_GATE"

    if "benchmark" in name or "real_engine" in name:
        return "BENCHMARK"

    if "integration" in name or "bridge" in name or "binding" in name:
        return "INTEGRATION"

    if domain.startswith("engineering_"):
        return "ENGINEERING_VERIFICATION"

    if domain == "regression":
        return "REGRESSION"

    return "ACTIVE_VERIFICATION"


def _permanent(domain: str, lifecycle: str) -> bool:
    if lifecycle in {"PRODUCTION_GATE", "BENCHMARK", "ENGINEERING_VERIFICATION", "REGRESSION", "INTEGRATION"}:
        return True

    return domain in PERMANENT_DOMAINS


def _can_archive(domain: str, lifecycle: str, permanent: bool) -> bool:
    if permanent:
        return False

    return domain in {"development_tests", "review"} and lifecycle in {"DEVELOPMENT", "REVIEW"}


def _owner_from_filename(filename: str, domain: str) -> str:
    name = filename.removeprefix("test_").removesuffix(".py")

    tokens = [
        token for token in name.split("_")
        if token not in {"phase", "post16f3", "post16f4", "post16f5"}
    ]

    if not tokens:
        return DOMAIN_SUBSYSTEMS.get(domain, "Unknown")

    return " ".join(token.capitalize() for token in tokens[:5])


def build_verification_registry() -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    rows = _load_classification_rows()

    blockers = []
    warnings = []

    if not CLASSIFICATION_MAP.exists():
        blockers.append(f"Classification map missing: {CLASSIFICATION_MAP}")

    records = []

    for index, row in enumerate(rows, start=1):
        source = row["source"]
        target = row["target"]
        domain = row["domain"]

        filename = Path(source).name
        source_path = ROOT / source

        lifecycle = _lifecycle(domain, filename)
        permanent = _permanent(domain, lifecycle)

        record = {
            "id": f"VER-{index:04d}",
            "phase": _phase_tag(filename),
            "filename": filename,
            "source_path": source,
            "target_path": target,
            "domain": domain,
            "subsystem": DOMAIN_SUBSYSTEMS.get(domain, "Unknown"),
            "owner": _owner_from_filename(filename, domain),
            "classification_reason": row.get("reason", ""),
            "lifecycle": lifecycle,
            "permanent": permanent,
            "can_archive": _can_archive(domain, lifecycle, permanent),
            "exists": source_path.exists(),
            "command": f"python {source}",
            "last_result": "NOT_RUN_BY_REGISTRY",
            "last_executed": None,
            "execution_time_seconds": None,
            "notes": [],
        }

        records.append(record)

    missing = [record for record in records if not record["exists"]]
    archiveable = [record for record in records if record["can_archive"]]

    if missing:
        warnings.append(f"{len(missing)} registry records point to missing source files.")

    if archiveable:
        warnings.append(f"{len(archiveable)} records are archive-eligible development/review checks.")

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    registry = {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "record_count": len(records),
        "missing_count": len(missing),
        "archiveable_count": len(archiveable),
        "records": records,
        "warnings": warnings,
        "blockers": blockers,
        "summary": f"{len(records)} verification records registered with metadata.",
    }

    REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    return registry


def build_verification_registry_report() -> str:
    registry = build_verification_registry()

    domain_counts: dict[str, int] = {}
    lifecycle_counts: dict[str, int] = {}

    for record in registry["records"]:
        domain_counts[record["domain"]] = domain_counts.get(record["domain"], 0) + 1
        lifecycle_counts[record["lifecycle"]] = lifecycle_counts.get(record["lifecycle"], 0) + 1

    lines = [
        "VERIFICATION REGISTRY & METADATA SYSTEM",
        "=======================================",
        f"Phase: {registry['phase']}",
        f"Status: {registry['status']}",
        f"Passed: {registry['passed']}",
        f"Summary: {registry['summary']}",
        f"Registry: {REGISTRY_PATH.relative_to(ROOT).as_posix()}",
        "",
        "COUNTS",
        "------",
        f"Records: {registry['record_count']}",
        f"Missing source files: {registry['missing_count']}",
        f"Archive-eligible records: {registry['archiveable_count']}",
        "",
        "DOMAIN COUNTS",
        "-------------",
    ]

    for key, value in sorted(domain_counts.items()):
        lines.append(f"{key}: {value}")

    lines.extend(["", "LIFECYCLE COUNTS", "----------------"])

    for key, value in sorted(lifecycle_counts.items()):
        lines.append(f"{key}: {value}")

    lines.extend(["", "REGISTRY PREVIEW", "----------------"])

    for record in registry["records"][:80]:
        lines.append(
            f"- {record['id']} | {record['domain']} | {record['lifecycle']} | "
            f"permanent={record['permanent']} | archive={record['can_archive']} | "
            f"{record['filename']}"
        )

    if len(registry["records"]) > 80:
        lines.append(f"... {len(registry['records']) - 80} additional records omitted from preview.")

    if registry["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in registry["warnings"])

    if registry["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in registry["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only writes a verification metadata registry. It does not move, delete, or execute verification files.",
    ])

    return "\n".join(lines)


def write_verification_registry_report() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output = REPORT_DIR / "VERIFICATION_REGISTRY_PHASE_16T3D.txt"
    output.write_text(build_verification_registry_report(), encoding="utf-8")
    return output


if __name__ == "__main__":
    report = write_verification_registry_report()
    registry = build_verification_registry()
    print(registry["status"])
    print(REGISTRY_PATH)
    print(report)
