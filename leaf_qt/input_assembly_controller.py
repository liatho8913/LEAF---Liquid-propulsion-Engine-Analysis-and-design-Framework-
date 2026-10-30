from PySide6.QtWidgets import QMessageBox


class InputAssemblyController:
    def __init__(
            self,
            manual_input_panel,
            cea_panel,
            geometry_panel,
            materials_panel,
            get_last_results_callback,
    ):
        self.manual_input_panel = manual_input_panel
        self.cea_panel = cea_panel
        self.geometry_panel = geometry_panel
        self.materials_panel = materials_panel
        self.get_last_results = get_last_results_callback
        self.regen_geometry_override_phase_16p4 = {}

    def get_clean_manual_inputs(self):
        return self.manual_input_panel.get_inputs()


    def set_regen_geometry_override_phase_16p4(self, geometry):
        """
        Phase 16P.4C
        Stores applied regen geometry so it can be injected into solver inputs
        after normal manual/geometry/material panels have populated the input dict.
        """
        if not isinstance(geometry, dict):
            geometry = {}

        allowed_keys = {
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "number_of_coolant_channels",
            "hot_gas_wall_thickness",
            "outer_wall_thickness",
            "outer_jacket_thickness",
            "coolant_flow_fraction",
        }

        clean = {}

        for key, value in geometry.items():
            if key in allowed_keys and value is not None:
                clean[key] = value

        self.regen_geometry_override_phase_16p4 = clean
        return dict(clean)

    def clear_regen_geometry_override_phase_16p4(self):
        self.regen_geometry_override_phase_16p4 = {}

    def _apply_regen_geometry_override_phase_16p4(self, inputs):
        """
        Phase 16P.4C
        Applies accepted automatic regen geometry after all normal input sources.
        """
        override = getattr(self, "regen_geometry_override_phase_16p4", {}) or {}

        if not isinstance(override, dict) or not override:
            return

        for key, value in override.items():
            if value is not None:
                inputs[key] = value

        inputs["phase_16p4_regen_geometry_override_applied"] = True
        inputs["phase_16p4_regen_geometry_override_keys"] = sorted(override.keys())
        inputs["phase_16p4_regen_geometry_override"] = dict(override)




    def build_combined_inputs(self):
        """
        Builds one shared input dictionary from current editable engineering state:
        1. manual inputs
        2. CEA panel inputs
        3. geometry panel inputs
        4. material panel selections

        Previous solved results are outputs/evidence and must not seed a new full solve.
        """

        inputs = {}

        self._apply_manual_inputs(inputs)
        self._apply_cea_inputs(inputs)
        self._apply_geometry_inputs(inputs)
        self._apply_material_inputs(inputs)
        self._apply_regen_geometry_override_phase_16p4(inputs)

        return inputs

    def show_missing_parameter_report(self, parent=None):
        from variable_registry import is_default_manual_input

        inputs = self.manual_input_panel.get_inputs()

        missing = [
            key for key, value in inputs.items()
            if value is None
            and is_default_manual_input(key)
        ]

        if not missing:
            QMessageBox.information(
                parent,
                "Missing Parameter Report",
                "No missing required manual input parameters."
            )
            return

        message = "Missing required manual input parameters:\n\n"

        for key in missing:
            message += f"- {key}\n"

        QMessageBox.information(
            parent,
            "Missing Parameter Report",
            message
        )

    def get_available_graph_input_keys(self):
        """
        Return numerical engineering inputs genuinely available through the
        current LEAF input UI.

        This is a presentation/discovery contract only. It does not calculate,
        validate, solve, or change any input value.

        Manual advanced overrides are included only while their existing UI
        rows are visible. Registry-only/non-input result fields are never
        introduced here.
        """
        available = []
        seen = set()

        def add_key(key):
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

            seen.add(key)
            available.append(key)

        panel = self.manual_input_panel

        entries = getattr(
            panel,
            "entries",
            {},
        )

        if isinstance(
            entries,
            dict,
        ):
            for key, entry in entries.items():

                if entry is None:
                    continue

                try:
                    visible = entry.isVisibleTo(
                        panel
                    )

                except Exception:
                    visible = True

                if visible:
                    add_key(key)

        try:
            cea_inputs = (
                self.cea_panel.get_cea_inputs()
            )

        except Exception:
            cea_inputs = {}

        if (
            isinstance(
                cea_inputs,
                dict,
            )
            and
            "mixture_ratio"
            in
            cea_inputs
        ):
            add_key(
                "mixture_ratio"
            )

        if self.geometry_panel is not None:

            try:
                geometry_inputs = (
                    self.geometry_panel.get_inputs()
                )

            except Exception:
                geometry_inputs = {}

            if isinstance(
                geometry_inputs,
                dict,
            ):
                for key, value in geometry_inputs.items():

                    if isinstance(
                        value,
                        bool,
                    ):
                        continue

                    if isinstance(
                        value,
                        (
                            int,
                            float,
                        ),
                    ):
                        add_key(
                            key
                        )
                        continue

                    try:
                        float(value)

                    except (
                        TypeError,
                        ValueError,
                    ):
                        continue

                    add_key(
                        key
                    )

        return available

    def _apply_manual_inputs(self, inputs):
        manual_inputs = self.manual_input_panel.get_inputs()

        for key, value in manual_inputs.items():
            if value is not None:
                inputs[key] = value

    def _apply_cea_inputs(self, inputs):
        cea_inputs = self.cea_panel.get_cea_inputs()

        for key, value in cea_inputs.items():
            if value is not None:
                inputs[key] = value

        fuel = cea_inputs.get("fuel")
        oxidizer = cea_inputs.get("oxidizer")
        fuel_temp_k = cea_inputs.get("fuel_temp_k")
        oxidizer_temp_k = cea_inputs.get("oxidizer_temp_k")
        mixture_ratio = cea_inputs.get("mixture_ratio")
        selected_coolant_name = cea_inputs.get("selected_coolant_name")

        if fuel is not None:
            inputs["fuel"] = fuel

        if oxidizer is not None:
            inputs["oxidizer"] = oxidizer

        if fuel_temp_k is not None:
            inputs["fuel_temp_k"] = fuel_temp_k

        if oxidizer_temp_k is not None:
            inputs["oxidizer_temp_k"] = oxidizer_temp_k

        if mixture_ratio is not None:
            inputs["mixture_ratio"] = mixture_ratio

        if selected_coolant_name is not None:
            inputs["selected_coolant_name"] = selected_coolant_name

        inputs["calculation_mode"] = cea_inputs.get("calculation_mode", "CEA")
        inputs["cea_authoritative_mode"] = True

    def _apply_geometry_inputs(self, inputs):
        if self.geometry_panel is None:
            return

        geometry_inputs = self.geometry_panel.get_inputs()
        inputs.update(geometry_inputs)

    def _apply_material_inputs(self, inputs):
        if self.materials_panel is None:
            return

        material_inputs = self.materials_panel.get_selected_materials()

        for key, value in material_inputs.items():
            if value is not None:
                inputs[key] = value