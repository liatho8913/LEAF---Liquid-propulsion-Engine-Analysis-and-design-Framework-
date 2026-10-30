from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
)


class DiagnosticsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels([
            "Severity",
            "Diagnostic",
            "Reason",
            "Suggestion"
        ])

        self.tree.setColumnWidth(0, 120)
        self.tree.setColumnWidth(1, 260)
        self.tree.setColumnWidth(2, 520)
        self.tree.setColumnWidth(3, 520)

        layout.addWidget(self.tree)

    def update_diagnostics(self, diagnostics_report):
        self.tree.clear()

        if not isinstance(diagnostics_report, dict):
            self.add_row(
                severity="critical",
                title="Invalid diagnostics report",
                detail="Diagnostics panel received an invalid report object.",
                suggestion="Check DiagnosticsEngine.evaluate() output."
            )
            return

        counts = diagnostics_report.get("counts", {})
        engine_scale = diagnostics_report.get("engine_scale", "unknown")
        issues = diagnostics_report.get("issues", [])

        summary = QTreeWidgetItem()
        summary.setText(0, "SUMMARY")
        summary.setText(1, f"Engine scale: {engine_scale}")
        summary.setText(
            2,
            (
                f"Critical: {counts.get('critical', 0)} | "
                f"Warnings: {counts.get('warning', 0)} | "
                f"Info: {counts.get('info', 0)}"
            )
        )
        summary.setText(3, "Diagnostics are scale-aware where possible.")
        summary.setExpanded(True)
        self.tree.addTopLevelItem(summary)

        if not issues:
            self.add_row(
                severity="info",
                title="No diagnostic issues detected",
                detail="The current solved outputs passed the diagnostics checks.",
                suggestion=""
            )
            self.resize_columns()
            return

        for issue in issues:
            self.add_row(
                severity=issue.get("severity", "info"),
                title=issue.get("title", ""),
                detail=issue.get("detail", ""),
                suggestion=issue.get("suggestion", "")
            )

        self.resize_columns()

    def add_row(self, severity, title, detail, suggestion):
        item = QTreeWidgetItem()

        severity_text = str(severity or "info").upper()

        item.setText(0, severity_text)
        item.setText(1, str(title or ""))
        item.setText(2, str(detail or ""))
        item.setText(3, str(suggestion or ""))

        if severity_text == "CRITICAL":
            item.setBackground(0, Qt.GlobalColor.darkRed)
            item.setBackground(1, Qt.GlobalColor.darkRed)
            item.setBackground(2, Qt.GlobalColor.darkRed)
            item.setBackground(3, Qt.GlobalColor.darkRed)
            item.setForeground(0, Qt.GlobalColor.white)
            item.setForeground(1, Qt.GlobalColor.white)
            item.setForeground(2, Qt.GlobalColor.white)
            item.setForeground(3, Qt.GlobalColor.white)

        elif severity_text == "WARNING":
            item.setBackground(0, Qt.GlobalColor.darkYellow)
            item.setBackground(1, Qt.GlobalColor.darkYellow)
            item.setBackground(2, Qt.GlobalColor.darkYellow)
            item.setBackground(3, Qt.GlobalColor.darkYellow)

        elif severity_text == "INFO":
            item.setBackground(0, Qt.GlobalColor.darkBlue)
            item.setBackground(1, Qt.GlobalColor.darkBlue)
            item.setBackground(2, Qt.GlobalColor.darkBlue)
            item.setBackground(3, Qt.GlobalColor.darkBlue)
            item.setForeground(0, Qt.GlobalColor.white)
            item.setForeground(1, Qt.GlobalColor.white)
            item.setForeground(2, Qt.GlobalColor.white)
            item.setForeground(3, Qt.GlobalColor.white)

        self.tree.addTopLevelItem(item)

    def resize_columns(self):
        for column in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(column)