from __future__ import annotations

import sys
from pathlib import Path

LEAF_QT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = LEAF_QT_DIR.parent

for candidate in (PROJECT_ROOT, LEAF_QT_DIR):
    value = str(candidate)
    if value not in sys.path:
        sys.path.insert(0, value)

import sys
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QInputDialog, QLineEdit, QMessageBox,
)

from leaf_qt.security_context import SecurityContextOwner
from main_window import LeafMainWindow

def main():
    app = QApplication(sys.argv)
    security_context = SecurityContextOwner()

    if not security_context.principal_store_path.exists():
        recover = QMessageBox.question(
            None,
            "LEAF Principal Recovery",
            "No local LEAF principal is present on this device.\n\n"
            "Choose Yes to recover an existing principal, or No to create a new one.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if recover == QMessageBox.Yes:
            recovery_path, _ = QFileDialog.getOpenFileName(
                None,
                "Select LEAF Principal Recovery Record",
                str(Path.home()),
                "LEAF Principal Recovery (*.leaf-principal-recovery.json);;All Files (*)",
            )
            if not recovery_path:
                return
            recovery_code, accepted = QInputDialog.getText(
                None,
                "LEAF Principal Recovery Code",
                "Enter the separate principal recovery code:",
                QLineEdit.Password,
            )
            if not accepted or not recovery_code:
                return
            try:
                SecurityContextOwner.restore_recovery_record(
                    recovery_path,
                    recovery_code,
                )
            except Exception as exc:
                QMessageBox.critical(
                    None,
                    "Principal Recovery Failed",
                    f"LEAF could not restore the principal:\n\n{exc}",
                )
                return
            QMessageBox.information(
                None,
                "Principal Recovered",
                "The recovered LEAF principal will be used for this session.",
            )

    window = LeafMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()