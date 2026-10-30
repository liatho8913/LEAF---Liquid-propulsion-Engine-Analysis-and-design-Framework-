from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from report_formatting import report_text_to_html


class ReportViewerWindow(QDialog):

    NAVIGATION_GROUPS = (
        (
            "Summary",
            (
                "Overview",
            ),
        ),
        (
            "Engine Analysis",
            (
                "Performance & Geometry",
                "Thermal & Cooling",
            ),
        ),
        (
            "Evidence",
            (
                "Materials & Sources",
                "Validation & Limitations",
                "Benchmark & Reproduction",
            ),
        ),
        (
            "Design",
            (
                "Design Recommendations",
                "Design History",
            ),
        ),
    )

    def __init__(
        self,
        parent,
        title,
        reports,
        export_controller,
    ):
        super().__init__(
            parent
        )

        self.export_controller = (
            export_controller
        )

        self.reports = (
            reports
            or
            {}
        )

        self.current_report_name = None
        self.navigation_items = {}

        self.setWindowTitle(
            title
        )

        self.resize(
            1100,
            760,
        )

        self.create_layout()
        self.load_first_report()

    def create_layout(self):
        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        root.setSpacing(
            8
        )

        heading = QLabel(
            "LEAF REPORT VIEWER"
        )

        font = heading.font()
        font.setBold(True)
        heading.setFont(font)

        root.addWidget(
            heading
        )

        self.splitter = QSplitter(
            Qt.Horizontal
        )

        root.addWidget(
            self.splitter,
            1,
        )

        self.navigation_tree = QTreeWidget()

        self.navigation_tree.setObjectName(
            "reportNavigationTree"
        )

        self.navigation_tree.setHeaderHidden(
            True
        )

        self.navigation_tree.setMinimumWidth(
            220
        )

        self.navigation_tree.setMaximumWidth(
            330
        )

        for (
            group_name,
            report_names,
        ) in self.NAVIGATION_GROUPS:

            group_item = QTreeWidgetItem(
                [
                    group_name
                ]
            )

            group_item.setFlags(
                group_item.flags()
                &
                ~Qt.ItemIsSelectable
            )

            self.navigation_tree.addTopLevelItem(
                group_item
            )

            for report_name in report_names:

                if (
                    report_name
                    not in
                    self.reports
                ):
                    continue

                item = QTreeWidgetItem(
                    [
                        report_name
                    ]
                )

                item.setData(
                    0,
                    Qt.UserRole,
                    report_name,
                )

                group_item.addChild(
                    item
                )

                self.navigation_items[
                    report_name
                ] = item

            group_item.setExpanded(
                True
            )

        self.navigation_tree.currentItemChanged.connect(
            self.change_report
        )

        self.splitter.addWidget(
            self.navigation_tree
        )

        report_panel = QWidget()

        report_layout = QVBoxLayout(
            report_panel
        )

        report_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        report_layout.setSpacing(
            6
        )

        self.report_title_label = QLabel(
            ""
        )

        title_font = (
            self.report_title_label.font()
        )

        title_font.setBold(
            True
        )

        self.report_title_label.setFont(
            title_font
        )

        report_layout.addWidget(
            self.report_title_label
        )

        self.text_box = QTextBrowser()

        self.text_box.setObjectName(
            "reportTextBrowser"
        )

        self.text_box.setReadOnly(
            True
        )

        self.text_box.setOpenExternalLinks(
            False
        )

        self.text_box.setTextInteractionFlags(
            Qt.TextSelectableByMouse
            |
            Qt.TextSelectableByKeyboard
        )

        report_layout.addWidget(
            self.text_box,
            1,
        )

        self.splitter.addWidget(
            report_panel
        )

        self.splitter.setStretchFactor(
            0,
            0,
        )

        self.splitter.setStretchFactor(
            1,
            1,
        )

        self.splitter.setSizes(
            [
                250,
                800,
            ]
        )

        controls = QHBoxLayout()

        controls.addStretch(
            1
        )

        self.copy_button = QPushButton(
            "Copy"
        )

        self.copy_button.clicked.connect(
            self.copy_report
        )

        controls.addWidget(
            self.copy_button
        )

        self.export_button = QPushButton(
            "Export TXT"
        )

        self.export_button.clicked.connect(
            self.export_report
        )

        controls.addWidget(
            self.export_button
        )

        self.export_html_button = QPushButton(
            "Export HTML"
        )

        self.export_html_button.clicked.connect(
            self.export_report_html
        )

        controls.addWidget(
            self.export_html_button
        )

        self.close_button = QPushButton(
            "Close"
        )

        self.close_button.clicked.connect(
            self.close
        )

        controls.addWidget(
            self.close_button
        )

        root.addLayout(
            controls
        )

    def load_first_report(self):
        for (
            group_name,
            report_names,
        ) in self.NAVIGATION_GROUPS:

            for report_name in report_names:

                item = (
                    self.navigation_items.get(
                        report_name
                    )
                )

                if item is not None:
                    self.navigation_tree.setCurrentItem(
                        item
                    )
                    return

        self.report_title_label.setText(
            "No report available"
        )

        self.text_box.setPlainText(
            "No user-facing report is available. "
            "Run a calculation first."
        )

    def change_report(
        self,
        current,
        previous=None,
    ):
        if isinstance(
            current,
            str,
        ):
            report_name = current

        elif current is not None:
            report_name = current.data(
                0,
                Qt.UserRole,
            )

        else:
            report_name = None

        if (
            not report_name

            or

            report_name
            not in
            self.reports
        ):
            return

        self.current_report_name = str(
            report_name
        )

        report_text = str(
            self.reports.get(
                self.current_report_name,
                "",
            )
            or
            ""
        )

        self.report_title_label.setText(
            self.current_report_name
        )

        self.text_box.setHtml(
            report_text_to_html(
                self.current_report_name,
                report_text,
            )
        )

    def copy_report(self):
        if self.current_report_name:
            QApplication.clipboard().setText(
                str(
                    self.reports.get(
                        self.current_report_name,
                        "",
                    )
                    or
                    ""
                )
            )

    def export_report(self):
        if not self.current_report_name:
            QMessageBox.warning(
                self,
                "No Report",
                "No report selected.",
            )
            return

        report_text = self.reports.get(
            self.current_report_name,
            "",
        )

        if not report_text:
            QMessageBox.warning(
                self,
                "Empty Report",
                "The selected report is empty.",
            )
            return

        safe_name = (
            self.current_report_name.lower()
            .replace(
                " ",
                "_",
            )
            .replace(
                "/",
                "_",
            )
            .replace(
                "-",
                "_",
            )
            .replace(
                "&",
                "and",
            )
        )

        self.export_controller.export_text_report(
            "Export Report",
            report_text,
            f"{safe_name}.txt",
        )

    def export_report_html(self):
        if not self.current_report_name:
            QMessageBox.warning(
                self,
                "No Report",
                "No report selected.",
            )
            return

        report_text = self.reports.get(
            self.current_report_name,
            "",
        )

        if not report_text:
            QMessageBox.warning(
                self,
                "Empty Report",
                "The selected report is empty.",
            )
            return

        safe_name = (
            self.current_report_name.lower()
            .replace(
                " ",
                "_",
            )
            .replace(
                "/",
                "_",
            )
            .replace(
                "-",
                "_",
            )
            .replace(
                "&",
                "and",
            )
        )

        self.export_controller.export_html_report(
            self.current_report_name,
            report_text,
            f"{safe_name}.html",
        )
