from pathlib import Path

path = Path("leaf_qt/foundation_result_key_audit.py")

text = path.read_text()

old = '"regen_completion_audit_": "VALIDATION_ONLY",'
new = '"regen_completion_audit_": "DIAGNOSTIC_ONLY",'

if old not in text:
    print("RULE NOT FOUND")
    raise SystemExit(1)

text = text.replace(old, new)

path.write_text(text)

print("REGEN_COMPLETION_AUDIT_VISIBILITY_RULE_FIXED")
