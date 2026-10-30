import math
import traceback

from PySide6.QtWidgets import QMessageBox

from calculation_bridge import calculate_with_full_bridge, module_execution_enabled
from warning_logic import autosize_wall_thickness


class CalculationController:
    def __init__(
            self,
            parent,
            diagnostics_engine,
            calculation_audit_engine,
            get_inputs_callback,
            get_cea_inputs_callback,
            get_benchmark_case_callback,
            get_startup_health_callback,
            apply_selected_material_metadata_callback,
            apply_foundation_layers_callback,
            update_ui_callback,
            set_cea_raw_output_callback,
            set_status_callback,
            run_cea_rocket_case=None,
            module_runtime_integrator=None,
    ):
        self.parent = parent
        self.diagnostics_engine = diagnostics_engine
        self.calculation_audit_engine = calculation_audit_engine

        self.get_inputs = get_inputs_callback
        self.get_cea_inputs = get_cea_inputs_callback
        self.get_benchmark_case = get_benchmark_case_callback
        self.get_startup_health = get_startup_health_callback

        self.apply_selected_material_metadata = apply_selected_material_metadata_callback
        self.apply_foundation_layers = apply_foundation_layers_callback
        self.update_ui = update_ui_callback
        self.set_cea_raw_output = set_cea_raw_output_callback
        self.set_status = set_status_callback

        self.run_cea_rocket_case = run_cea_rocket_case
        self.module_runtime_integrator = module_runtime_integrator

    def _module_execution_policy(self):
        if self.module_runtime_integrator is None:
            return None

        return self.module_runtime_integrator.execution_policy()

    def calculate(self):
        """
        Execute one canonical LEAF calculation.

        The Propellants panel calculation-mode selection determines
        thermodynamic authority:

        - CEA: NASA CEA supplies the authoritative thermodynamic state.
        - Manual: only the assembled user/manual thermodynamic state is used.

        This method performs calculation only. Presentation windows are
        opened separately by WindowLaunchController.
        """
        cea_inputs = self.get_cea_inputs()

        if not isinstance(cea_inputs, dict):
            cea_inputs = {}

        calculation_mode = str(
            cea_inputs.get("calculation_mode")
            or "CEA"
        ).strip().upper()

        if calculation_mode == "CEA":
            return self.run_cea_and_calculate()

        if calculation_mode != "MANUAL":
            self._handle_calculation_failure(
                "Calculation failed",
                ValueError(
                    "Unsupported calculation mode: "
                    f"{calculation_mode!r}"
                ),
            )
            return None

        try:
            module_execution_policy = (
                self._module_execution_policy()
            )

            inputs = self.get_inputs()

            if not isinstance(inputs, dict):
                inputs = {}

            # Manual mode must remain genuinely manual.
            # Do not call apply_cea_fallbacks(), because that helper
            # explicitly establishes CEA-authoritative state.
            inputs["calculation_mode"] = "Manual"
            inputs["cea_authoritative_mode"] = False
            inputs["cea_authoritative_used"] = False

            inputs = self.apply_geometry_fallbacks(
                inputs,
                module_execution_policy=module_execution_policy,
            )

            solved = self._run_full_pipeline(
                inputs,
                module_execution_policy=module_execution_policy,
            )

            required_outputs = (
                "throat_area",
                "exit_area",
                "characteristic_velocity",
                "thrust",
                "specific_impulse",
            )

            missing_outputs = [
                key
                for key in required_outputs
                if solved.get(key) is None
            ]

            if missing_outputs:
                self.set_status(
                    "Manual calculation incomplete — "
                    "thermodynamic inputs required"
                )

                QMessageBox.warning(
                    self.parent,
                    "Calculation Incomplete",
                    "Manual mode did not produce the required "
                    "engine outputs.\n\n"
                    "Missing outputs: "
                    + ", ".join(missing_outputs)
                    + "\n\nProvide the required manual "
                    "thermodynamic inputs or select CEA mode.",
                )

                return None

            self.set_status(
                "Manual calculation complete"
            )

            return solved

        except Exception as error:
            self._handle_calculation_failure(
                "Manual calculation failed",
                error,
            )

            return None

    def run_cea_and_calculate(self):
        try:
            if self.run_cea_rocket_case is None:
                QMessageBox.warning(
                    self.parent,
                    "CEA Unavailable",
                    "NASA CEA integration is unavailable. Run normal Calculate instead.",
                )
                self.set_status("CEA unavailable")
                return

            inputs = self.get_inputs()
            cea_inputs = self.get_cea_inputs()

            mixture_ratio = cea_inputs.get("mixture_ratio")
            selected_coolant_name = cea_inputs.get("selected_coolant_name")

            if selected_coolant_name is not None:
                inputs["selected_coolant_name"] = selected_coolant_name

            if mixture_ratio is not None:
                inputs["mixture_ratio"] = mixture_ratio

            chamber_pressure = inputs.get("chamber_pressure")

            if chamber_pressure is None:
                raise ValueError("Chamber pressure is required for CEA mode.")

            expansion_ratio = inputs.get("expansion_ratio") or 1.0

            cea_results, raw_output = self.run_cea_rocket_case(
                fuel_name=cea_inputs["fuel"],
                fuel_temp_k=cea_inputs["fuel_temp_k"],
                oxidizer_name=cea_inputs["oxidizer"],
                oxidizer_temp_k=cea_inputs["oxidizer_temp_k"],
                chamber_pressure_pa=chamber_pressure,
                mixture_ratio=mixture_ratio,
                expansion_ratio=expansion_ratio,
            )

            module_execution_policy = self._module_execution_policy()
            inputs = self.apply_cea_authority_to_inputs(inputs, cea_results)
            inputs = self.apply_geometry_fallbacks(
                inputs, module_execution_policy=module_execution_policy
            )

            solved = self._run_full_pipeline(
                inputs,
                cea_results=cea_results,
                module_execution_policy=module_execution_policy,
            )

            self.set_cea_raw_output(str(raw_output or cea_results))
            self.set_status("CEA + calculation complete")

            return solved

        except Exception as error:
            self.set_cea_raw_output(f"CEA failed:\n\n{error}")
            self._handle_calculation_failure("CEA failed", error)

    def _run_full_pipeline(
            self,
            inputs,
            cea_results=None,
            module_execution_policy=None,
    ):
        """
        Authoritative calculation order:

        inputs
        → optional CEA authority
        → geometry fallbacks
        → engine solve
        → post-solver fallbacks
        → selected material metadata
        → regen/wall autosizing
        → foundation layers
        → diagnostics/audit
        → UI update
        """

        solved, history = calculate_with_full_bridge(
            inputs,
            module_execution_policy=module_execution_policy,
        )

        if cea_results is not None:
            solved = self.apply_cea_authority_to_inputs(solved, cea_results)

        solved = self.apply_post_solver_fallbacks(
            solved, module_execution_policy=module_execution_policy
        )
        solved = self.apply_selected_material_metadata(solved)
        if module_execution_enabled(module_execution_policy, "regen"):
            solved = autosize_wall_thickness(solved)

        if isinstance(solved, dict):
            solved["calculation_history"] = history

        solved = self.apply_foundation_layers(solved)

        diagnostics_report = self.diagnostics_engine.evaluate(solved)
        audit_rows = self.calculation_audit_engine.audit(solved)

        self.update_ui(
            solved=solved,
            diagnostics_report=diagnostics_report,
            audit_rows=audit_rows,
        )

        return solved

    def _handle_calculation_failure(self, title, error):
        message = f"{title}: {error}"

        self.set_status(message)

        print(title)
        print(error)
        traceback.print_exc()

        QMessageBox.critical(
            self.parent,
            title,
            f"{message}\n\nSee terminal output for full traceback.",
        )

    def apply_cea_authority_to_inputs(self, inputs, cea_results):
        if not isinstance(inputs, dict):
            inputs = {}

        if not isinstance(cea_results, dict):
            return inputs

        inputs.update(cea_results)
        inputs["cea_authoritative_used"] = True

        def first_available(*keys):
            for key in keys:
                value = inputs.get(key)
                if value is not None:
                    return value
            return None

        cea_chamber_temperature = first_available(
            "cea_chamber_temperature",
            "cea_combustion_temperature",
            "cea_adiabatic_flame_temperature",
        )

        if cea_chamber_temperature is not None:
            inputs["chamber_temperature"] = cea_chamber_temperature

        cea_gamma = first_available(
            "cea_selected_gamma",
            "cea_chamber_gamma",
            "cea_throat_gamma",
            "cea_exit_gamma",
        )

        if cea_gamma is not None:
            inputs["Gamma"] = cea_gamma

        cea_molecular_weight = first_available(
            "cea_selected_molecular_weight",
            "cea_molecular_weight",
            "cea_chamber_molecular_weight",
            "cea_throat_molecular_weight",
            "cea_exit_molecular_weight",
        )

        if cea_molecular_weight is not None and cea_molecular_weight > 0:
            inputs["cea_selected_molecular_weight"] = cea_molecular_weight
            inputs["R"] = 8314.462618 / cea_molecular_weight

        cea_cp = first_available(
            "cea_selected_cp",
            "cea_cp_frozen",
            "cea_throat_cp",
            "cea_exit_cp",
        )

        if cea_cp is not None:
            inputs["specific_heat_cp"] = cea_cp
            inputs["gas_specific_heat_cp"] = cea_cp

        cea_prandtl = first_available(
            "cea_selected_prandtl",
            "cea_throat_prandtl",
            "cea_exit_prandtl",
            "gas_prandtl_number",
        )

        if cea_prandtl is not None:
            inputs["gas_prandtl_number"] = cea_prandtl

        cea_viscosity = first_available(
            "cea_selected_viscosity",
            "cea_throat_viscosity",
            "cea_exit_viscosity",
        )

        if cea_viscosity is not None:
            inputs["gas_dynamic_viscosity"] = cea_viscosity

        cea_conductivity = first_available(
            "cea_selected_conductivity",
            "cea_throat_conductivity",
            "cea_exit_conductivity",
        )

        if cea_conductivity is not None:
            inputs["gas_thermal_conductivity"] = cea_conductivity

        return inputs

    def apply_cea_fallbacks(self, inputs):
        if not isinstance(inputs, dict):
            inputs = {}

        inputs["cea_authoritative_mode"] = True

        if inputs.get("selected_length") is not None:
            if inputs.get("cea_selected_cp") is None:
                inputs["cea_selected_cp"] = inputs.get("specific_heat_cp")

            if inputs.get("cea_selected_gamma") is None:
                inputs["cea_selected_gamma"] = inputs.get("Gamma")

            if inputs.get("cea_selected_molecular_weight") is None:
                inputs["cea_selected_molecular_weight"] = inputs.get("cea_molecular_weight")

            if inputs.get("cea_selected_prandtl") is None:
                inputs["cea_selected_prandtl"] = inputs.get("gas_prandtl_number")

            if inputs.get("cea_selected_viscosity") is None:
                inputs["cea_selected_viscosity"] = inputs.get("cea_viscosity")

            if inputs.get("cea_selected_conductivity") is None:
                inputs["cea_selected_conductivity"] = inputs.get("cea_conductivity")

        return inputs

    def apply_geometry_fallbacks(self, inputs, module_execution_policy=None):
        if not isinstance(inputs, dict):
            inputs = {}

        pi = math.pi
        nozzle_active = module_execution_enabled(
            module_execution_policy, "nozzle"
        )

        throat_area = inputs.get("throat_area")
        exit_area = inputs.get("exit_area")
        expansion_ratio = inputs.get("expansion_ratio")

        throat_radius = inputs.get("throat_radius")
        exit_radius = inputs.get("exit_radius")

        selected_length = inputs.get("selected_length")
        nozzle_length = inputs.get("nozzle_length")

        if nozzle_active:
            if throat_area is None and throat_radius is not None:
                throat_area = pi * throat_radius ** 2
                inputs["throat_area"] = throat_area

            if throat_radius is None and throat_area is not None and throat_area > 0:
                throat_radius = math.sqrt(throat_area / pi)
                inputs["throat_radius"] = throat_radius

            if exit_area is None and exit_radius is not None:
                exit_area = pi * exit_radius ** 2
                inputs["exit_area"] = exit_area

            if exit_radius is None and exit_area is not None and exit_area > 0:
                exit_radius = math.sqrt(exit_area / pi)
                inputs["exit_radius"] = exit_radius

            if expansion_ratio is None and throat_area is not None and exit_area is not None and throat_area > 0:
                expansion_ratio = exit_area / throat_area
                inputs["expansion_ratio"] = expansion_ratio

            if exit_area is None and throat_area is not None and expansion_ratio is not None:
                exit_area = throat_area * expansion_ratio
                inputs["exit_area"] = exit_area
                inputs["exit_radius"] = math.sqrt(exit_area / pi)

        if nozzle_active:
            if inputs.get("radius_2") is None and throat_radius is not None:
                inputs["radius_2"] = throat_radius * 1.5

            if inputs.get("radius_3") is None and throat_radius is not None:
                inputs["radius_3"] = throat_radius * 0.382

            if nozzle_length is None and throat_radius is not None and exit_radius is not None:
                model = str(
                    inputs.get("nozzle_geometry_model")
                    or "RAO_BELL_APPROXIMATION"
                ).upper()

                conical_half_angle_deg = inputs.get("conical_half_angle_deg") or 15.0
                rao_length_fraction = inputs.get("rao_length_fraction") or 0.8

                half_angle_rad = math.radians(conical_half_angle_deg)

                if math.tan(half_angle_rad) != 0:
                    conical_length = (exit_radius - throat_radius) / math.tan(half_angle_rad)

                    if model == "CONICAL":
                        nozzle_length = conical_length
                    else:
                        nozzle_length = conical_length * rao_length_fraction

                    inputs["nozzle_length"] = nozzle_length

            if selected_length is None and nozzle_length is not None:
                inputs["selected_length"] = nozzle_length

        return inputs

    def apply_post_solver_fallbacks(self, solved, module_execution_policy=None):
        if not isinstance(solved, dict):
            solved = {}

        nozzle_active = module_execution_enabled(
            module_execution_policy, "nozzle"
        )

        mass_flow_rate = solved.get("mass_flow_rate")
        characteristic_velocity = solved.get("characteristic_velocity")
        chamber_pressure = solved.get("chamber_pressure")
        throat_area = solved.get("throat_area")

        if nozzle_active:
            if throat_area is None:
                if (
                        mass_flow_rate is not None
                        and characteristic_velocity is not None
                        and chamber_pressure is not None
                        and chamber_pressure > 0
                ):
                    throat_area = mass_flow_rate * characteristic_velocity / chamber_pressure
                    solved["throat_area"] = throat_area

            if solved.get("throat_radius") is None and throat_area is not None and throat_area > 0:
                solved["throat_radius"] = math.sqrt(throat_area / math.pi)

            expansion_ratio = solved.get("expansion_ratio")

            if expansion_ratio is not None and throat_area is not None:
                exit_area = solved.get("exit_area")

                if exit_area is None:
                    exit_area = throat_area * expansion_ratio
                    solved["exit_area"] = exit_area

                if solved.get("exit_radius") is None and exit_area > 0:
                    solved["exit_radius"] = math.sqrt(exit_area / math.pi)

        throat_radius = solved.get("throat_radius")

        if nozzle_active:
            if solved.get("radius_2") is None and throat_radius is not None:
                solved["radius_2"] = throat_radius * 1.5

            if solved.get("radius_3") is None and throat_radius is not None:
                solved["radius_3"] = throat_radius * 0.382

            exit_radius = solved.get("exit_radius")

            if solved.get("nozzle_length") is None:
                if throat_radius is not None and exit_radius is not None:
                    model = str(
                        solved.get("nozzle_geometry_model")
                        or "RAO_BELL_APPROXIMATION"
                    ).upper()

                    conical_half_angle_deg = solved.get("conical_half_angle_deg") or 15.0
                    rao_length_fraction = solved.get("rao_length_fraction") or 0.8

                    conical_length = (
                        exit_radius - throat_radius
                    ) / math.tan(math.radians(conical_half_angle_deg))

                    if model == "CONICAL":
                        solved["nozzle_length"] = conical_length
                    else:
                        solved["nozzle_length"] = conical_length * rao_length_fraction

        return solved