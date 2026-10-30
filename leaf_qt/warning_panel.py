from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
)


class WarningPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Type", "Variable", "Message"])

        self.tree.setColumnWidth(0, 140)
        self.tree.setColumnWidth(1, 220)
        self.tree.setColumnWidth(2, 600)

        layout.addWidget(self.tree)

    def update_warnings(self, warnings):
        self.tree.clear()

        if not warnings:
            item = QTreeWidgetItem()
            item.setText(0, "OK")
            item.setText(1, "All")
            item.setText(2, "No warnings detected.")
            self.tree.addTopLevelItem(item)
            return

        for warning in warnings:
            item = QTreeWidgetItem()

            item.setText(0, str(warning.get("type", "Warning")))
            item.setText(1, str(warning.get("variable", "")))
            item.setText(2, str(warning.get("message", "")))

            self.tree.addTopLevelItem(item)

    def clear_warnings(self):
        self.tree.clear()

        item = QTreeWidgetItem()
        item.setText(0, "OK")
        item.setText(1, "All")
        item.setText(2, "No warnings detected.")
        self.tree.addTopLevelItem(item)