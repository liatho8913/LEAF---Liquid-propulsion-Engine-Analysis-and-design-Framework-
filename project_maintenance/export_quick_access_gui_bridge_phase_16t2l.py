from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from project_maintenance.export_quick_access_registry_phase_16t2k import (
    ROOT,
    EXPORT_ROOT,
    EXPORT_CATEGORIES,
    ensure_registry_architecture,
    recent_exports,
)


PHASE = "16T.2L"

PASS_STATUS = "PASS_EXPORT_QUICK_ACCESS_GUI_BRIDGE_PHASE_16T2L"
FAIL_STATUS = "FAIL_EXPORT_QUICK_ACCESS_GUI_BRIDGE_PHASE_16T2L"

CATEGORY_LABELS = {
    "reports": "Reports",
    "audits": "Audits",
    "graphs": "Graphs",
    "station_tables": "Station Tables",
    "regen": "Regenerative Cooling",
    "geometry": "Geometry",
    "packaging": "Packaging",
    "snapshots": "Snapshots",
}


def export_category_rows() -> list[dict[str, Any]]:
    ensure_registry_architecture()

    rows = []

    for category in EXPORT_CATEGORIES:
        folder = EXPORT_ROOT / category
        rows.append(
            {
                "category": category,
                "label": CATEGORY_LABELS.get(category, category.replace("_", " ").title()),
                "folder": str(folder),
                "relative_folder": str(folder.relative_to(ROOT)),
                "exists": folder.is_dir(),
            }
        )

    return rows


def recent_export_rows(limit: int = 20, category: str | None = None) -> list[dict[str, Any]]:
    ensure_registry_architecture()

    rows = []

    for item in recent_exports(limit=limit, category=category):
        path = ROOT / item.get("path", "")

        rows.append(
            {
                "timestamp": item.get("timestamp", ""),
                "category": item.get("category", ""),
                "category_label": CATEGORY_LABELS.get(item.get("category", ""), item.get("category", "")),
                "label": item.get("label", ""),
                "filename": item.get("filename", ""),
                "extension": item.get("extension", ""),
                "export_type": item.get("export_type", ""),
                "relative_path": item.get("path", ""),
                "absolute_path": str(path),
                "exists": path.exists(),
                "source": item.get("source", ""),
            }
        )

    return rows


def gui_bridge_payload(limit: int = 20) -> dict[str, Any]:
    categories = export_category_rows()
    recent = recent_export_rows(limit=limit)

    missing_categories = [row["category"] for row in categories if not row["exists"]]
    missing_recent = [row["relative_path"] for row in recent if not row["exists"]]

    status = FAIL_STATUS if missing_categories else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not missing_categories,
        "category_count": len(categories),
        "recent_count": len(recent),
        "categories": categories,
        "recent_exports": recent,
        "missing_categories": missing_categories,
        "missing_recent_exports": missing_recent,
        "summary": f"{len(categories)} export categories and {len(recent)} recent exports prepared for GUI access.",
    }


def build_export_gui_bridge_report() -> str:
    payload = gui_bridge_payload()

    lines = [
        "EXPORT QUICK ACCESS GUI BRIDGE",
        "==============================",
        f"Phase: {payload['phase']}",
        f"Status: {payload['status']}",
        f"Passed: {payload['passed']}",
        f"Summary: {payload['summary']}",
        "",
        "EXPORT CATEGORY BUTTONS",
        "-----------------------",
    ]

    for row in payload["categories"]:
        lines.append(
            f"- {row['label']} | category={row['category']} | "
            f"folder={row['relative_folder']} | exists={row['exists']}"
        )

    lines.extend(["", "RECENT EXPORT ROWS", "------------------"])

    if payload["recent_exports"]:
        for row in payload["recent_exports"]:
            lines.append(
                f"- {row['timestamp']} | {row['category_label']} | "
                f"{row['label']} | {row['relative_path']} | exists={row['exists']}"
            )
    else:
        lines.append("- No recent exports available.")

    if payload["missing_recent_exports"]:
        lines.extend(["", "MISSING RECENT EXPORT FILES", "---------------------------"])
        lines.extend(f"- {path}" for path in payload["missing_recent_exports"])

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "This phase only prepares GUI-safe export access data. It does not open, delete, move, or overwrite files.",
    ])

    return "\n".join(lines)


def write_export_gui_bridge_report() -> Path:
    ensure_registry_architecture()
    report_path = EXPORT_ROOT / "audits" / "EXPORT_QUICK_ACCESS_GUI_BRIDGE_PHASE_16T2L.txt"
    report_path.write_text(build_export_gui_bridge_report(), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    report = write_export_gui_bridge_report()
    payload = gui_bridge_payload()
    print(payload["status"])
    print(report)
