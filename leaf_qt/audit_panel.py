from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
)


class AuditPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels([
            "Section",
            "Variable",
            "Status",
            "Reason",
            "Recommendation",
        ])

        self.tree.setColumnWidth(0, 130)
        self.tree.setColumnWidth(1, 220)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 420)
        self.tree.setColumnWidth(4, 420)

        layout.addWidget(self.tree)

    def update_audit(self, rows):
        self.tree.clear()

        for row in rows:
            item = QTreeWidgetItem()
            item.setText(0, str(row.get("section", "")))
            item.setText(1, str(row.get("variable", "")))
            item.setText(2, str(row.get("status", "")))
            item.setText(3, str(row.get("reason", "")))
            item.setText(4, str(row.get("recommendation", "")))

            status = str(row.get("status", "")).upper()

            if status == "PASS":
                item.setText(2, "PASS")
            elif status == "WARNING":
                item.setText(2, "WARNING")
            elif status == "FAIL":
                item.setText(2, "FAIL")
            elif status == "MISSING":
                item.setText(2, "MISSING")

            self.tree.addTopLevelItem(item)