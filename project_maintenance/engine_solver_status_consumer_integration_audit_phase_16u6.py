from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.6"
PASS_BANNER = "PASS_PHASE_16U6_ENGINE_SOLVER_STATUS_CONSUMER_INTEGRATION_AUDIT"

ROADMAP_JSON = Path("project_maintenance/structured_status_migration_roadmap_phase_16u3.json")
OUT_JSON = Path("project_maintenance/engine_solver_status_consumer_integration_audit_phase_16u6.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_STATUS_CONSUMER_INTEGRATION_AUDIT_PHASE_16U6.txt")


@dataclass(frozen=True)
class SolverMigrationCandidate:
    file: str
    line: int
    priority: str
    pattern: str
    migration_group: str
    risk: str
    recommended_wrapper: str
    reason: str
    snippet: str


def classify_solver_candidate(item: dict) -> SolverMigrationCandidate:
    snippet = item.get("snippet", "").strip()
    line = int(item.get("line", 0))
    pattern = item.get("pattern", "")
    priority = item.get("priority", "")

    if "!=" in snippet and '"PASS"' in snippet or "!= 'PASS'" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="PASS_NEGATION_CHECK",
            risk="LOW",
            recommended_wrapper="not solver_pass(value)",
            reason="Direct non-PASS decision can be wrapped without changing numerical calculations.",
            snippet=snippet,
        )

    if "== " in snippet and '"PASS"' in snippet or "== 'PASS'" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="PASS_EQUALITY_CHECK",
            risk="LOW",
            recommended_wrapper="solver_pass(value)",
            reason="Direct PASS equality can be wrapped by solver_pass.",
            snippet=snippet,
        )

    if "!=" in snippet and '"FAIL"' in snippet or "!= 'FAIL'" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="FAIL_NEGATION_CHECK",
            risk="LOW",
            recommended_wrapper="not solver_fail(value)",
            reason="Direct non-FAIL decision can be wrapped by solver_fail.",
            snippet=snippet,
        )

    if "== " in snippet and '"FAIL"' in snippet or "== 'FAIL'" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="FAIL_EQUALITY_CHECK",
            risk="LOW",
            recommended_wrapper="solver_fail(value)",
            reason="Direct FAIL equality can be wrapped by solver_fail.",
            snippet=snippet,
        )

    if '"FAIL" in' in snippet or "'FAIL' in" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="FAIL_COLLECTION_OR_TEXT_CONTAINS",
            risk="MEDIUM",
            recommended_wrapper="solver_highest_severity(values) / solver_fail(value)",
            reason="Contains-based failure checks may be list or text based; inspect before patching.",
            snippet=snippet,
        )

    if '"WARN" in' in snippet or "'WARN' in" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="WARN_COLLECTION_OR_TEXT_CONTAINS",
            risk="MEDIUM",
            recommended_wrapper="solver_highest_severity(values) / solver_warn(value)",
            reason="Contains-based warning checks may be list or text based; inspect before patching.",
            snippet=snippet,
        )

    if ".endswith" in snippet or ".startswith" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="PREFIX_SUFFIX_STATUS_CHECK",
            risk="MEDIUM",
            recommended_wrapper="solver_pass(value) / solver_fail(value)",
            reason="Prefix/suffix checks need context because some statuses encode extra meaning.",
            snippet=snippet,
        )

    if " not in " in snippet or " in (" in snippet or " in {" in snippet:
        return SolverMigrationCandidate(
            file=item.get("file", ""),
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="MEMBERSHIP_STATUS_CHECK",
            risk="MEDIUM",
            recommended_wrapper="solver_status(value) in {...}",
            reason="Membership checks often include non-status domain states and need manual preservation.",
            snippet=snippet,
        )

    return SolverMigrationCandidate(
        file=item.get("file", ""),
        line=line,
        priority=priority,
        pattern=pattern,
        migration_group="MANUAL_REVIEW",
        risk="HIGH",
        recommended_wrapper="manual inspection required",
        reason="Cannot safely infer wrapper from snippet alone.",
        snippet=snippet,
    )


def build_engine_solver_status_consumer_integration_audit() -> dict:
    if not ROADMAP_JSON.exists():
        raise FileNotFoundError(f"Missing {ROADMAP_JSON}. Run Phase 16U.3 first.")

    roadmap = json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))
    items = roadmap.get("roadmap", [])

    solver_items = [
        item for item in items
        if item.get("wave") == "A" and item.get("file") in {
            "leaf_qt/engine_solver.py",
            "leaf_qt/regen_geometry_solver.py",
        }
    ]

    candidates = [classify_solver_candidate(item) for item in solver_items]

    by_group: dict[str, int] = {}
    by_risk: dict[str, int] = {}

    for candidate in candidates:
        by_group[candidate.migration_group] = by_group.get(candidate.migration_group, 0) + 1
        by_risk[candidate.risk] = by_risk.get(candidate.risk, 0) + 1

    low_risk = [item for item in candidates if item.risk == "LOW"]
    medium_risk = [item for item in candidates if item.risk == "MEDIUM"]
    high_risk = [item for item in candidates if item.risk == "HIGH"]

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_roadmap_status": roadmap.get("status"),
        "solver_candidate_count": len(candidates),
        "low_risk_count": len(low_risk),
        "medium_risk_count": len(medium_risk),
        "high_risk_count": len(high_risk),
        "by_group": dict(sorted(by_group.items())),
        "by_risk": dict(sorted(by_risk.items())),
        "recommended_first_patch_group": "PASS_EQUALITY_CHECK / PASS_NEGATION_CHECK / FAIL_EQUALITY_CHECK / FAIL_NEGATION_CHECK",
        "candidates": [asdict(item) for item in candidates],
        "low_risk_candidates": [asdict(item) for item in low_risk],
        "phase_16u6_engine_solver_status_consumer_integration_audit_complete": True,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.6",
        "ENGINE SOLVER STATUS CONSUMER INTEGRATION AUDIT",
        "================================================",
        "",
        f"STATUS: {PASS_BANNER}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase audits Wave A solver status consumers.",
        "No engineering logic is modified.",
        "No solver equations are modified.",
        "No production consumers are patched in this phase.",
        "",
        "SUMMARY",
        "-------",
        f"Solver candidates: {payload['solver_candidate_count']}",
        f"Low risk: {payload['low_risk_count']}",
        f"Medium risk: {payload['medium_risk_count']}",
        f"High risk: {payload['high_risk_count']}",
        "",
        "GROUP BREAKDOWN",
        "---------------",
    ]

    for key, value in payload["by_group"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "RISK BREAKDOWN", "--------------"])
    for key, value in payload["by_risk"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "LOW-RISK FIRST PATCH TARGETS", "----------------------------"])
    for item in low_risk:
        lines.append(
            f"{item.file}:{item.line} "
            f"[{item.migration_group}/{item.pattern}] {item.snippet}"
        )
        lines.append(f"  wrapper: {item.recommended_wrapper}")
        lines.append(f"  reason: {item.reason}")

    lines.extend(
        [
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.7 — ENGINE SOLVER LOW-RISK STATUS WRAPPER PATCH",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.6 COMPLETE.",
            "Solver-side status consumer integration targets have been audited.",
            "The project may now patch only the low-risk equality/inequality group.",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_engine_solver_status_consumer_integration_audit()
    print(result["status"])
    print(f"solver_candidate_count={result['solver_candidate_count']}")
    print(f"low_risk_count={result['low_risk_count']}")
    print(f"medium_risk_count={result['medium_risk_count']}")
    print(f"high_risk_count={result['high_risk_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
