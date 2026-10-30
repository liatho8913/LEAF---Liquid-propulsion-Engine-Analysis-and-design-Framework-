from pathlib import Path
import ast, re, subprocess, sys, json

ROOT = Path(".").resolve()
PY_FILES = sorted(p for p in ROOT.rglob("*.py") if ".venv" not in str(p) and "__pycache__" not in str(p))

report = []
summary = {
    "total_py_files": len(PY_FILES),
    "syntax_errors": 0,
    "import_warnings": 0,
    "large_files": 0,
    "todo_count": 0,
    "phase_markers": {},
    "tests": [],
}

def add(title, lines):
    report.append("\n" + "="*80)
    report.append(title)
    report.append("="*80)
    report.extend(lines)

syntax_lines = []
import_lines = []
todo_lines = []
large_lines = []
class_func_lines = []
phase_lines = []

for path in PY_FILES:
    rel = path.relative_to(ROOT)
    text = path.read_text(errors="ignore")
    lines = text.splitlines()

    if len(lines) > 1200:
        summary["large_files"] += 1
        large_lines.append(f"{rel}: {len(lines)} lines")

    for i, line in enumerate(lines, 1):
        if "TODO" in line or "FIXME" in line or "pass  # TODO" in line:
            summary["todo_count"] += 1
            todo_lines.append(f"{rel}:{i}: {line.strip()}")

    try:
        tree = ast.parse(text, filename=str(rel))
    except SyntaxError as e:
        summary["syntax_errors"] += 1
        syntax_lines.append(f"{rel}: SyntaxError line {e.lineno}: {e.msg}")
        continue

    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    class_func_lines.append(
        f"{rel}: classes={len(classes)} funcs={len(funcs)}"
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("leaf_qt."):
                continue
            if node.level == 0 and node.module and node.module in {
                "calculation_bridge", "engine_solver", "leaf_data",
                "variable_registry", "foundation_attachment_pipeline"
            }:
                summary["import_warnings"] += 1
                import_lines.append(
                    f"{rel}: absolute local import from {node.module}"
                )

    for match in re.findall(r"PHASE[_\-\s]*([0-9A-Z\.]+)|POST-16[A-Z0-9\.]*|PASS_[A-Z0-9_]+", text):
        pass

    for marker in re.findall(r"(POST-16[A-Z0-9\.]*|PHASE[_\-\s]*[0-9A-Z\.]+|PASS_[A-Z0-9_]+)", text):
        summary["phase_markers"][marker] = summary["phase_markers"].get(marker, 0) + 1

    if rel.name.startswith("test_") or "/test_" in str(rel):
        summary["tests"].append(str(rel))

add("LEAF FULL PYTHON AUDIT SUMMARY", [
    f"Root: {ROOT}",
    f"Python files scanned: {summary['total_py_files']}",
    f"Syntax errors: {summary['syntax_errors']}",
    f"Local import warnings: {summary['import_warnings']}",
    f"Large files over 1200 lines: {summary['large_files']}",
    f"TODO/FIXME count: {summary['todo_count']}",
    f"Test files discovered: {len(summary['tests'])}",
])

add("SYNTAX ERRORS", syntax_lines or ["None"])
add("LOCAL IMPORT WARNINGS", import_lines or ["None"])
add("LARGE FILES", large_lines or ["None"])
add("TODO / FIXME ITEMS", todo_lines[:300] or ["None"])
add("CLASS / FUNCTION COUNTS", class_func_lines)
add("TEST FILES", summary["tests"] or ["None"])

phase_sorted = sorted(summary["phase_markers"].items(), key=lambda x: (-x[1], x[0]))
add("PHASE / PASS MARKERS", [f"{k}: {v}" for k, v in phase_sorted[:500]])

# Compile all files
compile_lines = []
for path in PY_FILES:
    rel = path.relative_to(ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        compile_lines.append(f"{rel} FAILED\n{result.stderr.strip()}")

add("PY_COMPILE RESULTS", compile_lines or ["All files compiled successfully."])

out = ROOT / "LEAF_FULL_PY_AUDIT_REPORT.txt"
out.write_text("\n".join(report))

json_out = ROOT / "LEAF_FULL_PY_AUDIT_SUMMARY.json"
json_out.write_text(json.dumps(summary, indent=2))

print("LEAF_FULL_PY_AUDIT_COMPLETE")
print(f"Report: {out}")
print(f"Summary JSON: {json_out}")
print()
print("\n".join(report[:80]))
