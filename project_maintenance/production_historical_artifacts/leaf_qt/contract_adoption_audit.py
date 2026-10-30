from __future__ import annotations

from pathlib import Path
from typing import Any

from core.architecture.io import read_json_artifact, write_json_artifact, write_text_artifact


INDEX_PATH = Path("artifacts/repository_architecture_index.json")
OUT_JSON = Path("artifacts/contract_adoption_audit.json")
OUT_TXT = Path("artifacts/contract_adoption_audit.txt")


CONTRACT_RULES = {
    "SolverContract": {
        "roles": {"SOLVER"},
        "subsystems": {"SOLVER", "REGEN"},
        "name_keywords": {"solver", "solve", "engine_solver"},
    },
    "ValidationContract": {
        "roles": {"VALIDATION_OWNER"},
        "subsystems": {"VALIDATION"},
        "name_keywords": {"validation", "validator", "validate"},
    },
    "ReportingContract": {
        "roles": {"REPORT_OWNER"},
        "subsystems": {"REPORTING"},
        "name_keywords": {"report", "reporting"},
    },
    "RegistryContract": {
        "roles": {"REGISTRY"},
        "subsystems": {"REGISTRY"},
        "name_keywords": {"registry", "registered"},
    },
    "OptimisationContract": {
        "roles": set(),
        "subsystems": {"OPTIMISATION", "CANDIDATE_SELECTION"},
        "name_keywords": {"optimisation", "optimization", "candidate", "ranking"},
    },
    "UIPanelContract": {
        "roles": {"UI_PANEL", "UI_WINDOW", "UI_VIEWER"},
        "subsystems": {"UI", "UI_VIEWER", "UI_GRAPHING"},
        "name_keywords": {"panel", "window", "viewer", "graph"},
    },
}


def load_index(path: Path = INDEX_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing architecture index: {path}. "
            "Run python leaf_qt/repository_architecture_index.py first."
        )
    return read_json_artifact(path)


def _score_contract(file_entry: dict[str, Any], contract_name: str, rule: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    path = file_entry.get("path", "")
    lowered_path = path.lower()
    role = file_entry.get("role", "")
    subsystem = file_entry.get("subsystem", "")
    classes = [str(item).lower() for item in file_entry.get("classes", [])]
    functions = [str(item).lower() for item in file_entry.get("functions", [])]

    if role in rule["roles"]:
        score += 40
        reasons.append(f"ROLE_MATCH:{role}")

    if subsystem in rule["subsystems"]:
        score += 30
        reasons.append(f"SUBSYSTEM_MATCH:{subsystem}")

    for keyword in rule["name_keywords"]:
        if keyword in lowered_path:
            score += 15
            reasons.append(f"PATH_KEYWORD:{keyword}")
            break

    for keyword in rule["name_keywords"]:
        if any(keyword in cls for cls in classes):
            score += 20
            reasons.append(f"CLASS_KEYWORD:{keyword}")
            break

    for keyword in rule["name_keywords"]:
        if any(keyword in fn for fn in functions):
            score += 10
            reasons.append(f"FUNCTION_KEYWORD:{keyword}")
            break

    if path.startswith("project_maintenance/"):
        score -= 30
        reasons.append("MAINTENANCE_PATH_DEPRIORITISED")

    if "test_" in lowered_path or lowered_path.endswith("_test.py"):
        score -= 25
        reasons.append("TEST_PATH_DEPRIORITISED")

    if "phase_" in lowered_path:
        score -= 20
        reasons.append("PHASE_ARTIFACT_DEPRIORITISED")

    return max(score, 0), reasons


def _should_skip_file(file_entry: dict[str, Any]) -> bool:
    path = str(file_entry.get("path", ""))
    lowered = path.lower()
    line_count = int(file_entry.get("line_count", 0))

    if line_count <= 0:
        return True

    if lowered.endswith("/__init__.py") or lowered == "__init__.py":
        return True

    if "/core/contracts/" in lowered:
        return True

    if "/core/solver_adapters/" in lowered:
        return True

    if "/core/architecture/" in lowered:
        return True

    if lowered.endswith("_audit.py"):
        return True

    if lowered.endswith("_plan.py"):
        return True

    if lowered.endswith("_harness.py"):
        return True

    return False


def build_contract_adoption_audit(index: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []

    for file_entry in index.get("files", []):
        if _should_skip_file(file_entry):
            continue

        best_contract = None
        best_score = 0
        best_reasons: list[str] = []

        for contract_name, rule in CONTRACT_RULES.items():
            score, reasons = _score_contract(file_entry, contract_name, rule)
            if score > best_score:
                best_contract = contract_name
                best_score = score
                best_reasons = reasons

        if not best_contract or best_score <= 0:
            continue

        if best_score >= 80:
            priority = "FIRST_WAVE"
        elif best_score >= 55:
            priority = "SECOND_WAVE"
        elif best_score >= 30:
            priority = "LATER_WAVE"
        else:
            priority = "LOW_CONFIDENCE"

        candidates.append(
            {
                "path": file_entry.get("path"),
                "recommended_contract": best_contract,
                "adoption_score": best_score,
                "priority": priority,
                "reasons": best_reasons,
                "subsystem": file_entry.get("subsystem"),
                "role": file_entry.get("role"),
                "line_count": file_entry.get("line_count", 0),
                "classes": file_entry.get("classes", []),
                "functions": file_entry.get("functions", []),
            }
        )

    candidates.sort(
        key=lambda item: (
            item["priority"] == "FIRST_WAVE",
            item["adoption_score"],
            item["line_count"],
        ),
        reverse=True,
    )

    contract_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    for item in candidates:
        contract_counts[item["recommended_contract"]] = contract_counts.get(item["recommended_contract"], 0) + 1
        priority_counts[item["priority"]] = priority_counts.get(item["priority"], 0) + 1

    return {
        "schema": "LEAF_CONTRACT_ADOPTION_AUDIT_V1",
        "source_schema": index.get("schema"),
        "summary": {
            "candidates": len(candidates),
            "contract_counts": dict(sorted(contract_counts.items())),
            "priority_counts": dict(sorted(priority_counts.items())),
        },
        "first_wave": [item for item in candidates if item["priority"] == "FIRST_WAVE"],
        "candidates": candidates,
        "safe_to_modify_files": False,
        "note": (
            "This audit recommends contract adoption order only. "
            "It does not modify existing runtime modules."
        ),
    }


def build_text_report(audit: dict[str, Any]) -> str:
    summary = audit["summary"]

    lines = [
        "LEAF CONTRACT ADOPTION AUDIT",
        "============================",
        f"schema={audit['schema']}",
        f"safe_to_modify_files={audit['safe_to_modify_files']}",
        f"candidates={summary['candidates']}",
        "",
        "CONTRACT COUNTS",
        "---------------",
    ]

    for key, value in summary["contract_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "PRIORITY COUNTS", "---------------"])

    for key, value in summary["priority_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "FIRST WAVE", "----------"])

    for item in audit["first_wave"][:30]:
        lines.append(
            f"{item['adoption_score']:>3} | "
            f"{item['recommended_contract']:<22} | "
            f"{item['line_count']:>6} lines | "
            f"{item['subsystem']} | "
            f"{item['role']} | "
            f"{item['path']}"
        )

    return "\n".join(lines)


def write_contract_adoption_audit() -> dict[str, Any]:
    index = load_index()
    audit = build_contract_adoption_audit(index)

    write_json_artifact(audit, OUT_JSON)
    write_text_artifact(build_text_report(audit), OUT_TXT)

    return audit


if __name__ == "__main__":
    result = write_contract_adoption_audit()
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")
    print("PASS_CONTRACT_ADOPTION_AUDIT")
