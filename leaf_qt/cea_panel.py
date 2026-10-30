import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEAF_QT_ROOT = Path(__file__).resolve().parent

for path in [PROJECT_ROOT, LEAF_QT_ROOT]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

try:
    from coolant_database import COOLANT_PROPERTY_DATABASE
except Exception:
    COOLANT_PROPERTY_DATABASE = {}

from propellant_database import (
    canonical_fuel,
    canonical_oxidizer,
    get_all_fuel_options,
    get_compatible_oxidizers_for_fuel,
    get_compatible_oxidizer_display_options_for_fuel,
    get_oxidizer_display_name,
    get_default_fuel_temperature_k,
    get_default_oxidizer_temperature_k,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
)


class CEAPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.is_syncing_propellants = False
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.fuel_selector = QComboBox()
        self.fuel_selector.addItems(get_all_fuel_options())

        self.oxidizer_selector = QComboBox()

        current_fuel = canonical_fuel(self.fuel_selector.currentText())
        self.oxidizer_selector.addItems(
            get_compatible_oxidizer_display_options_for_fuel(
                current_fuel
            )
        )

        self.coolant_selector = QComboBox()
        coolant_names = list(COOLANT_PROPERTY_DATABASE.keys())

        if not coolant_names:
            coolant_names = [
                "RP-1 / Kerosene",
                "Liquid Methane",
                "Liquid Hydrogen",
                "Water",
                "Ethanol",
            ]

        self.coolant_selector.addItems(coolant_names)

        self.fuel_temp_entry = QLineEdit(
            str(get_default_fuel_temperature_k(self.fuel_selector.currentText()))
        )
        self.oxidizer_temp_entry = QLineEdit(
            str(get_default_oxidizer_temperature_k(self.oxidizer_selector.currentText()))
        )
        self.mixture_ratio_entry = QLineEdit("3.5")

        self.fuel_selector.currentTextChanged.connect(
            self.refresh_oxidizer_selector_from_fuel
        )
        self.oxidizer_selector.currentTextChanged.connect(
            self.refresh_temperature_defaults_from_selection
        )

        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            "CEA",
            "Manual",
        ])

        form.addRow("Fuel", self.fuel_selector)
        form.addRow("Oxidizer", self.oxidizer_selector)
        form.addRow("Coolant", self.coolant_selector)
        form.addRow("Fuel temperature K", self.fuel_temp_entry)
        form.addRow("Oxidizer temperature K", self.oxidizer_temp_entry)
        form.addRow("O/F mixture ratio", self.mixture_ratio_entry)
        form.addRow("Calculation Mode", self.mode_selector)

        layout.addLayout(form)


        self.raw_output = QTextEdit()
        self.raw_output.setReadOnly(True)
        self.raw_output.setPlaceholderText("Raw CEA output will appear here later.")
        layout.addWidget(self.raw_output)

    def refresh_oxidizer_selector_from_fuel(self, set_default=False):
        if self.is_syncing_propellants:
            return

        self.is_syncing_propellants = True

        current_fuel = canonical_fuel(self.fuel_selector.currentText())
        current_oxidizer = canonical_oxidizer(self.oxidizer_selector.currentText())

        compatible_oxidizers = (
            get_compatible_oxidizer_display_options_for_fuel(
                current_fuel
            )
        )

        current_oxidizer_display = (
            get_oxidizer_display_name(
                current_oxidizer
            )
        )

        self.oxidizer_selector.blockSignals(True)
        self.oxidizer_selector.clear()
        self.oxidizer_selector.addItems(compatible_oxidizers)

        if current_oxidizer_display in compatible_oxidizers:
            self.oxidizer_selector.setCurrentText(
                current_oxidizer_display
            )
        elif compatible_oxidizers:
            self.oxidizer_selector.setCurrentIndex(0)

        self.oxidizer_selector.blockSignals(False)

        self.refresh_temperature_defaults_from_selection()

        self.is_syncing_propellants = False

    def refresh_temperature_defaults_from_selection(self):
        fuel = canonical_fuel(self.fuel_selector.currentText())
        oxidizer = canonical_oxidizer(self.oxidizer_selector.currentText())

        self.fuel_temp_entry.setText(
            str(get_default_fuel_temperature_k(fuel))
        )
        self.oxidizer_temp_entry.setText(
            str(get_default_oxidizer_temperature_k(oxidizer))
        )

    def set_inputs(self, inputs):
        if not isinstance(inputs, dict):
            return

        def set_combo(combo, value):
            if value is None:
                return

            if combo is self.oxidizer_selector:
                value = get_oxidizer_display_name(
                    value
                )

            index = combo.findText(str(value))

            if index >= 0:
                combo.setCurrentIndex(index)

        fuel_value = canonical_fuel(
            inputs.get("fuel")
            or inputs.get("fuel_input")
            or inputs.get("fuel_type")
        )

        set_combo(self.fuel_selector, fuel_value)
        self.refresh_oxidizer_selector_from_fuel()

        oxidizer_value = canonical_oxidizer(
            inputs.get("oxidizer")
            or inputs.get("oxidizer_input")
            or inputs.get("oxidizer_type")
        )

        set_combo(self.oxidizer_selector, oxidizer_value)

        set_combo(
            self.coolant_selector,
            inputs.get("selected_coolant_name")
            or inputs.get("coolant")
        )

        set_combo(
            self.mode_selector,
            inputs.get("calculation_mode")
            or inputs.get("mode")
        )

        value = inputs.get("mixture_ratio")
        if value is not None:
            self.mixture_ratio_entry.setText(str(value))

        value = inputs.get("fuel_temp_k") or inputs.get("fuel_temperature_k")
        if value is not None:
            self.fuel_temp_entry.setText(str(value))

        value = inputs.get("oxidizer_temp_k") or inputs.get("oxidizer_temperature_k")
        if value is not None:
            self.oxidizer_temp_entry.setText(str(value))

    def get_cea_inputs(self):
        return {
            "fuel": canonical_fuel(self.fuel_selector.currentText()),
            "oxidizer": canonical_oxidizer(self.oxidizer_selector.currentText()),
            "selected_coolant_name": self.coolant_selector.currentText(),
            "fuel_temp_k": self.safe_float(self.fuel_temp_entry.text()),
            "oxidizer_temp_k": self.safe_float(self.oxidizer_temp_entry.text()),
            "mixture_ratio": self.safe_float(self.mixture_ratio_entry.text()),
            "calculation_mode": self.mode_selector.currentText(),
        }

    def safe_float(self, text):
        try:
            return float(text.strip())
        except Exception:
            return None

    def set_raw_output(self, text):
        self.raw_output.setPlainText(text or "")