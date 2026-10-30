from PySide6.QtWidgets import QMessageBox


class RecommendedDesignController:
    def __init__(
            self,
            parent,
            manual_input_panel,
            materials_panel,
            get_results_callback,
            set_status_callback,
    ):
        self.parent = parent
        self.manual_input_panel = manual_input_panel
        self.materials_panel = materials_panel
        self.get_results = get_results_callback
        self.set_status = set_status_callback

    def set_manual_input_value(self, var_name, value, only_if_empty=False):
        entry = self.manual_input_panel.entries.get(var_name)

        if entry is None or value is None:
            return

        if only_if_empty:
            current_text = entry.text().strip()

            if current_text not in ["", "N/A", "n/a", "None", "none"]:
                return

        entry.setText(f"{value:.8g}" if isinstance(value, float) else str(value))

    def apply_liner_material_to_regen_inputs(self):
        material_name, material = self.materials_panel.get_hot_gas_liner_material()

        if material is None:
            self.set_status(f"Could not find material: {material_name}")
            return

        self.set_manual_input_value(
            "material_yield_strength",
            material.get("yield_strength"),
        )

        self.set_manual_input_value(
            "wall_thermal_conductivity",
            material.get("thermal_conductivity"),
        )

        self.set_manual_input_value(
            "material_density",
            material.get("density"),
        )

        self.set_manual_input_value(
            "material_max_wall_temperature",
            material.get("max_recommended_wall_temperature"),
        )

        self.set_manual_input_value("wall_safety_factor", 2.0, only_if_empty=True)
        self.set_manual_input_value("wall_joint_efficiency", 1.0, only_if_empty=True)
        self.set_manual_input_value("coolant_side_wall_temperature", 600.0, only_if_empty=True)
        self.set_manual_input_value("minimum_wall_thickness", 0.001, only_if_empty=True)
        self.set_manual_input_value("corrosion_allowance", 0.0002, only_if_empty=True)
        self.set_manual_input_value("hot_gas_heat_transfer_coefficient", 8000.0, only_if_empty=True)
        self.set_manual_input_value("coolant_channel_height", 0.002, only_if_empty=True)
        self.set_manual_input_value("coolant_channel_width", 0.0015, only_if_empty=True)
        self.set_manual_input_value("rib_width", 0.001, only_if_empty=True)
        self.set_manual_input_value("outer_jacket_thickness", 0.002, only_if_empty=True)
        self.set_manual_input_value("coating_thickness", 0.0, only_if_empty=True)
        self.set_manual_input_value("number_of_coolant_channels", 80.0, only_if_empty=True)

        self.set_status(f"Applied regen liner material: {material_name}")

    def apply_selected_material_metadata_to_results(self, final_params):
        if final_params is None:
            return final_params

        material_name, material = self.materials_panel.get_hot_gas_liner_material()

        if material is None:
            return final_params

        final_params["selected_material_name"] = material_name

        material_identity = (
            self.materials_panel.get_selected_materials()
        )

        final_params["selected_material_form"] = (
            material_identity.get(
                "selected_material_form"
            )
        )

        final_params["selected_material_heat_treatment"] = (
            material_identity.get(
                "selected_material_heat_treatment"
            )
        )

        if final_params.get("material_density") is None:
            final_params["material_density"] = material.get("density")

        if final_params.get("material_max_wall_temperature") is None:
            final_params["material_max_wall_temperature"] = material.get(
                "max_recommended_wall_temperature"
            )

        if final_params.get("material_yield_strength") is None:
            final_params["material_yield_strength"] = material.get("yield_strength")

        if final_params.get("wall_thermal_conductivity") is None:
            final_params["wall_thermal_conductivity"] = material.get(
                "thermal_conductivity"
            )

        return final_params

    def apply_recommended_regen_geometry_to_inputs(self):
        results = self.get_results()

        if not isinstance(results, dict) or not results:
            QMessageBox.warning(
                self.parent,
                "No Results",
                "Run a calculation before applying the recommended design.",
            )
            return

        design_package = results.get("recommended_design_package")

        if not isinstance(design_package, dict) or not design_package:
            design_package = {
                "number_of_coolant_channels": results.get("recommended_channel_count"),
                "coolant_channel_width": results.get("recommended_channel_width"),
                "coolant_channel_height": results.get("recommended_channel_height"),
                "rib_width": results.get("recommended_rib_width"),

                "selected_material": results.get("material_aware_combined_best_material"),
                "selected_material_name": results.get("material_aware_combined_best_material"),
                "material_name": results.get("material_aware_combined_best_material"),
                "hot_gas_liner": results.get("material_aware_combined_best_material"),

                "selected_coating_material": results.get("explicit_coating_material"),
                "selected_bond_coat": results.get("active_bond_coat"),
                "coating_thickness": results.get("explicit_coating_thickness"),
            }

        design_package = {
            key: value
            for key, value in design_package.items()
            if value not in (None, "", "N/A", "None")
        }

        required_geometry_keys = [
            "number_of_coolant_channels",
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
        ]

        missing_geometry = [
            key for key in required_geometry_keys
            if key not in design_package
        ]

        if missing_geometry:
            QMessageBox.warning(
                self.parent,
                "Recommended Design Missing",
                "Recommended regen geometry is incomplete:\n"
                + "\n".join(missing_geometry),
            )
            return

        status = str(results.get("recommended_geometry_status", "")).upper()
        valid = results.get("recommended_geometry_valid")

        if status not in ("PASS", "BEST_AVAILABLE_BELOW_TARGET") and valid != 1:
            reply = QMessageBox.question(
                self.parent,
                "Recommended Design Not Fully Valid",
                f"Recommended geometry status is {status or 'UNKNOWN'}.\n\n"
                "Apply the best available recommended design anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

        manual_values = {
            key: value
            for key, value in design_package.items()
            if key in getattr(self.manual_input_panel, "entries", {})
        }

        material_values = {
            key: value
            for key, value in design_package.items()
            if key not in manual_values
        }

        if manual_values:
            self.manual_input_panel.set_inputs(manual_values)

        if self.materials_panel is not None:
            self.materials_panel.set_inputs(material_values)

        applied_manual_inputs = self.manual_input_panel.get_inputs()
        applied_material_inputs = {}

        if self.materials_panel is not None:
            applied_material_inputs = self.materials_panel.get_selected_materials()

        failed = []

        for key, expected in design_package.items():
            actual = None

            if key in applied_manual_inputs:
                actual = applied_manual_inputs.get(key)
            elif key in applied_material_inputs:
                actual = applied_material_inputs.get(key)

            if actual is None:
                continue

            try:
                expected_f = float(expected)
                actual_f = float(actual)

                tolerance = max(abs(expected_f) * 1.0e-6, 1.0e-12)

                if abs(expected_f - actual_f) > tolerance:
                    failed.append((key, expected, actual))

            except Exception:
                if str(expected) != str(actual):
                    failed.append((key, expected, actual))

        if failed:
            message = "Some recommended values did not apply correctly:\n\n"

            for key, expected, actual in failed:
                message += f"{key}: expected {expected}, got {actual}\n"

            QMessageBox.warning(
                self.parent,
                "Apply Verification Failed",
                message,
            )
            return

        applied_keys = "\n".join(
            f"- {key}: {value}"
            for key, value in design_package.items()
        )

        QMessageBox.information(
            self.parent,
            "Recommended Design Applied",
            "Recommended design package has been applied.\n\n"
            "Applied values:\n"
            f"{applied_keys}\n\n"
            "Recalculate now to verify the updated design.",
        )