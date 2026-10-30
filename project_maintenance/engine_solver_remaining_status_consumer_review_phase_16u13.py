from __future__ import annotations

import json
import py_compile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.13"
PASS_BANNER = "PASS_PHASE_16U13_ENGINE_SOLVER_REMAINING_STATUS_CONSUMER_REVIEW"

AUDIT_JSON = Path("project_maintenance/engine_solver_status_consumer_integration_audit_phase_16u6.json")
LOW_REGRESSION_JSON = Path("project_maintenance/engine_solver_low_risk_status_wrapper_regression_phase_16u9.json")
MEDIUM_REGRESSION_JSON = Path("project_maintenance/engine_solver_medium_risk_status_wrapper_regression_phase_16u12.json")

OUT_JSON = Path("project_maintenance/engine_solver_remaining_status_consumer_review_phase_16u13.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_REMAINING_STATUS_CONSUMER_REVIEW_PHASE_16U13.txt")

ENGINE = Path("leaf_qt/engine_solver.py")
GEOMETRY = Path("leaf_qt/regen_geometry_solver.py")


@dataclass(frozen=True)
class RemainingConsumer:
    file: str
    line: int
    source_group: str
    risk: str
    remaining_category: str
    recommendation: str
    wave_closure_blocker: bool
    snippet: str
    reason: str


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(path), "passed": False, "error": repr(exc)}


def classify_remaining(item: dict) -> RemainingConsumer:
    snippet = item.get("snippet", "").strip()
    risk = item.get("risk", "")
    group = item.get("migration_group", "")

    if risk == "HIGH":
        return RemainingConsumer(
            file=item.get("file", ""),
            line=int(item.get("line", 0)),
            source_group=group,
            risk=risk,
            remaining_category="HIGH_RISK_MANUAL_REVIEW_REQUIRED",
            recommendation="Hold for manual review; do not automate in Wave A.",
            wave_closure_blocker=False,
            snippet=snippet,
            reason="High-risk items require local engineering context and should not block closure if explicitly recorded.",
        )

    if 'elif source_data_weighted_gate in ("PARTIAL", "FAIL")' in snippet:
        return RemainingConsumer(
            file=item.get("file", ""),
            line=int(item.get("line", 0)),
            source_group=group,
            risk=risk,
            remaining_category="DOMAIN_STATE_INTENTIONAL_HOLD",
            recommendation="Preserve until source-quality domain-state migration.",
            wave_closure_blocker=False,
            snippet=snippet,
            reason="PARTIAL is a source-quality state, not a simple status.",
        )

    if 'if item["status"] in ("MISSING", "PLACEHOLDER", "FAIL")' in snippet:
        return RemainingConsumer(
            file=item.get("file", ""),
            line=int(item.get("line", 0)),
            source_group=group,
            risk=risk,
            remaining_category="MIXED_DOMAIN_STATUS_INTENTIONAL_HOLD",
            recommendation="Preserve until coating/material data-quality status migration.",
            wave_closure_blocker=False,
            snippet=snippet,
            reason="MISSING and PLACEHOLDER are data-quality states mixed with FAIL.",
        )

    if "verdict.endswith" in snippet:
        return RemainingConsumer(
            file=item.get("file", ""),
            line=int(item.get("line", 0)),
            source_group=group,
            risk=risk,
            remaining_category="COMPOUND_VERDICT_INTENTIONAL_HOLD",
            recommendation="Preserve until compound verdict compatibility adapter exists.",
            wave_closure_blocker=False,
            snippet=snippet,
            reason="Suffix PASS handling may intentionally support compound legacy statuses.",
        )

    if '"FAIL" in text' in snippet or '"WARN" in text' in snippet:
        return RemainingConsumer(
            file=item.get("file", ""),
            line=int(item.get("line", 0)),
            source_group=group,
            risk=risk,
            remaining_category="FREEFORM_TEXT_SEMANTIC_INTENTIONAL_HOLD",
            recommendation="Preserve until text diagnostic parser is replaced with structured diagnostic payload.",
            wave_closure_blocker=False,
            snippet=snippet,
            reason="Freeform diagnostic text scanning is semantic and should not be wrapped blindly.",
        )

    return RemainingConsumer(
        file=item.get("file", ""),
        line=int(item.get("line", 0)),
        source_group=group,
        risk=risk,
        remaining_category="UNRESOLVED_REVIEW_REQUIRED",
        recommendation="Manual inspection required before Wave A closure.",
        wave_closure_blocker=True,
        snippet=snippet,
        reason="No known intentional-hold category matched.",
    )


def run_review() -> dict:
    for required in (AUDIT_JSON, LOW_REGRESSION_JSON, MEDIUM_REGRESSION_JSON):
        if not required.exists():
            raise FileNotFoundError(f"Missing {required}")

    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    low_regression = json.loads(LOW_REGRESSION_JSON.read_text(encoding="utf-8"))
    medium_regression = json.loads(MEDIUM_REGRESSION_JSON.read_text(encoding="utf-8"))

    candidates = audit.get("candidates", [])

    remaining_candidates = [
        item for item in candidates
        if item.get("risk") in {"MEDIUM", "HIGH"}
    ]

    # Remove medium-risk items already handled by Phase 16U.11.
    handled_snippets = {
        'if status not in ("REQUIRED", "PASS"):',
        'if "FAIL" in statuses:',
        'elif "WARN" in statuses:',
    }

    remaining_candidates = [
        item for item in remaining_candidates
        if item.get("snippet", "").strip() not in handled_snippets
    ]

    remaining = [classify_remaining(item) for item in remaining_candidates]

    by_category: dict[str, int] = {}
    blockers = []

    for item in remaining:
        by_category[item.remaining_category] = by_category.get(item.remaining_category, 0) + 1
        if item.wave_closure_blocker:
            blockers.append(item)

    compile_results = [compile_file(ENGINE), compile_file(GEOMETRY)]

    passed = (
        audit.get("status") == "PASS_PHASE_16U6_ENGINE_SOLVER_STATUS_CONSUMER_INTEGRATION_AUDIT"
        and low_regression.get("status") == "PASS_PHASE_16U9_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_REGRESSION"
        and medium_regression.get("status") == "PASS_PHASE_16U12_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_REGRESSION"
        and all(item["passed"] for item in compile_results)
        and not blockers
    )

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U13_ENGINE_SOLVER_REMAINING_STATUS_CONSUMER_REVIEW",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source_audit_status": audit.get("status"),
        "low_risk_regression_status": low_regression.get("status"),
        "medium_risk_regression_status": medium_regression.get("status"),
        "remaining_candidate_count": len(remaining),
        "wave_closure_blocker_count": len(blockers),
        "by_category": dict(sorted(by_category.items())),
        "remaining_consumers": [asdict(item) for item in remaining],
        "wave_closure_blockers": [asdict(item) for item in blockers],
        "compile_results": compile_results,
        "phase_16u13_engine_solver_remaining_status_consumer_review_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.13",
        "ENGINE SOLVER REMAINING STATUS CONSUMER REVIEW",
        "================================================",
        "",
        f"STATUS: {payload['status']}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase reviews remaining Wave A solver status consumers.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Remaining solver consumers: {payload['remaining_candidate_count']}",
        f"Wave closure blockers: {payload['wave_closure_blocker_count']}",
        "",
        "CATEGORY BREAKDOWN",
        "------------------",
    ]

    for key, value in payload["by_category"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "REMAINING CONSUMERS", "-------------------"])
    for item in remaining:
        lines.append(f"{item.file}:{item.line} [{item.remaining_category}]")
        lines.append(f"  snippet: {item.snippet}")
        lines.append(f"  recommendation: {item.recommendation}")
        lines.append(f"  reason: {item.reason}")
        lines.append("")

    lines.extend(["COMPILE RESULTS", "---------------"])
    for item in compile_results:
        lines.append(f"{item['file']}: {'PASS' if item['passed'] else 'FAIL'} {item['error']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.13 COMPLETE." if passed else "PHASE 16U.13 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.14 — WAVE A ENGINE SOLVER STATUS MIGRATION CLOSURE GATE",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_review()
    print(result["status"])
    print(f"remaining_candidate_count={result['remaining_candidate_count']}")
    print(f"wave_closure_blocker_count={result['wave_closure_blocker_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u13_engine_solver_remaining_status_consumer_review_complete"]:
        raise SystemExit(1)
