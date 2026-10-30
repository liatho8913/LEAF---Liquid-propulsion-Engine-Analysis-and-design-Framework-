from __future__ import annotations

from pathlib import Path
import ast
import json
import py_compile
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u165_safe_transactional_presentation_debt_cleanup_wave1.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u165b_failed_subset_repair.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u165b_failed_subset_repair.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u165b_backups"


def _tokens_from_literal(node: ast.AST) -> list[str]:
    raw = []

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        raw = [node.value]

    elif isinstance(node, ast.Tuple):
        for item in node.elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                raw.append(item.value)

    tokens = []
    for value in raw:
        upper = value.upper()
        for token in ("PASS", "WARN", "FAIL"):
            if upper.startswith(token) or upper.endswith("_" + token) or token in upper:
                if token not in tokens:
                    tokens.append(token)

    return tokens


def _status_expr(expr: str, tokens: list[str]) -> str:
    if len(tokens) == 1:
        return f'status_severity({expr}) == "{tokens[0]}"'

    joined = ", ".join(f'"{token}"' for token in tokens)
    return f"status_severity({expr}) in {{{joined}}}"


def _patch_line(line: str) -> tuple[str, int]:
    stripped = line.strip()

    if ".startswith(" not in stripped and ".endswith(" not in stripped:
        return line, 0

    try:
        tree = ast.parse(stripped)
    except SyntaxError:
        return line, 0

    replacements = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        if not isinstance(func, ast.Attribute):
            continue

        if func.attr not in {"startswith", "endswith"}:
            continue

        if not node.args:
            continue

        tokens = _tokens_from_literal(node.args[0])
        if not tokens:
            continue

        expr = ast.unparse(func.value)
        old = ast.get_source_segment(stripped, node)
        if not old:
            continue

        replacements.append((old, _status_expr(expr, tokens)))

    patched = stripped
    for old, new in replacements:
        patched = patched.replace(old, new)

    if not replacements:
        return line, 0

    indent = line[: len(line) - len(line.lstrip())]
    return indent + patched, len(replacements)


def _insert_import(text: str) -> str:
    import_line = "from leaf_qt.status_presentation import status_severity"

    if import_line in text:
        return text

    lines = text.splitlines()
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1

    lines.insert(insert_at, import_line)
    return "\n".join(lines) + "\n"


def patch_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    new_lines = []
    count = 0

    for line in text.splitlines():
        patched_line, line_count = _patch_line(line)
        new_lines.append(patched_line)
        count += line_count

    if count:
        patched = "\n".join(new_lines) + "\n"
        patched = _insert_import(patched)
        path.write_text(patched, encoding="utf-8")

    return count


def main() -> dict:
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    failures = data.get("compile_failures", [])

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    repaired = []
    unrepaired = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for failure in failures:
        rel_path = failure["path"]
        path = ROOT / rel_path

        if not path.exists():
            unrepaired.append({"path": rel_path, "reason": "missing_file"})
            continue

        backup_path = BACKUP_DIR / f"{timestamp}__{rel_path.replace('/', '__')}.bak"
        shutil.copy2(path, backup_path)

        replacement_count = patch_file(path)

        if replacement_count == 0:
            unrepaired.append({"path": rel_path, "reason": "no_ast_safe_replacement_found"})
            continue

        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            shutil.copy2(backup_path, path)
            unrepaired.append(
                {
                    "path": rel_path,
                    "reason": "compile_failed_after_repair",
                    "error": repr(exc),
                    "rolled_back": True,
                }
            )
            continue

        repaired.append(
            {
                "path": rel_path,
                "replacement_count": replacement_count,
                "backup": str(backup_path),
            }
        )

    passed = len(repaired) == len(failures) and not unrepaired

    result = {
        "phase": "16U.165B",
        "source_cleanup": str(IN_JSON),
        "failed_subset_count": len(failures),
        "repaired_count": len(repaired),
        "unrepaired_count": len(unrepaired),
        "repaired": repaired,
        "unrepaired": unrepaired,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U165B_FAILED_SUBSET_REPAIR"
            if passed
            else "FAIL_PHASE_16U165B_FAILED_SUBSET_REPAIR"
        ),
        "next_phase": "16U.166_SAFE_WAVE_REGRESSION_AND_RECLASSIFICATION",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.165B",
        "FAILED-SUBSET REPAIR",
        "=" * 28,
        f"status={result['status']}",
        f"failed_subset_count={result['failed_subset_count']}",
        f"repaired_count={result['repaired_count']}",
        f"unrepaired_count={result['unrepaired_count']}",
        "",
        "REPAIRED",
        "-" * 8,
    ]

    if repaired:
        for item in repaired:
            lines.append(f"{item['replacement_count']:4d}  {item['path']}")
    else:
        lines.append("No files repaired.")

    lines.extend(["", "UNREPAIRED", "-" * 10])
    if unrepaired:
        for item in unrepaired:
            lines.append(f"{item['path']} :: {item['reason']}")
    else:
        lines.append("No unrepaired files.")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"failed_subset_count={result['failed_subset_count']}")
    print(f"repaired_count={result['repaired_count']}")
    print(f"unrepaired_count={result['unrepaired_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
