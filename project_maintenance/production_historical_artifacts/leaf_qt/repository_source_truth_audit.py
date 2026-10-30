from __future__ import annotations

from core.architecture.repository_metadata import iter_supported_files
from pathlib import Path
from typing import Any

from core.architecture.io import write_json_artifact, write_text_artifact


DEFAULT_SUSPICIOUS_ROOT_NAMES = {
    "LEAF_UPLOAD",
    "LEAF_Minimal_Source",
    "LEAF_Regen_Only",
    "LEAF_Source",
    "backup",
    "backups",
    "exports",
    "dist",
    "build",
}


def _count_python_files(path: Path) -> int:
    """Count current Python source files inside exactly this directory."""
    if not path.exists() or not path.is_dir():
        return 0

    return sum(
        1
        for item in iter_supported_files(path)
        if item.suffix.lower() == ".py"
    )


def _has_source_shape(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False

    indicators = [
        path / "leaf_qt",
        path / "main.py",
        path / "requirements.txt",
        path / "pyproject.toml",
    ]

    return any(item.exists() for item in indicators)


def build_repository_source_truth_audit(
    root: str | Path = ".",
    suspicious_root_names: set[str] | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    suspicious = suspicious_root_names or DEFAULT_SUSPICIOUS_ROOT_NAMES

    findings: list[dict[str, Any]] = []

    for child in sorted(root_path.iterdir()):
        if not child.is_dir():
            continue

        if child.name in suspicious:
            py_count = _count_python_files(child)
            findings.append(
                {
                    "path": child.relative_to(root_path).as_posix(),
                    "kind": "SUSPICIOUS_ROOT",
                    "python_files": py_count,
                    "has_source_shape": _has_source_shape(child),
                    "recommended_action": (
                        "MOVE_OUTSIDE_REPOSITORY_OR_ARCHIVE"
                        if py_count or _has_source_shape(child)
                        else "IGNORE_EMPTY_OR_NON_SOURCE_DIRECTORY"
                    ),
                }
            )

    project_maintenance = root_path / "project_maintenance"
    if project_maintenance.exists():
        for child in sorted(project_maintenance.iterdir()):
            if not child.is_dir():
                continue
            lowered = child.name.lower()
            if "backup" in lowered or "archive" in lowered:
                py_count = _count_python_files(child)
                findings.append(
                    {
                        "path": child.relative_to(root_path).as_posix(),
                        "kind": "MAINTENANCE_BACKUP_OR_ARCHIVE",
                        "python_files": py_count,
                        "has_source_shape": _has_source_shape(child),
                        "recommended_action": "KEEP_OUT_OF_RUNTIME_INDEX_AND_REVIEW_FOR_EXTERNAL_ARCHIVE",
                    }
                )

    blocking_findings = [
        item for item in findings
        if item["recommended_action"] in {
            "MOVE_OUTSIDE_REPOSITORY_OR_ARCHIVE",
            "KEEP_OUT_OF_RUNTIME_INDEX_AND_REVIEW_FOR_EXTERNAL_ARCHIVE",
        }
        and item["python_files"] > 0
    ]

    return {
        "schema": "LEAF_REPOSITORY_SOURCE_TRUTH_AUDIT_V1",
        "root": str(root_path),
        "summary": {
            "findings": len(findings),
            "blocking_findings": len(blocking_findings),
            "suspicious_python_files": sum(item["python_files"] for item in findings),
        },
        "findings": findings,
        "blocking_findings": blocking_findings,
        "passed": len(blocking_findings) == 0,
        "note": (
            "This audit does not move files. It identifies duplicate source trees, "
            "packaged uploads, generated exports, and backup code that should not be "
            "treated as authoritative live source."
        ),
    }


def build_text_report(audit: dict[str, Any]) -> str:
    summary = audit["summary"]

    lines = [
        "LEAF REPOSITORY SOURCE TRUTH AUDIT",
        "==================================",
        f"schema={audit['schema']}",
        f"passed={audit['passed']}",
        f"findings={summary['findings']}",
        f"blocking_findings={summary['blocking_findings']}",
        f"suspicious_python_files={summary['suspicious_python_files']}",
        "",
        "FINDINGS",
        "--------",
    ]

    if not audit["findings"]:
        lines.append("No suspicious source roots found.")
    else:
        for item in audit["findings"]:
            lines.append(
                f"{item['kind']} | "
                f"python_files={item['python_files']} | "
                f"source_shape={item['has_source_shape']} | "
                f"action={item['recommended_action']} | "
                f"{item['path']}"
            )

    return "\n".join(lines)


def write_repository_source_truth_audit(
    root: str | Path = ".",
    json_path: str | Path = "artifacts/repository_source_truth_audit.json",
    txt_path: str | Path = "artifacts/repository_source_truth_audit.txt",
) -> dict[str, Any]:
    audit = build_repository_source_truth_audit(root)

    out_json = Path(json_path)
    out_txt = Path(txt_path)

    write_json_artifact(audit, out_json)
    write_text_artifact(build_text_report(audit), out_txt)

    return audit


if __name__ == "__main__":
    result = write_repository_source_truth_audit(".")
    print(build_text_report(result))
    print("")
    print("json=artifacts/repository_source_truth_audit.json")
    print("txt=artifacts/repository_source_truth_audit.txt")

    if result["passed"]:
        print("PASS_REPOSITORY_SOURCE_TRUTH_AUDIT")
    else:
        print("FAIL_REPOSITORY_SOURCE_TRUTH_AUDIT")
        raise SystemExit(1)
