from pathlib import Path
import ast
import re

SOURCE = Path("leaf_qt/regen_cross_section_viewer.py")

STATUS_ASSIGN_RE = re.compile(r'''results\[['"]([^'"]*status[^'"]*)['"]\]\s*=''')
SELF_STATUS_ASSIGN_RE = re.compile(r'''self\.results\[['"]([^'"]*status[^'"]*)['"]\]\s*=''')
STATUS_GET_RE = re.compile(r'''(?:results|self\.results)\.get\(['"]([^'"]*status[^'"]*)['"]''')


def main():
    if not SOURCE.exists():
        raise SystemExit("FAIL_PHASE_16T3W5A_VIEWER_FILE_MISSING")

    text = SOURCE.read_text(errors="replace")
    tree = ast.parse(text)

    public_classes = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    ]

    public_functions = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]

    status_assignments = sorted(set(
        STATUS_ASSIGN_RE.findall(text)
        + SELF_STATUS_ASSIGN_RE.findall(text)
    ))

    status_reads = sorted(set(STATUS_GET_RE.findall(text)))

    phase_status_keys = sorted(
        key for key in status_assignments
        if key.startswith("phase_")
    )

    viewer_status_keys = sorted(
        key for key in status_assignments
        if key.startswith("viewer_") or key.startswith("regen_viewer_")
    )

    regen_status_keys = sorted(
        key for key in status_assignments
        if key.startswith("regen_")
    )

    print("LEAF PHASE 16T.3W.5A")
    print("REGEN CROSS SECTION VIEWER STATUS ARCHITECTURE AUDIT")
    print("====================================================")
    print()
    print(f"source_exists: {SOURCE.exists()}")
    print(f"line_count: {len(text.splitlines())}")
    print(f"public_class_count: {len(public_classes)}")
    print(f"public_function_count: {len(public_functions)}")
    print(f"legacy_PASS_count: {text.count('PASS')}")
    print(f"legacy_WARN_count: {text.count('WARN')}")
    print(f"legacy_FAIL_count: {text.count('FAIL')}")
    print(f"structured_already_present: {'structured_findings' in text}")
    print(f"global_status_already_present: {'global_status' in text}")
    print(f"phase_16t3w5_already_present: {'phase_16t3w5' in text}")
    print()
    print("PUBLIC_CLASSES:")
    for name in public_classes:
        print(f"- {name}")
    print()
    print("PUBLIC_FUNCTIONS:")
    for name in public_functions:
        print(f"- {name}")
    print()
    print(f"status_assignment_key_count: {len(status_assignments)}")
    print(f"status_read_key_count: {len(status_reads)}")
    print(f"phase_status_key_count: {len(phase_status_keys)}")
    print(f"viewer_status_key_count: {len(viewer_status_keys)}")
    print(f"regen_status_key_count: {len(regen_status_keys)}")
    print()
    print("PHASE_STATUS_KEYS:")
    for key in phase_status_keys:
        print(f"- {key}")
    print()
    print("VIEWER_STATUS_KEYS:")
    for key in viewer_status_keys:
        print(f"- {key}")
    print()
    print("REGEN_STATUS_KEYS:")
    for key in regen_status_keys:
        print(f"- {key}")
    print()

    blocked = False

    if "RegenCrossSectionViewer" not in public_classes:
        print("BLOCKER: RegenCrossSectionViewer public class missing")
        blocked = True

    if "RegenCrossSectionCanvas" not in public_classes:
        print("BLOCKER: RegenCrossSectionCanvas public class missing")
        blocked = True

    if "phase_16t3w5" in text:
        print("AUDIT_RESULT: PHASE_ALREADY_PRESENT")
    elif blocked:
        print("AUDIT_RESULT: BLOCKED")
        raise SystemExit("FAIL_PHASE_16T3W5A_VIEWER_STATUS_ARCHITECTURE_AUDIT")
    else:
        print("AUDIT_RESULT: VIEWER_STATUS_ARCHITECTURE_MAPPED")
        print("NEXT_ACTION: APPLY_MINIMAL_VIEWER_ADAPTER_METHODS")

    print("PASS_PHASE_16T3W5A_REGEN_CROSS_SECTION_VIEWER_STATUS_ARCHITECTURE_AUDIT")


if __name__ == "__main__":
    main()
