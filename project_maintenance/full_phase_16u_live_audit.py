from pathlib import Path
import json, re, py_compile

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"
PM = ROOT / "project_maintenance"

BASELINE = PM / "phase_16u126b_locked_migration_scope_baseline.json"
OUT_JSON = PM / "FULL_PHASE_16U_LIVE_AUDIT.json"
OUT_TXT = PM / "FULL_PHASE_16U_LIVE_AUDIT.txt"

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

def legacy_hits(text):
    hits = []
    lines = text.splitlines()
    for pat in legacy_patterns:
        for m in re.finditer(pat, text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = lines[line_no - 1].strip() if line_no <= len(lines) else ""
            if line.startswith("#"):
                continue
            if "legacy_patterns" in line:
                continue
            hits.append({"line": line_no, "pattern": pat, "content": line})
    return hits

def compile_ok(path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except Exception as exc:
        return False, str(exc)

if not BASELINE.exists():
    raise SystemExit("FAIL: missing locked baseline phase_16u126b_locked_migration_scope_baseline.json")

baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
scope = sorted(set(baseline["baseline_scope"]))

closed = []
remaining = []
details = []
compile_failures = []

for name in scope:
    p = LEAF / name
    if not p.exists():
        remaining.append(name)
        details.append({"file": name, "status": "MISSING"})
        continue

    text = p.read_text(encoding="utf-8", errors="replace")
    ok, err = compile_ok(p)
    if not ok:
        compile_failures.append({"file": name, "error": err})

    hits = legacy_hits(text)
    has_lcp = "LegacyCompatibilityProducer" in text
    has_severity = "status_severity" in text

    migrated = ok and has_lcp and has_severity and not hits

    if migrated:
        closed.append(name)
        status = "CLOSED"
    else:
        remaining.append(name)
        status = "REMAINING"

    details.append({
        "file": name,
        "status": status,
        "compile_ok": ok,
        "has_LegacyCompatibilityProducer": has_lcp,
        "has_status_severity": has_severity,
        "legacy_hit_count": len(hits),
        "legacy_hits": hits[:10],
    })

json_files = sorted(PM.glob("*.json"))
phase_evidence = []
for jf in json_files:
    try:
        data = json.loads(jf.read_text(encoding="utf-8"))
    except Exception:
        continue
    phase = data.get("phase")
    target = data.get("target") or data.get("closed_target") or data.get("selected_file")
    passed = data.get("passed")
    complete_flags = [k for k, v in data.items() if k.endswith("_complete") and v is True]
    if phase or target or complete_flags:
        phase_evidence.append({
            "file": jf.name,
            "phase": phase,
            "target": target,
            "passed": passed,
            "complete_flags": complete_flags,
        })

result = {
    "audit": "FULL_PHASE_16U_LIVE_AUDIT",
    "locked_baseline": len(scope),
    "closed_targets": len(closed),
    "remaining_candidates": len(remaining),
    "progress": f"{len(closed)}/{len(scope)}",
    "closed_files": closed,
    "remaining_files": remaining,
    "compile_failures": compile_failures,
    "details": details,
    "phase_evidence_count": len(phase_evidence),
    "phase_evidence": phase_evidence,
}

OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

lines = [
    "FULL PHASE 16U LIVE AUDIT",
    "=========================",
    "",
    "SOURCE OF TRUTH",
    "---------------",
    "This audit uses the locked Phase 16U baseline, not a moving dynamic scope.",
    "",
    f"Locked baseline: {len(scope)}",
    f"Closed targets: {len(closed)}",
    f"Remaining candidates: {len(remaining)}",
    f"Progress: {len(closed)}/{len(scope)}",
    "",
    "COMPILE FAILURES",
    "----------------",
]

if compile_failures:
    lines.extend(f"- {x['file']}: {x['error']}" for x in compile_failures)
else:
    lines.append("None")

lines += [
    "",
    "CLOSED FILES",
    "------------",
    *[f"- {x}" for x in closed],
    "",
    "REMAINING FILES",
    "---------------",
]

for name in remaining:
    item = next(d for d in details if d["file"] == name)
    reasons = []
    if not item.get("compile_ok", False):
        reasons.append("compile_fail")
    if not item.get("has_LegacyCompatibilityProducer", False):
        reasons.append("missing_LegacyCompatibilityProducer")
    if not item.get("has_status_severity", False):
        reasons.append("missing_status_severity")
    if item.get("legacy_hit_count", 0):
        reasons.append(f"legacy_hits={item['legacy_hit_count']}")
    lines.append(f"- {name} [{', '.join(reasons) if reasons else 'needs_review'}]")
    for hit in item.get("legacy_hits", [])[:3]:
        lines.append(f"    line {hit['line']}: {hit['content']}")

lines += [
    "",
    "PHASE EVIDENCE COUNT",
    "--------------------",
    str(len(phase_evidence)),
    "",
    "OUTPUT FILES",
    "------------",
    str(OUT_TXT.relative_to(ROOT)),
    str(OUT_JSON.relative_to(ROOT)),
]

OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print("PASS_FULL_PHASE_16U_LIVE_AUDIT")
print(f"locked_baseline={len(scope)}")
print(f"closed_targets={len(closed)}")
print(f"remaining_candidates={len(remaining)}")
print(f"progress={len(closed)}/{len(scope)}")
print(f"compile_failures={len(compile_failures)}")
print(f"report={OUT_TXT.relative_to(ROOT)}")
print(f"json={OUT_JSON.relative_to(ROOT)}")
