from __future__ import annotations

from pathlib import Path
from collections import Counter
import ast
import json
import hashlib


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u175c_status_severity_import_issue_classifier.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u175d_local_status_severity_definition_equivalence_audit.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175d_local_status_severity_definition_equivalence_audit.txt"

SHARED_OWNER = ROOT / "leaf_qt" / "status_presentation.py"


def extract_function_source(path: Path, function_name: str) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "error": f"syntax_error:{exc}",
            "source": None,
            "normalised": None,
            "hash": None,
            "start_line": None,
            "end_line": None,
        }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            source = "\n".join(lines[start - 1:end])
            normalised = ast.dump(node, include_attributes=False)
            digest = hashlib.sha256(normalised.encode("utf-8")).hexdigest()

            return {
                "error": None,
                "source": source,
                "normalised": normalised,
                "hash": digest,
                "start_line": start,
                "end_line": end,
            }

    return None


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    shared = extract_function_source(SHARED_OWNER, "status_severity")

    if not shared or shared.get("error"):
        raise RuntimeError(f"Unable to extract shared status_severity owner from {SHARED_OWNER}")

    entries = []
    counts = Counter()

    for item in data.get("classified_issues", []):
        if item.get("classification") != "LOCAL_STATUS_SEVERITY_DEFINITION":
            continue

        rel_path = item["path"]
        path = ROOT / rel_path

        local = extract_function_source(path, "status_severity")

        if not local:
            equivalence = "LOCAL_DEFINITION_NOT_FOUND"
        elif local.get("error"):
            equivalence = "LOCAL_DEFINITION_PARSE_ERROR"
        elif local["hash"] == shared["hash"]:
            equivalence = "IDENTICAL_TO_SHARED_OWNER"
        else:
            equivalence = "DIFFERS_FROM_SHARED_OWNER"

        counts[equivalence] += 1

        entries.append(
            {
                "path": rel_path,
                "equivalence": equivalence,
                "local_start_line": local.get("start_line") if local else None,
                "local_end_line": local.get("end_line") if local else None,
                "local_hash": local.get("hash") if local else None,
                "shared_hash": shared["hash"],
                "local_source": local.get("source") if local else None,
            }
        )

    passed = (
        counts.get("LOCAL_DEFINITION_NOT_FOUND", 0) == 0
        and counts.get("LOCAL_DEFINITION_PARSE_ERROR", 0) == 0
    )

    result = {
        "phase": "16U.175D",
        "shared_owner": str(SHARED_OWNER.relative_to(ROOT)),
        "local_definition_count": len(entries),
        "equivalence_counts": dict(counts),
        "entries": entries,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175D_LOCAL_STATUS_SEVERITY_DEFINITION_EQUIVALENCE_AUDIT"
            if passed
            else "FAIL_PHASE_16U175D_LOCAL_STATUS_SEVERITY_DEFINITION_EQUIVALENCE_AUDIT"
        ),
        "next_phase": "16U.175E_LOCAL_STATUS_SEVERITY_DEDUPLICATION_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175D",
        "LOCAL STATUS SEVERITY DEFINITION EQUIVALENCE AUDIT",
        "=" * 60,
        f"status={result['status']}",
        f"shared_owner={result['shared_owner']}",
        f"local_definition_count={result['local_definition_count']}",
        "",
        "EQUIVALENCE COUNTS",
        "-" * 18,
    ]

    for key, value in sorted(counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "LOCAL DEFINITIONS", "-" * 17])

    for entry in entries:
        lines.append(
            f"{entry['path']} :: {entry['equivalence']} "
            f"lines={entry['local_start_line']}-{entry['local_end_line']}"
        )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"shared_owner={result['shared_owner']}")
    print(f"local_definition_count={result['local_definition_count']}")
    print(f"equivalence_counts={result['equivalence_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
