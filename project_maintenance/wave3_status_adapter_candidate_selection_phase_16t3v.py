from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

PASS_STATUS = "PASS_WAVE3_STATUS_ADAPTER_CANDIDATE_SELECTION_PHASE_16T3V"
FAIL_STATUS = "FAIL_WAVE3_STATUS_ADAPTER_CANDIDATE_SELECTION_PHASE_16T3V"


EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "_leaf_artifacts",
}

ALREADY_MIGRATED_MARKERS = [
    "phase_16t3q1_status_adapter_complete",
    "phase_16t3q2_status_adapter_complete",
    "phase_16t3q3_status_adapter_complete",
    "phase_16t3q4_status_adapter_complete",
    "phase_16t3q5_status_adapter_complete",
    "phase_16t3q6_status_adapter_complete",
    "phase_16t3q7_status_adapter_complete",
    "phase_16t3q8_status_adapter_complete",
    "phase_16t3q9_status_adapter_complete",
    "phase_16t3q10_status_adapter_complete",
    "phase_16t3q11_status_adapter_complete",
    "phase_16t3q12_status_adapter_complete",
]

LEGACY_STATUS_PATTERN = re.compile(
    r"\b(PASS|WARN|FAIL)_[A-Z0-9_]+"
)

PRIORITY_TERMS = [
    "master_gate",
    "validation",
    "validator",
    "owner",
    "audit",
    "completion",
    "sign_off",
    "benchmark",
    "convergence",
    "report",
]


def _is_excluded(path):
    return bool(set(path.parts) & EXCLUDE_DIRS)


def _score_candidate(path, text, legacy_count):
    score = legacy_count

    name = path.name.lower()
    full = str(path).lower()

    for term in PRIORITY_TERMS:
        if term in name or term in full:
            score += 5

    if "test_" in name:
        score -= 8

    if "project_maintenance" in full:
        score -= 2

    if "leaf_qt" in full:
        score += 4

    if "master_gate" in full:
        score += 8

    if "validation" in full or "validator" in full:
        score += 6

    if "structured_findings" not in text:
        score += 3

    if "global_status" not in text:
        score += 3

    return score


def _classify_candidate(path, text):
    full = str(path).lower()

    if "test_" in path.name.lower():
        return "TEST_OR_REGRESSION"

    if "master_gate" in full:
        return "MASTER_GATE"

    if "validation" in full or "validator" in full:
        return "VALIDATION"

    if "owner" in full:
        return "OWNER"

    if "audit" in full or "completion" in full or "sign_off" in full:
        return "AUDIT_OR_COMPLETION"

    if "report" in full:
        return "REPORTING"

    return "GENERAL_STATUS_EMITTER"


def select_wave3_candidates(limit=12):
    candidates = []

    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)

        if _is_excluded(rel):
            continue

        text = path.read_text(errors="replace")

        legacy_matches = sorted(set(LEGACY_STATUS_PATTERN.findall(text)))
        legacy_status_strings = sorted(set(re.findall(r"\b(?:PASS|WARN|FAIL)_[A-Z0-9_]+", text)))

        if not legacy_status_strings:
            continue

        if any(marker in text for marker in ALREADY_MIGRATED_MARKERS):
            continue

        score = _score_candidate(rel, text, len(legacy_status_strings))

        candidates.append(
            {
                "path": str(rel),
                "classification": _classify_candidate(rel, text),
                "score": score,
                "legacy_status_count": len(legacy_status_strings),
                "legacy_status_examples": legacy_status_strings[:10],
                "has_structured_findings": "structured_findings" in text,
                "has_global_status": "global_status" in text,
                "has_adapter_report": "adapter_report" in text,
            }
        )

    ranked = sorted(
        candidates,
        key=lambda item: (
            item["score"],
            item["legacy_status_count"],
            item["path"],
        ),
        reverse=True,
    )

    selected = ranked[:limit]

    passed = bool(selected)
    status = PASS_STATUS if passed else FAIL_STATUS

    report_lines = [
        "LEAF PHASE 16T.3V",
        "WAVE 3 STATUS ADAPTER CANDIDATE SELECTION",
        "==========================================",
        "",
        f"Status: {status}",
        f"Candidates discovered: {len(candidates)}",
        f"Wave 3 selected candidates: {len(selected)}",
        "",
        "Selected Candidates:",
    ]

    for index, item in enumerate(selected, start=1):
        report_lines.append(
            f"{index}. {item['path']} | {item['classification']} | "
            f"score={item['score']} | legacy_statuses={item['legacy_status_count']}"
        )
        for example in item["legacy_status_examples"][:5]:
            report_lines.append(f"   - {example}")

    report_lines.extend(
        [
            "",
            "Selection Policy:",
            "- Prefer production modules over tests.",
            "- Prefer master gates, validation, ownership, audits, and reporting modules.",
            "- Exclude Wave 2 modules already containing Phase 16T.3Q adapter markers.",
            "- Do not modify production code during candidate selection.",
            "",
            "Decision:",
            (
                "Wave 3 candidate selection is complete."
                if passed
                else "Wave 3 candidate selection found no candidates."
            ),
        ]
    )

    return {
        "phase": "16T.3V",
        "passed": passed,
        "status": status,
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "selected_candidates": selected,
        "all_candidates": ranked,
        "report": "\n".join(report_lines),
        "wave3_status_adapter_candidate_selection_complete": passed,
        "phase_16t3v_wave3_status_adapter_candidate_selection_complete": passed,
    }


if __name__ == "__main__":
    result = select_wave3_candidates()
    print(result["report"])
    if not result["passed"]:
        raise SystemExit(1)
