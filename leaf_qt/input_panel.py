from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QGroupBox, QComboBox
from variable_registry import is_default_manual_input, is_advanced_input, get_input_keys, get_variable
from leaf_data import AMBIENT_PRESSURE_PRESETS_PA

class ManualInputPanel(QWidget):
    def __init__(self, label_to_var, units, unit_groups, unit_preferences):
        super().__init__()

        self.label_to_var = label_to_var
        self.units = units
        self.unit_groups = unit_groups
        self.unit_preferences = unit_preferences

        self.entries = {}

        self.create_layout()

    @staticmethod
    def pressure_unit_factor_to_pa(unit):
        """
        Return the SI-Pa factor for a supported pressure display unit.

        The Manual Input Panel continues to use the existing LEAF
        pressure unit preference. This helper only makes the displayed
        numeric value consistent with that existing unit label.
        """

        aliases = {
            "pa": "Pa",
            "kpa": "kPa",
            "MPa": "MPa",
            "bar": "bar",
            "mbar": "mbar",
            "psi": "psi",
            "atm": "atm",
        }

        factors = {
            "Pa": 1.0,
            "kPa": 1000.0,
            "MPa": 1000000.0,
            "bar": 100000.0,
            "mbar": 100.0,
            "psi": 6894.757,
            "atm": 101325.0,
        }

        text = str(
            unit
            or
            "Pa"
        ).strip()

        canonical = aliases.get(
            text.lower()
        )

        if canonical is None:
            raise ValueError(
                "Unsupported LEAF pressure display unit: "
                f"{text!r}"
            )

        return factors[
            canonical
        ]


    def pressure_display_unit(self):
        """Return the current existing LEAF pressure-unit preference."""

        return str(
            self.unit_preferences.get(
                "pressure"
            )
            or
            "Pa"
        ).strip()


    def pressure_si_to_display(
            self,
            value_pa,
    ):
        """Convert canonical SI Pa to the active display pressure unit."""

        return (
            float(
                value_pa
            )
            /
            self.pressure_unit_factor_to_pa(
                self.pressure_display_unit()
            )
        )


    def pressure_display_to_si(
            self,
            display_value,
    ):
        """Convert the active display pressure unit to canonical SI Pa."""

        return (
            float(
                display_value
            )
            *
            self.pressure_unit_factor_to_pa(
                self.pressure_display_unit()
            )
        )


    @staticmethod
    def format_input_number(value):
        """Compact stable numeric formatting for manual input fields."""

        return (
            f"{float(value):.12g}"
        )


    def _set_ambient_pressure_selector_text(
            self,
            label,
    ):
        selector = getattr(
            self,
            "ambient_pressure_preset_selector",
            None,
        )

        if selector is None:
            return

        selector.blockSignals(
            True
        )

        selector.setCurrentText(
            str(
                label
            )
        )

        selector.blockSignals(
            False
        )


    def _sync_ambient_pressure_selector_from_si(
            self,
            value_pa,
    ):
        """
        Match an externally supplied SI pressure to a known preset.

        0 Pa is canonically represented as Vacuum when reconstructing
        from the scalar engineering value because Vacuum and the
        Mercury reference intentionally share the same model value.
        """

        try:
            value_pa = float(
                value_pa
            )

        except (
            TypeError,
            ValueError,
        ):
            self._set_ambient_pressure_selector_text(
                "Custom"
            )

            entry = self.entries.get(
                "ambient_pressure"
            )

            if entry is not None:
                entry.setReadOnly(
                    False
                )

            return "Custom"

        selected = "Custom"

        for (
            label,
            preset_pa,
        ) in AMBIENT_PRESSURE_PRESETS_PA.items():

            if (
                preset_pa
                is None
            ):
                continue

            tolerance = max(
                1.0e-6,
                abs(
                    float(
                        preset_pa
                    )
                )
                *
                1.0e-9,
            )

            if (
                abs(
                    value_pa
                    -
                    float(
                        preset_pa
                    )
                )
                <=
                tolerance
            ):
                selected = label
                break

        self._set_ambient_pressure_selector_text(
            selected
        )

        entry = self.entries.get(
            "ambient_pressure"
        )

        if entry is not None:
            entry.setReadOnly(
                selected
                !=
                "Custom"
            )

        return selected


    def _on_ambient_pressure_preset_changed(
            self,
            label,
    ):
        """
        Apply one reference operating condition to the existing
        ambient_pressure input.

        No solver is executed here.
        """

        entry = self.entries.get(
            "ambient_pressure"
        )

        if entry is None:
            return

        label = str(
            label
            or
            ""
        )

        value_pa = (
            AMBIENT_PRESSURE_PRESETS_PA.get(
                label
            )
        )

        if value_pa is None:
            entry.setReadOnly(
                False
            )

            return

        display_value = (
            self.pressure_si_to_display(
                value_pa
            )
        )

        entry.setText(
            self.format_input_number(
                display_value
            )
        )

        entry.setReadOnly(
            True
        )


    def create_layout(self):
        outer_layout = QVBoxLayout(self)

        heading = QLabel("ENGINE INPUTS")
        heading.setObjectName("engineInputsHeading")
        outer_layout.addWidget(heading)

        self.advanced_toggle = QPushButton("Advanced Overrides")
        self.advanced_toggle.setObjectName("advancedInputsToggle")
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.setChecked(False)
        self.advanced_toggle.toggled.connect(
            self._toggle_advanced_inputs
        )
        outer_layout.addWidget(
            self.advanced_toggle
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        self.entry_layouts = {}
        self.section_group_boxes = {}
        self.section_layouts = {}
        self.section_input_keys = {}
        self.section_order = []

        label_by_var = {
            var_name: label
            for label, var_name
            in self.label_to_var.items()
        }

        for var_name in get_input_keys():
            if self.should_hide_input(
                var_name
            ):
                continue

            definition = get_variable(
                var_name
            )

            if definition is None:
                continue

            section = getattr(
                definition,
                "section",
                None,
            )

            if (
                not isinstance(
                    section,
                    str,
                )
                or
                not section.strip()
            ):
                section = "General"

            if section not in self.section_layouts:
                group_box = QGroupBox(
                    section
                )

                form_layout = QFormLayout(
                    group_box
                )

                self.section_group_boxes[
                    section
                ] = group_box

                self.section_layouts[
                    section
                ] = form_layout

                self.section_input_keys[
                    section
                ] = []

                self.section_order.append(
                    section
                )

                content_layout.addWidget(
                    group_box
                )

            unit = self.get_display_unit(
                var_name
            )

            label = label_by_var.get(
                var_name,
                var_name,
            )

            if unit:
                display_label = (
                    f"{label} ({unit})"
                )
            else:
                display_label = label

            entry = QLineEdit()
            entry.setMinimumWidth(160)
            entry.installEventFilter(self)

            form_layout = (
                self.section_layouts[
                    section
                ]
            )

            self.entries[
                var_name
            ] = entry

            self.entry_layouts[
                var_name
            ] = form_layout

            self.section_input_keys[
                section
            ].append(
                var_name
            )

            if (
                var_name
                ==
                "ambient_pressure"
            ):
                selector = QComboBox()

                selector.setObjectName(
                    "ambientPressurePresetSelector"
                )

                selector.addItems(
                    list(
                        AMBIENT_PRESSURE_PRESETS_PA.keys()
                    )
                )

                selector.setToolTip(
                    "Reference operating condition for ambient pressure. "
                    "The solver value remains canonical SI Pa."
                )

                entry.setToolTip(
                    "Displayed using the current LEAF pressure-unit "
                    "preference; converted to SI Pa internally."
                )

                self.ambient_pressure_preset_selector = (
                    selector
                )

                form_layout.addRow(
                    "Ambient Pressure Preset",
                    selector,
                )

                selector.currentTextChanged.connect(
                    self._on_ambient_pressure_preset_changed
                )

                selector.setCurrentText(
                    "Earth Sea Level"
                )

                self._on_ambient_pressure_preset_changed(
                    "Earth Sea Level"
                )

            form_layout.addRow(
                display_label,
                entry,
            )

        content_layout.addStretch(1)

        scroll_area.setWidget(
            content
        )

        outer_layout.addWidget(
            scroll_area
        )

        self._set_advanced_visible(
            False
        )

    def _visible_input_entries(self):
        """
        Return manual input fields in their existing canonical UI order,
        excluding rows that are currently hidden.
        """
        return [
            entry
            for entry in self.entries.values()
            if entry.isVisibleTo(self)
        ]

    def _focus_relative_input(self, current_entry, offset):
        """
        Move focus between visible manual-input QLineEdits only.

        Focus movement intentionally reuses the existing self.entries order.
        No duplicate input ordering or engineering ownership is introduced.
        """
        entries = self._visible_input_entries()

        try:
            current_index = entries.index(
                current_entry
            )
        except ValueError:
            return False

        target_index = (
            current_index
            + int(offset)
        )

        if not (
            0
            <= target_index
            < len(entries)
        ):
            return False

        entries[
            target_index
        ].setFocus()

        return True

    def eventFilter(self, watched, event):
        """
        Manual-input keyboard ergonomics.

        Enter/Return:
            move to next visible manual input.

        Up/Down:
            move to previous/next visible manual input.

        Tab and Shift+Tab are deliberately not intercepted so Qt retains
        its native focus-chain behaviour.
        """
        if (
            watched in self.entries.values()
            and
            event.type()
            == QEvent.KeyPress
        ):
            key = event.key()

            if key in (
                Qt.Key_Return,
                Qt.Key_Enter,
            ):
                if self._focus_relative_input(
                    watched,
                    1,
                ):
                    return True

            elif key == Qt.Key_Down:
                if self._focus_relative_input(
                    watched,
                    1,
                ):
                    return True

            elif key == Qt.Key_Up:
                if self._focus_relative_input(
                    watched,
                    -1,
                ):
                    return True

        return super().eventFilter(
            watched,
            event,
        )

    def _set_advanced_visible(self, visible):
        visible = bool(
            visible
        )

        for var_name, entry in self.entries.items():
            layout = self.entry_layouts[
                var_name
            ]

            row_visible = (
                visible
                if is_advanced_input(
                    var_name
                )
                else True
            )

            layout.setRowVisible(
                entry,
                row_visible,
            )

        for section, group_box in (
            self.section_group_boxes.items()
        ):
            section_has_visible_input = any(
                (
                    not is_advanced_input(
                        var_name
                    )
                )
                or
                visible

                for var_name
                in self.section_input_keys.get(
                    section,
                    ()
                )
            )

            group_box.setVisible(
                section_has_visible_input
            )

    def _toggle_advanced_inputs(self, checked):
        self._set_advanced_visible(checked)
        self.advanced_toggle.setText(
            "Hide Advanced Overrides" if checked else "Advanced Overrides"
        )

    def should_hide_input(self, var_name):
        return not (
            is_default_manual_input(var_name)
            or is_advanced_input(var_name)
        )

    def get_display_unit(self, var_name):
        unit_group = self.unit_groups.get(var_name)

        if unit_group in self.unit_preferences:
            return self.unit_preferences[unit_group]

        return self.units.get(var_name, "")

    def get_inputs(self):
        values = {}

        for (
            var_name,
            entry,
        ) in self.entries.items():

            text = (
                entry.text()
                .strip()
            )

            if not text:
                values[
                    var_name
                ] = None

                continue

            if (
                text.lower()
                in
                [
                    "n/a",
                    "none",
                    "null",
                ]
            ):
                values[
                    var_name
                ] = None

                continue

            try:
                numeric_value = float(
                    text.replace(
                        ",",
                        "",
                    )
                )

                if (
                    var_name
                    ==
                    "ambient_pressure"
                ):
                    numeric_value = (
                        self.pressure_display_to_si(
                            numeric_value
                        )
                    )

                values[
                    var_name
                ] = numeric_value

            except ValueError:
                values[
                    var_name
                ] = text

        return values

    def set_inputs(
            self,
            values,
    ):
        for (
            var_name,
            value,
        ) in values.items():

            entry = self.entries.get(
                var_name
            )

            if entry is None:
                continue

            if (
                var_name
                !=
                "ambient_pressure"
            ):
                entry.setText(
                    ""
                    if value is None
                    else str(
                        value
                    )
                )

                continue

            if value is None:
                entry.setText(
                    ""
                )

                self._set_ambient_pressure_selector_text(
                    "Custom"
                )

                entry.setReadOnly(
                    False
                )

                continue

            try:
                value_pa = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):
                entry.setText(
                    str(
                        value
                    )
                )

                self._set_ambient_pressure_selector_text(
                    "Custom"
                )

                entry.setReadOnly(
                    False
                )

                continue

            display_value = (
                self.pressure_si_to_display(
                    value_pa
                )
            )

            entry.setText(
                self.format_input_number(
                    display_value
                )
            )

            self._sync_ambient_pressure_selector_from_si(
                value_pa
            )


    def clear_inputs(self):
        for entry in self.entries.values():
            entry.clear()

        selector = getattr(
            self,
            "ambient_pressure_preset_selector",
            None,
        )

        if selector is not None:
            self._set_ambient_pressure_selector_text(
                "Custom"
            )

        ambient_entry = (
            self.entries.get(
                "ambient_pressure"
            )
        )

        if ambient_entry is not None:
            ambient_entry.setReadOnly(
                False
            )
