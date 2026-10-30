from __future__ import annotations

from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "_leaf_exports"

EXPORT_CATEGORIES = [
    "reports",
    "audits",
    "graphs",
    "station_tables",
    "regen",
    "geometry",
    "packaging",
    "snapshots",
]

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


def ensure_registry_architecture() -> None:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    for category in EXPORT_CATEGORIES:
        (EXPORT_ROOT / category).mkdir(parents=True, exist_ok=True)


def recent_exports(limit: int = 20, category: str | None = None) -> list[dict[str, Any]]:
    ensure_registry_architecture()

    rows: list[dict[str, Any]] = []
    categories = [category] if category else EXPORT_CATEGORIES

    for item_category in categories:
        folder = EXPORT_ROOT / item_category
        for path in folder.glob("*"):
            if not path.is_file():
                continue
            rows.append(
                {
                    "timestamp": "",
                    "category": item_category,
                    "label": path.stem,
                    "filename": path.name,
                    "extension": path.suffix,
                    "export_type": path.suffix.lstrip("."),
                    "path": path.relative_to(ROOT).as_posix(),
                    "source": "leaf_qt.export_quick_access_gui_bridge",
                }
            )

    rows.sort(key=lambda row: row["path"], reverse=True)
    return rows[:limit]


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
                "relative_folder": folder.relative_to(ROOT).as_posix(),
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

    return {
        "status": "PASS" if not missing_categories else "FAIL",
        "passed": not missing_categories,
        "category_count": len(categories),
        "recent_count": len(recent),
        "categories": categories,
        "recent_exports": recent,
        "missing_categories": missing_categories,
        "missing_recent_exports": missing_recent,
        "summary": f"{len(categories)} export categories and {len(recent)} recent exports prepared for GUI access.",
    }
