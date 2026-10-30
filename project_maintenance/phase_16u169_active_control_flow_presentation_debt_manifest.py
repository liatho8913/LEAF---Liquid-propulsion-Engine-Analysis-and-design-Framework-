from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict
import ast
import json


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u168_presentation_debt_context_extractor.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u169_active_control_flow_presentation_debt_manifest.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u169_active_control_flow_presentation_debt_manifest.txt"


def classify_predicate_shape(line: str) -> str:
    stripped = line.strip()

    if ".startswith(" in stripped:
        return "STATUS_STARTSWITH_PREDICATE"

    if ".endswith(" in stripped:
        return "STATUS_ENDSWITH_PREDICATE"

    if "status_severity(" in stripped:
        return "SHARED_STATUS_SEVERITY_PREDICATE"

    if " in " in stripped and ("PASS" in stripped or "WARN" in stripped or "FAIL" in stripped):
        return "MEMBERSHIP_STATUS_LITERAL_PREDICATE"

    if "==" in stripped and ("PASS" in stripped or "WARN" in stripped or "FAIL" in stripped):
        return "EQUALITY_STATUS_LITERAL_PREDICATE"

    if "!=" in stripped and ("PASS" in stripped or "WARN" in stripped or "FAIL" in stripped):
        return "INEQUALITY_STATUS_LITERAL_PREDICATE"

    return "UNKNOWN_ACTIVE_CONTROL_FLOW_PREDICATE"


def ast_parseable(line: str) -> bool:
    try:
        ast.parse(line.strip())
        return True
    except SyntaxError:
        return False


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    context_manifest = data.get("context_manifest", [])

    entries = []
    shape_counts = Counter()
    parse_counts = Counter()
    files_by_shape = defaultdict(set)

    for file_item in context_manifest:
        path = file_item["path"]

        for ctx in file_item.get("contexts", []):
            if ctx.get("context_classification") != "ACTIVE_CONTROL_FLOW_REVIEW_REQUIRED":
                continue

            line = ctx["line"]
            shape = classify_predicate_shape(line)
            parseable = ast_parseable(line)

            shape_counts[shape] += 1
            parse_counts["AST_PARSEABLE" if parseable else "AST_NOT_PARSEABLE"] += 1
            files_by_shape[shape].add(path)

            entries.append(
                {
                    "path": path,
                    "line_number": ctx["line_number"],
                    "pattern": ctx["pattern"],
                    "line": line,
                    "predicate_shape": shape,
                    "ast_parseable": parseable,
                }
            )

    result = {
        "phase": "16U.169",
        "active_control_flow_count": len(entries),
        "predicate_shape_counts": dict(shape_counts),
        "parse_counts": dict(parse_counts),
        "files_by_shape": {
            shape: sorted(paths)
            for shape, paths in sorted(files_by_shape.items())
        },
        "entries": entries,
        "passed": True,
        "status": "PASS_PHASE_16U169_ACTIVE_CONTROL_FLOW_PRESENTATION_DEBT_MANIFEST",
        "next_phase": "16U.170_STRUCTURAL_PREDICATE_PATCHABILITY_AUDIT",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.169",
        "ACTIVE CONTROL-FLOW PRESENTATION DEBT MANIFEST",
        "=" * 54,
        f"status={result['status']}",
        f"active_control_flow_count={result['active_control_flow_count']}",
        "",
        "PREDICATE SHAPE COUNTS",
        "-" * 24,
    ]

    for key, value in sorted(shape_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "AST PARSE COUNTS", "-" * 16])
    for key, value in sorted(parse_counts.items()):
        lines.append(f"{key}={value}")

    lines.extend(["", "FILES BY SHAPE", "-" * 14])
    for shape, paths in sorted(files_by_shape.items()):
        lines.append("")
        lines.append(shape)
        for path in sorted(paths):
            lines.append(f"  {path}")

    lines.extend(["", "ENTRIES", "-" * 7])
    for item in entries:
        lines.append(
            f"{item['path']}:{item['line_number']} "
            f"[{item['predicate_shape']}] "
            f"parseable={item['ast_parseable']} :: {item['line']}"
        )

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"active_control_flow_count={result['active_control_flow_count']}")
    print(f"predicate_shape_counts={result['predicate_shape_counts']}")
    print(f"parse_counts={result['parse_counts']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")
