from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import json
import py_compile
import re
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u170_structural_predicate_patchability_audit.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u171_equality_inequality_literal_cleanup_wave2.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u171_equality_inequality_literal_cleanup_wave2.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u171_backups"

STATUS_IMPORT = "from leaf_qt.status_presentation import status_severity"

TARGET_PATCHABILITIES = {
    "SAFE_EQUALITY_LITERAL_CANDIDATE",
    "SAFE_INEQUALITY_LITERAL_CANDIDATE",
}

STATUS_LITERAL_COMPARE = re.compile(
    r'(?P<expr>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*|\[[^\]]+\])*)'
    r'\s*(?P<op>==|!=)\s*'
    r'(?P<quote>["\'])(?P<token>PASS|WARN|FAIL)(?P=quote)'
)


def normalise_token(token: str) -> str:
    return token.strip().upper()


def replace_status_literal_comparisons(line: str) -> tuple[str, int]:
    def repl(match: re.Match) -> str:
        expr = match.group("expr")
        op = match.group("op")
        token = normalise_token(match.group("token"))
        return f'status_severity({expr}) {op} "{token}"'

    return STATUS_LITERAL_COMPARE.subn(repl, line)


def ensure_import(text: str) -> str:
    if STATUS_IMPORT in text:
        return text

    lines = text.splitlines()
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1

    lines.insert(insert_at, STATUS_IMPORT)
    return "\n".join(lines) + "\n"


def patch_file(path: Path, entries: list[dict]) -> dict:
    original = path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines()

    replacement_count = 0
    touched_lines = []

    for entry in entries:
        line_number = entry["line_number"]
        idx = line_number - 1

        if idx < 0 or idx >= len(lines):
            continue

        old_line = lines[idx]
        new_line, count = replace_status_literal_comparisons(old_line)

        if count:
            lines[idx] = new_line
            replacement_count += count
            touched_lines.append(line_number)

    if not replacement_count:
        return {
            "replacement_count": 0,
            "touched_lines": [],
            "patched_text": original,
        }

    patched = "\n".join(lines) + "\n"
    patched = ensure_import(patched)

    return {
        "replacement_count": replacement_count,
        "touched_lines": touched_lines,
        "patched_text": patched,
    }


def main() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"Missing patchability audit: {IN_JSON}")

    data = json.loads(IN_JSON.read_text(encoding="utf-8"))

    entries_by_file = defaultdict(list)

    for entry in data.get("audited_predicates", []):
        if entry.get("patchability") in TARGET_PATCHABILITIES:
            entries_by_file[entry["path"]].append(entry)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    touched = []
    skipped = []
    compile_failures = []

    for rel_path, entries in sorted(entries_by_file.items()):
        path = ROOT / rel_path

        if not path.exists():
            skipped.append({"path": rel_path, "reason": "missing_file"})
            continue

        backup_path = BACKUP_DIR / f"{timestamp}__{rel_path.replace('/', '__')}.bak"
        shutil.copy2(path, backup_path)

        patch_result = patch_file(path, entries)

        if patch_result["replacement_count"] == 0:
            skipped.append({"path": rel_path, "reason": "no_line_level_replacements"})
            continue

        path.write_text(patch_result["patched_text"], encoding="utf-8")

        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            shutil.copy2(backup_path, path)
            compile_failures.append(
                {
                    "path": rel_path,
                    "error": repr(exc),
                    "backup": str(backup_path),
                    "rolled_back": True,
                }
            )
            continue

        touched.append(
            {
                "path": rel_path,
                "replacement_count": patch_result["replacement_count"],
                "touched_lines": patch_result["touched_lines"],
                "backup": str(backup_path),
            }
        )

    passed = bool(touched) and not compile_failures

    result = {
        "phase": "16U.171",
        "candidate_file_count": len(entries_by_file),
        "candidate_predicate_count": sum(len(v) for v in entries_by_file.values()),
        "touched_count": len(touched),
        "skipped_count": len(skipped),
        "compile_failure_count": len(compile_failures),
        "touched": touched,
        "skipped": skipped,
        "compile_failures": compile_failures,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U171_EQUALITY_INEQUALITY_LITERAL_CLEANUP_WAVE2"
            if passed
            else "FAIL_PHASE_16U171_EQUALITY_INEQUALITY_LITERAL_CLEANUP_WAVE2"
        ),
        "next_phase": "16U.172_WAVE2_REGRESSION_AND_RECLASSIFICATION",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.171",
        "EQUALITY / INEQUALITY LITERAL CLEANUP WAVE 2",
        "=" * 54,
        f"status={result['status']}",
        f"candidate_file_count={result['candidate_file_count']}",
        f"candidate_predicate_count={result['candidate_predicate_count']}",
        f"touched_count={result['touched_count']}",
        f"skipped_count={result['skipped_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        "",
        "TOUCHED FILES",
        "-" * 13,
    ]

    for item in touched:
        lines.append(
            f"{item['replacement_count']:4d}  {item['path']} lines={item['touched_lines']}"
        )

    lines.extend(["", "SKIPPED FILES", "-" * 13])
    if skipped:
        for item in skipped:
            lines.append(f"{item['path']} :: {item['reason']}")
    else:
        lines.append("No skipped files.")

    lines.extend(["", "COMPILE FAILURES", "-" * 16])
    if compile_failures:
        for item in compile_failures:
            lines.append(f"{item['path']} :: {item['error']}")
    else:
        lines.append("No compile failures.")

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"candidate_file_count={result['candidate_file_count']}")
    print(f"candidate_predicate_count={result['candidate_predicate_count']}")
    print(f"touched_count={result['touched_count']}")
    print(f"skipped_count={result['skipped_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
