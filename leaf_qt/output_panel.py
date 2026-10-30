from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QHeaderView,
    QApplication,
    QTabWidget,
)
from PySide6.QtCore import Qt
from variable_registry import (
    get_scalar_output_sections_by_key,
    get_scalar_output_keys,
    get_label,
    get_symbol,
    get_unit,
)

OUTPUT_GROUPS = {
    "Main Outputs": get_scalar_output_keys(),
}

for section_name, keys in get_scalar_output_sections_by_key().items():
    OUTPUT_GROUPS[section_name] = keys


class OutputPanel(QWidget):
    def __init__(self, sections, symbols, units):
        super().__init__()

        self.sections = sections
        self.symbols = symbols
        self.units = units
        self.last_results = {}
        self.tables = {}

        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search outputs...")
        self.search_box.textChanged.connect(self.apply_filter)

        self.copy_selected_button = QPushButton("Copy Selected")
        self.copy_selected_button.clicked.connect(self.copy_selected)

        self.copy_all_button = QPushButton("Copy Current Tab")
        self.copy_all_button.clicked.connect(self.copy_current_tab)

        self.title_label = QLabel("All Outputs")
        self.title_label.setMinimumHeight(34)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 6px;
            }
        """)

        layout.addWidget(self.title_label)
        top_bar.addWidget(self.search_box)
        top_bar.addWidget(self.copy_selected_button)
        top_bar.addWidget(self.copy_all_button)

        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tabs)

        for group_name in OUTPUT_GROUPS:
            table = self.create_table()
            self.tables[group_name] = table
            self.tabs.addTab(table, group_name)

    def on_tab_changed(self):
        current_index = self.tabs.currentIndex()

        if current_index >= 0:
            self.title_label.setText(self.tabs.tabText(current_index))

        self.apply_filter()

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Variable",
            "Symbol",
            "Value",
            "Unit",
            "Internal Name",
        ])

        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.ExtendedSelection)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(34)
        table.setMinimumHeight(500)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        return table

    def update_outputs(self, results):
        self.last_results = results or {}

        for group_name, var_list in OUTPUT_GROUPS.items():
            table = self.tables[group_name]

            grouped_results = {}

            for var_name in var_list:
                if var_name in self.last_results:
                    grouped_results[var_name] = self.last_results.get(var_name)

            self.populate_table(table, grouped_results, ordered_vars=var_list)

        self.apply_filter()

    def set_outputs(self, results):
        self.update_outputs(results)

    def clear_outputs(self):
        self.last_results = {}

        for table in self.tables.values():
            table.setRowCount(0)

    def populate_table(self, table, results, ordered_vars=None):
        rows = []

        if ordered_vars is None:
            items = sorted(results.items(), key=lambda item: item[0].lower())
        else:
            items = [(var_name, results.get(var_name)) for var_name in ordered_vars]

        for var_name, value in items:
            if value is None:
                continue

            label = self.pretty_label(var_name)
            symbol = get_symbol(var_name)
            unit = get_unit(var_name)
            rows.append((label, symbol, value, unit, var_name))

        table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            label, symbol, value, unit, var_name = row_data
            display_value = self.format_value(value)

            table_items = [
                QTableWidgetItem(str(label)),
                QTableWidgetItem(str(symbol)),
                QTableWidgetItem(str(display_value)),
                QTableWidgetItem(str(unit)),
                QTableWidgetItem(str(var_name)),
            ]

            for item in table_items:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)

            for column_index, item in enumerate(table_items):
                table.setItem(row_index, column_index, item)

    def current_table(self):
        return self.tabs.currentWidget()

    def apply_filter(self):
        table = self.current_table()

        if table is None:
            return

        search_text = self.search_box.text().strip().lower()

        for row in range(table.rowCount()):
            if not search_text:
                table.setRowHidden(row, False)
                continue

            row_text = ""

            for column in range(table.columnCount()):
                item = table.item(row, column)

                if item is not None:
                    row_text += " " + item.text().lower()

            table.setRowHidden(row, search_text not in row_text)

    def copy_selected(self):
        table = self.current_table()

        if table is None:
            return

        selected_rows = sorted(
            set(index.row() for index in table.selectedIndexes())
        )

        if not selected_rows:
            return

        title = self.tabs.tabText(self.tabs.currentIndex())

        lines = []
        lines.append(title.upper())
        lines.append("=" * len(title))
        lines.append("")

        for row in selected_rows:
            if table.isRowHidden(row):
                continue

            variable = table.item(row, 0).text() if table.item(row, 0) else ""
            symbol = table.item(row, 1).text() if table.item(row, 1) else ""
            value = table.item(row, 2).text() if table.item(row, 2) else ""
            unit = table.item(row, 3).text() if table.item(row, 3) else ""

            if symbol:
                line = f"{variable} ({symbol}): {value}"
            else:
                line = f"{variable}: {value}"

            if unit:
                line += f" {unit}"

            lines.append(line)

        QApplication.clipboard().setText("\n".join(lines))

    def copy_current_tab(self):
        current_title = self.tabs.tabText(self.tabs.currentIndex())

        if current_title == "Main Outputs":
            text = self.build_grouped_all_outputs_copy_text()
        else:
            table = self.current_table()
            text = self.build_table_copy_text(current_title, table)

        QApplication.clipboard().setText(text)

    def build_table_copy_text(self, title, table):
        if table is None:
            return ""

        lines = []
        lines.append(title.upper())
        lines.append("=" * len(title))
        lines.append("")

        for row in range(table.rowCount()):
            if table.isRowHidden(row):
                continue

            variable = table.item(row, 0).text() if table.item(row, 0) else ""
            symbol = table.item(row, 1).text() if table.item(row, 1) else ""
            value = table.item(row, 2).text() if table.item(row, 2) else ""
            unit = table.item(row, 3).text() if table.item(row, 3) else ""

            if symbol:
                line = f"{variable} ({symbol}): {value}"
            else:
                line = f"{variable}: {value}"

            if unit:
                line += f" {unit}"

            lines.append(line)

        return "\n".join(lines)

    def build_grouped_all_outputs_copy_text(self):
        lines = []
        lines.append("LEAF MAIN OUTPUTS")
        lines.append("=================")
        lines.append("")

        for group_name, var_list in OUTPUT_GROUPS.items():
            if group_name == "Main Outputs" or var_list is None:
                continue

            group_lines = []

            for var_name in var_list:
                if var_name not in self.last_results:
                    continue

                value = self.last_results.get(var_name)

                if value is None:
                    continue

                variable = self.pretty_label(var_name)
                symbol = get_symbol(var_name)
                unit = get_unit(var_name)
                display_value = self.format_value(value)

                if symbol:
                    line = f"{variable} ({symbol}): {display_value}"
                else:
                    line = f"{variable}: {display_value}"

                if unit:
                    line += f" {unit}"

                group_lines.append(line)

            if not group_lines:
                continue

            lines.append(group_name.upper())
            lines.append("-" * len(group_name))
            lines.extend(group_lines)
            lines.append("")

        return "\n".join(lines)

    def pretty_label(self, var_name):
        return get_label(var_name)

    def format_value(self, value):
        if isinstance(value, float):
            if abs(value) >= 1e5 or (abs(value) < 1e-3 and value != 0):
                return f"{value:.6e}"

            return f"{value:.6g}"

        return value