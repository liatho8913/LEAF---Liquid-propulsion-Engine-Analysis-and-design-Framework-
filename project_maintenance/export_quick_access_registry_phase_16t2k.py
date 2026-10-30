from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


PHASE = "16T.2K"

PASS_STATUS = "PASS_EXPORT_QUICK_ACCESS_REGISTRY_PHASE_16T2K"
FAIL_STATUS = "FAIL_EXPORT_QUICK_ACCESS_REGISTRY_PHASE_16T2K"

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "_leaf_artifacts" / "exports"
REGISTRY_DIR = ROOT / "_leaf_artifacts" / "exports" / "_registry"
REGISTRY_PATH = REGISTRY_DIR / "export_quick_access_registry.json"

EXPORT_CATEGORIES = (
    "reports",
    "audits",
    "graphs",
    "station_tables",
    "regen",
    "geometry",
    "packaging",
    "snapshots",
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_registry_architecture() -> dict[str, Any]:
    created = []
    existing = []

    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)

    for category in EXPORT_CATEGORIES:
        path = EXPORT_ROOT / category
        if path.exists():
            existing.append(str(path.relative_to(ROOT)))
        else:
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path.relative_to(ROOT)))

    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text(json.dumps({"exports": []}, indent=2), encoding="utf-8")
        created.append(str(REGISTRY_PATH.relative_to(ROOT)))

    missing = [
        category for category in EXPORT_CATEGORIES
        if not (EXPORT_ROOT / category).is_dir()
    ]

    if not REGISTRY_PATH.is_file():
        missing.append(str(REGISTRY_PATH.relative_to(ROOT)))

    status = FAIL_STATUS if missing else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not missing,
        "created": created,
        "existing": existing,
        "missing": missing,
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "summary": f"{len(EXPORT_CATEGORIES)} export categories and quick-access registry verified.",
    }


def load_registry() -> dict[str, Any]:
    ensure_registry_architecture()

    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = {"exports": []}

    if not isinstance(data, dict):
        data = {"exports": []}

    if not isinstance(data.get("exports"), list):
        data["exports"] = []

    return data


def save_registry(data: dict[str, Any]) -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def register_export(
    path: str | Path,
    category: str,
    label: str,
    export_type: str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    ensure_registry_architecture()

    p = Path(path)

    if p.is_absolute():
        rel = p.relative_to(ROOT).as_posix() if p.exists() and ROOT in p.parents else p.as_posix()
    else:
        rel = p.as_posix()

    record = {
        "timestamp": now_iso(),
        "category": category,
        "label": label,
        "path": rel,
        "filename": Path(rel).name,
        "extension": Path(rel).suffix,
        "export_type": export_type or Path(rel).suffix.replace(".", "").upper() or "UNKNOWN",
        "source": source or "manual_registration",
        "exists": (ROOT / rel).exists() if not Path(rel).is_absolute() else Path(rel).exists(),
    }

    data = load_registry()
    data["exports"].append(record)
    data["exports"] = data["exports"][-250:]
    save_registry(data)

    return record


def recent_exports(limit: int = 20, category: str | None = None) -> list[dict[str, Any]]:
    data = load_registry()
    exports = data.get("exports", [])

    if category:
        exports = [item for item in exports if item.get("category") == category]

    return list(reversed(exports[-limit:]))


def build_export_quick_access_report() -> str:
    audit = ensure_registry_architecture()
    data = load_registry()
    recent = recent_exports(20)

    lines = [
        "EXPORT QUICK ACCESS REGISTRY",
        "============================",
        f"Phase: {PHASE}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        f"Registry: {audit['registry_path']}",
        "",
        "EXPORT CATEGORIES",
        "-----------------",
    ]

    for category in EXPORT_CATEGORIES:
        lines.append(f"- {category}: {(EXPORT_ROOT / category).relative_to(ROOT).as_posix()}")

    lines.extend([
        "",
        "RECENT EXPORTS",
        "--------------",
    ])

    if recent:
        for item in recent:
            lines.append(
                f"- {item.get('timestamp')} | {item.get('category')} | "
                f"{item.get('label')} | {item.get('path')}"
            )
    else:
        lines.append("- No exports registered yet.")

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only creates and updates the export registry. It does not delete or move existing exports.",
    ])

    return "\n".join(lines)


def write_export_quick_access_report() -> Path:
    ensure_registry_architecture()
    report_path = EXPORT_ROOT / "audits" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}__EXPORT_QUICK_ACCESS_REGISTRY_PHASE_16T2K.txt"
    report_path.write_text(build_export_quick_access_report(), encoding="utf-8")
    register_export(
        report_path,
        category="audits",
        label="Export Quick Access Registry Report",
        export_type="TXT",
        source=PHASE,
    )
    return report_path


if __name__ == "__main__":
    report = write_export_quick_access_report()
    audit = ensure_registry_architecture()
    print(audit["status"])
    print(report)
