from __future__ import annotations

from pathlib import Path
import json
import py_compile
import re
import shutil
from datetime import datetime


ROOT = Path(__file__).resolve().parents[1]

IN_JSON = ROOT / "project_maintenance" / "phase_16u164_high_risk_presentation_debt_manifest.json"
OUT_JSON = ROOT / "project_maintenance" / "phase_16u165_safe_transactional_presentation_debt_cleanup_wave1.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u165_safe_transactional_presentation_debt_cleanup_wave1.txt"
BACKUP_DIR = ROOT / "project_maintenance" / "phase_16u165_backups"


PREFIX_PATTERN = re.compile(
    r'(?P<expr>[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]+\]|\.[A-Za-z_][A-Za-z0-9_]*|\([^()]*\))*)'
    r'\.startswith\((?P<arg>[^)]*)\)'
)

SUFFIX_PATTERN = re.compile(
    r'(?P<expr>[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]+\]|\.[A-Za-z_][A-Za-z0-9_]*|\([^()]*\))*)'
    r'\.endswith\((?P<arg>[^)]*)\)'
)


def _extract_status_tokens(arg: str) -> list[str]:
    tokens = []
    for token in ("PASS", "WARN", "FAIL"):
        if f'"{token}' in arg or f"'{token}" in arg or f'_{token}' in arg:
            tokens.append(token)
    return tokens


def _replacement(match: re.Match) -> str:
    expr = match.group("expr")
    arg = match.group("arg")
    tokens = _extract_status_tokens(arg)

    if len(tokens) == 1:
        return f'status_severity({expr}) == "{tokens[0]}"'

    if len(tokens) > 1:
        joined = ", ".join(f'"{token}"' for token in tokens)
        return f"status_severity({expr}) in {{{joined}}}"

    return match.group(0)


def _insert_status_import(source: str) -> str:
    if "from leaf_qt.status_presentation import status_severity" in source:
        return source

    lines = source.splitlines()
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    if insert_at < len(lines) and lines[insert_at].startswith(('"""', "'''")):
        quote = lines[insert_at][:3]
        insert_at += 1
        while insert_at < len(lines):
            if quote in lines[insert_at]:
                insert_at += 1
                break
            insert_at += 1

    while insert_at < len(lines) and lines[insert_at].startswith("from __future__ import"):
        insert_at += 1

    lines.insert(insert_at, "from leaf_qt.status_presentation import status_severity")
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def _patch_text(source: str) -> tuple[str, int]:
    patched = source
    count = 0

    patched, prefix_count = PREFIX_PATTERN.subn(_replacement, patched)
    patched, suffix_count = SUFFIX_PATTERN.subn(_replacement, patched)

    count += prefix_count + suffix_count

    if count:
        patched = _insert_status_import(patched)

    return patched, count


def main() -> dict:
    if not IN_JSON.exists():
        raise FileNotFoundError(f"Missing 16U.164 manifest: {IN_JSON}")

    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    candidates = data.get("safe_wave_candidates", [])

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    touched = []
    skipped = []
    compile_failures = []
    patch_failures = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for item in candidates:
        rel_path = item["path"]
        path = ROOT / rel_path

        if not path.exists():
            skipped.append({"path": rel_path, "reason": "missing_file"})
            continue

        original = path.read_text(encoding="utf-8", errors="replace")
        patched, replacement_count = _patch_text(original)

        if replacement_count == 0 or patched == original:
            skipped.append({"path": rel_path, "reason": "no_safe_replacement_found"})
            continue

        backup_path = BACKUP_DIR / f"{timestamp}__{rel_path.replace('/', '__')}.bak"
        shutil.copy2(path, backup_path)

        path.write_text(patched, encoding="utf-8")

        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            shutil.copy2(backup_path, path)
            compile_failures.append(
                {
                    "path": rel_path,
                    "backup": str(backup_path),
                    "error": repr(exc),
                    "rolled_back": True,
                }
            )
            continue

        touched.append(
            {
                "path": rel_path,
                "backup": str(backup_path),
                "replacement_count": replacement_count,
            }
        )

    passed = bool(touched) and not compile_failures and not patch_failures

    result = {
        "phase": "16U.165",
        "source_manifest": str(IN_JSON),
        "candidate_count": len(candidates),
        "touched_count": len(touched),
        "skipped_count": len(skipped),
        "compile_failure_count": len(compile_failures),
        "patch_failure_count": len(patch_failures),
        "touched": touched,
        "skipped": skipped,
        "compile_failures": compile_failures,
        "patch_failures": patch_failures,
        "backup_dir": str(BACKUP_DIR),
        "passed": passed,
        "status": (
            "PASS_PHASE_16U165_SAFE_TRANSACTIONAL_PRESENTATION_DEBT_CLEANUP_WAVE1"
            if passed
            else "FAIL_PHASE_16U165_SAFE_TRANSACTIONAL_PRESENTATION_DEBT_CLEANUP_WAVE1"
        ),
        "next_phase": "16U.166_SAFE_WAVE_REGRESSION_AND_RECLASSIFICATION",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.165",
        "SAFE TRANSACTIONAL PRESENTATION DEBT CLEANUP WAVE 1",
        "=" * 62,
        f"status={result['status']}",
        f"candidate_count={result['candidate_count']}",
        f"touched_count={result['touched_count']}",
        f"skipped_count={result['skipped_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        f"patch_failure_count={result['patch_failure_count']}",
        f"backup_dir={result['backup_dir']}",
        "",
        "TOUCHED FILES",
        "-" * 13,
    ]

    if touched:
        for item in touched:
            lines.append(f"{item['replacement_count']:4d}  {item['path']}")
    else:
        lines.append("No files touched.")

    lines.extend(["", "SKIPPED FILES", "-" * 13])
    if skipped:
        for item in skipped:
            lines.append(f"{item['path']} :: {item['reason']}")
    else:
        lines.append("No files skipped.")

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
    print(f"candidate_count={result['candidate_count']}")
    print(f"touched_count={result['touched_count']}")
    print(f"skipped_count={result['skipped_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"patch_failure_count={result['patch_failure_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
