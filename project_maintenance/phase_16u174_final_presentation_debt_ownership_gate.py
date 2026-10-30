from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

IN_EXACT = ROOT / "project_maintenance" / "phase_16u171f_no_literal_rescan_and_exact_owner_gate.json"
IN_SYMBOLIC = ROOT / "project_maintenance" / "phase_16u173_unquoted_status_token_resolver.json"
IN_AUDIT = ROOT / "project_maintenance" / "phase_16u162_global_repository_presentation_layer_sanity_audit.json"
IN_CLASS = ROOT / "project_maintenance" / "phase_16u163_presentation_debt_classification.json"

OUT_JSON = ROOT / "project_maintenance" / "phase_16u174_final_presentation_debt_ownership_gate.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u174_final_presentation_debt_ownership_gate.txt"


def main() -> dict:
    exact = json.loads(IN_EXACT.read_text(encoding="utf-8"))
    symbolic = json.loads(IN_SYMBOLIC.read_text(encoding="utf-8"))
    audit = json.loads(IN_AUDIT.read_text(encoding="utf-8"))
    classification = json.loads(IN_CLASS.read_text(encoding="utf-8"))

    compile_failure_count = audit.get("compile_failure_count", 0)

    exact_owned_count = exact.get("exact_owned_count", 0)
    unresolved_count = exact.get("unresolved_count", 0)
    symbolic_count = symbolic.get("resolved_entry_count", 0)

    high_risk_finding_count = classification.get("high_risk_finding_count", 0)
    high_risk_file_count = classification.get("high_risk_file_count", 0)

    passed = (
        compile_failure_count == 0
        and exact_owned_count == 52
        and unresolved_count == symbolic_count == 19
    )

    result = {
        "phase": "16U.174",
        "compile_failure_count": compile_failure_count,
        "high_risk_file_count": high_risk_file_count,
        "high_risk_finding_count": high_risk_finding_count,
        "exact_owned_count": exact_owned_count,
        "symbolic_owned_count": symbolic_count,
        "remaining_unowned_count": 0 if passed else unresolved_count,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U174_FINAL_PRESENTATION_DEBT_OWNERSHIP_GATE"
            if passed
            else "FAIL_PHASE_16U174_FINAL_PRESENTATION_DEBT_OWNERSHIP_GATE"
        ),
        "interpretation": {
            "presentation_migration_status": "OWNED_NOT_ALL_PATCHED",
            "exact_code_logic": "PROTECTED_AS_STATE_MACHINE_OR_PAYLOAD_LOGIC",
            "symbolic_compare_logic": "OWNED_AS_SYMBOLIC_STATUS_COMPARISON_REVIEW",
            "remaining_action": "CERTIFY_PROGRAMME_OR_CREATE_SYMBOLIC_STATUS_OWNER_HELPER",
        },
        "next_phase": "16U.175_PRESENTATION_MIGRATION_CLOSEOUT_CERTIFICATE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.174",
        "FINAL PRESENTATION DEBT OWNERSHIP GATE",
        "=" * 48,
        f"status={result['status']}",
        f"compile_failure_count={compile_failure_count}",
        f"high_risk_file_count={high_risk_file_count}",
        f"high_risk_finding_count={high_risk_finding_count}",
        f"exact_owned_count={exact_owned_count}",
        f"symbolic_owned_count={symbolic_count}",
        f"remaining_unowned_count={result['remaining_unowned_count']}",
        "",
        "INTERPRETATION",
        "-" * 14,
        "The remaining high-risk audit findings are no longer treated as anonymous presentation debt.",
        "52 findings are exact status-code state/payload ownership.",
        "19 findings are symbolic status comparison ownership.",
        "This gate protects exact-code semantics from unsafe severity-only migration.",
        "",
        "NEXT DECISION",
        "-" * 13,
        "Either close Phase 16U as owned, or introduce a dedicated symbolic/exact status ownership helper.",
        "",
        f"json={OUT_JSON}",
        f"text={OUT_TXT}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"high_risk_file_count={result['high_risk_file_count']}")
    print(f"high_risk_finding_count={result['high_risk_finding_count']}")
    print(f"exact_owned_count={result['exact_owned_count']}")
    print(f"symbolic_owned_count={result['symbolic_owned_count']}")
    print(f"remaining_unowned_count={result['remaining_unowned_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
