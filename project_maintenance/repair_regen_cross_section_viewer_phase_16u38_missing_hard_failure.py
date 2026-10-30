from pathlib import Path
import re
import py_compile

target = Path("leaf_qt/regen_cross_section_viewer.py")
text = target.read_text(encoding="utf-8", errors="replace")

original = text

pattern = re.compile(
    r'''hard_failures\s*=\s*\{\s*
\s*key:\s*value\s*
\s*for\s+key,\s*value\s+in\s+status_map\.items\(\)\s*
\s*if\s+"FAIL"\s+in\s+str\(value\)\.upper\(\)\s+or\s+"BLOCKED"\s+in\s+str\(value\)\.upper\(\)\s*
\s*\}''',
    re.MULTILINE,
)

replacement = '''hard_failures = {
        key: value
        for key, value in status_map.items()
        if _leaf_16u38_is_blocked_like(value)
    }'''

text, count = pattern.subn(replacement, text, count=1)

if count == 0:
    print("NO_MATCH_FOUND_FOR_HARD_FAILURE_BLOCK")
else:
    target.write_text(text, encoding="utf-8")
    print("PATCHED_HARD_FAILURE_BLOCK_PHASE_16U38")

py_compile.compile(str(target), doraise=True)
print("COMPILE_PASS")
