from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.3"
PASS_BANNER = "PASS_PHASE_16U3_STRUCTURED_STATUS_MIGRATION_ROADMAP"

IN_JSON = Path("project_maintenance/structured_status_consumer_classification_phase_16u2.json")
OUT_JSON = Path("project_maintenance/structured_status_migration_roadmap_phase_16u3.json")
OUT_TXT = Path("project_maintenance/STRUCTURED_STATUS_MIGRATION_ROADMAP_PHASE_16U3.txt")


@dataclass(frozen=True)
class MigrationRoadmapItem:
    wave: str
    wave_title: str
    file: str
    line: int
    source_category: str
    pattern: str
    priority: str
    migration_action: str
    dependency_reason: str
    snippet: str


WAVE_ORDER = {
    "A": "Core Solver Status Consumers",
    "B": "Validation Owners",
    "C": "Master Gates",
    "D": "Completion Audits",
    "E": "GUI Consumers",
    "F": "Report Consumers",
    "G": "Export Consumers",
    "H": "Utility / Developer Consumers",
    "I": "Manual Review",
}


def choose_wave(item: dict) -> tuple[str, str, str, str]:
    file_path = item.get("file", "")
    category = item.get("source_category", "")
    snippet = item.get("snippet", "")

    lower = file_path.lower()

    if "engine_solver.py" in lower or category == "SOLVER_CONSUMER":
        return (
            "A",
            WAVE_ORDER["A"],
            "Wrap raw solver status decisions behind structured status access helpers without changing calculations.",
            "Solver status values feed validation, gates, reports, and GUI; migrate first.",
        )

    if category == "VALIDATION" or "validation" in lower or "validator" in lower:
        return (
            "B",
            WAVE_ORDER["B"],
            "Consume structured findings/global payload instead of branching on raw status strings.",
            "Validation owners sit immediately above solver outputs and below gates.",
        )

    if category == "MASTER_GATE" or "master_gate" in lower:
        return (
            "C",
            WAVE_ORDER["C"],
            "Replace raw status/severity aggregation with structured finding severity aggregation.",
            "Master gates should migrate after validations expose structured status consistently.",
        )

    if category == "COMPLETION_AUDIT" or "completion_audit" in lower or "audit" in lower:
        return (
            "D",
            WAVE_ORDER["D"],
            "Replace raw PASS/FAIL checks with structured status helper interpretation.",
            "Completion audits depend on solver, validation, and gate outputs.",
        )

    if category == "GUI" or any(token in lower for token in ["viewer", "window", "panel", "main_window"]):
        return (
            "E",
            WAVE_ORDER["E"],
            "Render structured findings/global status payload while retaining legacy display text.",
            "GUI should migrate after backend status payloads are stable.",
        )

    if category == "REPORT" or "report" in lower:
        return (
            "F",
            WAVE_ORDER["F"],
            "Generate report sections from structured findings and adapter reports.",
            "Reports should reflect migrated backend/GUI workflow state.",
        )

    if category == "EXPORT" or "export" in lower:
        return (
            "G",
            WAVE_ORDER["G"],
            "Export structured status payloads alongside legacy fields.",
            "Exports should be last among user-facing data products.",
        )

    if category in {"UTILITY", "DEVELOPER_TOOL"}:
        return (
            "H",
            WAVE_ORDER["H"],
            "Keep compatibility unless the utility drives production completion.",
            "Developer utilities are lower risk and can be migrated after production path.",
        )

    return (
        "I",
        WAVE_ORDER["I"],
        "Manual review required before migration.",
        "Classifier could not assign a safe dependency wave.",
    )


def build_structured_status_migration_roadmap() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(
            f"Missing {IN_JSON}. Run Phase 16U.2 classification first."
        )

    source = json.loads(IN_JSON.read_text(encoding="utf-8"))
    migration_targets = source.get("migration_required_findings", [])

    roadmap: list[MigrationRoadmapItem] = []

    for item in migration_targets:
        wave, title, action, reason = choose_wave(item)
        roadmap.append(
            MigrationRoadmapItem(
                wave=wave,
                wave_title=title,
                file=item.get("file", ""),
                line=int(item.get("line", 0)),
                source_category=item.get("source_category", ""),
                pattern=item.get("pattern", ""),
                priority=item.get("priority", ""),
                migration_action=action,
                dependency_reason=reason,
                snippet=item.get("snippet", ""),
            )
        )

    roadmap = sorted(
        roadmap,
        key=lambda x: (
            x.wave,
            {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}.get(x.priority, 4),
            x.file,
            x.line,
        ),
    )

    by_wave: dict[str, int] = {}
    by_file: dict[str, int] = {}

    for item in roadmap:
        by_wave[f"{item.wave} — {item.wave_title}"] = by_wave.get(f"{item.wave} — {item.wave_title}", 0) + 1
        by_file[item.file] = by_file.get(item.file, 0) + 1

    top_files = dict(sorted(by_file.items(), key=lambda pair: pair[1], reverse=True)[:30])

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_classification_status": source.get("status"),
        "source_migration_required_count": len(migration_targets),
        "roadmap_item_count": len(roadmap),
        "by_wave": dict(sorted(by_wave.items())),
        "top_migration_files": top_files,
        "roadmap": [asdict(item) for item in roadmap],
        "phase_16u3_structured_status_migration_roadmap_complete": True,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.3",
        "STRUCTURED STATUS MIGRATION ROADMAP",
        "======================================",
        "",
        f"STATUS: {PASS_BANNER}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase creates the ordered migration roadmap from Phase 16U.2.",
        "No engineering logic is modified.",
        "No solver logic is modified.",
        "No GUI behaviour is modified.",
        "",
        "SUMMARY",
        "-------",
        f"Source migration targets: {payload['source_migration_required_count']}",
        f"Roadmap items: {payload['roadmap_item_count']}",
        "",
        "MIGRATION WAVES",
        "---------------",
    ]

    for wave, count in payload["by_wave"].items():
        lines.append(f"{wave}: {count}")

    lines.extend(["", "TOP MIGRATION FILES", "-------------------"])
    for file, count in payload["top_migration_files"].items():
        lines.append(f"{file}: {count}")

    lines.extend(["", "ROADMAP DETAILS", "---------------"])
    current_wave = None
    shown_by_wave: dict[str, int] = {}

    for item in roadmap:
        key = f"{item.wave} — {item.wave_title}"
        if key != current_wave:
            current_wave = key
            lines.extend(["", key, "-" * len(key)])

        shown_by_wave[key] = shown_by_wave.get(key, 0) + 1

        if shown_by_wave[key] <= 80:
            lines.append(
                f"{item.file}:{item.line} "
                f"[{item.priority}/{item.source_category}/{item.pattern}] "
                f"{item.snippet}"
            )
            lines.append(f"  action: {item.migration_action}")
            lines.append(f"  dependency: {item.dependency_reason}")

    lines.extend(
        [
            "",
            "DEVELOPMENT ORDER",
            "-----------------",
            "16U.4 — Wave A Core Solver Status Consumer Wrappers",
            "16U.5 — Wave B Validation Owner Consumer Migration",
            "16U.6 — Wave C Master Gate Consumer Migration",
            "16U.7 — Wave D Completion Audit Consumer Migration",
            "16U.8 — Wave E GUI Consumer Migration",
            "16U.9 — Wave F/G Report and Export Consumer Migration",
            "16U.10 — Wave H/I Utility and Manual Review Cleanup",
            "16U.11 — Global Regression",
            "16U.12 — Consumer Migration Completion Audit",
            "16U.13 — Consumer Migration Master Gate",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.3 COMPLETE.",
            "A dependency-aware migration roadmap now exists.",
            "The project may now begin Wave A migration safely.",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_structured_status_migration_roadmap()
    print(result["status"])
    print(f"source_migration_required_count={result['source_migration_required_count']}")
    print(f"roadmap_item_count={result['roadmap_item_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
