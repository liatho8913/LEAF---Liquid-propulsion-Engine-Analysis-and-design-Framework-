from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QListWidget,
        QListWidgetItem,
        QGroupBox,
        QSplitter,
        QTextEdit,
    )
except Exception:
    Qt = None
    QWidget = object
    QVBoxLayout = QHBoxLayout = QLabel = QPushButton = QListWidget = QListWidgetItem = QGroupBox = QSplitter = QTextEdit = None


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.export_quick_access_gui_bridge import (
    gui_bridge_payload,
)


PHASE = "16T.2M"

PASS_STATUS = "PASS_EXPORT_QUICK_ACCESS_PANEL_STUB_PHASE_16T2M"
FAIL_STATUS = "FAIL_EXPORT_QUICK_ACCESS_PANEL_STUB_PHASE_16T2M"


def open_path_in_file_manager(path: str | Path) -> bool:
    p = Path(path)

    if not p.exists():
        return False

    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        elif os.name == "nt":
            os.startfile(str(p))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(p)], check=False)
        return True
    except Exception:
        return False


class ExportQuickAccessPanel(QWidget):
    def __init__(self, parent: Any = None, recent_limit: int = 20) -> None:
        super().__init__(parent)
        self.recent_limit = recent_limit
        self.payload: dict[str, Any] = {}

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Export Quick Access")
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)

        button_row = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh)
        button_row.addWidget(self.refresh_button)

        layout.addLayout(button_row)

        splitter = QSplitter(Qt.Horizontal)

        category_box = QGroupBox("Export Folders")
        category_layout = QVBoxLayout(category_box)
        self.category_list = QListWidget()
        self.category_list.itemDoubleClicked.connect(self._open_selected_category)
        category_layout.addWidget(self.category_list)

        recent_box = QGroupBox("Recent Exports")
        recent_layout = QVBoxLayout(recent_box)
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self._open_selected_recent)
        recent_layout.addWidget(self.recent_list)

        splitter.addWidget(category_box)
        splitter.addWidget(recent_box)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        layout.addWidget(self.details)

    def refresh(self) -> None:
        self.payload = gui_bridge_payload(limit=self.recent_limit)
        self._populate_categories()
        self._populate_recent()
        self._populate_details()

    def _populate_categories(self) -> None:
        self.category_list.clear()

        for row in self.payload.get("categories", []):
            label = row.get("label", row.get("category", "Unknown"))
            exists = "OK" if row.get("exists") else "MISSING"
            item = QListWidgetItem(f"{label} — {exists}")
            item.setData(Qt.UserRole, row)
            self.category_list.addItem(item)

    def _populate_recent(self) -> None:
        self.recent_list.clear()

        for row in self.payload.get("recent_exports", []):
            exists = "OK" if row.get("exists") else "MISSING"
            label = row.get("label") or row.get("filename") or "Unnamed Export"
            category = row.get("category_label") or row.get("category") or "Export"
            item = QListWidgetItem(f"{category}: {label} — {exists}")
            item.setData(Qt.UserRole, row)
            self.recent_list.addItem(item)

    def _populate_details(self) -> None:
        lines = [
            "EXPORT QUICK ACCESS PANEL",
            "=========================",
            f"Phase: {PHASE}",
            f"Status: {self.payload.get('status')}",
            f"Summary: {self.payload.get('summary')}",
            "",
            "Usage:",
            "- Double-click an export folder to open it.",
            "- Double-click a recent export to open the file.",
            "",
            "Safety:",
            "- This panel does not delete, move, or overwrite files.",
        ]

        self.details.setPlainText("\n".join(lines))

    def _open_selected_category(self, item: Any) -> None:
        row = item.data(Qt.UserRole)
        if row:
            open_path_in_file_manager(row.get("folder", ""))

    def _open_selected_recent(self, item: Any) -> None:
        row = item.data(Qt.UserRole)
        if row:
            open_path_in_file_manager(row.get("absolute_path", ""))


def build_export_panel_stub_audit() -> dict[str, Any]:
    blockers = []

    try:
        payload = gui_bridge_payload(limit=5)
    except Exception as exc:
        payload = {}
        blockers.append(f"GUI bridge payload failed: {type(exc).__name__}: {exc}")

    if QWidget is object:
        blockers.append("PySide6 is unavailable; panel class is importable but not instantiable.")

    status = FAIL_STATUS if blockers else PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not blockers,
        "category_count": payload.get("category_count", 0),
        "recent_count": payload.get("recent_count", 0),
        "blockers": blockers,
        "warnings": [],
        "summary": f"Export panel stub prepared with {payload.get('category_count', 0)} categories and {payload.get('recent_count', 0)} recent exports.",
    }


if __name__ == "__main__":
    audit = build_export_panel_stub_audit()
    print(audit["status"])
