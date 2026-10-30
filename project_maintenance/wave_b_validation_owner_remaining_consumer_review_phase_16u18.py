from __future__ import annotations

import json
import py_compile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.18"
PASS_BANNER = "PASS_PHASE_16U18_WAVE_B_VALIDATION_OWNER_REMAINING_CONSUMER_REVIEW"

AUDIT_JSON = Path("project_maintenance/wave_b_validation_owner_status_consumer_audit_phase_16u15.json")
REGRESSION_JSON = Path("project_maintenance/wave_b_validation_owner_low_risk_status_wrapper_regression_phase_16u17.json")

OUT_JSON = Path("project_maintenance/wave_b_validation_owner_remaining_consumer_review_phase_16u18.json")
OUT_TXT = Path("project_maintenance/WAVE_B_VALIDATION_OWNER_REMAINING_CONSUMER_REVIEW_PHASE_16U18.txt")


HANDLED_SNIPPETS = {
    'if "FAIL" in severities:',
    'if key in results and str(results.get(key)).upper().startswith("PASS"):',
}


@dataclass(frozen=True)
class RemainingValidationConsumer:
    file: str
    line: int
    original_group: str
    remaining_category: str
    closure_blocker: bool
    recommendation: str
    reason: str
    snippet: str


def classify_remaining(item: dict) -> RemainingValidationConsumer:
    snippet = item.get("snippet", "").strip()
    file = item.get("file", "")
    line = int(item.get("line", 0))
    group = item.get("migration_group", "")

    if group == "PRESENTATION_MARKER":
        return RemainingValidationConsumer(
            file=file,
            line=line,
            original_group=group,
            remaining_category="PRESENTATION_MARKER_INTENTIONAL_HOLD",
            closure_blocker=False,
            recommendation="Preserve as report/evidence rendering.",
            reason="Boolean-to-text PASS/FAIL markers are presentation evidence, not status consumers.",
            snippet=snippet,
        )

    if group == "STATUS_PRODUCER_RETURN":
        return RemainingValidationConsumer(
            file=file,
            line=line,
            original_group=group,
            remaining_category="STATUS_PRODUCER_INTENTIONAL_HOLD",
            closure_blocker=False,
            recommendation="Preserve as legacy-compatible status producer.",
            reason="Return literals produce compatibility status output rather than consume it.",
            snippet=snippet,
        )

    if group == "LITERAL_CONTEXT_REVIEW":
        return RemainingValidationConsumer(
            file=file,
            line=line,
            original_group=group,
            remaining_category="PAYLOAD_LITERAL_INTENTIONAL_HOLD",
            closure_blocker=False,
            recommendation="Preserve until payload schema is migrated.",
            reason="Standalone literals likely belong to payload/evidence construction.",
            snippet=snippet,
        )

    if group == "TEXT_SEMANTIC_VALIDATION":
        return RemainingValidationConsumer(
            file=file,
            line=line,
            original_group=group,
            remaining_category="TEXT_SEMANTIC_INTENTIONAL_HOLD",
            closure_blocker=False,
            recommendation="Preserve until structured diagnostic payload replaces freeform text checks.",
            reason="Text scanning is semantic and should not be automatically wrapped.",
            snippet=snippet,
        )

    if group == "MANUAL_REVIEW_REQUIRED":
        if "regen_validation_master_gate.py" in file:
            return RemainingValidationConsumer(
                file=file,
                line=line,
                original_group=group,
                remaining_category="REASSIGN_TO_WAVE_C_MASTER_GATE",
                closure_blocker=False,
                recommendation="Reassign to Wave C master-gate migration.",
                reason="This file is classified as a master gate by architecture and should not block Wave B closure.",
                snippet=snippet,
            )

        if "regen_viewer_physical_geometry_validation_owner" in file:
            return RemainingValidationConsumer(
                file=file,
                line=line,
                original_group=group,
                remaining_category="GUI_VALIDATION_BRIDGE_INTENTIONAL_HOLD",
                closure_blocker=False,
                recommendation="Preserve until GUI/validation bridge migration.",
                reason="Viewer-phase validation bridge mixes GUI runtime status with validation status.",
                snippet=snippet,
            )

    return RemainingValidationConsumer(
        file=file,
        line=line,
        original_group=group,
        remaining_category="UNRESOLVED_VALIDATION_CONSUMER",
        closure_blocker=True,
        recommendation="Manual migration decision required before Wave B closure.",
        reason="No intentional-hold classification matched.",
        snippet=snippet,
    )


def compile_files(files: list[str]) -> list[dict]:
    results = []
    for file in sorted(set(files)):
        path = Path(file)
        if not path.exists():
            results.append({"file": file, "passed": False, "error": "missing"})
            continue
        try:
            py_compile.compile(str(path), doraise=True)
            results.append({"file": file, "passed": True, "error": ""})
        except Exception as exc:
            results.append({"file": file, "passed": False, "error": repr(exc)})
    return results


def run_review() -> dict:
    if not AUDIT_JSON.exists():
        raise FileNotFoundError(f"Missing {AUDIT_JSON}. Run Phase 16U.15 first.")
    if not REGRESSION_JSON.exists():
        raise FileNotFoundError(f"Missing {REGRESSION_JSON}. Run Phase 16U.17 first.")

    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    regression = json.loads(REGRESSION_JSON.read_text(encoding="utf-8"))

    all_candidates = audit.get("classified_candidates", [])

    remaining_raw = [
        item for item in all_candidates
        if item.get("snippet", "").strip() not in HANDLED_SNIPPETS
    ]

    remaining = [classify_remaining(item) for item in remaining_raw]

    by_category: dict[str, int] = {}
    blockers = []

    for item in remaining:
        by_category[item.remaining_category] = by_category.get(item.remaining_category, 0) + 1
        if item.closure_blocker:
            blockers.append(item)

    compile_results = compile_files([item.file for item in remaining])

    passed = (
        audit.get("status") == "PASS_PHASE_16U15_WAVE_B_VALIDATION_OWNER_STATUS_CONSUMER_AUDIT"
        and regression.get("status") == "PASS_PHASE_16U17_WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_REGRESSION"
        and not blockers
        and all(item["passed"] for item in compile_results)
    )

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U18_WAVE_B_VALIDATION_OWNER_REMAINING_CONSUMER_REVIEW",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "audit_status": audit.get("status"),
        "regression_status": regression.get("status"),
        "remaining_candidate_count": len(remaining),
        "closure_blocker_count": len(blockers),
        "by_category": dict(sorted(by_category.items())),
        "remaining_consumers": [asdict(item) for item in remaining],
        "closure_blockers": [asdict(item) for item in blockers],
        "compile_results": compile_results,
        "phase_16u18_wave_b_validation_owner_remaining_consumer_review_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.18",
        "WAVE B VALIDATION OWNER REMAINING CONSUMER REVIEW",
        "===================================================",
        "",
        f"STATUS: {payload['status']}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase reviews remaining Wave B validation-owner status consumers.",
        "No production files are modified.",
        "No validation equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Remaining validation consumers: {payload['remaining_candidate_count']}",
        f"Closure blockers: {payload['closure_blocker_count']}",
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
            "PHASE 16U.18 COMPLETE." if passed else "PHASE 16U.18 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.19 — WAVE B VALIDATION OWNER STATUS MIGRATION CLOSURE GATE",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_review()
    print(result["status"])
    print(f"remaining_candidate_count={result['remaining_candidate_count']}")
    print(f"closure_blocker_count={result['closure_blocker_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u18_wave_b_validation_owner_remaining_consumer_review_complete"]:
        raise SystemExit(1)
