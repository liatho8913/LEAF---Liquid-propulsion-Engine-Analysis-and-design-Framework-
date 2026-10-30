from collections import OrderedDict
import numpy as np

from calculation_bridge import calculate_with_full_bridge
from cea_integration.cea_runner import run_cea_rocket_case
from propellant_database import (
    canonical_fuel,
    canonical_oxidizer,
    get_default_fuel_temperature_k,
    get_default_oxidizer_temperature_k,
    get_cea_fuel_name,
    get_cea_oxidizer_name,
    get_of_ratio_range_for_pair,
    get_fuel_density_kg_m3,
    get_oxidizer_density_kg_m3,
)


GRAPH_INPUT_DEFAULTS = {
    "Gamma": 1.22,
    "R": 370.0,
    "specific_heat_cp": 2500.0,
    "specific_heat_cv": None,

    "mass_flow_rate": 1.0,
    "mixture_ratio": 2.5,

    "fuel_mass_flow_rate": None,
    "oxidizer_mass_flow_rate": None,

    "chamber_pressure": 3_000_000.0,
    "chamber_temperature": 3200.0,

    "characteristic_length": 1.0,
    "characteristic_velocity": None,

    "throat_area": 0.00025,
    "exit_area": 0.0025,
    "expansion_ratio": 10.0,

    "selected_length": 0.0,
    "nozzle_length": 0.08,

    "ambient_pressure": 101325.0,

    "combustion_efficiency": 1.0,
    "mixture_quality_factor": 1.0,
    "soot_risk_factor": 1.0,
    "thermal_risk_factor": 1.0,

    "fuel": "RP-1 / Kerosene",
    "oxidizer": "O2(L)",
    "fuel_temp_k": 298.0,
    "oxidizer_temp_k": 90.0,
    "calculation_mode": "CEA",
    "cea_authoritative_mode": True,

    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.002,
    "rib_width": 0.001,
    "outer_jacket_thickness": 0.002,
    "number_of_coolant_channels": 80.0,
    "selected_station_length": 0.001,
    "coolant_flow_fraction": 1.0,
}


CEA_AUTHORITATIVE_CORE_OUTPUTS = frozenset({
    "Gamma",
    "R",
    "chamber_temperature",
    "characteristic_velocity",
    "specific_heat_cp",
    "specific_heat_cv",
    "gas_specific_heat_cp",
    "gas_prandtl_number",
    "gas_dynamic_viscosity",
    "gas_thermal_conductivity",
})


DEPENDENCY_GRAPH = {
    "fuel_mass_flow_rate": {"mass_flow_rate", "mixture_ratio"},
    "oxidizer_mass_flow_rate": {"mass_flow_rate", "mixture_ratio"},

    "throat_area": {
        "mass_flow_rate",
        "chamber_pressure",
        "characteristic_velocity",
        "Gamma",
        "R",
        "chamber_temperature",
    },

    "throat_radius": {"throat_area"},
    "exit_area": {"throat_area", "expansion_ratio"},
    "exit_radius": {"exit_area"},
    "nozzle_length": {"throat_radius", "exit_radius"},
    "selected_expansion_ratio": {
        "selected_length",
        "nozzle_length",
        "throat_area",
        "exit_area",
        "throat_radius",
        "exit_radius",
    },
    "cross_sectional_area": {
        "selected_length",
        "nozzle_length",
        "throat_area",
        "exit_area",
        "throat_radius",
        "exit_radius",
    },

    "selected_mach_number": {
        "selected_expansion_ratio",
        "Gamma",
        "selected_length",
        "throat_area",
        "cross_sectional_area",
    },
    "mach_number": {"expansion_ratio", "Gamma"},

    "static_temperature": {
        "chamber_temperature",
        "selected_mach_number",
        "Gamma",
    },
    "static_pressure": {
        "chamber_pressure",
        "selected_mach_number",
        "Gamma",
    },
    "static_density": {"static_pressure", "static_temperature", "R"},

    "exit_pressure": {"chamber_pressure", "mach_number", "Gamma"},
    "exhaust_velocity": {
        "Gamma",
        "R",
        "chamber_temperature",
        "chamber_pressure",
        "exit_pressure",
    },

    "momentum_thrust": {"mass_flow_rate", "exhaust_velocity"},
    "pressure_thrust": {"exit_pressure", "ambient_pressure", "exit_area"},
    "thrust": {"momentum_thrust", "pressure_thrust", "mass_flow_rate", "exhaust_velocity"},
    "specific_impulse": {"thrust", "mass_flow_rate"},
    "vacuum_specific_impulse": {"thrust", "mass_flow_rate"},
    "sea_level_specific_impulse": {"thrust", "mass_flow_rate"},
    "thrust_coefficient": {"thrust", "chamber_pressure", "throat_area"},
    "effective_exhaust_velocity": {"thrust", "mass_flow_rate"},

    "ideal_engine_thrust": {"thrust"},
    "ideal_engine_specific_impulse": {"specific_impulse"},
    "ideal_volumetric_thrust": {
        "thrust",
        "fuel_density",
        "oxidizer_density",
        "fuel_mass_flow_rate",
        "oxidizer_mass_flow_rate",
    },

    "corrected_thrust": {
        "thrust",
        "mixture_ratio",
        "mass_flow_rate",
        "combustion_efficiency",
        "mixture_quality_factor",
        "soot_risk_factor",
        "thermal_risk_factor",
    },
    "corrected_specific_impulse": {
        "specific_impulse",
        "combustion_efficiency",
        "mixture_quality_factor",
        "soot_risk_factor",
        "thermal_risk_factor",
    },

    "fuel_density": {"mixture_ratio"},
    "oxidizer_density": {"mixture_ratio"},
    "total_propellant_volume_flow_rate": {
        "fuel_density",
        "oxidizer_density",
        "fuel_mass_flow_rate",
        "oxidizer_mass_flow_rate",
    },
    "volumetric_corrected_thrust": {
        "corrected_thrust",
        "total_propellant_volume_flow_rate",
    },

    "adiabatic_wall_temperature": {
        "chamber_temperature",
        "selected_mach_number",
        "Gamma",
    },
    "selected_gas_side_recovery_temperature": {
        "adiabatic_wall_temperature",
        "static_temperature",
        "selected_mach_number",
    },
    "compressibility_correlation_factor": {
        "selected_gas_side_recovery_temperature",
        "chamber_temperature",
        "selected_mach_number",
    },

    "bartz_gas_side_heat_transfer_coefficient": {
        "chamber_pressure",
        "characteristic_velocity",
        "throat_diameter",
        "throat_radius_of_curvature",
        "cross_sectional_area",
        "throat_area",
        "gas_dynamic_viscosity",
        "gas_specific_heat_cp",
        "gas_prandtl_number",
        "bartz_sigma",
        "selected_length",
    },

    "hot_gas_heat_transfer_coefficient": {"bartz_gas_side_heat_transfer_coefficient"},
    "hot_gas_heat_flux": {
        "hot_gas_heat_transfer_coefficient",
        "selected_gas_side_recovery_temperature",
        "coolant_side_wall_temperature",
    },

    "allowable_wall_stress": {
        "material_yield_strength",
        "wall_safety_factor",
        "wall_joint_efficiency",
    },
    "pressure_required_wall_thickness": {
        "chamber_pressure",
        "throat_radius",
        "allowable_wall_stress",
    },
    "conduction_required_wall_thickness": {
        "hot_gas_heat_flux",
        "wall_thermal_conductivity",
        "selected_gas_side_recovery_temperature",
        "coolant_side_wall_temperature",
    },
    "hot_gas_wall_thickness": {
        "pressure_required_wall_thickness",
        "conduction_required_wall_thickness",
        "minimum_wall_thickness",
        "corrosion_allowance",
        "coating_thickness",
    },

    "single_channel_flow_area": {"coolant_channel_width", "coolant_channel_height"},
    "total_coolant_flow_area": {
        "single_channel_flow_area",
        "number_of_coolant_channels",
    },
    "coolant_wetted_perimeter": {"coolant_channel_width", "coolant_channel_height"},
    "coolant_hydraulic_diameter": {
        "single_channel_flow_area",
        "coolant_wetted_perimeter",
    },
    "channel_pitch": {
        "coolant_channel_width",
        "rib_width",
    },
    "channel_mid_radius": {
        "cross_sectional_area",
        "hot_gas_wall_thickness",
        "coolant_channel_height",
    },
    "circumferential_channel_pitch": {
        "channel_mid_radius",
        "number_of_coolant_channels",
    },
    "effective_rib_width": {
        "circumferential_channel_pitch",
        "coolant_channel_width",
    },
    "channel_fit_ratio": {
        "channel_pitch",
        "circumferential_channel_pitch",
    },
    "channel_geometry_valid": {"channel_fit_ratio"},
    "regen_cross_section_outer_radius": {
        "cross_sectional_area",
        "hot_gas_wall_thickness",
        "coolant_channel_height",
        "outer_jacket_thickness",
        "coating_thickness",
    },

    "coolant_mass_flow_rate": {
        "fuel_mass_flow_rate",
        "coolant_flow_fraction",
    },
    "coolant_mass_flow_per_channel": {
        "coolant_mass_flow_rate",
        "number_of_coolant_channels",
    },
    "coolant_velocity": {
        "coolant_mass_flow_rate",
        "coolant_density",
        "total_coolant_flow_area",
    },
    "coolant_reynolds_number": {
        "coolant_density",
        "coolant_velocity",
        "coolant_hydraulic_diameter",
        "coolant_dynamic_viscosity",
    },
    "coolant_prandtl_number": {
        "coolant_specific_heat_cp",
        "coolant_dynamic_viscosity",
        "coolant_thermal_conductivity",
    },
    "coolant_nusselt_number": {
        "coolant_reynolds_number",
        "coolant_prandtl_number",
    },
    "coolant_heat_transfer_coefficient": {
        "coolant_nusselt_number",
        "coolant_thermal_conductivity",
        "coolant_hydraulic_diameter",
    },
    "coolant_friction_factor": {"coolant_reynolds_number"},
    "coolant_pressure_drop": {
        "coolant_friction_factor",
        "selected_station_length",
        "coolant_hydraulic_diameter",
        "coolant_density",
        "coolant_velocity",
    },

    "regen_total_thermal_resistance": {
        "hot_gas_heat_transfer_coefficient",
        "hot_gas_wall_thickness",
        "wall_thermal_conductivity",
        "coolant_heat_transfer_coefficient",
    },
    "regen_heat_flux": {
        "selected_gas_side_recovery_temperature",
        "coolant_bulk_temperature",
        "regen_total_thermal_resistance",
    },
    "hot_gas_side_wall_temperature": {
        "selected_gas_side_recovery_temperature",
        "regen_heat_flux",
        "hot_gas_heat_transfer_coefficient",
    },
    "coolant_side_wall_temperature_calculated": {
        "coolant_bulk_temperature",
        "regen_heat_flux",
        "coolant_heat_transfer_coefficient",
    },
    "coolant_temperature_rise": {
        "regen_heat_flux",
        "local_hot_gas_surface_area",
        "coolant_mass_flow_rate",
        "coolant_specific_heat_cp",
    },
    "coolant_outlet_temperature": {
        "coolant_bulk_temperature",
        "coolant_temperature_rise",
    },
    "material_temperature_margin": {
        "material_max_wall_temperature",
        "hot_gas_side_wall_temperature",
    },
}


class GraphExplorerEngine:
    def __init__(self):
        self.solver_cache = OrderedDict()
        self.solver_cache_limit = 512

        self.graph_cea_cache = OrderedDict()
        self.graph_cea_cache_limit = 256

        self.last_errors = []

    def make_cache_key(self, inputs):
        items = []

        for key, value in sorted(inputs.items()):
            if isinstance(value, float):
                value = round(value, 12)
            elif isinstance(value, (list, dict, set)):
                value = str(value)

            items.append((key, value))

        return tuple(items)

    def prepare_graph_inputs(self, inputs):
        """
        Build the scalar engineering state used by graph-point solves.

        Graph Explorer may receive the complete LEAF result dictionary so that
        axial viewer data remains available to the window. Nested profiles,
        reports, histories and other result containers are not solver inputs
        and must not be carried through every sweep point or cache key.
        """
        prepared = dict(GRAPH_INPUT_DEFAULTS)

        for key, value in dict(inputs or {}).items():
            if value is None:
                continue

            if isinstance(value, np.generic):
                value = value.item()

            if isinstance(value, str):
                # Short strings are legitimate engineering selections such as
                # fuel, oxidizer, coolant and mode. Long/multiline strings are
                # reports or diagnostics, not solver inputs.
                if "\n" in value or len(value) > 512:
                    continue

            elif not isinstance(
                value,
                (bool, int, float),
            ):
                # Lists/dicts/sets/arrays include axial profiles, reports,
                # histories and other result-owned structures. They remain in
                # the authoritative result object but not in graph-point solves.
                continue

            prepared[key] = value

        prepared.setdefault("combustion_efficiency", 1.0)
        prepared.setdefault("mixture_quality_factor", 1.0)
        prepared.setdefault("soot_risk_factor", 1.0)
        prepared.setdefault("thermal_risk_factor", 1.0)

        return prepared

    @staticmethod
    def compact_graph_solution(solved):
        """
        Retain the numerical engineering outputs useful to Graph Explorer.

        The full solver still executes. Only the cache representation is
        compacted so reports, station profiles, histories and nested validation
        payloads are not retained once per sweep point.
        """
        compact = {}

        identity_keys = {
            "fuel",
            "fuel_type",
            "oxidizer",
            "oxidizer_type",
            "calculation_mode",

            # Existing solver-owned Regen state consumed by Graph Explorer.
            # These values are presentation evidence, not new qualification.
            "regen_geometry_status",
            "regen_coolant_status",
            "regen_thermal_status",
            "regen_material_status",
            "regen_overall_status",
            "regen_feasibility_status",
        }

        for key, value in dict(solved or {}).items():
            if isinstance(value, np.generic):
                value = value.item()

            if isinstance(
                value,
                (bool, int, float),
            ):
                compact[key] = value

            elif (
                key in identity_keys
                and isinstance(value, str)
            ):
                compact[key] = value

        return compact

    def apply_cea_authority_to_inputs(self, inputs, cea_results):
        if not isinstance(cea_results, dict):
            return inputs

        inputs.update(cea_results)
        inputs["cea_authoritative_mode"] = True

        def first_available(*keys):
            for key in keys:
                value = inputs.get(key)
                if value is not None:
                    return value
            return None

        chamber_temperature = first_available(
            "cea_chamber_temperature",
            "cea_combustion_temperature",
            "cea_adiabatic_flame_temperature",
        )

        if chamber_temperature is not None:
            inputs["chamber_temperature"] = chamber_temperature

        gamma = first_available(
            "cea_selected_gamma",
            "cea_chamber_gamma",
            "cea_throat_gamma",
            "cea_exit_gamma",
        )

        if gamma is not None:
            inputs["Gamma"] = gamma

        molecular_weight = first_available(
            "cea_selected_molecular_weight",
            "cea_molecular_weight",
            "cea_chamber_molecular_weight",
            "cea_throat_molecular_weight",
            "cea_exit_molecular_weight",
        )

        if molecular_weight is not None and molecular_weight > 0:
            inputs["cea_selected_molecular_weight"] = molecular_weight
            inputs["R"] = 8314.462618 / molecular_weight

        cp = first_available(
            "cea_selected_cp",
            "cea_cp_frozen",
            "cea_throat_cp",
            "cea_exit_cp",
        )

        if cp is not None:
            inputs["specific_heat_cp"] = cp
            inputs["gas_specific_heat_cp"] = cp

        prandtl = first_available(
            "cea_selected_prandtl",
            "cea_throat_prandtl",
            "cea_exit_prandtl",
            "gas_prandtl_number",
        )

        if prandtl is not None:
            inputs["gas_prandtl_number"] = prandtl

        viscosity = first_available(
            "cea_selected_viscosity",
            "cea_throat_viscosity",
            "cea_exit_viscosity",
        )

        if viscosity is not None:
            inputs["gas_dynamic_viscosity"] = viscosity

        conductivity = first_available(
            "cea_selected_conductivity",
            "cea_throat_conductivity",
            "cea_exit_conductivity",
        )

        if conductivity is not None:
            inputs["gas_thermal_conductivity"] = conductivity

        return inputs

    def apply_graph_cea_to_inputs(self, inputs):
        """
        Promethean-style graph CEA layer.

        This is the missing piece in Qt LEAF:
        every graph point must run CEA for its own fuel, oxidizer, O/F,
        chamber pressure, and expansion ratio.
        """

        mode = str(inputs.get("calculation_mode") or "CEA").upper()

        if mode != "CEA":
            return inputs

        fuel = canonical_fuel(inputs.get("fuel") or inputs.get("fuel_type"))
        oxidizer = canonical_oxidizer(inputs.get("oxidizer") or inputs.get("oxidizer_type"))

        fuel_temp_k = inputs.get("fuel_temp_k") or inputs.get("fuel_temperature_k")
        oxidizer_temp_k = inputs.get("oxidizer_temp_k") or inputs.get("oxidizer_temperature_k")

        if fuel_temp_k is None:
            fuel_temp_k = get_default_fuel_temperature_k(fuel)

        if oxidizer_temp_k is None:
            oxidizer_temp_k = get_default_oxidizer_temperature_k(oxidizer)

        chamber_pressure = inputs.get("chamber_pressure")
        mixture_ratio = inputs.get("mixture_ratio")
        expansion_ratio = inputs.get("expansion_ratio")

        if expansion_ratio is None and inputs.get("exit_area") is not None and inputs.get("throat_area") is not None:
            throat_area = inputs.get("throat_area")
            if throat_area:
                expansion_ratio = inputs.get("exit_area") / throat_area

        if expansion_ratio is None:
            expansion_ratio = 10.0

        if chamber_pressure is None:
            raise ValueError("CEA graphing requires chamber pressure.")

        if mixture_ratio is None:
            raise ValueError("CEA graphing requires mixture ratio.")

        cea_fuel_name = get_cea_fuel_name(fuel)
        cea_oxidizer_name = get_cea_oxidizer_name(oxidizer)

        cache_key = (
            cea_fuel_name,
            round(float(fuel_temp_k), 4),
            cea_oxidizer_name,
            round(float(oxidizer_temp_k), 4),
            round(float(chamber_pressure), 3),
            round(float(mixture_ratio), 6),
            round(float(expansion_ratio), 6),
        )

        if cache_key in self.graph_cea_cache:
            cea_results = self.graph_cea_cache.pop(cache_key)
            self.graph_cea_cache[cache_key] = cea_results
        else:
            cea_results, raw_output = run_cea_rocket_case(
                fuel_name=cea_fuel_name,
                fuel_temp_k=float(fuel_temp_k),
                oxidizer_name=cea_oxidizer_name,
                oxidizer_temp_k=float(oxidizer_temp_k),
                chamber_pressure_pa=float(chamber_pressure),
                mixture_ratio=float(mixture_ratio),
                expansion_ratio=float(expansion_ratio),
            )

            self.graph_cea_cache[cache_key] = dict(cea_results)

            if len(self.graph_cea_cache) > self.graph_cea_cache_limit:
                oldest_key = next(iter(self.graph_cea_cache))
                self.graph_cea_cache.pop(oldest_key, None)

        inputs["fuel"] = fuel
        inputs["oxidizer"] = oxidizer
        inputs["fuel_type"] = fuel
        inputs["oxidizer_type"] = oxidizer
        inputs["fuel_temp_k"] = float(fuel_temp_k)
        inputs["oxidizer_temp_k"] = float(oxidizer_temp_k)
        inputs["fuel_temperature_k"] = float(fuel_temp_k)
        inputs["oxidizer_temperature_k"] = float(oxidizer_temp_k)

        inputs = self.apply_cea_authority_to_inputs(inputs, cea_results)

        # Force storage/liquid propellant densities after CEA merge.
        # CEA gas densities must not overwrite tank-volume density values.
        inputs["fuel_density"] = get_fuel_density_kg_m3(fuel)
        inputs["oxidizer_density"] = get_oxidizer_density_kg_m3(oxidizer)
        inputs["propellant_density_source"] = "storage_density_kg_m3"

        return inputs

    @staticmethod
    def get_dependency_parents(var_name):
        """
        Return canonical immediate graph parents for var_name.

        DEPENDENCY_GRAPH remains the ordinary relationship owner.

        Graph CEA already recalculates its thermochemical state from mixture
        ratio at each sweep point. This resolver exposes that existing CEA
        authority to dependency traversal so downstream relationships are
        inherited automatically rather than hard-coded onto every output.
        """
        from variable_registry import get_variable

        parents = set(
            DEPENDENCY_GRAPH.get(
                var_name,
                set(),
            )
        )

        definition = get_variable(
            var_name
        )

        section = str(
            getattr(
                definition,
                "section",
                "",
            )
            or ""
        )


        if (
            section == "CEA Chemical Outputs"
            or var_name
            in CEA_AUTHORITATIVE_CORE_OUTPUTS
        ):
            parents.add(
                "mixture_ratio"
            )

        parents.discard(
            var_name
        )

        return parents

    @staticmethod
    def graph_execution_scope(y_var):
        """
        Return the smallest conservative existing solver scope for y_var.

        Variable Registry section ownership and the existing Graph Explorer
        dependency graph remain authoritative. Any unknown or non-core
        dependency falls back to the established engineering graph scope.
        """
        from variable_registry import get_variable

        if not y_var:
            return "graph"

        if y_var in {
            "corrected_thrust",
            "corrected_specific_impulse",
        }:
            return "graph_corrected"

        core_sections = {
            "CEA Chemical Outputs",
            "Chamber Parameters",
            "Flow Properties",
            "Nozzle Geometry",
            "Performance / Thrust",
            "Thermodynamic Properties",
        }

        stack = [y_var]
        seen = set()

        while stack:
            key = stack.pop()

            if key in seen:
                continue

            seen.add(key)

            definition = get_variable(key)

            if definition is None:
                return "graph"

            section = str(
                getattr(
                    definition,
                    "section",
                    "",
                )
                or ""
            )

            if section not in core_sections:
                return "graph"

            stack.extend(
                GraphExplorerEngine.get_dependency_parents(
                    key
                )
            )

        return "graph_core"

    def solve_with_cache(self, inputs, y_var=None):
        prepared = self.prepare_graph_inputs(inputs)
        execution_scope = self.graph_execution_scope(
            y_var
        )

        cache_key = (
            execution_scope,
            self.make_cache_key(prepared),
        )

        if cache_key in self.solver_cache:
            cached = self.solver_cache.pop(cache_key)
            self.solver_cache[cache_key] = cached
            return cached.copy()

        solved, history = calculate_with_full_bridge(prepared, execution_scope=execution_scope)
        solved = self.apply_graph_output_fallbacks(solved)
        solved = self.apply_propellant_volume_overrides(solved)

        compact = self.compact_graph_solution(
            solved
        )

        self.solver_cache[cache_key] = compact

        if len(self.solver_cache) > self.solver_cache_limit:
            oldest_key = next(iter(self.solver_cache))
            self.solver_cache.pop(oldest_key, None)

        return compact.copy()

    def solve_full_state(
        self,
        inputs,
        y_var=None,
    ):
        """
        Run one explicit Graph Explorer design-state solve and retain the full
        canonical result dictionary.

        Ordinary parameter sweeps continue through solve_with_cache() and
        compact_graph_solution().  This operation exists only for a selected
        design that needs nested result-owned data such as a Regen axial
        station profile.
        """
        prepared = self.prepare_graph_inputs(
            inputs
        )

        # Preserve the selected Regen inputs before clearing prior calculated
        # outputs.  This uses the existing recalculation owner rather than
        # creating a second stale-output policy.
        selected_regen_inputs = {
            key:
                prepared.get(
                    key
                )
            for key in self.regen_geometry_sweep_keys()
            if key in prepared
        }

        prepared = (
            self.clear_recalculated_values(
                prepared,
                None,
            )
        )

        prepared.update(
            selected_regen_inputs
        )

        execution_scope = (
            self.graph_execution_scope(
                y_var
            )
        )

        solved, history = (
            calculate_with_full_bridge(
                prepared,
                execution_scope=
                    execution_scope,
            )
        )

        if not isinstance(
            solved,
            dict,
        ):
            return {}

        solved = (
            self.apply_graph_output_fallbacks(
                solved
            )
        )

        solved = (
            self.apply_propellant_volume_overrides(
                solved
            )
        )

        # Deliberately NOT placed in solver_cache.  Full nested station
        # profiles remain a one-selected-design result rather than being
        # accumulated once per ordinary graph sweep point.
        return dict(
            solved
        )

    def apply_graph_output_fallbacks(self, solved):
        if solved.get("corrected_thrust") is None and solved.get("thrust") is not None:
            solved["corrected_thrust"] = (
                solved["thrust"]
                * (solved.get("combustion_efficiency") or 1.0)
                * (solved.get("mixture_quality_factor") or 1.0)
                * (solved.get("soot_risk_factor") or 1.0)
                * (solved.get("thermal_risk_factor") or 1.0)
            )

        if solved.get("corrected_specific_impulse") is None and solved.get("specific_impulse") is not None:
            solved["corrected_specific_impulse"] = solved["specific_impulse"] * (
                solved.get("combustion_efficiency") or 1.0
            )

        return solved

    def clear_cache(self):
        self.solver_cache.clear()
        self.graph_cea_cache.clear()

    def get_deep_ancestors(self, var_name):
        ancestors = set()
        stack = list(self.get_dependency_parents(var_name))

        while stack:
            parent = stack.pop()

            if parent in ancestors:
                continue

            ancestors.add(parent)

            for grandparent in self.get_dependency_parents(parent):
                if grandparent not in ancestors:
                    stack.append(grandparent)

        return ancestors

    def get_deep_descendants(self, var_name):
        from variable_registry import get_graphable_keys

        descendants = set()

        candidate_children = set(
            DEPENDENCY_GRAPH
        )

        candidate_children.update(
            get_graphable_keys()
        )

        changed = True

        while changed:
            changed = False

            for child in candidate_children:
                if (
                    child == var_name
                    or child in descendants
                ):
                    continue

                parents = self.get_dependency_parents(
                    child
                )

                if (
                    var_name in parents
                    or any(
                        parent in descendants
                        for parent in parents
                    )
                ):
                    descendants.add(
                        child
                    )
                    changed = True

        return descendants

    def get_y_options_for_x(
        self,
        x_var,
        candidate_y_vars,
        inputs=None,
    ):
        if not self.is_sweepable_x_variable(
            x_var,
            inputs,
        ):
            return []

        descendants = (
            self.get_deep_descendants(
                x_var
            )
        )

        return [
            y_var
            for y_var in candidate_y_vars
            if (
                y_var in descendants
                and y_var != x_var
            )
        ]

    def get_x_options_for_y(
        self,
        y_var,
        candidate_x_vars,
        inputs=None,
    ):
        ancestors = self.get_deep_ancestors(
            y_var
        )

        return [
            x_var
            for x_var in candidate_x_vars
            if (
                x_var in ancestors
                and x_var != y_var
                and self.is_sweepable_x_variable(
                    x_var,
                    inputs,
                )
            )
        ]

    @staticmethod
    def regen_geometry_sweep_keys():
        """
        Independent Regen geometry parameters that Graph Explorer may vary
        around a selected real Regen design.

        This is an exploration contract only. It does not define engineering
        feasibility, qualification, manufacturing limits, or solver thresholds.
        """
        return {
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "number_of_coolant_channels",
            "hot_gas_wall_thickness",
            "outer_wall_thickness",
            "outer_jacket_thickness",
            "coolant_flow_fraction",
        }

    def regen_geometry_sweep_values(
        self,
        var_name,
        base_inputs,
        point_count,
    ):
        """
        Build an exploratory range around the selected Regen baseline.

        Solver-owned PASS/FAIL/WARN/UNPROVEN state remains authoritative.
        """
        if (
            var_name
            not in
            self.regen_geometry_sweep_keys()
        ):
            return None

        if not isinstance(
            base_inputs,
            dict,
        ):
            return None

        try:
            baseline = float(
                base_inputs.get(
                    var_name
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if (
            not np.isfinite(
                baseline
            )
            or
            baseline <= 0.0
        ):
            return None

        count = max(
            2,
            int(
                point_count
            ),
        )

        if (
            var_name
            ==
            "number_of_coolant_channels"
        ):
            start = max(
                1,
                int(
                    round(
                        baseline * 0.5
                    )
                ),
            )

            end = max(
                start + 1,
                int(
                    round(
                        baseline * 1.5
                    )
                ),
            )

            return [
                int(
                    round(
                        value
                    )
                )
                for value in np.linspace(
                    start,
                    end,
                    count,
                )
            ]

        if (
            var_name
            ==
            "coolant_flow_fraction"
        ):
            start = max(
                0.01,
                baseline * 0.5,
            )

            end = min(
                1.0,
                baseline * 1.5,
            )

            if end <= start:
                return None

            return np.linspace(
                start,
                end,
                count,
            )

        start = max(
            baseline * 0.5,
            1.0e-12,
        )

        end = baseline * 1.5

        if end <= start:
            return None

        return np.linspace(
            start,
            end,
            count,
        )

    def is_sweepable_x_variable(
        self,
        var_name,
        inputs=None,
    ):
        if var_name is None:
            return False

        if (
            var_name
            in
            self.regen_geometry_sweep_keys()
        ):
            if not isinstance(
                inputs,
                dict,
            ):
                return False

            try:
                current = float(
                    inputs.get(
                        var_name
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                return False

            return bool(
                np.isfinite(
                    current
                )
                and
                current > 0.0
            )

        if var_name not in GRAPH_INPUT_DEFAULTS:
            return False

        if var_name.endswith("_status"):
            return False

        if var_name.endswith("_valid"):
            return False

        if var_name.endswith("_pass"):
            return False

        if var_name in {
            "regen_axial_profile",
            "selected_coolant_name",
            "regen_geometry_status",
            "regen_thermal_status",
            "regen_coolant_status",
            "regen_material_status",
            "regen_overall_status",
        }:
            return False

        context = dict(
            GRAPH_INPUT_DEFAULTS
        )

        if isinstance(
            inputs,
            dict,
        ):
            context.update(
                inputs
            )

        calculation_mode = str(
            context.get(
                "calculation_mode"
            )
            or "CEA"
        ).upper()

        if calculation_mode == "CEA":
            from variable_registry import get_variable

            definition = get_variable(
                var_name
            )

            section = str(
                getattr(
                    definition,
                    "section",
                    "",
                )
                or ""
            )

            if (
                section
                == "CEA Chemical Outputs"
                or var_name
                in CEA_AUTHORITATIVE_CORE_OUTPUTS
            ):
                return False

        start, end = (
            self.default_start_end_for_var(
                var_name,
                context,
            )
        )

        if (
            start is None
            or end is None
        ):
            return False

        if start == end:
            return False

        return True

    def get_automatic_x_options(self, candidate_x_vars):
        return [
            var_name
            for var_name in candidate_x_vars
            if self.is_sweepable_x_variable(var_name)
        ]

    def get_automatic_y_options(self, candidate_y_vars):
        return [
            var_name
            for var_name in candidate_y_vars
            if var_name not in {
                "regen_axial_profile",
            }
               and not var_name.endswith("_status")
        ]

    def default_start_end_for_var(self, var_name, base_inputs):
        prepared = self.prepare_graph_inputs(base_inputs)
        current = prepared.get(var_name)

        if var_name == "mixture_ratio":
            return 1.2, 3.5

        if var_name == "selected_length":
            nozzle_length = prepared.get("nozzle_length") or 0.08
            return 0.0, nozzle_length

        if var_name == "chamber_pressure":
            return 1.0e6, 15.0e6

        if var_name == "mass_flow_rate":
            return 0.1, 10.0

        if var_name == "selected_station_length":
            return 0.00025, 0.01

        if var_name == "coolant_channel_width":
            return 0.0005, 0.004

        if var_name == "coolant_channel_height":
            return 0.0005, 0.006

        if var_name == "coolant_flow_fraction":
            return 0.1, 1.0

        if var_name == "number_of_coolant_channels":
            return 20.0, 200.0

        if isinstance(current, (int, float)) and current != 0:
            return current * 0.5, current * 1.5

        return 1.0, 10.0

    def get_sweep_values(self, var_name, base_inputs, point_count):
        if (
            var_name
            in
            self.regen_geometry_sweep_keys()
        ):
            return (
                self.regen_geometry_sweep_values(
                    var_name,
                    base_inputs,
                    point_count,
                )
            )

        prepared = self.prepare_graph_inputs(base_inputs)

        if var_name == "mixture_ratio":
            fuel = prepared.get("fuel") or prepared.get("fuel_type")
            oxidizer = prepared.get("oxidizer") or prepared.get("oxidizer_type")
            start, end = get_of_ratio_range_for_pair(fuel, oxidizer)
        else:
            start, end = self.default_start_end_for_var(var_name, base_inputs)

        if var_name == "number_of_coolant_channels":
            values = np.linspace(start, end, point_count)
            return [round(float(v)) for v in values]

        return np.linspace(start, end, point_count)

    def clear_cea_dependent_values(self, inputs):
        """
        Clears gas/CEA/performance values that must be recalculated when
        fuel, oxidizer, mixture ratio, or propellant temperature changes.
        """

        point_inputs = dict(inputs)

        keys_to_clear = [
            "Gamma",
            "R",
            "specific_heat_cp",
            "specific_heat_cv",

            "cea_molecular_weight",
            "cea_density",
            "cea_cp_frozen",
            "cea_cv_equilibrium",
            "cea_cv_frozen",
            "cea_selected_cp",
            "cea_selected_prandtl",
            "cea_selected_gamma",
            "cea_selected_molecular_weight",
            "cea_selected_viscosity",
            "cea_selected_conductivity",

            "cea_chamber_temperature",
            "cea_chamber_gamma",
            "cea_chamber_molecular_weight",
            "cea_chamber_density",
            "cea_chamber_sonic_velocity",

            "cea_throat_cp",
            "cea_throat_viscosity",
            "cea_throat_conductivity",
            "cea_throat_prandtl",
            "cea_throat_gamma",
            "cea_throat_molecular_weight",
            "cea_throat_temperature",
            "cea_throat_density",
            "cea_throat_sonic_velocity",

            "cea_exit_cp",
            "cea_exit_viscosity",
            "cea_exit_conductivity",
            "cea_exit_prandtl",
            "cea_exit_gamma",
            "cea_exit_molecular_weight",
            "cea_exit_temperature",
            "cea_exit_density",
            "cea_exit_sonic_velocity",

            "thermo_r_error",
            "thermo_r_error_percent",
            "thermo_model_note",
            "cea_authoritative_used",

            "gas_dynamic_viscosity",
            "gas_specific_heat_cp",
            "gas_prandtl_number",
            "gas_thermal_conductivity",

            "chamber_temperature",
            "characteristic_velocity",
            "exhaust_velocity",
            "exit_pressure",
            "momentum_thrust",
            "pressure_thrust",
            "thrust",
            "specific_impulse",
            "vacuum_specific_impulse",
            "sea_level_specific_impulse",
            "effective_exhaust_velocity",
            "thrust_coefficient",

            "combustion_efficiency",
            "mixture_quality_factor",
            "soot_risk_factor",
            "thermal_risk_factor",

            "ideal_engine_thrust",
            "ideal_engine_specific_impulse",
            "ideal_volumetric_thrust",
            "corrected_thrust",
            "corrected_specific_impulse",
            "fuel_density",
            "oxidizer_density",
            "total_propellant_volume_flow_rate",
            "volumetric_corrected_thrust",

            "adiabatic_wall_temperature",
            "selected_gas_side_recovery_temperature",
            "compressibility_correlation_factor",
            "static_temperature",
            "static_pressure",
            "static_density",

            "bartz_sigma",
            "bartz_gas_side_heat_transfer_coefficient",
            "hot_gas_heat_transfer_coefficient",
            "hot_gas_heat_flux",
            "regen_heat_flux",
            "hot_gas_side_wall_temperature",
            "material_temperature_margin",
        ]

        protected_inputs = {
            "fuel",
            "oxidizer",
            "fuel_density",
            "oxidizer_density",
            "fuel_temp_k",
            "oxidizer_temp_k",
            "mixture_ratio",
            "mass_flow_rate",
            "chamber_pressure",
            "calculation_mode",
            "cea_authoritative_mode",
        }

        for key in keys_to_clear:
            if key in protected_inputs:
                continue

            point_inputs[key] = None

        return point_inputs

    def solve_graph_point(self, base_inputs, x_var, x_value, y_var=None):
        inputs = self.prepare_graph_inputs(base_inputs)
        inputs[x_var] = float(x_value)

        if x_var in {
            "mixture_ratio",
            "fuel",
            "oxidizer",
            "fuel_temp_k",
            "oxidizer_temp_k",
        }:
            inputs = self.clear_cea_dependent_values(inputs)

        inputs = self.clear_recalculated_values(inputs, x_var)

        inputs = self.apply_graph_cea_to_inputs(inputs)

        return self.solve_with_cache(inputs, y_var=y_var)

    def get_graph_y_value(self, solved, y_var, graph_inputs=None):
        if y_var not in {
            "total_propellant_volume_flow_rate",
            "volumetric_corrected_thrust",
        }:
            return solved.get(y_var)

        graph_inputs = graph_inputs or {}

        mass_flow_rate = graph_inputs.get("mass_flow_rate")
        mixture_ratio = graph_inputs.get("mixture_ratio")
        fuel = graph_inputs.get("fuel") or graph_inputs.get("fuel_type")
        oxidizer = graph_inputs.get("oxidizer") or graph_inputs.get("oxidizer_type")

        if mass_flow_rate is None:
            mass_flow_rate = solved.get("mass_flow_rate")

        if mixture_ratio is None:
            mixture_ratio = solved.get("mixture_ratio")

        if fuel is None:
            fuel = solved.get("fuel") or solved.get("fuel_type")

        if oxidizer is None:
            oxidizer = solved.get("oxidizer") or solved.get("oxidizer_type")

        if mass_flow_rate is None or mixture_ratio is None:
            return solved.get(y_var)

        fuel = canonical_fuel(fuel)
        oxidizer = canonical_oxidizer(oxidizer)

        fuel_density = get_fuel_density_kg_m3(fuel)
        oxidizer_density = get_oxidizer_density_kg_m3(oxidizer)

        fuel_mass_flow_rate = float(mass_flow_rate) / (1.0 + float(mixture_ratio))
        oxidizer_mass_flow_rate = float(mass_flow_rate) - fuel_mass_flow_rate

        total_volume_flow = (
                fuel_mass_flow_rate / fuel_density
                + oxidizer_mass_flow_rate / oxidizer_density
        )

        if y_var == "total_propellant_volume_flow_rate":
            return total_volume_flow

        corrected_thrust = solved.get("corrected_thrust")

        if corrected_thrust is None or total_volume_flow <= 0:
            return solved.get(y_var)

        return corrected_thrust / total_volume_flow

    def generate_solution_series(
        self,
        base_inputs,
        x_var,
        point_count,
        y_var=None,
    ):
        """
        Run the existing controlled Graph Explorer sweep and retain each
        compact solved point.

        This is not another solver mechanism. solve_graph_point() remains the
        canonical per-point owner.
        """
        self.last_errors = []

        x_values = self.get_sweep_values(
            x_var,
            base_inputs,
            point_count,
        )

        records = []

        for x_value in x_values:

            try:
                solved = self.solve_graph_point(
                    base_inputs,
                    x_var,
                    x_value,
                    y_var=y_var,
                )

                if not isinstance(
                    solved,
                    dict,
                ):
                    self.last_errors.append(
                        f"{x_var}={x_value}: solver returned non-dict result"
                    )
                    continue

                records.append(
                    {
                        "x":
                            float(
                                x_value
                            ),

                        "solved":
                            dict(
                                solved
                            ),
                    }
                )

            except Exception as error:
                self.last_errors.append(
                    f"{x_var}={x_value}: "
                    f"{type(error).__name__}: {error}"
                )

        return records


    def prepare_propellant_comparison_inputs(
        self,
        base_inputs,
        fuel,
        oxidizer,
    ):
        """
        Shared chemistry preparation for ordinary and controlled graph sweeps.
        """
        comparison_inputs = self.prepare_graph_inputs(
            base_inputs
        )

        fuel = canonical_fuel(
            fuel
        )

        oxidizer = canonical_oxidizer(
            oxidizer
        )

        comparison_inputs[
            "fuel"
        ] = fuel

        comparison_inputs[
            "oxidizer"
        ] = oxidizer

        comparison_inputs[
            "fuel_type"
        ] = fuel

        comparison_inputs[
            "oxidizer_type"
        ] = oxidizer

        comparison_inputs[
            "fuel_temp_k"
        ] = get_default_fuel_temperature_k(
            fuel
        )

        comparison_inputs[
            "oxidizer_temp_k"
        ] = get_default_oxidizer_temperature_k(
            oxidizer
        )

        comparison_inputs[
            "fuel_temperature_k"
        ] = comparison_inputs[
            "fuel_temp_k"
        ]

        comparison_inputs[
            "oxidizer_temperature_k"
        ] = comparison_inputs[
            "oxidizer_temp_k"
        ]

        comparison_inputs[
            "calculation_mode"
        ] = "CEA"

        comparison_inputs[
            "cea_authoritative_mode"
        ] = True

        return self.clear_cea_dependent_values(
            comparison_inputs
        )


    def generate_propellant_solution_series(
        self,
        base_inputs,
        x_var,
        point_count,
        fuel,
        oxidizer,
        y_var=None,
    ):
        comparison_inputs = (
            self.prepare_propellant_comparison_inputs(
                base_inputs,
                fuel,
                oxidizer,
            )
        )

        return self.generate_solution_series(
            base_inputs=comparison_inputs,
            x_var=x_var,
            point_count=point_count,
            y_var=y_var,
        )

    def generate_series(self, base_inputs, x_var, y_var, point_count):
        self.last_errors = []

        x_values = self.get_sweep_values(x_var, base_inputs, point_count)

        x_points = []
        y_points = []

        for x in x_values:
            try:
                point_inputs = self.prepare_graph_inputs(base_inputs)
                point_inputs[x_var] = float(x)

                solved = self.solve_graph_point(base_inputs, x_var, x, y_var=y_var)
                y = self.get_graph_y_value(solved, y_var, point_inputs)

                # Force the corrected graph value back into the solved dictionary.
                # This prevents graph/window/export code from accidentally using the old solver value.
                if y is not None:
                    solved[y_var] = y

                if y is None:
                    self.last_errors.append(
                        f"{x_var}={x}: {y_var} returned None"
                    )
                    continue

                x_points.append(float(x))
                y_points.append(float(y))

            except Exception as error:
                self.last_errors.append(
                    f"{x_var}={x}: {type(error).__name__}: {error}"
                )
                continue

        return x_points, y_points

    def generate_propellant_series(
        self,
        base_inputs,
        x_var,
        y_var,
        point_count,
        fuel,
        oxidizer,
    ):
        comparison_inputs = (
            self.prepare_propellant_comparison_inputs(
                base_inputs,
                fuel,
                oxidizer,
            )
        )

        return self.generate_series(
            base_inputs=comparison_inputs,
            x_var=x_var,
            y_var=y_var,
            point_count=point_count,
        )

    def apply_propellant_volume_overrides(self, solved):
        mass_flow_rate = solved.get("mass_flow_rate")
        mixture_ratio = solved.get("mixture_ratio")
        fuel_density = solved.get("fuel_density")
        oxidizer_density = solved.get("oxidizer_density")

        if (
                mass_flow_rate is None
                or mixture_ratio is None
                or fuel_density is None
                or oxidizer_density is None
                or fuel_density <= 0
                or oxidizer_density <= 0
        ):
            return solved

        fuel_mass_flow_rate = mass_flow_rate / (1.0 + mixture_ratio)
        oxidizer_mass_flow_rate = mass_flow_rate - fuel_mass_flow_rate

        total_volume_flow = (
                fuel_mass_flow_rate / fuel_density
                + oxidizer_mass_flow_rate / oxidizer_density
        )

        solved["fuel_mass_flow_rate"] = fuel_mass_flow_rate
        solved["oxidizer_mass_flow_rate"] = oxidizer_mass_flow_rate
        solved["total_propellant_volume_flow_rate"] = total_volume_flow
        solved["volume_debug_mass_flow_rate"] = mass_flow_rate
        solved["volume_debug_mixture_ratio"] = mixture_ratio
        solved["volume_debug_fuel_density"] = fuel_density
        solved["volume_debug_oxidizer_density"] = oxidizer_density
        solved["volume_debug_fuel_mass_flow_rate"] = fuel_mass_flow_rate
        solved["volume_debug_oxidizer_mass_flow_rate"] = oxidizer_mass_flow_rate

        corrected_thrust = solved.get("corrected_thrust")

        if corrected_thrust is not None and total_volume_flow > 0:
            solved["volumetric_corrected_thrust"] = corrected_thrust / total_volume_flow

        return solved

    def clear_recalculated_values(self, inputs, x_var):
        """
        Promethean-style graph solve preparation.

        Clears outputs/dependent values before each graph point so the solver
        is forced to recalculate them from the swept X variable.
        """

        point_inputs = dict(inputs)

        keys_to_clear = [
            "fuel_mass_flow_rate",
            "oxidizer_mass_flow_rate",

            "selected_expansion_ratio",
            "cross_sectional_area",

            "throat_radius",
            "exit_radius",
            "radius_2",
            "radius_3",

            "chamber_volume",
            "chamber_contraction_ratio",
            "chamber_converging_half_angle_deg",
            "chamber_cross_sectional_area",
            "chamber_radius",
            "chamber_diameter",
            "chamber_converging_length",
            "chamber_converging_volume",
            "chamber_cylindrical_volume",
            "chamber_cylindrical_length",
            "chamber_total_length",
            "chamber_profile",
            "chamber_geometry_model",
            "chamber_geometry_status",
            "chamber_geometry_reason",

            "cea_chamber_temperature",

            "static_temperature",
            "static_pressure",
            "static_density",

            "estimated_residence_time",
            "characteristic_velocity",
            "exhaust_velocity",

            "mach_number",
            "selected_mach_number",

            "adiabatic_wall_temperature",
            "selected_gas_side_recovery_temperature",
            "compressibility_correlation_factor",

            "exit_pressure",
            "momentum_thrust",
            "pressure_thrust",
            "thrust",

            "specific_impulse",
            "vacuum_specific_impulse",
            "sea_level_specific_impulse",
            "effective_exhaust_velocity",
            "thrust_coefficient",

            "ideal_engine_thrust",
            "ideal_engine_specific_impulse",
            "ideal_volumetric_thrust",

            "combustion_efficiency",
            "mixture_quality_factor",
            "soot_risk_factor",
            "thermal_risk_factor",

            "corrected_thrust",
            "corrected_specific_impulse",

            "fuel_density",
            "oxidizer_density",
            "total_propellant_volume_flow_rate",
            "volumetric_corrected_thrust",

            "hot_gas_heat_flux",
            "pressure_required_wall_thickness",
            "conduction_required_wall_thickness",
            "hot_gas_wall_thickness",

            "coolant_velocity",
            "coolant_reynolds_number",
            "coolant_prandtl_number",
            "coolant_nusselt_number",
            "coolant_heat_transfer_coefficient",
            "coolant_friction_factor",
            "coolant_pressure_drop",

            "regen_total_thermal_resistance",
            "regen_heat_flux",
            "hot_gas_side_wall_temperature",
            "coolant_side_wall_temperature_calculated",
            "coolant_temperature_rise",
            "coolant_outlet_temperature",
            "material_temperature_margin",

            # Controlled Regen sweep outputs. These are solved values and must
            # never seed the next X point.
            "regen_axial_min_reynolds_number",
            "regen_axial_max_coolant_velocity",
            "regen_axial_total_pressure_drop",
            "regen_axial_max_hot_wall_temperature",
            "regen_axial_material_temperature_margin",
            "regen_axial_worst_material_margin",

            "regen_geometry_status",
            "regen_coolant_status",
            "regen_thermal_status",
            "regen_material_status",
            "regen_overall_status",
            "regen_feasibility_status",
            "regen_feasibility_pass",

            "regen_derived_pressure_drop_limit",
            "regen_derived_maximum_coolant_velocity",
            "regen_derived_target_reynolds_number",
        ]

        if x_var == "expansion_ratio":
            keys_to_clear.extend(["exit_area", "exit_radius"])

        elif x_var == "exit_area":
            keys_to_clear.extend(["expansion_ratio", "exit_radius"])

        elif x_var == "exit_radius":
            keys_to_clear.extend(["expansion_ratio", "exit_area"])

        elif x_var == "throat_area":
            keys_to_clear.extend(["throat_radius"])

        elif x_var == "throat_radius":
            keys_to_clear.extend(["throat_area"])

        if x_var in {
            "mixture_ratio",
            "fuel",
            "oxidizer",
            "fuel_temp_k",
            "oxidizer_temp_k",
        }:
            keys_to_clear.extend([
                "chamber_temperature",
                "characteristic_velocity",
                "Gamma",
                "R",
                "specific_heat_cp",
                "specific_heat_cv",
            ])

        protected_inputs = {
            "Gamma",
            "R",
            "specific_heat_cp",
            "specific_heat_cv",
            "chamber_temperature",
            "characteristic_velocity",
            "fuel",
            "oxidizer",
            "fuel_temp_k",
            "oxidizer_temp_k",
            "fuel_density",
            "oxidizer_density",
            "mass_flow_rate",
            "mixture_ratio",
            "chamber_pressure",
            "chamber_contraction_ratio",
            "chamber_converging_half_angle_deg",
            "characteristic_length",
            "selected_length",
            "selected_station_length",
            "ambient_pressure",
            "selected_coolant_name",
            "coolant_flow_fraction",
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "outer_jacket_thickness",
            "coating_thickness",
            "number_of_coolant_channels",
            "minimum_wall_thickness",
            "corrosion_allowance",
            "wall_safety_factor",
            "wall_joint_efficiency",
        }

        for key in keys_to_clear:
            if key == x_var:
                continue

            if key in protected_inputs:
                continue

            point_inputs[key] = None

        return point_inputs
