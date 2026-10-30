import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QPushButton,
    QTextEdit,
    QLineEdit,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from leaf_qt.material_database import (
        get_material_names,
        get_material_properties,
        get_material_summary_text,
        get_coating_material_names,
        get_coating_material_properties,
        get_bond_coat_names,
        get_bond_coat_properties,
    )
except ImportError:
    get_material_names = None
    get_material_properties = None
    get_material_summary_text = None
    get_coating_material_names = None
    get_coating_material_properties = None
    get_bond_coat_names = None
    get_bond_coat_properties = None


class MaterialsPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.material_selectors = {}
        self.material_unit_price_records = {}
        self.manufacturing_process_costs = {}
        self._economic_loading = False
        self._economic_material_name = None

        self.create_layout()
        self.update_material_summary()

    def safe_material_names(self):
        if get_material_names is None:
            return ["GRCop-42"]

        names = get_material_names()
        return names if names else ["GRCop-42"]

    def safe_coating_names(self):
        if get_coating_material_names is None:
            return []

        names = get_coating_material_names()
        return names if names else []

    def safe_bond_coat_names(self):
        if get_bond_coat_names is None:
            return []

        names = get_bond_coat_names()
        return names if names else []

    def set_combo_text(self, combo, value):
        if value in (None, ""):
            return

        index = combo.findText(str(value))

        if index >= 0:
            combo.setCurrentIndex(index)


    def _current_economic_record(self):
        price = self.unit_price_per_kg_entry.text().strip()
        currency = self.price_currency_entry.text().strip()
        source = self.price_source_entry.text().strip()
        timestamp = self.price_date_entry.text().strip()
        material_form = self.material_form_entry.text().strip()
        source_quality = self.price_source_quality_selector.currentText().strip()

        if not any(
            (
                price,
                currency,
                source,
                timestamp,
                material_form,
            )
        ):
            return None

        return {
            "unit_price_per_kg": price or None,
            "currency": currency or None,
            "source": source or None,
            "timestamp": timestamp or None,
            "source_quality": source_quality or None,
            "material_form": material_form or None,
        }

    def _store_economic_record(self):
        if self._economic_loading:
            return

        name = self._economic_material_name

        if not name:
            return

        record = self._current_economic_record()

        if record is None:
            self.material_unit_price_records.pop(
                name,
                None,
            )
        else:
            self.material_unit_price_records[
                name
            ] = record

    def _load_economic_record(self, name):
        record = (
            self.material_unit_price_records.get(
                name
            )
            or {}
        )

        self._economic_loading = True

        try:
            price = record.get(
                "unit_price_per_kg"
            )

            self.unit_price_per_kg_entry.setText(
                ""
                if price is None
                else str(price)
            )

            self.price_currency_entry.setText(
                str(
                    record.get(
                        "currency"
                    )
                    or ""
                )
            )

            self.price_source_entry.setText(
                str(
                    record.get(
                        "source"
                    )
                    or ""
                )
            )

            self.price_date_entry.setText(
                str(
                    record.get(
                        "timestamp"
                    )
                    or ""
                )
            )

            self.material_form_entry.setText(
                str(
                    record.get(
                        "material_form"
                    )
                    or ""
                )
            )

            self.price_source_quality_selector.setCurrentText(
                str(
                    record.get(
                        "source_quality"
                    )
                    or
                    "UNSOURCED"
                )
            )

        finally:
            self._economic_loading = False

    def _on_liner_material_changed(self, name):
        if self._economic_loading:
            return

        self._store_economic_record()

        self._economic_material_name = str(
            name
            or ""
        )

        self._load_economic_record(
            self._economic_material_name
        )

        self.update_material_summary()

    def _on_economic_field_changed(self, *args):
        if self._economic_loading:
            return

        self._store_economic_record()
        self.update_material_summary()

    def economic_basis_summary(self, name):
        record = (
            self.material_unit_price_records.get(
                name
            )
            or {}
        )

        price = record.get(
            "unit_price_per_kg"
        )

        if price in (
            None,
            "",
        ):
            return (
                "Unit Price: Supplier quote required\\n"
                "Economic Status: PRICE NOT SOURCED"
            )

        currency = (
            record.get(
                "currency"
            )
            or
            "N/A"
        )

        source = (
            record.get(
                "source"
            )
            or
            "N/A"
        )

        timestamp = (
            record.get(
                "timestamp"
            )
            or
            "N/A"
        )

        source_quality = (
            record.get(
                "source_quality"
            )
            or
            "UNSOURCED"
        )

        material_form = (
            record.get(
                "material_form"
            )
            or
            "N/A"
        )

        complete = all(
            value not in (
                None,
                "",
                "N/A",
                "UNSOURCED",
            )
            for value in (
                price,
                currency,
                source,
                timestamp,
                source_quality,
            )
        )

        status = (
            "SOURCE BASIS PROVIDED"
            if complete
            else
            "SOURCE BASIS INCOMPLETE"
        )

        return (
            f"Unit Price: {currency} {price} / kg\\n"
            f"Material Form: {material_form}\\n"
            f"Price Source: {source}\\n"
            f"Price Date: {timestamp}\\n"
            f"Source Quality: {source_quality}\\n"
            f"Economic Status: {status}"
        )

    def set_inputs(self, inputs):
        if not isinstance(inputs, dict):
            return

        selected_material_form = inputs.get(
            "selected_material_form"
        )

        if hasattr(
            self,
            "selected_material_form_selector",
        ):
            if selected_material_form in (None, ""):
                self.selected_material_form_selector.setCurrentIndex(0)
            else:
                self.selected_material_form_selector.setCurrentText(
                    str(selected_material_form)
                )

        selected_material_heat_treatment = inputs.get(
            "selected_material_heat_treatment"
        )

        if hasattr(
            self,
            "selected_material_heat_treatment_selector",
        ):
            if selected_material_heat_treatment in (None, ""):
                self.selected_material_heat_treatment_selector.setCurrentIndex(0)
            else:
                self.selected_material_heat_treatment_selector.setCurrentText(
                    str(selected_material_heat_treatment)
                )

        self.set_combo_text(
            self.hot_gas_liner_selector,
            inputs.get("hot_gas_liner")
            or inputs.get("hot_gas_liner_material")
            or inputs.get("selected_material_name")
            or inputs.get("selected_material")
            or inputs.get("material_name")
        )

        self.set_combo_text(
            self.outer_jacket_selector,
            inputs.get("outer_jacket")
            or inputs.get("outer_jacket_material")
        )

        self.set_combo_text(
            self.rib_channel_selector,
            inputs.get("rib_channel")
            or inputs.get("rib_channel_material")
        )

        self.set_combo_text(
            self.coating_selector,
            inputs.get("selected_coating_material")
            or inputs.get("selected_tbc")
            or inputs.get("selected_coating")
            or inputs.get("coating")
            or inputs.get("coating_material")
        )

        self.set_combo_text(
            self.bond_coat_selector,
            inputs.get("selected_bond_coat")
            or inputs.get("selected_interlayer")
            or inputs.get("bond_coat")
            or inputs.get("bond_coat_material")
        )

        cost_inputs = inputs.get(
            "cost_intelligence_inputs"
        )

        if not isinstance(
            cost_inputs,
            dict,
        ):
            cost_inputs = {}

        material_prices = cost_inputs.get(
            "material_unit_prices"
        )

        if not isinstance(
            material_prices,
            dict,
        ):
            material_prices = {}

        self.material_unit_price_records = {
            str(name): dict(record)
            for name, record in material_prices.items()
            if isinstance(
                record,
                dict,
            )
        }

        process_costs = cost_inputs.get(
            "manufacturing_process_costs"
        )

        self.manufacturing_process_costs = (
            dict(process_costs)
            if isinstance(
                process_costs,
                dict,
            )
            else {}
        )

        self._economic_material_name = (
            self.hot_gas_liner_selector.currentText()
        )

        self._load_economic_record(
            self._economic_material_name
        )

        self.update_material_summary()

    def create_layout(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        material_names = self.safe_material_names()
        coating_names = ["None"] + self.safe_coating_names()
        bond_coat_names = ["None"] + self.safe_bond_coat_names()

        self.hot_gas_liner_selector = QComboBox()
        self.hot_gas_liner_selector.addItems(material_names)
        self.hot_gas_liner_selector.setCurrentText("GRCop-42")

        self.selected_material_form_selector = QComboBox()
        self.selected_material_form_selector.addItems([
            "",
            "WROUGHT",
            "EXTRUDED",
            "L_PBF",
            "LP_DED",
        ])

        self.selected_material_heat_treatment_selector = QComboBox()
        self.selected_material_heat_treatment_selector.addItems([
            "",
            "AS_BUILT",
            "STRESS_RELIEVED",
            "HIP",
            "ANNEALED",
            "SOLUTION_TREATED",
            "HIP_PLUS_HEAT_TREATMENT",
        ])

        self.outer_jacket_selector = QComboBox()
        self.outer_jacket_selector.addItems(material_names)
        self.outer_jacket_selector.setCurrentText("Inconel 718")

        self.rib_channel_selector = QComboBox()
        self.rib_channel_selector.addItems(material_names)
        self.rib_channel_selector.setCurrentText("GRCop-42")

        self.coating_selector = QComboBox()
        self.coating_selector.addItems(coating_names)
        self.coating_selector.setCurrentText("None")

        self.bond_coat_selector = QComboBox()
        self.bond_coat_selector.addItems(bond_coat_names)
        self.bond_coat_selector.setCurrentText("None")

        self.unit_price_per_kg_entry = QLineEdit()
        self.unit_price_per_kg_entry.setPlaceholderText(
            "Supplier quote required"
        )

        self.price_currency_entry = QLineEdit()
        self.price_currency_entry.setPlaceholderText(
            "e.g. GBP"
        )

        self.price_source_entry = QLineEdit()
        self.price_source_entry.setPlaceholderText(
            "Supplier / quote reference"
        )

        self.price_date_entry = QLineEdit()
        self.price_date_entry.setPlaceholderText(
            "YYYY-MM-DD"
        )

        self.material_form_entry = QLineEdit()
        self.material_form_entry.setPlaceholderText(
            "e.g. AM powder, 15-53 um"
        )

        self.price_source_quality_selector = QComboBox()
        self.price_source_quality_selector.addItems([
            "UNSOURCED",
            "SUPPLIER_QUOTE",
            "MANUFACTURER_PUBLISHED_PRICE",
            "DISTRIBUTOR_QUOTE",
            "DISTRIBUTOR_PUBLISHED_PRICE",
        ])

        self.price_source_quality_selector.setEditable(
            True
        )

        self.price_source_quality_selector.setCurrentText(
            "UNSOURCED"
        )

        self._economic_material_name = (
            self.hot_gas_liner_selector.currentText()
        )

        self.material_selectors = {
            "hot_gas_liner": self.hot_gas_liner_selector,
            "outer_jacket": self.outer_jacket_selector,
            "rib_channel": self.rib_channel_selector,
            "selected_coating_material": self.coating_selector,
            "selected_bond_coat": self.bond_coat_selector,
        }

        form.addRow(
            "Hot-Gas Liner Material",
            self.hot_gas_liner_selector,
        )

        form.addRow(
            "Engineering Material Form",
            self.selected_material_form_selector,
        )

        form.addRow(
            "Engineering Heat Treatment",
            self.selected_material_heat_treatment_selector,
        )

        form.addRow(
            "Outer Jacket Material",
            self.outer_jacket_selector,
        )

        form.addRow(
            "Rib / Channel Material",
            self.rib_channel_selector,
        )

        form.addRow(
            "Coating / Liner",
            self.coating_selector,
        )

        form.addRow(
            "Bond Coat / Interlayer",
            self.bond_coat_selector,
        )







        layout.addLayout(form)

        self.apply_button = QPushButton(
            "Apply Selected Liner Material to Regen Inputs"
        )

        layout.addWidget(
            self.apply_button
        )

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)

        layout.addWidget(
            self.summary_text
        )

        self.hot_gas_liner_selector.currentTextChanged.connect(
            self._on_liner_material_changed
        )

        for selector in self.material_selectors.values():
            selector.currentTextChanged.connect(
                self.update_material_summary
            )

        for entry in (
            self.unit_price_per_kg_entry,
            self.price_currency_entry,
            self.price_source_entry,
            self.price_date_entry,
            self.material_form_entry,
        ):
            entry.textChanged.connect(
                self._on_economic_field_changed
            )

        self.price_source_quality_selector.currentTextChanged.connect(
            self._on_economic_field_changed
        )

    def base_material_summary(self, name):
        if get_material_summary_text is None:
            return f"Material selected: {name}"

        return get_material_summary_text(name)

    def coating_summary(self, name):
        if name in (None, "", "None"):
            return "No coating selected."

        if get_coating_material_properties is None:
            return f"Coating selected: {name}"

        coating = get_coating_material_properties(name)

        if coating is None:
            return f"Coating selected but not found in database: {name}"

        return (
            f"Coating: {coating.get('name', name)}\n"
            f"Family: {coating.get('family', 'Unknown')}\n"
            f"Role: {coating.get('coating_role', 'Unknown')}\n"
            f"Thermal Conductivity: {coating.get('thermal_conductivity')} W/(m·K)\n"
            f"Max Surface Temperature: {coating.get('max_surface_temperature')} K\n"
            f"Max Practical Thickness: {coating.get('max_practical_thickness')} m\n"
            f"Density: {coating.get('density')} kg/m³\n"
            f"Source Quality: {coating.get('source_quality')}\n"
            f"Validation Mode: {coating.get('source_validation_mode')}\n"
            f"Placeholder: {coating.get('source_is_placeholder')}\n"
            f"Notes: {coating.get('notes')}"
        )

    def bond_coat_summary(self, name):
        if name in (None, "", "None"):
            return "No bond coat selected."

        if get_bond_coat_properties is None:
            return f"Bond coat selected: {name}"

        bond = get_bond_coat_properties(name)

        if bond is None:
            return f"Bond coat selected but not found in database: {name}"

        return (
            f"Bond Coat: {bond.get('name', name)}\n"
            f"Family: {bond.get('family', 'Unknown')}\n"
            f"Max Stress Reduction Fraction: {bond.get('max_stress_reduction_fraction')}\n"
            f"Max Practical Thickness: {bond.get('max_practical_thickness')} m\n"
            f"Density: {bond.get('density')} kg/m³\n"
            f"Source Quality: {bond.get('source_quality')}\n"
            f"Validation Mode: {bond.get('source_validation_mode')}\n"
            f"Placeholder: {bond.get('source_is_placeholder')}\n"
            f"Notes: {bond.get('notes')}"
        )

    def update_material_summary(self):
        liner = self.hot_gas_liner_selector.currentText()
        jacket = self.outer_jacket_selector.currentText()
        rib = self.rib_channel_selector.currentText()
        coating = self.coating_selector.currentText()
        bond_coat = self.bond_coat_selector.currentText()

        summary = (
            "HOT-GAS LINER\n"
            "====================\n"
            f"{self.base_material_summary(liner)}\n"

            "OUTER JACKET\n"
            "====================\n"
            f"{self.base_material_summary(jacket)}\n\n"

            "RIB / CHANNEL MATERIAL\n"
            "====================\n"
            f"{self.base_material_summary(rib)}\n\n"

            "COATING / LINER\n"
            "====================\n"
            f"{self.coating_summary(coating)}\n\n"

            "BOND COAT / INTERLAYER\n"
            "====================\n"
            f"{self.bond_coat_summary(bond_coat)}"
        )

        self.summary_text.setPlainText(
            summary
        )

    def get_selected_materials(self):
        self._store_economic_record()

        return {
            "hot_gas_liner":
                self.hot_gas_liner_selector.currentText(),

            "outer_jacket":
                self.outer_jacket_selector.currentText(),

            "rib_channel":
                self.rib_channel_selector.currentText(),

            # Solver-facing compatibility keys
            "selected_material":
                self.hot_gas_liner_selector.currentText(),

            "selected_material_name":
                self.hot_gas_liner_selector.currentText(),

            "material_name":
                self.hot_gas_liner_selector.currentText(),

            "selected_coating_material":
                self.coating_selector.currentText(),

            "selected_bond_coat":
                self.bond_coat_selector.currentText(),

            "cost_intelligence_inputs": {
                "material_unit_prices": {
                    name: dict(record)

                    for name, record
                    in self.material_unit_price_records.items()
                },

                "manufacturing_process_costs":
                    dict(
                        self.manufacturing_process_costs
                    ),
            },
            "selected_material_form": (
                self.selected_material_form_selector.currentText()
                or None
            ),
            "selected_material_heat_treatment": (
                self.selected_material_heat_treatment_selector.currentText()
                or None
            ),
        }

    def get_hot_gas_liner_material(self):
        name = self.hot_gas_liner_selector.currentText()

        if get_material_properties is None:
            return name, None

        return name, get_material_properties(name)