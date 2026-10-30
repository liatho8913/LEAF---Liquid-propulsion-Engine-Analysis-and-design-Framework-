from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTextEdit,
)

from benchmark_case_database import (
    get_benchmark_case,
    get_benchmark_case_names,
)


class BenchmarkPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.case_names = get_benchmark_case_names()

        self.create_layout()
        self.update_case_description()

    def create_layout(self):
        layout = QVBoxLayout(self)

        title = QLabel("Benchmark Case Selector")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 6px;
            }
        """)
        layout.addWidget(title)

        row = QHBoxLayout()

        row.addWidget(QLabel("Benchmark case:"))

        self.case_selector = QComboBox()

        self.case_selector.addItem("No suitable public reference", None)
        for key, name in self.case_names.items():
            self.case_selector.addItem(name, key)

        self.case_selector.currentIndexChanged.connect(
            self.update_case_description
        )

        row.addWidget(self.case_selector)

        layout.addLayout(row)

        self.description_box = QTextEdit()
        self.description_box.setReadOnly(True)
        layout.addWidget(self.description_box)

    def get_selected_case_key(self):
        return self.case_selector.currentData()

    def set_selected_case_key(self, case_key):
        for index in range(self.case_selector.count()):
            if self.case_selector.itemData(index) == case_key:
                self.case_selector.setCurrentIndex(index)
                return

    def update_case_description(self):
        case_key = self.get_selected_case_key()
        case = get_benchmark_case(case_key)

        if not case:
            self.description_box.setPlainText("No benchmark case selected.")
            return

        lines = []
        lines.append(case.get("display_name", case_key))
        lines.append("=" * len(lines[0]))
        lines.append("")
        lines.append(f"Case key: {case_key}")
        lines.append(f"Source status: {case.get('source_status', 'UNKNOWN')}")
        lines.append(f"Engine family: {case.get('engine_family', 'UNKNOWN')}")
        lines.append("")

        notes = case.get("notes") or []

        if notes:
            lines.append("Notes:")
            for note in notes:
                lines.append(f"- {note}")
            lines.append("")

        targets = case.get("targets") or {}

        if targets:
            lines.append("Public benchmark envelope:")
            for key, value in targets.items():
                lines.append(f"- {key}: {value}")

        self.description_box.setPlainText("\n".join(lines))