from pathlib import Path
import json, hashlib, py_compile, re

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

PATCH_JSON = PM / "phase_16u133_wave1_transactional_patch.json"
OUT_JSON = PM / "phase_16u134_wave1_regression.json"
OUT_TXT = PM / "PHASE_16U134_WAVE1_REGRESSION.txt"

PASS = "PASS_PHASE_16U134_WAVE1_REGRESSION"
FAIL = "FAIL_PHASE_16U134_WAVE1_REGRESSION"

legacy_patterns = [
    r'"PASS"\s+if\s+.+?\s+else\s+"FAIL"',
    r"'PASS'\s+if\s+.+?\s+else\s+'FAIL'",
    r'"FAIL"\s+if\s+.+?\s+else\s+"PASS"',
    r"'FAIL'\s+if\s+.+?\s+else\s+'PASS'",
    r'"WARN"\s+if\s+.+?\s+else\s+"PASS"',
    r"'WARN'\s+if\s+.+?\s+else\s+'PASS'",
    r'\.startswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
    r'\.endswith\(\s*["\'](?:PASS|FAIL|WARN|BLOCKED)',
]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compile_ok(path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except Exception as exc:
        return False, str(exc)

def legacy_hits(text):
    hits = []
    lines = text.splitlines()
    for pat in legacy_patterns:
        for m in re.finditer(pat, text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = lines[line_no - 1].strip()
            if line.startswith("#") or "legacy_patterns" in line:
                continue
            hits.append({"line": line_no, "content": line})
    return hits

patch = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
files = patch["results"]

results = []
failures = []

for item in files:
    name = item["file"]
    path = LEAF / name
    backup = ROOT / item["backup"]

    file_failures = []
    if not path.exists():
        file_failures.append("target missing")
    if not backup.exists():
        file_failures.append("backup missing")

    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    ok, err = compile_ok(path) if path.exists() else (False, "missing")

    hits = legacy_hits(text)
    has_lcp = "LegacyCompatibilityProducer" in text
    has_severity = "status_severity" in text
    current_hash = sha256(path) if path.exists() else None

    if not ok:
        file_failures.append(f"compile failed: {err}")
    if not has_lcp:
        file_failures.append("LegacyCompatibilityProducer missing")
    if not has_severity:
        file_failures.append("status_severity missing")
    if hits:
        file_failures.append(f"legacy status hits remain: {len(hits)}")
    if current_hash != item.get("sha256_after"):
        file_failures.append("post-patch hash does not match patch record")
    if current_hash == item.get("sha256_before"):
        file_failures.append("file hash unchanged after patch")

    result = {
        "file": name,
        "passed": not file_failures,
        "compile_ok": ok,
        "has_LegacyCompatibilityProducer": has_lcp,
        "has_status_severity": has_severity,
        "legacy_hit_count": len(hits),
        "legacy_hits": hits,
        "backup_exists": backup.exists(),
        "sha256_before": item.get("sha256_before"),
        "sha256_after_recorded": item.get("sha256_after"),
        "sha256_current": current_hash,
        "failures": file_failures,
    }
    results.append(result)

    for f in file_failures:
        failures.append(f"{name}: {f}")

passed = not failures

out = {
    "phase": "16U.134",
    "wave_id": "16U-WAVE1",
    "passed": passed,
    "files_checked": len(results),
    "files_passed": sum(1 for r in results if r["passed"]),
    "files_failed": sum(1 for r in results if not r["passed"]),
    "results": results,
    "failures": failures,
    "phase_16u134_wave1_regression_complete": passed,
    "next_phase": "16U.135 — Wave 1 Closure Gate",
}

OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

OUT_TXT.write_text("\n".join([
    "LEAF PHASE 16U.134",
    "WAVE 1 REGRESSION",
    "==================",
    "",
    f"STATUS: {PASS if passed else FAIL}",
    "",
    f"Files checked: {len(results)}",
    f"Files passed: {out['files_passed']}",
    f"Files failed: {out['files_failed']}",
    "",
    "FILES",
    "-----",
    *[f"- {r['file']} :: {'PASS' if r['passed'] else 'FAIL'}" for r in results],
    "",
    "FAILURES",
    "--------",
    *[f"- {f}" for f in failures],
]), encoding="utf-8")

print(PASS if passed else FAIL)
print("wave_id=16U-WAVE1")
print(f"files_checked={len(results)}")
print(f"files_passed={out['files_passed']}")
print(f"files_failed={out['files_failed']}")
print("next_phase=16U.135_WAVE1_CLOSURE_GATE")

if not passed:
    raise SystemExit(1)
