from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.universal_sorter_intelligence_bridge import (
    build_sorter_intelligence_bridge,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BRIDGE_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "universal_sorter_intelligence_bridge.py"

SAFE_LAYERS = {"development", "documentation"}
RUNTIME_LAYER = "runtime"

MAX_BATCH_SIZE = 50


def movement_risk(row: dict[str, Any], root: Path = ROOT) -> str:
    path = row["path"]
    destination = row["proposed_destination"]
    layer = row.get("current_layer")
    confidence = int(row.get("semantic_confidence") or 0)

    if (root / destination).exists():
        return "DESTINATION_EXISTS"

    if layer == RUNTIME_LAYER:
        return "HIGH_RUNTIME_MOVE_REQUIRES_DEDICATED_IMPORT_REWRITE"

    if path == destination:
        return "ALREADY_ALIGNED"

    if not row.get("sorter_input_ready"):
        return "BLOCKED_NOT_SORTER_READY"

    if confidence < 5:
        return "LOW_CONFIDENCE"

    if layer not in SAFE_LAYERS:
        return "UNKNOWN_LAYER"

    if Path(destination).suffix != Path(path).suffix:
        return "SUFFIX_CHANGE_BLOCKED"

    return "LOW"


def rank_candidate(row: dict[str, Any]) -> tuple[int, int, str]:
    confidence = int(row.get("semantic_confidence") or 0)
    path_depth = len(Path(row["path"]).parts)
    return (-confidence, path_depth, row["path"])


def build_planning_gate(root: str | Path = ".") -> dict[str, Any]:
    bridge = build_sorter_intelligence_bridge(root)
    summary = bridge["summary"]

    candidates = bridge["candidate_moves"]

    assessed = []
    for row in candidates:
        risk = movement_risk(row, Path(root))
        assessed.append({
            **row,
            "movement_risk": risk,
            "approved_for_batch": risk == "LOW",
        })

    sorted_low_risk = sorted(
        [row for row in assessed if row["approved_for_batch"]],
        key=rank_candidate,
    )

    approved = []
    used_destinations = set()
    duplicate_destination_rows = []

    for row in sorted_low_risk:
        destination = row["proposed_destination"]
        if destination in used_destinations:
            duplicate = dict(row)
            duplicate["approved_for_batch"] = False
            duplicate["movement_risk"] = "DUPLICATE_BATCH_DESTINATION"
            duplicate_destination_rows.append(duplicate)
            continue

        approved.append(row)
        used_destinations.add(destination)

        if len(approved) >= MAX_BATCH_SIZE:
            break

    blocked = [row for row in assessed if not row["approved_for_batch"]] + duplicate_destination_rows

    risk_counts: dict[str, int] = {}
    for row in assessed:
        risk_counts[row["movement_risk"]] = risk_counts.get(row["movement_risk"], 0) + 1

    return {
        "phase": "17C.9B",
        "schema": "LEAF_INTELLIGENCE_GUIDED_SORTER_PLANNING_GATE_V1",
        "bridge_schema": bridge["schema"],
        "api_schema": bridge["api_schema"],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "files_considered": summary["files_considered"],
            "candidate_move_count": summary["candidate_move_count"],
            "assessed_candidate_count": len(assessed),
            "approved_candidate_count": len(approved),
            "blocked_candidate_count": len(blocked),
            "max_batch_size": MAX_BATCH_SIZE,
            "architecture_errors": summary["architecture_errors"],
            "risk_counts": dict(sorted(risk_counts.items())),
        },
        "approved_batch": approved,
        "blocked_preview": blocked[:100],
    }


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(BRIDGE_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"bridge_compile_failure={exc!r}")

    gate = build_planning_gate(ROOT)
    summary = gate["summary"]

    if gate["bridge_schema"] != "LEAF_UNIVERSAL_SORTER_INTELLIGENCE_BRIDGE_V1":
        failures.append("bridge_schema_invalid")

    if gate["api_schema"] != "LEAF_REPOSITORY_INTELLIGENCE_API_V1":
        failures.append("api_schema_invalid")

    if summary["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    if summary["candidate_move_count"] <= 0:
        failures.append("no_candidate_moves_available")

    if summary["approved_candidate_count"] <= 0:
        failures.append("no_safe_candidates_approved")

    if summary["approved_candidate_count"] > MAX_BATCH_SIZE:
        failures.append("approved_batch_exceeds_limit")

    destinations = [row["proposed_destination"] for row in gate["approved_batch"]]
    if len(destinations) != len(set(destinations)):
        failures.append("duplicate_destinations_in_approved_batch")

    for row in gate["approved_batch"]:
        src = ROOT / row["path"]
        dst = ROOT / row["proposed_destination"]

        if not src.exists():
            failures.append(f"approved_source_missing={row['path']}")

        if dst.exists():
            failures.append(f"approved_destination_already_exists={row['proposed_destination']}")

        if row["movement_risk"] != "LOW":
            failures.append(f"non_low_risk_candidate_approved={row['path']}")

    gate["passed"] = not failures
    gate["failures"] = failures
    gate["completion_notice"] = (
        "PHASE_17C9B_COMPLETE_INTELLIGENCE_GUIDED_SORTER_PLANNING_GATE_ESTABLISHED"
        if not failures
        else "PHASE_17C9B_BLOCKED"
    )
    gate["next_phase"] = "17C.9C_INTELLIGENCE_GUIDED_DRY_RUN_MOVEMENT_PLAN"

    gate_json = OUT_DIR / "intelligence_guided_sorter_planning_gate_phase_17c9b.json"
    approved_json = OUT_DIR / "approved_intelligence_guided_sorter_batch_phase_17c9b.json"
    gate_txt = OUT_DIR / "intelligence_guided_sorter_planning_gate_phase_17c9b.txt"

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    approved_json.write_text(json.dumps(gate["approved_batch"], indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.9B INTELLIGENCE-GUIDED SORTER PLANNING GATE",
            "============================================================",
            f"passed={gate['passed']}",
            f"files_considered={summary['files_considered']}",
            f"candidate_move_count={summary['candidate_move_count']}",
            f"assessed_candidate_count={summary['assessed_candidate_count']}",
            f"approved_candidate_count={summary['approved_candidate_count']}",
            f"blocked_candidate_count={summary['blocked_candidate_count']}",
            f"max_batch_size={summary['max_batch_size']}",
            f"architecture_errors={summary['architecture_errors']}",
            f"risk_counts={summary['risk_counts']}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"json={gate_json.relative_to(ROOT)}",
            f"approved_batch_json={approved_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9B_INTELLIGENCE_GUIDED_SORTER_PLANNING_GATE" if gate["passed"] else "FAIL_PHASE_17C9B_INTELLIGENCE_GUIDED_SORTER_PLANNING_GATE")
    print(f"candidate_move_count={summary['candidate_move_count']}")
    print(f"assessed_candidate_count={summary['assessed_candidate_count']}")
    print(f"approved_candidate_count={summary['approved_candidate_count']}")
    print(f"blocked_candidate_count={summary['blocked_candidate_count']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"risk_counts={summary['risk_counts']}")
    print(f"approved_batch_json={approved_json.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
