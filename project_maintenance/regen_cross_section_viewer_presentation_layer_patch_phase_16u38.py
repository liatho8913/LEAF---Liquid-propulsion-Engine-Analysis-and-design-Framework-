from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.38"
PASS_BANNER = "PASS_PHASE_16U38_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_PATCH"
FAIL_BANNER = "FAIL_PHASE_16U38_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_PATCH"

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "leaf_qt" / "regen_cross_section_viewer.py"

OUT_TXT = ROOT / "project_maintenance" / "REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_PATCH_PHASE_16U38.txt"
OUT_JSON = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_patch_phase_16u38.json"

IMPORT_BLOCK = '''\
try:
    from leaf_qt.status_presentation import (
        LegacyCompatibilityProducer,
        status_severity,
    )
except Exception:
    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value):
            return "PASS" if bool(value) else "FAIL"

    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "MARGINAL" in text or "PARTIAL" in text or "MISSING" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u38_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "MARGINAL" in text or "PARTIAL" in text or "MISSING" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u38_marker_from_bool(value, false_marker="FAIL"):
    try:
        if bool(value):
            return LegacyCompatibilityProducer.marker_from_bool(True)
        return false_marker
    except Exception:
        return "PASS" if bool(value) else false_marker


def _leaf_16u38_is_fail_like(value):
    return _leaf_16u38_status_severity(value) == "FAIL"


def _leaf_16u38_is_pass_like(value):
    return _leaf_16u38_status_severity(value) == "PASS"


def _leaf_16u38_is_warn_like(value):
    return _leaf_16u38_status_severity(value) == "WARN"


def _leaf_16u38_is_blocked_like(value):
    text = str(value or "").upper()
    return _leaf_16u38_status_severity(text) == "FAIL" or "BLOCKED" in text
'''

REPLACEMENTS = [
    (
        '''import math
import os
import json
''',
        '''import math
import os
import json

''' + IMPORT_BLOCK + "\n",
        "insert_shared_status_presentation_import_and_helpers",
    ),
    (
        '''        if severity == "PASS":
            colour = QColor(45, 145, 85)
        elif severity == "FAIL":
            colour = QColor(185, 65, 65)
        else:
            colour = QColor(210, 155, 45)
''',
        '''        severity_role = _leaf_16u38_status_severity(severity)
        if severity_role == "PASS":
            colour = QColor(45, 145, 85)
        elif severity_role == "FAIL":
            colour = QColor(185, 65, 65)
        else:
            colour = QColor(210, 155, 45)
''',
        "migrate_channel_topology_warning_colour_status_interpretation",
    ),
    (
        '''        for passed, title, action in self.canvas.build_source_data_checklist():
            status = "PASS" if passed else "MISSING"
            lines.append(f"{status}: {title}")
''',
        '''        for passed, title, action in self.canvas.build_source_data_checklist():
            status = _leaf_16u38_marker_from_bool(passed, false_marker="MISSING")
            lines.append(f"{status}: {title}")
''',
        "migrate_source_data_checklist_marker_presentation",
    ),
    (
        '''        if "FAIL" in status or "FAIL" in geometry or "FAIL" in thermal or "FAIL" in coolant:
            colour = "#5c1f1f"
            border = "#d46a6a"
''',
        '''        if any(_leaf_16u38_is_fail_like(value) for value in (status, geometry, thermal, coolant)):
            colour = "#5c1f1f"
            border = "#d46a6a"
''',
        "migrate_status_strip_fail_detection",
    ),
    (
        '''        elif "PASS" in status:
            colour = "#1f5c35"
            border = "#6ad487"
''',
        '''        elif _leaf_16u38_is_pass_like(status):
            colour = "#1f5c35"
            border = "#6ad487"
''',
        "migrate_status_strip_pass_detection",
    ),
    (
        '''        if status.startswith("BLOCKED") or status.startswith("FAIL"):
            return False
''',
        '''        if _leaf_16u38_is_blocked_like(status):
            return False
''',
        "migrate_recommended_geometry_blocked_status_detection",
    ),
    (
        '''    blocked = any("FAIL" in status or "BLOCKED" in status for status in blocked_statuses if status)
''',
        '''    blocked = any(_leaf_16u38_is_blocked_like(status) for status in blocked_statuses if status)
''',
        "migrate_geometry_decision_blocked_status_detection",
    ),
    (
        '''        and not recommended_status.upper().startswith(("BLOCKED", "FAIL"))
''',
        '''        and not _leaf_16u38_is_blocked_like(recommended_status)
''',
        "migrate_recommended_available_blocked_status_detection",
    ),
    (
        '''        and not best_status.upper().startswith(("FAIL", "BLOCKED"))
''',
        '''        and not _leaf_16u38_is_blocked_like(best_status)
''',
        "migrate_automatic_available_blocked_status_detection",
    ),
    (
        '''                    if str(status).startswith("PASS"):
                        label.setText("REGEN VIEWER RUNTIME SIGNOFF: PASS")
                    else:
                        label.setText("REGEN VIEWER RUNTIME SIGNOFF: FAIL")
''',
        '''                    marker = _leaf_16u38_marker_from_bool(
                        _leaf_16u38_is_pass_like(status),
                        false_marker="FAIL",
                    )
                    label.setText(f"REGEN VIEWER RUNTIME SIGNOFF: {marker}")
''',
        "migrate_runtime_signoff_label_marker_presentation",
    ),
    (
        '''hard_failures = {
        key: value
        for key, value in status_map.items()
        if "FAIL" in str(value).upper() or "BLOCKED" in str(value).upper()
    }''',
        '''hard_failures = {
        key: value
        for key, value in status_map.items()
        if _leaf_16u38_is_blocked_like(value)
    }''',
        "migrate_hard_failure_status_collection",
    ),
    (
        '''        if "WARN" in str(value).upper()
        or "PARTIAL" in str(value).upper()
        or "MISSING" in str(value).upper()
''',
        '''        if _leaf_16u38_is_warn_like(value)
''',
        "migrate_warning_status_collection",
    ),
]


def compile_target() -> tuple[bool, str]:
    try:
        py_compile.compile(str(TARGET), doraise=True)
        return True, ""
    except Exception as exc:
        return False, repr(exc)


def main() -> dict:
    if not TARGET.exists():
        result = {
            "phase": PHASE,
            "status": FAIL_BANNER,
            "target": str(TARGET.relative_to(ROOT)),
            "error": "target file missing",
            "applied": [],
            "already_applied": [],
            "missing": [],
            "phase_16u38_regen_cross_section_viewer_presentation_layer_patch_complete": False,
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        OUT_TXT.write_text("PHASE 16U.38 FAILED: target file missing.\n", encoding="utf-8")
        return result

    original = TARGET.read_text(encoding="utf-8", errors="replace")
    text = original

    applied = []
    already_applied = []
    missing = []

    backup = TARGET.with_suffix(".py.phase_16u38_backup")
    if not backup.exists():
        backup.write_text(original, encoding="utf-8")

    for old, new, name in REPLACEMENTS:
        if new in text:
            already_applied.append(name)
            continue

        if old in text:
            text = text.replace(old, new, 1)
            applied.append(name)
        else:
            missing.append(name)

    changed = text != original
    if changed:
        TARGET.write_text(text, encoding="utf-8")

    compiled, compile_error = compile_target()

    required_tokens = [
        "from leaf_qt.status_presentation import",
        "LegacyCompatibilityProducer",
        "status_severity",
        "_leaf_16u38_status_severity",
        "_leaf_16u38_marker_from_bool",
        "_leaf_16u38_is_blocked_like",
    ]

    final_text = TARGET.read_text(encoding="utf-8", errors="replace")
    missing_tokens = [token for token in required_tokens if token not in final_text]

    passed = compiled and not missing_tokens and not missing

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET.relative_to(ROOT)),
        "backup": str(backup.relative_to(ROOT)),
        "changed": changed,
        "applied": applied,
        "already_applied": already_applied,
        "missing": missing,
        "compiled": compiled,
        "compile_error": compile_error,
        "missing_tokens": missing_tokens,
        "phase_16u38_regen_cross_section_viewer_presentation_layer_patch_complete": passed,
        "next_phase": "16U.39 — First Report Owner Presentation Layer Rollout Regression",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.38",
        "REGEN CROSS SECTION VIEWER PRESENTATION LAYER PATCH",
        "===================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "First wider report-owner/UI presentation-layer rollout patch.",
        "",
        "TARGET",
        "------",
        result["target"],
        "",
        "PATCH ACCOUNTING",
        "----------------",
        f"Changed: {changed}",
        f"Applied: {len(applied)}",
        f"Already applied: {len(already_applied)}",
        f"Missing expected anchors: {len(missing)}",
        "",
        "APPLIED",
        "-------",
        *applied,
        "",
        "ALREADY APPLIED",
        "---------------",
        *already_applied,
        "",
        "MISSING",
        "-------",
        *missing,
        "",
        "COMPILE",
        "-------",
        f"Compiled: {compiled}",
        f"Compile error: {compile_error}",
        "",
        "COMPLETION NOTICE",
        "-----------------",
        "PHASE 16U.38 COMPLETE." if passed else "PHASE 16U.38 FAILED.",
        "",
        "NEXT FEATURE",
        "------------",
        "PHASE 16U.39 — FIRST REPORT OWNER PRESENTATION LAYER ROLLOUT REGRESSION",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target={result['target']}")
    print(f"changed={result['changed']}")
    print(f"applied={len(result['applied'])}")
    print(f"already_applied={len(result['already_applied'])}")
    print(f"missing={len(result['missing'])}")
    print(f"compiled={result['compiled']}")
    if result["missing"]:
        print("missing_items:")
        for item in result["missing"]:
            print(f"- {item}")
    if result["compile_error"]:
        print(result["compile_error"])
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u38_regen_cross_section_viewer_presentation_layer_patch_complete"]:
        raise SystemExit(1)
