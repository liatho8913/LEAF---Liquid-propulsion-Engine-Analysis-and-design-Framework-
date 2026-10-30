from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.10"
PASS_BANNER = "PASS_PHASE_16U10_ENGINE_SOLVER_MEDIUM_RISK_STATUS_CONSUMER_AUDIT"

AUDIT_JSON = Path("project_maintenance/engine_solver_status_consumer_integration_audit_phase_16u6.json")
LOW_RISK_REGRESSION_JSON = Path("project_maintenance/engine_solver_low_risk_status_wrapper_regression_phase_16u9.json")
OUT_JSON = Path("project_maintenance/engine_solver_medium_risk_status_consumer_audit_phase_16u10.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_MEDIUM_RISK_STATUS_CONSUMER_AUDIT_PHASE_16U10.txt")


@dataclass(frozen=True)
class MediumRiskCandidate:
    file: str
    line: int
    migration_group: str
    current_snippet: str
    recommended_action: str
    proposed_wrapper: str
    risk_resolution: str
    patchable_in_next_phase: bool
    reason: str


def classify_medium_candidate(item: dict) -> MediumRiskCandidate:
    snippet = item.get("snippet", "").strip()
    group = item.get("migration_group", "")
    file = item.get("file", "")
    line = int(item.get("line", 0))

    if '"FAIL" in statuses' in snippet or "'FAIL' in statuses" in snippet:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Replace list membership failure aggregation with solver_highest_severity(statuses).",
            proposed_wrapper='solver_highest_severity(statuses) == "FAIL"',
            risk_resolution="SAFE_COLLECTION_AGGREGATION",
            patchable_in_next_phase=True,
            reason="Variable name statuses indicates a collection of status values rather than arbitrary text.",
        )

    if '"WARN" in statuses' in snippet or "'WARN' in statuses" in snippet:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Replace list membership warning aggregation with solver_highest_severity(statuses).",
            proposed_wrapper='solver_highest_severity(statuses) == "WARN"',
            risk_resolution="SAFE_COLLECTION_AGGREGATION",
            patchable_in_next_phase=True,
            reason="Variable name statuses indicates a collection of status values rather than arbitrary text.",
        )

    if "status not in" in snippet and '"REQUIRED"' in snippet and '"PASS"' in snippet:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Preserve domain state REQUIRED and wrap PASS interpretation only.",
            proposed_wrapper='status != "REQUIRED" and not solver_pass(status)',
            risk_resolution="SAFE_DOMAIN_STATE_WITH_PASS_WRAPPER",
            patchable_in_next_phase=True,
            reason="REQUIRED is a domain state, not a canonical status; it must remain explicit.",
        )

    if 'elif source_data_weighted_gate in ("PARTIAL", "FAIL")' in snippet:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Do not migrate yet; PARTIAL is a source-quality domain state.",
            proposed_wrapper="manual review",
            risk_resolution="DOMAIN_STATE_REVIEW_REQUIRED",
            patchable_in_next_phase=False,
            reason="PARTIAL is not equivalent to WARN in all source-data contexts.",
        )

    if ".endswith" in snippet:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Do not migrate yet; suffix semantics may encode compound verdicts.",
            proposed_wrapper="manual review",
            risk_resolution="COMPOUND_STATUS_REVIEW_REQUIRED",
            patchable_in_next_phase=False,
            reason="endswith('PASS') may intentionally accept compound statuses that need context.",
        )

    if '"FAIL" in text' in snippet or '"WARN" in text' in snippet:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Do not migrate yet; text scanning may be semantic/freeform.",
            proposed_wrapper="manual review",
            risk_resolution="TEXT_SEMANTIC_REVIEW_REQUIRED",
            patchable_in_next_phase=False,
            reason="Freeform text scanning should not be converted without understanding source text.",
        )

    if snippet in {'"PASS",', '"FAIL",'}:
        return MediumRiskCandidate(
            file=file,
            line=line,
            migration_group=group,
            current_snippet=snippet,
            recommended_action="Do not migrate; likely literal inside payload/list context.",
            proposed_wrapper="none",
            risk_resolution="LIKELY_LITERAL_CONTEXT",
            patchable_in_next_phase=False,
            reason="Standalone literal needs surrounding context before modification.",
        )

    return MediumRiskCandidate(
        file=file,
        line=line,
        migration_group=group,
        current_snippet=snippet,
        recommended_action="Manual review required.",
        proposed_wrapper="manual review",
        risk_resolution="MANUAL_REVIEW_REQUIRED",
        patchable_in_next_phase=False,
        reason="No safe automated migration rule matched.",
    )


def build_medium_risk_audit() -> dict:
    if not AUDIT_JSON.exists():
        raise FileNotFoundError(f"Missing {AUDIT_JSON}. Run Phase 16U.6 first.")
    if not LOW_RISK_REGRESSION_JSON.exists():
        raise FileNotFoundError(f"Missing {LOW_RISK_REGRESSION_JSON}. Run Phase 16U.9 first.")

    source = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    low_regression = json.loads(LOW_RISK_REGRESSION_JSON.read_text(encoding="utf-8"))

    candidates = [
        item for item in source.get("candidates", [])
        if item.get("risk") == "MEDIUM"
    ]

    classified = [classify_medium_candidate(item) for item in candidates]

    by_resolution: dict[str, int] = {}
    patchable = []

    for item in classified:
        by_resolution[item.risk_resolution] = by_resolution.get(item.risk_resolution, 0) + 1
        if item.patchable_in_next_phase:
            patchable.append(item)

    passed = (
        source.get("status") == "PASS_PHASE_16U6_ENGINE_SOLVER_STATUS_CONSUMER_INTEGRATION_AUDIT"
        and low_regression.get("status") == "PASS_PHASE_16U9_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_REGRESSION"
        and len(candidates) > 0
        and len(classified) == len(candidates)
    )

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U10_ENGINE_SOLVER_MEDIUM_RISK_STATUS_CONSUMER_AUDIT",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_audit_status": source.get("status"),
        "low_risk_regression_status": low_regression.get("status"),
        "medium_risk_candidate_count": len(candidates),
        "patchable_next_phase_count": len(patchable),
        "manual_review_count": len(classified) - len(patchable),
        "by_resolution": dict(sorted(by_resolution.items())),
        "classified_candidates": [asdict(item) for item in classified],
        "patchable_candidates": [asdict(item) for item in patchable],
        "phase_16u10_engine_solver_medium_risk_status_consumer_audit_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.10",
        "ENGINE SOLVER MEDIUM-RISK STATUS CONSUMER AUDIT",
        "================================================",
        "",
        f"STATUS: {payload['status']}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase audits medium-risk Wave A solver status consumers.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Medium-risk candidates: {payload['medium_risk_candidate_count']}",
        f"Patchable next phase: {payload['patchable_next_phase_count']}",
        f"Manual review / hold: {payload['manual_review_count']}",
        "",
        "RESOLUTION BREAKDOWN",
        "--------------------",
    ]

    for key, value in payload["by_resolution"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "PATCHABLE NEXT PHASE", "--------------------"])
    for item in patchable:
        lines.append(f"{item.file}:{item.line} [{item.risk_resolution}]")
        lines.append(f"  current: {item.current_snippet}")
        lines.append(f"  wrapper: {item.proposed_wrapper}")
        lines.append(f"  reason: {item.reason}")

    lines.extend(["", "HELD FOR MANUAL REVIEW", "----------------------"])
    for item in classified:
        if not item.patchable_in_next_phase:
            lines.append(f"{item.file}:{item.line} [{item.risk_resolution}]")
            lines.append(f"  current: {item.current_snippet}")
            lines.append(f"  reason: {item.reason}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.10 COMPLETE." if passed else "PHASE 16U.10 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.11 — ENGINE SOLVER MEDIUM-RISK STATUS WRAPPER PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = build_medium_risk_audit()
    print(result["status"])
    print(f"medium_risk_candidate_count={result['medium_risk_candidate_count']}")
    print(f"patchable_next_phase_count={result['patchable_next_phase_count']}")
    print(f"manual_review_count={result['manual_review_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u10_engine_solver_medium_risk_status_consumer_audit_complete"]:
        raise SystemExit(1)
