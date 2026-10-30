from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


PHASE = "16T.3C"

PASS_STATUS = "PASS_VERIFICATION_ORCHESTRATOR_PHASE_16T3C"
WARN_STATUS = "WARN_VERIFICATION_ORCHESTRATOR_PHASE_16T3C"
FAIL_STATUS = "FAIL_VERIFICATION_ORCHESTRATOR_PHASE_16T3C"

ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"
CLASSIFICATION_MAP = ROOT / "_leaf_artifacts" / "allowlists" / "VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B.tsv"

DOMAIN_ORDER = (
    "development_tests",
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
    "review",
)


def load_verification_classification_map() -> list[dict[str, str]]:
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


def build_verification_suite_index() -> dict[str, list[dict[str, Any]]]:
    rows = load_verification_classification_map()

    suites: dict[str, list[dict[str, Any]]] = {domain: [] for domain in DOMAIN_ORDER}

    for row in rows:
        domain = row.get("domain") or "review"
        if domain not in suites:
            suites[domain] = []

        source = row.get("source", "")
        source_path = ROOT / source

        suites[domain].append(
            {
                "domain": domain,
                "source": source,
                "target": row.get("target", ""),
                "exists": source_path.exists(),
                "reason": row.get("reason", ""),
                "command": f"python {source}",
            }
        )

    return suites


def build_orchestrator_plan(selected_domain: str | None = None) -> dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not CLASSIFICATION_MAP.exists():
        return {
            "phase": PHASE,
            "status": FAIL_STATUS,
            "passed": False,
            "selected_domain": selected_domain or "ALL",
            "suite_count": 0,
            "test_count": 0,
            "missing_count": 0,
            "suites": {},
            "warnings": [],
            "blockers": [f"Classification map missing: {CLASSIFICATION_MAP}"],
            "summary": "Verification orchestrator cannot run because classification map is missing.",
        }

    suites = build_verification_suite_index()

    if selected_domain:
        suites = {selected_domain: suites.get(selected_domain, [])}

    missing = [
        item
        for tests in suites.values()
        for item in tests
        if not item["exists"]
    ]

    warnings = []
    blockers = []

    if missing:
        warnings.append(f"{len(missing)} mapped verification files are missing from their source paths.")

    if selected_domain and selected_domain not in DOMAIN_ORDER:
        blockers.append(f"Unknown verification domain: {selected_domain}")

    test_count = sum(len(items) for items in suites.values())

    status = FAIL_STATUS if blockers else WARN_STATUS if warnings else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "selected_domain": selected_domain or "ALL",
        "suite_count": sum(1 for items in suites.values() if items),
        "test_count": test_count,
        "missing_count": len(missing),
        "suites": suites,
        "warnings": warnings,
        "blockers": blockers,
        "summary": f"{test_count} verification files prepared across {sum(1 for items in suites.values() if items)} suites.",
    }


def build_orchestrator_report(selected_domain: str | None = None) -> str:
    plan = build_orchestrator_plan(selected_domain)

    lines = [
        "VERIFICATION ORCHESTRATOR FOUNDATION",
        "====================================",
        f"Phase: {plan['phase']}",
        f"Status: {plan['status']}",
        f"Passed: {plan['passed']}",
        f"Selected domain: {plan['selected_domain']}",
        f"Summary: {plan['summary']}",
        "",
        "SUITE COUNTS",
        "------------",
        f"Suites with tests: {plan['suite_count']}",
        f"Mapped verification files: {plan['test_count']}",
        f"Missing source files: {plan['missing_count']}",
        "",
        "DOMAIN EXECUTION PLAN",
        "---------------------",
    ]

    for domain in DOMAIN_ORDER:
        tests = plan["suites"].get(domain, [])
        if not tests:
            continue

        lines.append(f"\n[{domain}] count={len(tests)}")
        for item in tests:
            lines.append(
                f"- exists={item['exists']} | {item['command']} | target={item['target']}"
            )

    if plan["warnings"]:
        lines.extend(["", "WARNINGS", "--------"])
        lines.extend(f"- {warning}" for warning in plan["warnings"])

    if plan["blockers"]:
        lines.extend(["", "BLOCKERS", "--------"])
        lines.extend(f"- {blocker}" for blocker in plan["blockers"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only builds a dry-run verification execution plan. It does not move files or execute tests.",
    ])

    return "\n".join(lines)


def write_orchestrator_report(selected_domain: str | None = None) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    suffix = selected_domain or "ALL"
    output = REPORT_DIR / f"VERIFICATION_ORCHESTRATOR_PHASE_16T3C_{suffix}.txt"
    output.write_text(build_orchestrator_report(selected_domain), encoding="utf-8")
    return output


if __name__ == "__main__":
    report = write_orchestrator_report()
    plan = build_orchestrator_plan()
    print(plan["status"])
    print(report)
