from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QGroupBox,
)


class GeometryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)

        nozzle_group = QGroupBox("Nozzle Geometry")
        form = QFormLayout(nozzle_group)

        self.nozzle_geometry_combo = QComboBox()
        self.nozzle_geometry_combo.addItem(
            "Conical Nozzle",
            "CONICAL",
        )
        self.nozzle_geometry_combo.addItem(
            "Rao Bell Approximation",
            "RAO_BELL_APPROXIMATION",
        )
        self.nozzle_geometry_combo.setCurrentIndex(1)

        self.conical_half_angle_spin = QDoubleSpinBox()
        self.conical_half_angle_spin.setRange(5.0, 30.0)
        self.conical_half_angle_spin.setDecimals(2)
        self.conical_half_angle_spin.setSingleStep(0.5)
        self.conical_half_angle_spin.setValue(15.0)
        self.conical_half_angle_spin.setSuffix(" deg")

        self.rao_length_fraction_spin = QDoubleSpinBox()
        self.rao_length_fraction_spin.setRange(0.60, 1.00)
        self.rao_length_fraction_spin.setDecimals(3)
        self.rao_length_fraction_spin.setSingleStep(0.025)
        self.rao_length_fraction_spin.setValue(0.80)

        form.addRow("Nozzle Geometry Type", self.nozzle_geometry_combo)
        form.addRow("Conical Half Angle", self.conical_half_angle_spin)
        form.addRow("Rao Length Fraction", self.rao_length_fraction_spin)

        note = QLabel(
            "Rao length fraction is relative to an equivalent 15° conical nozzle. "
            "A value of 0.80 represents an 80% bell nozzle."
        )
        note.setWordWrap(True)

        layout.addWidget(nozzle_group)
        layout.addWidget(note)
        layout.addStretch(1)

    def get_inputs(self):
        return {
            "nozzle_geometry_model": self.nozzle_geometry_combo.currentData(),
            "conical_half_angle_deg": self.conical_half_angle_spin.value(),
            "rao_length_fraction": self.rao_length_fraction_spin.value(),
        }

    def set_inputs(self, values):
        if not isinstance(values, dict):
            return

        model = values.get("nozzle_geometry_model")

        if model is not None:
            for index in range(self.nozzle_geometry_combo.count()):
                if self.nozzle_geometry_combo.itemData(index) == model:
                    self.nozzle_geometry_combo.setCurrentIndex(index)
                    break

        if values.get("conical_half_angle_deg") is not None:
            self.conical_half_angle_spin.setValue(
                float(values.get("conical_half_angle_deg"))
            )

        if values.get("rao_length_fraction") is not None:
            self.rao_length_fraction_spin.setValue(
                float(values.get("rao_length_fraction"))
            )