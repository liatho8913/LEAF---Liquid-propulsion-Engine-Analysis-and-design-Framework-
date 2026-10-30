from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QWidget,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
    QFileDialog,
    QTextEdit,
    QCheckBox,
    QGroupBox,
    QCompleter
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from variable_registry import LABEL_TO_VAR, UNITS, get_graphable_labels
from graph_explorer_engine import GraphExplorerEngine

from propellant_database import (
    canonical_fuel,
    canonical_oxidizer,
    get_all_fuel_options,
    get_all_oxidizer_options,
    get_oxidizer_display_name,
    get_compatible_oxidizers_for_fuel,
    get_compatible_fuels_for_oxidizer,
    is_compatible_pair,
    get_of_ratio_range_for_pair,
)

PREFERRED_X_LABELS = [
    "Mixture Ratio",
    "Selected Length",
    "Chamber Pressure",
    "Mass Flow Rate",
    "Coolant Channel Width",
    "Coolant Channel Height",
    "Coolant Flow Fraction",
]

PREFERRED_Y_LABELS = [
    "Corrected Thrust",
    "Thrust",
    "Specific Impulse",
    "Selected Mach Number",
    "Static Pressure",
    "Static Temperature",
    "Hot-Gas-Side Wall Temperature",
    "Material Temperature Margin",
    "Regen Heat Flux",
    "Coolant Pressure Drop",
]

AXIAL_PROFILE_PRESETS = {
    "Hot Wall Temperature": {
        "x_key": "x",
        "y_key": "hot_gas_side_wall_temperature",
        "x_label": "Nozzle Position",
        "y_label": "Hot Wall Temperature",
        "x_unit": "m",
        "y_unit": "K",
    },
    "Coolant Wall Temperature": {
        "x_key": "x",
        "y_key": "coolant_side_wall_temperature",
        "x_label": "Nozzle Position",
        "y_label": "Coolant Wall Temperature",
        "x_unit": "m",
        "y_unit": "K",
    },
    "Coolant Temperature": {
        "x_key": "x",
        "y_key": "coolant_temperature",
        "x_label": "Nozzle Position",
        "y_label": "Coolant Temperature",
        "x_unit": "m",
        "y_unit": "K",
    },
    "Heat Flux": {
        "x_key": "x",
        "y_key": "regen_heat_flux",
        "x_label": "Nozzle Position",
        "y_label": "Heat Flux",
        "x_unit": "m",
        "y_unit": "W/m²",
    },
    "Reynolds Number": {
        "x_key": "x",
        "y_key": "coolant_reynolds_number",
        "x_label": "Nozzle Position",
        "y_label": "Coolant Reynolds Number",
        "x_unit": "m",
        "y_unit": "",
    },
    "Pressure Drop": {
        "x_key": "x",
        "y_key": "total_pressure_drop_so_far",
        "x_label": "Nozzle Position",
        "y_label": "Accumulated Pressure Drop",
        "x_unit": "m",
        "y_unit": "Pa",
    },
    "Mach Number": {
        "x_key": "x",
        "y_key": "mach",
        "x_label": "Nozzle Position",
        "y_label": "Mach Number",
        "x_unit": "m",
        "y_unit": "",
    },
}

class GraphExplorerWindow(QDialog):
    def __init__(self, parent, base_inputs):
        # RDSI 3L
        # Preserve launch-boundary metadata and explicit Regen evidence before
        # existing Graph Explorer input normalisation/filtering occurs.
        self._rdsi_graph_transport_snapshot = (
            dict(base_inputs)
            if isinstance(
                base_inputs,
                dict,
            )
            else
            {}
        )
        super().__init__(parent)

        raw_inputs = dict(base_inputs or {})

        self.engine = GraphExplorerEngine()

        self.base_inputs = self.engine.prepare_graph_inputs(
            raw_inputs
        )

        # Presentation provenance transferred by the existing window-launch
        # owner.  Keep this separate from engineering base_inputs: Graph
        # Explorer consumes it only to decide which Regen design population
        # may be presented to the user.
        self._regen_active_design_mode = str(
            raw_inputs.get(
                "regen_design_mode"
            )
            or
            raw_inputs.get(
                "regen_design_mode_strategy"
            )
            or
            ""
        ).strip().lower()
        self.available_input_keys = list(
            self.base_inputs.pop(
                "__leaf_graph_available_input_keys__",
                [],
            )
            or
            []
        )

        self.regen_design_history = list(
            self.base_inputs.pop(
                "__leaf_graph_design_history__",
                [],
            )
            or
            []
        )

        axial_keys = {"x"}
        axial_keys.update(
            preset["y_key"]
            for preset in AXIAL_PROFILE_PRESETS.values()
        )

        axial_profile = raw_inputs.get(
            "regen_axial_profile",
            [],
        )

        if isinstance(axial_profile, list):
            self.base_inputs[
                "regen_axial_profile"
            ] = [
                {
                    key: station.get(key)
                    for key in axial_keys
                    if key in station
                }
                for station in axial_profile
                if isinstance(station, dict)
            ]

        evaluated_population = raw_inputs.get(
            "regen_candidate_evaluated_population",
            [],
        )

        if isinstance(
            evaluated_population,
            list,
        ):
            self.base_inputs[
                "regen_candidate_evaluated_population"
            ] = [
                candidate
                for candidate in evaluated_population
                if isinstance(
                    candidate,
                    dict,
                )
            ]

        self._regen_analysis_active = False
        self._regen_standard_x_items = []
        self._regen_standard_y_items = []


        self.label_to_var = LABEL_TO_VAR
        self.var_to_label = {
            var_name: label
            for label, var_name in self.label_to_var.items()
        }

        self.all_labels = list(self.label_to_var.keys())
        self.all_numeric_labels = get_graphable_labels()

        self.setWindowTitle("LEAF Graph Explorer")
        self.resize(1250, 900)

        self.last_graph_data = []

        self.current_design_point = None
        self.best_graph_point = None
        self.is_syncing = False

        # RDSI 3L
        # Existing Graph Explorer preparation is intentionally allowed to
        # normalise scalar engineering inputs. Transport-only UI discovery
        # metadata and explicit Regen geometry evidence are restored only
        # after that preparation has completed.
        _rdsi_transport = getattr(
            self,
            "_rdsi_graph_transport_snapshot",
            {},
        )

        if not isinstance(
            _rdsi_transport,
            dict,
        ):
            _rdsi_transport = {}

        self.available_input_keys = list(
            _rdsi_transport.get(
                "__leaf_graph_available_input_keys__",
                [],
            )
            or
            []
        )

        self.regen_design_history = list(
            _rdsi_transport.get(
                "__leaf_graph_design_history__",
                [],
            )
            or
            []
        )

        if not isinstance(
            getattr(
                self,
                "base_inputs",
                None,
            ),
            dict,
        ):
            self.base_inputs = {}

        _rdsi_regen_keys = (
            "regen_viewer_manual_geometry_snapshot",
            "regen_manual_geometry",
            "manual_regen_geometry",
            "regen_current_geometry",
            "regen_ui_applied_geometry",
            "regen_viewer_accepted_geometry",
            "regen_geometry_commit_staged_geometry",
            "regen_candidate_ranked_population",
            "regen_candidate_evaluated_population",
            "regen_candidate_populations_by_strategy",
            "regen_axial_profile",
            "regen_axial_profile_source_key",
            "regen_geometry_source_active",
            "regen_viewer_actual_geometry_source",
        )

        for _rdsi_key in _rdsi_regen_keys:

            if _rdsi_key not in _rdsi_transport:
                continue

            _rdsi_value = (
                _rdsi_transport.get(
                    _rdsi_key
                )
            )

            if isinstance(
                _rdsi_value,
                dict,
            ):
                _rdsi_value = dict(
                    _rdsi_value
                )

            elif isinstance(
                _rdsi_value,
                list,
            ):
                _rdsi_value = list(
                    _rdsi_value
                )

            self.base_inputs[
                _rdsi_key
            ] = _rdsi_value

        # Transport keys themselves are not engineering inputs.
        self.base_inputs.pop(
            "__leaf_graph_available_input_keys__",
            None,
        )

        self.base_inputs.pop(
            "__leaf_graph_design_history__",
            None,
        )

        # No longer needed after the constructor has restored the canonical
        # presentation/evidence state.
        self._rdsi_graph_transport_snapshot = {}

        # Build presentation controls only after the canonical launch-boundary
        # Regen evidence has been restored.  The Regen Design selector therefore
        # sees every explicitly generated strategy on its first population pass.
        self.create_layout()
        self.initialise_automatic_graph_defaults()

    def interpolate_y_from_series(self, x_values, y_values, target_x):
        points = sorted(
            [(float(x), float(y)) for x, y in zip(x_values, y_values)],
            key=lambda item: item[0]
        )

        if not points:
            return None

        target_x = float(target_x)

        if target_x < points[0][0] or target_x > points[-1][0]:
            return None

        for x, y in points:
            if abs(x - target_x) < 1e-12:
                return y

        for index in range(len(points) - 1):
            x0, y0 = points[index]
            x1, y1 = points[index + 1]

            if x0 <= target_x <= x1:
                if abs(x1 - x0) < 1e-12:
                    return y0

                fraction = (target_x - x0) / (x1 - x0)
                return y0 + fraction * (y1 - y0)

        return None

    def get_current_design_point(self, x_var, y_var, fuel=None, oxidizer=None):
        prepared_inputs = self.engine.prepare_graph_inputs(self.base_inputs)
        current_x = prepared_inputs.get(x_var)

        if current_x is None:
            return None, None

        point_inputs = dict(prepared_inputs)
        point_inputs[x_var] = float(current_x)

        if fuel is not None:
            point_inputs["fuel"] = canonical_fuel(fuel)

        if oxidizer is not None:
            point_inputs["oxidizer"] = canonical_oxidizer(oxidizer)

        solved = self.engine.solve_graph_point(
            base_inputs=point_inputs,
            x_var=x_var,
            x_value=current_x
        )

        current_y = self.engine.get_graph_y_value(
            solved=solved,
            y_var=y_var,
            graph_inputs=point_inputs
        )

        if current_y is None:
            return None, None

        return float(current_x), float(current_y)

    def make_combo_searchable(self, combo):
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)

        completer = combo.completer()
        if completer is not None:
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(QCompleter.PopupCompletion)

    def create_layout(self):
        outer_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        layout = QVBoxLayout(content)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

        title = QLabel("Graph Explorer")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.status_label = QLabel("Automatic Promethean-style dependency filtering and sweep scaling.")
        layout.addWidget(self.status_label)

        form = QFormLayout()

        self.graph_mode_selector = QComboBox()
        self.graph_mode_selector.addItems([
            "Variable Sweep",
            "Axial Regen Profile",
            "Regen Analysis",
        ])
        self.graph_mode_selector.currentTextChanged.connect(self.on_graph_mode_changed)

        self.regen_analysis_source_selector = QComboBox()
        self.regen_analysis_source_selector.addItems([
            "Controlled Input Sweep",
            "Evaluated Candidate Scatter",
        ])
        self.regen_analysis_source_selector.setEnabled(False)
        self.regen_analysis_source_selector.currentTextChanged.connect(
            self.on_regen_analysis_source_changed
        )

        self.regen_design_selector = QComboBox()
        self.regen_design_selector.currentIndexChanged.connect(
            lambda _index: self._refresh_regen_controlled_x_selector()
        )
        self.regen_design_selector.setEnabled(False)
        self.regen_design_selector.setToolTip(
            "Select the actual Regen geometry used as the fixed baseline "
            "for Controlled Input Sweep analysis."
        )
        self.regen_design_selector.currentIndexChanged.connect(
            self.on_regen_design_selection_changed
        )

        self.axial_preset_label = QLabel("Axial Preset")
        self.axial_preset_selector = QComboBox()
        self.axial_preset_selector.addItems(AXIAL_PROFILE_PRESETS.keys())
        self.axial_preset_selector.setEnabled(False)
        self.axial_preset_selector.setVisible(False)
        self.axial_preset_label.setVisible(False)

        self.x_selector = QComboBox()
        self.y_selector = QComboBox()

        self.make_combo_searchable(self.x_selector)
        self.make_combo_searchable(self.y_selector)
        self.make_combo_searchable(self.axial_preset_selector)

        self.x_selector.currentTextChanged.connect(self.on_x_variable_changed)
        self.y_selector.currentTextChanged.connect(self.on_y_variable_changed)

        self.points_entry = QLineEdit("50")
        self.auto_range_label = QLabel("Auto range: -")

        form.addRow("Graph Mode", self.graph_mode_selector)
        form.addRow(
            "Regen Evidence",
            self.regen_analysis_source_selector,
        )
        form.addRow(
            "Regen Design",
            self.regen_design_selector,
        )
        form.addRow(
            self.axial_preset_label,
            self.axial_preset_selector,
        )
        self.graph_mode_selector.currentTextChanged.connect(
            self._sync_axial_preset_visibility
        )
        self._sync_axial_preset_visibility()
        form.addRow("X Variable", self.x_selector)
        form.addRow("Y Variable", self.y_selector)
        form.addRow("Points per Line", self.points_entry)
        form.addRow("Automatic X Range", self.auto_range_label)

        layout.addLayout(form)

        comparison_group = QGroupBox("Fuel / Oxidizer Comparison")
        comparison_layout = QVBoxLayout(comparison_group)

        fuel_row = QHBoxLayout()
        oxidizer_row = QHBoxLayout()

        fuel_row.addWidget(QLabel("Fuels:"))
        oxidizer_row.addWidget(QLabel("Oxidizers:"))

        self.fuel_compare_checks = {}
        self.oxidizer_compare_checks = {}

        for fuel in get_all_fuel_options():
            checkbox = QCheckBox(fuel)
            checkbox.stateChanged.connect(self.refresh_comparison_checkboxes)
            self.fuel_compare_checks[fuel] = checkbox
            fuel_row.addWidget(checkbox)

        for oxidizer in get_all_oxidizer_options():
            checkbox = QCheckBox(
                get_oxidizer_display_name(
                    oxidizer
                )
            )
            checkbox.stateChanged.connect(self.refresh_comparison_checkboxes)
            self.oxidizer_compare_checks[oxidizer] = checkbox
            oxidizer_row.addWidget(checkbox)

        comparison_layout.addLayout(fuel_row)
        comparison_layout.addLayout(oxidizer_row)

        layout.addWidget(comparison_group)

        self.refresh_comparison_checkboxes()

        button_row = QHBoxLayout()

        self.generate_button = QPushButton("Generate Graph")
        self.generate_button.clicked.connect(self.generate_graph)

        self.export_button = QPushButton("Export Graph Data CSV")
        self.export_button.clicked.connect(self.export_graph_csv)
        self.copy_data_button = QPushButton("Copy Graph Data")
        self.copy_data_button.clicked.connect(self.copy_graph_data_to_clipboard)
        self.clear_cache_button = QPushButton("Clear Graph Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)

        button_row.addWidget(self.generate_button)
        button_row.addWidget(self.copy_data_button)
        button_row.addWidget(self.export_button)
        button_row.addWidget(self.clear_cache_button)

        layout.addLayout(button_row)

        self.figure = Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setMinimumHeight(520)
        self.canvas.setMaximumHeight(520)
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        layout.addWidget(self.canvas)

        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)

        self.interpretation_box = QTextEdit()
        self.interpretation_box.setReadOnly(True)
        self.interpretation_box.setMinimumHeight(220)
        self.interpretation_box.setMaximumHeight(280)
        self.interpretation_box.setPlaceholderText(
            "Graph interpretation will appear here after generation."
        )

        layout.addWidget(self.interpretation_box)

        self.comparison_box = QTextEdit()
        self.comparison_box.setReadOnly(True)
        self.comparison_box.setMinimumHeight(180)
        self.comparison_box.setMaximumHeight(240)

        layout.addWidget(self.comparison_box)

    def initialise_automatic_graph_defaults(self):
        candidate_x_vars = [
            self.label_to_var[label]
            for label in self.all_numeric_labels
            if label in self.label_to_var
        ]

        automatic_x_vars = self.engine.get_automatic_x_options(candidate_x_vars)

        automatic_x_labels = [
            self.var_to_label[var_name]
            for var_name in automatic_x_vars
            if var_name in self.var_to_label
        ]

        if not automatic_x_labels:
            automatic_x_labels = self.all_numeric_labels

        self.populate_x_selector(automatic_x_labels)

        for label in PREFERRED_X_LABELS:
            index = self.x_selector.findText(label)

            if index >= 0:
                self.x_selector.setCurrentIndex(index)
                break

        self.on_x_variable_changed()

    def current_var(self, selector):
        label = selector.currentText()
        return self.label_to_var.get(label), label

    def populate_x_selector(self, labels, preferred_current=None):
        current = preferred_current or self.x_selector.currentText()

        self.x_selector.blockSignals(True)
        self.x_selector.clear()

        for label in labels:
            self.x_selector.addItem(label)

        if current in labels:
            self.x_selector.setCurrentText(current)
        elif labels:
            self.x_selector.setCurrentIndex(0)

        self.x_selector.blockSignals(False)

    def populate_y_selector(self, labels, preferred_current=None):
        current = preferred_current or self.y_selector.currentText()

        self.y_selector.blockSignals(True)
        self.y_selector.clear()

        for label in labels:
            self.y_selector.addItem(label)

        if current in labels:
            self.y_selector.setCurrentText(current)
        else:
            self.select_preferred_y(labels)

        self.y_selector.blockSignals(False)

    def on_x_variable_changed(self):
        if (
            self.graph_mode_selector.currentText()
            == "Regen Analysis"
        ):
            if (
                hasattr(
                    self,
                    "regen_analysis_source_selector",
                )
                and
                self.regen_analysis_source_selector.currentText()
                == "Controlled Input Sweep"
            ):
                self._regen_controlled_update_auto_range()

            return

        if self.is_syncing:
            return

        self.is_syncing = True

        x_var, x_label = self.current_var(self.x_selector)

        if x_var is None:
            self.is_syncing = False
            return

        start, end = self.engine.default_start_end_for_var(
            x_var,
            self.base_inputs
        )

        unit = UNITS.get(x_var, "")
        unit_text = f" {unit}" if unit else ""
        self.auto_range_label.setText(f"{start:g} to {end:g}{unit_text}")

        candidate_y_vars = [
            self.label_to_var[label]
            for label in self.all_numeric_labels
            if label in self.label_to_var
        ]

        candidate_y_vars = self.engine.get_automatic_y_options(candidate_y_vars)

        y_vars = self.engine.get_y_options_for_x(
            x_var,
            candidate_y_vars,
            self.base_inputs,
        )

        filtered_y_labels = [
            self.var_to_label[var_name]
            for var_name in y_vars
            if var_name in self.var_to_label
        ]

        self.populate_y_selector(
            filtered_y_labels
        )

        self.status_label.setText(
            f"Automatic filter: {len(filtered_y_labels)} Y variables available for {x_label}."
        )

        self.is_syncing = False

    def on_y_variable_changed(self):
        if (
            self.graph_mode_selector.currentText()
            == "Regen Analysis"
        ):
            return

        if self.is_syncing:
            return

        self.is_syncing = True

        y_var, y_label = self.current_var(self.y_selector)

        if y_var is None:
            self.is_syncing = False
            return

        candidate_x_vars = [
            self.label_to_var[label]
            for label in self.all_numeric_labels
        ]

        x_vars = self.engine.get_x_options_for_y(
            y_var,
            candidate_x_vars,
            self.base_inputs,
        )

        filtered_x_labels = [
            self.var_to_label[var_name]
            for var_name in x_vars
            if var_name in self.var_to_label
        ]

        current_x = self.x_selector.currentText()

        self.populate_x_selector(
            filtered_x_labels,
            preferred_current=current_x,
        )

        self.status_label.setText(
            f"Automatic filter: valid X variables found for {y_label}."
        )

        self.is_syncing = False

    def select_preferred_y(self, labels):
        for label in PREFERRED_Y_LABELS:
            if label in labels:
                self.y_selector.setCurrentText(label)
                return

        if labels:
            self.y_selector.setCurrentIndex(0)

    def get_point_count(self):
        try:
            requested = int(self.points_entry.text().strip())
        except Exception:
            requested = 50

        return max(5, min(requested, 250))

    def on_graph_mode_changed(self):
        mode = self.graph_mode_selector.currentText()

        if mode == "Regen Analysis":
            self._enter_regen_analysis_mode()
            return

        self._leave_regen_analysis_mode()

        is_axial_mode = (
            self.graph_mode_selector.currentText()
            ==
            "Axial Regen Profile"
        )

        # Axial analysis is design-aware.  The selector remains enabled so the
        # user chooses the exact Manual / Automatic / saved Regen design whose
        # station solution will be plotted.
        self.regen_design_selector.setEnabled(
            is_axial_mode
        )

        self.axial_preset_selector.setEnabled(
            is_axial_mode
        )

        self.x_selector.setEnabled(
            not is_axial_mode
        )

        self.y_selector.setEnabled(
            not is_axial_mode
        )

        self.points_entry.setEnabled(
            not is_axial_mode
        )

        for checkbox in self.fuel_compare_checks.values():
            checkbox.setEnabled(
                not is_axial_mode
            )

        for checkbox in self.oxidizer_compare_checks.values():
            checkbox.setEnabled(
                not is_axial_mode
            )

    def get_current_fuel(self):
        return canonical_fuel(
            self.base_inputs.get("fuel")
            or self.base_inputs.get("selected_fuel")
            or self.base_inputs.get("cea_fuel")
        )

    def get_current_oxidizer(self):
        return canonical_oxidizer(
            self.base_inputs.get("oxidizer")
            or self.base_inputs.get("selected_oxidizer")
            or self.base_inputs.get("cea_oxidizer")
        )

    def get_compatible_oxidizers_for_fuel(self, fuel):
        return get_compatible_oxidizers_for_fuel(fuel)

    def get_compatible_fuels_for_oxidizer(self, oxidizer):
        return get_compatible_fuels_for_oxidizer(oxidizer)

    def get_selected_fuel_comparisons(self):
        return [
            fuel
            for fuel, checkbox in self.fuel_compare_checks.items()
            if checkbox.isChecked()
        ]

    def get_selected_oxidizer_comparisons(self):
        return [
            oxidizer
            for oxidizer, checkbox in self.oxidizer_compare_checks.items()
            if checkbox.isChecked()
        ]

    def refresh_comparison_checkboxes(self):
        if getattr(self, "is_syncing", False):
            return

        self.is_syncing = True

        current_fuel = self.get_current_fuel()
        current_oxidizer = self.get_current_oxidizer()

        selected_fuels = [
            canonical_fuel(fuel)
            for fuel, checkbox in self.fuel_compare_checks.items()
            if checkbox.isChecked()
        ]

        selected_oxidizers = [
            canonical_oxidizer(oxidizer)
            for oxidizer, checkbox in self.oxidizer_compare_checks.items()
            if checkbox.isChecked()
        ]

        if not selected_fuels:
            selected_fuels = [current_fuel]

        if not selected_oxidizers:
            selected_oxidizers = [current_oxidizer]

        allowed_oxidizers = set()

        for fuel in selected_fuels:
            allowed_oxidizers.update(
                get_compatible_oxidizers_for_fuel(fuel)
            )

        allowed_fuels = set()

        for oxidizer in selected_oxidizers:
            allowed_fuels.update(
                get_compatible_fuels_for_oxidizer(oxidizer)
            )

        for fuel, checkbox in self.fuel_compare_checks.items():
            canonical = canonical_fuel(fuel)

            checkbox.blockSignals(True)
            checkbox.setVisible(canonical in allowed_fuels or canonical in selected_fuels)

            if canonical == current_fuel and not any(
                    cb.isChecked() for cb in self.fuel_compare_checks.values()
            ):
                checkbox.setChecked(True)

            checkbox.blockSignals(False)

        for oxidizer, checkbox in self.oxidizer_compare_checks.items():
            canonical = canonical_oxidizer(oxidizer)

            checkbox.blockSignals(True)
            checkbox.setVisible(canonical in allowed_oxidizers or canonical in selected_oxidizers)

            if canonical == current_oxidizer and not any(
                    cb.isChecked() for cb in self.oxidizer_compare_checks.values()
            ):
                checkbox.setChecked(True)

            checkbox.blockSignals(False)

        self.is_syncing = False

    def generate_axial_profile_graph(self):
        selected_payload = (
            self._selected_regen_design_payload()
        )

        metadata = selected_payload.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        selected_design_label = str(
            selected_payload.get(
                "label"
            )
            or
            "[Manual] Current Geometry"
        )

        selected_source = str(
            selected_payload.get(
                "source"
            )
            or
            ""
        )

        geometry_type = str(
            metadata.get(
                "geometry_type"
            )
            or
            ""
        ).upper()

        strategy = str(
            metadata.get(
                "regen_design_strategy"
            )
            or
            ""
        ).strip().lower()

        material_name = (
            metadata.get(
                "candidate_material_name"
            )
        )

        is_manual = (
            not selected_payload
            or
            geometry_type
            ==
            "MANUAL"
            or
            selected_source
            ==
            "REGEN_VIEWER_MANUAL"
        )

        profile_context = self.base_inputs

        if is_manual:
            profile = self.base_inputs.get(
                "regen_axial_profile",
                [],
            )

            solution_source = (
                "existing solved Manual Regen profile"
            )

        else:
            design_inputs = (
                selected_payload.get(
                    "design_inputs",
                    {},
                )
            )

            # Geometry + Materials is only scientifically meaningful when its
            # canonical material/design input payload survived transport.
            if (
                strategy
                ==
                "automatic_geometry_materials"
                and
                not (
                    isinstance(
                        design_inputs,
                        dict,
                    )
                    and
                    design_inputs
                )
            ):
                QMessageBox.warning(
                    self,
                    "Candidate Input Provenance Missing",
                    (
                        "The selected Geometry + Materials design does not "
                        "carry its canonical candidate design-input payload. "
                        "LEAF will not solve it using the current engine "
                        "material state."
                    ),
                )

                return

            baseline = (
                self._regen_selected_baseline_inputs()
            )

            try:
                solved = (
                    self.engine.solve_full_state(
                        baseline,
                        y_var=
                            "regen_axial_profile",
                    )
                )

            except Exception as exc:
                QMessageBox.warning(
                    self,
                    "Axial Design Solve Failed",
                    (
                        "The selected Regen design could not be solved "
                        "through the canonical LEAF calculation bridge.\n\n"
                        f"{exc}"
                    ),
                )

                return

            if not isinstance(
                solved,
                dict,
            ):
                solved = {}

            profile = (
                solved.get(
                    "regen_axial_profile"
                )
                or
                solved.get(
                    "recommended_regen_axial_profile"
                )
                or
                []
            )

            profile_context = solved

            solution_source = (
                "on-demand canonical LEAF selected-design solve"
            )

        if not isinstance(
            profile,
            list,
        ) or not profile:
            QMessageBox.warning(
                self,
                "No Axial Profile",
                (
                    "No solved axial regenerative cooling profile is "
                    "available for the selected Regen design:\n\n"
                    f"{selected_design_label}"
                ),
            )

            return

        preset_name = (
            self.axial_preset_selector.currentText()
        )

        preset = (
            AXIAL_PROFILE_PRESETS.get(
                preset_name
            )
        )

        if not preset:
            return

        x_key = preset[
            "x_key"
        ]

        y_key = preset[
            "y_key"
        ]

        x_values = []
        y_values = []

        for station in profile:
            if not isinstance(
                station,
                dict,
            ):
                continue

            x = station.get(
                x_key
            )

            y = station.get(
                y_key
            )

            if (
                isinstance(
                    x,
                    (
                        int,
                        float,
                    ),
                )
                and
                isinstance(
                    y,
                    (
                        int,
                        float,
                    ),
                )
            ):
                x_values.append(
                    x
                )

                y_values.append(
                    y
                )

        if not x_values or not y_values:
            QMessageBox.warning(
                self,
                "No Plot Data",
                (
                    f"No numeric data found for {preset_name} "
                    f"on {selected_design_label}."
                ),
            )

            return

        self.figure.clear()

        axis = (
            self.figure.add_subplot(
                111
            )
        )

        series_label = (
            f"{selected_design_label} — "
            f"{preset_name}"
        )

        axis.plot(
            x_values,
            y_values,
            marker="o",
            label=series_label,
        )

        selected_length = (
            profile_context.get(
                "selected_length"
            )
            if isinstance(
                profile_context,
                dict,
            )
            else None
        )

        if not isinstance(
            selected_length,
            (
                int,
                float,
            ),
        ):
            selected_length = (
                self.base_inputs.get(
                    "selected_length"
                )
            )

        if isinstance(
            selected_length,
            (
                int,
                float,
            ),
        ):
            axis.axvline(
                selected_length,
                linestyle="--",
                linewidth=1,
                label="Selected Length",
            )

        x_unit = preset.get(
            "x_unit",
            "",
        )

        y_unit = preset.get(
            "y_unit",
            "",
        )

        x_axis_label = preset[
            "x_label"
        ]

        y_axis_label = preset[
            "y_label"
        ]

        if x_unit:
            x_axis_label += (
                f" ({x_unit})"
            )

        if y_unit:
            y_axis_label += (
                f" ({y_unit})"
            )

        axis.set_xlabel(
            x_axis_label
        )

        axis.set_ylabel(
            y_axis_label
        )

        axis.set_title(
            (
                f"{preset['y_label']} vs "
                f"{preset['x_label']}\n"
                f"{selected_design_label}"
            )
        )

        axis.grid(
            True
        )

        axis.legend()

        self.canvas.draw()

        self.last_graph_data = [
            (
                selected_design_label,
                x,
                y,
            )
            for x, y
            in zip(
                x_values,
                y_values,
            )
        ]

        self.last_graph_series = {
            selected_design_label: {
                "x":
                    x_values,

                "y":
                    y_values,

                "fuel":
                    self.get_current_fuel(),

                "oxidizer":
                    self.get_current_oxidizer(),

                "regen_design":
                    selected_design_label,

                "material":
                    material_name,
            }
        }

        min_y = min(
            y_values
        )

        max_y = max(
            y_values
        )

        min_index = (
            y_values.index(
                min_y
            )
        )

        max_index = (
            y_values.index(
                max_y
            )
        )

        y_unit_text = (
            f" {y_unit}"
            if y_unit
            else
            ""
        )

        x_unit_text = (
            f" {x_unit}"
            if x_unit
            else
            ""
        )

        material_text = (
            str(
                material_name
            )
            if material_name
            else
            "current selected material"
        )

        self.summary_label.setText(
            (
                f"{selected_design_label} | "
                f"{preset_name}: "
                f"min {min_y:.6g}{y_unit_text} "
                f"at x={x_values[min_index]:.6g}{x_unit_text}; "
                f"max {max_y:.6g}{y_unit_text} "
                f"at x={x_values[max_index]:.6g}{x_unit_text}."
            )
        )

        self.interpretation_box.setPlainText(
            (
                "AXIAL PROFILE INTERPRETATION\n"
                "===========================\n\n"
                f"Regen design: {selected_design_label}\n"
                f"Material context: {material_text}\n"
                f"Solution source: {solution_source}\n"
                f"Station count: {len(profile)}\n\n"
                f"This plot shows {preset['y_label']} along the nozzle "
                "from throat to exit.\n\n"
                f"Minimum: {min_y:.6g}{y_unit_text} at x = "
                f"{x_values[min_index]:.6g}{x_unit_text}\n"
                f"Maximum: {max_y:.6g}{y_unit_text} at x = "
                f"{x_values[max_index]:.6g}{x_unit_text}\n\n"
                "The dashed vertical line marks the selected nozzle length, "
                "if available."
            )
        )

        self.comparison_box.setPlainText(
            (
                "Axial profile mode uses solved regenerative cooling station "
                "data for the explicitly selected Regen design. Automatic "
                "designs are solved ephemerally through the existing canonical "
                "LEAF calculation bridge; selecting or plotting a candidate "
                "does not accept or commit that design."
            )
        )


    @staticmethod
    def _regen_analysis_value(record, path):
        current = record

        for part in path.split("."):
            if not isinstance(current, dict):
                return None

            current = current.get(part)

        return current


    @staticmethod
    def _regen_analysis_numeric(value):
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        return None


    @staticmethod
    def _regen_analysis_x_options():
        return {
            "Coolant Channel Width": {
                "path": "candidate_geometry.coolant_channel_width",
                "unit": "m",
            },
            "Coolant Channel Height": {
                "path": "candidate_geometry.coolant_channel_height",
                "unit": "m",
            },
            "Number of Coolant Channels": {
                "path": "candidate_geometry.number_of_coolant_channels",
                "unit": "",
            },
            "Rib Width": {
                "path": "candidate_geometry.rib_width",
                "unit": "m",
            },
        }


    @staticmethod
    def _regen_analysis_y_options():
        return {
            "Coolant Pressure Drop": {
                "path": (
                    "regen_qualification_report.constraints."
                    "coolant_pressure_drop.predicted_value"
                ),
                "unit": "Pa",
            },
            "Pressure Drop Margin": {
                "path": (
                    "regen_qualification_report.constraints."
                    "coolant_pressure_drop.reserve"
                ),
                "unit": "Pa",
            },
            "Minimum Coolant Reynolds Number": {
                "path": (
                    "regen_qualification_report.constraints."
                    "coolant_reynolds.predicted_value"
                ),
                "unit": "",
            },
            "Reynolds Margin": {
                "path": (
                    "regen_qualification_report.constraints."
                    "coolant_reynolds.reserve"
                ),
                "unit": "",
            },
            "Maximum Coolant Velocity": {
                "path": (
                    "regen_qualification_report.constraints."
                    "coolant_velocity.predicted_value"
                ),
                "unit": "m/s",
            },
            "Coolant Velocity Margin": {
                "path": (
                    "regen_qualification_report.constraints."
                    "coolant_velocity.reserve"
                ),
                "unit": "m/s",
            },
            "Maximum Hot-Gas Wall Temperature": {
                "path": (
                    "regen_qualification_report.constraints."
                    "material_temperature.predicted_value"
                ),
                "unit": "K",
            },
            "Material Temperature Margin": {
                "path": (
                    "regen_qualification_report.constraints."
                    "material_temperature.reserve"
                ),
                "unit": "K",
            },
            "Geometry Fit": {
                "path": (
                    "regen_qualification_report.constraints."
                    "geometry_fit.predicted_value"
                ),
                "unit": "",
            },
            "Geometry Fit Margin": {
                "path": (
                    "regen_qualification_report.constraints."
                    "geometry_fit.reserve"
                ),
                "unit": "",
            },
        }


    @staticmethod
    def _regen_analysis_constraint_states(candidate):
        report = candidate.get(
            "regen_qualification_report",
            {}
        )

        if not isinstance(report, dict):
            return []

        constraints = report.get(
            "constraints",
            {}
        )

        if not isinstance(
            constraints,
            dict,
        ):
            return []

        states = []

        for constraint in constraints.values():
            if not isinstance(
                constraint,
                dict,
            ):
                continue

            status = constraint.get(
                "status"
            )

            if status is None:
                continue

            states.append(
                str(status).upper()
            )

        return states


    @classmethod
    def _regen_analysis_candidate_state(
        cls,
        candidate,
    ):
        states = (
            cls._regen_analysis_constraint_states(
                candidate
            )
        )

        if any(
            state == "FAIL"
            or state.startswith("FAIL_")
            for state in states
        ):
            return "FAIL"

        if any(
            state == "UNPROVEN"
            or state.startswith("UNPROVEN_")
            for state in states
        ):
            return "UNPROVEN"

        if (
            candidate.get(
                "regen_qualification_pass"
            )
            is True
        ):
            return "PASS"

        if (
            candidate.get(
                "regen_qualification_enforcement_ready"
            )
            is not True
        ):
            return "UNPROVEN"

        if (
            candidate.get(
                "regen_qualification_pass"
            )
            is False
        ):
            return "FAIL"

        return "UNPROVEN"


    @classmethod
    def _regen_analysis_failed_constraints(
        cls,
        candidate,
    ):
        report = candidate.get(
            "regen_qualification_report",
            {}
        )

        if not isinstance(
            report,
            dict,
        ):
            return []

        constraints = report.get(
            "constraints",
            {}
        )

        if not isinstance(
            constraints,
            dict,
        ):
            return []

        failed = []

        for name, constraint in (
            constraints.items()
        ):
            if not isinstance(
                constraint,
                dict,
            ):
                continue

            state = str(
                constraint.get(
                    "status",
                    ""
                )
            ).upper()

            if (
                state == "FAIL"
                or
                state.startswith("FAIL_")
            ):
                failed.append(
                    str(name)
                )

        return failed


    @classmethod
    def _regen_analysis_controlled_sweep(
        cls,
        population,
        selected_x_path,
    ):
        """
        Hard feasibility regions require explicit controlled-sweep
        evidence AND one-dimensional input variation.

        An uncontrolled multidimensional candidate population can never
        satisfy this contract.
        """
        if not population:
            return False

        explicit_control_evidence = False

        for candidate in population:
            if not isinstance(
                candidate,
                dict,
            ):
                return False

            stack = [
                candidate
            ]

            candidate_has_control = False

            while stack:
                current = stack.pop()

                if not isinstance(
                    current,
                    dict,
                ):
                    continue

                for key, value in (
                    current.items()
                ):
                    lower_key = str(
                        key
                    ).lower()

                    if isinstance(
                        value,
                        dict,
                    ):
                        stack.append(
                            value
                        )

                    if (
                        "controlled_sweep"
                        in lower_key
                        and
                        value is True
                    ):
                        candidate_has_control = (
                            True
                        )

            explicit_control_evidence = (
                explicit_control_evidence
                or
                candidate_has_control
            )

        if not explicit_control_evidence:
            return False

        input_paths = [
            "candidate_geometry.coolant_channel_width",
            "candidate_geometry.coolant_channel_height",
            "candidate_geometry.number_of_coolant_channels",
            "candidate_geometry.rib_width",
        ]

        for path in input_paths:
            if path == selected_x_path:
                continue

            values = []

            for candidate in population:
                value = cls._regen_analysis_numeric(
                    cls._regen_analysis_value(
                        candidate,
                        path,
                    )
                )

                if value is not None:
                    values.append(
                        round(
                            value,
                            14,
                        )
                    )

            if len(
                set(values)
            ) > 1:
                return False

        return True


    @classmethod
    def _regen_analysis_hard_fail_intervals(
        cls,
        population,
        selected_x_path,
    ):
        if not cls._regen_analysis_controlled_sweep(
            population,
            selected_x_path,
        ):
            return []

        points = []

        for candidate in population:
            x_value = cls._regen_analysis_numeric(
                cls._regen_analysis_value(
                    candidate,
                    selected_x_path,
                )
            )

            if x_value is None:
                continue

            points.append(
                (
                    x_value,
                    cls._regen_analysis_candidate_state(
                        candidate
                    ),
                )
            )

        points.sort(
            key=lambda item: item[0]
        )

        unique_points = []

        for x_value, state in points:
            existing = next(
                (
                    item
                    for item in unique_points
                    if item[0] == x_value
                ),
                None,
            )

            if existing is None:
                unique_points.append(
                    [
                        x_value,
                        {state},
                    ]
                )
            else:
                existing[1].add(
                    state
                )

        if len(
            unique_points
        ) < 2:
            return []

        intervals = []

        x_values = [
            item[0]
            for item in unique_points
        ]

        for index, (
            x_value,
            states,
        ) in enumerate(
            unique_points
        ):
            if states != {"FAIL"}:
                continue

            if index == 0:
                left = x_value
            else:
                left = (
                    x_values[
                        index - 1
                    ]
                    +
                    x_value
                ) / 2.0

            if (
                index
                ==
                len(
                    x_values
                )
                -
                1
            ):
                right = x_value
            else:
                right = (
                    x_value
                    +
                    x_values[
                        index + 1
                    ]
                ) / 2.0

            if right > left:
                intervals.append(
                    (
                        left,
                        right,
                    )
                )

        return intervals


    def _regen_analysis_population(self):
        population = self.base_inputs.get(
            "regen_candidate_evaluated_population",
            [],
        )

        if not isinstance(
            population,
            list,
        ):
            return []

        return [
            candidate
            for candidate in population
            if isinstance(
                candidate,
                dict,
            )
        ]


    @staticmethod
    def _combo_snapshot(combo):
        return [
            (
                combo.itemText(index),
                combo.itemData(index),
            )
            for index in range(
                combo.count()
            )
        ]


    @staticmethod
    def _restore_combo_snapshot(
        combo,
        items,
    ):
        combo.blockSignals(
            True
        )

        combo.clear()

        for text, data in items:
            combo.addItem(
                text,
                data,
            )

        combo.blockSignals(
            False
        )


    @staticmethod
    def _regen_controlled_y_options():
        """
        Regen metrics with existing solver-owned engineering status or limits.

        Graph Explorer does not establish any new threshold here.
        """
        return {
            "Maximum Hot-Gas Wall Temperature": {
                "value_keys": (
                    "regen_axial_max_hot_wall_temperature",
                    "hot_gas_side_wall_temperature",
                ),
                "limit_keys": (
                    "effective_material_temperature_limit",
                    "material_max_wall_temperature",
                    "material_max_service_temperature",
                    "sourced_material_temperature_limit",
                ),
                "status_key":
                    "regen_thermal_status",
                "relation":
                    "maximum",
                "unit":
                    "K",
                "limit_label":
                    "Material Temperature Limit",
            },

            "Material Temperature Margin": {
                "value_keys": (
                    "regen_axial_worst_material_margin",
                    "regen_axial_material_temperature_margin",
                    "material_temperature_margin",
                ),
                "limit_keys":
                    (),
                "status_key":
                    "regen_thermal_status",
                "relation":
                    "minimum_zero",
                "unit":
                    "K",
                "limit_label":
                    "Zero Material Margin",
            },

            "Minimum Coolant Reynolds Number": {
                "value_keys": (
                    "regen_axial_min_reynolds_number",
                    "coolant_reynolds_number",
                ),
                "limit_keys":
                    (),
                "status_key":
                    "regen_coolant_status",
                "relation":
                    "status",
                "unit":
                    "",
                "limit_label":
                    "Canonical Coolant Status",
            },

            "Maximum Coolant Velocity": {
                "value_keys": (
                    "regen_axial_max_coolant_velocity",
                    "coolant_velocity",
                ),
                "limit_keys": (
                    "regen_derived_maximum_coolant_velocity",
                    "regen_max_coolant_velocity",
                    "full_engine_regen_max_velocity",
                    "maximum_allowed_coolant_velocity",
                ),
                "status_key":
                    None,
                "relation":
                    "maximum",
                "unit":
                    "m/s",
                "limit_label":
                    "Maximum Coolant Velocity",
            },

            "Coolant Pressure Drop": {
                "value_keys": (
                    "regen_axial_total_pressure_drop",
                    "coolant_pressure_drop_total",
                    "coolant_pressure_drop",
                ),
                "limit_keys": (
                    "regen_derived_pressure_drop_limit",
                    "regen_pressure_drop_limit",
                ),
                "status_key":
                    None,
                "relation":
                    "maximum",
                "unit":
                    "Pa",
                "limit_label":
                    "Regen Pressure-Drop Limit",
            },
        }


    @classmethod
    def _regen_controlled_first_numeric(
        cls,
        solved,
        keys,
    ):
        for key in keys:

            value = cls._regen_analysis_numeric(
                solved.get(
                    key
                )
            )

            if value is not None:
                return value

        return None


    @classmethod
    def _regen_controlled_metric_state(
        cls,
        solved,
        option,
        value,
        limit,
    ):
        """
        Presentation-only state from the existing solver-owned status/limit.
        """
        status_key = option.get(
            "status_key"
        )

        if status_key:

            raw_status = str(
                solved.get(
                    status_key
                )
                or
                ""
            ).upper()

            if raw_status == "FAIL":
                return "FAIL"

            if raw_status == "PASS":
                return "PASS"

            if raw_status == "WARN":
                return "WARN"

        relation = option.get(
            "relation"
        )

        if relation == "minimum_zero":

            if value is None:
                return "UNPROVEN"

            return (
                "PASS"
                if value >= 0.0
                else
                "FAIL"
            )

        if (
            relation == "maximum"
            and
            value is not None
            and
            limit is not None
        ):
            return (
                "PASS"
                if value <= limit
                else
                "FAIL"
            )

        return "UNPROVEN"


    @classmethod
    def _regen_controlled_fail_intervals(
        cls,
        records,
    ):
        """
        Build red X cells from actual controlled solved FAIL samples.

        This is not multidimensional candidate interpolation.
        """
        points = sorted(
            (
                record["x"],
                record["state"],
            )
            for record in records
            if record.get(
                "x"
            ) is not None
        )

        if len(points) < 2:
            return []

        collapsed = []

        for x_value, state in points:

            existing = next(
                (
                    item
                    for item in collapsed
                    if item[0] == x_value
                ),
                None,
            )

            if existing is None:
                collapsed.append(
                    [
                        x_value,
                        {state},
                    ]
                )

            else:
                existing[1].add(
                    state
                )

        if len(collapsed) < 2:
            return []

        x_values = [
            item[0]
            for item in collapsed
        ]

        intervals = []

        for index, (
            x_value,
            states,
        ) in enumerate(
            collapsed
        ):

            if states != {"FAIL"}:
                continue

            if index == 0:
                left = x_value

            else:
                left = (
                    x_values[
                        index - 1
                    ]
                    +
                    x_value
                ) / 2.0

            if (
                index
                ==
                len(x_values)
                -
                1
            ):
                right = x_value

            else:
                right = (
                    x_value
                    +
                    x_values[
                        index + 1
                    ]
                ) / 2.0

            if right > left:
                intervals.append(
                    (
                        left,
                        right,
                    )
                )

        return intervals


    @staticmethod
    def _normalise_regen_design_geometry(
        geometry,
    ):
        if not isinstance(
            geometry,
            dict,
        ):
            return {}

        aliases = {
            "channel_width":
                "coolant_channel_width",

            "coolant_channel_width":
                "coolant_channel_width",

            "channel_height":
                "coolant_channel_height",

            "coolant_channel_height":
                "coolant_channel_height",

            "requested_rib_width":
                "rib_width",

            "rib_width":
                "rib_width",

            "channel_count":
                "number_of_coolant_channels",

            "number_of_coolant_channels":
                "number_of_coolant_channels",

            "wall":
                "hot_gas_wall_thickness",

            "wall_thickness":
                "hot_gas_wall_thickness",

            "hot_gas_wall_thickness":
                "hot_gas_wall_thickness",

            "outer_wall_thickness":
                "outer_wall_thickness",

            "jacket":
                "outer_jacket_thickness",

            "outer_jacket_thickness":
                "outer_jacket_thickness",

            "coolant_flow_fraction":
                "coolant_flow_fraction",
        }

        normalised = {}

        for source_key, target_key in aliases.items():

            if source_key not in geometry:
                continue

            value = geometry.get(
                source_key
            )

            if value is None:
                continue

            try:
                if (
                    target_key
                    ==
                    "number_of_coolant_channels"
                ):
                    value = int(
                        round(
                            float(
                                value
                            )
                        )
                    )

                else:
                    value = float(
                        value
                    )

            except (
                TypeError,
                ValueError,
            ):
                continue

            normalised[
                target_key
            ] = value

        return normalised


    @classmethod
    def _regen_design_signature(
        cls,
        geometry,
    ):
        geometry = (
            cls._normalise_regen_design_geometry(
                geometry
            )
        )

        if not geometry:
            return None

        return tuple(
            sorted(
                (
                    key,
                    round(
                        float(value),
                        12,
                    ),
                )
                for key, value
                in geometry.items()
            )
        )


    def _regen_design_options(
        self,
    ):
        """
        Return real Regen geometries produced or preserved by existing LEAF
        Regen owners.

        Selection here does not imply feasibility, ranking, recommendation,
        acceptance, or application. Graph Explorer is an analysis consumer.

        Sources:
        - current Manual geometry,
        - real accepted/applied geometry,
        - qualified ranked generated geometries,
        - all actually evaluated generated candidate geometries,
        - explicit Regen geometries preserved in design history.
        """
        options = []
        seen = set()

        # An explicit viewer-selected strategy is authoritative for
        # presentation.  Candidate population existence alone must never
        # imply that an Automatic strategy is active.
        active_strategy = str(
            getattr(
                self,
                "_regen_active_design_mode",
                "",
            )
            or
            ""
        ).strip().lower()

        explicit_strategy_present = (
            active_strategy
            in {
                "manual",
                "automatic_selected_material",
                "automatic_geometry_materials",
            }
        )

        def add_option(
            label,
            geometry,
            source,
            metadata=None,
            design_inputs=None,
        ):
            normalised = (
                self._normalise_regen_design_geometry(
                    geometry
                )
            )

            signature = (
                self._regen_design_signature(
                    normalised
                )
            )

            identity = (
                metadata.get(
                    "regen_design_strategy"
                )
                if isinstance(
                    metadata,
                    dict,
                )
                else
                None
            )

            if not identity:
                identity = (
                    metadata.get(
                        "geometry_type"
                    )
                    if isinstance(
                        metadata,
                        dict,
                    )
                    else
                    None
                )

            if not identity:
                identity = str(
                    source
                )

            candidate_identity = (
                metadata.get(
                    "candidate_id"
                )
                if isinstance(
                    metadata,
                    dict,
                )
                else None
            )

            seen_key = (
                str(
                    identity
                ),
                str(
                    candidate_identity
                    or
                    ""
                ),
                signature,
            )

            if (
                not normalised
                or
                signature is None
                or
                seen_key in seen
            ):
                return

            seen.add(
                seen_key
            )

            options.append(
                {
                    "label":
                        str(
                            label
                        ),

                    "geometry":
                        normalised,

                    "source":
                        str(
                            source
                        ),

                    "metadata":
                        (
                            dict(
                                metadata
                            )
                            if isinstance(
                                metadata,
                                dict,
                            )
                            else
                            {}
                        ),

                    "design_inputs":
                        (
                            dict(
                                design_inputs
                            )
                            if isinstance(
                                design_inputs,
                                dict,
                            )
                            else
                            {}
                        ),

                    "signature":
                        signature,
                }
            )

        def candidate_geometry(
            candidate,
        ):
            if not isinstance(
                candidate,
                dict,
            ):
                return {}

            # Candidate owners have used both wrapped and flat geometry
            # records historically. The existing geometry normaliser consumes
            # only recognised Regen geometry keys, so using the candidate
            # itself as the final fallback does not expose unrelated fields.
            return (
                candidate.get(
                    "candidate_geometry"
                )
                or
                candidate.get(
                    "geometry"
                )
                or
                candidate.get(
                    "input_patch"
                )
                or
                candidate
            )

        def candidate_status(
            candidate,
        ):
            if not isinstance(
                candidate,
                dict,
            ):
                return None

            for key in (
                "qualification_state",
                "qualification_status",
                "candidate_state",
                "candidate_status",
                "regen_overall_status",
                "overall_status",
                "status",
            ):
                value = candidate.get(
                    key
                )

                if (
                    isinstance(
                        value,
                        str,
                    )
                    and
                    value.strip()
                ):
                    return value.strip()

            return None

        # -------------------------------------------------------------
        # 1. Current Manual geometry
        # -------------------------------------------------------------
        manual = (
            self.base_inputs.get(
                "regen_viewer_manual_geometry_snapshot"
            )
            or
            self.base_inputs.get(
                "regen_manual_geometry"
            )
            or
            self.base_inputs.get(
                "manual_regen_geometry"
            )
            or
            {}
        )

        if isinstance(
            manual,
            dict,
        ) and manual:
            add_option(
                "[Manual] Current Geometry",
                manual,
                "REGEN_VIEWER_MANUAL",
                {
                    "geometry_type":
                        "MANUAL",
                },
            )

        # -------------------------------------------------------------
        # 2. Real accepted/applied geometry
        #
        # This is intentionally conditional. LEAF must never manufacture an
        # Accepted design merely to populate the Graph Explorer.
        # -------------------------------------------------------------
        accepted = (
            self.base_inputs.get(
                "regen_ui_applied_geometry"
            )
            or
            self.base_inputs.get(
                "regen_current_geometry"
            )
            or
            self.base_inputs.get(
                "regen_viewer_accepted_geometry"
            )
            or
            {}
        )

        if isinstance(
            accepted,
            dict,
        ) and accepted:
            add_option(
                "[Accepted] Current Geometry",
                accepted,
                "REGEN_VIEWER_ACCEPTED",
                {
                    "geometry_type":
                        "ACCEPTED",
                },
            )

        # -------------------------------------------------------------
        # 3. Strategy-specific generated designs
        #
        # Manual is represented separately above. Generated designs retain
        # the exact Automatic strategy that produced them:
        #   - Automatic — Selected Material
        #   - Automatic — Geometry + Materials
        #
        # Qualification state remains metadata; strategy is provenance.
        # -------------------------------------------------------------
        strategy_populations = (
            self.base_inputs.get(
                "regen_candidate_populations_by_strategy",
                {},
            )
        )

        if not isinstance(
            strategy_populations,
            dict,
        ):
            strategy_populations = {}

        # Captured strategy populations are explicit execution provenance.
        # Preserve every strategy that the user actually generated during
        # the Regen Viewer session, even when the active mode was returned
        # to Manual before Graph Explorer was opened.
        #
        # Do not re-enable the legacy generic candidate fallback here:
        # explicit_strategy_present continues to suppress uncaptured RPOP
        # data below.

        def compact_candidate_state(
            state,
        ):
            if not isinstance(
                state,
                str,
            ):
                return ""

            upper = state.strip().upper()

            if not upper:
                return ""

            if (
                "NOT_QUALIFIED"
                in upper
            ):
                return "Unqualified"

            if (
                "UNPROVEN"
                in upper
            ):
                return "Unproven"

            if (
                "FAIL"
                in upper
            ):
                return "Failed"

            if (
                "QUALIFIED"
                in upper
                or
                upper
                ==
                "PASS"
            ):
                return "Qualified"

            return state.replace(
                "_",
                " ",
            ).title()

        strategy_order = (
            (
                "automatic_selected_material",
                "Automatic — Selected Material",
            ),
            (
                "automatic_geometry_materials",
                "Automatic — Geometry + Materials",
            ),
        )

        for (
            strategy_key,
            default_strategy_label,
        ) in strategy_order:

            record = (
                strategy_populations.get(
                    strategy_key
                )
            )

            if not isinstance(
                record,
                dict,
            ):
                continue

            strategy_label = str(
                record.get(
                    "strategy_label"
                )
                or
                default_strategy_label
            )

            ranked_population = (
                record.get(
                    "ranked_population",
                    [],
                )
            )

            if isinstance(
                ranked_population,
                list,
            ):
                for index, candidate in enumerate(
                    ranked_population
                ):

                    if not isinstance(
                        candidate,
                        dict,
                    ):
                        continue

                    geometry = (
                        candidate_geometry(
                            candidate
                        )
                    )

                    if not geometry:
                        continue

                    candidate_id = (
                        candidate.get(
                            "candidate_id"
                        )
                        or
                        f"candidate-{index + 1}"
                    )

                    rank = candidate.get(
                        "candidate_rank",
                        index + 1,
                    )

                    state = (
                        compact_candidate_state(
                            candidate_status(
                                candidate
                            )
                        )
                    )

                    state_text = (
                        f" — {state}"
                        if state
                        else
                        ""
                    )

                    add_option(
                        (
                            f"[{strategy_label}] "
                            f"Rank {rank}"
                            f"{state_text}"
                        ),
                        geometry,
                        "REGEN_VIEWER_GENERATED_STRATEGY",
                        {
                            "geometry_type":
                                "AUTOMATIC_GENERATED",

                            "regen_design_strategy":
                                strategy_key,

                            "regen_design_strategy_label":
                                strategy_label,

                            "candidate_id":
                                candidate_id,

                            "candidate_rank":
                                rank,

                            "candidate_status":
                                candidate_status(
                                    candidate
                                ),

                            "candidate_material_name":
                                candidate.get(
                                    "candidate_material_name"
                                ),

                            "qualified_ranked":
                                True,
                        },
                        candidate.get(
                            "candidate_design_inputs"
                        ),
                    )

            evaluated_population = (
                record.get(
                    "evaluated_population",
                    [],
                )
            )

            if isinstance(
                evaluated_population,
                list,
            ):
                for index, candidate in enumerate(
                    evaluated_population
                ):

                    if not isinstance(
                        candidate,
                        dict,
                    ):
                        continue

                    geometry = (
                        candidate_geometry(
                            candidate
                        )
                    )

                    if not geometry:
                        continue

                    candidate_id = (
                        candidate.get(
                            "candidate_id"
                        )
                        or
                        f"candidate-{index + 1}"
                    )

                    state = (
                        compact_candidate_state(
                            candidate_status(
                                candidate
                            )
                        )
                    )

                    state_text = (
                        f" — {state}"
                        if state
                        else
                        ""
                    )

                    add_option(
                        (
                            f"[{strategy_label}] "
                            f"Candidate {index + 1:02d}"
                            f"{state_text}"
                        ),
                        geometry,
                        "REGEN_VIEWER_GENERATED_STRATEGY",
                        {
                            "geometry_type":
                                "AUTOMATIC_GENERATED",

                            "regen_design_strategy":
                                strategy_key,

                            "regen_design_strategy_label":
                                strategy_label,

                            "candidate_id":
                                candidate_id,

                            "candidate_status":
                                candidate_status(
                                    candidate
                                ),

                            "candidate_material_name":
                                candidate.get(
                                    "candidate_material_name"
                                ),

                            "qualified_ranked":
                                False,

                            "accepted":
                                False,
                        },
                        candidate.get(
                            "candidate_design_inputs"
                        ),
                    )

            display_geometry = (
                record.get(
                    "display_geometry"
                )
            )

            if (
                isinstance(
                    display_geometry,
                    dict,
                )
                and
                display_geometry
            ):
                add_option(
                    (
                        f"[{strategy_label}] "
                        "Current Generated Geometry"
                    ),
                    display_geometry,
                    "REGEN_VIEWER_GENERATED_STRATEGY",
                    {
                        "geometry_type":
                            "AUTOMATIC_GENERATED",

                        "regen_design_strategy":
                            strategy_key,

                        "regen_design_strategy_label":
                            strategy_label,

                        "qualified_ranked":
                            False,

                        "accepted":
                            False,
                    },
                )

        # -------------------------------------------------------------
        # 3. Qualified/ranked generated designs
        #
        # These retain priority in the selector. Evaluated population below
        # is deduplicated against these by geometry signature.
        # -------------------------------------------------------------
        ranked = (
            []
            if (
                explicit_strategy_present
                or
                strategy_populations
            )
            else
            self.base_inputs.get(
                "regen_candidate_ranked_population"
            )
        )

        if isinstance(
            ranked,
            list,
        ):
            for index, candidate in enumerate(
                ranked
            ):

                if not isinstance(
                    candidate,
                    dict,
                ):
                    continue

                candidate_id = (
                    candidate.get(
                        "candidate_id"
                    )
                    or
                    f"candidate-{index + 1}"
                )

                rank = candidate.get(
                    "candidate_rank",
                    index + 1,
                )

                geometry = (
                    candidate_geometry(
                        candidate
                    )
                )

                if not geometry:
                    continue

                state = (
                    candidate_status(
                        candidate
                    )
                )

                add_option(
                    (
                        f"[Automatic] Rank {rank} — "
                        f"{candidate_id}"
                    ),
                    geometry,
                    "REGEN_VIEWER_GENERATED",
                    {
                        "geometry_type":
                            "AUTOMATIC_GENERATED",

                        "candidate_id":
                            candidate_id,

                        "candidate_rank":
                            rank,

                        "candidate_status":
                            state,

                        "qualified_ranked":
                            True,
                    },
                )

        # -------------------------------------------------------------
        # 4. Every actually evaluated/generated candidate geometry
        #
        # A candidate may be FAIL or UNPROVEN and still be useful as a
        # controlled-sweep baseline. Listing it does NOT promote it into the
        # qualified/ranked or accepted population.
        # -------------------------------------------------------------
        evaluated = (
            []
            if (
                explicit_strategy_present
                or
                strategy_populations
            )
            else
            self.base_inputs.get(
                "regen_candidate_evaluated_population"
            )
        )

        if isinstance(
            evaluated,
            list,
        ):
            for index, candidate in enumerate(
                evaluated
            ):

                if not isinstance(
                    candidate,
                    dict,
                ):
                    continue

                candidate_id = (
                    candidate.get(
                        "candidate_id"
                    )
                    or
                    f"candidate-{index + 1}"
                )

                geometry = (
                    candidate_geometry(
                        candidate
                    )
                )

                if not geometry:
                    continue

                state = (
                    candidate_status(
                        candidate
                    )
                )

                state_text = (
                    f" — {state}"
                    if state
                    else
                    ""
                )

                add_option(
                    (
                        "[Automatic] Candidate — "
                        f"{candidate_id}"
                        f"{state_text}"
                    ),
                    geometry,
                    "REGEN_VIEWER_GENERATED_EVALUATED",
                    {
                        "geometry_type":
                            "AUTOMATIC_GENERATED",

                        "candidate_id":
                            candidate_id,

                        "candidate_status":
                            state,

                        "qualified_ranked":
                            False,

                        "accepted":
                            False,
                    },
                )

        # -------------------------------------------------------------
        # 5. Explicit Regen geometry stored in existing design history
        # -------------------------------------------------------------
        history = getattr(
            self,
            "regen_design_history",
            [],
        )

        if isinstance(
            history,
            list,
        ):
            for record in history:

                if not isinstance(
                    record,
                    dict,
                ):
                    continue

                results = record.get(
                    "results",
                    {},
                )

                if not isinstance(
                    results,
                    dict,
                ):
                    continue

                geometry = (
                    results.get(
                        "regen_viewer_manual_geometry_snapshot"
                    )
                    or
                    results.get(
                        "regen_ui_applied_geometry"
                    )
                    or
                    results.get(
                        "regen_current_geometry"
                    )
                    or
                    results.get(
                        "regen_viewer_accepted_geometry"
                    )
                    or
                    results.get(
                        "regen_manual_geometry"
                    )
                    or
                    {}
                )

                if not isinstance(
                    geometry,
                    dict,
                ) or not geometry:
                    continue

                iteration = record.get(
                    "iteration_number",
                    "?",
                )

                add_option(
                    (
                        f"[Saved] Iteration {iteration} — "
                        "Regen Geometry"
                    ),
                    geometry,
                    "DESIGN_HISTORY",
                    {
                        "geometry_type":
                            "SAVED_REGEN",

                        "iteration_number":
                            iteration,
                    },
                )

        return options


    def _refresh_regen_design_selector(
        self,
    ):
        selector = getattr(
            self,
            "regen_design_selector",
            None,
        )

        if selector is None:
            return False

        current_data = (
            selector.currentData()
        )

        previous_signature = (
            current_data.get(
                "signature"
            )
            if isinstance(
                current_data,
                dict,
            )
            else
            None
        )

        options = (
            self._regen_design_options()
        )

        selector.blockSignals(
            True
        )

        selector.clear()

        if not options:

            selector.addItem(
                "No Regen Geometry Available",
                None,
            )

            selector.setEnabled(
                False
            )

            selector.blockSignals(
                False
            )

            return False

        requested_index = None

        active_source = str(
            self.base_inputs.get(
                "regen_geometry_source_active"
            )
            or
            self.base_inputs.get(
                "regen_viewer_actual_geometry_source"
            )
            or
            ""
        ).lower()

        automatic_index = None
        manual_index = None

        for index, option in enumerate(
            options
        ):

            selector.addItem(
                option[
                    "label"
                ],
                option,
            )

            if (
                previous_signature is not None
                and
                option.get(
                    "signature"
                )
                ==
                previous_signature
            ):
                requested_index = index

            if (
                manual_index is None
                and
                option.get(
                    "source"
                )
                ==
                "REGEN_VIEWER_MANUAL"
            ):
                manual_index = index

            if (
                automatic_index is None
                and
                option.get(
                    "source"
                )
                ==
                "REGEN_VIEWER_ACCEPTED"
            ):
                automatic_index = index

        if requested_index is None:

            if (
                active_source
                ==
                "automatic"
                and
                automatic_index is not None
            ):
                requested_index = automatic_index

            elif manual_index is not None:
                requested_index = manual_index

            elif automatic_index is not None:
                requested_index = automatic_index

            else:
                requested_index = 0

        selector.setCurrentIndex(
            requested_index
        )

        selector.setEnabled(
            True
        )

        selector.blockSignals(
            False
        )

        return True


    def _selected_regen_design_payload(
        self,
    ):
        selector = getattr(
            self,
            "regen_design_selector",
            None,
        )

        if selector is None:
            return {}

        payload = selector.currentData()

        return (
            dict(
                payload
            )
            if isinstance(
                payload,
                dict,
            )
            else
            {}
        )


    def _regen_selected_baseline_inputs(
        self,
    ):
        baseline = dict(
            self.base_inputs
        )

        payload = (
            self._selected_regen_design_payload()
        )

        design_inputs = payload.get(
            "design_inputs",
            {},
        )

        if isinstance(
            design_inputs,
            dict,
        ):
            baseline.update(
                design_inputs
            )

        geometry = payload.get(
            "geometry",
            {},
        )

        if isinstance(
            geometry,
            dict,
        ):
            # Physical geometry remains authoritative over any duplicate
            # geometry values carried inside candidate_design_inputs.
            baseline.update(
                geometry
            )

        return baseline


    def on_regen_design_selection_changed(
        self,
        *args,
    ):
        if (
            getattr(
                self,
                "_regen_analysis_active",
                False,
            )
            and
            self.regen_analysis_source_selector.currentText()
            ==
            "Controlled Input Sweep"
        ):
            self._regen_controlled_update_auto_range()


    def _plot_regen_selected_design_current_point(
        self,
        axis,
        baseline_inputs,
        x_var,
        option,
    ):
        current_x = (
            self._regen_analysis_numeric(
                baseline_inputs.get(
                    x_var
                )
            )
        )

        if current_x is None:
            return None

        scope_y_var = option[
            "value_keys"
        ][0]

        try:
            solved = (
                self.engine.solve_graph_point(
                    baseline_inputs,
                    x_var,
                    current_x,
                    y_var=scope_y_var,
                )
            )

        except Exception:
            return None

        if not isinstance(
            solved,
            dict,
        ):
            return None

        current_y = (
            self._regen_controlled_first_numeric(
                solved,
                option[
                    "value_keys"
                ],
            )
        )

        if current_y is None:
            return None

        axis.scatter(
            [
                current_x
            ],
            [
                current_y
            ],
            marker="D",
            s=110,
            edgecolors="black",
            linewidths=1.4,
            label="Current Selected Regen Design",
        )

        axis.axvline(
            current_x,
            linestyle=":",
            linewidth=1.2,
        )

        return {
            "x":
                current_x,

            "y":
                current_y,

            "design":
                self._selected_regen_design_payload(),
        }

    def _regen_controlled_update_auto_range(
        self,
    ):
        if not getattr(
            self,
            "_regen_analysis_active",
            False,
        ):
            return

        if (
            self.regen_analysis_source_selector.currentText()
            !=
            "Controlled Input Sweep"
        ):
            return

        x_var = self.x_selector.currentData()

        if not isinstance(
            x_var,
            str,
        ):
            self.auto_range_label.setText(
                "Auto range: -"
            )
            return

        baseline_inputs = (
            self._regen_selected_baseline_inputs()
        )

        try:
            range_values = list(
                self.engine.get_sweep_values(
                    x_var,
                    baseline_inputs,
                    2,
                )
            )

        except Exception:
            range_values = []

        if len(
            range_values
        ) < 2:
            self.auto_range_label.setText(
                "Auto range: -"
            )
            return

        try:
            start = float(
                range_values[0]
            )

            end = float(
                range_values[-1]
            )

        except (
            TypeError,
            ValueError,
        ):
            self.auto_range_label.setText(
                "Auto range: -"
            )
            return

        unit = UNITS.get(
            x_var,
            "",
        )

        unit_text = (
            f" {unit}"
            if unit
            else
            ""
        )

        self.auto_range_label.setText(
            f"{start:g} to {end:g}{unit_text}"
        )


    def on_regen_analysis_source_changed(
        self,
    ):
        if (
            self.graph_mode_selector.currentText()
            ==
            "Regen Analysis"
        ):
            self._sync_regen_analysis_source_mode()


    def _regen_controlled_x_options_for_selected_design(
        self,
    ):
        """
        Return normal available LEAF inputs plus independent parameters carried
        by the selected real Regen geometry.

        The Regen Design selector chooses the baseline. Manual and Automatic
        therefore do not create duplicate copies of the same physical X variable.
        """
        baseline = (
            self._regen_selected_baseline_inputs()
        )

        payload = (
            self._selected_regen_design_payload()
        )

        geometry = payload.get(
            "geometry",
            {},
        )

        keys = []
        seen = set()

        def add_key(
            key,
        ):
            if (
                not isinstance(
                    key,
                    str,
                )
                or
                not key
                or
                key in seen
            ):
                return

            seen.add(
                key
            )

            keys.append(
                key
            )

        for key in (
            self.available_input_keys
            or
            []
        ):
            add_key(
                key
            )

        if isinstance(
            geometry,
            dict,
        ):
            for key in geometry:
                add_key(
                    key
                )

        fallback_labels = {
            "coolant_channel_width":
                "Coolant Channel Width",

            "coolant_channel_height":
                "Coolant Channel Height",

            "rib_width":
                "Rib Width",

            "number_of_coolant_channels":
                "Number of Coolant Channels",

            "hot_gas_wall_thickness":
                "Hot-Gas Wall Thickness",

            "outer_wall_thickness":
                "Outer Wall Thickness",

            "outer_jacket_thickness":
                "Outer Jacket Thickness",

            "coolant_flow_fraction":
                "Coolant Flow Fraction",
        }

        options = []

        for var_name in keys:

            if not (
                self.engine.is_sweepable_x_variable(
                    var_name,
                    baseline,
                )
            ):
                continue

            label = (
                self.var_to_label.get(
                    var_name
                )
                or
                fallback_labels.get(
                    var_name
                )
            )

            if not label:
                continue

            options.append(
                (
                    label,
                    var_name,
                )
            )

        return options

    def _refresh_regen_controlled_x_selector(
        self,
    ):
        """
        Rebuild controlled X choices when the selected Regen design changes.
        """
        if not getattr(
            self,
            "_regen_analysis_active",
            False,
        ):
            return

        source_selector = getattr(
            self,
            "regen_analysis_source_selector",
            None,
        )

        if (
            source_selector is None
            or
            source_selector.currentText()
            !=
            "Controlled Input Sweep"
        ):
            return

        previous = (
            self.x_selector.currentData()
        )

        self.x_selector.blockSignals(
            True
        )

        self.x_selector.clear()

        for (
            label,
            var_name,
        ) in (
            self._regen_controlled_x_options_for_selected_design()
        ):
            self.x_selector.addItem(
                label,
                var_name,
            )

        target_index = (
            self.x_selector.findData(
                previous
            )
            if previous is not None
            else
            -1
        )

        if target_index < 0:
            target_index = (
                self.x_selector.findData(
                    "mixture_ratio"
                )
            )

        if (
            target_index < 0
            and
            self.x_selector.count() > 0
        ):
            target_index = 0

        if target_index >= 0:
            self.x_selector.setCurrentIndex(
                target_index
            )

        self.x_selector.blockSignals(
            False
        )

    def _sync_axial_preset_visibility(
        self,
        *_args,
    ):
        """
        Axial Preset belongs only to the solved Axial Regen Profile mode.
        """
        is_axial = (
            self.graph_mode_selector.currentText()
            ==
            "Axial Regen Profile"
        )

        self.axial_preset_selector.setEnabled(
            is_axial
        )

        self.axial_preset_selector.setVisible(
            is_axial
        )

        self.axial_preset_label.setVisible(
            is_axial
        )

    def _sync_regen_analysis_source_mode(
        self,
    ):
        if not getattr(
            self,
            "_regen_analysis_active",
            False,
        ):
            return

        source = (
            self.regen_analysis_source_selector.currentText()
        )

        self.x_selector.blockSignals(
            True
        )

        self.y_selector.blockSignals(
            True
        )

        self.x_selector.clear()
        self.y_selector.clear()

        if source == "Controlled Input Sweep":

            self.regen_design_selector.setEnabled(
                True
            )

            self._refresh_regen_design_selector()

            for (
                label,
                var_name,
            ) in (
                self._regen_controlled_x_options_for_selected_design()
            ):
                self.x_selector.addItem(
                    label,
                    var_name,
                )

            for label, option in (
                self._regen_controlled_y_options()
                .items()
            ):
                self.y_selector.addItem(
                    label,
                    option[
                        "value_keys"
                    ][0],
                )

            preferred_x = (
                self.x_selector.findText(
                    "Mixture Ratio"
                )
            )

            if preferred_x >= 0:
                self.x_selector.setCurrentIndex(
                    preferred_x
                )

            elif self.x_selector.count():
                self.x_selector.setCurrentIndex(
                    0
                )

            preferred_y = (
                self.y_selector.findText(
                    "Maximum Hot-Gas Wall Temperature"
                )
            )

            if preferred_y >= 0:
                self.y_selector.setCurrentIndex(
                    preferred_y
                )

            elif self.y_selector.count():
                self.y_selector.setCurrentIndex(
                    0
                )

            self.points_entry.setEnabled(
                True
            )

            for checkbox in (
                self.fuel_compare_checks.values()
            ):
                checkbox.setEnabled(
                    True
                )

            for checkbox in (
                self.oxidizer_compare_checks.values()
            ):
                checkbox.setEnabled(
                    True
                )

            self.status_label.setText(
                "Controlled Regen sweep: one real LEAF input varies while "
                "the remaining controlled design state is held fixed."
            )

        else:

            self.regen_design_selector.setEnabled(
                False
            )

            for label, option in (
                self._regen_analysis_x_options()
                .items()
            ):
                self.x_selector.addItem(
                    label,
                    option[
                        "path"
                    ],
                )

            for label, option in (
                self._regen_analysis_y_options()
                .items()
            ):
                self.y_selector.addItem(
                    label,
                    option[
                        "path"
                    ],
                )

            self.points_entry.setEnabled(
                False
            )

            for checkbox in (
                self.fuel_compare_checks.values()
            ):
                checkbox.setEnabled(
                    False
                )

            for checkbox in (
                self.oxidizer_compare_checks.values()
            ):
                checkbox.setEnabled(
                    False
                )

            population = (
                self._regen_analysis_population()
            )

            self.auto_range_label.setText(
                "Evaluated candidates: "
                f"{len(population)}"
            )

            self.status_label.setText(
                "Stored evaluated Regen candidate scatter."
            )

            if not population:

                QMessageBox.warning(
                    self,
                    "No Evaluated Regen Candidates",
                    (
                        "No evaluated regenerative cooling candidate "
                        "population is available. Run a calculation first."
                    ),
                )

        self.x_selector.blockSignals(
            False
        )

        self.y_selector.blockSignals(
            False
        )

        if source == "Controlled Input Sweep":
            self._regen_controlled_update_auto_range()

    def _enter_regen_analysis_mode(self):
        if not getattr(
            self,
            "_regen_analysis_active",
            False,
        ):
            self._regen_standard_x_items = (
                self._combo_snapshot(
                    self.x_selector
                )
            )

            self._regen_standard_y_items = (
                self._combo_snapshot(
                    self.y_selector
                )
            )

        self._regen_analysis_active = True

        self.regen_analysis_source_selector.setEnabled(
            True
        )

        self.axial_preset_selector.setEnabled(
            False
        )

        self.x_selector.setEnabled(
            True
        )

        self.y_selector.setEnabled(
            True
        )

        self._sync_regen_analysis_source_mode()


    def _leave_regen_analysis_mode(self):
        if not getattr(
            self,
            "_regen_analysis_active",
            False,
        ):
            self.regen_analysis_source_selector.setEnabled(
                False
            )
            return

        self._restore_combo_snapshot(
            self.x_selector,
            getattr(
                self,
                "_regen_standard_x_items",
                [],
            ),
        )

        self._restore_combo_snapshot(
            self.y_selector,
            getattr(
                self,
                "_regen_standard_y_items",
                [],
            ),
        )

        self.regen_analysis_source_selector.setEnabled(
            False
        )

        self.regen_design_selector.setEnabled(
            False
        )

        self._regen_analysis_active = False


    def generate_regen_analysis_graph(self):
        if (
            self.regen_analysis_source_selector.currentText()
            ==
            "Evaluated Candidate Scatter"
        ):
            return self.generate_regen_candidate_scatter_graph()

        return self.generate_regen_controlled_sweep_graph()


    def generate_regen_controlled_sweep_graph(
        self,
    ):
        x_var = self.x_selector.currentData()

        if not isinstance(
            x_var,
            str,
        ):
            QMessageBox.warning(
                self,
                "Invalid Controlled Regen Sweep",
                "Select a valid LEAF input X variable.",
            )
            return

        x_label = (
            self.x_selector.currentText()
        )

        y_label = (
            self.y_selector.currentText()
        )

        option = (
            self._regen_controlled_y_options()
            .get(
                y_label
            )
        )

        if not option:
            QMessageBox.warning(
                self,
                "Invalid Controlled Regen Sweep",
                "Select a valid Regen Y metric.",
            )
            return

        selected_design_payload = (
            self._selected_regen_design_payload()
        )

        selected_design_label = (
            selected_design_payload.get(
                "label"
            )
            or
            "Current Inputs"
        )

        baseline_inputs = (
            self._regen_selected_baseline_inputs()
        )

        points = self.get_point_count()

        self.points_entry.setText(
            str(
                points
            )
        )

        scope_y_var = (
            option[
                "value_keys"
            ][0]
        )

        selected_fuels = (
            self.get_selected_fuel_comparisons()
        )

        selected_oxidizers = (
            self.get_selected_oxidizer_comparisons()
        )

        requested_series = []

        for fuel in selected_fuels:

            for oxidizer in selected_oxidizers:

                if not is_compatible_pair(
                    fuel,
                    oxidizer,
                ):
                    continue

                requested_series.append(
                    (
                        f"{fuel} / {oxidizer}",
                        fuel,
                        oxidizer,
                    )
                )

        if not requested_series:

            requested_series = [
                (
                    "Current Chemistry",
                    None,
                    None,
                )
            ]

        series_records = {}

        self.engine.last_errors = []

        for (
            series_label,
            fuel,
            oxidizer,
        ) in requested_series:

            if (
                fuel is not None
                and
                oxidizer is not None
            ):
                solved_records = (
                    self.engine.generate_propellant_solution_series(
                        base_inputs=baseline_inputs,
                        x_var=x_var,
                        point_count=points,
                        fuel=fuel,
                        oxidizer=oxidizer,
                        y_var=scope_y_var,
                    )
                )

            else:
                solved_records = (
                    self.engine.generate_solution_series(
                        base_inputs=baseline_inputs,
                        x_var=x_var,
                        point_count=points,
                        y_var=scope_y_var,
                    )
                )

            records = []

            for point in solved_records:

                solved = point.get(
                    "solved",
                    {},
                )

                value = (
                    self._regen_controlled_first_numeric(
                        solved,
                        option[
                            "value_keys"
                        ],
                    )
                )

                if value is None:
                    continue

                relation = option.get(
                    "relation"
                )

                if relation == "minimum_zero":
                    limit = 0.0

                else:
                    limit = (
                        self._regen_controlled_first_numeric(
                            solved,
                            option.get(
                                "limit_keys",
                                (),
                            ),
                        )
                    )

                state = (
                    self._regen_controlled_metric_state(
                        solved,
                        option,
                        value,
                        limit,
                    )
                )

                records.append(
                    {
                        "x":
                            point[
                                "x"
                            ],

                        "y":
                            value,

                        "limit":
                            limit,

                        "state":
                            state,

                        "fuel":
                            (
                                fuel
                                or
                                solved.get(
                                    "fuel"
                                )
                                or
                                self.get_current_fuel()
                            ),

                        "oxidizer":
                            (
                                oxidizer
                                or
                                solved.get(
                                    "oxidizer"
                                )
                                or
                                self.get_current_oxidizer()
                            ),
                    }
                )

            if records:
                series_records[
                    series_label
                ] = records

        if not series_records:

            error_text = "\n".join(
                self.engine.last_errors[
                    :12
                ]
            )

            QMessageBox.warning(
                self,
                "No Controlled Regen Sweep Data",
                (
                    f"No valid controlled Regen data was produced for "
                    f"{y_label} vs {x_label}.\n\n"
                    f"{error_text or 'No detailed solver error was captured.'}"
                ),
            )

            return

        self.figure.clear()

        axis = self.figure.add_subplot(
            111
        )

        state_styles = {
            "PASS": {
                "marker":
                    "o",
                "color":
                    "green",
            },

            "FAIL": {
                "marker":
                    "x",
                "color":
                    "red",
            },

            "WARN": {
                "marker":
                    "^",
                "color":
                    "darkorange",
            },

            "UNPROVEN": {
                "marker":
                    "s",
                "color":
                    "gray",
            },
        }

        self.last_graph_data = []
        self.last_graph_series = {}

        all_records = []

        for (
            series_label,
            records,
        ) in series_records.items():

            x_values = [
                record[
                    "x"
                ]
                for record in records
            ]

            y_values = [
                record[
                    "y"
                ]
                for record in records
            ]

            axis.plot(
                x_values,
                y_values,
                linewidth=1.4,
                label=series_label,
            )

            for state, style in (
                state_styles.items()
            ):

                subset = [
                    record
                    for record in records
                    if (
                        record[
                            "state"
                        ]
                        ==
                        state
                    )
                ]

                if not subset:
                    continue

                axis.scatter(
                    [
                        record[
                            "x"
                        ]
                        for record in subset
                    ],
                    [
                        record[
                            "y"
                        ]
                        for record in subset
                    ],
                    marker=style[
                        "marker"
                    ],
                    color=style[
                        "color"
                    ],
                    s=48,
                    linewidths=1.6,
                    label=(
                        state
                        if len(
                            series_records
                        )
                        ==
                        1
                        else
                        None
                    ),
                )

            numeric_limits = [
                (
                    record[
                        "x"
                    ],
                    record[
                        "limit"
                    ],
                )
                for record in records
                if (
                    record[
                        "limit"
                    ]
                    is not None
                )
            ]

            if numeric_limits:

                unique_limits = {
                    round(
                        limit,
                        12,
                    )
                    for _, limit
                    in numeric_limits
                }

                if len(
                    unique_limits
                ) == 1:

                    limit = (
                        numeric_limits[
                            0
                        ][1]
                    )

                    axis.axhline(
                        limit,
                        linestyle="--",
                        linewidth=1.4,
                        label=(
                            f"{series_label} — "
                            f"{option['limit_label']}"
                        ),
                    )

                else:

                    axis.plot(
                        [
                            item[
                                0
                            ]
                            for item in numeric_limits
                        ],
                        [
                            item[
                                1
                            ]
                            for item in numeric_limits
                        ],
                        linestyle="--",
                        linewidth=1.4,
                        label=(
                            f"{series_label} — "
                            f"{option['limit_label']}"
                        ),
                    )

            self.last_graph_series[
                series_label
            ] = {
                "x":
                    x_values,

                "y":
                    y_values,

                "states":
                    [
                        record[
                            "state"
                        ]
                        for record in records
                    ],

                "limits":
                    [
                        record[
                            "limit"
                        ]
                        for record in records
                    ],

                "fuel":
                    records[
                        0
                    ].get(
                        "fuel"
                    ),

                "oxidizer":
                    records[
                        0
                    ].get(
                        "oxidizer"
                    ),
            }

            for record in records:

                self.last_graph_data.append(
                    (
                        series_label,
                        record[
                            "x"
                        ],
                        record[
                            "y"
                        ],
                    )
                )

            all_records.extend(
                records
            )

        hard_intervals = []

        # One global X-region background is only truthful when exactly one
        # chemistry series is being examined.
        if len(
            series_records
        ) == 1:

            only_records = next(
                iter(
                    series_records.values()
                )
            )

            hard_intervals = (
                self._regen_controlled_fail_intervals(
                    only_records
                )
            )

            hard_label_added = False

            for left, right in hard_intervals:

                axis.axvspan(
                    left,
                    right,
                    facecolor="red",
                    alpha=0.12,
                    edgecolor="red",
                    linewidth=2.5,
                    hatch="////",
                    label=(
                        "Hard Infeasible X Region"
                        if not hard_label_added
                        else
                        None
                    ),
                )

                hard_label_added = True

        current_design_point = (
            self._plot_regen_selected_design_current_point(
                axis,
                baseline_inputs,
                x_var,
                option,
            )
        )

        self.last_regen_selected_design_current_point = (
            current_design_point
        )

        if isinstance(
            current_design_point,
            dict,
        ):
            self.last_graph_data.append(
                (
                    "Current Selected Regen Design",
                    current_design_point[
                        "x"
                    ],
                    current_design_point[
                        "y"
                    ],
                )
            )

        x_unit = UNITS.get(
            x_var,
            "",
        )

        y_unit = option.get(
            "unit",
            "",
        )

        x_axis_label = (
            x_label
            if not x_unit
            else
            f"{x_label} ({x_unit})"
        )

        y_axis_label = (
            y_label
            if not y_unit
            else
            f"{y_label} ({y_unit})"
        )

        axis.set_xlabel(
            x_axis_label
        )

        axis.set_ylabel(
            y_axis_label
        )

        axis.set_title(
            f"Controlled Regen Sweep — "
            f"{y_label} vs {x_label}"
        )

        axis.grid(
            True
        )

        axis.legend()

        self.figure.tight_layout()

        self.canvas.draw()

        counts = {
            state:
                sum(
                    1
                    for record in all_records
                    if (
                        record[
                            "state"
                        ]
                        ==
                        state
                    )
                )
            for state in (
                "PASS",
                "FAIL",
                "WARN",
                "UNPROVEN",
            )
        }

        self.summary_label.setText(
            (
                f"Controlled Regen Sweep: "
                f"{len(all_records)} solved points | "
                f"PASS {counts['PASS']} | "
                f"FAIL {counts['FAIL']} | "
                f"WARN {counts['WARN']} | "
                f"UNPROVEN {counts['UNPROVEN']}"
            )
        )

        self.interpretation_box.setPlainText(
            (
                "CONTROLLED REGEN INPUT SWEEP\n"
                "============================\n\n"
                f"Regen design: {selected_design_label}\n"
                f"X input: {x_label}\n"
                f"Y Regen metric: {y_label}\n"
                f"Solved point count: {len(all_records)}\n"
                f"Chemistry series: {len(series_records)}\n\n"
                "At every point, LEAF changes only the selected X input "
                "within the controlled graph state, clears dependent "
                "calculated values, refreshes CEA where required, and runs "
                "the existing calculation bridge.\n\n"
                "PASS / FAIL / WARN presentation is consumed from existing "
                "solver-owned Regen status or existing solver-owned limit "
                "values. Graph Explorer does not create engineering "
                "thresholds or independently requalify the design."
            )
        )

        if len(
            series_records
        ) == 1:

            region_text = (
                f"{len(hard_intervals)} red hatched infeasible X region(s) "
                "are shown from controlled single-variable solver evidence. "
                "Unshaded X regions are not hard-failed by the selected "
                "metric at the solved samples."
            )

        else:

            region_text = (
                "Global red background shading is intentionally disabled "
                "for multi-chemistry comparison because each fuel/oxidizer "
                "series can have a different failure boundary. Failed "
                "points remain visible per series. Select one chemistry "
                "pair to obtain its hard red X regions."
            )

        self.comparison_box.setPlainText(
            (
                "CONTROLLED-SWEEP FEASIBILITY EVIDENCE\n"
                "=====================================\n\n"
                f"{region_text}\n\n"
                f"Limit source: {option['limit_label']}.\n"
                "No multidimensional candidate interpolation is used."
            )
        )

    def generate_regen_candidate_scatter_graph(self):
        population = (
            self._regen_analysis_population()
        )

        if not population:
            QMessageBox.warning(
                self,
                "No Evaluated Regen Candidates",
                (
                    "No evaluated regenerative cooling candidate "
                    "population is available."
                ),
            )
            return

        x_path = (
            self.x_selector.currentData()
        )

        y_path = (
            self.y_selector.currentData()
        )

        if not isinstance(
            x_path,
            str,
        ) or not isinstance(
            y_path,
            str,
        ):
            QMessageBox.warning(
                self,
                "Invalid Regen Analysis Selection",
                "Select valid X and Y variables.",
            )
            return

        x_label = (
            self.x_selector.currentText()
        )

        y_label = (
            self.y_selector.currentText()
        )

        x_option = (
            self._regen_analysis_x_options()
            .get(
                x_label,
                {},
            )
        )

        y_option = (
            self._regen_analysis_y_options()
            .get(
                y_label,
                {},
            )
        )

        records = []

        for candidate in population:
            x_value = (
                self._regen_analysis_numeric(
                    self._regen_analysis_value(
                        candidate,
                        x_path,
                    )
                )
            )

            y_value = (
                self._regen_analysis_numeric(
                    self._regen_analysis_value(
                        candidate,
                        y_path,
                    )
                )
            )

            if (
                x_value is None
                or
                y_value is None
            ):
                continue

            records.append(
                {
                    "candidate_id":
                        candidate.get(
                            "candidate_id",
                            "",
                        ),

                    "x":
                        x_value,

                    "y":
                        y_value,

                    "state":
                        self._regen_analysis_candidate_state(
                            candidate
                        ),

                    "failed_constraints":
                        self._regen_analysis_failed_constraints(
                            candidate
                        ),
                }
            )

        if not records:
            QMessageBox.warning(
                self,
                "No Regen Analysis Data",
                (
                    f"No evaluated numeric candidate data exists for "
                    f"{x_label} vs {y_label}."
                ),
            )
            return

        self.figure.clear()

        axis = self.figure.add_subplot(
            111
        )

        state_styles = {
            "PASS": {
                "marker": "o",
                "color": "green",
            },
            "FAIL": {
                "marker": "x",
                "color": "red",
            },
            "UNPROVEN": {
                "marker": "^",
                "color": "darkorange",
            },
        }

        for state in (
            "PASS",
            "FAIL",
            "UNPROVEN",
        ):
            subset = [
                record
                for record in records
                if (
                    record[
                        "state"
                    ]
                    ==
                    state
                )
            ]

            if not subset:
                continue

            style = state_styles[
                state
            ]

            axis.scatter(
                [
                    record[
                        "x"
                    ]
                    for record in subset
                ],
                [
                    record[
                        "y"
                    ]
                    for record in subset
                ],
                marker=style[
                    "marker"
                ],
                color=style[
                    "color"
                ],
                s=54,
                linewidths=1.8,
                label=state,
            )

        hard_intervals = (
            self._regen_analysis_hard_fail_intervals(
                population,
                x_path,
            )
        )

        hard_label_added = False

        for left, right in (
            hard_intervals
        ):
            axis.axvspan(
                left,
                right,
                facecolor="none",
                edgecolor="red",
                linewidth=2.5,
                hatch="////",
                label=(
                    "Hard Infeasible Region"
                    if not hard_label_added
                    else None
                ),
            )

            hard_label_added = True

        x_unit = x_option.get(
            "unit",
            "",
        )

        y_unit = y_option.get(
            "unit",
            "",
        )

        x_axis_label = x_label

        y_axis_label = y_label

        if x_unit:
            x_axis_label += (
                f" ({x_unit})"
            )

        if y_unit:
            y_axis_label += (
                f" ({y_unit})"
            )

        axis.set_xlabel(
            x_axis_label
        )

        axis.set_ylabel(
            y_axis_label
        )

        axis.set_title(
            f"Regen Analysis — {y_label} vs {x_label}"
        )

        axis.grid(
            True
        )

        axis.legend()

        self.canvas.draw()

        self.last_graph_data = [
            (
                "Regen Analysis",
                record[
                    "x"
                ],
                record[
                    "y"
                ],
            )
            for record in records
        ]

        self.last_graph_series = {
            state: {
                "x": [
                    record[
                        "x"
                    ]
                    for record in records
                    if (
                        record[
                            "state"
                        ]
                        ==
                        state
                    )
                ],
                "y": [
                    record[
                        "y"
                    ]
                    for record in records
                    if (
                        record[
                            "state"
                        ]
                        ==
                        state
                    )
                ],
                "fuel":
                    self.get_current_fuel(),

                "oxidizer":
                    self.get_current_oxidizer(),
            }
            for state in (
                "PASS",
                "FAIL",
                "UNPROVEN",
            )
        }

        counts = {
            state:
                sum(
                    1
                    for record in records
                    if (
                        record[
                            "state"
                        ]
                        ==
                        state
                    )
                )
            for state in (
                "PASS",
                "FAIL",
                "UNPROVEN",
            )
        }

        failed_constraints = sorted({
            constraint
            for record in records
            for constraint in (
                record[
                    "failed_constraints"
                ]
            )
        })

        controlled = (
            self._regen_analysis_controlled_sweep(
                population,
                x_path,
            )
        )

        self.summary_label.setText(
            (
                f"Regen Analysis: {len(records)} evaluated candidates | "
                f"PASS {counts['PASS']} | "
                f"FAIL {counts['FAIL']} | "
                f"UNPROVEN {counts['UNPROVEN']}"
            )
        )

        failed_text = (
            ", ".join(
                failed_constraints
            )
            if failed_constraints
            else
            "None"
        )

        self.interpretation_box.setPlainText(
            (
                "REGEN DESIGN-SPACE INTERPRETATION\n"
                "=================================\n\n"
                f"Dataset: regen_candidate_evaluated_population\n"
                f"Candidate count plotted: {len(records)}\n\n"
                f"PASS: {counts['PASS']}\n"
                f"FAIL: {counts['FAIL']}\n"
                f"UNPROVEN: {counts['UNPROVEN']}\n\n"
                f"Observed failed constraints: {failed_text}\n\n"
                "Candidate state is taken from canonical regen "
                "qualification evidence. Graph Explorer does not "
                "recalculate engineering qualification."
            )
        )

        if controlled:
            region_text = (
                f"{len(hard_intervals)} hard infeasible region(s) "
                "are shown using red diagonal hatching because "
                "explicit controlled one-variable sweep evidence "
                "is present."
            )
        else:
            region_text = (
                "Hard infeasible regions are intentionally not drawn. "
                "This evaluated population is not proven to be a "
                "controlled one-variable sweep. Failed and unproven "
                "markers are observed candidate evidence only; LEAF "
                "does not interpolate a hard feasibility boundary "
                "from multidimensional scatter."
            )

        self.comparison_box.setPlainText(
            (
                "REGEN ANALYSIS EVIDENCE POLICY\n"
                "==============================\n\n"
                f"{region_text}\n\n"
                "Fuel/oxidizer comparison is disabled in this mode "
                "because the plotted records are a stored evaluated "
                "candidate population, not newly solved comparison "
                "curves."
            )
        )

    def generate_graph(self):
        if (
            self.graph_mode_selector.currentText()
            == "Regen Analysis"
        ):
            self.generate_regen_analysis_graph()
            return

        if self.graph_mode_selector.currentText() == "Axial Regen Profile":
            self.generate_axial_profile_graph()
            return

        x_var, x_label = self.current_var(self.x_selector)
        y_var, y_label = self.current_var(self.y_selector)

        if x_var is None or y_var is None:
            QMessageBox.warning(self, "Invalid Selection", "Invalid X or Y variable.")
            return

        points = self.get_point_count()
        self.points_entry.setText(str(points))

        # Defer the ordinary base sweep until we know it is needed.
        # Comparison mode should not first calculate a series that will never
        # be plotted.
        x_points = []
        y_points = []

        self.last_graph_data = []
        self.last_graph_series = {}

        self.figure.clear()
        axis = self.figure.add_subplot(111)

        x_unit = UNITS.get(x_var, "")
        y_unit = UNITS.get(y_var, "")

        x_axis_label = x_label if not x_unit else f"{x_label} ({x_unit})"
        y_axis_label = y_label if not y_unit else f"{y_label} ({y_unit})"

        selected_fuels = self.get_selected_fuel_comparisons()
        selected_oxidizers = self.get_selected_oxidizer_comparisons()

        series_count = 0

        for fuel in selected_fuels:
            for oxidizer in selected_oxidizers:
                if not is_compatible_pair(fuel, oxidizer):
                    continue

                comparison_x, comparison_y = self.engine.generate_propellant_series(
                    base_inputs=self.base_inputs,
                    x_var=x_var,
                    y_var=y_var,
                    point_count=points,
                    fuel=fuel,
                    oxidizer=oxidizer,
                )

                if not comparison_x:
                    continue

                series_label = f"{fuel} / {oxidizer}"

                axis.plot(
                    comparison_x,
                    comparison_y,
                    marker="o",
                    label=series_label
                )

                self.last_graph_series[series_label] = {
                    "x": comparison_x,
                    "y": comparison_y,
                    "fuel": fuel,
                    "oxidizer": oxidizer,
                }

                for x, y in zip(comparison_x, comparison_y):
                    self.last_graph_data.append((series_label, x, y))

                series_count += 1

        if series_count == 0:
            x_points, y_points = self.engine.generate_series(
                base_inputs=self.base_inputs,
                x_var=x_var,
                y_var=y_var,
                point_count=points,
            )

            if not x_points:
                error_text = "\n".join(
                    self.engine.last_errors[:12]
                )

                if not error_text:
                    error_text = (
                        "No detailed solver error was captured."
                    )

                QMessageBox.warning(
                    self,
                    "No Graph Data",
                    (
                        f"No valid graph data was produced for "
                        f"{y_label} vs {x_label}.\n\n"
                        f"First solver issues:\n{error_text}"
                    )
                )
                return

            axis.plot(
                x_points,
                y_points,
                marker="o",
                label="Current Sweep"
            )

            self.last_graph_series["Current Sweep"] = {
                "x": x_points,
                "y": y_points,
                "fuel": self.get_current_fuel(),
                "oxidizer": self.get_current_oxidizer(),
            }

            for x, y in zip(x_points, y_points):
                self.last_graph_data.append(("Current Sweep", x, y))

        # ---------------------------------------------------------
        # Current design marker
        # ---------------------------------------------------------
        # Only plot this marker when exactly ONE series exists.
        # Multi-fuel/multi-oxidizer comparison mode should remain clean.
        # ---------------------------------------------------------

        if len(self.last_graph_series) == 1:
            only_label = next(iter(self.last_graph_series.keys()))
            data = self.last_graph_series[only_label]

            prepared_inputs = self.engine.prepare_graph_inputs(self.base_inputs)
            current_x = prepared_inputs.get(x_var)

            current_y = None

            if current_x is not None:
                current_y = self.interpolate_y_from_series(
                    data.get("x", []),
                    data.get("y", []),
                    current_x
                )

            if current_x is not None and current_y is not None:
                axis.scatter(
                    [current_x],
                    [current_y],
                    s=120,
                    marker="o",
                    label="Current Design"
                )

                axis.axvline(
                    current_x,
                    linestyle="--",
                    linewidth=1
                )

                axis.axhline(
                    current_y,
                    linestyle="--",
                    linewidth=1
                )

                x_unit_text = f" {x_unit}" if x_unit else ""
                y_unit_text = f" {y_unit}" if y_unit else ""

                axis.annotate(
                    f"{x_label} = {float(current_x):.6g}{x_unit_text}",
                    xy=(float(current_x), float(current_y)),
                    xytext=(10, -35),
                    textcoords="offset points",
                    fontsize=9
                )

                axis.annotate(
                    f"{y_label} = {float(current_y):.6g}{y_unit_text}",
                    xy=(float(current_x), float(current_y)),
                    xytext=(10, 15),
                    textcoords="offset points",
                    fontsize=9
                )

        axis.set_xlabel(x_axis_label)
        axis.set_ylabel(y_axis_label)
        axis.set_title(f"{y_label} vs {x_label}")
        axis.grid(True)

        if x_var == "mixture_ratio":
            max_of = 0.0

            for fuel in selected_fuels:
                for oxidizer in selected_oxidizers:
                    if not is_compatible_pair(fuel, oxidizer):
                        continue

                    _, pair_max = get_of_ratio_range_for_pair(fuel, oxidizer)
                    max_of = max(max_of, pair_max)

            if max_of > 0:
                axis.set_xlim(0.0, max_of)

        axis.legend()

        self.figure.tight_layout()
        self.canvas.draw()

        self.update_multi_series_summary(
            self.last_graph_series,
            x_label,
            y_label,
            x_unit,
            y_unit
        )

        self.update_design_comparison_from_series(
            x_var,
            y_var,
            self.last_graph_series
        )
    def update_multi_series_summary(self, series_data, x_label, y_label, x_unit, y_unit):
        if not series_data:
            self.summary_label.setText("")
            self.interpretation_box.clear()
            return

        x_unit_text = f" {x_unit}" if x_unit else ""
        y_unit_text = f" {y_unit}" if y_unit else ""

        series_stats = []

        for label, data in series_data.items():
            x_points = data.get("x", [])
            y_points = data.get("y", [])

            if not x_points or not y_points:
                continue

            min_index = min(range(len(y_points)), key=lambda i: y_points[i])
            max_index = max(range(len(y_points)), key=lambda i: y_points[i])

            start_y = y_points[0]
            end_y = y_points[-1]
            delta_y = end_y - start_y

            if abs(start_y) > 1e-12:
                percent_change = delta_y / abs(start_y) * 100.0
            else:
                percent_change = 0.0

            increasing_steps = 0
            decreasing_steps = 0

            for previous, current in zip(y_points[:-1], y_points[1:]):
                if current > previous:
                    increasing_steps += 1
                elif current < previous:
                    decreasing_steps += 1

            total_steps = max(1, len(y_points) - 1)

            if increasing_steps / total_steps > 0.85:
                shape = "mostly increasing"
            elif decreasing_steps / total_steps > 0.85:
                shape = "mostly decreasing"
            else:
                shape = "non-monotonic / peaked"

            series_stats.append({
                "label": label,
                "x_points": x_points,
                "y_points": y_points,
                "min_x": x_points[min_index],
                "min_y": y_points[min_index],
                "max_x": x_points[max_index],
                "max_y": y_points[max_index],
                "start_x": x_points[0],
                "start_y": start_y,
                "end_x": x_points[-1],
                "end_y": end_y,
                "delta_y": delta_y,
                "percent_change": percent_change,
                "shape": shape,
            })

        if not series_stats:
            self.summary_label.setText("No valid series analysis available.")
            self.interpretation_box.clear()
            return

        best = max(series_stats, key=lambda item: item["max_y"])
        worst = min(series_stats, key=lambda item: item["max_y"])

        lines = []

        lines.append("MULTI-SERIES GRAPH ANALYSIS")
        lines.append("===========================")
        lines.append("")

        lines.append("GLOBAL RESULT")
        lines.append("-------------")
        lines.append(
            f"Best plotted series: {best['label']}"
        )
        lines.append(
            f"Maximum {y_label}: {best['max_y']:.6g}{y_unit_text} "
            f"at {x_label} = {best['max_x']:.6g}{x_unit_text}"
        )
        lines.append(
            f"Weakest peak series: {worst['label']} "
            f"with maximum {y_label} = {worst['max_y']:.6g}{y_unit_text}"
        )

        if abs(worst["max_y"]) > 1e-12:
            advantage = (best["max_y"] - worst["max_y"]) / abs(worst["max_y"]) * 100.0
            lines.append(
                f"Best-to-worst peak advantage: {advantage:.3f}%"
            )

        lines.append("")
        lines.append("SERIES BREAKDOWN")
        lines.append("----------------")

        for stats in series_stats:
            lines.append("")
            lines.append(stats["label"])
            lines.append("-" * len(stats["label"]))

            lines.append(
                f"Minimum {y_label}: {stats['min_y']:.6g}{y_unit_text} "
                f"at {x_label} = {stats['min_x']:.6g}{x_unit_text}"
            )

            lines.append(
                f"Maximum {y_label}: {stats['max_y']:.6g}{y_unit_text} "
                f"at {x_label} = {stats['max_x']:.6g}{x_unit_text}"
            )

            lines.append(
                f"Start: {stats['start_y']:.6g}{y_unit_text} "
                f"at {x_label} = {stats['start_x']:.6g}{x_unit_text}"
            )

            lines.append(
                f"End: {stats['end_y']:.6g}{y_unit_text} "
                f"at {x_label} = {stats['end_x']:.6g}{x_unit_text}"
            )

            lines.append(
                f"Net change: {stats['delta_y']:+.6g}{y_unit_text} "
                f"({stats['percent_change']:+.3f}%)"
            )

            lines.append(
                f"Curve shape: {stats['shape']}"
            )

        lines.append("")
        lines.append("VALIDATION NOTES")
        lines.append("----------------")

        validation_notes = self.build_metric_validation_notes(
            series_stats,
            x_label,
            y_label
        )

        if validation_notes:
            lines.extend(validation_notes)
        else:
            lines.append("No obvious graph-shape warnings detected.")

        self.summary_label.setText(
            f"Best: {best['label']} | "
            f"{y_label} = {best['max_y']:.6g}{y_unit_text} "
            f"at {x_label} = {best['max_x']:.6g}{x_unit_text}"
        )

        self.interpretation_box.setPlainText("\n".join(lines))

    def build_metric_validation_notes(self, series_stats, x_label, y_label):
        notes = []

        y_lower = y_label.lower()
        x_lower = x_label.lower()

        for stats in series_stats:
            label = stats["label"]
            max_x = stats["max_x"]
            max_y = stats["max_y"]
            min_y = stats["min_y"]
            shape = stats["shape"]

            if "mixture ratio" in x_lower:
                if "LH2" in label or "GH2" in label:
                    if not 3.0 <= max_x <= 6.5:
                        notes.append(
                            f"Warning: {label} peaks at O/F={max_x:.3g}, "
                            f"which is unusual for hydrogen/oxygen performance metrics."
                        )

                if "RP-1" in label or "Kerosene" in label or "Jet-A" in label:
                    if not 2.0 <= max_x <= 3.4:
                        notes.append(
                            f"Warning: {label} peaks at O/F={max_x:.3g}, "
                            f"which is unusual for kerosene/oxygen performance metrics."
                        )

                if "Ethanol" in label or "Methanol" in label:
                    if not 0.9 <= max_x <= 2.2:
                        notes.append(
                            f"Warning: {label} peaks at O/F={max_x:.3g}, "
                            f"which is unusual for alcohol/oxygen performance metrics."
                        )

            if max_y <= 0:
                notes.append(
                    f"Warning: {label} has non-positive maximum {y_label}; "
                    f"this usually indicates a solver or unit problem."
                )

            if abs(max_y - min_y) < 1e-9:
                notes.append(
                    f"Warning: {label} is effectively flat. "
                    f"This may mean the selected propellant is not affecting {y_label}."
                )

            if "corrected thrust" in y_lower and "mixture ratio" in x_lower:
                if shape == "mostly increasing" or shape == "mostly decreasing":
                    notes.append(
                        f"Check: {label} is {shape}. For mixture-ratio sweeps, "
                        f"a peaked curve is usually expected for thrust-like metrics."
                    )

        return notes

    def update_summary(self, x_points, y_points, x_label, y_label, x_unit, y_unit):
        min_index = min(range(len(y_points)), key=lambda index: y_points[index])
        max_index = max(range(len(y_points)), key=lambda index: y_points[index])

        x_unit_text = f" {x_unit}" if x_unit else ""
        y_unit_text = f" {y_unit}" if y_unit else ""

        min_x = x_points[min_index]
        min_y = y_points[min_index]
        max_x = x_points[max_index]
        max_y = y_points[max_index]

        self.summary_label.setText(
            f"Minimum {y_label}: {min_y:.6g}{y_unit_text} "
            f"at {x_label} = {min_x:.6g}{x_unit_text}    |    "
            f"Maximum {y_label}: {max_y:.6g}{y_unit_text} "
            f"at {x_label} = {max_x:.6g}{x_unit_text}"
        )

        interpretation = self.build_graph_interpretation(
            x_points=x_points,
            y_points=y_points,
            x_label=x_label,
            y_label=y_label,
            x_unit=x_unit,
            y_unit=y_unit,
            min_index=min_index,
            max_index=max_index,
        )

        self.interpretation_box.setPlainText(interpretation)

    def update_design_comparison_from_series(self, x_var, y_var, series_data):
        try:
            current_x, current_y = self.get_current_design_point(x_var, y_var)

            if current_x is None or current_y is None:
                self.comparison_box.clear()
                return

            best_label = None
            best_x = None
            best_y = None

            for label, data in series_data.items():
                x_points = data.get("x", [])
                y_points = data.get("y", [])

                if not x_points or not y_points:
                    continue

                max_index = max(range(len(y_points)), key=lambda i: y_points[i])

                candidate_x = x_points[max_index]
                candidate_y = y_points[max_index]

                if best_y is None or candidate_y > best_y:
                    best_label = label
                    best_x = candidate_x
                    best_y = candidate_y

            if best_y is None:
                self.comparison_box.clear()
                return

            delta = best_y - current_y

            if abs(current_y) > 1e-12:
                percent = delta / abs(current_y) * 100.0
            else:
                percent = 0.0

            text = []

            text.append("CURRENT DESIGN")
            text.append("====================")
            text.append(
                f"{self.var_to_label.get(x_var, x_var)} = {current_x:.6g}"
            )
            text.append(
                f"{self.var_to_label.get(y_var, y_var)} = {current_y:.6g}"
            )

            text.append("")
            text.append("BEST SERIES IN CURRENT GRAPH")
            text.append("============================")
            text.append(f"Series = {best_label}")
            text.append(
                f"{self.var_to_label.get(x_var, x_var)} = {best_x:.6g}"
            )
            text.append(
                f"{self.var_to_label.get(y_var, y_var)} = {best_y:.6g}"
            )

            text.append("")
            text.append("IMPROVEMENT POTENTIAL")
            text.append("=====================")
            text.append(f"Absolute Change = {delta:+.6g}")
            text.append(f"Percentage Change = {percent:+.3f}%")

            self.comparison_box.setPlainText("\n".join(text))

        except Exception as error:
            self.comparison_box.setPlainText(
                f"Design comparison failed:\n{type(error).__name__}: {error}"
            )

    def update_design_comparison(
            self,
            x_var,
            y_var,
            x_points,
            y_points
    ):
        try:
            current_x, current_y = self.get_current_design_point(x_var, y_var)

            if current_x is None or current_y is None:
                self.comparison_box.clear()
                return

            max_index = max(
                range(len(y_points)),
                key=lambda i: y_points[i]
            )

            best_x = x_points[max_index]
            best_y = y_points[max_index]

            self.current_design_point = (
                float(current_x),
                float(current_y)
            )

            self.best_graph_point = (
                float(best_x),
                float(best_y)
            )

            delta = best_y - current_y

            if abs(current_y) > 1e-12:
                percent = delta / abs(current_y) * 100.0
            else:
                percent = 0.0

            text = []

            text.append("CURRENT DESIGN")
            text.append("====================")
            text.append(
                f"{self.var_to_label.get(x_var, x_var)} = {current_x:.6g}"
            )
            text.append(
                f"{self.var_to_label.get(y_var, y_var)} = {current_y:.6g}"
            )

            text.append("")
            text.append("OPTIMUM WITHIN SWEEP RANGE")
            text.append("==========================")
            text.append(
                f"{self.var_to_label.get(x_var, x_var)} = {best_x:.6g}"
            )
            text.append(
                f"{self.var_to_label.get(y_var, y_var)} = {best_y:.6g}"
            )

            text.append("")
            text.append("IMPROVEMENT POTENTIAL")
            text.append("==========================")
            text.append(
                f"Absolute Change = {delta:+.6g}"
            )
            text.append(
                f"Percentage Change = {percent:+.3f}%"
            )

            text.append("")
            text.append("DIFFERENCE")
            text.append("====================")
            text.append(
                f"{delta:+.6g}"
            )
            text.append(
                f"{percent:+.3f}%"
            )

            self.comparison_box.setPlainText(
                "\n".join(text)
            )

        except Exception:
            self.comparison_box.clear()

    def build_graph_interpretation(
            self,
            x_points,
            y_points,
            x_label,
            y_label,
            x_unit,
            y_unit,
            min_index,
            max_index
    ):
        x_unit_text = f" {x_unit}" if x_unit else ""
        y_unit_text = f" {y_unit}" if y_unit else ""

        start_x = x_points[0]
        end_x = x_points[-1]

        start_y = y_points[0]
        end_y = y_points[-1]

        min_x = x_points[min_index]
        min_y = y_points[min_index]

        max_x = x_points[max_index]
        max_y = y_points[max_index]

        delta_y = end_y - start_y

        if abs(start_y) > 1e-12:
            percent_change = (delta_y / abs(start_y)) * 100.0
        else:
            percent_change = None

        if delta_y > 0:
            trend_text = "increases overall"
        elif delta_y < 0:
            trend_text = "decreases overall"
        else:
            trend_text = "stays approximately constant overall"

        # crude monotonicity check
        increasing_steps = 0
        decreasing_steps = 0

        for previous, current in zip(y_points[:-1], y_points[1:]):
            if current > previous:
                increasing_steps += 1
            elif current < previous:
                decreasing_steps += 1

        total_steps = max(1, len(y_points) - 1)

        if increasing_steps / total_steps > 0.85:
            shape_text = "The curve is mostly increasing across the plotted range."
        elif decreasing_steps / total_steps > 0.85:
            shape_text = "The curve is mostly decreasing across the plotted range."
        else:
            shape_text = "The curve is non-monotonic, meaning it has at least one local change in direction."

        if max_index not in [0, len(y_points) - 1]:
            optimum_text = (
                f"The maximum occurs inside the sweep range, suggesting an internal optimum near "
                f"{x_label} = {max_x:.6g}{x_unit_text}."
            )
        elif max_index == 0:
            optimum_text = (
                f"The highest value occurs at the lower bound of the sweep. A lower {x_label} may be worth testing."
            )
        else:
            optimum_text = (
                f"The highest value occurs at the upper bound of the sweep. A higher {x_label} may be worth testing."
            )

        lines = []

        lines.append("GRAPH INTERPRETATION")
        lines.append("====================")
        lines.append("")

        lines.append("Overall behaviour:")
        lines.append(
            f"- As {x_label} changes from {start_x:.6g}{x_unit_text} to "
            f"{end_x:.6g}{x_unit_text}, {y_label} {trend_text}."
        )

        if percent_change is not None:
            lines.append(
                f"- Net change: {delta_y:.6g}{y_unit_text}, approximately {percent_change:.3g}% relative to the starting value."
            )
        else:
            lines.append(
                f"- Net change: {delta_y:.6g}{y_unit_text}."
            )

        lines.append("")
        lines.append("Extremes:")
        lines.append(
            f"- Minimum {y_label}: {min_y:.6g}{y_unit_text} at {x_label} = {min_x:.6g}{x_unit_text}."
        )
        lines.append(
            f"- Maximum {y_label}: {max_y:.6g}{y_unit_text} at {x_label} = {max_x:.6g}{x_unit_text}."
        )

        lines.append("")
        lines.append("Shape:")
        lines.append(f"- {shape_text}")

        lines.append("")
        lines.append("Design implication:")
        lines.append(f"- {optimum_text}")

        lines.append("")
        lines.append("OPTIMUM IDENTIFIED")
        lines.append("====================")
        lines.append(
            f"Best {y_label} occurs near "
            f"{x_label} = {max_x:.6g}{x_unit_text}."
        )
        lines.append(
            f"Maximum {y_label} = "
            f"{max_y:.6g}{y_unit_text}."
        )

        return "\n".join(lines)

    def export_graph_csv(self):
        if not self.last_graph_data:
            QMessageBox.warning(self, "No Graph Data", "Generate a graph before exporting.")
            return

        x_var, x_label = self.current_var(self.x_selector)
        y_var, y_label = self.current_var(self.y_selector)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Graph Data",
            "",
            "CSV File (*.csv)"
        )

        if not path:
            return

        if not path.endswith(".csv"):
            path += ".csv"

        with open(path, "w", encoding="utf-8") as file:
            file.write(f"Series,{x_label},{y_label}\n")

            for series, x, y in self.last_graph_data:
                file.write(f"{series},{x},{y}\n")

        QMessageBox.information(self, "Export Complete", "Graph data exported.")

    def copy_graph_data_to_clipboard(self):
        if not getattr(self, "last_graph_data", None):
            QMessageBox.warning(
                self,
                "No Graph Data",
                "Generate a graph before copying data."
            )
            return

        x_var, x_label = self.current_var(self.x_selector)
        y_var, y_label = self.current_var(self.y_selector)

        lines = []

        if self.summary_label.text():
            lines.append("# " + self.summary_label.text())
            lines.append("")

        if self.interpretation_box.toPlainText().strip():
            lines.append("# ANALYSIS")
            for line in self.interpretation_box.toPlainText().splitlines():
                lines.append("# " + line)
            lines.append("")

        # ---------------------------------------------------------
        # Plotted curve data only
        # ---------------------------------------------------------
        # This is intentionally ONLY the actual points plotted on
        # the graph curve. Current/chosen design points are not mixed
        # into this table, because they may not exist in the sweep.
        # ---------------------------------------------------------

        lines.append("# PLOTTED CURVE DATA")
        lines.append(f"Series\t{x_label}\t{y_label}")

        for row in self.last_graph_data:
            if len(row) == 3:
                series, x, y = row
                lines.append(f"{series}\t{x}\t{y}")
            elif len(row) == 2:
                x, y = row
                lines.append(f"Current Sweep\t{x}\t{y}")

        # ---------------------------------------------------------
        # Chosen/current design comparison data
        # ---------------------------------------------------------
        # These are interpolated from the canonical plotted series at
        # the exact selected X value and remain separate from the sweep data.
        # ---------------------------------------------------------

        chosen_rows = []

        if getattr(self, "last_graph_series", None):
            for series_label, data in self.last_graph_series.items():
                fuel = data.get("fuel")
                oxidizer = data.get("oxidizer")

                prepared_inputs = self.engine.prepare_graph_inputs(self.base_inputs)
                current_x = prepared_inputs.get(x_var)

                current_y = None

                if current_x is not None:
                    current_y = self.interpolate_y_from_series(
                        data.get("x", []),
                        data.get("y", []),
                        current_x
                    )

                if current_x is None or current_y is None:
                    continue

                chosen_rows.append((series_label, current_x, current_y))

        if chosen_rows:
            lines.append("")
            lines.append("# CHOSEN / CURRENT DESIGN VALUES")
            lines.append(
                "# These values are interpolated from the canonical plotted series "
                "at the exact selected X value. They are not inserted into the plotted curve."
            )
            lines.append(f"Series\tChosen {x_label}\tChosen {y_label}")

            for series_label, current_x, current_y in chosen_rows:
                lines.append(f"{series_label}\t{current_x}\t{current_y}")

        QApplication.clipboard().setText("\n".join(lines))

        QMessageBox.information(
            self,
            "Copied",
            "Graph data copied to clipboard."
        )

    def clear_cache(self):
        self.engine.clear_cache()
        QMessageBox.information(self, "Cache Cleared", "Graph cache cleared.")