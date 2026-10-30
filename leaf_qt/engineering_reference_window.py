from __future__ import annotations

import html
from numbers import Real

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from engineering_reference_catalog import (
    build_engineering_reference_catalog,
)


class EngineeringReferenceWindow(QDialog):

    CATEGORIES = (
        "Materials",
        "Coatings",
        "Fuels",
        "Oxidisers",
    )

    COST_PROPERTY = (
        "Economic / Reference price per kg"
    )

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.catalog = (
            build_engineering_reference_catalog()
        )

        self.filtered_records = []
        self.comparison_specs = {}

        self.setWindowTitle(
            "LEAF Engineering Reference"
        )

        self.setMinimumSize(
            1100,
            700,
        )

        self.resize(
            1280,
            820,
        )

        self._create_layout()
        self.refresh_records()

    @staticmethod
    def _escape(value):
        return html.escape(
            "Not available"
            if value is None
            else str(value)
        )

    @staticmethod
    def _pretty(value):
        return (
            str(value or "")
            .replace("_", " ")
            .strip()
            .title()
        )

    @staticmethod
    def _is_number(value):
        return (
            isinstance(
                value,
                Real,
            )
            and
            not isinstance(
                value,
                bool,
            )
        )

    def _create_layout(self):
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

        title = QLabel(
            "ENGINEERING REFERENCE"
        )

        title_font = title.font()
        title_font.setBold(True)
        title.setFont(
            title_font
        )

        root.addWidget(
            title
        )

        subtitle = QLabel(
            "Engineering reference data with source and "
            "evidence transparency. Missing numeric values "
            "are excluded from ranking and are never zero-filled."
        )

        subtitle.setWordWrap(
            True
        )

        root.addWidget(
            subtitle
        )

        # --------------------------------------------------------
        # Filters
        # --------------------------------------------------------

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(
            QLabel(
                "Category"
            )
        )

        self.category_combo = QComboBox()

        self.category_combo.addItems(
            self.CATEGORIES
        )

        filter_layout.addWidget(
            self.category_combo
        )

        filter_layout.addWidget(
            QLabel(
                "Search"
            )
        )

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            "Name, alias, formula, composition, supplier..."
        )

        filter_layout.addWidget(
            self.search_edit,
            1,
        )

        clear_button = QPushButton(
            "Clear"
        )

        clear_button.clicked.connect(
            self.search_edit.clear
        )

        filter_layout.addWidget(
            clear_button
        )

        root.addLayout(
            filter_layout
        )

        # --------------------------------------------------------
        # Main splitter
        # --------------------------------------------------------

        self.splitter = QSplitter(
            Qt.Horizontal
        )

        root.addWidget(
            self.splitter,
            1,
        )

        # --------------------------------------------------------
        # Reference table
        # --------------------------------------------------------

        self.record_table = QTableWidget(
            0,
            4,
        )

        self.record_table.setObjectName(
            "engineeringReferenceRecordTable"
        )

        self.record_table.setHorizontalHeaderLabels(
            [
                "Name",
                "Formula / composition",
                "Reference price / kg",
                "Price evidence",
            ]
        )

        self.record_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.record_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.record_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.record_table.verticalHeader().setVisible(
            False
        )

        header = (
            self.record_table
            .horizontalHeader()
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.Stretch,
        )

        for column in range(
            1,
            4,
        ):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeToContents,
            )

        self.splitter.addWidget(
            self.record_table
        )

        # --------------------------------------------------------
        # Detail panel
        # --------------------------------------------------------

        detail_panel = QWidget()

        detail_layout = QVBoxLayout(
            detail_panel
        )

        detail_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.record_title = QLabel(
            "Select a reference record"
        )

        record_font = (
            self.record_title.font()
        )

        record_font.setBold(
            True
        )

        self.record_title.setFont(
            record_font
        )

        detail_layout.addWidget(
            self.record_title
        )

        self.detail_browser = QTextBrowser()

        self.detail_browser.setObjectName(
            "engineeringReferenceDetailBrowser"
        )

        self.detail_browser.setOpenExternalLinks(
            False
        )

        detail_layout.addWidget(
            self.detail_browser,
            3,
        )

        # --------------------------------------------------------
        # Comparison
        # --------------------------------------------------------

        comparison_group = QGroupBox(
            "Compare filtered records"
        )

        comparison_layout = QVBoxLayout(
            comparison_group
        )

        comparison_controls = QHBoxLayout()

        comparison_controls.addWidget(
            QLabel(
                "Property"
            )
        )

        self.comparison_property_combo = (
            QComboBox()
        )

        comparison_controls.addWidget(
            self.comparison_property_combo,
            1,
        )

        comparison_controls.addWidget(
            QLabel(
                "Ordering"
            )
        )

        self.comparison_preference_combo = (
            QComboBox()
        )

        self.comparison_preference_combo.addItems(
            [
                "Lower values first",
                "Higher values first",
            ]
        )

        comparison_controls.addWidget(
            self.comparison_preference_combo
        )

        comparison_layout.addLayout(
            comparison_controls
        )

        self.comparison_summary = QLabel(
            ""
        )

        self.comparison_summary.setWordWrap(
            True
        )

        comparison_layout.addWidget(
            self.comparison_summary
        )

        self.comparison_table = QTableWidget(
            0,
            5,
        )

        self.comparison_table.setHorizontalHeaderLabels(
            [
                "Rank",
                "Name",
                "Value",
                "Unit",
                "Evidence",
            ]
        )

        self.comparison_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.comparison_table.verticalHeader().setVisible(
            False
        )

        compare_header = (
            self.comparison_table
            .horizontalHeader()
        )

        compare_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents,
        )

        compare_header.setSectionResizeMode(
            1,
            QHeaderView.Stretch,
        )

        for column in range(
            2,
            5,
        ):
            compare_header.setSectionResizeMode(
                column,
                QHeaderView.ResizeToContents,
            )

        comparison_layout.addWidget(
            self.comparison_table
        )

        detail_layout.addWidget(
            comparison_group,
            2,
        )

        self.splitter.addWidget(
            detail_panel
        )

        self.splitter.setStretchFactor(
            0,
            1,
        )

        self.splitter.setStretchFactor(
            1,
            2,
        )

        self.splitter.setSizes(
            [
                600,
                660,
            ]
        )

        bottom = QHBoxLayout()
        bottom.addStretch(1)

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.close
        )

        bottom.addWidget(
            close_button
        )

        root.addLayout(
            bottom
        )

        # --------------------------------------------------------
        # Wiring
        # --------------------------------------------------------

        self.category_combo.currentTextChanged.connect(
            self.refresh_records
        )

        self.search_edit.textChanged.connect(
            self.refresh_records
        )

        self.record_table.itemSelectionChanged.connect(
            self._show_selected_record
        )

        self.comparison_property_combo.currentTextChanged.connect(
            self._comparison_property_changed
        )

        self.comparison_preference_combo.currentTextChanged.connect(
            self.refresh_comparison
        )


    def _price_text(
        self,
        record,
    ):
        economic = (
            record.get(
                "economic_record"
            )
            or
            {}
        )

        price = economic.get(
            "unit_price_per_kg"
        )

        currency = economic.get(
            "currency"
        )

        status = str(
            economic.get(
                "status"
            )
            or
            "NOT_AVAILABLE"
        )

        if self._is_number(
            price
        ):
            value = float(
                price
            )

            if currency == "GBP":
                return (
                    f"£{value:.2f}/kg"
                )

            if currency == "USD":
                return (
                    f"${value:.2f}/kg"
                )

            if currency == "EUR":
                return (
                    f"€{value:.2f}/kg"
                )

            if currency:
                return (
                    f"{value:.2f} "
                    f"{currency}/kg"
                )

            return (
                f"{value:.2f}/kg"
            )

        if (
            status
            ==
            "SUPPLIER_QUOTE_REQUIRED"
        ):
            return (
                "Quote required"
            )

        return (
            "Not available"
        )


    def _composition_summary(
        self,
        record,
    ):
        formula = record.get(
            "chemical_formula"
        )

        if formula:
            return str(formula)

        reference_type = str(
            record.get("reference_type")
            or
            ""
        )

        composition = record.get(
            "composition"
        )

        if isinstance(
            composition,
            dict,
        ):
            if reference_type == "MIXTURE":
                return "Mixture composition"

            if reference_type in (
                "METALLIC_ALLOY",
                "PURE_MATERIAL",
            ):
                return "Elemental composition"

            if reference_type == "COATING":
                return "Coating composition"

            return "Composition available"

        if reference_type == "MIXTURE":
            return "Mixture"

        if reference_type in (
            "METALLIC_ALLOY",
            "PURE_MATERIAL",
        ):
            return "Elemental composition unavailable"

        if reference_type == "COATING":
            return "Composition unavailable"

        return "Not available"

    def _search_text(
        self,
        record,
    ):
        economic = (
            record.get(
                "economic_record"
            )
            or
            {}
        )

        values = (
            record.get(
                "display_name"
            ),
            record.get(
                "canonical_name"
            ),
            record.get(
                "aliases"
            ),
            record.get(
                "reference_type"
            ),
            record.get(
                "phase"
            ),
            record.get(
                "chemical_formula"
            ),
            record.get(
                "atomic_composition"
            ),
            record.get(
                "composition"
            ),
            economic.get(
                "status"
            ),
            economic.get(
                "supplier"
            ),
            economic.get(
                "material_form"
            ),
        )

        return " ".join(
            str(value)

            for value in values

            if value is not None
        ).lower()



    def refresh_records(
        self,
        *args,
    ):
        category = (
            self.category_combo
            .currentText()
        )

        query = (
            self.search_edit
            .text()
            .strip()
            .lower()
        )

        records = list(
            (
                self.catalog.get(
                    category,
                    {},
                )
                or
                {}
            ).values()
        )

        records.sort(
            key=lambda record:
                str(
                    record.get(
                        "display_name"
                    )
                    or
                    record.get(
                        "canonical_name"
                    )
                    or
                    ""
                ).lower()
        )

        if query:
            records = [
                record

                for record in records

                if query
                in
                self._search_text(
                    record
                )
            ]

        self.filtered_records = (
            records
        )

        self.record_table.blockSignals(
            True
        )

        self.record_table.setRowCount(
            len(records)
        )

        for row, record in enumerate(
            records
        ):
            name = str(
                record.get(
                    "display_name"
                )
                or
                record.get(
                    "canonical_name"
                )
            )

            canonical_name = (
                record.get(
                    "canonical_name"
                )
            )

            economic = (
                record.get(
                    "economic_record"
                )
                or
                {}
            )

            name_item = QTableWidgetItem(
                name
            )

            name_item.setData(
                Qt.UserRole,
                (
                    category,
                    canonical_name,
                ),
            )

            # Full name remains available even where the visible
            # column must elide it.
            name_item.setToolTip(
                name
            )

            composition_item = QTableWidgetItem(
                self._composition_summary(
                    record
                )
            )

            composition = (
                record.get(
                    "composition"
                )
            )

            if isinstance(
                composition,
                dict,
            ):
                composition_item.setToolTip(
                    "\n".join(
                        f"{key}: {value}"

                        for key, value
                        in composition.items()
                    )
                )

            price_item = QTableWidgetItem(
                self._price_text(
                    record
                )
            )

            basis = economic.get(
                "price_basis"
            )

            if basis:
                price_item.setToolTip(
                    str(
                        basis
                    )
                )

            evidence_item = QTableWidgetItem(
                self._pretty(
                    economic.get(
                        "status"
                    )
                    or
                    "NOT_AVAILABLE"
                )
            )

            evidence_item.setToolTip(
                str(
                    economic.get(
                        "price_basis"
                    )
                    or
                    "No qualified numeric public reference "
                    "price is attached."
                )
            )

            cells = (
                name_item,
                composition_item,
                price_item,
                evidence_item,
            )

            for column, item in enumerate(
                cells
            ):
                self.record_table.setItem(
                    row,
                    column,
                    item,
                )

        self.record_table.blockSignals(
            False
        )

        self._refresh_comparison_properties()

        if records:
            self.record_table.selectRow(
                0
            )

            self._show_selected_record()

        else:
            self.record_title.setText(
                "No matching reference record"
            )

            self.detail_browser.setPlainText(
                "No record matches the current filter."
            )

    def _record(
        self,
        category,
        canonical_name,
    ):
        return (
            self.catalog.get(
                category,
                {}
            )
            .get(
                canonical_name
            )
        )

    def _show_selected_record(
        self,
    ):
        rows = (
            self.record_table
            .selectionModel()
            .selectedRows()
        )

        if not rows:
            return

        item = (
            self.record_table
            .item(
                rows[0].row(),
                0,
            )
        )

        if item is None:
            return

        key = item.data(
            Qt.UserRole
        )

        if not (
            isinstance(
                key,
                (tuple, list),
            )
            and
            len(key) == 2
        ):
            return

        record = self._record(
            key[0],
            key[1],
        )

        if record is not None:
            self._show_record(
                record
            )

    def _formula_text(
        self,
        record,
    ):
        formula = record.get(
            "chemical_formula"
        )

        if formula:
            return str(
                formula
            )

        reference_type = str(
            record.get(
                "reference_type"
            )
            or
            ""
        )

        if reference_type == "MIXTURE":
            return (
                "Not applicable — mixture"
            )

        if reference_type in (
            "METALLIC_ALLOY",
            "PURE_MATERIAL",
        ):
            return (
                "Not applicable — material/alloy"
            )

        return (
            "Not available"
        )

    def _atomic_text(
        self,
        record,
    ):
        atomic = record.get(
            "atomic_composition"
        )

        if isinstance(
            atomic,
            dict,
        ):
            return ", ".join(
                f"{element}: {count}"

                for element, count
                in atomic.items()
            )

        reference_type = str(
            record.get(
                "reference_type"
            )
            or
            ""
        )

        if reference_type == "MIXTURE":
            return (
                "Not single-valued for a mixture"
            )

        if reference_type in (
            "METALLIC_ALLOY",
            "PURE_MATERIAL",
        ):
            return (
                "Use elemental composition"
            )

        return (
            "Not available"
        )

    def _dictionary_html(
        self,
        value,
    ):
        if not isinstance(
            value,
            dict,
        ):
            return self._escape(
                value
            )

        return (
            "<ul>"
            +
            "".join(
                "<li>"
                f"<b>{self._escape(key)}</b>: "
                f"{self._escape(item)}"
                "</li>"

                for key, item
                in value.items()
            )
            +
            "</ul>"
        )



    def _show_record(
        self,
        record,
    ):
        self.record_title.setText(
            str(
                record.get(
                    "display_name"
                )
                or
                record.get(
                    "canonical_name"
                )
            )
        )

        reference_type = str(
            record.get(
                "reference_type"
            )
            or
            ""
        )

        aliases = (
            record.get(
                "aliases"
            )
            or
            []
        )

        economic = (
            record.get(
                "economic_record"
            )
            or
            {}
        )

        composition = record.get(
            "composition"
        )

        # ========================================================
        # CHEMISTRY / COMPOSITION
        # ========================================================

        if reference_type in (
            "PURE_COMPOUND",
            "PHASE_VARIANT",
        ):
            structure = (
                record.get(
                    "structural_representation"
                )
            )

            structure_html = (
                "<h4>Structural representation</h4>"
                "<pre style='font-family: monospace; "
                "font-size: 13px; margin-left: 12px;'>"
                f"{self._escape(structure)}"
                "</pre>"

                if structure

                else

                "<h4>Structural representation</h4>"
                "Not available"
            )

            chemistry_html = (
                "<h3>Chemistry</h3>"
                "<table>"
                "<tr><td><b>Molecular formula</b></td><td>"
                f"{self._escape(self._formula_text(record))}"
                "</td></tr>"
                "<tr><td><b>Atomic composition</b></td><td>"
                f"{self._escape(self._atomic_text(record))}"
                "</td></tr>"
                "<tr><td><b>Molecular weight</b></td><td>"
                f"{self._escape(record.get('molecular_weight'))}"
                "</td></tr>"
                "<tr><td><b>CAS</b></td><td>"
                f"{self._escape(record.get('cas_number'))}"
                "</td></tr>"
                "<tr><td><b>InChI</b></td><td>"
                f"{self._escape(record.get('inchi'))}"
                "</td></tr>"
                "<tr><td><b>Structure reference</b></td><td>"
                f"{self._escape(record.get('structure_reference'))}"
                "</td></tr>"
                "</table>"
                +
                structure_html
            )

            if composition is not None:
                chemistry_html += (
                    "<h4>Composition</h4>"
                    +
                    self._dictionary_html(
                        composition
                    )
                )

        elif reference_type == "MIXTURE":
            chemistry_html = (
                "<h3>Chemistry & mixture composition</h3>"
                "<table>"
                "<tr><td><b>Molecular formula</b></td>"
                "<td>Not applicable — mixture</td></tr>"
                "<tr><td><b>Atomic composition</b></td>"
                "<td>Not single-valued for a mixture</td></tr>"
                "<tr><td><b>Molecular structure</b></td>"
                "<td>Not applicable — mixture</td></tr>"
                "</table>"
                "<h4>Mixture composition / classification</h4>"
                +
                self._dictionary_html(
                    composition
                )
            )

        else:
            chemistry_html = (
                "<h3>Composition</h3>"
                +
                self._dictionary_html(
                    composition
                )
            )

        # ========================================================
        # ENGINEERING PROPERTIES WITH UNITS
        # ========================================================

        engineering = (
            record.get(
                "engineering_properties"
            )
            or
            {}
        )

        engineering_rows = []

        for key, value in (
            engineering.items()
        ):
            if isinstance(
                value,
                dict,
            ):
                value_text = (
                    f"{len(value)} structured values"
                )

            elif isinstance(
                value,
                (list, tuple),
            ):
                value_text = (
                    ", ".join(
                        str(item)
                        for item in value
                    )

                    if len(value) <= 10

                    else

                    f"{len(value)} values"
                )

            elif self._is_number(
                value
            ):
                unit = (
                    self._unit_for_key(
                        key
                    )
                )

                value_text = (
                    f"{float(value):.6g}"
                )

                if unit != "—":
                    value_text += (
                        f" {unit}"
                    )

            else:
                value_text = str(
                    value
                )

            engineering_rows.append(
                "<tr>"
                f"<td><b>{self._escape(self._pretty(key))}</b></td>"
                f"<td>{self._escape(value_text)}</td>"
                "</tr>"
            )

        if not engineering_rows:
            engineering_rows.append(
                "<tr><td colspan='2'>"
                "No engineering-property record is available."
                "</td></tr>"
            )

        # ========================================================
        # SOURCES / LIMITATIONS
        # ========================================================

        sources = (
            record.get(
                "sources"
            )
            or
            []
        )

        if sources:
            source_html = (
                "<ul>"
                +
                "".join(
                    "<li>"
                    f"{self._escape(source.get('authority') or 'Unknown authority')}"
                    " — "
                    f"{self._escape(source.get('reference') or 'No reference')}"
                    " ["
                    f"{self._escape(source.get('source_quality') or 'quality unavailable')}"
                    "]"
                    "</li>"

                    for source in sources
                )
                +
                "</ul>"
            )

        else:
            source_html = (
                "No explicit reference source is currently attached."
            )

        limitations = (
            record.get(
                "limitations"
            )
            or
            []
        )

        if limitations:
            limitation_html = (
                "<ul>"
                +
                "".join(
                    "<li>"
                    f"{self._escape(item)}"
                    "</li>"

                    for item in limitations
                )
                +
                "</ul>"
            )

        else:
            limitation_html = (
                "No additional limitation recorded."
            )

        # ========================================================
        # REFERENCE PRICE EVIDENCE
        # ========================================================

        reference_only = (
            economic.get(
                "reference_only"
            )
            is True
        )

        not_cost_input = (
            economic.get(
                "not_cost_input"
            )
            is True
        )

        use_text = (
            "Reference evidence only — not automatically used "
            "as a LEAF manufacturing-cost input."

            if (
                reference_only
                or
                not_cost_input
            )

            else

            "No automatic cost-model relationship is declared."
        )

        # ========================================================
        # FINAL DOCUMENT
        # ========================================================

        detail = (
            "<style>"
            "table { border-collapse: collapse; }"
            "td { padding: 2px 16px 2px 0; vertical-align: top; }"
            "h3 { margin-top: 14px; margin-bottom: 5px; }"
            "h4 { margin-top: 9px; margin-bottom: 4px; }"
            "</style>"

            "<h3>At a glance</h3>"
            "<table>"
            "<tr><td><b>Type</b></td><td>"
            f"{self._escape(self._pretty(reference_type))}"
            "</td></tr>"
            "<tr><td><b>Formula / composition</b></td><td>"
            f"{self._escape(self._composition_summary(record))}"
            "</td></tr>"
            "<tr><td><b>Reference price / kg</b></td><td>"
            f"{self._escape(self._price_text(record))}"
            "</td></tr>"
            "<tr><td><b>Price evidence</b></td><td>"
            f"{self._escape(self._pretty(economic.get('status') or 'NOT_AVAILABLE'))}"
            "</td></tr>"
            "</table>"

            "<h3>Identity</h3>"
            "<table>"
            "<tr><td><b>Category</b></td><td>"
            f"{self._escape(record.get('category'))}"
            "</td></tr>"
            "<tr><td><b>Canonical name</b></td><td>"
            f"{self._escape(record.get('canonical_name'))}"
            "</td></tr>"
            "<tr><td><b>Phase</b></td><td>"
            f"{self._escape(record.get('phase') or 'Not specified')}"
            "</td></tr>"
            "<tr><td><b>Aliases</b></td><td>"
            f"{self._escape(', '.join(str(v) for v in aliases) if aliases else 'None')}"
            "</td></tr>"
            "</table>"

            +
            chemistry_html
            +

            "<h3>Engineering properties</h3>"
            "<table>"
            +
            "".join(
                engineering_rows
            )
            +
            "</table>"

            "<h3>Reference price evidence</h3>"
            "<table>"
            "<tr><td><b>Reference price / kg</b></td><td>"
            f"{self._escape(self._price_text(record))}"
            "</td></tr>"
            "<tr><td><b>Price evidence</b></td><td>"
            f"{self._escape(self._pretty(economic.get('status') or 'NOT_AVAILABLE'))}"
            "</td></tr>"
            "<tr><td><b>Currency</b></td><td>"
            f"{self._escape(economic.get('currency'))}"
            "</td></tr>"
            "<tr><td><b>Supplier</b></td><td>"
            f"{self._escape(economic.get('supplier'))}"
            "</td></tr>"
            "<tr><td><b>Product / material form</b></td><td>"
            f"{self._escape(economic.get('material_form'))}"
            "</td></tr>"
            "<tr><td><b>Commercial basis</b></td><td>"
            f"{self._escape(economic.get('price_basis'))}"
            "</td></tr>"
            "<tr><td><b>Tax basis</b></td><td>"
            f"{self._escape(economic.get('tax_basis'))}"
            "</td></tr>"
            "<tr><td><b>Reference date</b></td><td>"
            f"{self._escape(economic.get('price_date'))}"
            "</td></tr>"
            "<tr><td><b>Price source</b></td><td>"
            f"{self._escape(economic.get('price_source'))}"
            "</td></tr>"
            "<tr><td><b>Source quality</b></td><td>"
            f"{self._escape(economic.get('source_quality'))}"
            "</td></tr>"
            "<tr><td><b>Derivation</b></td><td>"
            f"{self._escape(economic.get('reference_price_derivation'))}"
            "</td></tr>"
            "<tr><td><b>Use in LEAF cost model</b></td><td>"
            f"{self._escape(use_text)}"
            "</td></tr>"
            "</table>"

            "<h3>Sources</h3>"
            +
            source_html
            +

            "<h3>Limitations</h3>"
            +
            limitation_html
        )

        self.detail_browser.setHtml(
            detail
        )

    def _numeric_properties(
        self,
        record,
    ):
        engineering = (
            record.get(
                "engineering_properties"
            )
            or
            {}
        )

        result = {}

        for key, value in (
            engineering.items()
        ):
            if self._is_number(
                value
            ):
                label = (
                    "Engineering / "
                    +
                    self._pretty(
                        key
                    )
                )

                result[
                    label
                ] = (
                    "engineering",
                    key,
                )

        return result


    def _refresh_comparison_properties(
        self,
    ):
        previous = (
            self.comparison_property_combo
            .currentText()
        )

        specs = {
            self.COST_PROPERTY:
                (
                    "economic",
                    "unit_price_per_kg",
                )
        }

        for record in self.filtered_records:
            specs.update(
                self._numeric_properties(
                    record
                )
            )

        engineering_labels = sorted(
            label
            for label in specs
            if label
            !=
            self.COST_PROPERTY
        )

        # Engineering properties come first.
        # Cost remains selectable, but is not the automatic
        # default simply because it is the first inserted option.
        labels = [
            *engineering_labels,
            self.COST_PROPERTY,
        ]

        self.comparison_specs = specs

        self.comparison_property_combo.blockSignals(
            True
        )

        self.comparison_property_combo.clear()

        self.comparison_property_combo.addItems(
            labels
        )

        if (
            previous
            and
            previous in labels
        ):
            selected = previous

        else:
            selected = next(
                (
                    label
                    for label in engineering_labels
                    if "Density" in label
                ),
                None,
            )

            if selected is None:
                selected = (
                    engineering_labels[0]
                    if engineering_labels
                    else
                    self.COST_PROPERTY
                )

        self.comparison_property_combo.setCurrentText(
            selected
        )

        self.comparison_property_combo.blockSignals(
            False
        )

        self._comparison_property_changed(
            selected
        )


    def _comparison_property_changed(
        self,
        label,
    ):
        if label == self.COST_PROPERTY:
            self.comparison_preference_combo.setCurrentText(
                "Lower values first"
            )

        self.refresh_comparison()

    @staticmethod

    @staticmethod
    def _unit_for_key(
        key,
    ):
        key = str(
            key
        ).strip().lower()

        if (
            "density"
            in
            key
        ):
            return "kg/m³"

        if (
            "thermal_conductivity"
            in
            key
            or
            "conductivity"
            in
            key
        ):
            return "W/(m·K)"

        if (
            "specific_heat"
            in
            key
        ):
            return "J/(kg·K)"

        if (
            "thermal_expansion"
            in
            key
        ):
            return "1/K"

        if (
            "poisson"
            in
            key
        ):
            return "dimensionless"

        if any(
            token in key

            for token in (
                "yield_strength",
                "ultimate_tensile_strength",
                "elastic_modulus",
            )
        ):
            return "Pa"

        if any(
            token in key

            for token in (
                "melting_point",
                "temperature",
                "boiling_point",
                "freezing_point",
            )
        ):
            return "K"

        if (
            "viscosity"
            in
            key
        ):
            return "Pa·s"

        if (
            "pressure"
            in
            key
            or
            key.endswith(
                "_pa"
            )
        ):
            return "Pa"

        if (
            "percent"
            in
            key
            or
            key.endswith(
                "_pct"
            )
        ):
            return "%"

        return "—"


    def _comparison_value(
        self,
        record,
        spec,
    ):
        source, key = spec

        if source == "economic":
            economic = (
                record.get(
                    "economic_record"
                )
                or
                {}
            )

            value = economic.get(
                key
            )

            currency = economic.get(
                "currency"
            )

            unit = (
                f"{currency}/kg"
                if currency
                else
                "currency/kg"
            )

            supplier = economic.get(
                "supplier"
            )

            quality = economic.get(
                "source_quality"
            )

            if supplier and quality:
                evidence = (
                    f"{supplier} — {quality}"
                )

            elif supplier:
                evidence = str(
                    supplier
                )

            elif quality:
                evidence = str(
                    quality
                )

            else:
                evidence = (
                    economic.get(
                        "status"
                    )
                    or
                    "Not available"
                )

        else:
            engineering = (
                record.get(
                    "engineering_properties"
                )
                or
                {}
            )

            value = engineering.get(
                key
            )

            unit = (
                self._unit_for_key(
                    key
                )
            )

            quality = (
                engineering.get(
                    "source_quality"
                )
                or
                record.get(
                    "source_quality"
                )
                or
                "source quality unavailable"
            )

            category = str(
                record.get(
                    "category"
                )
                or
                ""
            )

            if category in (
                "Materials",
                "Coatings",
            ):
                owner = (
                    "LEAF material database"
                )

            elif category in (
                "Fuels",
                "Oxidisers",
            ):
                owner = (
                    "LEAF propellant database"
                )

            else:
                owner = (
                    "LEAF engineering database"
                )

            evidence = (
                f"{owner} — {quality}"
            )

        if not self._is_number(
            value
        ):
            return (
                None,
                unit,
                str(
                    evidence
                ),
            )

        return (
            float(
                value
            ),
            unit,
            str(
                evidence
            ),
        )


    def refresh_comparison(
        self,
        *args,
    ):
        self.comparison_table.setRowCount(
            0
        )

        label = (
            self.comparison_property_combo
            .currentText()
        )

        spec = (
            self.comparison_specs.get(
                label
            )
        )

        if spec is None:
            self.comparison_summary.setText(
                "No comparable property is available."
            )
            return

        rows = []
        missing = 0

        for record in (
            self.filtered_records
        ):
            value, unit, evidence = (
                self._comparison_value(
                    record,
                    spec,
                )
            )

            if value is None:
                missing += 1
                continue

            economic = (
                record.get(
                    "economic_record"
                )
                or
                {}
            )

            rows.append({
                "name":
                    str(
                        record.get(
                            "display_name"
                        )
                        or
                        record.get(
                            "canonical_name"
                        )
                    ),

                "value":
                    value,

                "unit":
                    unit,

                "evidence":
                    evidence,

                "currency":
                    economic.get(
                        "currency"
                    )
                    if spec[0] == "economic"
                    else None,

                "comparison_group":
                    economic.get(
                        "comparison_group"
                    )
                    if spec[0] == "economic"
                    else None,
            })

        # --------------------------------------------------------
        # Reference prices are only ranked on a common commercial
        # basis. Same currency alone is not sufficient.
        # --------------------------------------------------------

        if spec[0] == "economic":
            currencies = {
                row[
                    "currency"
                ]

                for row in rows

                if row[
                    "currency"
                ]
            }

            if len(
                currencies
            ) > 1:
                self.comparison_summary.setText(
                    "Reference prices use multiple currencies. "
                    "Ranking is disabled until a qualified "
                    "common-currency basis exists."
                )
                return

            basis_groups = {
                row[
                    "comparison_group"
                ]

                for row in rows
            }

            if (
                len(rows) > 1

                and

                (
                    None in basis_groups
                    or
                    len(basis_groups) > 1
                )
            ):
                self.comparison_summary.setText(
                    "Reference prices have different commercial "
                    "bases (for example product form, size or "
                    "quantity). Ranking is disabled. Narrow the "
                    "filter to records sharing one price basis."
                )
                return

        if not rows:
            self.comparison_summary.setText(
                "No comparable sourced numeric values are available "
                "for this property. Missing values are excluded and "
                "are never treated as zero."
            )
            return

        lower_first = (
            self.comparison_preference_combo
            .currentText()
            ==
            "Lower values first"
        )

        rows.sort(
            key=lambda row:
                row[
                    "value"
                ],

            reverse=
                not lower_first,
        )

        self.comparison_table.setRowCount(
            len(rows)
        )

        for index, row in enumerate(
            rows
        ):
            if len(rows) == 1:
                rank = (
                    "Only value"
                )

            elif index == 0:
                rank = (
                    "Lowest"
                    if lower_first
                    else
                    "Highest"
                )

            elif index == (
                len(rows) - 1
            ):
                rank = (
                    "Highest"
                    if lower_first
                    else
                    "Lowest"
                )

            else:
                rank = str(
                    index + 1
                )

            cells = (
                rank,
                row[
                    "name"
                ],
                f"{row['value']:.6g}",
                row[
                    "unit"
                ],
                row[
                    "evidence"
                ],
            )

            for column, value in enumerate(
                cells
            ):
                self.comparison_table.setItem(
                    index,
                    column,
                    QTableWidgetItem(
                        str(
                            value
                        )
                    ),
                )

        ordering = (
            "lower values first"
            if lower_first
            else
            "higher values first"
        )

        self.comparison_summary.setText(
            f"Compared {len(rows)} of "
            f"{len(self.filtered_records)} filtered records; "
            f"{missing} missing/non-numeric values excluded. "
            f"Ordering: {ordering}. "
            "This is numeric ordering under the selected direction, "
            "not a universal engineering judgement of best/worst."
        )
