from __future__ import annotations

import json
import py_compile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


PHASE = "16U.15"
PASS_BANNER = "PASS_PHASE_16U15_WAVE_B_VALIDATION_OWNER_STATUS_CONSUMER_AUDIT"

ROADMAP_JSON = Path("project_maintenance/structured_status_migration_roadmap_phase_16u3.json")
WAVE_A_GATE_JSON = Path("project_maintenance/wave_a_engine_solver_status_migration_closure_gate_phase_16u14.json")

OUT_JSON = Path("project_maintenance/wave_b_validation_owner_status_consumer_audit_phase_16u15.json")
OUT_TXT = Path("project_maintenance/WAVE_B_VALIDATION_OWNER_STATUS_CONSUMER_AUDIT_PHASE_16U15.txt")


@dataclass(frozen=True)
class ValidationCandidate:
    file: str
    line: int
    priority: str
    pattern: str
    migration_group: str
    risk: str
    patchable_next_phase: bool
    recommended_wrapper: str
    reason: str
    snippet: str


def classify_validation_candidate(item: dict) -> ValidationCandidate:
    file = item.get("file", "")
    line = int(item.get("line", 0))
    priority = item.get("priority", "")
    pattern = item.get("pattern", "")
    snippet = item.get("snippet", "").strip()

    if 'if "FAIL" in severities:' in snippet:
        return ValidationCandidate(
            file=file,
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="SEVERITY_COLLECTION_FAIL_AGGREGATION",
            risk="LOW",
            patchable_next_phase=True,
            recommended_wrapper='highest_severity(severities) == "FAIL"',
            reason="Variable name severities indicates structured severity aggregation, not freeform text.",
            snippet=snippet,
        )

    if 'str(results.get(key)).upper().startswith("PASS")' in snippet:
        return ValidationCandidate(
            file=file,
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="RESULT_KEY_PASS_PREFIX_CHECK",
            risk="LOW",
            patchable_next_phase=True,
            recommended_wrapper="is_pass(results.get(key))",
            reason="Result-key status prefix check can be routed through structured_status_access.is_pass.",
            snippet=snippet,
        )

    if 'return "FAIL"' in snippet or 'return "PASS"' in snippet:
        return ValidationCandidate(
            file=file,
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="STATUS_PRODUCER_RETURN",
            risk="HOLD",
            patchable_next_phase=False,
            recommended_wrapper="none",
            reason="This appears to produce legacy-compatible status output, not consume it.",
            snippet=snippet,
        )

    if 'marker = "PASS" if check["passed"] else "FAIL"' in snippet:
        return ValidationCandidate(
            file=file,
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="PRESENTATION_MARKER",
            risk="HOLD",
            patchable_next_phase=False,
            recommended_wrapper="none",
            reason="This appears to render a pass/fail marker from boolean check evidence.",
            snippet=snippet,
        )

    if '"FAIL" not in text' in snippet or '"WARN" not in text' in snippet:
        return ValidationCandidate(
            file=file,
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="TEXT_SEMANTIC_VALIDATION",
            risk="MEDIUM",
            patchable_next_phase=False,
            recommended_wrapper="manual review",
            reason="Text scanning may be semantic/freeform and should not be blindly wrapped.",
            snippet=snippet,
        )

    if snippet in {'"FAIL",', '"PASS",'}:
        return ValidationCandidate(
            file=file,
            line=line,
            priority=priority,
            pattern=pattern,
            migration_group="LITERAL_CONTEXT_REVIEW",
            risk="HOLD",
            patchable_next_phase=False,
            recommended_wrapper="none",
            reason="Standalone literal likely belongs to payload construction or evidence list.",
            snippet=snippet,
        )

    return ValidationCandidate(
        file=file,
        line=line,
        priority=priority,
        pattern=pattern,
        migration_group="MANUAL_REVIEW_REQUIRED",
        risk="MEDIUM",
        patchable_next_phase=False,
        recommended_wrapper="manual review",
        reason="No safe automated migration rule matched.",
        snippet=snippet,
    )


def compile_validation_files(files: list[str]) -> list[dict]:
    results = []
    for name in sorted(set(files)):
        path = Path(name)
        if not path.exists():
            results.append({"file": name, "passed": False, "error": "missing"})
            continue
        try:
            py_compile.compile(str(path), doraise=True)
            results.append({"file": name, "passed": True, "error": ""})
        except Exception as exc:
            results.append({"file": name, "passed": False, "error": repr(exc)})
    return results


def run_audit() -> dict:
    if not ROADMAP_JSON.exists():
        raise FileNotFoundError(f"Missing {ROADMAP_JSON}. Run Phase 16U.3 first.")
    if not WAVE_A_GATE_JSON.exists():
        raise FileNotFoundError(f"Missing {WAVE_A_GATE_JSON}. Run Phase 16U.14 first.")

    roadmap = json.loads(ROADMAP_JSON.read_text(encoding="utf-8"))
    wave_a_gate = json.loads(WAVE_A_GATE_JSON.read_text(encoding="utf-8"))

    validation_items = [
        item for item in roadmap.get("roadmap", [])
        if item.get("wave") == "B"
    ]

    classified = [classify_validation_candidate(item) for item in validation_items]
    patchable = [item for item in classified if item.patchable_next_phase]

    by_group: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    by_file: dict[str, int] = {}

    for item in classified:
        by_group[item.migration_group] = by_group.get(item.migration_group, 0) + 1
        by_risk[item.risk] = by_risk.get(item.risk, 0) + 1
        by_file[item.file] = by_file.get(item.file, 0) + 1

    compile_results = compile_validation_files([item.file for item in classified])

    passed = (
        roadmap.get("status") == "PASS_PHASE_16U3_STRUCTURED_STATUS_MIGRATION_ROADMAP"
        and wave_a_gate.get("status") == "PASS_PHASE_16U14_WAVE_A_ENGINE_SOLVER_STATUS_MIGRATION_CLOSURE_GATE"
        and len(validation_items) > 0
        and len(classified) == len(validation_items)
        and all(item["passed"] for item in compile_results)
    )

    payload = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U15_WAVE_B_VALIDATION_OWNER_STATUS_CONSUMER_AUDIT",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "roadmap_status": roadmap.get("status"),
        "wave_a_gate_status": wave_a_gate.get("status"),
        "validation_candidate_count": len(validation_items),
        "patchable_next_phase_count": len(patchable),
        "hold_or_manual_review_count": len(classified) - len(patchable),
        "by_group": dict(sorted(by_group.items())),
        "by_risk": dict(sorted(by_risk.items())),
        "by_file": dict(sorted(by_file.items())),
        "classified_candidates": [asdict(item) for item in classified],
        "patchable_candidates": [asdict(item) for item in patchable],
        "compile_results": compile_results,
        "phase_16u15_wave_b_validation_owner_status_consumer_audit_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.15",
        "WAVE B VALIDATION OWNER STATUS CONSUMER AUDIT",
        "================================================",
        "",
        f"STATUS: {payload['status']}",
        f"Generated: {payload['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase audits Wave B validation-owner status consumers.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Validation candidates: {payload['validation_candidate_count']}",
        f"Patchable next phase: {payload['patchable_next_phase_count']}",
        f"Hold/manual-review: {payload['hold_or_manual_review_count']}",
        "",
        "GROUP BREAKDOWN",
        "---------------",
    ]

    for key, value in payload["by_group"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "RISK BREAKDOWN", "--------------"])
    for key, value in payload["by_risk"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "FILES", "-----"])
    for key, value in payload["by_file"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "PATCHABLE NEXT PHASE", "--------------------"])
    for item in patchable:
        lines.append(f"{item.file}:{item.line} [{item.migration_group}]")
        lines.append(f"  current: {item.snippet}")
        lines.append(f"  wrapper: {item.recommended_wrapper}")
        lines.append(f"  reason: {item.reason}")
        lines.append("")

    lines.extend(["HELD / MANUAL REVIEW", "--------------------"])
    for item in classified:
        if not item.patchable_next_phase:
            lines.append(f"{item.file}:{item.line} [{item.migration_group}]")
            lines.append(f"  current: {item.snippet}")
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
            "PHASE 16U.15 COMPLETE." if passed else "PHASE 16U.15 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.16 — WAVE B VALIDATION OWNER LOW-RISK STATUS WRAPPER PATCH",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_audit()
    print(result["status"])
    print(f"validation_candidate_count={result['validation_candidate_count']}")
    print(f"patchable_next_phase_count={result['patchable_next_phase_count']}")
    print(f"hold_or_manual_review_count={result['hold_or_manual_review_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u15_wave_b_validation_owner_status_consumer_audit_complete"]:
        raise SystemExit(1)
