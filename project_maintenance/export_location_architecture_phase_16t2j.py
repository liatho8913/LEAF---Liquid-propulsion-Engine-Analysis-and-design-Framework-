from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


PHASE = "16T.2J"

PASS_STATUS = "PASS_EXPORT_LOCATION_ARCHITECTURE_PHASE_16T2J"
FAIL_STATUS = "FAIL_EXPORT_LOCATION_ARCHITECTURE_PHASE_16T2J"

ROOT = Path(__file__).resolve().parents[1]

EXPORT_ROOT = ROOT / "_leaf_artifacts" / "exports"

EXPORT_CATEGORIES = {
    "reports": EXPORT_ROOT / "reports",
    "audits": EXPORT_ROOT / "audits",
    "graphs": EXPORT_ROOT / "graphs",
    "station_tables": EXPORT_ROOT / "station_tables",
    "regen": EXPORT_ROOT / "regen",
    "geometry": EXPORT_ROOT / "geometry",
    "packaging": EXPORT_ROOT / "packaging",
    "snapshots": EXPORT_ROOT / "snapshots",
}


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_label(label: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in str(label).strip())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    return cleaned or "LEAF_EXPORT"


def ensure_export_architecture() -> dict[str, Any]:
    created = []
    existing = []

    for key, folder in EXPORT_CATEGORIES.items():
        if folder.exists():
            existing.append(str(folder.relative_to(ROOT)))
        else:
            folder.mkdir(parents=True, exist_ok=True)
            created.append(str(folder.relative_to(ROOT)))

    missing = [
        key for key, folder in EXPORT_CATEGORIES.items()
        if not folder.is_dir()
    ]

    status = FAIL_STATUS if missing else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not missing,
        "export_root": str(EXPORT_ROOT.relative_to(ROOT)),
        "created": created,
        "existing": existing,
        "missing": missing,
        "categories": {key: str(path.relative_to(ROOT)) for key, path in EXPORT_CATEGORIES.items()},
        "summary": f"{len(EXPORT_CATEGORIES)} export categories verified under _leaf_artifacts/exports.",
    }


def export_path(category: str, label: str, extension: str) -> Path:
    ensure_export_architecture()

    if category not in EXPORT_CATEGORIES:
        raise ValueError(f"Unknown export category: {category}")

    ext = extension if extension.startswith(".") else f".{extension}"
    name = f"{timestamp()}__{safe_label(label)}{ext}"

    return EXPORT_CATEGORIES[category] / name


def write_text_export(category: str, label: str, text: str, extension: str = ".txt") -> Path:
    path = export_path(category, label, extension)
    path.write_text(text, encoding="utf-8")
    return path


def build_export_architecture_report() -> str:
    audit = ensure_export_architecture()

    lines = [
        "EXPORT LOCATION ARCHITECTURE",
        "============================",
        f"Phase: {audit['phase']}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "EXPORT ROOT",
        "-----------",
        audit["export_root"],
        "",
        "EXPORT CATEGORIES",
        "-----------------",
    ]

    for key, path in audit["categories"].items():
        lines.append(f"- {key}: {path}")

    lines.extend([
        "",
        "FILENAME RULE",
        "-------------",
        "YYYYMMDD_HHMMSS__Human_Readable_Label.ext",
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only creates export folders and path helpers. It does not delete or move existing files.",
    ])

    return "\n".join(lines)


def write_export_architecture_report() -> Path:
    ensure_export_architecture()
    path = EXPORT_CATEGORIES["audits"] / f"{timestamp()}__EXPORT_LOCATION_ARCHITECTURE_PHASE_16T2J.txt"
    path.write_text(build_export_architecture_report(), encoding="utf-8")
    return path


if __name__ == "__main__":
    report = write_export_architecture_report()
    audit = ensure_export_architecture()
    print(audit["status"])
    print(report)
