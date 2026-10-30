from pathlib import Path
import re
import py_compile

target = Path("leaf_qt/regen_scalability_failure_owner.py")
s = target.read_text(encoding="utf-8", errors="replace")

helper_pattern = re.compile(
    r'\ntry:\n'
    r'    from leaf_qt\.status_presentation import status_severity\n'
    r'except Exception:\n'
    r'    def status_severity\(value\):\n'
    r'(?:        .*\n)+?'
    r'\n\ndef _leaf_16u42_status_severity\(value\):\n'
    r'(?:    .*\n)+?'
    r'\n\ndef _leaf_16u42_is_fail_like\(value\):\n'
    r'    return _leaf_16u42_status_severity\(value\) == "FAIL"\n'
    r'\n\ndef _leaf_16u42_is_warn_like\(value\):\n'
    r'    return _leaf_16u42_status_severity\(value\) == "WARN"\n'
    r'\n\ndef _leaf_16u42_is_pass_like\(value\):\n'
    r'    return _leaf_16u42_status_severity\(value\) == "PASS"\n',
    re.MULTILINE,
)

helper_block = '''
try:
    from leaf_qt.status_presentation import status_severity
except Exception:
    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u42_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u42_is_fail_like(value):
    return _leaf_16u42_status_severity(value) == "FAIL"


def _leaf_16u42_is_warn_like(value):
    return _leaf_16u42_status_severity(value) == "WARN"


def _leaf_16u42_is_pass_like(value):
    return _leaf_16u42_status_severity(value) == "PASS"
'''

s, removed = helper_pattern.subn("\n", s)

lines = s.splitlines()
insert_at = 0
for i, line in enumerate(lines):
    if line.startswith("import ") or line.startswith("from "):
        insert_at = i + 1

lines = lines[:insert_at] + [helper_block] + lines[insert_at:]
s = "\n".join(lines) + "\n"

target.write_text(s, encoding="utf-8")
py_compile.compile(str(target), doraise=True)

print("REPAIRED_16U42_HELPER_SCOPE")
print(f"removed_helper_blocks={removed}")
print("COMPILE_PASS")
