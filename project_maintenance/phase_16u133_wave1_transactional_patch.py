from pathlib import Path
import json, hashlib, py_compile, re, shutil

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

MANIFEST_JSON = PM / "phase_16u132_wave1_manifest_selection.json"
OUT_JSON = PM / "phase_16u133_wave1_transactional_patch.json"
OUT_TXT = PM / "PHASE_16U133_WAVE1_TRANSACTIONAL_PATCH.txt"
BACKUP_DIR = PM / "phase_16u133_wave1_backups"
BACKUP_DIR.mkdir(exist_ok=True)

PASS = "PASS_PHASE_16U133_WAVE1_TRANSACTIONAL_PATCH"
FAIL = "FAIL_PHASE_16U133_WAVE1_TRANSACTIONAL_PATCH"

fallback = '''try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "DEGRADED" in text:
            return "WARN"
        if "PASS" in text or "OK" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"

    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

'''

legacy_patterns = [
    (r'"PASS"\s+if\s+([^,\n]+?)\s+else\s+"FAIL"', r'LegacyCompatibilityProducer.marker_from_bool(\1)'),
    (r"'PASS'\s+if\s+([^,\n]+?)\s+else\s+'FAIL'", r'LegacyCompatibilityProducer.marker_from_bool(\1)'),
    (r'"FAIL"\s+if\s+([^,\n]+?)\s+else\s+"PASS"', r'LegacyCompatibilityProducer.marker_from_bool(not (\1))'),
    (r"'FAIL'\s+if\s+([^,\n]+?)\s+else\s+'PASS'", r'LegacyCompatibilityProducer.marker_from_bool(not (\1))'),
    (r'"WARN"\s+if\s+([^,\n]+?)\s+else\s+"PASS"', r'("WARN" if bool(\1) else "PASS")'),
    (r"'WARN'\s+if\s+([^,\n]+?)\s+else\s+'PASS'", r'("WARN" if bool(\1) else "PASS")'),
]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compile_ok(path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except Exception as exc:
        return False, str(exc)

def insert_fallback(text):
    if "LegacyCompatibilityProducer" in text:
        return text, "already_present"

    if "from leaf_qt.status_presentation import status_severity" in text:
        return text.replace(
            "from leaf_qt.status_presentation import status_severity",
            "from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity",
            1,
        ), "extended_existing_status_presentation_import"

    if "from leaf_qt.status_presentation import" in text:
        return re.sub(
            r"from leaf_qt\.status_presentation import ([^\n]+)",
            lambda m: m.group(0) if "LegacyCompatibilityProducer" in m.group(1)
            else "from leaf_qt.status_presentation import LegacyCompatibilityProducer, " + m.group(1),
            text,
            count=1,
        ), "extended_existing_status_presentation_import_generic"

    lines = text.splitlines(True)
    idx = 0
    while idx < len(lines):
        s = lines[idx].strip()
        if s.startswith("#") or s == "":
            idx += 1
            continue
        if s.startswith('"""') or s.startswith("'''"):
            q = s[:3]
            idx += 1
            while idx < len(lines) and q not in lines[idx]:
                idx += 1
            idx += 1
            continue
        break

    return "".join(lines[:idx]) + fallback + "".join(lines[idx:]), "inserted_status_presentation_import_fallback"

manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
files = manifest["selected_files"]

results = []
wave_failures = []

for name in files:
    path = LEAF / name
    backup = BACKUP_DIR / name

    file_result = {
        "file": name,
        "path": f"leaf_qt/{name}",
        "backup": str(backup.relative_to(ROOT)),
        "applied": [],
        "failures": [],
    }

    if not path.exists():
        file_result["failures"].append("missing file")
        results.append(file_result)
        wave_failures.append(f"{name}: missing file")
        continue

    pre_hash = sha256(path)
    file_result["sha256_before"] = pre_hash

    shutil.copy2(path, backup)
    file_result["backup_created"] = backup.exists()

    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    pre_compile, pre_compile_error = compile_ok(path)
    file_result["compile_before"] = pre_compile
    if not pre_compile:
        file_result["failures"].append(f"pre_compile_failed: {pre_compile_error}")

    text, import_action = insert_fallback(text)
    file_result["applied"].append(import_action)

    for pattern, repl in legacy_patterns:
        text, count = re.subn(pattern, repl, text)
        if count:
            file_result["applied"].append(f"legacy_replacement:{pattern}:{count}")

    path.write_text(text, encoding="utf-8")

    post_compile, post_compile_error = compile_ok(path)
    file_result["compile_after"] = post_compile
    if not post_compile:
        file_result["failures"].append(f"post_compile_failed: {post_compile_error}")
        path.write_text(original, encoding="utf-8")

    patched = path.read_text(encoding="utf-8", errors="replace")
    file_result["sha256_after"] = sha256(path)

    if "LegacyCompatibilityProducer" not in patched:
        file_result["failures"].append("LegacyCompatibilityProducer missing after patch")
    if "status_severity" not in patched:
        file_result["failures"].append("status_severity missing after patch")

    if file_result["failures"]:
        wave_failures.extend(f"{name}: {f}" for f in file_result["failures"])

    results.append(file_result)

passed = not wave_failures

result = {
    "phase": "16U.133",
    "wave_id": "16U-WAVE1",
    "passed": passed,
    "files_attempted": len(files),
    "files_passed": sum(1 for r in results if not r["failures"]),
    "files_failed": sum(1 for r in results if r["failures"]),
    "results": results,
    "wave_failures": wave_failures,
    "phase_16u133_wave1_transactional_patch_complete": passed,
    "next_phase": "16U.134 — Wave 1 Regression",
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.133",
    "WAVE 1 TRANSACTIONAL PATCH",
    "==========================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "",
    f"Files attempted: {len(files)}",
    f"Files passed: {result['files_passed']}",
    f"Files failed: {result['files_failed']}",
    "",
    "FILES",
    "-----",
    *[
        f"- {r['file']} :: {'PASS' if not r['failures'] else 'FAIL'} :: {', '.join(r['applied'])}"
        for r in results
    ],
    "",
    "FAILURES",
    "--------",
    *[f"- {f}" for f in wave_failures],
]), encoding="utf-8")

print(PASS if passed else FAIL)
print("wave_id=16U-WAVE1")
print(f"files_attempted={len(files)}")
print(f"files_passed={result['files_passed']}")
print(f"files_failed={result['files_failed']}")
print(f"backup_dir={BACKUP_DIR.relative_to(ROOT)}")
print("next_phase=16U.134_WAVE1_REGRESSION")

if not passed:
    raise SystemExit(1)
