from engine_solver_extracted_helpers import calculate_coolant_flow_fraction_default
from engine_solver_extracted_helpers import calculate_selected_station_length_default
from leaf_qt.solver_status_access import solver_fail, solver_highest_severity, solver_pass
import math
from scipy.optimize import brentq
from material_property_interpolation_owner import attach_material_property_interpolation_owner
from material_property_consumption_audit_owner import attach_material_property_consumption_audit_owner
try:
    from reference_engine_database import (
        get_reference_engine,
        evaluate_reference_source_ledger_coverage,
        evaluate_reference_data_quality,
    )
except ImportError:
    get_reference_engine = None
    evaluate_reference_source_ledger_coverage = None
    evaluate_reference_data_quality = None
try:
    from fluid_property_database import (
        get_fluid_properties,
        get_fluid_properties_at_temperature,
        get_fluid_density,
    )
except ImportError:
    get_fluid_properties = None
    get_fluid_properties_at_temperature = None
    get_fluid_density = None
try:
    from coolant_database import (
        get_coolant_properties,
        get_coolant_properties_at_temperature,
    )
except ImportError:
    get_coolant_properties = None
    get_coolant_properties_at_temperature = None

try:
    from material_database import (
        get_material_properties,
        get_material_names,
        get_coating_material_properties,
        get_bond_coat_properties,
        classify_source_validation_mode,
        PLACEHOLDER_MODE,
        PARTIAL_SOURCE_MODE,
        SOURCED_VALIDATION_MODE,
        COATING_MATERIAL_DATABASE,
        BOND_COAT_DATABASE,
        get_coating_material_names,
        get_bond_coat_names,
        get_coating_database_summary,
    )
except ImportError:
    get_material_properties = None
    get_material_names = None
    get_coating_material_properties = None
    get_bond_coat_properties = None
    classify_source_validation_mode = None
    get_coating_material_names = None
    get_bond_coat_names = None
    get_coating_database_summary = None
    PLACEHOLDER_MODE = "PLACEHOLDER_MODE"
    PARTIAL_SOURCE_MODE = "PARTIAL_SOURCE_MODE"
    SOURCED_VALIDATION_MODE = "SOURCED_VALIDATION_MODE"
    COATING_MATERIAL_DATABASE = []
    BOND_COAT_DATABASE = []

try:
    from leaf_qt.materials.owner.material_thermal_conductivity_integration_owner import (
        attach_material_thermal_conductivity_integration_owner,
    )
except Exception:
    try:
        from material_thermal_conductivity_integration_owner import (
            attach_material_thermal_conductivity_integration_owner,
        )
    except Exception:
        attach_material_thermal_conductivity_integration_owner = None

try:
    from leaf_qt.material_specific_heat_integration_owner import (
        attach_material_specific_heat_integration_owner,
    )
except Exception:
    try:
        from material_specific_heat_integration_owner import (
            attach_material_specific_heat_integration_owner,
        )
    except Exception:
        attach_material_specific_heat_integration_owner = None

try:
    from leaf_qt.material_density_integration_owner import (
        attach_material_density_integration_owner,
    )
except Exception:
    try:
        from material_density_integration_owner import (
            attach_material_density_integration_owner,
        )
    except Exception:
        attach_material_density_integration_owner = None

try:
    from leaf_qt.material_temperature_limit_integration_owner import (
        attach_material_temperature_limit_integration_owner,
    )
except Exception:
    try:
        from material_temperature_limit_integration_owner import (
            attach_material_temperature_limit_integration_owner,
        )
    except Exception:
        attach_material_temperature_limit_integration_owner = None

try:
    from leaf_qt.material_strength_limit_integration_owner import (
        attach_material_strength_limit_integration_owner,
    )
except Exception:
    try:
        from material_strength_limit_integration_owner import (
            attach_material_strength_limit_integration_owner,
        )
    except Exception:
        attach_material_strength_limit_integration_owner = None

try:
    from leaf_qt.materials.owner.coating_thermal_conductivity_integration_owner import (
        attach_coating_thermal_conductivity_integration_owner,
    )
except Exception:
    try:
        from coating_thermal_conductivity_integration_owner import (
            attach_coating_thermal_conductivity_integration_owner,
        )
    except Exception:
        attach_coating_thermal_conductivity_integration_owner = None

try:
    from leaf_qt.coating_thickness_integration_owner import (
        attach_coating_thickness_integration_owner,
    )
except Exception:
    try:
        from coating_thickness_integration_owner import (
            attach_coating_thickness_integration_owner,
        )
    except Exception:
        attach_coating_thickness_integration_owner = None

try:
    from leaf_qt.coating_thermal_resistance_integration_owner import (
        attach_coating_thermal_resistance_integration_owner,
    )
except Exception:
    try:
        from coating_thermal_resistance_integration_owner import (
            attach_coating_thermal_resistance_integration_owner,
        )
    except Exception:
        attach_coating_thermal_resistance_integration_owner = None

try:
    from leaf_qt.coating_temperature_limit_integration_owner import (
        attach_coating_temperature_limit_integration_owner,
    )
except Exception:
    try:
        from coating_temperature_limit_integration_owner import (
            attach_coating_temperature_limit_integration_owner,
        )
    except Exception:
        attach_coating_temperature_limit_integration_owner = None

try:
    from leaf_qt.bond_coat_integration_owner import (
        attach_bond_coat_integration_owner,
    )
except Exception:
    try:
        from bond_coat_integration_owner import (
            attach_bond_coat_integration_owner,
        )
    except Exception:
        attach_bond_coat_integration_owner = None

try:
    from leaf_qt.regen_candidate_generator import attach_regen_candidate_generator
except Exception:
    try:
        from regen_candidate_generator import attach_regen_candidate_generator
    except Exception:
        attach_regen_candidate_generator = None

try:
    from leaf_qt.regen_candidate_validator import attach_regen_candidate_validator
except Exception:
    try:
        from regen_candidate_validator import attach_regen_candidate_validator
    except Exception:
        attach_regen_candidate_validator = None

try:
    from leaf_qt.regen_candidate_ranker import attach_regen_candidate_ranker
except Exception:
    try:
        from regen_candidate_ranker import attach_regen_candidate_ranker
    except Exception:
        attach_regen_candidate_ranker = None

try:
    from leaf_qt.regen_candidate_selector import attach_regen_candidate_selector
except Exception:
    try:
        from regen_candidate_selector import attach_regen_candidate_selector
    except Exception:
        attach_regen_candidate_selector = None

try:
    from leaf_qt.regen_candidate_recommendation_owner import (
        attach_regen_candidate_recommendation_owner,
    )
except Exception:
    try:
        from regen_candidate_recommendation_owner import (
            attach_regen_candidate_recommendation_owner,
        )
    except Exception:
        attach_regen_candidate_recommendation_owner = None

try:
    from leaf_qt.regen_candidate_application_owner import (
        attach_regen_candidate_application_owner,
    )
except Exception:
    try:
        from regen_candidate_application_owner import (
            attach_regen_candidate_application_owner,
        )
    except Exception:
        attach_regen_candidate_application_owner = None

try:
    from leaf_qt.regen_candidate_resolve_owner import (
        attach_regen_candidate_resolve_owner,
    )
except Exception:
    try:
        from regen_candidate_resolve_owner import (
            attach_regen_candidate_resolve_owner,
        )
    except Exception:
        attach_regen_candidate_resolve_owner = None

try:
    from leaf_qt.regen_candidate_resolve_execution_owner import (
        attach_regen_candidate_resolve_execution_owner,
    )
except Exception:
    try:
        from regen_candidate_resolve_execution_owner import (
            attach_regen_candidate_resolve_execution_owner,
        )
    except Exception:
        attach_regen_candidate_resolve_execution_owner = None

try:
    from leaf_qt.regen_candidate_post_resolve_validation_owner import (
        attach_regen_candidate_post_resolve_validation_owner,
    )
except Exception:
    try:
        from regen_candidate_post_resolve_validation_owner import (
            attach_regen_candidate_post_resolve_validation_owner,
        )
    except Exception:
        attach_regen_candidate_post_resolve_validation_owner = None

try:
    from leaf_qt.regen_candidate_decision_gate_owner import (
        attach_regen_candidate_decision_gate_owner,
    )
except Exception:
    try:
        from regen_candidate_decision_gate_owner import (
            attach_regen_candidate_decision_gate_owner,
        )
    except Exception:
        attach_regen_candidate_decision_gate_owner = None

try:
    from leaf_qt.optimisation.owner.regen_candidate_ranking_owner import (
        attach_regen_candidate_ranking_owner,
    )
except Exception:
    try:
        from regen_candidate_ranking_owner import (
            attach_regen_candidate_ranking_owner,
        )
    except Exception:
        attach_regen_candidate_ranking_owner = None

try:
    from leaf_qt.regen_autonomous_geometry_commit_controller import (
        attach_regen_autonomous_geometry_commit_controller,
    )
except Exception:
    try:
        from regen_autonomous_geometry_commit_controller import (
            attach_regen_autonomous_geometry_commit_controller,
        )
    except Exception:
        attach_regen_autonomous_geometry_commit_controller = None

try:
    from leaf_qt.regen_autonomous_geometry_commit_history_owner import (
        attach_regen_autonomous_geometry_commit_history_owner,
    )
except Exception:
    try:
        from regen_autonomous_geometry_commit_history_owner import (
            attach_regen_autonomous_geometry_commit_history_owner,
        )
    except Exception:
        attach_regen_autonomous_geometry_commit_history_owner = None

try:
    from leaf_qt.regen_autonomous_geometry_commit_report_owner import (
        attach_regen_autonomous_geometry_commit_report_owner,
    )
except Exception:
    try:
        from regen_autonomous_geometry_commit_report_owner import (
            attach_regen_autonomous_geometry_commit_report_owner,
        )
    except Exception:
        attach_regen_autonomous_geometry_commit_report_owner = None

try:
    from leaf_qt.regen_autonomous_geometry_commit_master_gate import (
        attach_regen_autonomous_geometry_commit_master_gate,
    )
except Exception:
    try:
        from regen_autonomous_geometry_commit_master_gate import (
            attach_regen_autonomous_geometry_commit_master_gate,
        )
    except Exception:
        attach_regen_autonomous_geometry_commit_master_gate = None

try:
    from leaf_qt.regen_automatic_geometry_objective_selector import (
        attach_regen_automatic_geometry_objective_selector,
    )
except Exception:
    try:
        from regen_automatic_geometry_objective_selector import (
            attach_regen_automatic_geometry_objective_selector,
        )
    except Exception:
        attach_regen_automatic_geometry_objective_selector = None

try:
    from leaf_qt.regen_candidate_population_generation_owner import (
        attach_regen_candidate_population_generation_owner,
    )
except Exception:
    try:
        from regen_candidate_population_generation_owner import (
            attach_regen_candidate_population_generation_owner,
        )
    except Exception:
        attach_regen_candidate_population_generation_owner = None


try:
    from leaf_qt.regen_candidate_population_report_owner import (
        attach_regen_candidate_population_report_owner,
    )
except Exception:
    try:
        from regen_candidate_population_report_owner import (
            attach_regen_candidate_population_report_owner,
        )
    except Exception:
        attach_regen_candidate_population_report_owner = None


try:
    from leaf_qt.regen_candidate_population_registration_owner import (
        attach_regen_candidate_population_registration_owner,
    )
except Exception:
    try:
        from regen_candidate_population_registration_owner import (
            attach_regen_candidate_population_registration_owner,
        )
    except Exception:
        attach_regen_candidate_population_registration_owner = None


try:
    from leaf_qt.regen_candidate_population_completion_audit import (
        attach_regen_candidate_population_completion_audit,
    )
except Exception:
    try:
        from regen_candidate_population_completion_audit import (
            attach_regen_candidate_population_completion_audit,
        )
    except Exception:
        attach_regen_candidate_population_completion_audit = None


try:
    from leaf_qt.regen_candidate_population_master_gate import (
        attach_regen_candidate_population_master_gate,
    )
except Exception:
    try:
        from regen_candidate_population_master_gate import (
            attach_regen_candidate_population_master_gate,
        )
    except Exception:
        attach_regen_candidate_population_master_gate = None


try:
    from leaf_qt.optimisation.validation.regen_candidate_ranking_input_audit import (
        attach_regen_candidate_ranking_input_audit,
    )
except Exception:
    try:
        from regen_candidate_ranking_input_audit import (
            attach_regen_candidate_ranking_input_audit,
        )
    except Exception:
        attach_regen_candidate_ranking_input_audit = None


try:
    from leaf_qt.optimisation.report.regen_candidate_ranking_report_owner import (
        attach_regen_candidate_ranking_report_owner,
    )
except Exception:
    try:
        from regen_candidate_ranking_report_owner import (
            attach_regen_candidate_ranking_report_owner,
        )
    except Exception:
        attach_regen_candidate_ranking_report_owner = None


try:
    from leaf_qt.optimisation.owner.regen_candidate_ranking_registration_owner import (
        attach_regen_candidate_ranking_registration_owner,
    )
except Exception:
    try:
        from regen_candidate_ranking_registration_owner import (
            attach_regen_candidate_ranking_registration_owner,
        )
    except Exception:
        attach_regen_candidate_ranking_registration_owner = None


try:
    from leaf_qt.optimisation.validation.regen_candidate_ranking_completion_audit import (
        attach_regen_candidate_ranking_completion_audit,
    )
except Exception:
    try:
        from regen_candidate_ranking_completion_audit import (
            attach_regen_candidate_ranking_completion_audit,
        )
    except Exception:
        attach_regen_candidate_ranking_completion_audit = None


try:
    from leaf_qt.optimisation.validation.regen_candidate_ranking_master_gate import (
        attach_regen_candidate_ranking_master_gate,
    )
except Exception:
    try:
        from regen_candidate_ranking_master_gate import (
            attach_regen_candidate_ranking_master_gate,
        )
    except Exception:
        attach_regen_candidate_ranking_master_gate = None


# --------- Constants ----------
Gravity = 9.81
Ambient_Pressure = 101325.0

# Universal Gas Constant
Universal_Gas_Constant = 8314.462618  # J/(kmol·K)

# =========================================================
# PROPELLANT DENSITY DATABASE
# =========================================================
# Approximate reference densities in kg/m³.
#
# These are engineering reference values for comparison graphs.
# They are not a replacement for full temperature/pressure dependent
# fluid property modelling.
#
# The key rule:
# - liquid options should use liquid density
# - room-temperature/gaseous options should use approximate gas density

PROPELLANT_DENSITY_DATABASE = {
    # -----------------------------
    # Methane
    # -----------------------------
    "CH4": {
        "room": 0.657,
        "gas": 0.657,
        "liquid": 422.0,
        "default": "liquid"
    },
    "METHANE": {
        "room": 0.657,
        "gas": 0.657,
        "liquid": 422.0,
        "default": "liquid"
    },
    "GCH4": {
        "room": 0.657,
        "gas": 0.657,
        "liquid": 422.0,
        "default": "gas"
    },
    "LCH4": {
        "room": 0.657,
        "gas": 0.657,
        "liquid": 422.0,
        "default": "liquid"
    },
    "LCH4_NASA": {
        "room": 0.657,
        "gas": 0.657,
        "liquid": 422.0,
        "default": "liquid"
    },
    "LIQUID METHANE": {
        "room": 0.657,
        "gas": 0.657,
        "liquid": 422.0,
        "default": "liquid"
    },

    # -----------------------------
    # Hydrogen
    # -----------------------------
    "H2": {
        "room": 0.0838,
        "gas": 0.0838,
        "liquid": 70.85,
        "default": "liquid"
    },
    "HYDROGEN": {
        "room": 0.0838,
        "gas": 0.0838,
        "liquid": 70.85,
        "default": "liquid"
    },
    "GH2": {
        "room": 0.0838,
        "gas": 0.0838,
        "liquid": 70.85,
        "default": "gas"
    },
    "LH2": {
        "room": 0.0838,
        "gas": 0.0838,
        "liquid": 70.85,
        "default": "liquid"
    },
    "LH2_NASA": {
        "room": 0.0838,
        "gas": 0.0838,
        "liquid": 70.85,
        "default": "liquid"
    },
    "LIQUID HYDROGEN": {
        "room": 0.0838,
        "gas": 0.0838,
        "liquid": 70.85,
        "default": "liquid"
    },

    # -----------------------------
    # Kerosene / hydrocarbon fuels
    # -----------------------------
    "RP-1": {
        "room": 810.0,
        "liquid": 810.0,
        "default": "liquid"
    },
    "RP1": {
        "room": 810.0,
        "liquid": 810.0,
        "default": "liquid"
    },
    "RP-1 / KEROSENE": {
        "room": 810.0,
        "liquid": 810.0,
        "default": "liquid"
    },
    "KEROSENE": {
        "room": 810.0,
        "liquid": 810.0,
        "default": "liquid"
    },
    "JET-A": {
        "room": 804.0,
        "liquid": 804.0,
        "default": "liquid"
    },
    "JETA": {
        "room": 804.0,
        "liquid": 804.0,
        "default": "liquid"
    },
    "JET A": {
        "room": 804.0,
        "liquid": 804.0,
        "default": "liquid"
    },

    # -----------------------------
    # Alcohol fuels
    # -----------------------------
    "ETHANOL": {
        "room": 789.0,
        "liquid": 789.0,
        "default": "liquid"
    },
    "METHANOL": {
        "room": 792.0,
        "liquid": 792.0,
        "default": "liquid"
    },

    # -----------------------------
    # Hypergolic fuels
    # -----------------------------
    "MMH": {
        "room": 874.0,
        "liquid": 874.0,
        "default": "liquid"
    },
    "UDMH": {
        "room": 793.0,
        "liquid": 793.0,
        "default": "liquid"
    },
    "N2H4": {
        "room": 1004.0,
        "liquid": 1004.0,
        "default": "liquid"
    },
    "HYDRAZINE": {
        "room": 1004.0,
        "liquid": 1004.0,
        "default": "liquid"
    },

    # -----------------------------
    # Oxygen
    # -----------------------------
    "O2": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "gas"
    },
    "GOX": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "gas"
    },
    "GASEOUS O2": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "gas"
    },
    "GASEOUS OXYGEN": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "gas"
    },
    "LOX": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "liquid"
    },
    "LO2": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "liquid"
    },
    "O2(L)": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "liquid"
    },
    "LIQUID OXYGEN": {
        "room": 1.331,
        "gas": 1.331,
        "liquid": 1141.0,
        "default": "liquid"
    },

    # -----------------------------
    # Other oxidizers
    # -----------------------------
    "N2O": {
        "room": 1.977,
        "gas": 1.977,
        "liquid": 750.0,
        "default": "liquid"
    },
    "NITROUS OXIDE": {
        "room": 1.977,
        "gas": 1.977,
        "liquid": 750.0,
        "default": "liquid"
    },
    "N2O4": {
        "room": 1440.0,
        "liquid": 1440.0,
        "default": "liquid"
    },
    "NTO": {
        "room": 1440.0,
        "liquid": 1440.0,
        "default": "liquid"
    },
    "MON3": {
        "room": 1440.0,
        "liquid": 1440.0,
        "default": "liquid"
    },
    "MON15": {
        "room": 1420.0,
        "liquid": 1420.0,
        "default": "liquid"
    },
    "MON25": {
        "room": 1400.0,
        "liquid": 1400.0,
        "default": "liquid"
    },
    "H2O2": {
        "room": 1450.0,
        "liquid": 1450.0,
        "default": "liquid"
    },
    "90_H2O2": {
        "room": 1390.0,
        "liquid": 1390.0,
        "default": "liquid"
    },
    "98_H2O2": {
        "room": 1430.0,
        "liquid": 1430.0,
        "default": "liquid"
    },
    "PEROXIDE90": {
        "room": 1390.0,
        "liquid": 1390.0,
        "default": "liquid"
    },
    "PEROXIDE98": {
        "room": 1430.0,
        "liquid": 1430.0,
        "default": "liquid"
    },
}


def normalise_propellant_density_key(propellant_name):
    if propellant_name is None:
        return None

    return str(propellant_name).strip().upper()


def get_propellant_density(propellant_name, phase=None):
    """
    Returns approximate propellant density in kg/m³.

    phase options:
        None      -> use database default phase
        "room"   -> room-temperature/gas reference where available
        "gas"    -> gaseous reference where available
        "liquid" -> liquid reference where available
    """

    key = normalise_propellant_density_key(propellant_name)

    if key not in PROPELLANT_DENSITY_DATABASE:
        return None

    data = PROPELLANT_DENSITY_DATABASE[key]

    if phase is None:
        phase = data.get("default", "liquid")

    phase = str(phase).lower()

    density = data.get(phase)

    if density is None:
        density = data.get("liquid")

    if density is None:
        density = data.get("room")

    if density is None:
        density = data.get("gas")

    return density


def infer_propellant_phase(propellant_name, temperature_k=None):
    """
    Infers the density phase from the selected name and temperature.

    This avoids treating H2 at 20 K as room-temperature gas.
    """

    name = normalise_propellant_density_key(propellant_name)

    if name is None:
        return None

    if name.startswith("G") or "GASEOUS" in name:
        return "gas"

    if name.startswith("L") or "(L)" in name or "LIQUID" in name:
        return "liquid"

    temp = None
    try:
        if temperature_k is not None:
            temp = float(temperature_k)
    except Exception:
        temp = None

    if temp is not None:
        if temp < 160.0:
            return "liquid"

    data = PROPELLANT_DENSITY_DATABASE.get(name)

    if data is None:
        return None

    return data.get("default", "liquid")


def get_propellant_density_from_temperature(propellant_name, temperature_k=None):
    if get_fluid_density is not None:
        density = get_fluid_density(propellant_name, temperature_k)

        if density is not None:
            return density

    phase = infer_propellant_phase(propellant_name, temperature_k)
    return get_propellant_density(propellant_name, phase=phase)


# --------- Input helpers ----------
def ask_float(prompt):
    while True:
        value = input(prompt)
        if value.strip() == "" or value.lower() == "n/a":
            return None
        try:
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a number, leave blank, or 'N/A'.")

def get_inputs():
    params = {}
    prompts = {
        "Gamma": "Enter the Specific Heat Ratio (Gamma) or 'N/A': ",
        "R": "Enter the Specific Gas Constant (R) or 'N/A': ",
        "gas_prandtl_number": "Enter the Prandtl Number (Pr) or 'N/A': ",
        "mass_flow_rate": "Enter Mass Flow Rate (kg/s) or 'N/A': ",
        "mixture_ratio": "Enter Mixture Ratio O/F or 'N/A': ",
        "fuel_mass_flow_rate": "Enter Fuel Mass Flow Rate (kg/s) or 'N/A': ",
        "oxidizer_mass_flow_rate": "Enter Oxidizer Mass Flow Rate (kg/s) or 'N/A': ",
        "throat_area": "Enter Throat Area (m²) or 'N/A': ",
        "exit_area": "Enter Exit Area (m²) or 'N/A': ",
        "expansion_ratio": "Enter Expansion Ratio or 'N/A': ",
        "selected_length": "Enter Selected Length Along Nozzle (m) or 'N/A': ",
        "cross_sectional_area": "Enter Cross Sectional Area (m²) or 'N/A': ",
        "throat_radius": "Enter Throat Radius (m) or 'N/A': ",
        "exit_radius": "Enter Exit Radius (m) or 'N/A': ",
        "radius_2": "Enter Radius 2 (m) or 'N/A': ",
        "radius_3": "Enter Radius 3 (m) or 'N/A': ",
        "chamber_contraction_ratio": "Enter Chamber Contraction Ratio Ac/At or 'N/A': ",
        "chamber_converging_half_angle_deg": "Enter Chamber Converging Half Angle (deg) or 'N/A': ",
        "chamber_temperature": "Enter Chamber Temperature (K) or 'N/A': ",
        "chamber_pressure": "Enter Chamber Pressure (Pa) or 'N/A': ",
        "static_temperature": "Enter Static Temperature (K) or 'N/A': ",
        "static_pressure": "Enter Static Pressure (Pa) or 'N/A': ",
        "static_density": "Enter Static Density (kg/m³) or 'N/A': ",
        "estimated_residence_time": "Enter Estimated Residence Time (s) or 'N/A': ",
        "characteristic_length": "Enter Characteristic Length (m) or 'N/A': ",
        "characteristic_velocity": "Enter Characteristic Velocity (m/s) or 'N/A': ",
        "exhaust_velocity": "Enter Exhaust Velocity (m/s) or 'N/A': ",
        "thrust": "Enter Thrust (N) or 'N/A': ",
        "specific_impulse": "Enter Specific Impulse (s) or 'N/A': ",
        "vacuum_specific_impulse": "Enter Vacuum Specific Impulse (s) or 'N/A': ",
        "sea_level_specific_impulse": "Enter Sea Level Specific Impulse (s) or 'N/A': ",
        "thrust_coefficient": "Enter Thrust Coefficient or 'N/A': ",
        "momentum_thrust": "Enter Momentum Thrust (N) or 'N/A': ",
        "pressure_thrust": "Enter Pressure Thrust (N) or 'N/A': ",
        "exit_pressure": "Enter Exit Pressure (Pa) or 'N/A': ",
        "ambient_pressure": "Enter Ambient Pressure (Pa) or 'N/A': ",
        "effective_exhaust_velocity": "Enter Effective Exhaust Velocity (m/s) or 'N/A': ",
        "combustion_efficiency": None,
        "mixture_quality_factor": None,
        "soot_risk_factor": None,
        "thermal_risk_factor": None,
        "corrected_thrust": None,
        "corrected_specific_impulse": None,
        "mach_number": "Enter Mach Number (M) or 'N/A': ",
        "selected_mach_number": "Enter Selected Mach Number (M) or 'N/A': ",
        "adiabatic_wall_temperature": "Enter Adiabatic Wall Temperature (K) or 'N/A': ",
        "selected_gas_side_recovery_temperature": "Enter Selected Gas Side Recovery Temperature (K) or 'N/A': ",
        "compressibility_correlation_factor": "Enter Compressibility Correlation Factor (R) or 'N/A': ",
    }

    for key, prompt in prompts.items():
        if prompt is None:
            params[key] = None
        else:
            params[key] = ask_float(prompt)

    return params

# --------- Calculation functions ----------
# =========================================================
# THERMODYNAMIC PROPERTY CONSISTENCY
# =========================================================

def solve_thermodynamic_properties(results):
    """
    Creates a consistent thermodynamic set.

    Priority:
    1. Use CEA-selected gamma and molecular weight to compute R.
    2. Use gamma and R to compute internally consistent Cp and Cv.
    3. Keep raw CEA Cp/Cv values as reference only.
    """

    gamma = (
        results.get("Gamma")
        or results.get("cea_selected_gamma")
    )

    molecular_weight = (
        results.get("cea_selected_molecular_weight")
        or results.get("cea_molecular_weight")
    )

    gas_constant = results.get("R")

    if gas_constant is None and molecular_weight is not None and molecular_weight > 0:
        gas_constant = Universal_Gas_Constant / molecular_weight

    if gamma is not None and gas_constant is not None and gamma > 1:
        cp_consistent = gamma * gas_constant / (gamma - 1)
        cv_consistent = gas_constant / (gamma - 1)

        results["Gamma"] = gamma
        results["R"] = gas_constant
        results["specific_heat_cp"] = cp_consistent
        results["specific_heat_cv"] = cv_consistent

        results["thermo_model_note"] = (
            "Cp and Cv computed from Gamma and R for internal consistency. "
            "CEA Cp/Cv values retained as raw reference values."
        )

        results["thermo_r_error"] = 0.0
        results["thermo_r_error_percent"] = 0.0

    return results

def calculate_mass_flow_rate(throat_area=None, chamber_pressure=None, chamber_temperature=None, mach_number=None, characteristic_velocity=None, characteristic_length=None, estimated_residence_time=None, Gamma=None, R=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if throat_area is not None and chamber_pressure is not None and chamber_temperature is not None:
        if Gamma is None or R is None:
            return None
        if not _finite(throat_area, chamber_pressure, chamber_temperature, Gamma, R):
            return None
        if throat_area <= 0 or chamber_pressure <= 0 or chamber_temperature <= 0 or Gamma <= 1 or R <= 0:
            return None
        term1 = throat_area * chamber_pressure
        term2 = math.sqrt(Gamma / (R * chamber_temperature))
        term3 = ((2 / (Gamma + 1)) ** ((Gamma + 1) / (2 * (Gamma - 1))))
        result = term1 * term2 * term3
        return result if _finite(result) and result >= 0 else None

    elif characteristic_velocity is not None and throat_area is not None and chamber_pressure is not None:
        if not _finite(characteristic_velocity, throat_area, chamber_pressure):
            return None
        if characteristic_velocity <= 0 or throat_area <= 0 or chamber_pressure <= 0:
            return None
        result = (chamber_pressure * throat_area) / characteristic_velocity
        return result if _finite(result) and result >= 0 else None

    elif estimated_residence_time is not None and chamber_temperature is not None and throat_area is not None and characteristic_length is not None and mach_number is not None:
        if chamber_pressure is None or R is None:
            return None
        if not _finite(
            estimated_residence_time,
            chamber_temperature,
            throat_area,
            characteristic_length,
            mach_number,
            chamber_pressure,
            R,
        ):
            return None
        if (
            estimated_residence_time <= 0
            or chamber_temperature <= 0
            or throat_area <= 0
            or characteristic_length <= 0
            or mach_number <= 0
            or chamber_pressure <= 0
            or R <= 0
        ):
            return None
        term1 = chamber_pressure * mach_number * throat_area * characteristic_length
        term2 = estimated_residence_time * R * chamber_temperature
        result = term1 / term2
        return result if _finite(result) and result >= 0 else None

    return None

def calculate_throat_area(mass_flow_rate=None, chamber_pressure=None, chamber_temperature=None, chamber_volume=None, mach_number=None, characteristic_velocity=None, characteristic_length=None, exit_area=None, estimated_residence_time=None, Gamma=None, R=None):
    if mass_flow_rate is not None and characteristic_velocity is not None and chamber_pressure is not None:
        return (characteristic_velocity * mass_flow_rate) / chamber_pressure
    elif mass_flow_rate is not None and chamber_pressure is not None and chamber_temperature is not None:
        term1 = mass_flow_rate / chamber_pressure
        term2 = math.sqrt((R * chamber_temperature) / Gamma)
        term3 = ((Gamma + 1) / 2) ** ((Gamma + 1) / (2 * (Gamma - 1)))
        return term1 * term2 * term3
    elif characteristic_length is not None and chamber_volume is not None:
        return chamber_volume / characteristic_length
    elif exit_area is not None and mach_number is not None:
        term1 = ((2 / (Gamma + 1)) * (1 + ((Gamma - 1) / 2) * mach_number ** 2))
        term2 = term1 ** ((Gamma + 1) / (2 * (Gamma - 1)))
        return (exit_area * mach_number) / term2
    elif mass_flow_rate is not None and chamber_temperature is not None and chamber_pressure is not None and characteristic_length is not None and mach_number is not None and estimated_residence_time is not None:
        return (mass_flow_rate * estimated_residence_time * R * chamber_temperature) / (chamber_pressure * mach_number * characteristic_length)
    else:
        return None

def calculate_exit_area(mach_number=None, throat_area=None, Gamma=None):
    if mach_number is None or throat_area is None or Gamma is None:
        return None
    if not all(math.isfinite(float(value)) for value in (mach_number, throat_area, Gamma)):
        return None
    if mach_number <= 0 or throat_area <= 0 or Gamma <= 1:
        return None
    term1 = throat_area / mach_number
    term2 = ((2 / (Gamma + 1)) * (1 + ((Gamma - 1) / 2) * mach_number ** 2))
    term3 = term2 ** ((Gamma + 1) / (2 * (Gamma - 1)))
    return term1 * term3

def calculate_expansion_ratio(throat_area=None, exit_area=None):
    if throat_area is None or exit_area is None:
        return None
    if not all(math.isfinite(float(value)) for value in (throat_area, exit_area)):
        return None
    if throat_area <= 0 or exit_area < 0:
        return None
    return exit_area / throat_area

def calculate_selected_expansion_ratio(throat_area=None, cross_sectional_area=None):
    if throat_area is None or cross_sectional_area is None:
        return None
    if not all(math.isfinite(float(value)) for value in (throat_area, cross_sectional_area)):
        return None
    if throat_area <= 0 or cross_sectional_area < 0:
        return None
    return cross_sectional_area / throat_area

def calculate_nozzle_length(
        radius_3=None,
        throat_radius=None,
        exit_radius=None,
        nozzle_geometry_model="RAO_BELL_APPROXIMATION",
        conical_half_angle_deg=15.0,
        rao_length_fraction=0.8,
):
    if throat_radius is None or exit_radius is None:
        return None

    if throat_radius <= 0 or exit_radius <= throat_radius:
        return None

    model = str(nozzle_geometry_model or "RAO_BELL_APPROXIMATION").upper()

    conical_length = calculate_equivalent_conical_nozzle_length(
        throat_radius=throat_radius,
        exit_radius=exit_radius,
        half_angle_deg=conical_half_angle_deg,
    )

    if conical_length is None:
        return None

    if model == "CONICAL":
        return conical_length

    return conical_length * rao_length_fraction

def calculate_cross_sectional_area(radius_3=None, selected_length=None, throat_radius=None):
    if radius_3 is not None and selected_length is not None and throat_radius is not None:
        threshold = math.sin(math.radians(15)) * radius_3
        if selected_length == 0:
            return math.pi * (throat_radius ** 2)
        elif 0 < selected_length <= threshold:
            return math.pi * (((- math.sqrt(radius_3 ** 2 - selected_length ** 2)) + radius_3 + throat_radius) ** 2)
        else:
            C = (throat_radius + (radius_3 * (1 - math.cos(math.radians(15)))) - ((math.sin(math.radians(15)) ** 2 * radius_3) / math.cos(math.radians(15))))
            return math.pi * (((math.sin(math.radians(15)) / math.cos(math.radians(15))) * selected_length + C) ** 2)
    else:
        return None

def calculate_equivalent_conical_nozzle_length(
        throat_radius=None,
        exit_radius=None,
        half_angle_deg=15.0
):
    """
    Equivalent conical nozzle length.

    Valid-domain relation:
        L = (Re - Rt) / tan(theta)

    where theta is the conical half-angle in degrees.
    """

    if (
        throat_radius is None
        or exit_radius is None
        or half_angle_deg is None
    ):
        return None

    try:
        throat_radius_value = float(
            throat_radius
        )

        exit_radius_value = float(
            exit_radius
        )

        half_angle_value = float(
            half_angle_deg
        )

    except (TypeError, ValueError):
        return None


    if (
        not math.isfinite(
            throat_radius_value
        )
        or not math.isfinite(
            exit_radius_value
        )
        or not math.isfinite(
            half_angle_value
        )
        or throat_radius_value <= 0.0
        or exit_radius_value <= throat_radius_value
        or half_angle_value <= 0.0
        or half_angle_value >= 90.0
    ):
        return None


    angle = math.radians(
        half_angle_value
    )

    tangent = math.tan(
        angle
    )


    if (
        not math.isfinite(
            tangent
        )
        or tangent <= 0.0
    ):
        return None


    return (
        (
            exit_radius_value
            - throat_radius_value
        )
        / tangent
    )



def estimate_rao_bell_angles(expansion_ratio=None, rao_length_fraction=0.8):
    if expansion_ratio is None or expansion_ratio <= 1.0:
        expansion_ratio = 10.0

    if rao_length_fraction is None:
        rao_length_fraction = 0.8

    rao_length_fraction = max(0.6, min(1.0, rao_length_fraction))

    if expansion_ratio < 10.0:
        theta_start = 30.0
        theta_exit = 12.0
    elif expansion_ratio < 25.0:
        theta_start = 28.0
        theta_exit = 9.0
    elif expansion_ratio < 50.0:
        theta_start = 26.0
        theta_exit = 7.0
    elif expansion_ratio < 100.0:
        theta_start = 24.0
        theta_exit = 5.5
    else:
        theta_start = 22.0
        theta_exit = 4.5

    if rao_length_fraction < 0.8:
        theta_start += 2.0
        theta_exit += 1.0
    elif rao_length_fraction > 0.9:
        theta_start -= 1.0
        theta_exit -= 0.5

    return theta_start, theta_exit


def calculate_rao_bell_nozzle_length(
        throat_radius=None,
        exit_radius=None,
        rao_length_fraction=0.8
):
    """
    Rao-style bell approximation length.

    The active LEAF approximation defines bell length as a bounded
    fraction of the equivalent 15-degree conical nozzle length.

    Qualified fraction domain:
        0.60 <= rao_length_fraction <= 1.00
    """

    if rao_length_fraction is None:
        return None

    try:
        fraction = float(
            rao_length_fraction
        )

    except (TypeError, ValueError):
        return None


    if (
        not math.isfinite(
            fraction
        )
        or fraction < 0.60
        or fraction > 1.00
    ):
        return None


    conical_length = (
        calculate_equivalent_conical_nozzle_length(
            throat_radius=throat_radius,
            exit_radius=exit_radius,
            half_angle_deg=15.0,
        )
    )


    if conical_length is None:
        return None


    return (
        conical_length
        * fraction
    )



def calculate_rao_bell_radius_at_x(
        x=None,
        throat_radius=None,
        exit_radius=None,
        nozzle_length=None,
        expansion_ratio=None,
        rao_length_fraction=0.8
):
    """
    Return the local Rao-bell gas radius.

    The divergent contour uses the existing 0.382 Rt throat-radius
    owner from T to the Rao start-angle point N, followed by the
    tangent-matched quadratic parabolic bell from N to exit E.
    """
    if (
        x is None
        or throat_radius is None
        or exit_radius is None
        or nozzle_length is None
    ):
        return None

    if (
        throat_radius <= 0
        or exit_radius <= throat_radius
        or nozzle_length <= 0
    ):
        return None

    x = max(
        0.0,
        min(
            float(x),
            float(nozzle_length),
        ),
    )

    theta_start_deg, theta_exit_deg = estimate_rao_bell_angles(
        expansion_ratio=expansion_ratio,
        rao_length_fraction=rao_length_fraction,
    )

    theta_start = math.radians(
        theta_start_deg
    )
    theta_exit = math.radians(
        theta_exit_deg
    )

    radius_3 = calculate_radius_3(
        throat_radius=throat_radius
    )

    if (
        radius_3 is None
        or radius_3 <= 0
    ):
        return None

    n_x = (
        radius_3
        * math.sin(theta_start)
    )
    n_radius = (
        throat_radius
        + radius_3
        * (
            1.0
            - math.cos(theta_start)
        )
    )

    if x <= n_x:
        ratio = max(
            -1.0,
            min(
                1.0,
                x / radius_3,
            ),
        )

        phi = math.asin(
            ratio
        )

        return (
            throat_radius
            + radius_3
            * (
                1.0
                - math.cos(phi)
            )
        )

    slope_start = math.tan(
        theta_start
    )
    slope_exit = math.tan(
        theta_exit
    )

    denominator = (
        slope_start
        - slope_exit
    )

    if abs(denominator) < 1.0e-15:
        return None

    start_intercept = (
        n_radius
        - slope_start * n_x
    )
    exit_intercept = (
        exit_radius
        - slope_exit * nozzle_length
    )

    control_x = (
        exit_intercept
        - start_intercept
    ) / denominator

    control_radius = (
        slope_start
        * control_x
        + start_intercept
    )

    if not (
        n_x
        < control_x
        < nozzle_length
    ):
        return None

    a = (
        n_x
        - 2.0 * control_x
        + nozzle_length
    )
    b = (
        2.0
        * (
            control_x
            - n_x
        )
    )
    c = (
        n_x
        - x
    )

    if abs(a) < 1.0e-15:
        if abs(b) < 1.0e-15:
            return None

        roots = [
            -c / b
        ]

    else:
        discriminant = (
            b * b
            - 4.0 * a * c
        )

        if (
            discriminant < 0.0
            and discriminant > -1.0e-12
        ):
            discriminant = 0.0

        if discriminant < 0.0:
            return None

        root = math.sqrt(
            discriminant
        )

        roots = [
            (
                -b + root
            )
            / (
                2.0 * a
            ),
            (
                -b - root
            )
            / (
                2.0 * a
            ),
        ]

    valid_roots = [
        max(
            0.0,
            min(
                1.0,
                root,
            ),
        )
        for root in roots
        if (
            -1.0e-12
            <= root
            <= 1.0 + 1.0e-12
        )
    ]

    if not valid_roots:
        return None

    def x_at(parameter):
        one_minus = (
            1.0
            - parameter
        )

        return (
            one_minus ** 2
            * n_x
            + 2.0
            * one_minus
            * parameter
            * control_x
            + parameter ** 2
            * nozzle_length
        )

    parameter = min(
        valid_roots,
        key=lambda candidate:
            abs(
                x_at(candidate)
                - x
            ),
    )

    one_minus = (
        1.0
        - parameter
    )

    radius = (
        one_minus ** 2
        * n_radius
        + 2.0
        * one_minus
        * parameter
        * control_radius
        + parameter ** 2
        * exit_radius
    )

    return max(
        throat_radius,
        radius,
    )


def build_rao_nozzle_profile(results, station_count=100):
    if results is None:
        return results

    throat_radius = results.get("throat_radius")
    exit_radius = results.get("exit_radius")
    expansion_ratio = results.get("expansion_ratio")
    rao_length_fraction = results.get("rao_length_fraction", 0.8)

    if throat_radius is None or exit_radius is None:
        results["rao_nozzle_status"] = "RAO_GEOMETRY_BLOCKED"
        results["rao_nozzle_reason"] = "Missing throat or exit radius."
        return results

    if expansion_ratio is None and throat_radius > 0:
        expansion_ratio = (exit_radius / throat_radius) ** 2
        results["expansion_ratio"] = expansion_ratio

    # IMPORTANT:
    # Always recompute active Rao length from active geometry settings.
    # Do not reuse old conical/legacy nozzle_length.
    nozzle_length = calculate_rao_bell_nozzle_length(
        throat_radius=throat_radius,
        exit_radius=exit_radius,
        rao_length_fraction=rao_length_fraction,
    )

    results["nozzle_length"] = nozzle_length

    if nozzle_length is None or nozzle_length <= 0:
        results["rao_nozzle_status"] = "RAO_GEOMETRY_BLOCKED"
        results["rao_nozzle_reason"] = "Could not calculate Rao bell nozzle length."
        return results

    theta_start_deg, theta_exit_deg = estimate_rao_bell_angles(
        expansion_ratio=expansion_ratio,
        rao_length_fraction=rao_length_fraction,
    )

    station_count = int(station_count or 100)
    station_count = max(8, min(station_count, 400))

    profile = []
    previous_radius = None
    monotonic = True

    for index in range(station_count):
        fraction = index / max(station_count - 1, 1)
        x = fraction * nozzle_length

        radius = calculate_rao_bell_radius_at_x(
            x=x,
            throat_radius=throat_radius,
            exit_radius=exit_radius,
            nozzle_length=nozzle_length,
            expansion_ratio=expansion_ratio,
            rao_length_fraction=rao_length_fraction,
        )

        if radius is None:
            continue

        if previous_radius is not None and radius < previous_radius:
            monotonic = False

        previous_radius = radius

        area = math.pi * radius**2
        local_expansion_ratio = area / max(math.pi * throat_radius**2, 1.0e-12)

        profile.append({
            "station_index": index,
            "station_label": f"Rao {index}",
            "x": x,
            "fraction": fraction,
            "radius": radius,
            "area": area,
            "local_expansion_ratio": local_expansion_ratio,
            "nozzle_model": "RAO_BELL_APPROXIMATION",
        })

    results["nozzle_geometry_model"] = "RAO_BELL_APPROXIMATION"
    results.pop("rao_nozzle_reason", None)
    results["rao_nozzle_status"] = (
        "RAO_GEOMETRY_READY"
        if monotonic and profile
        else "RAO_GEOMETRY_WARN_NON_MONOTONIC"
    )
    results["rao_nozzle_profile"] = profile
    results["rao_nozzle_summary"] = {
        "nozzle_model": "RAO_BELL_APPROXIMATION",
        "throat_radius": throat_radius,
        "exit_radius": exit_radius,
        "nozzle_length": nozzle_length,
        "expansion_ratio": expansion_ratio,
        "rao_length_fraction": rao_length_fraction,
        "theta_start_deg": theta_start_deg,
        "theta_exit_deg": theta_exit_deg,
        "station_count": len(profile),
        "monotonic_radius": monotonic,
    }

    return results

def build_conical_nozzle_profile(results, station_count=100):
    if results is None:
        return results

    throat_radius = results.get("throat_radius")
    exit_radius = results.get("exit_radius")
    half_angle_deg = results.get("conical_half_angle_deg") or 15.0

    if throat_radius is None or exit_radius is None:
        results["conical_nozzle_status"] = "CONICAL_GEOMETRY_BLOCKED"
        results["conical_nozzle_reason"] = "Missing throat or exit radius."
        return results

    # IMPORTANT:
    # Always recompute active conical length from active geometry settings.
    # Do not reuse old Rao/legacy nozzle_length.
    nozzle_length = calculate_equivalent_conical_nozzle_length(
        throat_radius=throat_radius,
        exit_radius=exit_radius,
        half_angle_deg=half_angle_deg,
    )

    results["nozzle_length"] = nozzle_length

    if nozzle_length is None or nozzle_length <= 0:
        results["conical_nozzle_status"] = "CONICAL_GEOMETRY_BLOCKED"
        results["conical_nozzle_reason"] = "Could not calculate conical nozzle length."
        return results

    station_count = int(station_count or 100)
    station_count = max(8, min(station_count, 400))

    profile = []

    for index in range(station_count):
        fraction = index / max(station_count - 1, 1)
        x = fraction * nozzle_length

        radius = throat_radius + fraction * (exit_radius - throat_radius)
        area = math.pi * radius**2
        local_expansion_ratio = area / max(math.pi * throat_radius**2, 1.0e-12)

        profile.append({
            "station_index": index,
            "station_label": f"Conical {index}",
            "x": x,
            "fraction": fraction,
            "radius": radius,
            "area": area,
            "local_expansion_ratio": local_expansion_ratio,
            "nozzle_model": "CONICAL",
        })

    results["nozzle_geometry_model"] = "CONICAL"
    results.pop("conical_nozzle_reason", None)
    results["conical_nozzle_status"] = "CONICAL_GEOMETRY_READY"
    results["conical_nozzle_profile"] = profile
    results["conical_nozzle_summary"] = {
        "nozzle_model": "CONICAL",
        "throat_radius": throat_radius,
        "exit_radius": exit_radius,
        "nozzle_length": nozzle_length,
        "conical_half_angle_deg": half_angle_deg,
        "station_count": len(profile),
    }

    return results

def evaluate_nozzle_geometry_smoothness(results):
    if results is None:
        return results

    model = str(
        results.get("nozzle_geometry_model")
        or "RAO_BELL_APPROXIMATION"
    ).upper()

    if model == "CONICAL":
        profile = results.get("conical_nozzle_profile") or []
    else:
        profile = results.get("rao_nozzle_profile") or []

    if not profile:
        results["nozzle_geometry_smoothness_status"] = "NO_PROFILE"
        results["nozzle_geometry_smoothness_notes"] = [
            "No nozzle profile exists to evaluate."
        ]
        return results

    notes = []
    radius_failures = 0

    previous_radius = None

    for station in profile:
        radius = station.get("radius")

        if radius is None:
            continue

        if previous_radius is not None and radius < previous_radius:
            radius_failures += 1

        previous_radius = radius

    if radius_failures > 0:
        status = "NOZZLE_GEOMETRY_NOT_MONOTONIC"
        notes.append(f"{radius_failures} stations reduce in radius downstream.")
    else:
        status = "NOZZLE_GEOMETRY_SMOOTH_BASIC"
        notes.append("Nozzle radius increases monotonically from throat to exit.")

    results["nozzle_geometry_smoothness_status"] = status
    results["nozzle_geometry_smoothness_notes"] = notes

    return results

def calculate_throat_radius(throat_area=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if throat_area is not None:
        if not _finite(throat_area):
            return None
        if throat_area < 0:
            return None

        result = math.sqrt(throat_area / math.pi)
        return result if _finite(result) and result >= 0 else None

    return None

def calculate_exit_radius(exit_area=None):
    if exit_area is None:
        return None
    if not math.isfinite(float(exit_area)):
        return None
    if exit_area < 0:
        return None
    return math.sqrt(exit_area / math.pi)

def calculate_radius_2(throat_radius=None):
    if throat_radius is not None:
        return throat_radius * 1.5
    else:
        return None

def calculate_radius_3(throat_radius=None):
    if throat_radius is not None:
        return throat_radius * 0.382
    else:
        return None

def calculate_chamber_volume(
    characteristic_length=None,
    throat_area=None,
):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if (
        characteristic_length is not None
        and throat_area is not None
    ):
        if not _finite(characteristic_length, throat_area):
            return None
        if characteristic_length <= 0 or throat_area <= 0:
            return None

        result = characteristic_length * throat_area
        return result if _finite(result) and result > 0 else None

    return None


def calculate_chamber_cross_sectional_area(
    throat_area=None,
    chamber_contraction_ratio=None,
):
    if (
        throat_area is not None
        and throat_area > 0
        and chamber_contraction_ratio is not None
        and chamber_contraction_ratio > 1.0
    ):
        return (
            chamber_contraction_ratio
            * throat_area
        )

    return None


def calculate_chamber_radius(
    chamber_cross_sectional_area=None,
):
    if (
        chamber_cross_sectional_area is not None
        and chamber_cross_sectional_area > 0
    ):
        return math.sqrt(
            chamber_cross_sectional_area
            / math.pi
        )

    return None


def calculate_chamber_diameter(
    chamber_radius=None,
):
    if (
        chamber_radius is not None
        and chamber_radius > 0
    ):
        return 2.0 * chamber_radius

    return None


def calculate_chamber_converging_length(
        chamber_radius=None,
        throat_radius=None,
        half_angle_deg=None,
):
    """Return axial length of the conical convergent plus the 1.5 Rt throat blend."""
    if None in (
        chamber_radius,
        throat_radius,
        half_angle_deg,
    ):
        return None

    if not (
        chamber_radius > throat_radius > 0
        and 0 < half_angle_deg < 90
    ):
        return None

    theta = math.radians(
        half_angle_deg
    )

    radius_2 = calculate_radius_2(
        throat_radius=throat_radius
    )

    if (
        radius_2 is None
        or radius_2 <= 0
    ):
        return None

    join_radius = (
        throat_radius
        + radius_2
        * (
            1.0
            - math.cos(theta)
        )
    )

    if chamber_radius <= join_radius:
        return None

    straight_length = (
        chamber_radius
        - join_radius
    ) / math.tan(theta)

    if straight_length <= 0:
        return None

    return (
        straight_length
        + radius_2
        * math.sin(theta)
    )


def calculate_chamber_converging_volume(
        chamber_radius=None,
        throat_radius=None,
        length=None,
        half_angle_deg=None,
):
    """Return exact volume of the conical convergent plus the 1.5 Rt throat blend."""
    if None in (
        chamber_radius,
        throat_radius,
        length,
        half_angle_deg,
    ):
        return None

    if not (
        chamber_radius > throat_radius > 0
        and length > 0
        and 0 < half_angle_deg < 90
    ):
        return None

    theta = math.radians(
        half_angle_deg
    )

    radius_2 = calculate_radius_2(
        throat_radius=throat_radius
    )

    if (
        radius_2 is None
        or radius_2 <= 0
    ):
        return None

    sin_theta = math.sin(
        theta
    )

    cos_theta = math.cos(
        theta
    )

    join_radius = (
        throat_radius
        + radius_2
        * (
            1.0
            - cos_theta
        )
    )

    arc_axial_length = (
        radius_2
        * sin_theta
    )

    straight_length = (
        length
        - arc_axial_length
    )

    if (
        chamber_radius <= join_radius
        or straight_length <= 0
    ):
        return None

    expected_straight_length = (
        chamber_radius
        - join_radius
    ) / math.tan(theta)

    if not math.isclose(
        straight_length,
        expected_straight_length,
        rel_tol=1.0e-10,
        abs_tol=1.0e-12,
    ):
        return None

    straight_volume = (
        math.pi
        * straight_length
        * (
            chamber_radius ** 2
            + chamber_radius
            * join_radius
            + join_radius ** 2
        )
        / 3.0
    )

    axis_radius = (
        throat_radius
        + radius_2
    )

    arc_integral = (
        (
            axis_radius ** 2
            + radius_2 ** 2
        )
        * radius_2
        * sin_theta

        - (
            radius_2 ** 3
            * sin_theta ** 3
            / 3.0
        )

        - (
            axis_radius
            * radius_2 ** 2
            * (
                sin_theta
                * cos_theta
                + theta
            )
        )
    )

    arc_volume = (
        math.pi
        * arc_integral
    )

    converging_volume = (
        straight_volume
        + arc_volume
    )

    if (
        not math.isfinite(
            converging_volume
        )
        or converging_volume <= 0
    ):
        return None

    return converging_volume


def build_combustion_chamber_geometry(
        results,
        module_execution_policy=None,
):
    """Canonical cylinder + conical convergent + 1.5 Rt throat blend with L* volume closure."""
    derived = (
        "chamber_volume",
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
    )

    if not module_execution_enabled(
        module_execution_policy,
        "combustion_chamber",
    ):
        for key in derived:
            results.pop(
                key,
                None,
            )

        return results

    volume = calculate_chamber_volume(
        results.get(
            "characteristic_length"
        ),
        results.get(
            "throat_area"
        ),
    )

    area = (
        calculate_chamber_cross_sectional_area(
            results.get(
                "throat_area"
            ),
            results.get(
                "chamber_contraction_ratio"
            ),
        )
    )

    radius = calculate_chamber_radius(
        area
    )

    diameter = calculate_chamber_diameter(
        radius
    )

    for key, value in {
        "chamber_volume":
            volume,

        "chamber_cross_sectional_area":
            area,

        "chamber_radius":
            radius,

        "chamber_diameter":
            diameter,
    }.items():

        if value is None:
            results.pop(
                key,
                None,
            )

        else:
            results[key] = value

    def block(
        reason,
        status="CHAMBER_GEOMETRY_BLOCKED",
    ):
        for key in derived[4:10]:
            results.pop(
                key,
                None,
            )

        results.update(
            chamber_geometry_model=(
                "CONICAL_CONVERGENT"
            ),
            chamber_geometry_status=status,
            chamber_geometry_reason=reason,
        )

        return results

    throat_radius = results.get(
        "throat_radius"
    )

    angle = results.get(
        "chamber_converging_half_angle_deg"
    )

    if None in (
        volume,
        area,
        radius,
        throat_radius,
    ):
        return block(
            "Missing chamber volume, chamber cross-section, "
            "or throat radius."
        )

    if angle is None:
        return block(
            "Missing chamber converging half angle."
        )

    if not 0 < angle < 90:
        return block(
            "Chamber converging half angle must be "
            "between 0 and 90 degrees.",
            "CHAMBER_GEOMETRY_INVALID",
        )

    radius_2 = calculate_radius_2(
        throat_radius=throat_radius
    )

    if (
        radius_2 is None
        or radius_2 <= 0
    ):
        return block(
            "Unable to construct the upstream 1.5 Rt throat blend.",
            "CHAMBER_GEOMETRY_INVALID",
        )

    theta = math.radians(
        angle
    )

    arc_join_radius = (
        throat_radius
        + radius_2
        * (
            1.0
            - math.cos(theta)
        )
    )

    if radius <= arc_join_radius:
        return block(
            "Chamber radius is too small for the upstream "
            "1.5 Rt throat blend at the selected converging angle.",
            "CHAMBER_GEOMETRY_INVALID",
        )

    converging_length = (
        calculate_chamber_converging_length(
            radius,
            throat_radius,
            angle,
        )
    )

    converging_volume = (
        calculate_chamber_converging_volume(
            radius,
            throat_radius,
            converging_length,
            angle,
        )
    )

    if None in (
        converging_length,
        converging_volume,
    ):
        return block(
            "Unable to construct R2-blended chamber convergence.",
            "CHAMBER_GEOMETRY_INVALID",
        )

    cylindrical_volume = (
        volume
        - converging_volume
    )

    if cylindrical_volume <= 0:
        return block(
            "Characteristic chamber volume is not large enough "
            "for the R2-blended converging section.",
            "CHAMBER_GEOMETRY_INVALID",
        )

    cylindrical_length = (
        cylindrical_volume
        / area
    )

    total_length = (
        cylindrical_length
        + converging_length
    )

    arc_join_x = (
        -radius_2
        * math.sin(theta)
    )

    x_converging_start = (
        -converging_length
    )

    profile = [
        {
            "x":
                -total_length,

            "radius":
                radius,

            "area":
                area,

            "section":
                "injector_face",
        },
        {
            "x":
                x_converging_start,

            "radius":
                radius,

            "area":
                area,

            "section":
                "converging_start",
        },
    ]

    straight_profile_station_count = 100

    for index in range(
        1,
        straight_profile_station_count + 1,
    ):
        fraction = (
            index
            / straight_profile_station_count
        )

        x_value = (
            x_converging_start
            + fraction
            * (
                arc_join_x
                - x_converging_start
            )
        )

        radius_value = (
            radius
            - math.tan(theta)
            * (
                x_value
                - x_converging_start
            )
        )

        profile.append({
            "x":
                x_value,

            "radius":
                radius_value,

            "area":
                math.pi
                * radius_value ** 2,

            "section":
                "straight_convergent",
        })

    arc_profile_station_count = 100

    for index in range(
        1,
        arc_profile_station_count + 1,
    ):
        fraction = (
            index
            / arc_profile_station_count
        )

        # Cosine clustering resolves both tangent ends of the
        # circular throat arc without inflating the profile size.
        phi = (
            theta
            * 0.5
            * (
                1.0
                + math.cos(
                    math.pi
                    * fraction
                )
            )
        )

        x_value = (
            -radius_2
            * math.sin(phi)
        )

        radius_value = (
            throat_radius
            + radius_2
            * (
                1.0
                - math.cos(phi)
            )
        )

        if index == arc_profile_station_count:
            x_value = 0.0
            radius_value = throat_radius

            area_value = results.get(
                "throat_area"
            )

            section = "throat"

        else:
            area_value = (
                math.pi
                * radius_value ** 2
            )

            section = (
                "R2_upstream_throat_arc"
            )

        profile.append({
            "x":
                x_value,

            "radius":
                radius_value,

            "area":
                area_value,

            "section":
                section,
        })

    results.update(
        chamber_geometry_model=(
            "CONICAL_CONVERGENT"
        ),

        chamber_converging_length=(
            converging_length
        ),

        chamber_converging_volume=(
            converging_volume
        ),

        chamber_cylindrical_volume=(
            cylindrical_volume
        ),

        chamber_cylindrical_length=(
            cylindrical_length
        ),

        chamber_total_length=(
            total_length
        ),

        chamber_profile=profile,

        chamber_geometry_status=(
            "CHAMBER_GEOMETRY_READY"
        ),
    )

    results.pop(
        "chamber_geometry_reason",
        None,
    )

    return results

def calculate_chamber_temperature(
        mass_flow_rate=None,
        throat_area=None,
        chamber_pressure=None,
        characteristic_velocity=None,
        characteristic_length=None,
        estimated_residence_time=None,
        mach_number=None,
        exhaust_velocity=None,
        Gamma=None,
        R=None
):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if (
        characteristic_velocity is not None
        and Gamma is not None
        and R is not None
    ):
        if not _finite(characteristic_velocity, Gamma, R):
            return None
        if characteristic_velocity <= 0 or Gamma <= 1 or R <= 0:
            return None

        cstar_factor = Gamma * (
            (2 / (Gamma + 1))
            ** ((Gamma + 1) / (2 * (Gamma - 1)))
        )

        if not _finite(cstar_factor):
            return None

        result = ((characteristic_velocity * cstar_factor) ** 2) / R
        return result if _finite(result) and result > 0 else None

    elif (
        mass_flow_rate is not None
        and estimated_residence_time is not None
        and characteristic_length is not None
        and chamber_pressure is not None
        and throat_area is not None
        and mach_number is not None
        and R is not None
    ):
        if not _finite(
            mass_flow_rate,
            estimated_residence_time,
            characteristic_length,
            chamber_pressure,
            throat_area,
            mach_number,
            R,
        ):
            return None

        if (
            mass_flow_rate <= 0
            or estimated_residence_time <= 0
            or characteristic_length <= 0
            or chamber_pressure <= 0
            or throat_area <= 0
            or mach_number <= 0
            or R <= 0
        ):
            return None

        result = (
            chamber_pressure
            * mach_number
            * throat_area
            * characteristic_length
        ) / (
            estimated_residence_time
            * R
            * mass_flow_rate
        )

        return result if _finite(result) and result > 0 else None

    return None

def calculate_chamber_pressure(mass_flow_rate=None, throat_area=None, chamber_temperature=None, characteristic_velocity=None, characteristic_length=None, exhaust_velocity=None, estimated_residence_time=None, mach_number=None, Gamma=None, R=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if mass_flow_rate is not None and throat_area is not None and chamber_temperature is not None:
        if Gamma is None or R is None:
            return None
        if not _finite(mass_flow_rate, throat_area, chamber_temperature, Gamma, R):
            return None
        if mass_flow_rate <= 0 or throat_area <= 0 or chamber_temperature <= 0 or Gamma <= 1 or R <= 0:
            return None

        term1 = mass_flow_rate / throat_area
        term2 = math.sqrt((R * chamber_temperature) / Gamma)
        term3 = (((Gamma + 1) / 2) ** ((Gamma + 1) / (2 * (Gamma - 1))))
        result = term1 * term2 * term3
        return result if _finite(result) and result > 0 else None

    elif characteristic_velocity is not None and mass_flow_rate is not None and throat_area is not None:
        if not _finite(characteristic_velocity, mass_flow_rate, throat_area):
            return None
        if characteristic_velocity <= 0 or mass_flow_rate <= 0 or throat_area <= 0:
            return None

        result = (characteristic_velocity * mass_flow_rate) / throat_area
        return result if _finite(result) and result > 0 else None

    elif mass_flow_rate is not None and chamber_temperature is not None and characteristic_length is not None and throat_area is not None and estimated_residence_time is not None and mach_number is not None:
        if R is None:
            return None
        if not _finite(
            mass_flow_rate,
            chamber_temperature,
            characteristic_length,
            throat_area,
            estimated_residence_time,
            mach_number,
            R,
        ):
            return None

        if (
            mass_flow_rate <= 0
            or chamber_temperature <= 0
            or characteristic_length <= 0
            or throat_area <= 0
            or estimated_residence_time <= 0
            or mach_number <= 0
            or R <= 0
        ):
            return None

        term1 = mass_flow_rate * estimated_residence_time * R * chamber_temperature
        term2 = throat_area * mach_number * characteristic_length
        result = term1 / term2
        return result if _finite(result) and result > 0 else None

    return None

def calculate_static_temperature(Gamma=None, selected_mach_number=None, chamber_temperature=None):
    if Gamma is not None and selected_mach_number is not None and chamber_temperature is not None:
        term1 = ((Gamma - 1) / 2)
        return chamber_temperature * ((1 + term1 * (selected_mach_number ** 2)) ** -1)
    else:
        return None

def calculate_static_pressure(Gamma=None, selected_mach_number=None, chamber_pressure=None):
    """
    Constant-gamma isentropic static-pressure relation.

    Returns None outside the physical/model domain accepted by this
    closed-form relation.
    """
    if (
        Gamma is None
        or selected_mach_number is None
        or chamber_pressure is None
    ):
        return None

    try:
        gamma = float(Gamma)
        mach = float(selected_mach_number)
        total_pressure = float(chamber_pressure)
    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(gamma)
        or not math.isfinite(mach)
        or not math.isfinite(total_pressure)
        or gamma <= 1.0
        or mach < 0.0
        or total_pressure <= 0.0
    ):
        return None

    term1 = ((gamma - 1.0) / 2.0)
    term2 = (-(gamma / (gamma - 1.0)))

    return (
        total_pressure
        * (
            1.0
            + term1
            * (mach ** 2)
        )
        ** term2
    )

def calculate_static_density(R=None, static_temperature=None, static_pressure=None):
    if R is not None and static_temperature is not None and static_pressure is not None:
        return static_pressure / (R * static_temperature)
    else:
        return None


def calculate_estimated_residence_time(throat_area=None, chamber_temperature=None, chamber_pressure=None, characteristic_length=None, mach_number=None, mass_flow_rate=None, R=None):
    if throat_area is not None and chamber_temperature is not None and chamber_pressure is not None and characteristic_length is not None and mach_number is not None and mass_flow_rate is not None:
        term1 = (chamber_pressure * mach_number * throat_area * characteristic_length)
        term2 = (R * chamber_temperature * mass_flow_rate)
        return  term1 / term2
    else:
        return None

def calculate_characteristic_length(throat_area=None, chamber_volume=None, mass_flow_rate=None, chamber_pressure=None, chamber_temperature=None, estimated_residence_time=None, mach_number=None, R=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if chamber_volume is not None and throat_area is not None:
        if not _finite(chamber_volume, throat_area):
            return None
        if chamber_volume <= 0 or throat_area <= 0:
            return None

        result = chamber_volume / throat_area
        return result if _finite(result) and result > 0 else None

    elif mass_flow_rate is not None and estimated_residence_time is not None and chamber_pressure is not None and throat_area is not None:
        if chamber_temperature is None or mach_number is None or R is None:
            return None

        if not _finite(
            mass_flow_rate,
            estimated_residence_time,
            chamber_pressure,
            throat_area,
            chamber_temperature,
            mach_number,
            R,
        ):
            return None

        if (
            mass_flow_rate <= 0
            or estimated_residence_time <= 0
            or chamber_pressure <= 0
            or throat_area <= 0
            or chamber_temperature <= 0
            or mach_number <= 0
            or R <= 0
        ):
            return None

        term1 = mass_flow_rate * estimated_residence_time * R * chamber_temperature
        term2 = chamber_pressure * mach_number * throat_area
        result = term1 / term2
        return result if _finite(result) and result > 0 else None

    return None

def calculate_characteristic_velocity(
        mass_flow_rate=None,
        chamber_temperature=None,
        throat_area=None,
        chamber_pressure=None,
        Gamma=None,
        R=None
):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if (
        mass_flow_rate is not None
        and throat_area is not None
        and chamber_pressure is not None
    ):
        if not _finite(mass_flow_rate, throat_area, chamber_pressure):
            return None
        if mass_flow_rate <= 0 or throat_area <= 0 or chamber_pressure <= 0:
            return None

        denominator = mass_flow_rate
        result = (chamber_pressure * throat_area) / denominator
        return result if _finite(result) and result > 0 else None

    elif (
        chamber_temperature is not None
        and Gamma is not None
        and R is not None
    ):
        if not _finite(chamber_temperature, Gamma, R):
            return None
        if chamber_temperature <= 0 or Gamma <= 1 or R <= 0:
            return None

        term1 = math.sqrt(R * chamber_temperature)

        term2 = Gamma * (
            (2 / (Gamma + 1))
            ** ((Gamma + 1) / (2 * (Gamma - 1)))
        )

        if not _finite(term2) or term2 == 0:
            return None

        result = term1 / term2
        return result if _finite(result) and result > 0 else None

    return None

def calculate_exhaust_velocity(
        chamber_temperature=None,
        chamber_pressure=None,
        exit_pressure=None,
        mach_number=None,
        Gamma=None,
        R=None
):
    """
    Calculates ideal nozzle exit velocity.

    Preferred:
        Use exit Mach and exit static temperature.

    Fallback:
        Use chamber pressure / exit pressure energy equation.
    """

    if (
        chamber_temperature is not None
        and mach_number is not None
        and Gamma is not None
        and R is not None
    ):
        static_temperature = chamber_temperature / (
            1 + ((Gamma - 1) / 2) * mach_number ** 2
        )

        speed_of_sound = math.sqrt(Gamma * R * static_temperature)

        return mach_number * speed_of_sound

    if (
        chamber_temperature is not None
        and chamber_pressure is not None
        and exit_pressure is not None
        and Gamma is not None
        and R is not None
    ):
        if chamber_pressure <= 0 or exit_pressure <= 0:
            return None

        pressure_ratio = exit_pressure / chamber_pressure

        term1 = (2 * Gamma / (Gamma - 1)) * R * chamber_temperature
        term2 = 1 - pressure_ratio ** ((Gamma - 1) / Gamma)

        if term2 <= 0:
            return None

        return math.sqrt(term1 * term2)

    return None

def calculate_mach_number(
        chamber_pressure=None,
        ambient_pressure=None,
        expansion_ratio=None,
        Gamma=None
):
    """
    Calculates nozzle exit Mach number.

    Preferred method:
        Use expansion ratio through the area-Mach relation.

    Fallback method:
        Use chamber pressure / ambient pressure relation.
    """

    if Gamma is not None and expansion_ratio is not None:
        def area_mach_relation(mach):
            term1 = 1 / mach
            term2 = (
                (2 / (Gamma + 1))
                * (1 + ((Gamma - 1) / 2) * mach ** 2)
            ) ** ((Gamma + 1) / (2 * (Gamma - 1)))

            return term1 * term2 - expansion_ratio

        try:
            return brentq(area_mach_relation, 1.01, 20)
        except ValueError:
            return None

    if chamber_pressure is not None and Gamma is not None:
        if ambient_pressure is None:
            ambient_pressure = Ambient_Pressure

        if ambient_pressure <= 0:
            return None

        term1 = 2 / (Gamma - 1)
        term2 = ((chamber_pressure / ambient_pressure) ** ((Gamma - 1) / Gamma)) - 1

        if term2 <= 0:
            return None

        return math.sqrt(term1 * term2)

    return None

def calculate_selected_mach_number(
        Gamma=None,
        selected_expansion_ratio=None,
        branch="supersonic",
):
    """
    Solve the isentropic area-Mach relation on an explicit branch.

    Existing callers preserve historical behaviour because the default
    branch remains supersonic.

    branch="subsonic":
        0 < M < 1

    branch="supersonic":
        M > 1

    A/A* = 1 is the sonic throat boundary and returns M = 1 exactly.
    """

    if (
        Gamma is None
        or selected_expansion_ratio is None
    ):
        return None

    try:
        gamma = float(Gamma)
        area_ratio = float(
            selected_expansion_ratio
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    if (
        not math.isfinite(gamma)
        or
        not math.isfinite(area_ratio)
        or
        gamma <= 1.0
        or
        area_ratio < 1.0
    ):
        return None

    if abs(
        area_ratio - 1.0
    ) <= 1.0e-12:
        return 1.0

    selected_branch = str(
        branch
        or
        "supersonic"
    ).strip().lower()

    if selected_branch not in {
        "subsonic",
        "supersonic",
    }:
        return None

    def area_mach_relation(mach):
        term1 = 1.0 / mach

        term2 = (
            (
                2.0
                /
                (gamma + 1.0)
            )
            *
            (
                1.0
                +
                (
                    (gamma - 1.0)
                    /
                    2.0
                )
                *
                mach ** 2
            )
        ) ** (
            (gamma + 1.0)
            /
            (
                2.0
                *
                (gamma - 1.0)
            )
        )

        return (
            term1
            *
            term2
            -
            area_ratio
        )

    try:
        if (
            selected_branch
            ==
            "subsonic"
        ):
            return brentq(
                area_mach_relation,
                1.0e-8,
                1.0 - 1.0e-8,
            )

        return brentq(
            area_mach_relation,
            1.0 + 1.0e-8,
            10.0,
        )

    except ValueError:
        print(
            "Error: No valid "
            f"{selected_branch} "
            "Mach number found for "
            "given area ratio."
        )

        return None


def calculate_adiabatic_wall_temperature(
        Gamma=None,
        Prandtl=None,
        cea_selected_prandtl=None,
        chamber_temperature=None,
        selected_mach_number=None
):
    """
    Adiabatic-wall / recovery temperature using the turbulent
    boundary-layer recovery-factor approximation.

    Effective recovery factor:
        r = Pr^(1/3)

    The CEA-selected Prandtl number retains precedence over the
    fallback Prandtl input when supplied.

    The present owner models turbulent recovery only; laminar
    Pr^(1/2) recovery is not represented by this function.
    """

    pr = (
        cea_selected_prandtl
        if cea_selected_prandtl is not None
        else Prandtl
    )

    if (
        Gamma is None
        or pr is None
        or chamber_temperature is None
        or selected_mach_number is None
    ):
        return None

    try:
        gamma = float(
            Gamma
        )

        effective_prandtl = float(
            pr
        )

        total_temperature = float(
            chamber_temperature
        )

        mach = float(
            selected_mach_number
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            gamma
        )
        or not math.isfinite(
            effective_prandtl
        )
        or not math.isfinite(
            total_temperature
        )
        or not math.isfinite(
            mach
        )
        or gamma <= 1.0
        or effective_prandtl <= 0.0
        or total_temperature <= 0.0
        or mach < 0.0
    ):
        return None

    term1 = (
        1.0
        + (
            effective_prandtl
            ** (
                1.0 / 3.0
            )
        )
        * (
            (
                gamma - 1.0
            )
            / 2.0
        )
        * mach ** 2
    )

    term2 = (
        1.0
        + (
            (
                gamma - 1.0
            )
            / 2.0
        )
        * mach ** 2
    )

    return (
        total_temperature
        * (
            term1
            / term2
        )
    )


# =========================================================
# REGENERATIVE COOLING FOUNDATION
# =========================================================

def calculate_allowable_wall_stress(
        material_yield_strength=None,
        wall_safety_factor=None,
        wall_joint_efficiency=None
):
    """
    Calculates allowable wall stress.

    Equation:
        sigma_allow = Sy * E / FS

    Sy = material yield strength [Pa]
    E  = joint efficiency [-]
    FS = safety factor [-]
    """

    if material_yield_strength is None:
        return None

    if wall_safety_factor is None:
        wall_safety_factor = 2.0

    if wall_joint_efficiency is None:
        wall_joint_efficiency = 1.0

    try:
        yield_strength = float(
            material_yield_strength
        )

        safety_factor = float(
            wall_safety_factor
        )

        joint_efficiency = float(
            wall_joint_efficiency
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            yield_strength
        )
        or not math.isfinite(
            safety_factor
        )
        or not math.isfinite(
            joint_efficiency
        )
        or yield_strength <= 0.0
        or safety_factor <= 0.0
        or joint_efficiency <= 0.0
        or joint_efficiency > 1.0
    ):
        return None

    return (
        yield_strength
        * joint_efficiency
        / safety_factor
    )



def calculate_pressure_required_wall_thickness(
        chamber_pressure=None,
        static_pressure=None,
        throat_radius=None,
        cross_sectional_area=None,
        allowable_wall_stress=None
):
    """
    Thin-wall pressure vessel approximation.

    Preferred local equation:
        tw_pressure = P * r / sigma_allow

    Uses local static pressure if available.
    Falls back to chamber pressure.
    Uses local area-derived radius if available.
    Falls back to throat radius.
    """

    pressure_raw = (
        static_pressure
        if static_pressure is not None
        else chamber_pressure
    )

    if (
        pressure_raw is None
        or allowable_wall_stress is None
    ):
        return None

    try:
        pressure = float(
            pressure_raw
        )

        allowable_stress = float(
            allowable_wall_stress
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            pressure
        )
        or not math.isfinite(
            allowable_stress
        )
        or pressure <= 0.0
        or allowable_stress <= 0.0
    ):
        return None

    if cross_sectional_area is not None:
        try:
            area = float(
                cross_sectional_area
            )

        except (TypeError, ValueError):
            return None

        if (
            not math.isfinite(
                area
            )
            or area <= 0.0
        ):
            return None

        radius = math.sqrt(
            area
            / math.pi
        )

    else:
        if throat_radius is None:
            return None

        try:
            radius = float(
                throat_radius
            )

        except (TypeError, ValueError):
            return None

    if (
        not math.isfinite(
            radius
        )
        or radius <= 0.0
    ):
        return None

    return (
        pressure
        * radius
        / allowable_stress
    )





def _pfq_finite_real(value):
    """
    Return True only for finite real scalar-compatible values.

    PFQ-5 containment authority only.

    This helper deliberately does not enforce positivity,
    non-negativity, engineering ranges, or correlation validity.
    Owner-specific domain guards remain authoritative.
    """
    if value is None:
        return False

    if isinstance(
        value,
        (
            bool,
            str,
            bytes,
            bytearray,
        ),
    ):
        return False

    try:
        numeric_value = float(
            value
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return False

    return math.isfinite(
        numeric_value
    )


def calculate_conduction_required_wall_thickness(
        wall_thermal_conductivity=None,
        hot_gas_side_wall_temperature=None,
        coolant_side_wall_temperature=None,
        hot_gas_heat_flux=None
):
    """
    Diagnostic 1D wall-conduction thickness reconstructed from the
    canonical solved regenerative-cooling thermal state.

    Standard conduction:
        q'' = kw * (Twg - Twc) / tw

    Rearranged:
        tw_conduction = kw * (Twg - Twc) / q''

    Important:
        This value is diagnostic only. It is not an independent
        hot-gas-wall sizing authority.
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_side_wall_temperature,
            hot_gas_heat_flux,
            hot_gas_side_wall_temperature,
            wall_thermal_conductivity,
        )
    ):
        return None


    if (
        wall_thermal_conductivity is None
        or hot_gas_side_wall_temperature is None
        or coolant_side_wall_temperature is None
        or hot_gas_heat_flux is None
        or hot_gas_heat_flux <= 0
    ):
        return None

    delta_t_wall = (
        hot_gas_side_wall_temperature
        - coolant_side_wall_temperature
    )

    if delta_t_wall <= 0:
        return None

    return (
        wall_thermal_conductivity
        * delta_t_wall
        / hot_gas_heat_flux
    )


def calculate_hot_gas_wall_thickness(
        pressure_required_wall_thickness=None,
        conduction_required_wall_thickness=None,
        minimum_wall_thickness=None,
        corrosion_allowance=None,
        coating_thickness=None
):
    """
    Practical first-pass hot-gas wall thickness.

    Important:
    conduction_required_wall_thickness is NOT used for autosizing here.

    Reason:
    The current conduction value is a diagnostic-only 1D conduction estimate.
    It does not include coolant-side convection, so it can produce unrealistic
    wall thicknesses such as 100+ mm.

    Real regen wall sizing should later use:
        1/hg + tw/k + 1/hc

    For now, wall thickness is sized from:
        - pressure-required wall thickness
        - minimum manufacturable wall thickness
        - corrosion allowance
        - coating thickness
    """
    # PFQ-5 fail-closed scalar containment guard.
    # This owner is fallback-producing rather than return-None-producing.
    # Invalid guarded values therefore collapse to their existing None semantics.
    if (
        coating_thickness is not None
        and not _pfq_finite_real(coating_thickness)
    ):
        coating_thickness = None

    if (
        corrosion_allowance is not None
        and not _pfq_finite_real(corrosion_allowance)
    ):
        corrosion_allowance = None

    if (
        minimum_wall_thickness is not None
        and not _pfq_finite_real(minimum_wall_thickness)
    ):
        minimum_wall_thickness = None

    if (
        pressure_required_wall_thickness is not None
        and not _pfq_finite_real(pressure_required_wall_thickness)
    ):
        pressure_required_wall_thickness = None


    _ = conduction_required_wall_thickness

    candidates = []

    if pressure_required_wall_thickness is not None and pressure_required_wall_thickness > 0:
        candidates.append(pressure_required_wall_thickness)

    practical_minimum = 0.0005

    if minimum_wall_thickness is not None and minimum_wall_thickness > 0:
        practical_minimum = max(practical_minimum, minimum_wall_thickness)

    candidates.append(practical_minimum)

    corrosion_allowance = corrosion_allowance or 0.0
    coating_thickness = coating_thickness or 0.0

    return max(candidates) + corrosion_allowance + coating_thickness

def calculate_single_channel_flow_area(
        coolant_channel_width=None,
        coolant_channel_height=None
):
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_channel_height,
            coolant_channel_width,
        )
    ):
        return None

    if (
        coolant_channel_width is None
        or coolant_channel_height is None
        or coolant_channel_width <= 0
        or coolant_channel_height <= 0
    ):
        return None

    return coolant_channel_width * coolant_channel_height


def calculate_total_coolant_flow_area(
        single_channel_flow_area=None,
        number_of_coolant_channels=None
):
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            number_of_coolant_channels,
            single_channel_flow_area,
        )
    ):
        return None

    if (
        single_channel_flow_area is None
        or number_of_coolant_channels is None
        or single_channel_flow_area <= 0
        or number_of_coolant_channels <= 0
    ):
        return None

    return single_channel_flow_area * number_of_coolant_channels


def calculate_coolant_wetted_perimeter(
        coolant_channel_width=None,
        coolant_channel_height=None
):
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_channel_height,
            coolant_channel_width,
        )
    ):
        return None

    if (
        coolant_channel_width is None
        or coolant_channel_height is None
        or coolant_channel_width <= 0
        or coolant_channel_height <= 0
    ):
        return None

    return 2.0 * (coolant_channel_width + coolant_channel_height)


def calculate_coolant_hydraulic_diameter(
        single_channel_flow_area=None,
        coolant_wetted_perimeter=None
):
    """
    Hydraulic diameter:

        Dh = 4A / Pw
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_wetted_perimeter,
            single_channel_flow_area,
        )
    ):
        return None


    if (
        single_channel_flow_area is None
        or coolant_wetted_perimeter is None
        or single_channel_flow_area <= 0
        or coolant_wetted_perimeter <= 0
    ):
        return None

    return 4.0 * single_channel_flow_area / coolant_wetted_perimeter


def calculate_channel_pitch(
        coolant_channel_width=None,
        rib_width=None
):
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_channel_width,
            rib_width,
        )
    ):
        return None

    if (
        coolant_channel_width is None
        or rib_width is None
        or coolant_channel_width <= 0
        or rib_width < 0
    ):
        return None

    return coolant_channel_width + rib_width

def calculate_channel_mid_radius(
        cross_sectional_area=None,
        throat_radius=None,
        coating_thickness=None,
        hot_gas_wall_thickness=None,
        coolant_channel_height=None
):
    """
    Radius at the middle of the coolant channel band.

    This is the correct radius for circumferential pitch checks.
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coating_thickness,
            coolant_channel_height,
            cross_sectional_area,
            hot_gas_wall_thickness,
        )
    ):
        return None


    gas_radius = None

    if cross_sectional_area is not None and cross_sectional_area > 0:
        gas_radius = math.sqrt(cross_sectional_area / math.pi)
    elif throat_radius is not None and throat_radius > 0:
        gas_radius = throat_radius

    if gas_radius is None:
        return None

    coating = coating_thickness if coating_thickness is not None else 0.0
    wall = hot_gas_wall_thickness if hot_gas_wall_thickness is not None else 0.0
    height = coolant_channel_height if coolant_channel_height is not None else 0.0

    return gas_radius + coating + wall + (0.5 * height)


def calculate_circumferential_channel_pitch(
        channel_mid_radius=None,
        number_of_coolant_channels=None
):
    """
    True physical pitch available around the circumference.

    p_actual = 2*pi*Rmid / N
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            channel_mid_radius,
            number_of_coolant_channels,
        )
    ):
        return None


    if (
        channel_mid_radius is None
        or number_of_coolant_channels is None
        or channel_mid_radius <= 0
        or number_of_coolant_channels <= 0
    ):
        return None

    return (2.0 * math.pi * channel_mid_radius) / number_of_coolant_channels


def calculate_effective_rib_width(
        circumferential_channel_pitch=None,
        coolant_channel_width=None
):
    """
    Actual rib width that physically remains after fitting the channel
    into the available circular pitch.
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            circumferential_channel_pitch,
            coolant_channel_width,
        )
    ):
        return None


    if (
        circumferential_channel_pitch is None
        or coolant_channel_width is None
        or circumferential_channel_pitch <= 0
        or coolant_channel_width <= 0
    ):
        return None

    return circumferential_channel_pitch - coolant_channel_width


def calculate_channel_fit_ratio(
        required_channel_pitch=None,
        circumferential_channel_pitch=None
):
    """
    Ratio of actual available pitch to requested pitch.

    1.0 = perfect fit
    below 1.0 = requested channel/rib pair is too wide
    above 1.0 = spare circumference exists
    """

    if (
        required_channel_pitch is None
        or circumferential_channel_pitch is None
        or required_channel_pitch <= 0
        or circumferential_channel_pitch <= 0
    ):
        return None

    return circumferential_channel_pitch / required_channel_pitch


def calculate_channel_geometry_valid(
        effective_rib_width=None,
        requested_rib_width=None,
        channel_fit_ratio=None,
        required_channel_pitch=None,
        circumferential_channel_pitch=None
):
    """
    Returns 1.0 only if the requested channel/rib geometry fits.

    Valid means:
    - effective rib width is positive
    - effective rib width is not smaller than requested rib width
    - available circumferential pitch is at least the requested pitch
    - channel fit ratio is at least 1.0

    channel_fit_ratio = available_pitch / requested_pitch
    """

    if effective_rib_width is None:
        return None

    if effective_rib_width <= 0:
        return 0.0

    if requested_rib_width is not None:
        if effective_rib_width < requested_rib_width:
            return 0.0

    if channel_fit_ratio is not None:
        if channel_fit_ratio < 1.0:
            return 0.0

    if required_channel_pitch is not None and circumferential_channel_pitch is not None:
        if circumferential_channel_pitch < required_channel_pitch:
            return 0.0

    return 1.0

def build_geometry_aware_recommended_regen_design(results):
    """
    Builds recommended regen channel geometry using the active nozzle geometry.

    This does NOT overwrite manual inputs:
    - coolant_channel_width
    - coolant_channel_height
    - rib_width
    - number_of_coolant_channels

    It only writes recommended_* values.
    """

    if results is None:
        return results

    coolant_mdot = (
        results.get("coolant_mass_flow_rate")
        or results.get("fuel_mass_flow_rate")
    )

    coolant_density = results.get("coolant_density") or 810.0
    coolant_viscosity = results.get("coolant_dynamic_viscosity") or 0.0016

    wall = (
        results.get("hot_gas_wall_thickness")
        or results.get("minimum_wall_thickness")
        or 0.001
    )

    coating = results.get("coating_thickness") or 0.0
    jacket = results.get("outer_jacket_thickness") or 0.002

    min_channel_width = results.get("regen_min_channel_width") or 0.00035
    min_rib_width = results.get("regen_min_rib_width") or 0.00035
    min_channel_height = results.get("regen_min_channel_height") or 0.0005
    max_channel_height = results.get("regen_max_channel_height") or 0.004

    max_velocity = results.get("regen_max_coolant_velocity") or 18.0
    target_reynolds = results.get("regen_target_reynolds_number") or 5000.0

    profile = (
        results.get("regen_axial_profile")
        or results.get("rao_nozzle_profile")
        or results.get("conical_nozzle_profile")
    )

    radii = []

    if isinstance(profile, list):
        for station in profile:
            if not isinstance(station, dict):
                continue

            radius = station.get("radius") or station.get("r")

            try:
                radius = float(radius)
            except Exception:
                radius = None

            if radius is not None and radius > 0:
                radii.append(radius)

    if not radii:
        throat_radius = results.get("throat_radius")
        exit_radius = results.get("exit_radius")

        if throat_radius is not None and throat_radius > 0:
            radii.append(throat_radius)

        if exit_radius is not None and exit_radius > 0:
            radii.append(exit_radius)

    if not radii:
        results["recommended_geometry_status"] = "BLOCKED_NO_RADIUS_DATA"
        results["recommended_geometry_valid"] = 0
        results["recommended_geometry_reason"] = (
            "Cannot autosize recommended regen geometry because no nozzle/chamber radius data exists."
        )
        return results

    tightest_gas_radius = min(radii)
    tightest_channel_mid_radius = (
        tightest_gas_radius
        + coating
        + wall
        + 0.5 * min_channel_height
    )

    if tightest_channel_mid_radius <= 0:
        results["recommended_geometry_status"] = "BLOCKED_INVALID_RADIUS"
        results["recommended_geometry_valid"] = 0
        return results

    tightest_circumference = 2.0 * math.pi * tightest_channel_mid_radius

    if coolant_mdot is None or coolant_mdot <= 0:
        results["recommended_geometry_status"] = "BLOCKED_NO_COOLANT_FLOW"
        results["recommended_geometry_valid"] = 0
        results["recommended_geometry_reason"] = (
            "Cannot autosize recommended regen geometry because coolant mass flow is missing."
        )
        return results

    best = None

    min_channel_count = int(results.get("regen_min_channel_count") or 12)
    max_channel_count = int(results.get("regen_max_channel_count") or 240)

    for channel_count in range(min_channel_count, max_channel_count + 1):
        available_pitch = tightest_circumference / channel_count

        if available_pitch <= min_channel_width + min_rib_width:
            continue

        channel_width = available_pitch - min_rib_width

        if channel_width < min_channel_width:
            continue

        channel_width = min(channel_width, results.get("coolant_channel_width") or channel_width)

        rib_width = available_pitch - channel_width

        if rib_width < min_rib_width:
            continue

        for height_step in range(0, 36):
            channel_height = min_channel_height + height_step * 0.0001

            if channel_height > max_channel_height:
                break

            single_area = channel_width * channel_height
            total_area = single_area * channel_count

            if total_area <= 0:
                continue

            velocity = coolant_mdot / max(coolant_density * total_area, 1.0e-12)

            wetted_perimeter = 2.0 * (channel_width + channel_height)
            hydraulic_diameter = 4.0 * single_area / max(wetted_perimeter, 1.0e-12)

            reynolds = (
                coolant_density
                * velocity
                * hydraulic_diameter
                / max(coolant_viscosity, 1.0e-12)
            )

            velocity_ratio = velocity / max(max_velocity, 1.0e-12)
            reynolds_ratio = reynolds / max(target_reynolds, 1.0e-12)

            fit_ratio = available_pitch / max(channel_width + rib_width, 1.0e-12)
            coverage = (
                channel_width * channel_count
            ) / max(tightest_circumference, 1.0e-12)

            velocity_penalty = abs(velocity_ratio - 0.65)
            reynolds_penalty = abs(reynolds_ratio - 1.2)
            coverage_penalty = abs(coverage - 0.65)

            if velocity > max_velocity * 1.05:
                velocity_penalty += 10.0

            if reynolds < 2300:
                reynolds_penalty += 10.0

            score = (
                velocity_penalty * 2.0
                + reynolds_penalty * 2.0
                + coverage_penalty
                + channel_height * 100.0
            )

            candidate = {
                "score": score,
                "channel_count": channel_count,
                "channel_width": channel_width,
                "channel_height": channel_height,
                "rib_width": rib_width,
                "pitch": available_pitch,
                "effective_rib_width": rib_width,
                "fit_ratio": fit_ratio,
                "coverage": coverage,
                "single_channel_area": single_area,
                "total_flow_area": total_area,
                "velocity": velocity,
                "hydraulic_diameter": hydraulic_diameter,
                "reynolds": reynolds,
                "tightest_gas_radius": tightest_gas_radius,
                "tightest_channel_mid_radius": tightest_channel_mid_radius,
            }

            if best is None or candidate["score"] < best["score"]:
                best = candidate

    if best is None:
        results["recommended_geometry_status"] = "FAIL_NO_PHYSICAL_FIT"
        results["recommended_geometry_valid"] = 0
        results["recommended_geometry_reason"] = (
            "No recommended channel geometry could satisfy minimum width and rib limits."
        )
        return results

    recommended_valid = 1.0

    if best["fit_ratio"] < 0.999:
        recommended_valid = 0.0

    if best["effective_rib_width"] < min_rib_width:
        recommended_valid = 0.0

    if best["velocity"] > max_velocity * 1.05:
        recommended_valid = 0.0

    recommended_status = "PASS" if recommended_valid == 1.0 else "WARN_LIMITED"

    if best["reynolds"] < 2300:
        recommended_status = "WARN_LAMINAR_REYNOLDS"

    results["recommended_geometry_status"] = recommended_status
    results["recommended_geometry_valid"] = recommended_valid

    results["recommended_channel_count"] = best["channel_count"]
    results["recommended_number_of_coolant_channels"] = best["channel_count"]

    results["recommended_channel_width"] = best["channel_width"]
    results["recommended_coolant_channel_width"] = best["channel_width"]

    results["recommended_channel_height"] = best["channel_height"]
    results["recommended_coolant_channel_height"] = best["channel_height"]

    results["recommended_rib_width"] = best["rib_width"]
    results["recommended_requested_rib_width"] = min_rib_width
    results["recommended_effective_rib_width"] = best["effective_rib_width"]

    results["recommended_channel_pitch"] = best["pitch"]
    results["recommended_available_circumferential_pitch"] = best["pitch"]
    results["recommended_channel_fit_ratio"] = best["fit_ratio"]
    results["recommended_circumferential_cooling_coverage"] = best["coverage"]
    results["recommended_cooling_coverage"] = best["coverage"]

    results["recommended_single_channel_flow_area"] = best["single_channel_area"]
    results["recommended_total_coolant_flow_area"] = best["total_flow_area"]
    results["recommended_coolant_velocity"] = best["velocity"]
    results["recommended_hydraulic_diameter"] = best["hydraulic_diameter"]
    results["recommended_reynolds_number"] = best["reynolds"]

    results["recommended_tightest_gas_radius"] = best["tightest_gas_radius"]
    results["recommended_tightest_channel_mid_radius"] = best["tightest_channel_mid_radius"]

    reasons = []

    reasons.append(
        "Recommended geometry was autosized from the active nozzle geometry profile."
    )
    reasons.append(
        f"Tightest gas radius used: {best['tightest_gas_radius']:.6g} m."
    )
    reasons.append(
        f"Recommended pitch: {best['pitch']:.6g} m; rib width: {best['rib_width']:.6g} m."
    )

    if best["reynolds"] < 2300:
        reasons.append(
            "Recommended coolant Reynolds number is still laminar; thermal/coolant status may remain FAIL."
        )

    if best["velocity"] > max_velocity:
        reasons.append(
            "Recommended coolant velocity exceeds target but remains within warning allowance."
        )

    results["recommended_geometry_reasons"] = reasons

    return results

def evaluate_full_engine_regen_geometry_gates(
        results,
        geometry_profile_key="velocity_limited_variable_geometry_profile",
        thermal_profile_key="variable_geometry_thermal_profile",
):
    """
    Full-engine honest regen validation gate.

    This checks:
    - geometry fit across all stations
    - coolant Reynolds across all stations
    - coolant velocity across all stations
    - pressure drop
    - thermal wall temperature across all stations
    - material limit

    It must never force PASS.
    """

    if results is None:
        return results

    geometry_profile = results.get(geometry_profile_key)
    thermal_profile = results.get(thermal_profile_key)

    if not isinstance(geometry_profile, list) or not geometry_profile:
        results["full_engine_regen_geometry_status"] = "FAIL_NO_GEOMETRY_PROFILE"
        results["full_engine_regen_geometry_pass"] = 0
        results["full_engine_regen_geometry_reasons"] = [
            f"No geometry profile found for {geometry_profile_key}."
        ]
        return results

    if not isinstance(thermal_profile, list) or not thermal_profile:
        thermal_profile = []

    target_reynolds = (
            results.get("derived_target_reynolds_number")
            or results.get("regen_target_reynolds_number")
            or results.get("regen_derived_target_reynolds_number")
            or 5000.0
    )

    minimum_turbulent_reynolds = (
            results.get("regen_minimum_turbulent_reynolds_number")
            or 2300.0
    )

    max_velocity = (
        results.get("derived_max_coolant_velocity")
        or results.get("regen_derived_maximum_coolant_velocity")
        or results.get("regen_max_coolant_velocity")
        or 20.0
    )

    material_limit = (
        results.get("material_max_wall_temperature")
        or results.get("effective_material_temperature_limit")
    )

    pressure_drop_limit = (
        results.get("derived_pressure_drop_limit")
        or results.get("regen_derived_pressure_drop_limit")
        or results.get("regen_pressure_drop_limit")
    )

    def nearest_thermal_station(geometry_station, index):
        if not thermal_profile:
            return None

        gx = geometry_station.get("x")

        if gx is not None:
            try:
                gx = float(gx)
                return min(
                    thermal_profile,
                    key=lambda station: abs(float(station.get("x", 0.0)) - gx)
                )
            except Exception:
                pass

        if index < len(thermal_profile):
            return thermal_profile[index]

        return None

    failed_fit = []
    failed_reynolds = []
    below_target_reynolds = []
    failed_velocity = []
    failed_thermal = []
    failed_missing = []

    min_reynolds = None
    max_velocity_seen = None
    max_hot_wall = None
    max_pressure_drop = None
    station_rows = []

    for index, geometry_station in enumerate(geometry_profile):
        if not isinstance(geometry_station, dict):
            failed_missing.append((index, None, "Geometry station is not a dict"))
            continue

        thermal_station = nearest_thermal_station(geometry_station, index)

        station_label = geometry_station.get("station_label", f"Station {index:03d}")
        x = geometry_station.get("x")

        fit_valid = (
            geometry_station.get("safe_variable_geometry_valid")
            or geometry_station.get("variable_geometry_valid")
            or geometry_station.get("channel_geometry_valid")
        )

        reynolds = (
            geometry_station.get("safe_variable_reynolds_number")
            or geometry_station.get("variable_reynolds_number")
            or geometry_station.get("coolant_reynolds_number")
        )

        velocity = (
            geometry_station.get("safe_variable_coolant_velocity")
            or geometry_station.get("variable_coolant_velocity")
            or geometry_station.get("coolant_velocity")
        )

        pressure_drop = (
            geometry_station.get("pressure_drop_total")
            or geometry_station.get("coolant_pressure_drop_total")
            or geometry_station.get("delta_p_total")
        )

        hot_wall = None

        if isinstance(thermal_station, dict):
            hot_wall = (
                thermal_station.get("variable_thermal_hot_wall_temperature")
                or thermal_station.get("hot_gas_side_wall_temperature")
                or thermal_station.get("coupled_split_hot_wall_temperature")
                or thermal_station.get("explicit_coating_liner_liner_temperature")
            )

        try:
            fit_valid_f = float(fit_valid)
        except Exception:
            fit_valid_f = None

        try:
            reynolds_f = float(reynolds)
        except Exception:
            reynolds_f = None

        try:
            velocity_f = float(velocity)
        except Exception:
            velocity_f = None

        try:
            pressure_drop_f = float(pressure_drop)
        except Exception:
            pressure_drop_f = None

        try:
            hot_wall_f = float(hot_wall)
        except Exception:
            hot_wall_f = None

        failure_reasons = []

        if fit_valid_f != 1.0:
            failure_reasons.append("Geometry fit failed.")

        if reynolds_f is None:
            failure_reasons.append("Missing Reynolds number.")
        elif reynolds_f < minimum_turbulent_reynolds:
            failure_reasons.append("Reynolds number below turbulent threshold.")
        elif reynolds_f < target_reynolds:
            failure_reasons.append("Reynolds number below target.")

        if velocity_f is None:
            failure_reasons.append("Missing coolant velocity.")
        elif velocity_f > max_velocity:
            failure_reasons.append("Coolant velocity exceeds limit.")

        if hot_wall_f is None:
            failure_reasons.append("Missing hot-wall temperature.")
        elif material_limit is not None and hot_wall_f > material_limit:
            failure_reasons.append("Hot-wall temperature exceeds material limit.")

        if pressure_drop_f is not None and pressure_drop_limit is not None:
            if pressure_drop_f > pressure_drop_limit:
                failure_reasons.append("Pressure drop exceeds limit.")

        station_rows.append({
            "station_index": index,
            "station_label": station_label,
            "x": x,

            "channel_geometry_valid": fit_valid_f,
            "coolant_reynolds_number": reynolds_f,
            "coolant_velocity": velocity_f,
            "coolant_pressure_drop": pressure_drop_f,
            "hot_gas_side_wall_temperature": hot_wall_f,

            "failure_reason": "; ".join(failure_reasons) if failure_reasons else "",
            "diagnostic_note": "PASS" if not failure_reasons else "CHECK",
        })

        if fit_valid_f != 1.0:
            failed_fit.append((station_label, x, fit_valid))

        if reynolds_f is None:
            failed_missing.append((station_label, x, "Reynolds missing"))
        else:
            min_reynolds = reynolds_f if min_reynolds is None else min(min_reynolds, reynolds_f)

            if reynolds_f < minimum_turbulent_reynolds:
                failed_reynolds.append((station_label, x, reynolds_f))
            elif reynolds_f < target_reynolds:
                below_target_reynolds.append((station_label, x, reynolds_f))

        if velocity_f is None:
            failed_missing.append((station_label, x, "Velocity missing"))
        else:
            max_velocity_seen = velocity_f if max_velocity_seen is None else max(max_velocity_seen, velocity_f)

            if velocity_f > max_velocity:
                failed_velocity.append((station_label, x, velocity_f))

        if hot_wall_f is None:
            failed_missing.append((station_label, x, "Thermal wall temperature missing"))
        else:
            max_hot_wall = hot_wall_f if max_hot_wall is None else max(max_hot_wall, hot_wall_f)

            if material_limit is not None and hot_wall_f > material_limit:
                failed_thermal.append((station_label, x, hot_wall_f))

        if pressure_drop_f is not None:
            max_pressure_drop = (
                pressure_drop_f
                if max_pressure_drop is None
                else max(max_pressure_drop, pressure_drop_f)
            )

    pressure_drop_pass = True

    if pressure_drop_limit is not None and max_pressure_drop is not None:
        pressure_drop_pass = max_pressure_drop <= pressure_drop_limit

    hard_failure_count = (
        len(failed_fit)
        + len(failed_reynolds)
        + len(failed_velocity)
        + len(failed_thermal)
        + (0 if pressure_drop_pass else 1)
    )

    if hard_failure_count == 0 and not failed_missing:
        status = "PASS"
        passed = 1
    elif hard_failure_count == 0 and failed_missing:
        status = "FAIL_MISSING_DATA"
        passed = 0
    else:
        status = "FAIL"
        passed = 0

    reasons = []

    if failed_fit:
        reasons.append(f"{len(failed_fit)} station(s) failed geometry fit.")

    if failed_reynolds:
        reasons.append(
            f"{len(failed_reynolds)} station(s) failed minimum turbulent Reynolds limit."
        )

    if below_target_reynolds:
        reasons.append(
            f"{len(below_target_reynolds)} station(s) are below the preferred Reynolds target but above the hard turbulent floor."
        )

    if failed_velocity:
        reasons.append(f"{len(failed_velocity)} station(s) exceeded coolant velocity limit.")

    if failed_thermal:
        reasons.append(f"{len(failed_thermal)} station(s) exceeded material wall-temperature limit.")

    if not pressure_drop_pass:
        reasons.append("Total pressure drop exceeded pressure-drop limit.")

    if failed_missing:
        reasons.append(f"{len(failed_missing)} station item(s) had missing data.")

    if not reasons:
        reasons.append("All full-engine regen gates passed.")

    results["full_engine_regen_geometry_status"] = status
    results["full_engine_regen_geometry_pass"] = passed

    results["full_engine_regen_geometry_profile_key"] = geometry_profile_key
    results["full_engine_regen_thermal_profile_key"] = thermal_profile_key
    results["full_engine_regen_geometry_station_count"] = len(geometry_profile)

    results["full_engine_regen_failed_fit_count"] = len(failed_fit)
    results["full_engine_regen_failed_reynolds_count"] = len(failed_reynolds)
    results["full_engine_regen_below_target_reynolds_count"] = len(below_target_reynolds)
    results["full_engine_regen_target_reynolds"] = target_reynolds
    results["full_engine_regen_minimum_turbulent_reynolds"] = minimum_turbulent_reynolds
    results["full_engine_regen_failed_velocity_count"] = len(failed_velocity)
    results["full_engine_regen_failed_thermal_count"] = len(failed_thermal)
    results["full_engine_regen_missing_data_count"] = len(failed_missing)

    results["full_engine_regen_min_reynolds"] = min_reynolds
    results["full_engine_regen_max_velocity"] = max_velocity_seen
    results["full_engine_regen_max_hot_wall_temperature"] = max_hot_wall
    results["full_engine_regen_max_pressure_drop"] = max_pressure_drop

    results["full_engine_regen_pressure_drop_limit"] = pressure_drop_limit
    results["full_engine_regen_pressure_drop_pass"] = 1 if pressure_drop_pass else 0

    results["full_engine_regen_geometry_reasons"] = reasons
    results["regen_station_rows"] = station_rows

    return results

def classify_full_engine_regen_design(
        results,
        design_name,
        geometry_profile_key,
        thermal_profile_key,
):
    """
    Evaluates one full-engine regen candidate without overwriting
    the main full-engine gate result.

    This lets LEAF compare available designs while still refusing
    to fake a PASS.
    """

    if results is None:
        return None

    geometry_profile = results.get(geometry_profile_key)

    if not isinstance(geometry_profile, list) or not geometry_profile:
        return None

    scratch = dict(results)

    scratch = evaluate_full_engine_regen_geometry_gates(
        scratch,
        geometry_profile_key=geometry_profile_key,
        thermal_profile_key=thermal_profile_key,
    )

    failed_fit = scratch.get("full_engine_regen_failed_fit_count") or 0
    failed_re = scratch.get("full_engine_regen_failed_reynolds_count") or 0
    below_target_re = scratch.get("full_engine_regen_below_target_reynolds_count") or 0
    failed_velocity = scratch.get("full_engine_regen_failed_velocity_count") or 0
    failed_thermal = scratch.get("full_engine_regen_failed_thermal_count") or 0
    missing = scratch.get("full_engine_regen_missing_data_count") or 0

    min_re = scratch.get("full_engine_regen_min_reynolds")
    max_velocity = scratch.get("full_engine_regen_max_velocity")
    max_twg = scratch.get("full_engine_regen_max_hot_wall_temperature")
    max_dp = scratch.get("full_engine_regen_max_pressure_drop")

    material_limit = (
        results.get("material_max_wall_temperature")
        or results.get("effective_material_temperature_limit")
    )

    thermal_margin = None

    if max_twg is not None and material_limit is not None:
        thermal_margin = material_limit - max_twg

    hard_fail_count = (
        failed_fit
        + failed_re
        + failed_velocity
        + failed_thermal
        + missing
    )

    score = 0.0

    # Hard failures dominate the score.
    score += failed_fit * 100000.0
    score += missing * 100000.0
    score += failed_re * 50000.0
    score += failed_velocity * 25000.0
    score += failed_thermal * 10000.0

    # Below-target Reynolds is a warning, not a hard fail.
    score += below_target_re * 500.0

    if thermal_margin is not None and thermal_margin < 0:
        score += abs(thermal_margin) * 10.0

    if min_re is not None:
        if min_re < 2300.0:
            score += (2300.0 - min_re) * 20.0
        elif min_re < 5000.0:
            score += (5000.0 - min_re) * 2.0

    return {
        "design_name": design_name,
        "geometry_profile_key": geometry_profile_key,
        "thermal_profile_key": thermal_profile_key,
        "status": scratch.get("full_engine_regen_geometry_status"),
        "passed": scratch.get("full_engine_regen_geometry_pass"),
        "score": score,
        "hard_fail_count": hard_fail_count,
        "failed_fit_count": failed_fit,
        "failed_reynolds_count": failed_re,
        "below_target_reynolds_count": below_target_re,
        "failed_velocity_count": failed_velocity,
        "failed_thermal_count": failed_thermal,
        "missing_data_count": missing,
        "min_reynolds": min_re,
        "max_velocity": max_velocity,
        "max_hot_wall_temperature": max_twg,
        "thermal_margin": thermal_margin,
        "max_pressure_drop": max_dp,
        "reasons": scratch.get("full_engine_regen_geometry_reasons", []),
    }


def select_best_full_engine_regen_design(results):
    """
    Selects the best available full-engine regen design.

    This function can select a best failing design, but it never converts
    a failing design into PASS.
    """

    if results is None:
        return results

    candidate_specs = [
        (
            "Velocity-Limited Variable Geometry",
            "velocity_limited_variable_geometry_profile",
            "variable_geometry_thermal_profile",
        ),
        (
            "Variable Geometry",
            "variable_channel_geometry_profile",
            "variable_geometry_thermal_profile",
        ),
        (
            "Recommended Geometry Thermal Preview",
            "recommended_regen_axial_profile",
            "recommended_regen_axial_profile",
        ),
        (
            "Base Manual Regen Axial Profile",
            "regen_axial_profile",
            "regen_axial_profile",
        ),
    ]

    candidates = []

    for design_name, geometry_key, thermal_key in candidate_specs:
        candidate = classify_full_engine_regen_design(
            results=results,
            design_name=design_name,
            geometry_profile_key=geometry_key,
            thermal_profile_key=thermal_key,
        )

        if candidate is not None:
            candidates.append(candidate)

    if not candidates:
        results["best_full_engine_regen_status"] = "FAIL_NO_CANDIDATES"
        results["best_full_engine_regen_pass"] = 0
        results["best_full_engine_regen_design"] = None
        results["best_full_engine_regen_reason"] = (
            "No full-engine regen design candidates were available."
        )
        return results

    candidates.sort(key=lambda item: item.get("score", 1.0e99))
    best = candidates[0]

    hard_pass = (
        best.get("failed_fit_count", 0) == 0
        and best.get("failed_reynolds_count", 0) == 0
        and best.get("failed_velocity_count", 0) == 0
        and best.get("failed_thermal_count", 0) == 0
        and best.get("missing_data_count", 0) == 0
    )

    if hard_pass:
        status = "PASS"
        pass_flag = 1
    else:
        status = "FAIL_BEST_AVAILABLE"
        pass_flag = 0

    results["best_full_engine_regen_status"] = status
    results["best_full_engine_regen_pass"] = pass_flag
    results["best_full_engine_regen_design"] = best.get("design_name")
    results["best_full_engine_regen_score"] = best.get("score")

    results["best_full_engine_regen_failed_fit_count"] = best.get("failed_fit_count")
    results["best_full_engine_regen_failed_reynolds_count"] = best.get("failed_reynolds_count")
    results["best_full_engine_regen_below_target_reynolds_count"] = best.get("below_target_reynolds_count")
    results["best_full_engine_regen_failed_velocity_count"] = best.get("failed_velocity_count")
    results["best_full_engine_regen_failed_thermal_count"] = best.get("failed_thermal_count")
    results["best_full_engine_regen_missing_data_count"] = best.get("missing_data_count")

    results["best_full_engine_regen_min_reynolds"] = best.get("min_reynolds")
    results["best_full_engine_regen_max_velocity"] = best.get("max_velocity")
    results["best_full_engine_regen_max_hot_wall_temperature"] = best.get("max_hot_wall_temperature")
    results["best_full_engine_regen_thermal_margin"] = best.get("thermal_margin")
    results["best_full_engine_regen_max_pressure_drop"] = best.get("max_pressure_drop")

    results["best_full_engine_regen_candidates"] = candidates

    if pass_flag:
        reason = "Best full-engine regen design passes all hard gates."
    else:
        reason = (
            f"Best available design is {best.get('design_name')}, but it still fails: "
            f"fit={best.get('failed_fit_count')}, "
            f"hard_Re={best.get('failed_reynolds_count')}, "
            f"below_target_Re={best.get('below_target_reynolds_count')}, "
            f"velocity={best.get('failed_velocity_count')}, "
            f"thermal={best.get('failed_thermal_count')}, "
            f"missing={best.get('missing_data_count')}."
        )

    results["best_full_engine_regen_reason"] = reason

    return results

def clamp_value(value, minimum=None, maximum=None):
    if value is None:
        return None

    if minimum is not None:
        value = max(value, minimum)

    if maximum is not None:
        value = min(value, maximum)

    return value

def repair_variable_channel_station_geometry(
    *,
    circumference,
    local_channel_count,
    local_channel_width,
    local_channel_height,
    min_channel_width,
    min_rib_width,
    max_channel_height,
    max_velocity,
    coolant_mdot,
    coolant_density,
    max_channel_count,
):
    """
    Repairs one variable-channel station so it physically fits.

    Priority:
    1. Preserve fit.
    2. Keep velocity below max.
    3. Avoid impossible rib collapse.
    """

    local_channel_count = max(1, int(local_channel_count))

    for _ in range(80):
        available_pitch = circumference / max(local_channel_count, 1)

        local_channel_width = min(local_channel_width, available_pitch - min_rib_width)
        local_channel_width = max(min_channel_width, local_channel_width)

        local_rib_width = available_pitch - local_channel_width

        if local_rib_width < min_rib_width:
            local_rib_width = min_rib_width
            local_channel_width = available_pitch - local_rib_width

        if local_channel_width < min_channel_width:
            if local_channel_count > 1:
                local_channel_count -= 1
                continue
            local_channel_width = min_channel_width

        local_channel_height = max(min_channel_width, local_channel_height)
        local_channel_height = min(local_channel_height, max_channel_height)
        local_channel_height = min(local_channel_height, local_channel_width * 2.5)

        single_area = local_channel_width * local_channel_height
        total_area = single_area * local_channel_count

        velocity = coolant_mdot / max(coolant_density * total_area, 1e-12)

        if velocity <= max_velocity:
            break

        # First try increasing height.
        required_total_area = coolant_mdot / max(coolant_density * max_velocity, 1e-12)
        required_single_area = required_total_area / max(local_channel_count, 1)
        required_height = required_single_area / max(local_channel_width, 1e-12)

        if required_height <= max_channel_height and required_height <= local_channel_width * 2.5:
            local_channel_height = max(local_channel_height, required_height)
            break

        # If height cannot fix velocity, try increasing channel count.
        if local_channel_count < max_channel_count:
            local_channel_count += 1
        else:
            # Last-resort: accept lower velocity target failure but preserve physical fit.
            break
    available_pitch = circumference / max(local_channel_count, 1)

    local_channel_width = min(local_channel_width, available_pitch - min_rib_width)
    local_channel_width = max(min_channel_width, local_channel_width)

    local_rib_width = available_pitch - local_channel_width

    local_channel_height = max(min_channel_width, local_channel_height)
    local_channel_height = min(local_channel_height, max_channel_height)
    local_channel_height = min(local_channel_height, local_channel_width * 2.5)

    single_area = local_channel_width * local_channel_height
    total_area = single_area * local_channel_count
    velocity = coolant_mdot / max(coolant_density * total_area, 1e-12)

    geometry_valid = 1.0

    if local_channel_width < min_channel_width:
        geometry_valid = 0.0

    if local_rib_width < min_rib_width:
        geometry_valid = 0.0

    if local_channel_height <= 0 or local_channel_height > max_channel_height:
        geometry_valid = 0.0

    if local_channel_width + local_rib_width > available_pitch * 1.0001:
        geometry_valid = 0.0

    # Velocity failure is now tracked separately.
    # Do not mark geometry physically invalid purely because velocity is high.
    # Geometry validity should mean "does it fit".
    if velocity > max_velocity * 1.05:
        pass

    return {
        "channel_count": local_channel_count,
        "channel_width": local_channel_width,
        "channel_height": local_channel_height,
        "rib_width": local_rib_width,
        "pitch": available_pitch,
        "single_area": single_area,
        "total_area": total_area,
        "velocity": velocity,
        "geometry_valid": geometry_valid,
        "velocity_valid": 1.0 if velocity <= max_velocity * 1.05 else 0.0,
    }

def build_variable_channel_geometry_profile(results):
    """
    Builds a first-pass variable channel geometry profile.

    This version starts from the recommended constant geometry and only modifies
    it locally. That prevents the variable optimiser from accidentally becoming
    worse everywhere.
    """

    if results is None:
        return results

    profile = results.get("recommended_regen_axial_profile") or results.get("regen_axial_profile")

    if not profile:
        results["variable_channel_geometry_status"] = "NO_AXIAL_PROFILE"
        return results

    min_channel_width = results.get("regen_derived_min_channel_width") or 0.00025
    min_rib_width = results.get("regen_derived_min_rib_width") or 0.00025
    max_channel_height = results.get("regen_derived_max_channel_height") or 0.004
    min_channel_count = int(results.get("regen_derived_min_channel_count") or 8)
    max_channel_count = int(results.get("regen_derived_max_channel_count") or 300)
    max_velocity = (
            results.get("regen_derived_max_coolant_velocity")
            or results.get("recommended_coolant_velocity", 12.0) * 1.8
            or 25.0
    )
    target_re = results.get("regen_derived_target_reynolds_number") or results.get("regen_target_reynolds_number") or 5000.0

    coolant_mdot = results.get("coolant_mass_flow_rate") or results.get("fuel_mass_flow_rate")
    coolant_density = results.get("coolant_density") or 810.0
    coolant_viscosity = results.get("coolant_dynamic_viscosity") or 0.0016

    if coolant_mdot is None or coolant_mdot <= 0:
        results["variable_channel_geometry_status"] = "NO_COOLANT_MASS_FLOW"
        return results

    if results.get("recommended_geometry_status") in (None, "BLOCKED_NO_RADIUS_DATA", "FAIL_NO_PHYSICAL_FIT"):
        results = build_geometry_aware_recommended_regen_design(results)

    base_channel_count = int(results.get("recommended_channel_count") or min_channel_count)
    base_channel_width = results.get("recommended_channel_width") or min_channel_width
    base_channel_height = results.get("recommended_channel_height") or min_channel_width
    base_rib_width = results.get("recommended_rib_width") or min_rib_width

    heat_flux_values = []

    for station in profile:
        q = station.get("regen_heat_flux") or station.get("heat_flux") or station.get("q")
        try:
            q = float(q)
            if q > 0:
                heat_flux_values.append(q)
        except Exception:
            pass

    if not heat_flux_values:
        results["variable_channel_geometry_status"] = "NO_HEAT_FLUX_DATA"
        return results

    max_heat_flux = max(heat_flux_values)
    min_heat_flux = min(heat_flux_values)

    variable_profile = []

    failed_fit_count = 0
    failed_velocity_count = 0
    fallback_count = 0
    max_required_velocity = None
    min_reynolds = None
    max_reynolds = None
    min_hydraulic_diameter = None
    max_hydraulic_diameter = None

    for station in profile:
        x = station.get("x", 0.0)
        radius = station.get("radius") or station.get("r")
        q = station.get("regen_heat_flux") or station.get("heat_flux") or station.get("q")

        try:
            x = float(x)
        except Exception:
            x = 0.0

        try:
            radius = float(radius)
        except Exception:
            radius = results.get("throat_radius") or 0.01

        try:
            q = float(q)
        except Exception:
            q = max_heat_flux

        if radius <= 0:
            radius = results.get("throat_radius") or 0.01

        heat_load_fraction = (q - min_heat_flux) / max(max_heat_flux - min_heat_flux, 1e-9)
        heat_load_fraction = max(0.0, min(1.0, heat_load_fraction))

        circumference = 2.0 * math.pi * radius

        # Start from recommended channel count.
        # Add only modest extra channels near the throat/high heat-flux region.
        count_multiplier = 1.0 + 0.20 * heat_load_fraction
        local_channel_count = int(round(base_channel_count * count_multiplier))
        local_channel_count = max(min_channel_count, min(max_channel_count, local_channel_count))

        available_pitch = circumference / max(local_channel_count, 1)

        # Start from recommended width, then reduce width near high heat-flux stations.
        width_multiplier = 1.0 - 0.12 * heat_load_fraction
        local_channel_width = base_channel_width * width_multiplier
        local_channel_width = max(min_channel_width, local_channel_width)

        # Prevent width from consuming impossible pitch.
        max_width_from_pitch = max(available_pitch - min_rib_width, min_channel_width)
        local_channel_width = min(local_channel_width, max_width_from_pitch)

        local_rib_width = available_pitch - local_channel_width

        if local_rib_width < min_rib_width:
            local_rib_width = min_rib_width
            local_channel_width = max(min_channel_width, available_pitch - local_rib_width)

        # Keep height close to recommended, slightly larger in lower heat-load regions.
        height_multiplier = 1.0 + 0.35 * (1.0 - heat_load_fraction)
        local_channel_height = base_channel_height * height_multiplier

        # High heat flux: reduce height slightly to reduce hydraulic diameter.
        local_channel_height *= (1.0 - 0.08 * heat_load_fraction)

        local_channel_height = max(min_channel_width, min(max_channel_height, local_channel_height))
        local_channel_height = min(local_channel_height, local_channel_width * 2.0)

        single_area = local_channel_width * local_channel_height
        total_area = single_area * local_channel_count

        repair = repair_variable_channel_station_geometry(
            circumference=circumference,
            local_channel_count=local_channel_count,
            local_channel_width=local_channel_width,
            local_channel_height=local_channel_height,
            min_channel_width=min_channel_width,
            min_rib_width=min_rib_width,
            max_channel_height=max_channel_height,
            max_velocity=max_velocity,
            coolant_mdot=coolant_mdot,
            coolant_density=coolant_density,
            max_channel_count=max_channel_count,
        )

        local_channel_count = repair["channel_count"]
        local_channel_width = repair["channel_width"]
        local_channel_height = repair["channel_height"]
        local_rib_width = repair["rib_width"]
        available_pitch = repair["pitch"]
        single_area = repair["single_area"]
        total_area = repair["total_area"]
        velocity = repair["velocity"]
        geometry_valid = repair["geometry_valid"]
        velocity_valid = repair["velocity_valid"]

        if geometry_valid == 0.0:
            local_channel_count = base_channel_count
            local_channel_width = base_channel_width
            local_channel_height = base_channel_height
            local_rib_width = base_rib_width

            available_pitch = circumference / max(local_channel_count, 1)

            if local_channel_width + local_rib_width > available_pitch:
                local_rib_width = max(min_rib_width, available_pitch - local_channel_width)

            single_area = local_channel_width * local_channel_height
            total_area = single_area * local_channel_count
            velocity = coolant_mdot / max(coolant_density * total_area, 1e-12)

            wetted_perimeter = 2.0 * (local_channel_width + local_channel_height)
            hydraulic_diameter = 4.0 * single_area / max(wetted_perimeter, 1e-12)

            reynolds = coolant_density * velocity * hydraulic_diameter / max(coolant_viscosity, 1e-12)

            geometry_valid = 1.0
            velocity_valid = 1.0 if velocity <= max_velocity * 1.05 else 0.0
            used_recommended_fallback = 1.0
        else:
            used_recommended_fallback = 0.0

        wetted_perimeter = 2.0 * (local_channel_width + local_channel_height)
        hydraulic_diameter = 4.0 * single_area / max(wetted_perimeter, 1e-12)

        reynolds = coolant_density * velocity * hydraulic_diameter / max(coolant_viscosity, 1e-12)

        geometry_valid = min(geometry_valid, 1.0)

        # Final fit-only validation.
        # Geometry validity means "does this channel/rib layout physically fit".
        # Velocity is tracked separately using velocity_valid.
        if local_channel_width + local_rib_width > available_pitch * 1.0001:
            geometry_valid = 0.0

        if local_channel_width <= 0 or local_channel_height <= 0 or local_rib_width <= 0:
            geometry_valid = 0.0

        if local_channel_width < min_channel_width:
            geometry_valid = 0.0

        if local_rib_width < min_rib_width:
            geometry_valid = 0.0

        if local_channel_height > max_channel_height:
            geometry_valid = 0.0

        velocity_valid = 1.0 if velocity <= max_velocity * 1.05 else 0.0

        if geometry_valid == 0.0:
            failed_fit_count += 1

        if velocity_valid == 0.0:
            failed_velocity_count += 1

        if used_recommended_fallback == 1.0:
            fallback_count += 1

        if max_required_velocity is None or velocity > max_required_velocity:
            max_required_velocity = velocity

        if min_reynolds is None or reynolds < min_reynolds:
            min_reynolds = reynolds

        if max_reynolds is None or reynolds > max_reynolds:
            max_reynolds = reynolds

        if min_hydraulic_diameter is None or hydraulic_diameter < min_hydraulic_diameter:
            min_hydraulic_diameter = hydraulic_diameter

        if max_hydraulic_diameter is None or hydraulic_diameter > max_hydraulic_diameter:
            max_hydraulic_diameter = hydraulic_diameter

        variable_profile.append({
            "station_label": station.get("station_label"),
            "station_index": station.get("station_index"),
            "x": x,
            "radius": radius,
            "heat_flux": q,
            "heat_load_fraction": heat_load_fraction,
            "variable_channel_count": local_channel_count,
            "variable_channel_width": local_channel_width,
            "variable_channel_height": local_channel_height,
            "variable_rib_width": local_rib_width,
            "variable_channel_pitch": available_pitch,
            "variable_single_channel_area": single_area,
            "variable_total_flow_area": total_area,
            "variable_coolant_velocity": velocity,
            "variable_hydraulic_diameter": hydraulic_diameter,
            "variable_reynolds_number": reynolds,
            "variable_geometry_valid": geometry_valid,
            "variable_velocity_valid": velocity_valid,
            "variable_geometry_used_recommended_fallback": used_recommended_fallback,
        })

    results["variable_channel_geometry_profile"] = variable_profile
    results["variable_channel_geometry_station_count"] = len(variable_profile)
    results["variable_channel_geometry_failed_station_count"] = failed_fit_count
    results["variable_channel_geometry_valid_station_count"] = (
            len(variable_profile) - failed_fit_count
    )
    results["variable_channel_geometry_min_reynolds_number"] = min_reynolds
    results["variable_channel_geometry_max_reynolds_number"] = max_reynolds
    results["variable_channel_geometry_max_velocity"] = max_required_velocity
    if max_required_velocity is not None and max_velocity is not None and max_velocity > 0:
        results["variable_channel_geometry_velocity_limit_ratio"] = max_required_velocity / max_velocity
    results["variable_channel_geometry_min_hydraulic_diameter"] = min_hydraulic_diameter
    results["variable_channel_geometry_max_hydraulic_diameter"] = max_hydraulic_diameter
    results["variable_channel_geometry_target_reynolds_number"] = target_re
    results["variable_channel_velocity_failed_station_count"] = failed_velocity_count
    results["variable_channel_geometry_fallback_station_count"] = fallback_count

    reynolds_target_ratio = None

    if min_reynolds is not None:
        reynolds_target_ratio = min_reynolds / max(target_re, 1e-9)
        results["variable_channel_geometry_reynolds_target_ratio"] = reynolds_target_ratio

    if failed_fit_count > 0:
        status = "FAIL_GEOMETRY"
    elif failed_velocity_count > 0:
        status = "FAIL_VELOCITY_LIMIT"
    elif reynolds_target_ratio is not None and reynolds_target_ratio < 0.8:
        status = "FAIL_REYNOLDS"
    elif reynolds_target_ratio is not None and reynolds_target_ratio < 1.0:
        status = "MARGINAL_REYNOLDS"
    else:
        status = "PASS"

    results["variable_channel_geometry_status"] = status

    reasons = []
    recommendations = []

    if failed_fit_count > 0:
        reasons.append(f"{failed_fit_count} variable-geometry stations failed physical fit checks.")

    if failed_velocity_count > 0:
        reasons.append(
            f"{failed_velocity_count} variable-geometry stations exceed the coolant velocity limit."
        )
        recommendations.append(
            "Increase total flow area, reduce channel count, increase channel height/width within pitch limits, or raise the allowed pressure-drop/velocity budget."
        )

    if reynolds_target_ratio is not None and reynolds_target_ratio < 1.0:
        reasons.append(
            f"Minimum variable-channel Reynolds number is below target: {min_reynolds:.3g} vs {target_re:.3g}."
        )
        recommendations.append(
            "Increase local coolant velocity, reduce hydraulic diameter, increase channel count near low-Re stations, or allow a higher pressure-drop budget."
        )

    if max_required_velocity is not None and max_required_velocity >= max_velocity:
        recommendations.append(
            "Variable geometry is hitting the maximum coolant velocity constraint; pressure-drop and pump limits should be reviewed."
        )

    if not reasons:
        reasons.append("Variable channel geometry satisfies fit, velocity, and Reynolds checks.")

    if not recommendations:
        recommendations.append("Proceed to variable-geometry thermal preview.")

    results["variable_channel_geometry_reasons"] = reasons
    results["variable_channel_geometry_recommendations"] = recommendations

    return results

def build_velocity_limited_variable_channel_geometry_profile(results):
    """
    Builds a safe variable-channel geometry profile that obeys coolant velocity
    limits.

    This is intentionally conservative:
    - starts from variable geometry if available
    - increases flow area until velocity is acceptable
    - falls back to recommended geometry if needed
    - never marks a station as valid if velocity exceeds the limit
    """

    if results is None:
        return results

    source_profile = results.get("variable_channel_geometry_profile")
    base_profile = results.get("recommended_regen_axial_profile")

    if not source_profile:
        results["velocity_limited_variable_geometry_status"] = "NO_VARIABLE_PROFILE"
        return results

    coolant_mdot = results.get("coolant_mass_flow_rate") or results.get("fuel_mass_flow_rate")
    coolant_density = results.get("coolant_density") or 810.0
    coolant_viscosity = results.get("coolant_dynamic_viscosity") or 0.0016

    max_velocity = (
        results.get("regen_derived_maximum_coolant_velocity")
        or results.get("recommended_coolant_velocity")
        or 12.0
    )

    min_channel_width = results.get("regen_derived_minimum_channel_width") or 0.00025
    min_rib_width = results.get("regen_derived_minimum_rib_width") or 0.00025
    max_channel_height = results.get("regen_derived_maximum_channel_height") or 0.004
    max_channel_count = int(results.get("regen_derived_maximum_channel_count") or 300)

    recommended_count = int(results.get("recommended_channel_count") or 1)
    recommended_width = results.get("recommended_channel_width") or min_channel_width
    recommended_height = results.get("recommended_channel_height") or min_channel_width
    recommended_rib = results.get("recommended_rib_width") or min_rib_width

    if coolant_mdot is None or coolant_mdot <= 0:
        results["velocity_limited_variable_geometry_status"] = "NO_COOLANT_MASS_FLOW"
        return results

    safe_profile = []

    failed_geometry_count = 0
    failed_velocity_count = 0
    fallback_count = 0

    min_re = None
    max_re = None
    max_seen_velocity = None

    for index, station in enumerate(source_profile):
        new_station = dict(station)

        radius = station.get("radius") or station.get("r")

        try:
            radius = float(radius)
        except Exception:
            radius = results.get("throat_radius") or 0.01

        circumference = 2.0 * math.pi * max(radius, 1e-9)

        channel_count = int(station.get("variable_channel_count") or recommended_count)
        width = station.get("variable_channel_width") or recommended_width
        height = station.get("variable_channel_height") or recommended_height
        rib = station.get("variable_rib_width") or recommended_rib

        try:
            width = float(width)
            height = float(height)
            rib = float(rib)
        except Exception:
            width = recommended_width
            height = recommended_height
            rib = recommended_rib

        # First try opening height to reduce velocity.
        for _ in range(80):
            pitch = circumference / max(channel_count, 1)

            width = min(width, pitch - min_rib_width)
            width = max(width, min_channel_width)
            rib = pitch - width

            if rib < min_rib_width:
                rib = min_rib_width
                width = pitch - rib

            if width < min_channel_width:
                if channel_count > 1:
                    channel_count -= 1
                    continue
                width = min_channel_width

            height = max(height, min_channel_width)
            height = min(height, max_channel_height)

            single_area = width * height
            total_area = single_area * channel_count
            velocity = coolant_mdot / max(coolant_density * total_area, 1e-12)

            if velocity <= max_velocity * 1.05:
                break

            required_total_area = coolant_mdot / max(coolant_density * max_velocity, 1e-12)
            required_single_area = required_total_area / max(channel_count, 1)
            required_height = required_single_area / max(width, 1e-12)

            if required_height <= max_channel_height:
                height = required_height
            else:
                # Velocity still too high. Reduce channel count to increase pitch
                # and allow wider channels.
                if channel_count > 1:
                    channel_count -= 1
                    width = min(pitch - min_rib_width, width * 1.05)
                else:
                    break

        pitch = circumference / max(channel_count, 1)
        width = min(width, pitch - min_rib_width)
        width = max(width, min_channel_width)
        rib = pitch - width
        height = max(min_channel_width, min(height, max_channel_height))

        single_area = width * height
        total_area = single_area * channel_count
        velocity = coolant_mdot / max(coolant_density * total_area, 1e-12)

        geometry_valid = 1.0
        velocity_valid = 1.0 if velocity <= max_velocity * 1.05 else 0.0

        if width <= 0 or height <= 0 or rib <= 0:
            geometry_valid = 0.0

        if width < min_channel_width or rib < min_rib_width:
            geometry_valid = 0.0

        if width + rib > pitch * 1.0001:
            geometry_valid = 0.0

        if height > max_channel_height:
            geometry_valid = 0.0

        # Final conservative fallback to recommended geometry.
        if geometry_valid == 0.0 or velocity_valid == 0.0:
            fallback_count += 1

            channel_count = recommended_count
            width = recommended_width
            height = recommended_height
            rib = recommended_rib
            pitch = circumference / max(channel_count, 1)

            single_area = width * height
            total_area = single_area * channel_count
            velocity = coolant_mdot / max(coolant_density * total_area, 1e-12)

            geometry_valid = 1.0
            velocity_valid = 1.0 if velocity <= max_velocity * 1.05 else 0.0

            if width + rib > pitch * 1.0001 or rib < min_rib_width:
                geometry_valid = 0.0

        wetted_perimeter = 2.0 * (width + height)
        hydraulic_diameter = 4.0 * single_area / max(wetted_perimeter, 1e-12)
        reynolds = coolant_density * velocity * hydraulic_diameter / max(coolant_viscosity, 1e-12)

        if geometry_valid == 0.0:
            failed_geometry_count += 1

        if velocity_valid == 0.0:
            failed_velocity_count += 1

        if min_re is None or reynolds < min_re:
            min_re = reynolds

        if max_re is None or reynolds > max_re:
            max_re = reynolds

        if max_seen_velocity is None or velocity > max_seen_velocity:
            max_seen_velocity = velocity

        new_station["safe_variable_channel_count"] = channel_count
        new_station["safe_variable_channel_width"] = width
        new_station["safe_variable_channel_height"] = height
        new_station["safe_variable_rib_width"] = rib
        new_station["safe_variable_channel_pitch"] = pitch
        new_station["safe_variable_total_flow_area"] = total_area
        new_station["safe_variable_hydraulic_diameter"] = hydraulic_diameter
        new_station["safe_variable_coolant_velocity"] = velocity
        new_station["safe_variable_reynolds_number"] = reynolds
        new_station["safe_variable_geometry_valid"] = geometry_valid
        new_station["safe_variable_velocity_valid"] = velocity_valid
        new_station["safe_variable_used_recommended_fallback"] = 1.0 if index < fallback_count else 0.0

        safe_profile.append(new_station)

    results["velocity_limited_variable_geometry_profile"] = safe_profile
    results["velocity_limited_variable_geometry_station_count"] = len(safe_profile)
    results["velocity_limited_variable_geometry_failed_station_count"] = failed_geometry_count
    results["velocity_limited_variable_velocity_failed_station_count"] = failed_velocity_count
    results["velocity_limited_variable_geometry_fallback_station_count"] = fallback_count
    results["velocity_limited_variable_geometry_min_reynolds_number"] = min_re
    results["velocity_limited_variable_geometry_max_reynolds_number"] = max_re
    results["velocity_limited_variable_geometry_max_velocity"] = max_seen_velocity
    results["velocity_limited_variable_geometry_max_allowed_velocity"] = max_velocity

    if max_seen_velocity is not None and max_velocity > 0:
        results["velocity_limited_variable_geometry_velocity_ratio"] = max_seen_velocity / max_velocity

    if failed_geometry_count > 0:
        status = "FAIL_GEOMETRY"
    elif failed_velocity_count > 0:
        status = "FAIL_VELOCITY_LIMIT"
    else:
        status = "PASS"

    results["velocity_limited_variable_geometry_status"] = status

    return results

def build_variable_geometry_thermal_preview(results):
    """
    Conservative thermal preview using variable channel geometry.

    Invalid variable-geometry stations are not allowed to improve the result.
    If a station fails geometry, LEAF falls back to the recommended constant
    geometry thermal result for that station.
    """

    if results is None:
        return results

    base_profile = results.get("recommended_regen_axial_profile")
    variable_profile = (
            results.get("velocity_limited_variable_geometry_profile")
            or results.get("variable_channel_geometry_profile")
    )

    if not base_profile:
        results["variable_geometry_thermal_preview_status"] = "NO_RECOMMENDED_PROFILE"
        return results

    if not variable_profile:
        results["variable_geometry_thermal_preview_status"] = "NO_VARIABLE_PROFILE"
        return results

    material_limit = results.get("material_max_wall_temperature")

    coolant_reference_temperature = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    recovery_temperature_global = (
        results.get("regen_feasibility_reference_recovery_temperature")
        or results.get("chamber_temperature")
        or 3280.0
    )

    if material_limit is None:
        results["variable_geometry_thermal_preview_status"] = "NO_MATERIAL_LIMIT"
        return results

    preview_profile = []

    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None
    failed_station_count = 0

    min_re = None
    max_re = None
    min_h_ratio = None
    max_h_ratio = None

    improved_station_count = 0
    worsened_station_count = 0
    invalid_station_count = 0
    fallback_station_count = 0

    for base_station, var_station in zip(base_profile, variable_profile):
        new_station = dict(base_station)

        x = base_station.get("x", var_station.get("x", 0.0))

        try:
            x = float(x)
        except Exception:
            x = 0.0

        base_twg = (
            base_station.get("hot_gas_side_wall_temperature")
            or base_station.get("Twg")
        )

        base_re = (
            base_station.get("coolant_reynolds_number")
            or results.get("recommended_reynolds_number")
            or results.get("regen_axial_min_reynolds_number")
        )

        var_re = (
                var_station.get("safe_variable_reynolds_number")
                or var_station.get("variable_reynolds_number")
        )

        base_dh = (
            results.get("recommended_hydraulic_diameter")
            or base_station.get("coolant_hydraulic_diameter")
            or 0.001
        )

        var_dh = (
                var_station.get("safe_variable_hydraulic_diameter")
                or var_station.get("variable_hydraulic_diameter")
        )

        recovery_temperature = (
            base_station.get("recovery_temperature")
            or base_station.get("adiabatic_wall_temperature")
            or recovery_temperature_global
        )

        geometry_valid = (
            var_station.get("safe_variable_geometry_valid")
            if var_station.get("safe_variable_geometry_valid") is not None
            else var_station.get("variable_geometry_valid", 0.0)
        )

        try:
            base_twg = float(base_twg)
            base_re = float(base_re)
            var_re = float(var_re)
            base_dh = float(base_dh)
            var_dh = float(var_dh)
            recovery_temperature = float(recovery_temperature)
            geometry_valid = float(geometry_valid)
        except Exception:
            preview_profile.append(new_station)
            continue

        if base_re <= 0 or var_re <= 0 or base_dh <= 0 or var_dh <= 0:
            preview_profile.append(new_station)
            continue

        if geometry_valid < 1.0:
            invalid_station_count += 1
            fallback_station_count += 1

            variable_twg = base_twg
            h_ratio = 1.0
            used_fallback = 1.0

        else:
            h_ratio = (var_re / base_re) ** 0.8 * (base_dh / var_dh)

            # Screening limit.
            h_ratio = max(0.35, min(4.0, h_ratio))

            thermal_gap = base_twg - coolant_reference_temperature

            if thermal_gap > 0:
                candidate_twg = coolant_reference_temperature + thermal_gap / h_ratio
            else:
                candidate_twg = base_twg

            candidate_twg = max(candidate_twg, coolant_reference_temperature)
            candidate_twg = min(candidate_twg, recovery_temperature)

            # Conservative rule:
            # If variable profile is worse than recommended, reject locally.
            if candidate_twg > base_twg:
                variable_twg = base_twg
                h_ratio = 1.0
                used_fallback = 1.0
                fallback_station_count += 1
            else:
                variable_twg = candidate_twg
                used_fallback = 0.0

        margin = material_limit - variable_twg

        new_station.update(var_station)
        new_station["variable_thermal_source_profile"] = (
            "velocity_limited"
            if var_station.get("safe_variable_reynolds_number") is not None
            else "raw_variable"
        )
        new_station["variable_thermal_h_ratio"] = h_ratio
        new_station["variable_thermal_hot_wall_temperature"] = variable_twg
        new_station["variable_thermal_material_margin"] = margin
        new_station["variable_thermal_pass"] = 1.0 if margin >= 0.0 else 0.0
        new_station["variable_thermal_used_recommended_fallback"] = used_fallback

        if variable_twg < base_twg:
            improved_station_count += 1
        elif variable_twg > base_twg:
            worsened_station_count += 1

        if margin < 0.0:
            failed_station_count += 1

        if max_twg is None or variable_twg > max_twg:
            max_twg = variable_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        if min_re is None or var_re < min_re:
            min_re = var_re

        if max_re is None or var_re > max_re:
            max_re = var_re

        if min_h_ratio is None or h_ratio < min_h_ratio:
            min_h_ratio = h_ratio

        if max_h_ratio is None or h_ratio > max_h_ratio:
            max_h_ratio = h_ratio

        preview_profile.append(new_station)

    results["variable_geometry_thermal_profile"] = preview_profile
    results["variable_geometry_thermal_station_count"] = len(preview_profile)
    results["variable_geometry_thermal_max_hot_wall_temperature"] = max_twg
    results["variable_geometry_thermal_max_hot_wall_temperature_location"] = max_twg_location
    results["variable_geometry_thermal_worst_material_margin"] = worst_margin
    results["variable_geometry_thermal_worst_material_margin_location"] = worst_margin_location
    results["variable_geometry_thermal_failed_station_count"] = failed_station_count
    results["variable_geometry_thermal_min_reynolds_number"] = min_re
    results["variable_geometry_thermal_max_reynolds_number"] = max_re
    results["variable_geometry_thermal_min_h_ratio"] = min_h_ratio
    results["variable_geometry_thermal_max_h_ratio"] = max_h_ratio
    results["variable_geometry_thermal_improved_station_count"] = improved_station_count
    results["variable_geometry_thermal_worsened_station_count"] = worsened_station_count
    results["variable_geometry_thermal_invalid_station_count"] = invalid_station_count
    results["variable_geometry_thermal_fallback_station_count"] = fallback_station_count

    if invalid_station_count > 0:
        status = "PARTIAL_INVALID_GEOMETRY"
    elif failed_station_count == 0:
        status = "PASS"
    elif improved_station_count > 0:
        status = "FAIL_BUT_IMPROVED"
    else:
        status = "FAIL"

    results["variable_geometry_thermal_preview_status"] = status

    if invalid_station_count > 0:
        recommendation = (
            "Variable geometry contains invalid stations. Thermal preview uses recommended-geometry fallback at invalid stations."
        )
    elif status == "FAIL_BUT_IMPROVED":
        recommendation = (
            "Variable geometry improves valid stations but still fails material limits."
        )
    elif status == "PASS":
        recommendation = "Variable geometry passes this first-pass thermal preview."
    else:
        recommendation = "Variable geometry does not yet provide acceptable thermal performance."

    results["variable_geometry_thermal_recommendation"] = recommendation

    return results

def build_velocity_limited_combined_thermal_preview(results):
    """
    Applies film + material upgrade to the physically velocity-limited
    variable-geometry thermal preview.
    """

    if results is None:
        return results

    profile = results.get("variable_geometry_thermal_profile")

    if not profile:
        results["velocity_limited_combined_preview_status"] = "NO_VARIABLE_THERMAL_PROFILE"
        return results

    material_limit = results.get("material_max_wall_temperature")
    material_factor = results.get("combined_material_factor_target") or 1.0
    film_initial = results.get("combined_film_effectiveness_target") or 0.0

    coolant_ref = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    nozzle_length = results.get("nozzle_length") or 1.0
    film_decay_length = max(nozzle_length * 0.45, 1e-9)

    if material_limit is None:
        results["velocity_limited_combined_preview_status"] = "NO_MATERIAL_LIMIT"
        return results

    improved_material_limit = material_limit * material_factor

    combined_profile = []
    failed_count = 0
    max_twg = None
    worst_margin = None
    max_twg_location = None
    worst_margin_location = None

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)
        try:
            x = float(x)
        except Exception:
            x = 0.0

        twg = station.get("variable_thermal_hot_wall_temperature")

        try:
            twg = float(twg)
        except Exception:
            combined_profile.append(new_station)
            continue

        local_film = film_initial * math.exp(-x / film_decay_length)
        local_film = max(0.0, min(0.95, local_film))

        film_twg = twg - local_film * (twg - coolant_ref)
        film_twg = max(film_twg, coolant_ref)

        margin = improved_material_limit - film_twg

        new_station["velocity_limited_combined_film_effectiveness"] = local_film
        new_station["velocity_limited_combined_hot_wall_temperature"] = film_twg
        new_station["velocity_limited_combined_material_limit"] = improved_material_limit
        new_station["velocity_limited_combined_material_margin"] = margin
        new_station["velocity_limited_combined_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_count += 1

        if max_twg is None or film_twg > max_twg:
            max_twg = film_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        combined_profile.append(new_station)

    results["velocity_limited_combined_profile"] = combined_profile
    results["velocity_limited_combined_station_count"] = len(combined_profile)
    results["velocity_limited_combined_failed_station_count"] = failed_count
    results["velocity_limited_combined_max_hot_wall_temperature"] = max_twg
    results["velocity_limited_combined_max_hot_wall_temperature_location"] = max_twg_location
    results["velocity_limited_combined_worst_material_margin"] = worst_margin
    results["velocity_limited_combined_worst_material_margin_location"] = worst_margin_location
    results["velocity_limited_combined_material_limit"] = improved_material_limit
    results["velocity_limited_combined_preview_status"] = "PASS" if failed_count == 0 else "FAIL"

    return results

def calculate_velocity_limited_required_improvements(results):
    """
    Calculates what extra improvement is required for the physically grounded
    velocity-limited combined cooling preview to pass.
    """

    if results is None:
        return results

    max_twg = results.get("velocity_limited_combined_max_hot_wall_temperature")
    material_limit = results.get("velocity_limited_combined_material_limit")

    if max_twg is None or material_limit is None:
        results["vl_required_improvement_status"] = "INSUFFICIENT_DATA"
        return results

    try:
        max_twg = float(max_twg)
        material_limit = float(material_limit)
    except Exception:
        results["vl_required_improvement_status"] = "INVALID_DATA"
        return results

    coolant_ref = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    try:
        coolant_ref = float(coolant_ref)
    except Exception:
        coolant_ref = 293.0

    thermal_gap = max(max_twg - coolant_ref, 1e-9)
    allowable_gap = max(material_limit - coolant_ref, 1e-9)

    required_total_factor = thermal_gap / allowable_gap
    required_extra_reduction_fraction = 1.0 - (allowable_gap / thermal_gap)

    required_material_limit = max_twg
    required_material_factor = max_twg / max(results.get("material_max_wall_temperature") or 900.0, 1e-9)

    current_film = results.get("combined_film_effectiveness_target") or 0.0
    extra_film_needed = required_extra_reduction_fraction
    total_film_needed = current_film + extra_film_needed * (1.0 - current_film)

    results["vl_required_improvement_status"] = "PASS" if max_twg <= material_limit else "REQUIRED"
    results["vl_required_temperature_gap"] = max_twg - material_limit
    results["vl_required_total_cooling_factor"] = required_total_factor
    results["vl_required_extra_heat_reduction_fraction"] = required_extra_reduction_fraction
    results["vl_required_material_temperature_limit"] = required_material_limit
    results["vl_required_material_factor"] = required_material_factor
    results["vl_required_additional_film_effectiveness"] = extra_film_needed
    results["vl_required_total_film_effectiveness"] = total_film_needed

    recommendations = []

    if max_twg > material_limit:
        recommendations.append(
            "Physically grounded combined cooling still fails; extra improvement is required."
        )
        recommendations.append(
            "Options: increase material limit, improve film effectiveness, reduce chamber heat load, or reduce chamber pressure/temperature."
        )
    else:
        recommendations.append(
            "Velocity-limited combined cooling passes; no extra improvement required."
        )

    results["vl_required_improvement_recommendations"] = recommendations

    return results

def evaluate_velocity_limited_improvement_options(results):
    """
    Ranks improvement options for closing the remaining velocity-limited
    combined cooling gap.
    """

    if results is None:
        return results

    status = results.get("vl_required_improvement_status")

    if status != "REQUIRED" and not solver_pass(status):
        results["vl_improvement_options_status"] = "INSUFFICIENT_DATA"
        return results

    required_extra_heat_reduction = results.get("vl_required_extra_heat_reduction_fraction")
    required_total_film = results.get("vl_required_total_film_effectiveness")
    required_material_factor = results.get("vl_required_material_factor")
    required_material_limit = results.get("vl_required_material_temperature_limit")

    options = []

    # Option 1: material-only
    if required_material_factor is not None:
        if required_material_factor <= 1.6:
            material_status = "PLAUSIBLE"
            material_score = 80
        elif required_material_factor <= 2.0:
            material_status = "AGGRESSIVE"
            material_score = 55
        else:
            material_status = "UNLIKELY"
            material_score = 20

        options.append({
            "name": "Material capability increase",
            "status": material_status,
            "score": material_score,
            "requirement": f"Material limit must reach {required_material_limit:.3g} K.",
        })

    # Option 2: film-only
    if required_total_film is not None:
        if required_total_film <= 0.35:
            film_status = "PLAUSIBLE"
            film_score = 85
        elif required_total_film <= 0.50:
            film_status = "AGGRESSIVE"
            film_score = 60
        else:
            film_status = "SEVERE"
            film_score = 25

        options.append({
            "name": "Increase film cooling effectiveness",
            "status": film_status,
            "score": film_score,
            "requirement": f"Total film effectiveness must reach {required_total_film:.3f}.",
        })

    # Option 3: heat-load reduction
    if required_extra_heat_reduction is not None:
        if required_extra_heat_reduction <= 0.10:
            heat_status = "PLAUSIBLE"
            heat_score = 80
        elif required_extra_heat_reduction <= 0.25:
            heat_status = "AGGRESSIVE"
            heat_score = 65
        else:
            heat_status = "SEVERE"
            heat_score = 30

        options.append({
            "name": "Reduce chamber/nozzle heat load",
            "status": heat_status,
            "score": heat_score,
            "requirement": f"Additional heat-load reduction required: {required_extra_heat_reduction:.3f}.",
        })

    # Option 4: split strategy
    split_score = 90
    split_status = "RECOMMENDED"
    split_requirement = (
        "Combine modest film improvement, modest heat-load reduction, and material upgrade instead of relying on one extreme change."
    )

    options.append({
        "name": "Split improvement strategy",
        "status": split_status,
        "score": split_score,
        "requirement": split_requirement,
    })

    options.sort(key=lambda item: item.get("score", 0), reverse=True)

    results["vl_improvement_options_status"] = "COMPLETE"
    results["vl_improvement_options"] = options
    results["vl_improvement_best_option"] = options[0] if options else None
    results["vl_improvement_recommendation"] = (
        "Use the split improvement strategy as the next design target."
        if options else "No improvement options could be evaluated."
    )

    return results

def build_velocity_limited_split_strategy_preview(results):
    """
    Applies a balanced split strategy to the velocity-limited combined preview.

    Instead of closing the remaining gap with one extreme change, this applies:
    - modest extra film improvement
    - modest extra heat-load reduction
    - modest material capability increase
    """

    if results is None:
        return results

    profile = results.get("velocity_limited_combined_profile")

    if not profile:
        results["vl_split_strategy_status"] = "NO_VL_COMBINED_PROFILE"
        return results

    base_limit = results.get("velocity_limited_combined_material_limit")
    coolant_ref = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    extra_reduction = results.get("vl_required_extra_heat_reduction_fraction") or 0.0

    # Split the remaining required improvement across several mechanisms.
    split_extra_film = min(0.08, extra_reduction * 0.35)
    split_heat_reduction = min(0.08, extra_reduction * 0.35)
    split_material_factor = 1.0 + min(0.12, extra_reduction * 0.70)

    if base_limit is None:
        results["vl_split_strategy_status"] = "NO_MATERIAL_LIMIT"
        return results

    improved_limit = base_limit * split_material_factor

    split_profile = []
    failed_count = 0
    max_twg = None
    worst_margin = None
    max_twg_location = None
    worst_margin_location = None

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)

        try:
            x = float(x)
        except Exception:
            x = 0.0

        twg = station.get("velocity_limited_combined_hot_wall_temperature")

        try:
            twg = float(twg)
        except Exception:
            split_profile.append(new_station)
            continue

        # Apply modest extra film-like reduction.
        after_extra_film = twg - split_extra_film * (twg - coolant_ref)
        after_extra_film = max(after_extra_film, coolant_ref)

        # Apply modest heat-load reduction to remaining thermal gap.
        final_twg = coolant_ref + (
            (after_extra_film - coolant_ref) * (1.0 - split_heat_reduction)
        )

        margin = improved_limit - final_twg

        new_station["vl_split_extra_film_effectiveness"] = split_extra_film
        new_station["vl_split_heat_load_reduction"] = split_heat_reduction
        new_station["vl_split_material_factor"] = split_material_factor
        new_station["vl_split_material_limit"] = improved_limit
        new_station["vl_split_hot_wall_temperature"] = final_twg
        new_station["vl_split_material_margin"] = margin
        new_station["vl_split_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_count += 1

        if max_twg is None or final_twg > max_twg:
            max_twg = final_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        split_profile.append(new_station)

    results["vl_split_strategy_profile"] = split_profile
    results["vl_split_strategy_station_count"] = len(split_profile)
    results["vl_split_strategy_failed_station_count"] = failed_count
    results["vl_split_strategy_extra_film_effectiveness"] = split_extra_film
    results["vl_split_strategy_heat_load_reduction"] = split_heat_reduction
    results["vl_split_strategy_material_factor"] = split_material_factor
    results["vl_split_strategy_material_limit"] = improved_limit
    results["vl_split_strategy_max_hot_wall_temperature"] = max_twg
    results["vl_split_strategy_max_hot_wall_temperature_location"] = max_twg_location
    results["vl_split_strategy_worst_material_margin"] = worst_margin
    results["vl_split_strategy_worst_material_margin_location"] = worst_margin_location
    results["vl_split_strategy_status"] = "PASS" if failed_count == 0 else "FAIL"

    return results

def build_coupled_split_strategy_marching_preview(results):
    """
    First coupled axial split-strategy marching preview.

    This upgrades the split strategy from a static screening correction into a
    station-by-station marching profile using the velocity-limited geometry
    thermal profile as the base.

    It still remains a model approximation, but it is more honest than the
    previous global split preview.
    """

    if results is None:
        return results

    base_profile = results.get("variable_geometry_thermal_profile")

    if not base_profile:
        results["coupled_split_strategy_status"] = "NO_VARIABLE_THERMAL_PROFILE"
        return results

    coolant_mdot = results.get("coolant_mass_flow_rate") or results.get("fuel_mass_flow_rate")
    coolant_cp = results.get("coolant_specific_heat_cp") or 2000.0

    if coolant_mdot is None or coolant_mdot <= 0:
        results["coupled_split_strategy_status"] = "NO_COOLANT_MASS_FLOW"
        return results

    coolant_ref = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    try:
        coolant_temperature = float(coolant_ref)
        coolant_cp = float(coolant_cp)
        coolant_mdot = float(coolant_mdot)
    except Exception:
        results["coupled_split_strategy_status"] = "INVALID_COOLANT_DATA"
        return results

    base_limit = results.get("velocity_limited_combined_material_limit")

    if base_limit is None:
        results["coupled_split_strategy_status"] = "NO_MATERIAL_LIMIT"
        return results

    try:
        base_limit = float(base_limit)
    except Exception:
        results["coupled_split_strategy_status"] = "INVALID_MATERIAL_LIMIT"
        return results

    extra_film = results.get("vl_split_strategy_extra_film_effectiveness") or 0.0
    heat_reduction = results.get("vl_split_strategy_heat_load_reduction") or 0.0
    material_factor = results.get("vl_split_strategy_material_factor") or 1.0

    extra_film = max(0.0, min(0.95, float(extra_film)))
    heat_reduction = max(0.0, min(0.95, float(heat_reduction)))
    material_factor = max(0.1, float(material_factor))

    improved_limit = base_limit * material_factor

    nozzle_length = results.get("nozzle_length") or 1.0

    try:
        nozzle_length = float(nozzle_length)
    except Exception:
        nozzle_length = 1.0

    film_decay_length = max(nozzle_length * 0.45, 1e-9)

    # March in physical coolant direction if coolant_path_index exists.
    marching_profile = sorted(
        base_profile,
        key=lambda station: station.get("coolant_path_index", station.get("station_index", 0))
    )

    coupled_by_station_index = {}

    failed_count = 0
    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None
    total_heat_absorbed = 0.0
    max_coolant_temperature = coolant_temperature

    for station in marching_profile:
        new_station = dict(station)

        x = station.get("x", 0.0)

        try:
            x = float(x)
        except Exception:
            x = 0.0

        base_twg = (
            station.get("variable_thermal_hot_wall_temperature")
            or station.get("hot_gas_side_wall_temperature")
        )

        q_station = (
            station.get("Q_station")
            or station.get("heat_absorbed_station")
            or station.get("station_heat_absorbed")
            or 0.0
        )

        try:
            base_twg = float(base_twg)
        except Exception:
            coupled_by_station_index[station.get("station_index", len(coupled_by_station_index))] = new_station
            continue

        try:
            q_station = float(q_station)
        except Exception:
            q_station = 0.0

        local_film = extra_film * math.exp(-x / film_decay_length)
        local_film = max(0.0, min(0.95, local_film))

        after_film_twg = base_twg - local_film * (base_twg - coolant_temperature)
        after_film_twg = max(after_film_twg, coolant_temperature)

        final_twg = coolant_temperature + (
            (after_film_twg - coolant_temperature) * (1.0 - heat_reduction)
        )

        final_twg = max(final_twg, coolant_temperature)

        # Heat absorbed is reduced by film + heat-load reduction.
        effective_heat_absorbed = q_station * (1.0 - local_film) * (1.0 - heat_reduction)
        effective_heat_absorbed = max(0.0, effective_heat_absorbed)

        delta_t_coolant = effective_heat_absorbed / max(coolant_mdot * coolant_cp, 1e-12)

        coolant_in = coolant_temperature
        coolant_out = coolant_temperature + delta_t_coolant
        coolant_temperature = coolant_out

        margin = improved_limit - final_twg

        new_station["coupled_split_local_film_effectiveness"] = local_film
        new_station["coupled_split_heat_load_reduction"] = heat_reduction
        new_station["coupled_split_material_factor"] = material_factor
        new_station["coupled_split_material_limit"] = improved_limit
        new_station["coupled_split_hot_wall_temperature"] = final_twg
        new_station["coupled_split_material_margin"] = margin
        new_station["coupled_split_pass"] = 1.0 if margin >= 0.0 else 0.0
        new_station["coupled_split_coolant_in_temperature"] = coolant_in
        new_station["coupled_split_coolant_out_temperature"] = coolant_out
        new_station["coupled_split_coolant_delta_t"] = delta_t_coolant
        new_station["coupled_split_station_heat_absorbed"] = effective_heat_absorbed

        if margin < 0.0:
            failed_count += 1

        if max_twg is None or final_twg > max_twg:
            max_twg = final_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        total_heat_absorbed += effective_heat_absorbed
        max_coolant_temperature = max(max_coolant_temperature, coolant_out)

        coupled_by_station_index[station.get("station_index", len(coupled_by_station_index))] = new_station

    # Return to normal x/station order for plotting/report compatibility.
    coupled_profile = [
        coupled_by_station_index[key]
        for key in sorted(coupled_by_station_index.keys())
    ]

    results["coupled_split_strategy_profile"] = coupled_profile
    results["coupled_split_strategy_station_count"] = len(coupled_profile)
    results["coupled_split_strategy_status"] = "PASS" if failed_count == 0 else "FAIL"
    results["coupled_split_strategy_failed_station_count"] = failed_count
    results["coupled_split_strategy_material_limit"] = improved_limit
    results["coupled_split_strategy_max_hot_wall_temperature"] = max_twg
    results["coupled_split_strategy_max_hot_wall_temperature_location"] = max_twg_location
    results["coupled_split_strategy_worst_material_margin"] = worst_margin
    results["coupled_split_strategy_worst_material_margin_location"] = worst_margin_location
    results["coupled_split_strategy_total_heat_absorbed"] = total_heat_absorbed
    results["coupled_split_strategy_coolant_outlet_temperature"] = coolant_temperature
    results["coupled_split_strategy_coolant_total_temperature_rise"] = coolant_temperature - coolant_ref
    results["coupled_split_strategy_max_coolant_temperature"] = max_coolant_temperature

    return results

def calculate_coupled_split_required_improvements(results):
    """
    Calculates the remaining improvement required for the coupled split strategy
    to pass.
    """

    if results is None:
        return results

    max_twg = results.get("coupled_split_strategy_max_hot_wall_temperature")
    material_limit = results.get("coupled_split_strategy_material_limit")

    if max_twg is None or material_limit is None:
        results["coupled_split_required_status"] = "INSUFFICIENT_DATA"
        return results

    try:
        max_twg = float(max_twg)
        material_limit = float(material_limit)
    except Exception:
        results["coupled_split_required_status"] = "INVALID_DATA"
        return results

    coolant_ref = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    try:
        coolant_ref = float(coolant_ref)
    except Exception:
        coolant_ref = 293.0

    thermal_gap = max(max_twg - coolant_ref, 1e-9)
    allowable_gap = max(material_limit - coolant_ref, 1e-9)

    required_total_factor = thermal_gap / allowable_gap
    required_extra_reduction_fraction = 1.0 - (allowable_gap / thermal_gap)

    results["coupled_split_required_status"] = (
        "PASS" if max_twg <= material_limit else "REQUIRED"
    )
    results["coupled_split_required_temperature_gap"] = max_twg - material_limit
    results["coupled_split_required_total_cooling_factor"] = required_total_factor
    results["coupled_split_required_extra_heat_reduction_fraction"] = required_extra_reduction_fraction
    results["coupled_split_required_material_temperature_limit"] = max_twg
    results["coupled_split_required_material_factor"] = (
        max_twg / max(results.get("material_max_wall_temperature") or 900.0, 1e-9)
    )

    return results

def build_coupled_split_auto_tuned_preview(results):
    """
    Applies the remaining coupled split required improvement automatically.

    This is a design-target preview, not final validation.
    It answers: what happens if LEAF applies the coupled-required extra
    improvement to the coupled split marching result?
    """

    if results is None:
        return results

    profile = results.get("coupled_split_strategy_profile")

    if not profile:
        results["coupled_split_auto_tuned_status"] = "NO_COUPLED_PROFILE"
        return results

    required_extra = results.get("coupled_split_required_extra_heat_reduction_fraction") or 0.0
    material_limit = results.get("coupled_split_strategy_material_limit")

    if material_limit is None:
        results["coupled_split_auto_tuned_status"] = "NO_MATERIAL_LIMIT"
        return results

    try:
        required_extra = float(required_extra)
        material_limit = float(material_limit)
    except Exception:
        results["coupled_split_auto_tuned_status"] = "INVALID_INPUTS"
        return results

    # Split the remaining coupled requirement across mechanisms.
    extra_film = min(0.12, required_extra * 0.40)
    extra_heat_reduction = min(0.12, required_extra * 0.40)
    extra_material_factor = 1.0 + min(0.20, required_extra * 0.80)

    improved_limit = material_limit * extra_material_factor

    tuned_profile = []
    failed_count = 0
    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)
        try:
            x = float(x)
        except Exception:
            x = 0.0

        base_twg = station.get("coupled_split_hot_wall_temperature")

        coolant_temperature = (
            station.get("coupled_split_coolant_in_temperature")
            or station.get("coolant_temperature_in")
            or results.get("coolant_inlet_temperature")
            or 293.0
        )

        try:
            base_twg = float(base_twg)
            coolant_temperature = float(coolant_temperature)
        except Exception:
            tuned_profile.append(new_station)
            continue

        after_film = base_twg - extra_film * (base_twg - coolant_temperature)
        after_film = max(after_film, coolant_temperature)

        tuned_twg = coolant_temperature + (
            (after_film - coolant_temperature) * (1.0 - extra_heat_reduction)
        )

        margin = improved_limit - tuned_twg

        new_station["coupled_auto_extra_film_effectiveness"] = extra_film
        new_station["coupled_auto_extra_heat_reduction"] = extra_heat_reduction
        new_station["coupled_auto_extra_material_factor"] = extra_material_factor
        new_station["coupled_auto_material_limit"] = improved_limit
        new_station["coupled_auto_hot_wall_temperature"] = tuned_twg
        new_station["coupled_auto_material_margin"] = margin
        new_station["coupled_auto_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_count += 1

        if max_twg is None or tuned_twg > max_twg:
            max_twg = tuned_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        tuned_profile.append(new_station)

    results["coupled_split_auto_tuned_profile"] = tuned_profile
    results["coupled_split_auto_tuned_status"] = "PASS" if failed_count == 0 else "FAIL"
    results["coupled_split_auto_tuned_station_count"] = len(tuned_profile)
    results["coupled_split_auto_tuned_failed_station_count"] = failed_count
    results["coupled_split_auto_tuned_extra_film_effectiveness"] = extra_film
    results["coupled_split_auto_tuned_extra_heat_reduction"] = extra_heat_reduction
    results["coupled_split_auto_tuned_extra_material_factor"] = extra_material_factor
    results["coupled_split_auto_tuned_material_limit"] = improved_limit
    results["coupled_split_auto_tuned_max_hot_wall_temperature"] = max_twg
    results["coupled_split_auto_tuned_max_hot_wall_temperature_location"] = max_twg_location
    results["coupled_split_auto_tuned_worst_material_margin"] = worst_margin
    results["coupled_split_auto_tuned_worst_material_margin_location"] = worst_margin_location

    return results

def translate_coupled_auto_tuned_target(results):
    """
    Converts the coupled auto-tuned abstract target into explicit design targets.

    This does not validate the design. It creates requirements for real
    implementation:
    - film effectiveness target
    - heat-load reduction target
    - material temperature target
    """

    if results is None:
        return results

    if not solver_pass(results.get("coupled_split_auto_tuned_status")):
        results["coupled_auto_target_status"] = "NO_PASSING_AUTO_TUNED_TARGET"
        return results

    base_film = results.get("vl_split_strategy_extra_film_effectiveness") or 0.0
    base_heat = results.get("vl_split_strategy_heat_load_reduction") or 0.0
    base_material_factor = results.get("vl_split_strategy_material_factor") or 1.0

    extra_film = results.get("coupled_split_auto_tuned_extra_film_effectiveness") or 0.0
    extra_heat = results.get("coupled_split_auto_tuned_extra_heat_reduction") or 0.0
    extra_material_factor = results.get("coupled_split_auto_tuned_extra_material_factor") or 1.0

    material_limit = results.get("coupled_split_auto_tuned_material_limit")
    max_twg = results.get("coupled_split_auto_tuned_max_hot_wall_temperature")
    worst_margin = results.get("coupled_split_auto_tuned_worst_material_margin")

    total_film = base_film + extra_film * (1.0 - base_film)
    total_heat_reduction = 1.0 - ((1.0 - base_heat) * (1.0 - extra_heat))
    total_material_factor = base_material_factor * extra_material_factor

    results["coupled_auto_target_status"] = "COMPLETE"
    results["coupled_auto_target_total_film_effectiveness"] = total_film
    results["coupled_auto_target_total_heat_load_reduction"] = total_heat_reduction
    results["coupled_auto_target_total_material_factor"] = total_material_factor
    results["coupled_auto_target_material_limit"] = material_limit
    results["coupled_auto_target_max_hot_wall_temperature"] = max_twg
    results["coupled_auto_target_worst_material_margin"] = worst_margin

    requirements = []

    requirements.append(
        f"Achieve total effective film cooling of approximately {total_film:.3f} near the controlling hot region."
    )
    requirements.append(
        f"Achieve total heat-load reduction of approximately {total_heat_reduction:.3f}."
    )
    requirements.append(
        f"Use a material/liner system with effective temperature capability of approximately {material_limit:.0f} K."
    )
    requirements.append(
        "Re-run coupled marching using explicit physical mechanisms instead of auto-tuned abstract factors."
    )

    results["coupled_auto_target_requirements"] = requirements

    return results

def screen_materials_against_coupled_auto_target(results):
    """
    Screens known material candidates against the coupled auto-tuned target.
    Uses existing material-screening outputs if available.
    """

    if results is None:
        return results

    target_temp = results.get("coupled_auto_target_material_limit")

    if target_temp is None:
        results["coupled_auto_material_screen_status"] = "NO_TARGET_TEMPERATURE"
        return results

    try:
        target_temp = float(target_temp)
    except Exception:
        results["coupled_auto_material_screen_status"] = "INVALID_TARGET_TEMPERATURE"
        return results

    candidates = []

    for key in (
            "material_screened_candidates",
            "material_candidate_screened_candidates",
            "material_candidate_all",
            "material_candidate_passing",
            "material_candidate_passing_candidates",
            "material_candidate_best",
            "material_candidate_best_candidate",
            "passing_candidates",
            "material_database_candidates",
            "material_candidates",
    ):
        value = results.get(key)

        if isinstance(value, list):
            candidates.extend(value)
        elif isinstance(value, dict):
            candidates.append(value)

    best_existing = results.get("material_candidate_best_candidate") or results.get("best_material_candidate")
    if isinstance(best_existing, dict):
        candidates.append(best_existing)

    selected_name = results.get("selected_material") or results.get("material_name")
    selected_limit = results.get("material_max_wall_temperature")

    if selected_name and selected_limit is not None:
        candidates.append({
            "name": selected_name,
            "family": results.get("material_family", "Selected material"),
            "max_wall_temperature": selected_limit,
            "thermal_conductivity": results.get("material_thermal_conductivity"),
            "notes": results.get("material_notes", ""),
        })

    unique = {}
    for mat in candidates:
        if not isinstance(mat, dict):
            continue

        name = mat.get("name") or mat.get("material") or "Unknown"
        limit = (
            mat.get("max_wall_temperature")
            or mat.get("material_max_wall_temperature")
            or mat.get("temperature_limit")
        )

        try:
            limit = float(limit)
        except Exception:
            continue

        unique[name] = {
            "name": name,
            "family": mat.get("family", "Unknown"),
            "max_wall_temperature": limit,
            "thermal_conductivity": mat.get("thermal_conductivity"),
            "notes": mat.get("notes", ""),
        }

    screened = []

    for mat in unique.values():
        margin = mat["max_wall_temperature"] - target_temp

        if margin >= 100.0:
            status = "PASS_WITH_MARGIN"
        elif margin >= 0.0:
            status = "PASS_LOW_MARGIN"
        else:
            status = "FAIL"

        screened.append({
            **mat,
            "target_temperature": target_temp,
            "margin": margin,
            "status": status,
            "score": margin,
        })

    screened.sort(key=lambda item: item.get("score", -1e9), reverse=True)

    passing = [item for item in screened if not solver_fail(item.get("status"))]

    results["coupled_auto_material_screen_status"] = "COMPLETE"
    results["coupled_auto_material_target_temperature"] = target_temp
    results["coupled_auto_material_candidate_count"] = len(screened)
    results["coupled_auto_material_passing_count"] = len(passing)
    results["coupled_auto_material_best_candidate"] = screened[0] if screened else None
    results["coupled_auto_material_passing_candidates"] = passing
    results["coupled_auto_material_screened_candidates"] = screened

    if passing:
        results["coupled_auto_material_recommendation"] = (
            "At least one material candidate meets the coupled auto target."
        )
    else:
        results["coupled_auto_material_recommendation"] = (
            "No current material candidate meets the coupled auto target. Shift more burden onto film cooling, heat-load reduction, chamber derating, coating, or improve the material database."
        )

    return results

def rebalance_coupled_auto_target_if_material_fails(results):
    """
    If no real material meets the coupled auto target, estimate how much extra
    film/heat-load reduction is needed to avoid relying on impossible material.
    """

    if results is None:
        return results

    if results.get("coupled_auto_material_screen_status") != "COMPLETE":
        results["coupled_auto_rebalance_status"] = "NO_MATERIAL_SCREEN"
        return results

    if results.get("coupled_auto_material_passing_count", 0) > 0:
        results["coupled_auto_rebalance_status"] = "NOT_REQUIRED"
        return results

    best = results.get("coupled_auto_material_best_candidate")
    max_twg = results.get("coupled_auto_target_max_hot_wall_temperature")

    if not best or max_twg is None:
        results["coupled_auto_rebalance_status"] = "INSUFFICIENT_DATA"
        return results

    try:
        best_limit = float(best.get("max_wall_temperature"))
        max_twg = float(max_twg)
    except Exception:
        results["coupled_auto_rebalance_status"] = "INVALID_DATA"
        return results

    coolant_ref = results.get("coolant_inlet_temperature") or results.get("coolant_temperature") or 293.0

    try:
        coolant_ref = float(coolant_ref)
    except Exception:
        coolant_ref = 293.0

    thermal_gap = max(max_twg - coolant_ref, 1e-9)
    allowed_gap = max(best_limit - coolant_ref, 1e-9)

    required_extra_reduction = 1.0 - allowed_gap / thermal_gap
    required_extra_reduction = max(0.0, min(0.95, required_extra_reduction))

    current_film = results.get("coupled_auto_target_total_film_effectiveness") or 0.0
    current_heat = results.get("coupled_auto_target_total_heat_load_reduction") or 0.0

    results["coupled_auto_rebalance_status"] = "REQUIRED"
    results["coupled_auto_rebalance_best_material_limit"] = best_limit
    results["coupled_auto_rebalance_required_extra_reduction"] = required_extra_reduction
    results["coupled_auto_rebalance_total_film_if_film_only"] = current_film + required_extra_reduction * (1.0 - current_film)
    results["coupled_auto_rebalance_total_heat_reduction_if_heat_only"] = current_heat + required_extra_reduction * (1.0 - current_heat)
    results["coupled_auto_rebalance_recommendation"] = (
        "Current material database cannot meet the coupled target. Rebalance toward explicit film cooling and heat-load reduction."
    )

    return results

def evaluate_coupled_auto_rebalance_options(results):
    """
    Evaluates realistic rebalance options when no material meets the coupled
    auto-tuned target.
    """

    if results is None:
        return results

    if results.get("coupled_auto_rebalance_status") != "REQUIRED":
        results["coupled_auto_rebalance_options_status"] = "NOT_REQUIRED"
        return results

    film_only = results.get("coupled_auto_rebalance_total_film_if_film_only")
    heat_only = results.get("coupled_auto_rebalance_total_heat_reduction_if_heat_only")
    best_limit = results.get("coupled_auto_rebalance_best_material_limit")
    target_temp = results.get("coupled_auto_material_target_temperature")

    options = []

    if film_only is not None:
        if film_only <= 0.35:
            status = "PLAUSIBLE"
            score = 80
        elif film_only <= 0.50:
            status = "AGGRESSIVE"
            score = 55
        else:
            status = "SEVERE"
            score = 20

        options.append({
            "name": "Film cooling dominant rebalance",
            "status": status,
            "score": score,
            "requirement": f"Total effective film cooling must reach {film_only:.3f}.",
        })

    if heat_only is not None:
        if heat_only <= 0.25:
            status = "PLAUSIBLE"
            score = 80
        elif heat_only <= 0.50:
            status = "AGGRESSIVE"
            score = 60
        else:
            status = "SEVERE"
            score = 25

        options.append({
            "name": "Heat-load reduction dominant rebalance",
            "status": status,
            "score": score,
            "requirement": f"Total heat-load reduction must reach {heat_only:.3f}.",
        })

    if best_limit is not None and target_temp is not None:
        missing_temperature = target_temp - best_limit

        options.append({
            "name": "Material/coating upgrade",
            "status": "SEVERE" if missing_temperature > 300 else "AGGRESSIVE",
            "score": 30 if missing_temperature > 300 else 55,
            "requirement": f"Material/coating system must close about {missing_temperature:.0f} K above the best database material.",
        })

    options.append({
        "name": "Balanced rebalance",
        "status": "RECOMMENDED",
        "score": 90,
        "requirement": "Split the remaining burden across film cooling, heat-load reduction, coatings/material improvement, and chamber derating.",
    })

    options.sort(key=lambda item: item.get("score", 0), reverse=True)

    results["coupled_auto_rebalance_options_status"] = "COMPLETE"
    results["coupled_auto_rebalance_options"] = options
    results["coupled_auto_rebalance_best_option"] = options[0] if options else None
    results["coupled_auto_rebalance_selected_path"] = "BALANCED_REBALANCE"

    return results

def build_coupled_auto_balanced_rebalance_preview(results):
    """
    Applies the selected balanced rebalance path using the best available
    material candidate and split film/heat-load reductions.

    This remains a design-target preview.
    """

    if results is None:
        return results

    profile = results.get("coupled_split_auto_tuned_profile")

    if not profile:
        results["coupled_auto_balanced_rebalance_status"] = "NO_AUTO_TUNED_PROFILE"
        return results

    if results.get("coupled_auto_rebalance_selected_path") != "BALANCED_REBALANCE":
        results["coupled_auto_balanced_rebalance_status"] = "NOT_SELECTED"
        return results

    best_material_limit = results.get("coupled_auto_rebalance_best_material_limit")
    required_extra = results.get("coupled_auto_rebalance_required_extra_reduction")

    if best_material_limit is None or required_extra is None:
        results["coupled_auto_balanced_rebalance_status"] = "INSUFFICIENT_DATA"
        return results

    try:
        best_material_limit = float(best_material_limit)
        required_extra = float(required_extra)
    except Exception:
        results["coupled_auto_balanced_rebalance_status"] = "INVALID_DATA"
        return results

    # Split remaining burden evenly across film and heat-load reduction.
    extra_film = min(0.25, required_extra * 0.50)
    extra_heat_reduction = min(0.25, required_extra * 0.50)

    profile_out = []
    failed_count = 0
    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)

        try:
            x = float(x)
        except Exception:
            x = 0.0

        base_twg = station.get("coupled_auto_hot_wall_temperature")

        coolant_temperature = (
            station.get("coupled_split_coolant_in_temperature")
            or results.get("coolant_inlet_temperature")
            or results.get("coolant_temperature")
            or 293.0
        )

        try:
            base_twg = float(base_twg)
            coolant_temperature = float(coolant_temperature)
        except Exception:
            profile_out.append(new_station)
            continue

        after_film = base_twg - extra_film * (base_twg - coolant_temperature)
        after_film = max(after_film, coolant_temperature)

        balanced_twg = coolant_temperature + (
            (after_film - coolant_temperature) * (1.0 - extra_heat_reduction)
        )

        margin = best_material_limit - balanced_twg

        new_station["coupled_balanced_extra_film_effectiveness"] = extra_film
        new_station["coupled_balanced_extra_heat_reduction"] = extra_heat_reduction
        new_station["coupled_balanced_material_limit"] = best_material_limit
        new_station["coupled_balanced_hot_wall_temperature"] = balanced_twg
        new_station["coupled_balanced_material_margin"] = margin
        new_station["coupled_balanced_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_count += 1

        if max_twg is None or balanced_twg > max_twg:
            max_twg = balanced_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        profile_out.append(new_station)

    results["coupled_auto_balanced_rebalance_profile"] = profile_out
    results["coupled_auto_balanced_rebalance_status"] = "PASS" if failed_count == 0 else "FAIL"
    results["coupled_auto_balanced_rebalance_station_count"] = len(profile_out)
    results["coupled_auto_balanced_rebalance_failed_station_count"] = failed_count
    results["coupled_auto_balanced_rebalance_extra_film"] = extra_film
    results["coupled_auto_balanced_rebalance_extra_heat_reduction"] = extra_heat_reduction
    results["coupled_auto_balanced_rebalance_material_limit"] = best_material_limit
    results["coupled_auto_balanced_rebalance_max_hot_wall_temperature"] = max_twg
    results["coupled_auto_balanced_rebalance_max_hot_wall_temperature_location"] = max_twg_location
    results["coupled_auto_balanced_rebalance_worst_material_margin"] = worst_margin
    results["coupled_auto_balanced_rebalance_worst_material_margin_location"] = worst_margin_location

    return results

def evaluate_coating_liner_gap_for_balanced_rebalance(results):
    """
    Evaluates whether the remaining balanced-rebalance failure can plausibly
    be closed by a coating/liner allowance.

    This does not force a pass. It only reports the required extra thermal
    protection temperature margin.
    """

    if results is None:
        return results

    status = results.get("coupled_auto_balanced_rebalance_status")

    if not solver_fail(status):
        results["coating_liner_gap_status"] = "NOT_REQUIRED"
        return results

    worst_margin = results.get("coupled_auto_balanced_rebalance_worst_material_margin")

    if worst_margin is None:
        results["coating_liner_gap_status"] = "INSUFFICIENT_DATA"
        return results

    try:
        worst_margin = float(worst_margin)
    except Exception:
        results["coating_liner_gap_status"] = "INVALID_DATA"
        return results

    required_gap = max(0.0, -worst_margin)

    if required_gap <= 50.0:
        plausibility = "PLAUSIBLE"
    elif required_gap <= 150.0:
        plausibility = "AGGRESSIVE"
    else:
        plausibility = "SEVERE"

    results["coating_liner_gap_status"] = "REQUIRED"
    results["coating_liner_required_temperature_margin"] = required_gap
    results["coating_liner_plausibility"] = plausibility
    results["coating_liner_recommendation"] = (
        "Add an explicit coating/liner model before accepting the design. "
        "The current gap is small enough to evaluate with coating, liner, or local derating, "
        "but should not be treated as a pass yet."
    )

    return results

def build_explicit_coating_liner_preview(results):
    """
    Applies an explicit coating/liner thermal-resistance preview to the
    balanced rebalance result.

    This is still not final validation. If coating data is placeholder-only,
    the best possible status is PLACEHOLDER_DATA_NOT_QUALIFIABLE.
    """

    if results is None:
        return results

    profile = results.get("coupled_auto_balanced_rebalance_profile")

    if not profile:
        results["explicit_coating_liner_status"] = "NO_BALANCED_REBALANCE_PROFILE"
        return results

    if results.get("coating_liner_gap_status") != "REQUIRED":
        results["explicit_coating_liner_status"] = "NOT_REQUIRED"
        return results

    best_coating_candidate = (
            results.get("selected_explicit_coating_liner_candidate")
            or results.get("coating_material_best_thermal_barrier_candidate")
            or results.get("coating_material_best_candidate")
            or {}
    )

    coating_thickness = (
        results.get("coating_liner_thickness")
        or results.get("coating_thickness")
        or best_coating_candidate.get("required_thickness")
        or results.get("required_coating_liner_max_required_thickness")
        or 0.00025
    )

    coating_conductivity = (
        results.get("coating_liner_thermal_conductivity")
        or results.get("coating_thermal_conductivity")
        or best_coating_candidate.get("thermal_conductivity")
        or results.get("required_coating_liner_thermal_conductivity")
        or 2.0
    )

    coating_max_surface_temperature = (
        results.get("coating_liner_max_surface_temperature")
        or results.get("coating_max_surface_temperature")
        or best_coating_candidate.get("max_surface_temperature")
        or 1800.0
    )

    coating_material_name = best_coating_candidate.get("name", "Manual / default coating")
    coating_source_quality = best_coating_candidate.get("source_quality", "unknown")
    coating_max_practical_thickness = best_coating_candidate.get("max_practical_thickness")
    coating_density = best_coating_candidate.get("density")
    coating_elastic_modulus = best_coating_candidate.get("elastic_modulus")
    coating_poisson_ratio = best_coating_candidate.get("poisson_ratio")
    coating_thermal_expansion_coefficient = best_coating_candidate.get("thermal_expansion_coefficient")
    coating_allowable_stress = best_coating_candidate.get("allowable_coating_stress")

    required_liner_safety_margin = (
            results.get("explicit_coating_liner_required_safety_margin")
            or 50.0
    )

    required_surface_safety_margin = (
            results.get("explicit_coating_surface_required_safety_margin")
            or 100.0
    )

    data_quality_status = results.get("coating_material_data_quality_status")
    source_quality_text = str(coating_source_quality).lower()

    uses_placeholder_data = (
        data_quality_status != "SOURCED_DATA"
        or "placeholder" in source_quality_text
        or "estimate" in source_quality_text
        or "approx" in source_quality_text
    )

    try:
        coating_thickness = float(coating_thickness)
        coating_conductivity = float(coating_conductivity)
        coating_max_surface_temperature = float(coating_max_surface_temperature)
    except Exception:
        results["explicit_coating_liner_status"] = "INVALID_COATING_INPUTS"
        return results

    if coating_thickness <= 0 or coating_conductivity <= 0:
        results["explicit_coating_liner_status"] = "INVALID_COATING_PROPERTIES"
        return results

    coated_profile = []

    failed_count = 0
    surface_failed_count = 0
    sanity_failed_count = 0
    worst_liner_safety_margin_deficit = None
    worst_surface_safety_margin_deficit = None
    worst_extra_coating_thickness_required = None
    worst_total_coating_thickness_required = None
    max_liner_twg = None
    max_surface_temperature = None
    worst_margin = None
    worst_margin_location = None
    max_liner_location = None
    coated_surface_area_total = 0.0
    coating_mass_total = None
    thermal_stress_failed_count = 0
    max_coating_thermal_stress = None
    worst_coating_stress_margin = None
    worst_required_stress_reduction_fraction = None
    worst_required_allowable_stress_factor = None

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)

        try:
            x = float(x)
        except Exception:
            x = 0.0

        radius = (
                station.get("radius")
                or station.get("r")
                or results.get("throat_radius")
                or 0.0
        )

        try:
            radius = float(radius)
        except Exception:
            radius = 0.0

        base_twg = station.get("coupled_balanced_hot_wall_temperature")
        material_limit = station.get("coupled_balanced_material_limit")

        heat_flux = (
            station.get("regen_heat_flux")
            or station.get("heat_flux")
            or station.get("q")
            or results.get("preview_max_heat_flux")
            or results.get("max_heat_flux")
            or 0.0
        )

        try:
            base_twg = float(base_twg)
            material_limit = float(material_limit)
            heat_flux = float(heat_flux)
        except Exception:
            coated_profile.append(new_station)
            continue

        raw_coating_delta_t = heat_flux * coating_thickness / coating_conductivity

        coolant_temperature = (
            station.get("coupled_split_coolant_in_temperature")
            or station.get("coolant_temperature")
            or results.get("coolant_inlet_temperature")
            or 293.0
        )

        try:
            coolant_temperature = float(coolant_temperature)
        except Exception:
            coolant_temperature = 293.0

        available_thermal_gap = max(base_twg - coolant_temperature, 0.0)
        max_allowed_coating_delta_t = available_thermal_gap * 0.75

        coating_delta_t = min(raw_coating_delta_t, max_allowed_coating_delta_t)
        coating_thermal_stress = None
        coating_stress_margin = None
        coating_thermal_stress_pass = None
        required_stress_reduction_fraction = None
        required_allowable_stress_factor = None

        if (
                coating_elastic_modulus is not None
                and coating_poisson_ratio is not None
                and coating_thermal_expansion_coefficient is not None
                and coating_allowable_stress is not None
        ):
            try:
                coating_thermal_stress = (
                        float(coating_elastic_modulus)
                        * float(coating_thermal_expansion_coefficient)
                        * abs(coating_delta_t)
                        / max(1.0 - float(coating_poisson_ratio), 1e-9)
                )

                coating_stress_margin = float(coating_allowable_stress) - coating_thermal_stress
                coating_thermal_stress_pass = 1.0 if coating_stress_margin >= 0.0 else 0.0

                required_stress_reduction_fraction = 0.0
                required_allowable_stress_factor = 1.0

                if coating_thermal_stress > float(coating_allowable_stress):
                    required_stress_reduction_fraction = (
                                                                 coating_thermal_stress - float(
                                                             coating_allowable_stress)
                                                         ) / max(coating_thermal_stress, 1e-9)

                    required_allowable_stress_factor = (
                            coating_thermal_stress / max(float(coating_allowable_stress), 1e-9)
                    )

            except Exception:
                coating_thermal_stress = None
                coating_stress_margin = None
                coating_thermal_stress_pass = None

        liner_twg = base_twg - coating_delta_t
        coating_surface_temperature = base_twg

        material_margin = material_limit - liner_twg
        surface_margin = coating_max_surface_temperature - coating_surface_temperature

        liner_safety_margin_deficit = required_liner_safety_margin - material_margin
        surface_safety_margin_deficit = required_surface_safety_margin - surface_margin

        liner_safety_margin_deficit = max(liner_safety_margin_deficit, 0.0)
        surface_safety_margin_deficit = max(surface_safety_margin_deficit, 0.0)

        extra_coating_thickness_required = None
        total_coating_thickness_required = None

        if heat_flux > 0 and liner_safety_margin_deficit > 0:
            extra_coating_thickness_required = (
                    liner_safety_margin_deficit
                    * coating_conductivity
                    / heat_flux
            )
            total_coating_thickness_required = (
                    coating_thickness + extra_coating_thickness_required
            )
        else:
            extra_coating_thickness_required = 0.0
            total_coating_thickness_required = coating_thickness

        station_dx = (
                station.get("dx")
                or station.get("station_dx")
                or station.get("axial_step")
        )

        try:
            station_dx = float(station_dx)
        except Exception:
            station_dx = None

        if station_dx is None or station_dx <= 0:
            station_count_for_dx = max(len(profile), 1)
            nozzle_length_for_dx = (
                    results.get("nozzle_length")
                    or results.get("Ln")
                    or results.get("nozzle_length_m")
                    or 0.0
            )

            try:
                nozzle_length_for_dx = float(nozzle_length_for_dx)
            except Exception:
                nozzle_length_for_dx = 0.0

            station_dx = nozzle_length_for_dx / station_count_for_dx

        station_surface_area = 2.0 * math.pi * max(radius, 0.0) * max(station_dx, 0.0)

        effective_coating_thickness_for_mass = (
                total_coating_thickness_required
                or coating_thickness
                or 0.0
        )

        station_coating_mass = None

        if coating_density is not None:
            try:
                station_coating_mass = (
                        station_surface_area
                        * effective_coating_thickness_for_mass
                        * float(coating_density)
                )
            except Exception:
                station_coating_mass = None

        coated_surface_area_total += station_surface_area

        if station_coating_mass is not None:
            if coating_mass_total is None:
                coating_mass_total = 0.0
            coating_mass_total += station_coating_mass

        coating_sanity_valid = 1.0

        if raw_coating_delta_t > max_allowed_coating_delta_t:
            coating_sanity_valid = 0.0

        if liner_twg < coolant_temperature:
            coating_sanity_valid = 0.0

        thermal_stress_station_ok = (
                coating_thermal_stress_pass is None
                or coating_thermal_stress_pass == 1.0
        )

        pass_flag = 1.0 if (
                material_margin >= required_liner_safety_margin
                and surface_margin >= required_surface_safety_margin
                and coating_sanity_valid == 1.0
                and thermal_stress_station_ok
        ) else 0.0

        new_station["explicit_coating_thickness"] = coating_thickness
        new_station["explicit_coating_thermal_conductivity"] = coating_conductivity
        new_station["explicit_coating_delta_t"] = coating_delta_t
        new_station["explicit_coating_surface_temperature"] = coating_surface_temperature
        new_station["explicit_coating_surface_limit"] = coating_max_surface_temperature
        new_station["explicit_coating_surface_margin"] = surface_margin
        new_station["explicit_coated_liner_hot_wall_temperature"] = liner_twg
        new_station["explicit_coated_liner_material_limit"] = material_limit
        new_station["explicit_coated_liner_material_margin"] = material_margin
        new_station["explicit_coating_liner_required_safety_margin"] = required_liner_safety_margin
        new_station["explicit_coating_liner_safety_margin_deficit"] = liner_safety_margin_deficit
        new_station["explicit_coating_surface_required_safety_margin"] = required_surface_safety_margin
        new_station["explicit_coating_surface_safety_margin_deficit"] = surface_safety_margin_deficit
        new_station["explicit_coating_extra_thickness_required"] = extra_coating_thickness_required
        new_station["explicit_coating_total_thickness_required"] = total_coating_thickness_required
        new_station["explicit_coating_station_surface_area"] = station_surface_area
        new_station["explicit_coating_station_mass"] = station_coating_mass
        new_station["explicit_coating_liner_pass"] = pass_flag
        new_station["explicit_coating_raw_delta_t"] = raw_coating_delta_t
        new_station["explicit_coating_max_allowed_delta_t"] = max_allowed_coating_delta_t
        new_station["explicit_coating_sanity_valid"] = coating_sanity_valid
        new_station["explicit_coating_thermal_stress"] = coating_thermal_stress
        new_station["explicit_coating_allowable_stress"] = coating_allowable_stress
        new_station["explicit_coating_stress_margin"] = coating_stress_margin
        new_station["explicit_coating_thermal_stress_pass"] = coating_thermal_stress_pass
        new_station["explicit_coating_required_stress_reduction_fraction"] = required_stress_reduction_fraction
        new_station["explicit_coating_required_allowable_stress_factor"] = required_allowable_stress_factor

        if material_margin < required_liner_safety_margin:
            failed_count += 1

        if surface_margin < required_surface_safety_margin:
            surface_failed_count += 1

        if coating_sanity_valid == 0.0:
            sanity_failed_count += 1

        if max_liner_twg is None or liner_twg > max_liner_twg:
            max_liner_twg = liner_twg
            max_liner_location = x

        if max_surface_temperature is None or coating_surface_temperature > max_surface_temperature:
            max_surface_temperature = coating_surface_temperature

        if worst_margin is None or material_margin < worst_margin:
            worst_margin = material_margin
            worst_margin_location = x

        if (
                worst_liner_safety_margin_deficit is None
                or liner_safety_margin_deficit > worst_liner_safety_margin_deficit
        ):
            worst_liner_safety_margin_deficit = liner_safety_margin_deficit

        if (
                worst_surface_safety_margin_deficit is None
                or surface_safety_margin_deficit > worst_surface_safety_margin_deficit
        ):
            worst_surface_safety_margin_deficit = surface_safety_margin_deficit

        if (
                worst_extra_coating_thickness_required is None
                or extra_coating_thickness_required > worst_extra_coating_thickness_required
        ):
            worst_extra_coating_thickness_required = extra_coating_thickness_required

        if (
                worst_total_coating_thickness_required is None
                or total_coating_thickness_required > worst_total_coating_thickness_required
        ):
            worst_total_coating_thickness_required = total_coating_thickness_required

        if coating_thermal_stress_pass == 0.0:
            thermal_stress_failed_count += 1

        if coating_thermal_stress is not None:
            if max_coating_thermal_stress is None or coating_thermal_stress > max_coating_thermal_stress:
                max_coating_thermal_stress = coating_thermal_stress

        if coating_stress_margin is not None:
            if worst_coating_stress_margin is None or coating_stress_margin < worst_coating_stress_margin:
                worst_coating_stress_margin = coating_stress_margin

        if required_stress_reduction_fraction is not None:
            if (
                    worst_required_stress_reduction_fraction is None
                    or required_stress_reduction_fraction > worst_required_stress_reduction_fraction
            ):
                worst_required_stress_reduction_fraction = required_stress_reduction_fraction

        if required_allowable_stress_factor is not None:
            if (
                    worst_required_allowable_stress_factor is None
                    or required_allowable_stress_factor > worst_required_allowable_stress_factor
            ):
                worst_required_allowable_stress_factor = required_allowable_stress_factor

        coated_profile.append(new_station)

    thickness_margin_status = "UNKNOWN"
    thickness_margin = None

    if coating_max_practical_thickness is not None and worst_total_coating_thickness_required is not None:
        thickness_margin = coating_max_practical_thickness - worst_total_coating_thickness_required

        if thickness_margin >= 0.0:
            thickness_margin_status = "PASS"
        else:
            thickness_margin_status = "FAIL"

    if sanity_failed_count > 0:
        status = "FAIL_SANITY_LIMIT"
    elif surface_failed_count > 0:
        status = "FAIL_SURFACE_LIMIT"
    elif thermal_stress_failed_count > 0:
        status = "FAIL_THERMAL_STRESS"
    elif failed_count > 0 and thickness_margin_status == "PASS":
        status = "FAIL_LINER_LIMIT_BUT_THICKNESS_RECOVERABLE"
    elif failed_count > 0:
        status = "FAIL_LINER_LIMIT"
    elif thickness_margin_status == "FAIL":
        status = "FAIL_THICKNESS_LIMIT"
    elif uses_placeholder_data:
        status = "PLACEHOLDER_DATA_NOT_QUALIFIABLE"
    else:
        status = "PASS"

    results["explicit_coating_liner_profile"] = coated_profile
    results["explicit_coating_liner_status"] = status
    results["explicit_coating_liner_uses_placeholder_data"] = uses_placeholder_data
    results["explicit_coating_liner_station_count"] = len(coated_profile)
    results["explicit_coating_liner_failed_station_count"] = failed_count
    results["explicit_coating_liner_surface_failed_station_count"] = surface_failed_count
    results["explicit_coating_liner_material_name"] = coating_material_name
    results["explicit_coating_liner_source_quality"] = coating_source_quality
    results["explicit_coating_liner_thickness"] = coating_thickness
    results["explicit_coating_liner_thermal_conductivity"] = coating_conductivity
    results["explicit_coating_liner_surface_limit"] = coating_max_surface_temperature
    results["explicit_coating_liner_max_liner_hot_wall_temperature"] = max_liner_twg
    results["explicit_coating_liner_max_surface_temperature"] = max_surface_temperature
    results["explicit_coating_liner_worst_material_margin"] = worst_margin
    results["explicit_coating_liner_worst_safety_margin_deficit"] = worst_liner_safety_margin_deficit
    results["explicit_coating_surface_worst_safety_margin_deficit"] = worst_surface_safety_margin_deficit
    results["explicit_coating_extra_thickness_required_for_margin"] = worst_extra_coating_thickness_required
    results["explicit_coating_total_thickness_required_for_margin"] = worst_total_coating_thickness_required
    results["explicit_coating_max_practical_thickness"] = coating_max_practical_thickness
    results["explicit_coating_thickness_margin"] = thickness_margin
    results["explicit_coating_thickness_margin_status"] = thickness_margin_status
    coating_mass_status = "UNKNOWN"
    coating_mass_recommendation = "Coating mass could not be assessed."

    if coating_mass_total is not None:
        if coating_mass_total < 0.01:
            coating_mass_status = "NEGLIGIBLE"
            coating_mass_recommendation = (
                "Coating mass penalty is negligible for this preliminary design."
            )
        elif coating_mass_total < 0.1:
            coating_mass_status = "LOW"
            coating_mass_recommendation = (
                "Coating mass penalty is low, but should still be included in final engine mass accounting."
            )
        elif coating_mass_total < 1.0:
            coating_mass_status = "MODERATE"
            coating_mass_recommendation = (
                "Coating mass penalty is moderate and should be included in chamber/nozzle mass optimisation."
            )
        else:
            coating_mass_status = "HIGH"
            coating_mass_recommendation = (
                "Coating mass penalty is high; reassess coating thickness, density, and coated area."
            )

    results["explicit_coating_density"] = coating_density
    results["explicit_coating_surface_area_total"] = coated_surface_area_total
    results["explicit_coating_mass_total"] = coating_mass_total
    results["explicit_coating_mass_status"] = coating_mass_status
    results["explicit_coating_mass_recommendation"] = coating_mass_recommendation
    results["explicit_coating_liner_required_safety_margin"] = required_liner_safety_margin
    results["explicit_coating_surface_required_safety_margin"] = required_surface_safety_margin
    results["explicit_coating_liner_worst_material_margin_location"] = worst_margin_location
    results["explicit_coating_liner_max_liner_temperature_location"] = max_liner_location
    results["explicit_coating_liner_sanity_failed_station_count"] = sanity_failed_count

    results["explicit_coating_elastic_modulus"] = coating_elastic_modulus
    results["explicit_coating_poisson_ratio"] = coating_poisson_ratio
    results["explicit_coating_thermal_expansion_coefficient"] = coating_thermal_expansion_coefficient
    results["explicit_coating_allowable_stress"] = coating_allowable_stress
    results["explicit_coating_max_thermal_stress"] = max_coating_thermal_stress
    results["explicit_coating_worst_stress_margin"] = worst_coating_stress_margin
    results["explicit_coating_thermal_stress_failed_station_count"] = thermal_stress_failed_count
    results["explicit_coating_required_stress_reduction_fraction"] = worst_required_stress_reduction_fraction
    results["explicit_coating_required_allowable_stress_factor"] = worst_required_allowable_stress_factor
    stress_recovery_status = "UNKNOWN"
    stress_recovery_recommendation = "Coating thermal-stress recovery could not be assessed."

    if worst_required_stress_reduction_fraction is not None:
        if worst_required_stress_reduction_fraction <= 0.10:
            stress_recovery_status = "MINOR_RECOVERY_REQUIRED"
            stress_recovery_recommendation = (
                "Coating thermal stress is only slightly above the placeholder limit. "
                "Sourced material data or a modest bond-coat model may close the gap."
            )
        elif worst_required_stress_reduction_fraction <= 0.30:
            stress_recovery_status = "MODERATE_RECOVERY_REQUIRED"
            stress_recovery_recommendation = (
                "Coating thermal stress requires moderate reduction. "
                "Evaluate compliant bond coat, graded coating, lower-modulus coating, or lower coating temperature drop."
            )
        elif worst_required_stress_reduction_fraction <= 0.50:
            stress_recovery_status = "MAJOR_RECOVERY_REQUIRED"
            stress_recovery_recommendation = (
                "Coating thermal stress requires major reduction. "
                "Do not accept the coating path without a dedicated bond-coat, fatigue, and spallation model."
            )
        else:
            stress_recovery_status = "SEVERE_RECOVERY_REQUIRED"
            stress_recovery_recommendation = (
                "Coating thermal stress recovery requirement is severe. "
                "Current coating architecture is likely unsuitable without substantial redesign."
            )

    results["explicit_coating_stress_recovery_status"] = stress_recovery_status
    results["explicit_coating_stress_recovery_recommendation"] = stress_recovery_recommendation

    bond_coat_max_stress_reduction_fraction = (
            results.get("explicit_bond_coat_max_stress_reduction_fraction")
            or 0.25
    )

    bond_coat_required_stress_reduction_fraction = worst_required_stress_reduction_fraction

    bond_coat_recovery_margin = None
    bond_coat_recovery_status = "UNKNOWN"

    if bond_coat_required_stress_reduction_fraction is not None:
        bond_coat_recovery_margin = (
                bond_coat_max_stress_reduction_fraction
                - bond_coat_required_stress_reduction_fraction
        )

        if bond_coat_recovery_margin >= 0.0:
            bond_coat_recovery_status = "RECOVERABLE_WITH_COMPLIANT_LAYER_TARGET"
        else:
            bond_coat_recovery_status = "FAIL_COMPLIANT_LAYER_TARGET"

    results["explicit_bond_coat_max_stress_reduction_fraction"] = bond_coat_max_stress_reduction_fraction
    results["explicit_bond_coat_required_stress_reduction_fraction"] = bond_coat_required_stress_reduction_fraction
    results["explicit_bond_coat_recovery_margin"] = bond_coat_recovery_margin
    results["explicit_bond_coat_recovery_status"] = bond_coat_recovery_status

    bond_coat_candidates = results.get("bond_coat_candidates") or BOND_COAT_DATABASE
    screened_bond_coats = []

    for bond in bond_coat_candidates:
        reduction = bond.get("max_stress_reduction_fraction")
        thickness = bond.get("max_practical_thickness")

        if reduction is None:
            continue

        margin = None
        status = "UNKNOWN"

        try:
            reduction = float(reduction)

            if bond_coat_required_stress_reduction_fraction is not None:
                margin = reduction - bond_coat_required_stress_reduction_fraction
                status = "PASS" if margin >= 0.0 else "FAIL"

        except Exception:
            continue

        screened_bond_coats.append({
            "name": bond.get("name", "Unknown bond coat"),
            "family": bond.get("family", "Unknown"),
            "max_stress_reduction_fraction": reduction,
            "required_stress_reduction_fraction": bond_coat_required_stress_reduction_fraction,
            "stress_reduction_margin": margin,
            "max_practical_thickness": thickness,
            "density": bond.get("density"),
            "source_quality": bond.get("source_quality", "unknown"),
            "notes": bond.get("notes", ""),
            "status": status,
            "score": margin if margin is not None else -1e9,
        })

    screened_bond_coats.sort(
        key=lambda item: item.get("score", -1e9),
        reverse=True
    )

    passing_bond_coats = [
        item for item in screened_bond_coats
        if solver_pass(item.get("status"))
    ]

    bond_coat_best_candidate = screened_bond_coats[0] if screened_bond_coats else None

    bond_coat_uses_placeholder_data = False
    bond_coat_best_source_quality = "unknown"
    bond_coat_best_name = "N/A"

    if bond_coat_best_candidate:
        bond_coat_best_name = bond_coat_best_candidate.get("name", "N/A")
        bond_coat_best_source_quality = bond_coat_best_candidate.get("source_quality", "unknown")

        source_quality_text = str(bond_coat_best_source_quality).lower()
        name_text = str(bond_coat_best_name).lower()

        bond_coat_uses_placeholder_data = (
                "placeholder" in source_quality_text
                or "estimate" in source_quality_text
                or "approx" in source_quality_text
                or "generic" in name_text
        )

    results["bond_coat_screen_status"] = (
        "COMPLETE" if screened_bond_coats else "NO_CANDIDATES"
    )
    results["bond_coat_candidate_count"] = len(screened_bond_coats)
    results["bond_coat_passing_count"] = len(passing_bond_coats)
    results["bond_coat_best_candidate"] = bond_coat_best_candidate
    results["bond_coat_best_candidate_name"] = bond_coat_best_name
    results["bond_coat_best_source_quality"] = bond_coat_best_source_quality
    results["bond_coat_uses_placeholder_data"] = bond_coat_uses_placeholder_data
    results["bond_coat_passing_candidates"] = passing_bond_coats

    bond_coat_mass_total = None
    bond_coat_density = None
    bond_coat_thickness = None

    if bond_coat_best_candidate:
        bond_coat_density = bond_coat_best_candidate.get("density")
        bond_coat_thickness = bond_coat_best_candidate.get("max_practical_thickness")

        try:
            bond_coat_mass_total = (
                    coated_surface_area_total
                    * float(bond_coat_thickness)
                    * float(bond_coat_density)
            )
        except Exception:
            bond_coat_mass_total = None

    bond_coat_mass_status = "UNKNOWN"

    if bond_coat_mass_total is not None:
        if bond_coat_mass_total < 0.01:
            bond_coat_mass_status = "NEGLIGIBLE"
        elif bond_coat_mass_total < 0.1:
            bond_coat_mass_status = "LOW"
        elif bond_coat_mass_total < 1.0:
            bond_coat_mass_status = "MODERATE"
        else:
            bond_coat_mass_status = "HIGH"

    results["bond_coat_density"] = bond_coat_density
    results["bond_coat_thickness"] = bond_coat_thickness
    results["bond_coat_mass_total"] = bond_coat_mass_total
    results["bond_coat_mass_status"] = bond_coat_mass_status

    coating_stack_mass_total = None

    if coating_mass_total is not None or bond_coat_mass_total is not None:
        coating_stack_mass_total = (
                (coating_mass_total or 0.0)
                + (bond_coat_mass_total or 0.0)
        )

    coating_stack_mass_status = "UNKNOWN"

    if coating_stack_mass_total is not None:
        if coating_stack_mass_total < 0.01:
            coating_stack_mass_status = "NEGLIGIBLE"
        elif coating_stack_mass_total < 0.1:
            coating_stack_mass_status = "LOW"
        elif coating_stack_mass_total < 1.0:
            coating_stack_mass_status = "MODERATE"
        else:
            coating_stack_mass_status = "HIGH"

    results["coating_stack_mass_total"] = coating_stack_mass_total
    results["coating_stack_mass_status"] = coating_stack_mass_status

    coating_stack_total_thickness = None

    if worst_total_coating_thickness_required is not None or bond_coat_thickness is not None:
        coating_stack_total_thickness = (
                (worst_total_coating_thickness_required or 0.0)
                + (bond_coat_thickness or 0.0)
        )

    coating_stack_thickness_status = "UNKNOWN"

    if coating_stack_total_thickness is not None:
        if coating_stack_total_thickness <= 0.00025:
            coating_stack_thickness_status = "LOW"
        elif coating_stack_total_thickness <= 0.0005:
            coating_stack_thickness_status = "MODERATE"
        elif coating_stack_total_thickness <= 0.001:
            coating_stack_thickness_status = "HIGH"
        else:
            coating_stack_thickness_status = "EXCESSIVE"

    results["coating_stack_total_thickness"] = coating_stack_total_thickness
    results["coating_stack_thickness_status"] = coating_stack_thickness_status

    if passing_bond_coats:
        if bond_coat_uses_placeholder_data:
            results["bond_coat_validation_status"] = "PLACEHOLDER_DATA_NOT_QUALIFIABLE"
            results["bond_coat_validation_recommendation"] = (
                "A bond-coat/interlayer candidate can close the first-pass stress gap, "
                "but the candidate is generic or placeholder. Do not validate until sourced material data is added."
            )
        else:
            results["bond_coat_validation_status"] = "PASS"
            results["bond_coat_validation_recommendation"] = (
                "A sourced bond-coat/interlayer candidate can close the first-pass stress gap. "
                "Proceed to fatigue, spallation, adhesion, and manufacturing checks."
            )

        bond_coat_validation_status = results.get("bond_coat_validation_status")

        coating_stack_validation_status = "UNKNOWN"

        if (
                coating_stack_mass_status in ("NEGLIGIBLE", "LOW")
                and coating_stack_thickness_status in ("LOW", "MODERATE")
                and results.get("bond_coat_validation_status") == "PLACEHOLDER_DATA_NOT_QUALIFIABLE"
        ):
            coating_stack_validation_status = "PLACEHOLDER_DATA_NOT_QUALIFIABLE"
        elif (
                coating_stack_mass_status in ("HIGH",)
                or coating_stack_thickness_status in ("HIGH", "EXCESSIVE")
        ):
            coating_stack_validation_status = "FAIL_STACK_PRACTICALITY"
        else:
            coating_stack_validation_status = "NEEDS_REVIEW"

        results["coating_stack_validation_status"] = coating_stack_validation_status

        if coating_stack_validation_status == "PLACEHOLDER_DATA_NOT_QUALIFIABLE":
            coating_stack_validation_recommendation = (
                "Coating stack mass and thickness are practical at placeholder level, "
                "but validation is blocked until sourced coating and bond-coat data are added."
            )
        elif coating_stack_validation_status == "FAIL_STACK_PRACTICALITY":
            coating_stack_validation_recommendation = (
                "Coating stack mass or thickness is too high; reduce layer thicknesses, "
                "select lower-density materials, or redesign the coating architecture."
            )
        else:
            coating_stack_validation_recommendation = (
                "Coating stack practicality needs review because one or more stack checks were unavailable."
            )

        results["coating_stack_validation_recommendation"] = coating_stack_validation_recommendation

        adhesion_risk_status = "NOT_EVALUATED"
        adhesion_risk_recommendation = (
            "Coating/bond-coat adhesion has not been evaluated."
        )

        if coating_stack_validation_status == "PLACEHOLDER_DATA_NOT_QUALIFIABLE":
            adhesion_risk_status = "REQUIRES_MODEL"
            adhesion_risk_recommendation = (
                "Add sourced bond strength, thermal-cycle, CTE-mismatch, and spallation data before accepting the coating stack."
            )
        elif coating_stack_validation_status == "FAIL_STACK_PRACTICALITY":
            adhesion_risk_status = "BLOCKED_BY_STACK_PRACTICALITY"
            adhesion_risk_recommendation = (
                "Resolve stack mass/thickness practicality before adhesion modelling."
            )

        results["coating_stack_adhesion_risk_status"] = adhesion_risk_status
        results["coating_stack_adhesion_risk_recommendation"] = adhesion_risk_recommendation

        spallation_fatigue_status = "NOT_EVALUATED"
        spallation_fatigue_recommendation = (
            "Coating stack cyclic fatigue and spallation risk have not been evaluated."
        )

        if adhesion_risk_status == "REQUIRES_MODEL":
            spallation_fatigue_status = "REQUIRES_MODEL"
            spallation_fatigue_recommendation = (
                "Add thermal-cycle count, strain range, bond-coat oxidation growth, coating toughness, "
                "and spallation-life data before accepting the coating stack."
            )
        elif adhesion_risk_status == "BLOCKED_BY_STACK_PRACTICALITY":
            spallation_fatigue_status = "BLOCKED_BY_STACK_PRACTICALITY"
            spallation_fatigue_recommendation = (
                "Resolve coating-stack practicality before cyclic fatigue or spallation modelling."
            )

        results["coating_stack_spallation_fatigue_status"] = spallation_fatigue_status
        results["coating_stack_spallation_fatigue_recommendation"] = spallation_fatigue_recommendation

        coating_stack_unresolved_blockers = []

        if uses_placeholder_data:
            coating_stack_unresolved_blockers.append(
                "Coating material properties are placeholder engineering values."
            )

        if bond_coat_uses_placeholder_data:
            coating_stack_unresolved_blockers.append(
                "Bond-coat/interlayer properties are placeholder engineering values."
            )

        if adhesion_risk_status == "REQUIRES_MODEL":
            coating_stack_unresolved_blockers.append(
                "Coating/bond-coat adhesion has not been modelled."
            )

        if spallation_fatigue_status == "REQUIRES_MODEL":
            coating_stack_unresolved_blockers.append(
                "Coating cyclic fatigue and spallation life have not been modelled."
            )

        if thermal_stress_failed_count > 0 and not solver_pass(results.get("bond_coat_validation_status")):
            coating_stack_unresolved_blockers.append(
                "Coating thermal stress remains unresolved by sourced bond-coat data."
            )

        if coating_stack_unresolved_blockers:
            coating_stack_development_status = "BLOCKED_PENDING_VALIDATION_DATA"
        else:
            coating_stack_development_status = "READY_FOR_HIGHER_FIDELITY_VALIDATION"

        results["coating_stack_unresolved_blockers"] = coating_stack_unresolved_blockers
        results["coating_stack_development_status"] = coating_stack_development_status

        coating_stack_source_data_requirements = [
            "Coating thermal conductivity versus temperature.",
            "Coating allowable surface temperature with source.",
            "Coating elastic modulus versus temperature.",
            "Coating thermal expansion coefficient versus temperature.",
            "Coating allowable stress or failure strain with source.",
            "Bond-coat/interlayer stress-reduction capability with source.",
            "Bond-coat/interlayer density and practical thickness range.",
            "Bond strength or adhesion strength data.",
            "Thermal-cycle fatigue or spallation-life data.",
        ]

        results["coating_stack_source_data_requirements"] = (
            coating_stack_source_data_requirements
        )

        coating_stack_source_data_completed = []
        coating_stack_source_data_missing = []

        coating_source_quality = (
            str(best_coating_candidate.get("source_quality", "")).lower()
            if best_coating_candidate else ""
        )
        bond_source_quality = str(bond_coat_best_source_quality).lower()

        coating_has_sourced_data = (
                "placeholder" not in coating_source_quality
                and "unknown" not in coating_source_quality
                and coating_source_quality != ""
        )

        bond_coat_has_sourced_data = (
                "placeholder" not in bond_source_quality
                and "unknown" not in bond_source_quality
                and bond_source_quality != ""
        )

        for requirement in coating_stack_source_data_requirements:
            requirement_lower = requirement.lower()

            if requirement_lower.startswith("coating"):
                if coating_has_sourced_data:
                    coating_stack_source_data_completed.append(requirement)
                else:
                    coating_stack_source_data_missing.append(requirement)
            elif requirement_lower.startswith("bond"):
                if bond_coat_has_sourced_data:
                    coating_stack_source_data_completed.append(requirement)
                else:
                    coating_stack_source_data_missing.append(requirement)
            else:
                coating_stack_source_data_missing.append(requirement)

        source_total = len(coating_stack_source_data_requirements)
        source_completed = len(coating_stack_source_data_completed)

        if source_total <= 0:
            coating_stack_source_data_status = "NO_REQUIREMENTS"
        elif source_completed == 0:
            coating_stack_source_data_status = "NO_SOURCED_DATA"
        elif source_completed < source_total:
            coating_stack_source_data_status = "PARTIAL_SOURCED_DATA"
        else:
            coating_stack_source_data_status = "COMPLETE_SOURCED_DATA"

        if source_total > 0:
            coating_stack_source_data_completion_fraction = source_completed / source_total
            coating_stack_source_data_completion_percent = 100.0 * coating_stack_source_data_completion_fraction
        else:
            coating_stack_source_data_completion_fraction = None
            coating_stack_source_data_completion_percent = None

        results["coating_stack_source_data_completed"] = coating_stack_source_data_completed
        results["coating_stack_source_data_missing"] = coating_stack_source_data_missing
        results["coating_stack_source_data_completed_count"] = len(coating_stack_source_data_completed)
        results["coating_stack_source_data_missing_count"] = len(coating_stack_source_data_missing)
        results["coating_stack_source_data_status"] = coating_stack_source_data_status
        results["coating_stack_source_data_completion_fraction"] = coating_stack_source_data_completion_fraction
        results["coating_stack_source_data_completion_percent"] = coating_stack_source_data_completion_percent

        source_data_missing_category_counts = {
            "coating": 0,
            "bond_coat": 0,
            "adhesion": 0,
            "fatigue_spallation": 0,
            "other": 0,
        }

        for missing_item in coating_stack_source_data_missing:
            missing_lower = str(missing_item).lower()

            if missing_lower.startswith("coating"):
                source_data_missing_category_counts["coating"] += 1
            elif missing_lower.startswith("bond"):
                source_data_missing_category_counts["bond_coat"] += 1
            elif "bond strength" in missing_lower or "adhesion" in missing_lower:
                source_data_missing_category_counts["adhesion"] += 1
            elif "fatigue" in missing_lower or "spallation" in missing_lower:
                source_data_missing_category_counts["fatigue_spallation"] += 1
            else:
                source_data_missing_category_counts["other"] += 1

        results["coating_stack_source_data_missing_category_counts"] = (
            source_data_missing_category_counts
        )

        source_data_dominant_missing_category = "NONE"

        if source_data_missing_category_counts:
            source_data_dominant_missing_category = max(
                source_data_missing_category_counts,
                key=source_data_missing_category_counts.get,
            )

            if source_data_missing_category_counts.get(
                    source_data_dominant_missing_category, 0
            ) <= 0:
                source_data_dominant_missing_category = "NONE"

        results["coating_stack_source_data_dominant_missing_category"] = (
            source_data_dominant_missing_category
        )

        if source_data_dominant_missing_category == "coating":
            source_data_category_recommendation = (
                "Prioritise sourced coating data first: temperature-dependent thermal conductivity, "
                "surface temperature limit, modulus, CTE, and allowable stress/failure strain."
            )
        elif source_data_dominant_missing_category == "bond_coat":
            source_data_category_recommendation = (
                "Prioritise sourced bond-coat/interlayer data first: stress-reduction capability, "
                "density, thickness range, modulus, CTE, and compatibility with the coating."
            )
        elif source_data_dominant_missing_category == "adhesion":
            source_data_category_recommendation = (
                "Prioritise adhesion data first: bond strength, interface temperature limits, "
                "CTE mismatch tolerance, and thermal-cycle degradation."
            )
        elif source_data_dominant_missing_category == "fatigue_spallation":
            source_data_category_recommendation = (
                "Prioritise fatigue/spallation data first: cycle count, strain range, coating toughness, "
                "bond-coat oxidation growth, and spallation-life correlations."
            )
        elif source_data_dominant_missing_category == "other":
            source_data_category_recommendation = (
                "Review uncategorised missing coating-stack source-data requirements."
            )
        else:
            source_data_category_recommendation = (
                "No missing coating-stack source-data category dominates."
            )

        results["coating_stack_source_data_category_recommendation"] = (
            source_data_category_recommendation
        )

        source_data_gap_weights = {
            "coating": 2.0,
            "bond_coat": 2.0,
            "adhesion": 1.5,
            "fatigue_spallation": 1.5,
            "other": 1.0,
        }

        source_data_weighted_missing_score = 0.0
        source_data_weighted_total_score = 0.0

        for requirement in coating_stack_source_data_requirements:
            requirement_lower = str(requirement).lower()

            if requirement_lower.startswith("coating"):
                category = "coating"
            elif requirement_lower.startswith("bond"):
                category = "bond_coat"
            elif "bond strength" in requirement_lower or "adhesion" in requirement_lower:
                category = "adhesion"
            elif "fatigue" in requirement_lower or "spallation" in requirement_lower:
                category = "fatigue_spallation"
            else:
                category = "other"

            weight = source_data_gap_weights.get(category, 1.0)
            source_data_weighted_total_score += weight

            if requirement in coating_stack_source_data_missing:
                source_data_weighted_missing_score += weight

        if source_data_weighted_total_score > 0:
            source_data_weighted_completion_fraction = (
                    1.0 - source_data_weighted_missing_score / source_data_weighted_total_score
            )
        else:
            source_data_weighted_completion_fraction = None

        if source_data_weighted_completion_fraction is not None:
            source_data_weighted_completion_percent = (
                    100.0 * source_data_weighted_completion_fraction
            )
        else:
            source_data_weighted_completion_percent = None

        results["coating_stack_source_data_weighted_missing_score"] = (
            source_data_weighted_missing_score
        )
        results["coating_stack_source_data_weighted_total_score"] = (
            source_data_weighted_total_score
        )
        results["coating_stack_source_data_weighted_completion_fraction"] = (
            source_data_weighted_completion_fraction
        )
        results["coating_stack_source_data_weighted_completion_percent"] = (
            source_data_weighted_completion_percent
        )

        if source_data_weighted_completion_percent is None:
            source_data_weighted_gate = "UNKNOWN"
        elif source_data_weighted_completion_percent >= 90.0:
            source_data_weighted_gate = "PASS"
        elif source_data_weighted_completion_percent >= 60.0:
            source_data_weighted_gate = "PARTIAL"
        else:
            source_data_weighted_gate = "FAIL"

        results["coating_stack_source_data_weighted_gate"] = source_data_weighted_gate

        if source_data_weighted_gate == "PASS":
            coating_stack_source_data_gate = "PASS"
        elif source_data_weighted_gate == "PARTIAL":
            coating_stack_source_data_gate = "FAIL_INCOMPLETE_SOURCE_DATA"
        elif coating_stack_source_data_status == "NO_SOURCED_DATA":
            coating_stack_source_data_gate = "FAIL_NO_SOURCE_DATA"
        elif source_data_weighted_gate == "FAIL":
            coating_stack_source_data_gate = "FAIL_INCOMPLETE_SOURCE_DATA"
        else:
            coating_stack_source_data_gate = "UNKNOWN"

        results["coating_stack_source_data_gate"] = coating_stack_source_data_gate

        results["coating_stack_source_data_weighted_gate"] = source_data_weighted_gate

        if source_data_weighted_gate == "PASS":
            coating_stack_source_data_gate = "PASS"
        elif coating_stack_source_data_status == "NO_SOURCED_DATA":
            coating_stack_source_data_gate = "FAIL_NO_SOURCE_DATA"
        elif source_data_weighted_gate in ("PARTIAL", "FAIL"):
            coating_stack_source_data_gate = "FAIL_INCOMPLETE_SOURCE_DATA"
        else:
            coating_stack_source_data_gate = "UNKNOWN"

        results["coating_stack_source_data_gate"] = coating_stack_source_data_gate

        if coating_stack_source_data_gate == "PASS":
            coating_stack_source_data_gate_reason = (
                "Coating-stack source-data gate passed the weighted source-data threshold."
            )
            coating_stack_source_data_gate_action_plan = [
                "Proceed to higher-fidelity coating-stack validation checks."
            ]
            coating_stack_source_data_severity = "GREEN"
            coating_stack_source_data_report_visibility = "SUMMARY_ONLY"

        elif coating_stack_source_data_gate == "FAIL_NO_SOURCE_DATA":
            coating_stack_source_data_gate_reason = (
                "No sourced coating-stack data is available. Current coating and bond-coat values are placeholder only."
            )
            coating_stack_source_data_gate_action_plan = [
                "Replace placeholder coating material properties with sourced temperature-dependent data.",
                "Replace placeholder bond-coat/interlayer values with sourced data.",
                "Add adhesion, thermal-cycle fatigue, and spallation-life source data.",
            ]
            coating_stack_source_data_severity = "RED"
            coating_stack_source_data_report_visibility = "EXPANDED"

        elif coating_stack_source_data_gate == "FAIL_INCOMPLETE_SOURCE_DATA":
            coating_stack_source_data_gate_reason = (
                "Coating-stack source data is incomplete and cannot support final validation."
            )
            coating_stack_source_data_gate_action_plan = [
                source_data_category_recommendation,
                "Complete all missing coating-stack source-data requirements before accepting the coating route.",
            ]
            coating_stack_source_data_severity = "ORANGE"
            coating_stack_source_data_report_visibility = "EXPANDED"

        else:
            coating_stack_source_data_gate_reason = (
                "Coating-stack source-data gate could not be determined."
            )
            coating_stack_source_data_gate_action_plan = [
                "Review coating-stack source-data inputs and requirement classification."
            ]
            coating_stack_source_data_severity = "YELLOW"
            coating_stack_source_data_report_visibility = "SUMMARY_PLUS_WARNINGS"

        results["coating_stack_source_data_gate_reason"] = coating_stack_source_data_gate_reason
        results["coating_stack_source_data_gate_action_plan"] = coating_stack_source_data_gate_action_plan
        results["coating_stack_source_data_status_line"] = (
            f"{coating_stack_source_data_gate} | "
            f"{source_data_weighted_gate} | "
            f"{source_data_weighted_completion_percent if source_data_weighted_completion_percent is not None else 'N/A'}%"
        )
        results["coating_stack_source_data_severity"] = coating_stack_source_data_severity
        results["coating_stack_source_data_report_visibility"] = coating_stack_source_data_report_visibility

        coating_stack_validation_readiness_score = 100

        if uses_placeholder_data:
            coating_stack_validation_readiness_score -= 25
        if bond_coat_uses_placeholder_data:
            coating_stack_validation_readiness_score -= 25
        if adhesion_risk_status == "REQUIRES_MODEL":
            coating_stack_validation_readiness_score -= 20
        if spallation_fatigue_status == "REQUIRES_MODEL":
            coating_stack_validation_readiness_score -= 20
        if results.get("explicit_coating_liner_status") == "FAIL_THERMAL_STRESS":
            coating_stack_validation_readiness_score -= 10

        coating_stack_validation_readiness_score = max(0, min(100, coating_stack_validation_readiness_score))

        if coating_stack_validation_readiness_score >= 90:
            coating_stack_validation_readiness_status = "READY_FOR_VALIDATION_REVIEW"
        elif coating_stack_validation_readiness_score >= 60:
            coating_stack_validation_readiness_status = "PARTIALLY_READY"
        elif coating_stack_validation_readiness_score >= 30:
            coating_stack_validation_readiness_status = "EARLY_VALIDATION_STAGE"
        else:
            coating_stack_validation_readiness_status = "NOT_READY"

        results["coating_stack_validation_readiness_score"] = coating_stack_validation_readiness_score
        results["coating_stack_validation_readiness_status"] = coating_stack_validation_readiness_status

        critical_blockers = 0
        major_blockers = 0
        minor_blockers = 0

        if results.get("explicit_coating_liner_status") == "FAIL_THERMAL_STRESS":
            critical_blockers += 1
        if uses_placeholder_data:
            major_blockers += 1
        if bond_coat_uses_placeholder_data:
            major_blockers += 1
        if adhesion_risk_status == "REQUIRES_MODEL":
            major_blockers += 1
        if spallation_fatigue_status == "REQUIRES_MODEL":
            major_blockers += 1
        if coating_stack_mass_status in ("MODERATE", "HIGH"):
            minor_blockers += 1
        if coating_stack_thickness_status in ("HIGH", "EXCESSIVE"):
            major_blockers += 1

        if critical_blockers > 0:
            coating_stack_validation_priority = "CRITICAL"
        elif major_blockers >= 3:
            coating_stack_validation_priority = "HIGH"
        elif major_blockers > 0:
            coating_stack_validation_priority = "MEDIUM"
        elif minor_blockers > 0:
            coating_stack_validation_priority = "LOW"
        else:
            coating_stack_validation_priority = "CLEAR"

        results["coating_stack_validation_critical_blocker_count"] = critical_blockers
        results["coating_stack_validation_major_blocker_count"] = major_blockers
        results["coating_stack_validation_minor_blocker_count"] = minor_blockers
        results["coating_stack_validation_priority"] = coating_stack_validation_priority

        if coating_stack_source_data_gate in ("FAIL_NO_SOURCE_DATA", "FAIL_INCOMPLETE_SOURCE_DATA"):
            coating_stack_validation_gate_status = "ADVISORY_ONLY"
        elif coating_stack_validation_priority in ("CRITICAL", "HIGH"):
            coating_stack_validation_gate_status = "ADVISORY_ONLY"
        elif coating_stack_validation_priority == "MEDIUM":
            coating_stack_validation_gate_status = "PROVISIONAL_ONLY"
        elif coating_stack_validation_priority == "LOW":
            coating_stack_validation_gate_status = "REVIEW_REQUIRED"
        else:
            coating_stack_validation_gate_status = "CAN_SUPPORT_VALIDATION"

        results["coating_stack_validation_gate_status"] = coating_stack_validation_gate_status

        if coating_stack_validation_gate_status == "ADVISORY_ONLY":
            coating_stack_validation_decision = "DEVELOPMENT_ROUTE_ONLY"
        elif coating_stack_validation_gate_status == "PROVISIONAL_ONLY":
            coating_stack_validation_decision = "PROVISIONAL_RECOVERY_ROUTE"
        elif coating_stack_validation_gate_status == "REVIEW_REQUIRED":
            coating_stack_validation_decision = "REVIEW_BEFORE_VALIDATION"
        else:
            coating_stack_validation_decision = "CAN_SUPPORT_FINAL_VALIDATION"

        results["coating_stack_validation_decision"] = coating_stack_validation_decision

        results["coating_stack_progress_summary"] = (
            f"{coating_stack_validation_readiness_status} "
            f"({coating_stack_validation_readiness_score}/100): "
            f"{len(coating_stack_unresolved_blockers)} unresolved blocker(s)."
        )

        results["coating_stack_status_line"] = (
            f"{coating_stack_validation_decision} | "
            f"{coating_stack_validation_gate_status} | "
            f"{coating_stack_validation_readiness_score}/100 | "
            f"{coating_stack_validation_priority}"
        )

        if coating_stack_validation_priority == "CRITICAL":
            coating_stack_status_severity = "RED"
        elif coating_stack_validation_priority == "HIGH":
            coating_stack_status_severity = "ORANGE"
        elif coating_stack_validation_priority == "MEDIUM":
            coating_stack_status_severity = "YELLOW"
        elif coating_stack_validation_priority == "LOW":
            coating_stack_status_severity = "BLUE"
        else:
            coating_stack_status_severity = "GREEN"

        results["coating_stack_status_severity"] = coating_stack_status_severity

        if coating_stack_status_severity in ("RED", "ORANGE"):
            coating_stack_report_visibility = "EXPANDED"
        elif coating_stack_status_severity == "YELLOW":
            coating_stack_report_visibility = "SUMMARY_PLUS_WARNINGS"
        else:
            coating_stack_report_visibility = "SUMMARY_ONLY"

        results["coating_stack_report_visibility"] = coating_stack_report_visibility

        if coating_stack_validation_readiness_score < 25:
            coating_stack_validation_milestone = "MILESTONE_1_CONCEPT_SCREENING"
        elif coating_stack_validation_readiness_score < 50:
            coating_stack_validation_milestone = "MILESTONE_2_PLACEHOLDER_RECOVERY_MODEL"
        elif coating_stack_validation_readiness_score < 75:
            coating_stack_validation_milestone = "MILESTONE_3_PARTIAL_VALIDATION_DATA"
        elif coating_stack_validation_readiness_score < 90:
            coating_stack_validation_milestone = "MILESTONE_4_PRE_VALIDATION_REVIEW"
        else:
            coating_stack_validation_milestone = "MILESTONE_5_VALIDATION_READY"

        results["coating_stack_validation_milestone"] = coating_stack_validation_milestone

        if coating_stack_validation_milestone == "MILESTONE_1_CONCEPT_SCREENING":
            coating_stack_next_milestone = "MILESTONE_2_PLACEHOLDER_RECOVERY_MODEL"
        elif coating_stack_validation_milestone == "MILESTONE_2_PLACEHOLDER_RECOVERY_MODEL":
            coating_stack_next_milestone = "MILESTONE_3_PARTIAL_VALIDATION_DATA"
        elif coating_stack_validation_milestone == "MILESTONE_3_PARTIAL_VALIDATION_DATA":
            coating_stack_next_milestone = "MILESTONE_4_PRE_VALIDATION_REVIEW"
        elif coating_stack_validation_milestone == "MILESTONE_4_PRE_VALIDATION_REVIEW":
            coating_stack_next_milestone = "MILESTONE_5_VALIDATION_READY"
        else:
            coating_stack_next_milestone = "NONE_VALIDATION_READY"

        results["coating_stack_next_milestone"] = coating_stack_next_milestone

        results["coating_stack_validation_summary"] = {
            "decision": coating_stack_validation_decision,
            "gate_status": coating_stack_validation_gate_status,
            "priority": coating_stack_validation_priority,
            "severity": coating_stack_status_severity,
            "readiness_score": coating_stack_validation_readiness_score,
            "readiness_status": coating_stack_validation_readiness_status,
            "development_status": coating_stack_development_status,
            "source_data_gate": coating_stack_source_data_gate,
            "source_data_weighted_gate": source_data_weighted_gate,
            "source_data_completion_percent": coating_stack_source_data_completion_percent,
            "weighted_source_data_completion_percent": source_data_weighted_completion_percent,
            "unresolved_blockers": coating_stack_unresolved_blockers,
            "next_milestone": coating_stack_next_milestone,
        }

        if coating_stack_validation_readiness_status == "READY_FOR_VALIDATION_REVIEW":
            coating_stack_validation_readiness_recommendation = (
                "Coating stack is ready for higher-fidelity validation review. Proceed with sourced material checks, manufacturing review, and final coupled thermal validation."
            )
        elif coating_stack_validation_readiness_status == "PARTIALLY_READY":
            coating_stack_validation_readiness_recommendation = (
                "Coating stack is partially ready. Clear the remaining unresolved blockers before accepting the coating path."
            )
        elif coating_stack_validation_readiness_status == "EARLY_VALIDATION_STAGE":
            coating_stack_validation_readiness_recommendation = (
                "Coating stack is still in early validation. Prioritise sourced coating/bond-coat data and missing failure-mode models."
            )
        else:
            coating_stack_validation_readiness_recommendation = (
                "Coating stack is not ready for validation. Treat all coating-based recovery as provisional only."
            )

        gate_transition_requirements = []

        if coating_stack_validation_gate_status == "ADVISORY_ONLY":
            gate_transition_requirements.extend([
                "Replace placeholder coating and bond-coat/interlayer data with sourced temperature-dependent data.",
                "Resolve coating thermal-stress failure using sourced mechanical properties and bond-coat/interlayer model.",
                "Add adhesion, cyclic fatigue, and spallation-life checks.",
            ])
        elif coating_stack_validation_gate_status == "PROVISIONAL_ONLY":
            gate_transition_requirements.append(
                "Review remaining medium-priority coating-stack blockers before allowing validation support."
            )
        elif coating_stack_validation_gate_status == "REVIEW_REQUIRED":
            gate_transition_requirements.append(
                "Review low-priority coating-stack concerns before final validation."
            )
        else:
            gate_transition_requirements.append(
                "Coating stack may support validation, pending full coupled thermal review."
            )

        coating_stack_validation_action_plan = []

        if uses_placeholder_data:
            coating_stack_validation_action_plan.append(
                "Replace coating placeholder values with sourced temperature-dependent coating material data."
            )

        if bond_coat_uses_placeholder_data:
            coating_stack_validation_action_plan.append(
                "Replace generic/placeholder bond-coat or interlayer values with sourced material data."
            )

        if adhesion_risk_status == "REQUIRES_MODEL":
            coating_stack_validation_action_plan.append(
                "Add adhesion model using bond strength, CTE mismatch, thermal-cycle range, and interface temperature."
            )

        if spallation_fatigue_status == "REQUIRES_MODEL":
            coating_stack_validation_action_plan.append(
                "Add cyclic fatigue and spallation-life model using cycle count, strain range, coating toughness, and bond-coat oxidation growth."
            )

        if results.get("explicit_coating_liner_status") == "FAIL_THERMAL_STRESS":
            coating_stack_validation_action_plan.append(
                "Re-run coating thermal-stress check using sourced coating and bond-coat mechanical properties."
            )

        if not coating_stack_validation_action_plan:
            coating_stack_validation_action_plan.append(
                "No coating-stack validation blockers remain; proceed to higher-fidelity coupled thermal validation."
            )

        results["coating_stack_validation_readiness_recommendation"] = (
            coating_stack_validation_readiness_recommendation
        )
        results["coating_stack_gate_transition_requirements"] = gate_transition_requirements
        results["coating_stack_validation_action_plan"] = coating_stack_validation_action_plan

    else:
        results["bond_coat_validation_status"] = "FAIL"
        results["bond_coat_validation_recommendation"] = (
            "No bond-coat/interlayer candidate currently closes the required stress-reduction gap."
        )

    if thermal_stress_failed_count > 0:
        results["explicit_coating_thermal_stress_status"] = "FAIL"
    else:
        results["explicit_coating_thermal_stress_status"] = "PASS_OR_NOT_EVALUATED"

    return results

def finalize_coating_stack_validation_gate(results):
    """
    Final conservative acceptance gate for coating/liner routes.

    This does not replace the explicit coating/liner preview.
    It decides whether that preview is allowed to support a final verdict.

    Current rule:
    - Placeholder coating or bond-coat data can support development routing only.
    - Missing adhesion/fatigue/spallation models block final validation.
    - Source-data gate must pass before coating can support final acceptance.
    """

    if results is None:
        return results

    explicit_status = results.get("explicit_coating_liner_status")
    source_data_gate = results.get("coating_stack_source_data_gate")
    weighted_gate = results.get("coating_stack_source_data_weighted_gate")
    validation_gate = results.get("coating_stack_validation_gate_status")
    development_status = results.get("coating_stack_development_status")
    unresolved_blockers = results.get("coating_stack_unresolved_blockers") or []

    coating_route_active = explicit_status in ("PASS", "FAIL_THERMAL_STRESS")

    final_blockers = []

    if not coating_route_active:
        acceptance_status = "NOT_APPLICABLE"
        final_blocker_gate = "NO_ACTIVE_COATING_ROUTE"

    else:
        if explicit_status == "PLACEHOLDER_DATA_NOT_QUALIFIABLE":
            final_blockers.append(
                "Explicit coating/liner preview uses placeholder engineering data."
            )

        if not solver_pass(source_data_gate):
            final_blockers.append(
                f"Coating-stack source-data gate is not passed: {source_data_gate}."
            )

        if not solver_pass(weighted_gate):
            final_blockers.append(
                f"Weighted source-data gate is not passed: {weighted_gate}."
            )

        if validation_gate in ("ADVISORY_ONLY", "PROVISIONAL_ONLY", "REVIEW_REQUIRED"):
            final_blockers.append(
                f"Coating-stack validation gate remains {validation_gate}."
            )

        if development_status == "BLOCKED_PENDING_VALIDATION_DATA":
            final_blockers.append(
                "Coating stack remains blocked pending validation data."
            )

        for blocker in unresolved_blockers:
            final_blockers.append(str(blocker))

        if final_blockers:
            acceptance_status = "DEVELOPMENT_ROUTE_ONLY"
            final_blocker_gate = "BLOCKED_PENDING_VALIDATION_DATA"
        else:
            acceptance_status = "VALIDATION_SUPPORT_ALLOWED"
            final_blocker_gate = "PASS"

    results["coating_stack_route_active"] = coating_route_active
    results["coating_stack_final_acceptance_status"] = acceptance_status
    results["coating_stack_final_validation_blocker_gate"] = final_blocker_gate
    results["coating_stack_final_validation_blockers"] = final_blockers
    results["coating_stack_final_validation_blocker_count"] = len(final_blockers)

    if acceptance_status == "VALIDATION_SUPPORT_ALLOWED":
        status_line = "Coating stack may support final validation, pending full coupled review."
        severity = "GREEN"
    elif acceptance_status == "DEVELOPMENT_ROUTE_ONLY":
        status_line = (
            "Coating stack is development-route-only and must not be treated as a final validated pass."
        )
        severity = "RED"
    else:
        status_line = "No active coating-stack final acceptance route."
        severity = "BLUE"

    results["coating_stack_final_acceptance_status_line"] = status_line
    results["coating_stack_final_acceptance_severity"] = severity

    results["coating_stack_report_sections"] = {
        "summary": [
            "coating_stack_final_acceptance_status",
            "coating_stack_final_acceptance_status_line",
            "coating_stack_validation_decision",
            "coating_stack_validation_gate_status",
            "coating_stack_validation_readiness_score",
            "coating_stack_validation_readiness_status",
            "coating_stack_development_status",
        ],
        "source_data": [
            "coating_stack_source_data_gate",
            "coating_stack_source_data_weighted_gate",
            "coating_stack_source_data_completion_percent",
            "coating_stack_source_data_weighted_completion_percent",
            "coating_stack_source_data_dominant_missing_category",
            "coating_stack_source_data_category_recommendation",
        ],
        "blockers": [
            "coating_stack_final_validation_blocker_count",
            "coating_stack_final_validation_blockers",
            "coating_stack_unresolved_blockers",
            "coating_stack_gate_transition_requirements",
            "coating_stack_validation_action_plan",
        ],
    }

    return results

def evaluate_coating_database_visibility(results):
    """
    Reports coating and bond-coat database availability.

    This does not validate a coating stack.
    It only exposes database readiness and confirms whether the
    available coating/bond-coat records are placeholder, partial, or sourced.
    """

    if results is None:
        return results

    if get_coating_database_summary is None:
        results["coating_database_status"] = "DATABASE_NOT_AVAILABLE"
        results["coating_database_reason"] = "material_database.py coating helpers are not available."
        return results

    summary = get_coating_database_summary()

    coating_count = summary.get("coating_candidate_count", 0)
    bond_count = summary.get("bond_coat_candidate_count", 0)
    coating_placeholder_count = summary.get("coating_placeholder_count", 0)
    bond_placeholder_count = summary.get("bond_coat_placeholder_count", 0)

    results["coating_database_status"] = "AVAILABLE"
    results["coating_candidate_count"] = coating_count
    results["bond_coat_candidate_count"] = bond_count
    results["coating_placeholder_count"] = coating_placeholder_count
    results["bond_coat_placeholder_count"] = bond_placeholder_count

    if coating_count <= 0 or bond_count <= 0:
        results["coating_database_readiness"] = "INCOMPLETE_DATABASE"
        results["coating_database_reason"] = "Coating or bond-coat candidate lists are empty."
    elif coating_placeholder_count > 0 or bond_placeholder_count > 0:
        results["coating_database_readiness"] = "PLACEHOLDER_DATABASE"
        results["coating_database_reason"] = (
            "Coating and bond-coat candidates exist, but one or more records are placeholder data. "
            "They cannot support final validation."
        )
    else:
        results["coating_database_readiness"] = "SOURCE_DATA_READY_FOR_SCREENING"
        results["coating_database_reason"] = (
            "Coating and bond-coat records are available without placeholder flags."
        )

    if get_coating_material_names is not None:
        results["available_coating_materials"] = ", ".join(get_coating_material_names())

    if get_bond_coat_names is not None:
        results["available_bond_coats"] = ", ".join(get_bond_coat_names())

    return results

def evaluate_active_coating_stack_selection(results):
    """
    Exposes the currently selected coating and bond coat.

    This is a selection/diagnostic layer only.
    It does not validate the coating stack and cannot produce final PASS.
    """

    if results is None:
        return results

    selected_coating = (
        results.get("selected_coating_material")
        or results.get("selected_tbc")
        or results.get("selected_coating")
        or "None"
    )

    selected_bond_coat = (
        results.get("selected_bond_coat")
        or results.get("selected_interlayer")
        or "None"
    )

    results["active_coating_material"] = selected_coating
    results["active_bond_coat"] = selected_bond_coat

    if selected_coating in (None, "", "None"):
        results["active_coating_status"] = "NO_COATING_SELECTED"
        results["active_coating_source_mode"] = "NOT_APPLICABLE"
        results["active_coating_source_quality"] = "N/A"
        results["active_coating_reason"] = "No thermal barrier coating or liner is selected."
    else:
        coating = None
        if get_coating_material_properties is not None:
            coating = get_coating_material_properties(selected_coating)

        if coating is None:
            results["active_coating_status"] = "COATING_NOT_FOUND"
            results["active_coating_source_mode"] = "INSUFFICIENT_SOURCE_MODE"
            results["active_coating_source_quality"] = "N/A"
            results["active_coating_reason"] = "Selected coating was not found in the material database."
        else:
            results["active_coating_status"] = "COATING_SELECTED"
            results["active_coating_family"] = coating.get("family")
            results["active_coating_role"] = coating.get("coating_role")
            results["active_coating_source_quality"] = coating.get("source_quality")
            results["active_coating_source_mode"] = coating.get("source_validation_mode")
            results["active_coating_source_score"] = coating.get("source_validation_score")
            results["active_coating_is_placeholder"] = 1 if coating.get("source_is_placeholder") else 0
            results["active_coating_thermal_conductivity"] = coating.get("thermal_conductivity")
            results["active_coating_max_surface_temperature"] = coating.get("max_surface_temperature")
            results["active_coating_max_practical_thickness"] = coating.get("max_practical_thickness")
            results["active_coating_reason"] = coating.get("source_validation_recommendation")

    if selected_bond_coat in (None, "", "None"):
        results["active_bond_coat_status"] = "NO_BOND_COAT_SELECTED"
        results["active_bond_coat_source_mode"] = "NOT_APPLICABLE"
        results["active_bond_coat_source_quality"] = "N/A"
        results["active_bond_coat_reason"] = "No bond coat or interlayer is selected."
    else:
        bond = None
        if get_bond_coat_properties is not None:
            bond = get_bond_coat_properties(selected_bond_coat)

        if bond is None:
            results["active_bond_coat_status"] = "BOND_COAT_NOT_FOUND"
            results["active_bond_coat_source_mode"] = "INSUFFICIENT_SOURCE_MODE"
            results["active_bond_coat_source_quality"] = "N/A"
            results["active_bond_coat_reason"] = "Selected bond coat was not found in the material database."
        else:
            results["active_bond_coat_status"] = "BOND_COAT_SELECTED"
            results["active_bond_coat_family"] = bond.get("family")
            results["active_bond_coat_source_quality"] = bond.get("source_quality")
            results["active_bond_coat_source_mode"] = bond.get("source_validation_mode")
            results["active_bond_coat_source_score"] = bond.get("source_validation_score")
            results["active_bond_coat_is_placeholder"] = 1 if bond.get("source_is_placeholder") else 0
            results["active_bond_coat_max_stress_reduction_fraction"] = bond.get("max_stress_reduction_fraction")
            results["active_bond_coat_max_practical_thickness"] = bond.get("max_practical_thickness")
            results["active_bond_coat_reason"] = bond.get("source_validation_recommendation")

    coating_mode = results.get("active_coating_source_mode")
    bond_mode = results.get("active_bond_coat_source_mode")

    if selected_coating in (None, "", "None") and selected_bond_coat in (None, "", "None"):
        stack_status = "NO_ACTIVE_COATING_STACK"
        stack_pass = 0
        stack_reason = "No coating stack is selected."
    elif coating_mode == SOURCED_VALIDATION_MODE and bond_mode == SOURCED_VALIDATION_MODE:
        stack_status = "ACTIVE_STACK_SOURCED_REVIEW_READY"
        stack_pass = 0
        stack_reason = (
            "Selected coating and bond coat have sourced validation modes, "
            "but thermal/stress stack validation has not yet been run."
        )
    else:
        stack_status = "ACTIVE_STACK_SOURCE_BLOCKED"
        stack_pass = 0
        stack_reason = (
            "A coating stack is selected, but one or more records are placeholder, "
            "partial, missing, or not sourced. Final validation is blocked."
        )

    results["active_coating_stack_status"] = stack_status
    results["active_coating_stack_pass"] = stack_pass
    results["active_coating_stack_reason"] = stack_reason

    return results

def build_coating_stack_evidence_matrix(results):
    """
    Builds a structured evidence matrix for the coating-stack route.

    Purpose:
    - Make missing validation evidence explicit.
    - Separate placeholder screening from real validation.
    - Provide a clean report/table-ready structure.
    """

    if results is None:
        return results

    explicit_status = results.get("explicit_coating_liner_status")
    coating_name = (
            results.get("explicit_coating_liner_material")
            or results.get("explicit_coating_liner_material_name")
            or results.get("explicit_coating_material")
            or results.get("coating_material_best_candidate_name")
    )
    coating_source_quality = str(
        results.get("explicit_coating_liner_source_quality") or ""
    ).lower()

    bond_name = results.get("bond_coat_best_candidate_name")
    bond_source_quality = str(
        results.get("bond_coat_best_source_quality") or ""
    ).lower()

    coating_uses_placeholder = bool(
        results.get("explicit_coating_liner_uses_placeholder_data")
    )
    bond_uses_placeholder = bool(
        results.get("bond_coat_uses_placeholder_data")
    )

    def evidence_item(
        category,
        requirement,
        status,
        blocking,
        current_basis,
        next_action,
        weight,
    ):
        return {
            "category": category,
            "requirement": requirement,
            "status": status,
            "blocking": bool(blocking),
            "current_basis": current_basis,
            "next_action": next_action,
            "weight": weight,
        }

    evidence = []

    evidence.append(
        evidence_item(
            category="coating_material",
            requirement="Named coating candidate selected",
            status="AVAILABLE" if coating_name else "MISSING",
            blocking=False if coating_name else True,
            current_basis=coating_name or "No coating candidate selected",
            next_action="Select a coating candidate from the coating material database.",
            weight=5,
        )
    )

    evidence.append(
        evidence_item(
            category="coating_material",
            requirement="Sourced coating thermal conductivity",
            status="PLACEHOLDER" if coating_uses_placeholder else "AVAILABLE",
            blocking=coating_uses_placeholder,
            current_basis=coating_source_quality or "unknown",
            next_action="Add sourced temperature-dependent coating thermal conductivity.",
            weight=15,
        )
    )

    evidence.append(
        evidence_item(
            category="coating_material",
            requirement="Sourced coating surface temperature limit",
            status="PLACEHOLDER" if coating_uses_placeholder else "AVAILABLE",
            blocking=coating_uses_placeholder,
            current_basis=coating_source_quality or "unknown",
            next_action="Add sourced coating surface temperature limit with citation.",
            weight=15,
        )
    )

    evidence.append(
        evidence_item(
            category="coating_mechanics",
            requirement="Sourced coating elastic modulus / CTE / Poisson ratio",
            status="PLACEHOLDER" if coating_uses_placeholder else "AVAILABLE",
            blocking=coating_uses_placeholder,
            current_basis=coating_source_quality or "unknown",
            next_action="Add sourced temperature-dependent mechanical properties.",
            weight=15,
        )
    )

    evidence.append(
        evidence_item(
            category="coating_mechanics",
            requirement="Allowable coating stress or failure strain",
            status="PLACEHOLDER" if coating_uses_placeholder else "AVAILABLE",
            blocking=coating_uses_placeholder,
            current_basis=coating_source_quality or "unknown",
            next_action="Add coating allowable stress, failure strain, fracture toughness, or equivalent failure criterion.",
            weight=15,
        )
    )

    evidence.append(
        evidence_item(
            category="bond_coat",
            requirement="Named bond-coat / interlayer candidate selected",
            status="AVAILABLE" if bond_name else "MISSING",
            blocking=False if bond_name else True,
            current_basis=bond_name or "No bond-coat candidate selected",
            next_action="Select or define a real bond-coat/interlayer material.",
            weight=10,
        )
    )

    evidence.append(
        evidence_item(
            category="bond_coat",
            requirement="Sourced bond-coat stress relief data",
            status="PLACEHOLDER" if bond_uses_placeholder else "AVAILABLE",
            blocking=bond_uses_placeholder,
            current_basis=bond_source_quality or "unknown",
            next_action="Replace generic bond-coat stress-reduction fraction with sourced material and test data.",
            weight=20,
        )
    )

    evidence.append(
        evidence_item(
            category="interface",
            requirement="Coating/bond-coat adhesion model",
            status="MISSING",
            blocking=True,
            current_basis=results.get("coating_stack_adhesion_risk_status", "REQUIRES_MODEL"),
            next_action="Add bond strength, interface temperature, CTE mismatch, and thermal-cycle adhesion check.",
            weight=25,
        )
    )

    evidence.append(
        evidence_item(
            category="life",
            requirement="Cyclic fatigue and spallation-life model",
            status="MISSING",
            blocking=True,
            current_basis=results.get("coating_stack_spallation_fatigue_status", "REQUIRES_MODEL"),
            next_action="Add cycle count, strain range, oxidation growth, coating toughness, and spallation-life model.",
            weight=25,
        )
    )

    evidence.append(
        evidence_item(
            category="analysis",
            requirement="Thermal stress resolved with sourced data",
            status="FAIL" if explicit_status == "FAIL_THERMAL_STRESS" else "AVAILABLE",
            blocking=explicit_status == "FAIL_THERMAL_STRESS",
            current_basis=explicit_status or "unknown",
            next_action="Re-run coating thermal-stress model using sourced coating and bond-coat data.",
            weight=25,
        )
    )

    total_weight = sum(item["weight"] for item in evidence)
    available_weight = sum(
        item["weight"]
        for item in evidence
        if item["status"] == "AVAILABLE"
    )
    blocking_items = [item for item in evidence if item["blocking"]]
    missing_items = [
        item for item in evidence
        if item["status"] in ("MISSING", "PLACEHOLDER", "FAIL")
    ]

    completion_percent = 0.0
    if total_weight > 0:
        completion_percent = 100.0 * available_weight / total_weight

    category_counts = {}

    for item in missing_items:
        category = item["category"]
        category_counts[category] = category_counts.get(category, 0) + 1

    dominant_category = None
    if category_counts:
        dominant_category = max(
            category_counts,
            key=lambda key: category_counts[key]
        )

    if not evidence:
        matrix_status = "NO_EVIDENCE"
    elif blocking_items:
        matrix_status = "BLOCKED"
    elif completion_percent < 90.0:
        matrix_status = "INCOMPLETE"
    else:
        matrix_status = "READY_FOR_REVIEW"

    if matrix_status == "READY_FOR_REVIEW":
        recommendation = (
            "Evidence matrix is complete enough for a validation review."
        )
    elif dominant_category == "coating_material":
        recommendation = (
            "Prioritise sourced coating thermal and mechanical material data."
        )
    elif dominant_category == "bond_coat":
        recommendation = (
            "Prioritise real bond-coat/interlayer material data and stress-relief evidence."
        )
    elif dominant_category == "interface":
        recommendation = (
            "Prioritise coating adhesion and interface failure modelling."
        )
    elif dominant_category == "life":
        recommendation = (
            "Prioritise cyclic fatigue and spallation-life modelling."
        )
    elif dominant_category == "analysis":
        recommendation = (
            "Prioritise resolving coating thermal stress using sourced material data."
        )
    else:
        recommendation = (
            "Complete missing coating-stack validation evidence before final acceptance."
        )

    results["coating_stack_evidence_matrix"] = evidence
    results["coating_stack_evidence_status"] = matrix_status
    results["coating_stack_evidence_total_weight"] = total_weight
    results["coating_stack_evidence_available_weight"] = available_weight
    results["coating_stack_evidence_completion_percent"] = completion_percent
    results["coating_stack_evidence_blocking_count"] = len(blocking_items)
    results["coating_stack_evidence_missing_count"] = len(missing_items)
    results["coating_stack_evidence_missing_category_counts"] = category_counts
    results["coating_stack_evidence_dominant_missing_category"] = dominant_category
    results["coating_stack_evidence_recommendation"] = recommendation
    results["coating_stack_evidence_blocking_items"] = blocking_items
    results["coating_stack_evidence_missing_items"] = missing_items

    return results

def build_coating_stack_validation_roadmap(results):
    """
    Converts the evidence matrix into staged coating-stack validation milestones.

    This is a roadmap/gate system, not a physics model.
    It tells LEAF what must be completed before the coating stack can move from:
        DEVELOPMENT_ROUTE_ONLY -> PROVISIONAL_REVIEW -> VALIDATION_SUPPORT_ALLOWED
    """

    if results is None:
        return results

    evidence = results.get("coating_stack_evidence_matrix") or []
    evidence_status = results.get("coating_stack_evidence_status")
    source_data_gate = results.get("coating_stack_source_data_gate")
    final_acceptance = results.get("coating_stack_final_acceptance_status")

    def has_available(requirement_text):
        for item in evidence:
            if item.get("requirement") == requirement_text:
                return item.get("status") == "AVAILABLE"
        return False

    milestones = []

    coating_name = (
            results.get("explicit_coating_liner_material")
            or results.get("explicit_coating_liner_material_name")
            or results.get("explicit_coating_material")
            or results.get("coating_material_best_candidate_name")
    )

    milestone_1_complete = bool(
        coating_name
        and results.get("explicit_coating_liner_status")
    )

    milestones.append({
        "id": "M1",
        "name": "Concept coating route identified",
        "status": "COMPLETE" if milestone_1_complete else "INCOMPLETE",
        "description": "A named coating/liner route exists and has been screened thermally.",
        "required_for": "Development route visibility",
        "blocking": not milestone_1_complete,
        "next_action": "Select and run an explicit coating/liner candidate."
    })

    milestone_2_complete = (
        has_available("Sourced coating thermal conductivity")
        and has_available("Sourced coating surface temperature limit")
        and has_available("Sourced coating elastic modulus / CTE / Poisson ratio")
        and has_available("Allowable coating stress or failure strain")
    )

    milestones.append({
        "id": "M2",
        "name": "Sourced coating material data",
        "status": "COMPLETE" if milestone_2_complete else "INCOMPLETE",
        "description": "Coating thermal and mechanical data are sourced rather than placeholder.",
        "required_for": "Provisional coating validation",
        "blocking": not milestone_2_complete,
        "next_action": "Add cited, temperature-dependent coating thermal/mechanical properties."
    })

    milestone_3_complete = (
        has_available("Named bond-coat / interlayer candidate selected")
        and has_available("Sourced bond-coat stress relief data")
    )

    milestones.append({
        "id": "M3",
        "name": "Sourced bond-coat/interlayer data",
        "status": "COMPLETE" if milestone_3_complete else "INCOMPLETE",
        "description": "Bond-coat/interlayer material and stress-relief capability are sourced.",
        "required_for": "Thermal-stress recovery validation",
        "blocking": not milestone_3_complete,
        "next_action": "Replace generic interlayer model with real sourced bond-coat/interlayer data."
    })

    milestone_4_complete = has_available("Coating/bond-coat adhesion model")

    milestones.append({
        "id": "M4",
        "name": "Adhesion/interface model",
        "status": "COMPLETE" if milestone_4_complete else "INCOMPLETE",
        "description": "Coating/bond-coat/substrate adhesion and interface failure are modelled.",
        "required_for": "Final coating-stack acceptance",
        "blocking": not milestone_4_complete,
        "next_action": "Add interface bond strength, CTE mismatch, interface temperature, and thermal-cycle adhesion check."
    })

    milestone_5_complete = has_available("Cyclic fatigue and spallation-life model")

    milestones.append({
        "id": "M5",
        "name": "Cyclic fatigue and spallation model",
        "status": "COMPLETE" if milestone_5_complete else "INCOMPLETE",
        "description": "Coating cyclic durability and spallation life are modelled.",
        "required_for": "Reusable-engine validation",
        "blocking": not milestone_5_complete,
        "next_action": "Add cycle count, strain range, bond-coat oxidation growth, toughness, and spallation-life model."
    })

    milestone_6_complete = has_available("Thermal stress resolved with sourced data")

    milestones.append({
        "id": "M6",
        "name": "Thermal stress resolved with sourced data",
        "status": "COMPLETE" if milestone_6_complete else "INCOMPLETE",
        "description": "Coating thermal stress is below allowable using sourced coating and bond-coat data.",
        "required_for": "Final coating-stack acceptance",
        "blocking": not milestone_6_complete,
        "next_action": "Re-run thermal-stress model after sourced coating and bond-coat data are added."
    })

    complete_count = sum(1 for item in milestones if item["status"] == "COMPLETE")
    incomplete_count = len(milestones) - complete_count
    blocking_milestones = [item for item in milestones if item["blocking"]]

    roadmap_completion_percent = 100.0 * complete_count / max(len(milestones), 1)

    if final_acceptance == "VALIDATION_SUPPORT_ALLOWED":
        roadmap_status = "VALIDATION_READY"
    elif source_data_gate == "PASS" and evidence_status in ("READY_FOR_REVIEW", "INCOMPLETE"):
        roadmap_status = "PROVISIONAL_REVIEW_READY"
    elif complete_count >= 1:
        roadmap_status = "DEVELOPMENT_ROADMAP_ACTIVE"
    else:
        roadmap_status = "NOT_STARTED"

    if blocking_milestones:
        next_milestone = blocking_milestones[0]
    else:
        next_milestone = None

    if next_milestone:
        next_action = next_milestone["next_action"]
        next_milestone_id = next_milestone["id"]
        next_milestone_name = next_milestone["name"]
    else:
        next_action = "All coating-stack roadmap milestones are complete. Proceed to final validation review."
        next_milestone_id = "NONE"
        next_milestone_name = "All milestones complete"

    results["coating_stack_validation_roadmap"] = milestones
    results["coating_stack_roadmap_status"] = roadmap_status
    results["coating_stack_roadmap_complete_count"] = complete_count
    results["coating_stack_roadmap_incomplete_count"] = incomplete_count
    results["coating_stack_roadmap_completion_percent"] = roadmap_completion_percent
    results["coating_stack_roadmap_blocking_milestones"] = blocking_milestones
    results["coating_stack_roadmap_next_milestone_id"] = next_milestone_id
    results["coating_stack_roadmap_next_milestone_name"] = next_milestone_name
    results["coating_stack_roadmap_next_action"] = next_action

    return results

def classify_coating_stack_data_mode(results):
    """
    Classifies whether the coating stack is using placeholder, partial,
    or sourced data.

    This is the bridge between today's placeholder database and future
    cited material datasets.
    """

    if results is None:
        return results

    coating_candidate = (
        results.get("selected_explicit_coating_liner_candidate")
        or results.get("coating_material_best_thermal_barrier_candidate")
        or results.get("coating_material_best_candidate")
        or {}
    )

    bond_candidate = (
        results.get("bond_coat_best_candidate")
        or {}
    )

    coating_source_type = str(
        coating_candidate.get("data_source_type")
        or coating_candidate.get("source_quality")
        or ""
    ).lower()

    bond_source_type = str(
        bond_candidate.get("data_source_type")
        or bond_candidate.get("source_quality")
        or ""
    ).lower()

    coating_has_citation = bool(coating_candidate.get("citation"))
    bond_has_citation = bool(bond_candidate.get("citation"))

    coating_temp_data = bool(
        coating_candidate.get("temperature_dependent_data_available")
    )
    coating_mech_data = bool(
        coating_candidate.get("mechanical_data_available")
    )
    coating_failure_data = bool(
        coating_candidate.get("failure_data_available")
    )

    bond_temp_data = bool(
        bond_candidate.get("temperature_dependent_data_available")
    )
    bond_stress_data = bool(
        bond_candidate.get("stress_relief_data_available")
    )
    bond_adhesion_data = bool(
        bond_candidate.get("adhesion_data_available")
    )
    bond_fatigue_data = bool(
        bond_candidate.get("fatigue_data_available")
    )

    placeholder_indicators = (
        "placeholder",
        "estimate",
        "approx",
        "engineering_reference",
        "generic",
    )

    coating_is_placeholder = any(
        word in coating_source_type for word in placeholder_indicators
    )
    bond_is_placeholder = any(
        word in bond_source_type for word in placeholder_indicators
    )

    coating_source_score = 0
    bond_source_score = 0

    if coating_has_citation:
        coating_source_score += 20
    if coating_temp_data:
        coating_source_score += 25
    if coating_mech_data:
        coating_source_score += 25
    if coating_failure_data:
        coating_source_score += 30

    if bond_has_citation:
        bond_source_score += 20
    if bond_temp_data:
        bond_source_score += 15
    if bond_stress_data:
        bond_source_score += 30
    if bond_adhesion_data:
        bond_source_score += 20
    if bond_fatigue_data:
        bond_source_score += 15

    combined_score = min(100, round((coating_source_score + bond_source_score) / 2.0, 2))

    if coating_is_placeholder or bond_is_placeholder:
        data_mode = "PLACEHOLDER_MODE"
    elif combined_score >= 85:
        data_mode = "SOURCED_VALIDATION_MODE"
    elif combined_score >= 45:
        data_mode = "PARTIAL_SOURCE_MODE"
    else:
        data_mode = "INSUFFICIENT_SOURCE_MODE"

    if data_mode == "SOURCED_VALIDATION_MODE":
        recommendation = "Coating stack has enough sourced data to enter validation review."
    elif data_mode == "PARTIAL_SOURCE_MODE":
        recommendation = "Some sourced coating-stack data exists, but more is required before final validation."
    elif data_mode == "PLACEHOLDER_MODE":
        recommendation = "Coating stack is still placeholder-driven. Keep as development route only."
    else:
        recommendation = "Coating-stack source data is insufficient. Add citations and temperature-dependent properties."

    results["coating_stack_data_mode"] = data_mode
    results["coating_stack_data_mode_score"] = combined_score
    results["coating_stack_coating_source_score"] = coating_source_score
    results["coating_stack_bond_source_score"] = bond_source_score
    results["coating_stack_coating_has_citation"] = coating_has_citation
    results["coating_stack_bond_has_citation"] = bond_has_citation
    results["coating_stack_data_mode_recommendation"] = recommendation

    return results

def build_coating_stack_certification_checklist(results):
    """
    Converts coating-stack status into a certification-style checklist.

    This is stricter than the evidence matrix:
    - Evidence matrix says what data exists.
    - Roadmap says what milestone is next.
    - Certification checklist says whether the route may support final design acceptance.
    """

    if results is None:
        return results

    data_mode = results.get("coating_stack_data_mode")
    source_gate = results.get("coating_stack_source_data_gate")
    final_acceptance = results.get("coating_stack_final_acceptance_status")
    evidence_status = results.get("coating_stack_evidence_status")
    roadmap_status = results.get("coating_stack_roadmap_status")
    explicit_status = results.get("explicit_coating_liner_status")
    thermal_stress_status = results.get("explicit_coating_thermal_stress_status")
    bond_validation_status = results.get("bond_coat_validation_status")
    adhesion_status = results.get("coating_stack_adhesion_risk_status")
    fatigue_status = results.get("coating_stack_spallation_fatigue_status")

    checklist = []

    def add_check(name, passed, critical, current_status, required_status, action):
        checklist.append({
            "name": name,
            "passed": bool(passed),
            "critical": bool(critical),
            "current_status": current_status,
            "required_status": required_status,
            "action": action,
        })

    add_check(
        name="Explicit coating/liner preview exists",
        passed=explicit_status in ("PASS", "FAIL_THERMAL_STRESS"),
        critical=True,
        current_status=explicit_status,
        required_status="PASS or stress-recoverable development route",
        action="Run explicit coating/liner preview."
    )

    add_check(
        name="Source-data gate passed",
        passed=source_gate == "PASS",
        critical=True,
        current_status=source_gate,
        required_status="PASS",
        action="Replace placeholder coating/bond-coat data with sourced data."
    )

    add_check(
        name="Sourced validation data mode",
        passed=data_mode == "SOURCED_VALIDATION_MODE",
        critical=True,
        current_status=data_mode,
        required_status="SOURCED_VALIDATION_MODE",
        action="Add citations, temperature-dependent properties, and failure data."
    )

    add_check(
        name="Evidence matrix ready",
        passed=evidence_status == "READY_FOR_REVIEW",
        critical=True,
        current_status=evidence_status,
        required_status="READY_FOR_REVIEW",
        action="Complete missing coating-stack evidence items."
    )

    add_check(
        name="Roadmap validation-ready",
        passed=roadmap_status == "VALIDATION_READY",
        critical=True,
        current_status=roadmap_status,
        required_status="VALIDATION_READY",
        action="Complete all coating-stack validation roadmap milestones."
    )

    add_check(
        name="Thermal stress resolved",
        passed=thermal_stress_status == "PASS",
        critical=True,
        current_status=thermal_stress_status,
        required_status="PASS",
        action="Resolve coating thermal stress using sourced coating and bond-coat data."
    )

    add_check(
        name="Bond-coat validation cleared",
        passed=bond_validation_status == "PASS",
        critical=True,
        current_status=bond_validation_status,
        required_status="PASS",
        action="Replace placeholder bond-coat/interlayer candidate with sourced validation data."
    )

    add_check(
        name="Adhesion model cleared",
        passed=adhesion_status == "PASS",
        critical=True,
        current_status=adhesion_status,
        required_status="PASS",
        action="Add coating/bond-coat/substrate adhesion model."
    )

    add_check(
        name="Spallation/fatigue model cleared",
        passed=fatigue_status == "PASS",
        critical=True,
        current_status=fatigue_status,
        required_status="PASS",
        action="Add cyclic fatigue and spallation-life model."
    )

    add_check(
        name="Final acceptance gate cleared",
        passed=final_acceptance == "VALIDATION_SUPPORT_ALLOWED",
        critical=True,
        current_status=final_acceptance,
        required_status="VALIDATION_SUPPORT_ALLOWED",
        action="Clear all final validation blockers before accepting coating-stack route."
    )

    passed_count = sum(1 for item in checklist if item["passed"])
    failed_count = len(checklist) - passed_count
    critical_failed_count = sum(
        1 for item in checklist
        if item["critical"] and not item["passed"]
    )

    score = 100.0 * passed_count / max(len(checklist), 1)

    if critical_failed_count > 0:
        certification_status = "CERTIFICATION_BLOCKED"
    elif score >= 100.0:
        certification_status = "CERTIFICATION_READY"
    elif score >= 75.0:
        certification_status = "PROVISIONAL_CERTIFICATION_REVIEW"
    else:
        certification_status = "NOT_CERTIFICATION_READY"

    failed_actions = [
        item["action"]
        for item in checklist
        if not item["passed"]
    ]

    if certification_status == "CERTIFICATION_READY":
        recommendation = (
            "Coating stack is ready to support final certification review."
        )
    elif certification_status == "PROVISIONAL_CERTIFICATION_REVIEW":
        recommendation = (
            "Coating stack is close to review, but remaining checklist items must be closed."
        )
    else:
        recommendation = (
            "Coating stack remains blocked for final certification."
        )

    results["coating_stack_certification_checklist"] = checklist
    results["coating_stack_certification_status"] = certification_status
    results["coating_stack_certification_score"] = score
    results["coating_stack_certification_passed_count"] = passed_count
    results["coating_stack_certification_failed_count"] = failed_count
    results["coating_stack_certification_critical_failed_count"] = critical_failed_count
    results["coating_stack_certification_failed_actions"] = failed_actions
    results["coating_stack_certification_recommendation"] = recommendation

    return results

def build_coating_stack_risk_register(results):
    """
    Builds a risk register for the coating-stack development route.

    This converts validation blockers into ranked engineering risks.
    """

    if results is None:
        return results

    evidence_blockers = results.get("coating_stack_evidence_blocking_items") or []
    final_blockers = results.get("coating_stack_final_validation_blockers") or []
    checklist = results.get("coating_stack_certification_checklist") or []

    risks = []

    def add_risk(
        risk_id,
        title,
        category,
        likelihood,
        consequence,
        mitigation,
        trigger,
        owner="Coating validation",
    ):
        score = likelihood * consequence

        if score >= 20:
            severity = "CRITICAL"
        elif score >= 12:
            severity = "HIGH"
        elif score >= 6:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        risks.append({
            "id": risk_id,
            "title": title,
            "category": category,
            "likelihood": likelihood,
            "consequence": consequence,
            "score": score,
            "severity": severity,
            "mitigation": mitigation,
            "trigger": trigger,
            "owner": owner,
        })

    if results.get("explicit_coating_liner_uses_placeholder_data"):
        add_risk(
            "CSR-001",
            "Placeholder coating material data",
            "source_data",
            5,
            5,
            "Replace placeholder coating thermal/mechanical properties with sourced temperature-dependent data.",
            "Coating source quality is placeholder."
        )

    if results.get("bond_coat_uses_placeholder_data"):
        add_risk(
            "CSR-002",
            "Placeholder bond-coat/interlayer data",
            "source_data",
            5,
            5,
            "Replace generic bond-coat/interlayer model with sourced material and stress-relief data.",
            "Bond-coat source quality is placeholder."
        )

    if solver_fail(results.get("explicit_coating_thermal_stress_status")):
        add_risk(
            "CSR-003",
            "Coating thermal stress failure",
            "mechanical",
            4,
            5,
            "Resolve thermal stress using sourced coating properties, bond-coat compliance, and strain/failure criteria.",
            "Explicit coating thermal stress status is FAIL."
        )

    if not solver_pass(results.get("coating_stack_adhesion_risk_status")):
        add_risk(
            "CSR-004",
            "Coating/bond-coat adhesion unvalidated",
            "interface",
            5,
            5,
            "Add adhesion model using bond strength, CTE mismatch, interface temperature, and thermal cycling.",
            "Adhesion status is not PASS."
        )

    if not solver_pass(results.get("coating_stack_spallation_fatigue_status")):
        add_risk(
            "CSR-005",
            "Spallation and cyclic fatigue unvalidated",
            "life",
            5,
            5,
            "Add cycle-life and spallation model using strain range, cycle count, oxidation growth, and toughness.",
            "Spallation/fatigue status is not PASS."
        )

    if not solver_pass(results.get("coating_stack_source_data_gate")):
        add_risk(
            "CSR-006",
            "Source-data gate failed",
            "validation_gate",
            5,
            4,
            "Complete coating-stack source-data requirements before final validation.",
            "Source-data gate is not PASS."
        )

    if results.get("coating_stack_certification_status") != "CERTIFICATION_READY":
        add_risk(
            "CSR-007",
            "Certification checklist blocked",
            "certification",
            5,
            4,
            "Close all critical certification checklist items before allowing final acceptance.",
            "Certification status is not CERTIFICATION_READY."
        )

    if results.get("coating_stack_final_acceptance_status") != "VALIDATION_SUPPORT_ALLOWED":
        add_risk(
            "CSR-008",
            "Final coating-stack acceptance blocked",
            "final_acceptance",
            5,
            5,
            "Keep coating route as development-only until all final validation blockers are cleared.",
            "Final acceptance status is not VALIDATION_SUPPORT_ALLOWED."
        )

    for index, item in enumerate(evidence_blockers[:5], start=1):
        requirement = item.get("requirement", "Unknown evidence blocker")
        add_risk(
            f"CSR-E{index:02d}",
            f"Evidence blocker: {requirement}",
            item.get("category", "evidence"),
            4,
            4,
            item.get("next_action", "Complete missing evidence item."),
            item.get("current_basis", "Evidence item is blocking.")
        )

    for index, blocker in enumerate(final_blockers[:5], start=1):
        add_risk(
            f"CSR-F{index:02d}",
            f"Final blocker: {blocker}",
            "final_blocker",
            4,
            4,
            "Resolve this final validation blocker before accepting the coating-stack route.",
            blocker
        )

    for index, item in enumerate(checklist[:5], start=1):
        if not item.get("passed"):
            add_risk(
                f"CSR-C{index:02d}",
                f"Checklist failed: {item.get('name')}",
                "checklist",
                4,
                4,
                item.get("action", "Close failed checklist item."),
                item.get("current_status", "Checklist item failed.")
            )

    # De-duplicate by title while keeping highest score.
    deduped = {}

    for risk in risks:
        title = risk["title"]
        existing = deduped.get(title)

        if existing is None or risk["score"] > existing["score"]:
            deduped[title] = risk

    risks = list(deduped.values())
    risks.sort(key=lambda item: item["score"], reverse=True)

    critical_count = sum(1 for item in risks if item["severity"] == "CRITICAL")
    high_count = sum(1 for item in risks if item["severity"] == "HIGH")
    medium_count = sum(1 for item in risks if item["severity"] == "MEDIUM")
    low_count = sum(1 for item in risks if item["severity"] == "LOW")

    top_risk = risks[0] if risks else None

    if critical_count > 0:
        risk_status = "CRITICAL_RISK"
    elif high_count > 0:
        risk_status = "HIGH_RISK"
    elif medium_count > 0:
        risk_status = "MEDIUM_RISK"
    elif risks:
        risk_status = "LOW_RISK"
    else:
        risk_status = "NO_REGISTERED_RISKS"

    if top_risk:
        recommendation = top_risk["mitigation"]
    else:
        recommendation = "No coating-stack risks currently registered."

    results["coating_stack_risk_register"] = risks
    results["coating_stack_risk_status"] = risk_status
    results["coating_stack_risk_count"] = len(risks)
    results["coating_stack_critical_risk_count"] = critical_count
    results["coating_stack_high_risk_count"] = high_count
    results["coating_stack_medium_risk_count"] = medium_count
    results["coating_stack_low_risk_count"] = low_count
    results["coating_stack_top_risk"] = top_risk
    results["coating_stack_top_risk_title"] = top_risk.get("title") if top_risk else None
    results["coating_stack_top_risk_mitigation"] = top_risk.get("mitigation") if top_risk else None
    results["coating_stack_risk_recommendation"] = recommendation

    return results

def build_coating_stack_risk_burndown_plan(results):
    """
    Converts the coating-stack risk register into an ordered burn-down plan.

    Purpose:
    - Rank what to fix first.
    - Group risks into engineering work packages.
    - Define the current validation phase.
    """

    if results is None:
        return results

    risks = results.get("coating_stack_risk_register") or []
    certification_status = results.get("coating_stack_certification_status")
    data_mode = results.get("coating_stack_data_mode")
    roadmap_status = results.get("coating_stack_roadmap_status")
    final_acceptance = results.get("coating_stack_final_acceptance_status")

    work_packages = {
        "WP1_SOURCE_DATA": {
            "name": "Source coating and bond-coat material data",
            "risk_categories": ("source_data", "validation_gate"),
            "priority": 1,
            "risks": [],
            "actions": [],
        },
        "WP2_THERMAL_STRESS": {
            "name": "Resolve coating thermal stress",
            "risk_categories": ("mechanical", "analysis"),
            "priority": 2,
            "risks": [],
            "actions": [],
        },
        "WP3_INTERFACE": {
            "name": "Validate adhesion and interface behaviour",
            "risk_categories": ("interface",),
            "priority": 3,
            "risks": [],
            "actions": [],
        },
        "WP4_LIFE": {
            "name": "Validate fatigue and spallation life",
            "risk_categories": ("life",),
            "priority": 4,
            "risks": [],
            "actions": [],
        },
        "WP5_CERTIFICATION": {
            "name": "Close final certification and acceptance gates",
            "risk_categories": ("certification", "final_acceptance", "final_blocker", "checklist", "evidence"),
            "priority": 5,
            "risks": [],
            "actions": [],
        },
    }

    for risk in risks:
        category = risk.get("category")
        mitigation = risk.get("mitigation")

        assigned = False

        for package in work_packages.values():
            if category in package["risk_categories"]:
                package["risks"].append(risk)

                if mitigation and mitigation not in package["actions"]:
                    package["actions"].append(mitigation)

                assigned = True
                break

        if not assigned:
            package = work_packages["WP5_CERTIFICATION"]
            package["risks"].append(risk)

            if mitigation and mitigation not in package["actions"]:
                package["actions"].append(mitigation)

    package_list = []

    for package_id, package in work_packages.items():
        package_risks = package["risks"]
        open_risk_count = len(package_risks)
        max_score = max((risk.get("score", 0) for risk in package_risks), default=0)

        if open_risk_count == 0:
            status = "COMPLETE"
        elif max_score >= 20:
            status = "CRITICAL_OPEN"
        elif max_score >= 12:
            status = "OPEN"
        else:
            status = "MONITOR"

        package_list.append({
            "id": package_id,
            "name": package["name"],
            "priority": package["priority"],
            "status": status,
            "open_risk_count": open_risk_count,
            "max_risk_score": max_score,
            "actions": package["actions"],
            "risks": package_risks,
        })

    package_list.sort(key=lambda item: item["priority"])

    open_packages = [
        package for package in package_list
        if package["status"] != "COMPLETE"
    ]

    next_package = open_packages[0] if open_packages else None

    total_open_risks = sum(package["open_risk_count"] for package in package_list)
    complete_packages = sum(1 for package in package_list if package["status"] == "COMPLETE")
    completion_percent = 100.0 * complete_packages / max(len(package_list), 1)

    if final_acceptance == "VALIDATION_SUPPORT_ALLOWED":
        validation_phase = "PHASE_5_VALIDATION_SUPPORT_ALLOWED"
    elif certification_status == "CERTIFICATION_READY":
        validation_phase = "PHASE_4_CERTIFICATION_REVIEW"
    elif roadmap_status in ("PROVISIONAL_REVIEW_READY", "VALIDATION_READY"):
        validation_phase = "PHASE_3_PROVISIONAL_VALIDATION_REVIEW"
    elif data_mode in ("PARTIAL_SOURCE_MODE", "SOURCED_VALIDATION_MODE"):
        validation_phase = "PHASE_2_SOURCE_DATA_INTEGRATION"
    else:
        validation_phase = "PHASE_1_PLACEHOLDER_DEVELOPMENT"

    if next_package:
        next_package_id = next_package["id"]
        next_package_name = next_package["name"]
        next_actions = next_package["actions"] or [
            "Close open risks in this work package."
        ]
    else:
        next_package_id = "NONE"
        next_package_name = "All work packages complete"
        next_actions = [
            "Proceed to final coating-stack validation review."
        ]

    if validation_phase == "PHASE_1_PLACEHOLDER_DEVELOPMENT":
        phase_recommendation = (
            "Do not optimise acceptance criteria yet. First replace placeholder source data."
        )
    elif validation_phase == "PHASE_2_SOURCE_DATA_INTEGRATION":
        phase_recommendation = (
            "Integrate sourced coating and bond-coat data, then re-run stress and evidence gates."
        )
    elif validation_phase == "PHASE_3_PROVISIONAL_VALIDATION_REVIEW":
        phase_recommendation = (
            "Review remaining provisional validation blockers before certification."
        )
    elif validation_phase == "PHASE_4_CERTIFICATION_REVIEW":
        phase_recommendation = (
            "Certification checklist is ready; perform final engineering review."
        )
    else:
        phase_recommendation = (
            "Coating stack may support final validation, subject to coupled design review."
        )

    results["coating_stack_risk_burndown_plan"] = package_list
    results["coating_stack_risk_burndown_status"] = (
        "OPEN" if total_open_risks > 0 else "COMPLETE"
    )
    results["coating_stack_risk_burndown_open_risk_count"] = total_open_risks
    results["coating_stack_risk_burndown_complete_package_count"] = complete_packages
    results["coating_stack_risk_burndown_completion_percent"] = completion_percent
    results["coating_stack_next_work_package_id"] = next_package_id
    results["coating_stack_next_work_package_name"] = next_package_name
    results["coating_stack_next_work_package_actions"] = next_actions
    results["coating_stack_validation_phase"] = validation_phase
    results["coating_stack_validation_phase_recommendation"] = phase_recommendation

    return results

def build_coating_stack_priority_action_plan(results):
    """
    Builds a compact, non-duplicated priority action plan from the full
    coating-stack risk system.

    The full risk register is intentionally verbose.
    This function creates the short engineering view:
        - what is the root issue?
        - what should be fixed first?
        - what gates will it unlock?
    """

    if results is None:
        return results

    data_mode = results.get("coating_stack_data_mode")
    source_gate = results.get("coating_stack_source_data_gate")
    thermal_stress_status = results.get("explicit_coating_thermal_stress_status")
    bond_status = results.get("bond_coat_validation_status")
    adhesion_status = results.get("coating_stack_adhesion_risk_status")
    fatigue_status = results.get("coating_stack_spallation_fatigue_status")
    final_acceptance = results.get("coating_stack_final_acceptance_status")

    actions = []

    def add_action(
        action_id,
        title,
        priority,
        status,
        reason,
        action,
        unlocks,
    ):
        actions.append({
            "id": action_id,
            "title": title,
            "priority": priority,
            "status": status,
            "reason": reason,
            "action": action,
            "unlocks": unlocks,
        })

    if data_mode != "SOURCED_VALIDATION_MODE" or not solver_pass(source_gate):
        add_action(
            "CPA-001",
            "Replace placeholder coating data",
            1,
            "OPEN",
            f"Data mode is {data_mode}; source gate is {source_gate}.",
            "Add cited, temperature-dependent coating thermal conductivity, surface temperature limit, elastic modulus, CTE, Poisson ratio, and allowable stress/failure strain.",
            "Unlocks sourced coating material gate, evidence matrix progress, certification checklist progress, and thermal-stress re-analysis.",
        )

    if not solver_pass(bond_status):
        add_action(
            "CPA-002",
            "Replace placeholder bond-coat/interlayer data",
            2,
            "OPEN",
            f"Bond-coat validation status is {bond_status}.",
            "Replace generic compliant interlayer values with sourced bond-coat/interlayer data including stress relief, thickness limits, density, thermal expansion, and compatibility notes.",
            "Unlocks bond-coat validation, stress recovery credibility, and final coating-stack acceptance path.",
        )

    if not solver_pass(thermal_stress_status):
        add_action(
            "CPA-003",
            "Resolve coating thermal stress",
            3,
            "OPEN",
            f"Thermal stress status is {thermal_stress_status}.",
            "Re-run coating thermal stress using sourced coating and bond-coat mechanical properties, then check stress margin against allowable stress or failure strain.",
            "Unlocks thermal-stress resolved milestone and removes a critical final blocker.",
        )

    if not solver_pass(adhesion_status):
        add_action(
            "CPA-004",
            "Add adhesion/interface model",
            4,
            "OPEN",
            f"Adhesion status is {adhesion_status}.",
            "Add coating/bond-coat/substrate adhesion check using bond strength, CTE mismatch, interface temperature, and thermal-cycle range.",
            "Unlocks interface validation and final certification readiness.",
        )

    if not solver_pass(fatigue_status):
        add_action(
            "CPA-005",
            "Add fatigue/spallation-life model",
            5,
            "OPEN",
            f"Spallation/fatigue status is {fatigue_status}.",
            "Add cyclic fatigue and spallation model using cycle count, strain range, coating toughness, oxidation growth, and bond-coat degradation.",
            "Unlocks reusable-engine coating-stack validation.",
        )

    if final_acceptance != "VALIDATION_SUPPORT_ALLOWED":
        add_action(
            "CPA-006",
            "Run final coating-stack acceptance review",
            6,
            "BLOCKED",
            f"Final acceptance status is {final_acceptance}.",
            "Only run this after source data, bond-coat data, stress, adhesion, fatigue, and spallation checks are complete.",
            "Allows coating stack to move from DEVELOPMENT_ROUTE_ONLY to validation support.",
        )

    actions.sort(key=lambda item: item["priority"])

    open_actions = [item for item in actions if item["status"] == "OPEN"]
    blocked_actions = [item for item in actions if item["status"] == "BLOCKED"]

    if open_actions:
        next_action = open_actions[0]
    elif blocked_actions:
        next_action = blocked_actions[0]
    else:
        next_action = None

    if next_action:
        summary = f"Next action: {next_action['title']} — {next_action['action']}"
        status = "OPEN"
    else:
        summary = "No coating-stack priority actions remain open."
        status = "COMPLETE"

    results["coating_stack_priority_action_plan"] = actions
    results["coating_stack_priority_action_status"] = status
    results["coating_stack_priority_action_count"] = len(actions)
    results["coating_stack_open_priority_action_count"] = len(open_actions)
    results["coating_stack_blocked_priority_action_count"] = len(blocked_actions)
    results["coating_stack_next_priority_action"] = next_action
    results["coating_stack_next_priority_action_title"] = (
        next_action.get("title") if next_action else None
    )
    results["coating_stack_next_priority_action_summary"] = summary

    return results

def build_coating_stack_source_data_checklist(results):
    """
    Creates a compact checklist of the source-data items needed to move the
    coating stack out of placeholder mode.

    Unlike the first placeholder version, this responds to the current result
    keys so the checklist can become COMPLETE when sourced data is later added.
    """

    if results is None:
        return results

    coating_uses_placeholder = bool(
        results.get("explicit_coating_liner_uses_placeholder_data")
    )
    bond_uses_placeholder = bool(
        results.get("bond_coat_uses_placeholder_data")
    )

    adhesion_status = results.get("coating_stack_adhesion_risk_status")
    fatigue_status = results.get("coating_stack_spallation_fatigue_status")
    stress_status = results.get("explicit_coating_thermal_stress_status")

    coating_has_citation = bool(results.get("coating_stack_coating_has_citation"))
    bond_has_citation = bool(results.get("coating_stack_bond_has_citation"))

    data_mode = results.get("coating_stack_data_mode")
    source_gate = results.get("coating_stack_source_data_gate")

    checklist = []

    def add_item(item_id, title, passed, action, evidence=None):
        checklist.append({
            "id": item_id,
            "title": title,
            "status": "COMPLETE" if passed else "MISSING",
            "passed": bool(passed),
            "action": action,
            "evidence": evidence,
        })

    coating_sourced = (
        not coating_uses_placeholder
        and coating_has_citation
        and data_mode in ("PARTIAL_SOURCE_MODE", "SOURCED_VALIDATION_MODE")
    )

    bond_sourced = (
        not bond_uses_placeholder
        and bond_has_citation
        and data_mode in ("PARTIAL_SOURCE_MODE", "SOURCED_VALIDATION_MODE")
    )

    add_item(
        "CSD-001",
        "Coating thermal conductivity",
        coating_sourced,
        "Add cited temperature-dependent coating thermal conductivity.",
        results.get("explicit_coating_liner_source_quality"),
    )
    add_item(
        "CSD-002",
        "Coating surface temperature limit",
        coating_sourced,
        "Add cited maximum surface temperature / operating limit.",
        results.get("explicit_coating_liner_source_quality"),
    )
    add_item(
        "CSD-003",
        "Coating mechanical properties",
        coating_sourced,
        "Add elastic modulus, Poisson ratio, CTE, and temperature dependence.",
        results.get("explicit_coating_liner_source_quality"),
    )
    add_item(
        "CSD-004",
        "Coating failure criterion",
        coating_sourced,
        "Add allowable stress, failure strain, fracture toughness, or equivalent criterion.",
        results.get("explicit_coating_liner_source_quality"),
    )
    add_item(
        "CSD-005",
        "Bond-coat stress relief data",
        bond_sourced,
        "Add sourced stress reduction or compliance data for the bond-coat/interlayer.",
        results.get("bond_coat_best_source_quality"),
    )
    add_item(
        "CSD-006",
        "Adhesion/interface data",
        adhesion_status == "PASS",
        "Add bond strength, interface temperature, and CTE mismatch data.",
        adhesion_status,
    )
    add_item(
        "CSD-007",
        "Thermal-cycle fatigue data",
        fatigue_status == "PASS",
        "Add cycle count, strain range, fatigue limit, and degradation model.",
        fatigue_status,
    )
    add_item(
        "CSD-008",
        "Spallation-life data",
        fatigue_status == "PASS",
        "Add spallation-life or coating delamination criterion.",
        fatigue_status,
    )
    add_item(
        "CSD-009",
        "Thermal stress resolved with sourced data",
        stress_status == "PASS" and source_gate == "PASS",
        "Resolve coating thermal stress using sourced coating and bond-coat data.",
        stress_status,
    )

    completed = [item for item in checklist if item["passed"]]
    missing = [item for item in checklist if not item["passed"]]

    results["coating_stack_source_data_checklist"] = checklist
    results["coating_stack_source_data_checklist_completed"] = completed
    results["coating_stack_source_data_checklist_missing"] = missing
    results["coating_stack_source_data_checklist_status"] = (
        "COMPLETE" if not missing else "INCOMPLETE"
    )
    results["coating_stack_source_data_checklist_completed_count"] = len(completed)
    results["coating_stack_source_data_checklist_missing_count"] = len(missing)

    return results

def build_coating_stack_executive_summary(results):
    """
    Produces compact coating-stack summary labels for UI/report use.

    This prevents the final report from relying only on long blocker lists.
    """

    if results is None:
        return results

    final_acceptance = results.get("coating_stack_final_acceptance_status")
    certification_status = results.get("coating_stack_certification_status")
    risk_status = results.get("coating_stack_risk_status")
    burndown_status = results.get("coating_stack_risk_burndown_status")
    validation_phase = results.get("coating_stack_validation_phase")
    data_mode = results.get("coating_stack_data_mode")
    source_gate = results.get("coating_stack_source_data_gate")
    evidence_status = results.get("coating_stack_evidence_status")
    next_work_package = results.get("coating_stack_next_work_package_name")
    top_risk = results.get("coating_stack_top_risk_title")

    if final_acceptance == "VALIDATION_SUPPORT_ALLOWED":
        acceptance_label = "CAN_SUPPORT_FINAL_VALIDATION"
        acceptance_colour = "GREEN"
        acceptance_rank = 5
    elif certification_status == "CERTIFICATION_READY":
        acceptance_label = "READY_FOR_CERTIFICATION_REVIEW"
        acceptance_colour = "BLUE"
        acceptance_rank = 4
    elif data_mode in ("PARTIAL_SOURCE_MODE", "SOURCED_VALIDATION_MODE"):
        acceptance_label = "SOURCE_DATA_INTEGRATION_IN_PROGRESS"
        acceptance_colour = "YELLOW"
        acceptance_rank = 3
    elif final_acceptance == "DEVELOPMENT_ROUTE_ONLY":
        acceptance_label = "DEVELOPMENT_ROUTE_ONLY"
        acceptance_colour = "ORANGE"
        acceptance_rank = 2
    else:
        acceptance_label = "NOT_ACCEPTABLE_FOR_VALIDATION"
        acceptance_colour = "RED"
        acceptance_rank = 1

    if risk_status == "CRITICAL_RISK":
        risk_label = "CRITICAL_RISK_BLOCKED"
    elif risk_status == "HIGH_RISK":
        risk_label = "HIGH_RISK_REVIEW_REQUIRED"
    elif risk_status == "MEDIUM_RISK":
        risk_label = "MEDIUM_RISK_MONITOR"
    elif risk_status == "LOW_RISK":
        risk_label = "LOW_RISK"
    else:
        risk_label = "NO_REGISTERED_RISKS"

    if source_gate == "PASS" and data_mode == "SOURCED_VALIDATION_MODE":
        source_label = "SOURCE_DATA_READY"
    elif data_mode == "PARTIAL_SOURCE_MODE":
        source_label = "PARTIAL_SOURCE_DATA"
    elif data_mode == "PLACEHOLDER_MODE":
        source_label = "PLACEHOLDER_DATA"
    else:
        source_label = "SOURCE_DATA_INSUFFICIENT"

    if evidence_status == "READY_FOR_REVIEW":
        evidence_label = "EVIDENCE_READY"
    elif evidence_status == "BLOCKED":
        evidence_label = "EVIDENCE_BLOCKED"
    elif evidence_status == "INCOMPLETE":
        evidence_label = "EVIDENCE_INCOMPLETE"
    else:
        evidence_label = "EVIDENCE_UNKNOWN"

    executive_summary = {
        "acceptance_label": acceptance_label,
        "acceptance_colour": acceptance_colour,
        "acceptance_rank": acceptance_rank,
        "risk_label": risk_label,
        "source_label": source_label,
        "evidence_label": evidence_label,
        "validation_phase": validation_phase,
        "next_work_package": next_work_package,
        "top_risk": top_risk,
        "certification_status": certification_status,
        "final_acceptance": final_acceptance,
        "burndown_status": burndown_status,
    }

    status_line = (
        f"{acceptance_label} | {source_label} | {risk_label} | {validation_phase}"
    )

    if acceptance_label == "CAN_SUPPORT_FINAL_VALIDATION":
        plain_language_summary = (
            "Coating stack may support final validation, subject to coupled design review."
        )
    elif acceptance_label == "READY_FOR_CERTIFICATION_REVIEW":
        plain_language_summary = (
            "Coating stack is ready for certification review but is not yet accepted."
        )
    elif acceptance_label == "SOURCE_DATA_INTEGRATION_IN_PROGRESS":
        plain_language_summary = (
            "Coating stack has some source-data progress but is not final-validation-ready."
        )
    elif acceptance_label == "DEVELOPMENT_ROUTE_ONLY":
        plain_language_summary = (
            "Coating stack is useful as a development route but must not be accepted as validated."
        )
    else:
        plain_language_summary = (
            "Coating stack is not acceptable for validation in its current state."
        )

    if top_risk:
        plain_language_summary += f" Top risk: {top_risk}."

    if next_work_package:
        plain_language_summary += f" Next work package: {next_work_package}."

    results["coating_stack_acceptance_label"] = acceptance_label
    results["coating_stack_acceptance_colour"] = acceptance_colour
    results["coating_stack_acceptance_rank"] = acceptance_rank
    results["coating_stack_risk_label"] = risk_label
    results["coating_stack_source_label"] = source_label
    results["coating_stack_evidence_label"] = evidence_label
    results["coating_stack_executive_status_line"] = status_line
    results["coating_stack_plain_language_summary"] = plain_language_summary
    results["coating_stack_executive_summary"] = executive_summary

    return results

def build_coating_stack_dashboard_payload(results):
    """
    Builds a compact dashboard/export payload for coating-stack validation.

    This is designed for:
    - GUI summary panels
    - report exports
    - future JSON/CSV export
    - avoiding dozens of scattered result keys
    """

    if results is None:
        return results

    payload = {
        "executive": {
            "acceptance_label": results.get("coating_stack_acceptance_label"),
            "acceptance_colour": results.get("coating_stack_acceptance_colour"),
            "acceptance_rank": results.get("coating_stack_acceptance_rank"),
            "status_line": results.get("coating_stack_executive_status_line"),
            "plain_language_summary": results.get("coating_stack_plain_language_summary"),
        },
        "validation": {
            "final_acceptance_status": results.get("coating_stack_final_acceptance_status"),
            "final_blocker_gate": results.get("coating_stack_final_validation_blocker_gate"),
            "validation_decision": results.get("coating_stack_validation_decision"),
            "validation_gate_status": results.get("coating_stack_validation_gate_status"),
            "validation_phase": results.get("coating_stack_validation_phase"),
            "certification_status": results.get("coating_stack_certification_status"),
            "certification_score": results.get("coating_stack_certification_score"),
            "critical_failed_count": results.get("coating_stack_certification_critical_failed_count"),
        },
        "source_data": {
            "data_mode": results.get("coating_stack_data_mode"),
            "data_mode_score": results.get("coating_stack_data_mode_score"),
            "source_gate": results.get("coating_stack_source_data_gate"),
            "weighted_gate": results.get("coating_stack_source_data_weighted_gate"),
            "completion_percent": results.get("coating_stack_source_data_completion_percent"),
            "weighted_completion_percent": results.get("coating_stack_source_data_weighted_completion_percent"),
            "dominant_missing_category": results.get("coating_stack_source_data_dominant_missing_category"),
            "recommendation": results.get("coating_stack_source_data_category_recommendation"),
        },
        "evidence": {
            "status": results.get("coating_stack_evidence_status"),
            "completion_percent": results.get("coating_stack_evidence_completion_percent"),
            "blocking_count": results.get("coating_stack_evidence_blocking_count"),
            "missing_count": results.get("coating_stack_evidence_missing_count"),
            "dominant_missing_category": results.get("coating_stack_evidence_dominant_missing_category"),
            "recommendation": results.get("coating_stack_evidence_recommendation"),
        },
        "risk": {
            "risk_status": results.get("coating_stack_risk_status"),
            "risk_count": results.get("coating_stack_risk_count"),
            "critical_risk_count": results.get("coating_stack_critical_risk_count"),
            "high_risk_count": results.get("coating_stack_high_risk_count"),
            "top_risk": results.get("coating_stack_top_risk_title"),
            "top_risk_mitigation": results.get("coating_stack_top_risk_mitigation"),
            "risk_recommendation": results.get("coating_stack_risk_recommendation"),
        },
        "priority_action": {
            "status": results.get("coating_stack_priority_action_status"),
            "action_count": results.get("coating_stack_priority_action_count"),
            "open_action_count": results.get("coating_stack_open_priority_action_count"),
            "blocked_action_count": results.get("coating_stack_blocked_priority_action_count"),
            "next_action_title": results.get("coating_stack_next_priority_action_title"),
            "next_action_summary": results.get("coating_stack_next_priority_action_summary"),
        },
        "burndown": {
            "status": results.get("coating_stack_risk_burndown_status"),
            "open_risk_count": results.get("coating_stack_risk_burndown_open_risk_count"),
            "completion_percent": results.get("coating_stack_risk_burndown_completion_percent"),
            "next_work_package_id": results.get("coating_stack_next_work_package_id"),
            "next_work_package_name": results.get("coating_stack_next_work_package_name"),
            "next_work_package_actions": results.get("coating_stack_next_work_package_actions"),
            "phase_recommendation": results.get("coating_stack_validation_phase_recommendation"),
        },
        "thermal_preview": {
            "explicit_status": results.get("explicit_coating_liner_status"),
            "coating_material": (
                results.get("explicit_coating_liner_material")
                or results.get("explicit_coating_liner_material_name")
                or results.get("explicit_coating_material")
                or results.get("coating_material_best_candidate_name")
            ),
            "coating_source_quality": results.get("explicit_coating_liner_source_quality"),
            "uses_placeholder_data": results.get("explicit_coating_liner_uses_placeholder_data"),
            "thermal_stress_status": results.get("explicit_coating_thermal_stress_status"),
            "required_stress_reduction_fraction": results.get("explicit_coating_required_stress_reduction_fraction"),
            "bond_coat_validation_status": results.get("bond_coat_validation_status"),
            "bond_coat_best_candidate": results.get("bond_coat_best_candidate_name"),
        },
    }

    compact_lines = []

    compact_lines.append(
        f"Acceptance: {payload['executive']['acceptance_label']}"
    )
    compact_lines.append(
        f"Phase: {payload['validation']['validation_phase']}"
    )
    compact_lines.append(
        f"Data: {payload['source_data']['data_mode']} / {payload['source_data']['source_gate']}"
    )
    compact_lines.append(
        f"Certification: {payload['validation']['certification_status']} "
        f"({payload['validation']['certification_score']}/100)"
    )
    compact_lines.append(
        f"Risk: {payload['risk']['risk_status']} | Top: {payload['risk']['top_risk']}"
    )
    compact_lines.append(
        f"Next: {payload['priority_action']['next_action_title']}"
    )

    payload["compact_lines"] = compact_lines

    results["coating_stack_dashboard_payload"] = payload
    results["coating_stack_dashboard_compact_lines"] = compact_lines
    results["coating_stack_dashboard_status"] = "COMPLETE"

    return results

def build_coating_stack_ui_warning_cards(results):
    """
    Builds compact UI warning cards for the coating-stack system.

    These are intended for:
    - main window warning panels
    - future dashboard widgets
    - compact report summaries
    """

    if results is None:
        return results

    cards = []

    def add_card(card_id, title, severity, message, action, visible=True):
        severity_rank = {
            "GREEN": 0,
            "BLUE": 1,
            "YELLOW": 2,
            "ORANGE": 3,
            "RED": 4,
        }.get(severity, 2)

        cards.append({
            "id": card_id,
            "title": title,
            "severity": severity,
            "severity_rank": severity_rank,
            "message": message,
            "action": action,
            "visible": bool(visible),
        })

    acceptance_label = results.get("coating_stack_acceptance_label")
    data_mode = results.get("coating_stack_data_mode")
    source_gate = results.get("coating_stack_source_data_gate")
    certification_status = results.get("coating_stack_certification_status")
    risk_status = results.get("coating_stack_risk_status")
    validation_phase = results.get("coating_stack_validation_phase")
    top_risk = results.get("coating_stack_top_risk_title")
    next_wp = results.get("coating_stack_next_work_package_name")
    explicit_status = results.get("explicit_coating_liner_status")

    if acceptance_label != "CAN_SUPPORT_FINAL_VALIDATION":
        add_card(
            "COAT-W001",
            "Coating stack not final-valid",
            "RED",
            f"Acceptance label is {acceptance_label}.",
            "Keep coating/liner route as development-only until final validation gates are cleared.",
        )

    if data_mode != "SOURCED_VALIDATION_MODE":
        add_card(
            "COAT-W002",
            "Coating stack source data incomplete",
            "RED" if data_mode == "PLACEHOLDER_MODE" else "ORANGE",
            f"Data mode is {data_mode}; source gate is {source_gate}.",
            "Add cited coating and bond-coat material data with temperature-dependent properties.",
        )

    if certification_status != "CERTIFICATION_READY":
        add_card(
            "COAT-W003",
            "Certification checklist blocked",
            "RED",
            f"Certification status is {certification_status}.",
            "Close all critical certification checklist items before final acceptance.",
        )

    if risk_status in ("CRITICAL_RISK", "HIGH_RISK"):
        add_card(
            "COAT-W004",
            "High coating-stack risk",
            "RED" if risk_status == "CRITICAL_RISK" else "ORANGE",
            f"Risk status is {risk_status}. Top risk: {top_risk}.",
            results.get("coating_stack_top_risk_mitigation")
            or "Resolve critical/high coating-stack risks.",
        )

    if explicit_status == "FAIL_THERMAL_STRESS":
        add_card(
            "COAT-W005",
            "Coating thermal stress failure",
            "RED",
            "Explicit coating/liner preview fails first-pass thermal stress.",
            "Use sourced coating and bond-coat data to resolve stress before accepting the route.",
        )

    if validation_phase == "PHASE_1_PLACEHOLDER_DEVELOPMENT":
        add_card(
            "COAT-W006",
            "Placeholder development phase",
            "ORANGE",
            "Coating stack is still in placeholder development phase.",
            "Prioritise source-data replacement before tuning acceptance criteria.",
        )

    if next_wp:
        add_card(
            "COAT-I001",
            "Next coating-stack work package",
            "BLUE",
            f"Next work package: {next_wp}.",
            "Complete this package before moving to the next validation phase.",
        )

    visible_cards = [card for card in cards if card["visible"]]
    visible_cards.sort(key=lambda item: item["severity_rank"], reverse=True)

    max_rank = max((card["severity_rank"] for card in visible_cards), default=0)

    if max_rank >= 4:
        ui_severity = "RED"
    elif max_rank == 3:
        ui_severity = "ORANGE"
    elif max_rank == 2:
        ui_severity = "YELLOW"
    elif max_rank == 1:
        ui_severity = "BLUE"
    else:
        ui_severity = "GREEN"

    results["coating_stack_ui_warning_cards"] = visible_cards
    results["coating_stack_ui_warning_card_count"] = len(visible_cards)
    results["coating_stack_ui_severity"] = ui_severity
    results["coating_stack_ui_top_card"] = visible_cards[0] if visible_cards else None
    results["coating_stack_ui_top_message"] = (
        visible_cards[0]["message"] if visible_cards else "No coating-stack warnings."
    )
    results["coating_stack_ui_top_action"] = (
        visible_cards[0]["action"] if visible_cards else "No action required."
    )

    return results

def evaluate_explicit_coating_thermal_resistance_preview(results):
    """
    Explicit coating thermal-resistance preview v1.

    This estimates the first-order thermal effect of an active coating / liner.

    Important:
    - This is a development preview only.
    - Placeholder coating data can never generate validation PASS.
    - This does not replace the axial regen validation or best full-engine selector.
    """

    if results is None:
        return results

    def safe_float(value, default=None):
        try:
            if value in (None, ""):
                return default
            return float(value)
        except Exception:
            return default

    selected_coating = (
        results.get("selected_coating_material")
        or results.get("active_coating_material")
        or results.get("selected_tbc")
        or results.get("selected_coating")
        or "None"
    )

    if selected_coating in (None, "", "None"):
        results["explicit_coating_preview_status"] = "NO_COATING_SELECTED"
        results["explicit_coating_preview_pass"] = 0
        results["explicit_coating_preview_reason"] = "No coating or refractory liner is selected."
        return results

    if get_coating_material_properties is None:
        results["explicit_coating_preview_status"] = "COATING_DATABASE_NOT_AVAILABLE"
        results["explicit_coating_preview_pass"] = 0
        results["explicit_coating_preview_reason"] = "Coating database helper is not available."
        return results

    coating = get_coating_material_properties(selected_coating)

    if coating is None:
        results["explicit_coating_preview_status"] = "COATING_NOT_FOUND"
        results["explicit_coating_preview_pass"] = 0
        results["explicit_coating_preview_reason"] = (
            f"Selected coating '{selected_coating}' was not found in the coating database."
        )
        return results

    base_hot_wall_temperature = safe_float(
        results.get("best_full_engine_regen_max_hot_wall_temperature")
        or results.get("variable_thermal_max_hot_wall_temperature")
        or results.get("recommended_preview_max_hot_wall_temperature")
        or results.get("regen_axial_max_hot_wall_temperature")
        or results.get("hot_gas_side_wall_temperature")
    )

    heat_flux = safe_float(
        results.get("recommended_preview_max_heat_flux")
        or results.get("regen_axial_max_heat_flux")
        or results.get("hot_gas_heat_flux")
        or results.get("regen_heat_flux")
    )

    liner_limit = safe_float(
        results.get("material_max_wall_temperature"),
        900.0,
    )

    coating_thickness = safe_float(
        results.get("coating_thickness"),
        None,
    )

    if coating_thickness is None or coating_thickness <= 0.0:
        coating_thickness = safe_float(
            coating.get("max_practical_thickness"),
            0.00025,
        )

    coating_k = safe_float(coating.get("thermal_conductivity"), None)
    coating_surface_limit = safe_float(coating.get("max_surface_temperature"), None)
    coating_max_practical_thickness = safe_float(coating.get("max_practical_thickness"), None)
    coating_density = safe_float(coating.get("density"), None)

    if base_hot_wall_temperature is None or heat_flux is None or coating_k in (None, 0.0):
        results["explicit_coating_preview_status"] = "INSUFFICIENT_THERMAL_DATA"
        results["explicit_coating_preview_pass"] = 0
        results["explicit_coating_preview_reason"] = (
            "Missing base wall temperature, heat flux, or coating conductivity."
        )
        return results

    coating_resistance = coating_thickness / coating_k
    coating_temperature_drop = heat_flux * coating_resistance

    raw_liner_hot_wall_temperature = base_hot_wall_temperature - coating_temperature_drop
    coating_surface_temperature = base_hot_wall_temperature

    coated_liner_hot_wall_temperature = raw_liner_hot_wall_temperature

    coating_physical_sanity_status = "PASS"
    coating_physical_sanity_reason = "Coating preview temperatures are physically plausible."

    if raw_liner_hot_wall_temperature < 200.0:
        coating_physical_sanity_status = "FAIL_UNPHYSICAL_LINER_TEMPERATURE"
        coating_physical_sanity_reason = (
            "The first-order coating resistance estimate predicts an unrealistically low liner temperature. "
            "Treat this preview as diagnostic only; a coupled coating/regen heat-balance model is required."
        )
        coated_liner_hot_wall_temperature = 200.0

    elif raw_liner_hot_wall_temperature > coating_surface_temperature:
        coating_physical_sanity_status = "FAIL_TEMPERATURE_ORDER"
        coating_physical_sanity_reason = (
            "The coating preview predicted liner temperature above the hot surface temperature."
        )

    liner_margin = liner_limit - coated_liner_hot_wall_temperature

    if coating_surface_limit is None:
        surface_margin = None
    else:
        surface_margin = coating_surface_limit - coating_surface_temperature

    source_mode = coating.get("source_validation_mode", "PLACEHOLDER_MODE")
    source_is_placeholder = bool(coating.get("source_is_placeholder"))

    thickness_margin = None
    if coating_max_practical_thickness is not None:
        thickness_margin = coating_max_practical_thickness - coating_thickness

    # Approximate coating mass using total hot-gas surface area if available.
    surface_area_total = safe_float(
        results.get("regen_axial_total_hot_gas_surface_area")
        or results.get("coating_surface_area_total")
        or results.get("local_hot_gas_surface_area"),
        None,
    )

    coating_mass = None
    if surface_area_total is not None and coating_density is not None:
        coating_mass = surface_area_total * coating_thickness * coating_density

    thermal_screen_pass = liner_margin >= 0.0

    if surface_margin is not None and surface_margin < 0.0:
        thermal_screen_pass = False

    if thickness_margin is not None and thickness_margin < 0.0:
        thermal_screen_pass = False

    if source_is_placeholder or source_mode != "SOURCED_VALIDATION_MODE":
        status = "DEVELOPMENT_PREVIEW_SOURCE_BLOCKED"
        pass_flag = 0
        reason = (
            "Coating thermal preview was calculated, but coating source data is not sufficient "
            "for validation. Placeholder or partial coating data cannot produce PASS."
        )
    elif thermal_screen_pass:
        status = "THERMAL_SCREEN_PASS_SOURCE_READY"
        pass_flag = 0
        reason = (
            "Coating thermal preview passes the first-order screen, but full coating-stack "
            "thermal stress, adhesion, fatigue, and spallation validation are still required."
        )
    else:
        status = "THERMAL_SCREEN_FAIL"
        pass_flag = 0
        reason = "Selected coating does not pass the first-order thermal screen."

    results["explicit_coating_preview_status"] = status
    results["explicit_coating_preview_pass"] = pass_flag
    results["explicit_coating_preview_reason"] = reason

    results["explicit_coating_material"] = coating.get("name", selected_coating)
    results["explicit_coating_family"] = coating.get("family")
    results["explicit_coating_role"] = coating.get("coating_role")
    results["explicit_coating_source_quality"] = coating.get("source_quality")
    results["explicit_coating_source_mode"] = source_mode
    results["explicit_coating_is_placeholder"] = 1 if source_is_placeholder else 0

    results["explicit_coating_thickness"] = coating_thickness
    results["explicit_coating_thermal_conductivity"] = coating_k
    results["explicit_coating_thermal_resistance"] = coating_resistance
    results["explicit_coating_temperature_drop"] = coating_temperature_drop

    results["explicit_coating_base_hot_wall_temperature"] = base_hot_wall_temperature
    results["explicit_coating_liner_hot_wall_temperature"] = coated_liner_hot_wall_temperature
    results["explicit_coating_surface_temperature"] = coating_surface_temperature

    results["explicit_coating_liner_limit"] = liner_limit
    results["explicit_coating_liner_margin"] = liner_margin
    results["explicit_coating_surface_limit"] = coating_surface_limit
    results["explicit_coating_surface_margin"] = surface_margin

    results["explicit_coating_max_practical_thickness"] = coating_max_practical_thickness
    results["explicit_coating_thickness_margin"] = thickness_margin
    results["explicit_coating_density"] = coating_density
    results["explicit_coating_surface_area_total"] = surface_area_total
    results["explicit_coating_mass_total"] = coating_mass

    results["explicit_coating_raw_liner_hot_wall_temperature"] = raw_liner_hot_wall_temperature
    results["explicit_coating_physical_sanity_status"] = coating_physical_sanity_status
    results["explicit_coating_physical_sanity_reason"] = coating_physical_sanity_reason

    return results

def build_coating_stack_export_summary(results):
    """
    Builds CSV/report-friendly coating-stack export rows.

    These rows avoid dumping nested dictionaries directly into exports.
    """

    if results is None:
        return results

    rows = []

    def add_row(section, key, label, value, unit="", severity=""):
        rows.append({
            "section": section,
            "key": key,
            "label": label,
            "value": value,
            "unit": unit,
            "severity": severity,
        })

    add_row(
        "executive",
        "coating_stack_acceptance_label",
        "Acceptance Label",
        results.get("coating_stack_acceptance_label"),
        severity=results.get("coating_stack_acceptance_colour", ""),
    )
    add_row(
        "executive",
        "coating_stack_plain_language_summary",
        "Plain Language Summary",
        results.get("coating_stack_plain_language_summary"),
    )
    add_row(
        "executive",
        "coating_stack_executive_status_line",
        "Executive Status Line",
        results.get("coating_stack_executive_status_line"),
    )

    add_row(
        "validation",
        "coating_stack_final_acceptance_status",
        "Final Acceptance Status",
        results.get("coating_stack_final_acceptance_status"),
    )
    add_row(
        "validation",
        "coating_stack_final_validation_blocker_gate",
        "Final Validation Blocker Gate",
        results.get("coating_stack_final_validation_blocker_gate"),
    )
    add_row(
        "validation",
        "coating_stack_validation_phase",
        "Validation Phase",
        results.get("coating_stack_validation_phase"),
    )
    add_row(
        "validation",
        "coating_stack_certification_status",
        "Certification Status",
        results.get("coating_stack_certification_status"),
    )
    add_row(
        "validation",
        "coating_stack_certification_score",
        "Certification Score",
        results.get("coating_stack_certification_score"),
        unit="/100",
    )

    add_row(
        "source_data",
        "coating_stack_data_mode",
        "Data Mode",
        results.get("coating_stack_data_mode"),
    )
    add_row(
        "source_data",
        "coating_stack_source_data_gate",
        "Source Data Gate",
        results.get("coating_stack_source_data_gate"),
    )
    add_row(
        "source_data",
        "coating_stack_source_data_weighted_gate",
        "Weighted Source Gate",
        results.get("coating_stack_source_data_weighted_gate"),
    )
    add_row(
        "source_data",
        "coating_stack_source_data_completion_percent",
        "Source Data Completion",
        results.get("coating_stack_source_data_completion_percent"),
        unit="%",
    )
    add_row(
        "source_data",
        "coating_stack_source_data_weighted_completion_percent",
        "Weighted Source Data Completion",
        results.get("coating_stack_source_data_weighted_completion_percent"),
        unit="%",
    )

    add_row(
        "risk",
        "coating_stack_risk_status",
        "Risk Status",
        results.get("coating_stack_risk_status"),
    )
    add_row(
        "risk",
        "coating_stack_top_risk_title",
        "Top Risk",
        results.get("coating_stack_top_risk_title"),
    )
    add_row(
        "risk",
        "coating_stack_top_risk_mitigation",
        "Top Risk Mitigation",
        results.get("coating_stack_top_risk_mitigation"),
    )
    add_row(
        "risk",
        "coating_stack_risk_count",
        "Risk Count",
        results.get("coating_stack_risk_count"),
    )
    add_row(
        "risk",
        "coating_stack_critical_risk_count",
        "Critical Risk Count",
        results.get("coating_stack_critical_risk_count"),
    )

    add_row(
        "burndown",
        "coating_stack_risk_burndown_status",
        "Risk Burn-Down Status",
        results.get("coating_stack_risk_burndown_status"),
    )
    add_row(
        "burndown",
        "coating_stack_next_work_package_name",
        "Next Work Package",
        results.get("coating_stack_next_work_package_name"),
    )
    add_row(
        "burndown",
        "coating_stack_validation_phase_recommendation",
        "Validation Phase Recommendation",
        results.get("coating_stack_validation_phase_recommendation"),
    )

    add_row(
        "priority_action",
        "coating_stack_priority_action_status",
        "Priority Action Status",
        results.get("coating_stack_priority_action_status"),
    )
    add_row(
        "priority_action",
        "coating_stack_next_priority_action_title",
        "Next Priority Action",
        results.get("coating_stack_next_priority_action_title"),
    )
    add_row(
        "priority_action",
        "coating_stack_next_priority_action_summary",
        "Next Priority Action Summary",
        results.get("coating_stack_next_priority_action_summary"),
    )

    add_row(
        "ui",
        "coating_stack_ui_severity",
        "UI Severity",
        results.get("coating_stack_ui_severity"),
    )
    add_row(
        "ui",
        "coating_stack_ui_top_message",
        "UI Top Message",
        results.get("coating_stack_ui_top_message"),
    )
    add_row(
        "ui",
        "coating_stack_ui_top_action",
        "UI Top Action",
        results.get("coating_stack_ui_top_action"),
    )

    results["coating_stack_export_summary_rows"] = rows
    results["coating_stack_export_summary_row_count"] = len(rows)
    results["coating_stack_export_summary_status"] = "COMPLETE"

    return results

def ensure_coating_stack_source_data_gate_outputs(results):
    """
    Ensures coating-stack source-data gate outputs always exist.

    This does not override real calculated gate values.
    It only fills conservative defaults when earlier coating-stack logic
    did not populate the gate.
    """

    if results is None:
        return results

    existing_gate = results.get("coating_stack_source_data_gate")

    if existing_gate not in (None, ""):
        return results

    final_acceptance = results.get("coating_stack_final_acceptance_status")
    source_status = results.get("coating_stack_source_data_status")
    weighted_gate = results.get("coating_stack_source_data_weighted_gate")

    data_mode = (
        results.get("coating_stack_data_mode")
        or results.get("coating_stack_source_data_mode")
        or results.get("source_validation_mode")
        or "INSUFFICIENT_SOURCE_MODE"
    )

    if final_acceptance in (None, "", "NOT_APPLICABLE"):
        gate = "NO_ACTIVE_COATING_ROUTE"
        reason = "No active coating-stack validation route is currently selected."
        severity = "BLUE"
        visibility = "SUMMARY_ONLY"

    elif source_status in (None, "", "NO_SOURCED_DATA"):
        gate = "FAIL_NO_SOURCE_DATA"
        reason = (
            "No sourced coating-stack data is available. Current coating and bond-coat "
            "values cannot support validation."
        )
        severity = "RED"
        visibility = "EXPANDED"

    elif weighted_gate == "PASS":
        gate = "PASS"
        reason = "Coating-stack source-data gate passed the weighted source-data threshold."
        severity = "GREEN"
        visibility = "SUMMARY_ONLY"

    else:
        gate = "FAIL_INCOMPLETE_SOURCE_DATA"
        reason = "Coating-stack source data is incomplete and cannot support final validation."
        severity = "ORANGE"
        visibility = "EXPANDED"

    if weighted_gate in (None, ""):
        weighted_gate = "UNKNOWN"

    results["coating_stack_source_data_gate"] = gate
    results["coating_stack_source_data_weighted_gate"] = weighted_gate
    results["coating_stack_source_data_gate_reason"] = reason
    results["coating_stack_source_data_status_line"] = (
        f"{gate} | weighted={weighted_gate} | mode={data_mode}"
    )
    results["coating_stack_source_data_severity"] = severity
    results["coating_stack_source_data_report_visibility"] = visibility

    return results

def audit_coating_stack_validation_system(results):
    """
    Performs an internal health audit of the coating-stack validation system.

    This does not change the engineering result.
    It checks whether the coating-stack validation pipeline produced the expected
    keys and whether the conservative final-blocking behaviour is active.
    """

    if results is None:
        return results

    required_keys = [
        "explicit_coating_liner_status",
        "coating_stack_source_data_gate",
        "coating_stack_final_acceptance_status",
        "coating_stack_evidence_status",
        "coating_stack_roadmap_status",
        "coating_stack_data_mode",
        "coating_stack_certification_status",
        "coating_stack_risk_status",
        "coating_stack_risk_burndown_status",
        "coating_stack_acceptance_label",
        "coating_stack_dashboard_status",
        "coating_stack_ui_severity",
        "coating_stack_export_summary_status",
    ]

    missing_keys = []
    present_keys = []

    for key in required_keys:
        if key in results:
            present_keys.append(key)
        else:
            missing_keys.append(key)

    warnings = []
    failures = []

    final_verdict = results.get("final_regen_design_verdict")
    acceptance_label = results.get("coating_stack_acceptance_label")
    data_mode = results.get("coating_stack_data_mode")
    source_gate = results.get("coating_stack_source_data_gate")
    certification_status = results.get("coating_stack_certification_status")
    final_acceptance = results.get("coating_stack_final_acceptance_status")

    if missing_keys:
        failures.append(
            f"Missing coating-stack output keys: {missing_keys}"
        )

    if data_mode == "PLACEHOLDER_MODE" and final_acceptance == "VALIDATION_SUPPORT_ALLOWED":
        failures.append(
            "Placeholder data is incorrectly allowed to support final validation."
        )

    if not solver_pass(source_gate) and final_acceptance == "VALIDATION_SUPPORT_ALLOWED":
        failures.append(
            "Source-data gate has not passed, but final validation support is allowed."
        )

    if certification_status != "CERTIFICATION_READY" and acceptance_label == "CAN_SUPPORT_FINAL_VALIDATION":
        failures.append(
            "Acceptance label allows final validation while certification is not ready."
        )

    if acceptance_label != "CAN_SUPPORT_FINAL_VALIDATION":
        clearly_downgraded_verdicts = (
            "DEVELOPMENT_ROUTE_ONLY_COATING_STACK_BLOCKED",
            "DEVELOPMENT_ROUTE_ONLY",
            "FAIL",
            "REGEN_ONLY_NOT_FEASIBLE",
            "COMBINED_COOLING_DEVELOPMENT_REQUIRED",
            "REGEN_PLUS_FILM_OR_REDUCED_HEAT_LOAD_REQUIRED",
            None,
        )

        if final_verdict not in clearly_downgraded_verdicts:
            warnings.append(
                "Coating stack is not final-valid, but final verdict is not clearly downgraded."
            )

    if results.get("coating_stack_ui_severity") == "GREEN" and acceptance_label != "CAN_SUPPORT_FINAL_VALIDATION":
        warnings.append(
            "UI severity is green even though coating stack cannot support final validation."
        )

    if results.get("coating_stack_export_summary_row_count") in (None, 0):
        warnings.append(
            "Coating-stack export summary rows are missing or empty."
        )

    if failures:
        audit_status = "FAIL"
    elif warnings:
        audit_status = "WARN"
    else:
        audit_status = "PASS"

    results["coating_stack_system_audit_status"] = audit_status
    results["coating_stack_system_audit_present_keys"] = present_keys
    results["coating_stack_system_audit_missing_keys"] = missing_keys
    results["coating_stack_system_audit_warnings"] = warnings
    results["coating_stack_system_audit_failures"] = failures
    results["coating_stack_system_audit_summary"] = (
        f"{audit_status}: {len(present_keys)} present, "
        f"{len(missing_keys)} missing, "
        f"{len(warnings)} warning(s), "
        f"{len(failures)} failure(s)."
    )

    return results

def build_final_regen_verdict_review_summary(results):
    """
    Builds compact, deduplicated final-verdict review fields for reports.

    The raw final_regen_design_reasons list is intentionally detailed.
    This creates a readable top-level engineering review.
    """

    if results is None:
        return results

    raw_reasons = results.get("final_regen_design_reasons") or []
    raw_recommendations = results.get("final_regen_design_recommendations") or []

    priority_reasons = []

    def add_reason(text):
        if text and text not in priority_reasons:
            priority_reasons.append(text)

    final_verdict = results.get("final_regen_design_verdict")
    regen_status = results.get("regen_overall_status") or results.get("overall_status")
    geometry_valid = results.get("channel_geometry_valid")
    recommended_status = results.get("recommended_geometry_status")
    viability_status = results.get("recommended_regen_viability_status")
    coating_acceptance = results.get("coating_stack_final_acceptance_status")
    coating_data_mode = results.get("coating_stack_data_mode")
    coating_top_risk = results.get("coating_stack_top_risk_title")
    next_priority = results.get("coating_stack_next_priority_action_title")
    source_gate = results.get("coating_stack_source_data_gate")
    certification_status = results.get("coating_stack_certification_status")

    add_reason(f"Final verdict is {final_verdict}.")
    add_reason(f"Base regen status is {regen_status}.")
    add_reason(f"Manual channel geometry valid flag is {geometry_valid}.")
    add_reason(f"Recommended geometry status is {recommended_status}.")
    add_reason(f"Recommended regen viability status is {viability_status}.")
    add_reason(f"Coating-stack final acceptance is {coating_acceptance}.")
    add_reason(f"Coating-stack data mode is {coating_data_mode}; source gate is {source_gate}.")
    add_reason(f"Coating-stack certification status is {certification_status}.")
    add_reason(f"Top coating-stack risk is {coating_top_risk}.")
    add_reason(f"Next priority action is {next_priority}.")

    # Keep a few useful raw reasons after the structured summary.
    # Keep the review summary compact. Avoid re-adding the full coating-gate
    # blocker dump because those details already appear in the coating sections.
    allowed_raw_reason_keywords = (
        "Coupled auto-tuned",
        "Recommended",
        "regen",
        "geometry",
        "cooling",
        "material margin",
    )

    for reason in raw_reasons:
        if len(priority_reasons) >= 12:
            break

        if not any(keyword.lower() in str(reason).lower() for keyword in allowed_raw_reason_keywords):
            continue

        if reason not in priority_reasons:
            priority_reasons.append(reason)

    priority_recommendations = []

    def add_recommendation(text):
        if text and text not in priority_recommendations:
            priority_recommendations.append(text)

    add_recommendation("Use recommended geometry rather than the current manual channel geometry.")
    add_recommendation("Treat all coating/liner and bond-coat results as development-route-only until sourced data is added.")
    add_recommendation("Do not accept coupled auto-tuned cooling as validation; convert it into physical film, heat-load, material, and coating models.")
    add_recommendation(results.get("coating_stack_next_priority_action_summary"))
    add_recommendation(results.get("coating_stack_source_data_category_recommendation"))
    add_recommendation(results.get("coating_stack_validation_phase_recommendation"))

    allowed_raw_recommendation_keywords = (
        "geometry",
        "cooling",
        "coupled",
        "film",
        "source",
        "validation",
        "material",
    )

    for recommendation in raw_recommendations:
        if len(priority_recommendations) >= 10:
            break

        if not any(
                keyword.lower() in str(recommendation).lower()
                for keyword in allowed_raw_recommendation_keywords
        ):
            continue

        if recommendation not in priority_recommendations:
            priority_recommendations.append(recommendation)

    results["final_regen_design_review_reasons"] = priority_reasons
    results["final_regen_design_review_recommendations"] = priority_recommendations
    results["final_regen_design_review_status"] = "COMPLETE"

    return results

def build_report_system_completion_status(results):
    """
    Tracks whether the current report/output system has all major summary layers.

    This does not affect physics or validation.
    It is only used to decide whether future work should move away from report
    cleanup and into the next modelling feature.
    """

    if results is None:
        return results

    required_keys = [
        "final_regen_design_review_status",
        "coating_stack_system_audit_status",
        "coating_stack_executive_summary",
        "coating_stack_dashboard_status",
        "coating_stack_ui_warning_cards",
        "coating_stack_export_summary_status",
        "coating_stack_source_data_checklist_status",
        "coating_stack_priority_action_status",
    ]

    missing = [key for key in required_keys if key not in results]

    if missing:
        status = "INCOMPLETE"
        recommendation = "Finish report/output summary keys before starting the next modelling feature."
    else:
        status = "COMPLETE"
        recommendation = "Report system is complete enough. Move to the next modelling feature: sourced material/coating database integration."

    results["report_system_completion_status"] = status
    results["report_system_missing_keys"] = missing
    results["report_system_recommendation"] = recommendation

    return results

def recommend_coating_stack_candidate(results):
    """
    Selects a best-available coating and bond-coat candidate for the recommended design package.

    This does not validate the coating stack.
    Placeholder coating/bond-coat data can only produce RECOMMENDED_DEVELOPMENT_ONLY.
    """

    if results is None:
        return results

    if get_coating_material_names is None or get_coating_material_properties is None:
        results["recommended_coating_stack_status"] = "COATING_DATABASE_NOT_AVAILABLE"
        results["recommended_coating_stack_reason"] = "Coating database helpers are unavailable."
        return results

    if get_bond_coat_names is None or get_bond_coat_properties is None:
        results["recommended_coating_stack_status"] = "BOND_COAT_DATABASE_NOT_AVAILABLE"
        results["recommended_coating_stack_reason"] = "Bond-coat database helpers are unavailable."
        return results

    coating_names = get_coating_material_names()
    bond_names = get_bond_coat_names()

    if not coating_names:
        results["recommended_coating_stack_status"] = "NO_COATING_CANDIDATES"
        results["recommended_coating_stack_reason"] = "No coating candidates exist."
        return results

    if not bond_names:
        results["recommended_coating_stack_status"] = "NO_BOND_COAT_CANDIDATES"
        results["recommended_coating_stack_reason"] = "No bond-coat candidates exist."
        return results

    def safe_float(value, default=0.0):
        try:
            if value in (None, ""):
                return default
            return float(value)
        except Exception:
            return default

    required_surface_temperature = safe_float(
        results.get("best_full_engine_regen_max_hot_wall_temperature")
        or results.get("full_engine_regen_max_hot_wall_temperature")
        or results.get("regen_axial_max_hot_wall_temperature"),
        0.0,
    )

    best_coating = None
    best_coating_score = -1.0e99

    for name in coating_names:
        coating = get_coating_material_properties(name)

        if not isinstance(coating, dict):
            continue

        surface_limit = safe_float(coating.get("max_surface_temperature"), 0.0)
        thickness = safe_float(coating.get("max_practical_thickness"), 0.0)
        conductivity = safe_float(coating.get("thermal_conductivity"), 999.0)
        source_score = safe_float(coating.get("source_validation_score"), 0.0)

        temperature_margin = surface_limit - required_surface_temperature

        score = (
            temperature_margin * 0.05
            + thickness * 10000.0
            - conductivity * 3.0
            + source_score
        )

        if score > best_coating_score:
            best_coating_score = score
            best_coating = coating

    best_bond = None
    best_bond_score = -1.0e99

    for name in bond_names:
        bond = get_bond_coat_properties(name)

        if not isinstance(bond, dict):
            continue

        stress_reduction = safe_float(bond.get("max_stress_reduction_fraction"), 0.0)
        thickness = safe_float(bond.get("max_practical_thickness"), 0.0)
        source_score = safe_float(bond.get("source_validation_score"), 0.0)

        score = (
            stress_reduction * 100.0
            + thickness * 10000.0
            + source_score
        )

        if score > best_bond_score:
            best_bond_score = score
            best_bond = bond

    if best_coating is None or best_bond is None:
        results["recommended_coating_stack_status"] = "NO_USABLE_COATING_STACK"
        results["recommended_coating_stack_reason"] = "No usable coating/bond-coat pair could be selected."
        return results

    coating_placeholder = bool(best_coating.get("source_is_placeholder"))
    bond_placeholder = bool(best_bond.get("source_is_placeholder"))

    if coating_placeholder or bond_placeholder:
        status = "RECOMMENDED_DEVELOPMENT_ONLY"
        pass_flag = 0
        reason = (
            "A best-available coating stack was selected, but one or more records use "
            "placeholder data. It can be applied for development testing only."
        )
    else:
        status = "RECOMMENDED_SOURCE_READY_REVIEW"
        pass_flag = 0
        reason = (
            "A best-available coating stack was selected from sourced records, but full "
            "thermal-stress, adhesion, fatigue, and spallation validation is still required."
        )

    results["recommended_coating_stack_status"] = status
    results["recommended_coating_stack_pass"] = pass_flag
    results["recommended_coating_stack_reason"] = reason

    results["recommended_coating_material"] = best_coating.get("name")
    results["recommended_coating_source_mode"] = best_coating.get("source_validation_mode")
    results["recommended_coating_source_quality"] = best_coating.get("source_quality")
    results["recommended_coating_is_placeholder"] = 1 if coating_placeholder else 0
    results["recommended_coating_thickness"] = best_coating.get("max_practical_thickness")

    results["recommended_bond_coat"] = best_bond.get("name")
    results["recommended_bond_coat_source_mode"] = best_bond.get("source_validation_mode")
    results["recommended_bond_coat_source_quality"] = best_bond.get("source_quality")
    results["recommended_bond_coat_is_placeholder"] = 1 if bond_placeholder else 0
    results["recommended_bond_coat_thickness"] = best_bond.get("max_practical_thickness")

    return results

def build_recommended_design_package(results):
    """
    Builds a scalable recommended design package.

    The UI should apply this package rather than hardcoding every possible
    future recommended value.

    This may include:
    - regen geometry
    - selected material
    - coating / bond coat
    - coating thickness
    - future film/thermal-management values

    Important:
    This does not mean the design passes validation.
    It only packages the best available recommended values.
    """

    if results is None:
        return results

    package = {}

    def add_if_real(key, value):
        if value in (None, "", "N/A", "None"):
            return
        package[key] = value

    # Regen geometry
    add_if_real("number_of_coolant_channels", results.get("recommended_channel_count"))
    add_if_real("coolant_channel_width", results.get("recommended_channel_width"))
    add_if_real("coolant_channel_height", results.get("recommended_channel_height"))
    add_if_real("rib_width", results.get("recommended_rib_width"))

    # Best material from material-aware optimiser
    best_material = results.get("material_aware_combined_best_material")
    add_if_real("selected_material", best_material)
    add_if_real("selected_material_name", best_material)
    add_if_real("material_name", best_material)
    add_if_real("hot_gas_liner", best_material)

    # Coating / bond coat selections
    add_if_real(
        "selected_coating_material",
        results.get("recommended_coating_material")
        or results.get("explicit_coating_material")
    )

    add_if_real(
        "selected_bond_coat",
        results.get("recommended_bond_coat")
        or results.get("active_bond_coat")
    )

    # Coating physical values
    add_if_real(
        "coating_thickness",
        results.get("recommended_coating_thickness")
        or results.get("explicit_coating_thickness")
    )

    results["recommended_design_package"] = package
    results["recommended_design_package_key_count"] = len(package)
    results["recommended_design_package_keys"] = ", ".join(package.keys())

    if package:
        results["recommended_design_package_status"] = "AVAILABLE"
    else:
        results["recommended_design_package_status"] = "NO_RECOMMENDED_VALUES"

    return results

def size_required_coating_liner_for_balanced_rebalance(results):
    """
    Sizes the coating thermal resistance actually required to close the
    balanced rebalance gap without over-crediting insulation.

    Required thickness:
        t_required = ΔT_required * k / q''

    This creates a sizing target, not a validation pass.
    """

    if results is None:
        return results

    profile = results.get("coupled_auto_balanced_rebalance_profile")

    if not profile:
        results["required_coating_liner_status"] = "NO_BALANCED_REBALANCE_PROFILE"
        return results

    required_gap = results.get("coating_liner_required_temperature_margin")

    if required_gap is None:
        results["required_coating_liner_status"] = "NO_REQUIRED_GAP"
        return results

    coating_conductivity = (
        results.get("coating_liner_thermal_conductivity")
        or results.get("coating_thermal_conductivity")
        or 2.0
    )

    try:
        required_gap = float(required_gap)
        coating_conductivity = float(coating_conductivity)
    except Exception:
        results["required_coating_liner_status"] = "INVALID_INPUTS"
        return results

    if required_gap <= 0 or coating_conductivity <= 0:
        results["required_coating_liner_status"] = "NOT_REQUIRED"
        return results

    sized_profile = []

    max_required_thickness = None
    max_required_thickness_location = None
    worst_heat_flux = None

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)
        try:
            x = float(x)
        except Exception:
            x = 0.0

        heat_flux = (
            station.get("regen_heat_flux")
            or station.get("heat_flux")
            or station.get("q")
            or results.get("preview_max_heat_flux")
            or results.get("max_heat_flux")
            or 0.0
        )

        try:
            heat_flux = float(heat_flux)
        except Exception:
            heat_flux = 0.0

        if heat_flux > 0:
            required_thickness = required_gap * coating_conductivity / heat_flux
        else:
            required_thickness = None

        new_station["required_coating_liner_temperature_margin"] = required_gap
        new_station["required_coating_liner_thermal_conductivity"] = coating_conductivity
        new_station["required_coating_liner_thickness"] = required_thickness

        if required_thickness is not None:
            if max_required_thickness is None or required_thickness > max_required_thickness:
                max_required_thickness = required_thickness
                max_required_thickness_location = x

        if worst_heat_flux is None or heat_flux > worst_heat_flux:
            worst_heat_flux = heat_flux

        sized_profile.append(new_station)

    if max_required_thickness is None:
        status = "INSUFFICIENT_HEAT_FLUX_DATA"
    elif max_required_thickness <= 0.00025:
        status = "PLAUSIBLE_THICKNESS_TARGET"
    elif max_required_thickness <= 0.001:
        status = "AGGRESSIVE_THICKNESS_TARGET"
    else:
        status = "SEVERE_THICKNESS_TARGET"

    results["required_coating_liner_profile"] = sized_profile
    results["required_coating_liner_status"] = status
    results["required_coating_liner_temperature_margin"] = required_gap
    results["required_coating_liner_thermal_conductivity"] = coating_conductivity
    results["required_coating_liner_max_required_thickness"] = max_required_thickness
    results["required_coating_liner_max_required_thickness_location"] = max_required_thickness_location
    results["required_coating_liner_worst_heat_flux"] = worst_heat_flux
    results["required_coating_liner_recommendation"] = (
        "Use this as a coating sizing target only. Do not accept the design until coating thermal resistance, adhesion, erosion, thermal stress, and chamber performance penalties are modelled."
    )

    return results

def screen_coating_materials_for_required_liner(results):
    """
    Screens possible coating/liner materials against the required coating
    thickness target.

    This is still not validation. It checks whether the required thickness
    is plausible for candidate coating materials.
    """

    if results is None:
        return results

    required_thickness = results.get("required_coating_liner_max_required_thickness")
    required_margin = results.get("required_coating_liner_temperature_margin")

    if required_thickness is None or required_margin is None:
        results["coating_material_screen_status"] = "INSUFFICIENT_DATA"
        return results

    try:
        required_thickness = float(required_thickness)
        required_margin = float(required_margin)
    except Exception:
        results["coating_material_screen_status"] = "INVALID_INPUTS"
        return results

    coating_candidates = results.get("coating_material_candidates") or COATING_MATERIAL_DATABASE

    screened = []

    worst_heat_flux = results.get("required_coating_liner_worst_heat_flux") or 0.0

    try:
        worst_heat_flux = float(worst_heat_flux)
    except Exception:
        worst_heat_flux = 0.0

    for material in coating_candidates:
        if not isinstance(material, dict):
            continue

        name = material.get("name", "Unknown coating")
        k = material.get("thermal_conductivity")
        surface_limit = material.get("max_surface_temperature")
        max_practical_thickness = material.get("max_practical_thickness")

        try:
            k = float(k)
            surface_limit = float(surface_limit)
            max_practical_thickness = float(max_practical_thickness)
        except Exception:
            continue

        if worst_heat_flux > 0.0:
            material_required_thickness = required_margin * k / worst_heat_flux
        else:
            material_required_thickness = None

        role = material.get("coating_role", "unknown")
        density = material.get("density")

        if material_required_thickness is None:
            status = "INSUFFICIENT_HEAT_FLUX"
            margin = None
            temperature_margin = 0.0
            score = -1e9
        else:
            margin = max_practical_thickness - material_required_thickness
            temperature_margin = surface_limit - required_margin

            if margin >= 0.0001:
                status = "PASS_WITH_MARGIN"
            elif margin >= 0.0:
                status = "PASS_LOW_MARGIN"
            else:
                status = "FAIL_THICKNESS"

            thermal_barrier_bonus = 0.0
            liner_penalty = 0.0
            density_penalty = 0.0

            if role == "thermal_barrier":
                thermal_barrier_bonus = 250.0

            if role == "refractory_liner":
                liner_penalty = 150.0

            if density is not None:
                density_penalty = density / 100.0

            conductivity_penalty = k * 2.0

            score = (
                    (margin * 1e6)
                    + temperature_margin
                    + thermal_barrier_bonus
                    - liner_penalty
                    - density_penalty
                    - conductivity_penalty
            )

        screened.append({
            "name": name,
            "family": material.get("family", "Unknown"),
            "source_quality": material.get("source_quality", "unknown"),
            "thermal_conductivity": k,
            "max_surface_temperature": surface_limit,
            "max_practical_thickness": max_practical_thickness,
            "required_thickness": material_required_thickness,
            "thickness_margin": margin,
            "status": status,
            "score": score,
            "notes": material.get("notes", ""),
            "coating_role": material.get("coating_role", "unknown"),
            "density": material.get("density"),
            "elastic_modulus": material.get("elastic_modulus"),
            "poisson_ratio": material.get("poisson_ratio"),
            "thermal_expansion_coefficient": material.get("thermal_expansion_coefficient"),
            "allowable_coating_stress": material.get("allowable_coating_stress"),
        })

    screened.sort(key=lambda item: item.get("score", -1e9), reverse=True)

    passing = [
        item for item in screened
        if item["status"] in ("PASS_WITH_MARGIN", "PASS_LOW_MARGIN")
    ]

    thermal_barrier_candidates = [
        item for item in passing
        if item.get("coating_role") == "thermal_barrier"
    ]

    refractory_liner_candidates = [
        item for item in passing
        if item.get("coating_role") == "refractory_liner"
    ]

    thermal_barrier_candidates.sort(key=lambda item: item.get("score", -1e9), reverse=True)
    refractory_liner_candidates.sort(key=lambda item: item.get("score", -1e9), reverse=True)

    results["coating_material_screen_status"] = "COMPLETE"
    results["coating_material_candidate_count"] = len(screened)
    results["coating_material_passing_count"] = len(passing)
    results["coating_material_best_candidate"] = screened[0] if screened else None
    results["coating_material_best_thermal_barrier_candidate"] = (
        thermal_barrier_candidates[0] if thermal_barrier_candidates else None
    )
    results["coating_material_best_refractory_liner_candidate"] = (
        refractory_liner_candidates[0] if refractory_liner_candidates else None
    )
    results["coating_material_passing_candidates"] = passing
    results["coating_material_screened_candidates"] = screened

    if passing:
        results["coating_material_recommendation"] = (
            "At least one coating candidate can meet the required thickness target, but validation still requires surface temperature, erosion, adhesion, and thermal stress checks."
        )
    else:
        results["coating_material_recommendation"] = (
            "No coating candidate meets the required thickness target. Rebalance toward more film cooling, heat-load reduction, or chamber derating."
        )

    return results

def assess_coating_material_data_quality(results):
    """
    Checks whether coating material screening is based on sourced data,
    placeholder engineering estimates, or generic candidates.
    """

    if results is None:
        return results

    candidates = results.get("coating_material_screened_candidates") or []

    if not candidates:
        results["coating_material_data_quality_status"] = "NO_CANDIDATES"
        return results

    generic_count = 0
    placeholder_count = 0
    sourced_count = 0

    for candidate in candidates:
        name = str(candidate.get("name", "")).lower()
        notes = str(candidate.get("notes", "")).lower()
        source_quality = str(candidate.get("source_quality", "")).lower()

        is_generic = (
            "generic" in name
            or "placeholder" in notes
            or "replace with sourced" in notes
        )

        is_placeholder = (
            "placeholder" in source_quality
            or "approx" in source_quality
            or "estimate" in source_quality
        )

        if is_generic:
            generic_count += 1
        elif is_placeholder:
            placeholder_count += 1
        else:
            sourced_count += 1

    if sourced_count == 0 and placeholder_count == 0:
        status = "GENERIC_ONLY"
    elif sourced_count == 0:
        status = "PLACEHOLDER_ENGINEERING_DATA"
    elif placeholder_count > 0 or generic_count > 0:
        status = "MIXED_DATA_QUALITY"
    else:
        status = "SOURCED_DATA"

    results["coating_material_data_quality_status"] = status
    results["coating_material_generic_candidate_count"] = generic_count
    results["coating_material_placeholder_candidate_count"] = placeholder_count
    results["coating_material_sourced_candidate_count"] = sourced_count

    if status == "SOURCED_DATA":
        recommendation = (
            "Coating material data appears sourced; proceed to surface temperature, erosion, adhesion, and thermal stress checks."
        )
    elif status == "PLACEHOLDER_ENGINEERING_DATA":
        recommendation = (
            "Coating candidates now use real material names but still rely on placeholder engineering values. Add citations and temperature-dependent data before accepting coating-based validation."
        )
    else:
        recommendation = (
            "Replace generic coating candidates with sourced real coating/liner materials before accepting any coating-based pass."
        )

    results["coating_material_data_quality_recommendation"] = recommendation

    return results

def derive_regen_target_reynolds_number(results):
    """
    Derives a scalable target Reynolds number for regen cooling.

    Small engines should not automatically use the same target Reynolds
    number as large engines.
    """

    if results is None:
        return None

    # User override always wins
    if results.get("regen_user_target_reynolds_number") is not None:
        return results.get("regen_user_target_reynolds_number")

    mass_flow_rate = results.get("mass_flow_rate")
    throat_radius = results.get("throat_radius")
    chamber_pressure = results.get("chamber_pressure")

    if mass_flow_rate is None or throat_radius is None:
        return 10000.0

    if mass_flow_rate <= 0 or throat_radius <= 0:
        return 10000.0

    throat_diameter = 2.0 * throat_radius

    # Engine scale proxy.
    # Higher mdot through a larger engine should permit/require higher Re.
    scale_parameter = mass_flow_rate / max(throat_diameter, 1e-9)

    if scale_parameter < 30:
        target_re = 3000.0
    elif scale_parameter < 80:
        target_re = 5000.0
    elif scale_parameter < 200:
        target_re = 8000.0
    elif scale_parameter < 500:
        target_re = 12000.0
    else:
        target_re = 20000.0

    # Chamber pressure modifier.
    # Higher-pressure engines can usually tolerate stronger cooling demands.
    if chamber_pressure is not None and chamber_pressure > 0:
        if chamber_pressure > 15e6:
            target_re *= 1.25
        elif chamber_pressure < 3e6:
            target_re *= 0.85

    target_re = clamp_value(
        target_re,
        minimum=2500.0,
        maximum=30000.0
    )

    results["regen_scale_parameter"] = scale_parameter
    results["regen_derived_target_reynolds_number"] = target_re

    return target_re

def derive_regen_design_constraints(results):
    """
    Derives scalable regen design constraints from the current engine.

    This prevents LEAF from using one fixed set of geometry limits for every
    engine size.

    User-entered values still override derived defaults when present.
    """

    if results is None:
        return results

    throat_radius = results.get("throat_radius")
    chamber_pressure = results.get("chamber_pressure")
    nozzle_length = results.get("nozzle_length")
    coolant_density = results.get("coolant_density")

    if throat_radius is None or throat_radius <= 0:
        return results

    # -------------------------
    # User-level requirements
    # -------------------------

    derived_target_re = derive_regen_target_reynolds_number(results)

    results["regen_derived_target_reynolds_number"] = derived_target_re

    # User override only wins if explicitly provided.
    # Otherwise the active optimiser target should follow the derived scalable target.
    if results.get("regen_user_target_reynolds_number") is not None:
        results["regen_target_reynolds_number"] = results.get("regen_user_target_reynolds_number")
    else:
        results["regen_target_reynolds_number"] = derived_target_re

    if results.get("regen_pressure_drop_fraction") is None:
        results["regen_pressure_drop_fraction"] = 0.10

    if results.get("regen_geometry_aggressiveness") is None:
        results["regen_geometry_aggressiveness"] = "balanced"

    aggressiveness = str(results.get("regen_geometry_aggressiveness")).lower()

    if aggressiveness == "conservative":
        rib_factor = 0.050
        width_factor = 0.040
        height_factor = 0.250
        velocity_fraction_of_pressure_head = 0.20
        minimum_cooling_coverage = 0.45
        thermal_pitch_multiplier = 6.0
        radius_pitch_factor = 0.45

    elif aggressiveness == "aggressive":
        rib_factor = 0.025
        width_factor = 0.025
        height_factor = 0.650
        velocity_fraction_of_pressure_head = 0.45
        minimum_cooling_coverage = 0.30
        thermal_pitch_multiplier = 10.0
        radius_pitch_factor = 0.70

    else:
        rib_factor = 0.035
        width_factor = 0.030
        height_factor = 0.450
        velocity_fraction_of_pressure_head = 0.30
        minimum_cooling_coverage = 0.40
        thermal_pitch_multiplier = 8.0
        radius_pitch_factor = 0.55

    # -------------------------
    # Pressure drop limit
    # -------------------------

    pressure_drop_limit = None

    if chamber_pressure is not None and chamber_pressure > 0:
        pressure_drop_limit = (
            chamber_pressure
            * results.get("regen_pressure_drop_fraction")
        )

    if results.get("regen_pressure_drop_limit") is not None:
        pressure_drop_limit = results.get("regen_pressure_drop_limit")

    results["regen_derived_pressure_drop_limit"] = pressure_drop_limit

    # -------------------------
    # Scalable manufacturable geometry
    # -------------------------

    derived_min_rib_width = throat_radius * rib_factor
    derived_min_channel_width = throat_radius * width_factor
    derived_max_channel_height = throat_radius * height_factor

    # Practical engineering floors/ceilings.
    # These are not design targets; they only prevent impossible dimensions.
    derived_min_rib_width = clamp_value(
        derived_min_rib_width,
        minimum=0.00025,
        maximum=0.003
    )

    derived_min_channel_width = clamp_value(
        derived_min_channel_width,
        minimum=0.00025,
        maximum=0.004
    )

    derived_max_channel_height = clamp_value(
        derived_max_channel_height,
        minimum=derived_min_channel_width,
        maximum=max(derived_min_channel_width, throat_radius)
    )

    if results.get("regen_minimum_rib_width") is not None:
        derived_min_rib_width = results.get("regen_minimum_rib_width")

    if results.get("regen_minimum_channel_width") is not None:
        derived_min_channel_width = results.get("regen_minimum_channel_width")

    if results.get("regen_maximum_channel_height") is not None:
        derived_max_channel_height = results.get("regen_maximum_channel_height")

    results["regen_derived_minimum_rib_width"] = derived_min_rib_width
    results["regen_derived_minimum_channel_width"] = derived_min_channel_width
    results["regen_derived_maximum_channel_height"] = derived_max_channel_height

    # -------------------------
    # Velocity limit derived from pressure head
    # -------------------------

    derived_max_velocity = None

    if (
        pressure_drop_limit is not None
        and coolant_density is not None
        and pressure_drop_limit > 0
        and coolant_density > 0
    ):
        ideal_pressure_head_velocity = math.sqrt(
            2.0 * pressure_drop_limit / coolant_density
        )

        derived_max_velocity = (
            ideal_pressure_head_velocity
            * velocity_fraction_of_pressure_head
        )

    if results.get("regen_maximum_coolant_velocity") is not None:
        derived_max_velocity = results.get("regen_maximum_coolant_velocity")

    results["regen_derived_maximum_coolant_velocity"] = derived_max_velocity

    # -------------------------
    # Hydraulic diameter scale
    # -------------------------

    derived_min_hydraulic_diameter = max(
        0.5 * derived_min_channel_width,
        throat_radius * 0.025
    )

    if results.get("regen_minimum_hydraulic_diameter") is not None:
        derived_min_hydraulic_diameter = results.get("regen_minimum_hydraulic_diameter")

    results["regen_derived_minimum_hydraulic_diameter"] = derived_min_hydraulic_diameter

    # -------------------------
    # Channel count search bounds
    # -------------------------

    channel_mid_radius = results.get("channel_mid_radius")

    if channel_mid_radius is not None and channel_mid_radius > 0:
        circumference = 2.0 * math.pi * channel_mid_radius

        minimum_physical_pitch = max(
            derived_min_channel_width + derived_min_rib_width,
            1e-9
        )

        max_count_from_min_pitch = int(
            circumference / minimum_physical_pitch
        )

        thermal_distribution_pitch = max(
            minimum_physical_pitch * thermal_pitch_multiplier,
            throat_radius * radius_pitch_factor
        )

        min_count_from_thermal_distribution = int(
            math.ceil(circumference / thermal_distribution_pitch)
        )

        derived_min_channel_count = max(
            4,
            min_count_from_thermal_distribution
        )

        derived_max_channel_count = max(
            derived_min_channel_count,
            max_count_from_min_pitch
        )

        if results.get("regen_minimum_channel_count") is not None:
            derived_min_channel_count = int(results.get("regen_minimum_channel_count"))

        if results.get("regen_maximum_channel_count") is not None:
            derived_max_channel_count = int(results.get("regen_maximum_channel_count"))

        results["regen_derived_maximum_channel_pitch"] = thermal_distribution_pitch
        results["regen_derived_minimum_channel_count"] = derived_min_channel_count
        results["regen_derived_maximum_channel_count"] = derived_max_channel_count

    else:
        results["regen_derived_maximum_channel_pitch"] = None
        results["regen_derived_minimum_channel_count"] = 4
        results["regen_derived_maximum_channel_count"] = 300

    # -------------------------
    # Minimum cooling coverage
    # -------------------------
    # Circumferential coverage = total channel width / circumference.
    # This prevents the optimiser from selecting only a few very large-spaced
    # channels with huge ribs and poor wall coverage.

    if results.get("regen_minimum_cooling_coverage") is not None:
        minimum_cooling_coverage = results.get("regen_minimum_cooling_coverage")

    minimum_cooling_coverage = clamp_value(
        minimum_cooling_coverage,
        minimum=0.05,
        maximum=0.95
    )

    results["regen_derived_minimum_cooling_coverage"] = minimum_cooling_coverage

    results["regen_design_constraints_note"] = (
        "Regen constraints are derived from engine scale, chamber pressure, "
        "coolant properties, and selected aggressiveness. User-defined values "
        "override derived defaults."
    )

    return results

def calculate_regen_geometry_auto_sizing(
        channel_mid_radius=None,
        coolant_mass_flow_rate=None,
        coolant_density=None,
        coolant_dynamic_viscosity=None,
        target_reynolds_number=None,
        minimum_rib_width=None,
        minimum_channel_width=None,
        maximum_channel_height=None,
        channel_aspect_ratio=None,
        minimum_channel_count=None,
        maximum_channel_count=None,
        maximum_coolant_velocity=None,
        minimum_hydraulic_diameter=None,
        pressure_drop_limit=None,
        nozzle_length=None,
        minimum_cooling_coverage=None
):
    """
    Regen Geometry Phase 1D wrapper.

    engine_solver.py no longer owns automatic regen geometry solving.
    It delegates to:

        leaf_qt/regen_geometry_solver.py

    This keeps engine_solver.py from becoming the owner of candidate
    generation, constraint ownership, iteration history, and solver status.
    """

    try:
        from leaf_qt.regen_geometry_solver import solve_regen_geometry_to_engine_results
    except Exception:
        from regen_geometry_solver import solve_regen_geometry_to_engine_results

    return solve_regen_geometry_to_engine_results(
        channel_mid_radius=channel_mid_radius,
        coolant_mass_flow_rate=coolant_mass_flow_rate,
        coolant_density=coolant_density,
        coolant_dynamic_viscosity=coolant_dynamic_viscosity,
        target_reynolds_number=target_reynolds_number or 10000.0,
        minimum_rib_width=minimum_rib_width or 0.0005,
        minimum_channel_width=minimum_channel_width or 0.0005,
        maximum_channel_height=maximum_channel_height,
        channel_aspect_ratio=channel_aspect_ratio or 2.0,
        minimum_channel_count=int(minimum_channel_count or 4),
        maximum_channel_count=int(maximum_channel_count or 300),
        maximum_coolant_velocity=maximum_coolant_velocity,
        minimum_hydraulic_diameter=minimum_hydraulic_diameter,
        pressure_drop_limit=pressure_drop_limit,
        nozzle_length=nozzle_length,
        minimum_cooling_coverage=minimum_cooling_coverage,
    )

def calculate_recommended_regen_thermal_preview(results):
    """
    Runs a second non-destructive axial regen solve using the recommended
    cooling geometry.

    Manual results remain untouched.

    Output keys are stored as:
        recommended_regen_...
    """

    if results is None:
        return results

    required = [
        "recommended_number_of_coolant_channels",
        "recommended_coolant_channel_width",
        "recommended_coolant_channel_height",
        "recommended_rib_width",
    ]

    for key in required:
        if results.get(key) is None:
            results["recommended_regen_preview_status"] = "NO_RECOMMENDED_GEOMETRY"
            return results

    preview = dict(results)

    preview["number_of_coolant_channels"] = results.get("recommended_number_of_coolant_channels")
    preview["coolant_channel_width"] = results.get("recommended_coolant_channel_width")
    preview["coolant_channel_height"] = results.get("recommended_coolant_channel_height")
    preview["rib_width"] = results.get("recommended_rib_width")

    # Recalculate geometry-dependent coolant values
    preview["single_channel_flow_area"] = calculate_single_channel_flow_area(
        coolant_channel_width=preview.get("coolant_channel_width"),
        coolant_channel_height=preview.get("coolant_channel_height")
    )

    preview["total_coolant_flow_area"] = calculate_total_coolant_flow_area(
        single_channel_flow_area=preview.get("single_channel_flow_area"),
        number_of_coolant_channels=preview.get("number_of_coolant_channels")
    )

    preview["coolant_wetted_perimeter"] = calculate_coolant_wetted_perimeter(
        coolant_channel_width=preview.get("coolant_channel_width"),
        coolant_channel_height=preview.get("coolant_channel_height")
    )

    preview["coolant_hydraulic_diameter"] = calculate_coolant_hydraulic_diameter(
        single_channel_flow_area=preview.get("single_channel_flow_area"),
        coolant_wetted_perimeter=preview.get("coolant_wetted_perimeter")
    )

    preview["channel_pitch"] = calculate_channel_pitch(
        coolant_channel_width=preview.get("coolant_channel_width"),
        rib_width=preview.get("rib_width")
    )

    preview["channel_mid_radius"] = calculate_channel_mid_radius(
        cross_sectional_area=preview.get("throat_area"),
        throat_radius=preview.get("throat_radius"),
        coating_thickness=preview.get("coating_thickness"),
        hot_gas_wall_thickness=preview.get("hot_gas_wall_thickness"),
        coolant_channel_height=preview.get("coolant_channel_height")
    )

    preview["circumferential_channel_pitch"] = calculate_circumferential_channel_pitch(
        channel_mid_radius=preview.get("channel_mid_radius"),
        number_of_coolant_channels=preview.get("number_of_coolant_channels")
    )

    preview["effective_rib_width"] = calculate_effective_rib_width(
        circumferential_channel_pitch=preview.get("circumferential_channel_pitch"),
        coolant_channel_width=preview.get("coolant_channel_width")
    )

    preview["channel_fit_ratio"] = calculate_channel_fit_ratio(
        required_channel_pitch=preview.get("channel_pitch"),
        circumferential_channel_pitch=preview.get("circumferential_channel_pitch")
    )

    preview["channel_geometry_valid"] = calculate_channel_geometry_valid(
        effective_rib_width=preview.get("effective_rib_width"),
        requested_rib_width=preview.get("rib_width"),
        channel_fit_ratio=preview.get("channel_fit_ratio"),
        required_channel_pitch=preview.get("channel_pitch"),
        circumferential_channel_pitch=preview.get("circumferential_channel_pitch")
    )

    regen_station_count = results.get("regen_axial_requested_station_count")

    if regen_station_count is None:
        regen_station_count = results.get("regen_axial_station_count")

    if regen_station_count is None:
        regen_station_count = 100

    preview = calculate_regen_axial_marching_profile(
        preview,
        station_count=regen_station_count
    )

    recommended_profile = preview.get("regen_axial_profile")

    if not recommended_profile:
        results["recommended_regen_preview_status"] = "FAILED"
        return results

    results["recommended_regen_preview_status"] = "PASS"

    results["recommended_regen_axial_profile"] = recommended_profile
    results["recommended_regen_axial_station_count"] = preview.get("regen_axial_station_count")

    results["recommended_regen_axial_max_hot_wall_temperature"] = preview.get("regen_axial_max_hot_wall_temperature")
    results["recommended_regen_axial_max_hot_wall_temperature_location"] = preview.get("regen_axial_max_hot_wall_temperature_location")

    results["recommended_regen_axial_max_coolant_wall_temperature"] = preview.get("regen_axial_max_coolant_wall_temperature")
    results["recommended_regen_axial_max_heat_flux"] = preview.get("regen_axial_max_heat_flux")

    results["recommended_regen_axial_min_reynolds_number"] = preview.get("regen_axial_min_reynolds_number")
    results["recommended_regen_axial_total_pressure_drop"] = preview.get("regen_axial_total_pressure_drop")
    results["recommended_regen_axial_coolant_outlet_pressure"] = preview.get("coolant_outlet_pressure")

    results["recommended_regen_axial_coolant_outlet_temperature"] = preview.get("regen_axial_coolant_outlet_temperature")
    results["recommended_regen_axial_coolant_total_temperature_rise"] = preview.get("regen_axial_coolant_total_temperature_rise")
    results["recommended_regen_axial_total_heat_absorbed"] = preview.get("regen_axial_total_heat_absorbed")

    results["recommended_regen_axial_primary_thermal_bottleneck"] = preview.get("regen_axial_primary_thermal_bottleneck")
    results["recommended_regen_axial_thermal_bottleneck_counts"] = preview.get("regen_axial_thermal_bottleneck_counts")

    results["recommended_regen_axial_worst_material_margin"] = preview.get("regen_axial_worst_material_margin")
    results["recommended_regen_axial_worst_material_margin_location"] = preview.get("regen_axial_worst_material_margin_location")

    # Comparison deltas
    manual_twg = results.get("regen_axial_max_hot_wall_temperature")
    rec_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")

    if manual_twg is not None and rec_twg is not None:
        results["recommended_regen_hot_wall_temperature_change"] = rec_twg - manual_twg

    manual_re = results.get("regen_axial_min_reynolds_number")
    rec_re = results.get("recommended_regen_axial_min_reynolds_number")

    if manual_re is not None and rec_re is not None:
        results["recommended_regen_reynolds_change"] = rec_re - manual_re

        if manual_re > 0:
            results["recommended_regen_reynolds_factor"] = rec_re / manual_re

    manual_dp = results.get("regen_axial_total_pressure_drop")
    rec_dp = results.get("recommended_regen_axial_total_pressure_drop")

    if manual_dp is not None and rec_dp is not None:
        results["recommended_regen_pressure_drop_change"] = rec_dp - manual_dp

    return results

def apply_selected_material_properties(results):
    """
    Applies selected material database values to solver results.
    """

    if results is None:
        return results

    material_name = (
        results.get("selected_material")
        or results.get("selected_material_name")
        or results.get("hot_gas_liner_material")
        or results.get("wall_material")
        or results.get("material")
    )
    if not material_name:
        results["material_database_status"] = "MATERIAL_IDENTITY_REQUIRED"
        results["material_database_requested_material"] = None
        results["material_source_quality"] = "PLACEHOLDER"
        results["material_identity_authority_status"] = "MISSING_FAIL_CLOSED"
        return results

    if get_material_properties is None:
        results["material_database_status"] = "IMPORT_FAILED"
        return results

    material = get_material_properties(material_name)

    if material is None:
        results["material_database_status"] = "MATERIAL_NOT_FOUND"
        results["material_database_requested_material"] = material_name
        return results

    results["material_database_status"] = "PASS"
    results["selected_material_name"] = material.get("name")
    results["material_family"] = material.get("family")
    results["material_density"] = material.get("density")
    results["material_yield_strength"] = material.get("yield_strength")
    results["material_ultimate_tensile_strength"] = material.get("ultimate_tensile_strength")
    results["material_thermal_conductivity"] = material.get("thermal_conductivity")
    results["material_specific_heat"] = material.get("specific_heat")
    results["material_melting_point"] = material.get("melting_point")
    results["material_max_wall_temperature"] = material.get("max_recommended_wall_temperature")
    results["material_thermal_expansion"] = material.get("thermal_expansion")
    results["material_elastic_modulus"] = material.get("elastic_modulus")
    results["material_poisson_ratio"] = material.get("poisson_ratio")
    results["material_source_quality"] = material.get("source_quality")
    results["material_notes"] = material.get("notes")

    return results


def calculate_base_wall_thermal_expansion_strain(results):
    """Calculate free through-wall thermal strain differential.

    delta_epsilon = alpha * (T_hot_wall - T_coolant_wall)

    This deliberately does NOT calculate chamber-wall thermal
    stress. A valid stress calculation requires an appropriate
    structural constraint model.
    """

    import math

    results = (
        results
        if isinstance(results, dict)
        else {}
    )

    results[
        "material_thermal_stress"
    ] = None

    results[
        "material_thermal_stress_model_available"
    ] = False

    results[
        "material_thermal_stress_model_status"
    ] = (
        "NOT_MODELLED_REQUIRES_STRUCTURAL_CONSTRAINT_MODEL"
    )

    results[
        "material_thermal_expansion_relation"
    ] = (
        "delta_epsilon=alpha*(T_hot_wall-T_coolant_wall)"
    )

    results[
        "material_thermal_expansion_assumption"
    ] = (
        "FREE_UNCONSTRAINED_THERMAL_STRAIN_DIFFERENTIAL_ONLY"
    )

    def finite_number(value):
        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

        if not math.isfinite(value):
            return None

        return value

    alpha = finite_number(
        results.get(
            "material_thermal_expansion"
        )
    )

    hot_wall = finite_number(
        results.get(
            "hot_gas_side_wall_temperature"
        )
    )

    cool_wall = finite_number(
        results.get(
            "coolant_side_wall_temperature_calculated"
        )
    )

    if cool_wall is None:
        cool_wall = finite_number(
            results.get(
                "coolant_side_wall_temperature"
            )
        )

    results[
        "material_thermal_expansion_coefficient"
    ] = alpha

    results[
        "material_thermal_expansion_hot_wall_temperature"
    ] = hot_wall

    results[
        "material_thermal_expansion_coolant_wall_temperature"
    ] = cool_wall

    unavailable_keys = (
        "material_free_thermal_strain_differential",
        "material_free_thermal_strain_differential_magnitude",
        "material_free_thermal_strain_microstrain",
        "material_wall_temperature_difference",
    )

    if alpha is None:
        for key in unavailable_keys:
            results[key] = None

        results[
            "material_thermal_expansion_intelligence_status"
        ] = (
            "UNAVAILABLE_MISSING_THERMAL_EXPANSION_COEFFICIENT"
        )

        results[
            "material_thermal_expansion_intelligence_complete"
        ] = True

        return results

    if alpha < 0.0:
        for key in unavailable_keys:
            results[key] = None

        results[
            "material_thermal_expansion_intelligence_status"
        ] = (
            "UNAVAILABLE_INVALID_NEGATIVE_THERMAL_EXPANSION_COEFFICIENT"
        )

        results[
            "material_thermal_expansion_intelligence_complete"
        ] = True

        return results

    if (
        hot_wall is None
        or
        cool_wall is None
    ):
        for key in unavailable_keys:
            results[key] = None

        results[
            "material_thermal_expansion_intelligence_status"
        ] = (
            "UNAVAILABLE_MISSING_WALL_TEMPERATURES"
        )

        results[
            "material_thermal_expansion_intelligence_complete"
        ] = True

        return results

    delta_t = (
        hot_wall
        -
        cool_wall
    )

    free_strain = (
        alpha
        *
        delta_t
    )

    results[
        "material_wall_temperature_difference"
    ] = delta_t

    results[
        "material_free_thermal_strain_differential"
    ] = free_strain

    results[
        "material_free_thermal_strain_differential_magnitude"
    ] = abs(
        free_strain
    )

    results[
        "material_free_thermal_strain_microstrain"
    ] = (
        free_strain
        *
        1.0e6
    )

    results[
        "material_thermal_expansion_intelligence_status"
    ] = (
        "CALCULATED_FREE_THERMAL_STRAIN_DIFFERENTIAL"
    )

    results[
        "material_thermal_expansion_intelligence_complete"
    ] = True

    return results



def validate_recommended_regen_viability(results):
    """
    Final engineering viability check for the recommended regen design.

    This does not check whether the recommended geometry merely improves
    the manual design.

    It checks whether the recommended design is actually capable of cooling
    the engine within the current design requirements.
    """

    if results is None:
        return results

    reasons = []
    warnings = []
    recommendations = []

    score = 100.0

    preview_status = results.get("recommended_regen_preview_status")
    geometry_valid = results.get("recommended_channel_geometry_valid")

    max_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")
    material_limit = results.get("material_max_wall_temperature")
    material_margin = results.get("recommended_regen_axial_worst_material_margin")

    min_re = results.get("recommended_regen_axial_min_reynolds_number")
    target_re = (
        results.get("regen_derived_target_reynolds_number")
        or results.get("regen_target_reynolds_number")
    )

    pressure_drop = results.get("recommended_regen_axial_total_pressure_drop")
    pressure_drop_limit = results.get("regen_derived_pressure_drop_limit")

    bottleneck = results.get("recommended_regen_axial_primary_thermal_bottleneck")

    heat_absorbed = results.get("recommended_regen_axial_total_heat_absorbed")
    coolant_temp_rise = results.get("recommended_regen_axial_coolant_total_temperature_rise")

    # -------------------------------------------------
    # Preview availability
    # -------------------------------------------------

    if not solver_pass(preview_status):
        reasons.append("Recommended geometry thermal preview did not run successfully.")
        recommendations.append("Check recommended geometry generation and axial regen preview inputs.")
        score -= 35.0

    # -------------------------------------------------
    # Geometry validity
    # -------------------------------------------------

    if geometry_valid != 1 and geometry_valid != 1.0:
        reasons.append("Recommended channel geometry is not physically valid.")
        recommendations.append("Relax geometry constraints or increase available channel circumference.")
        score -= 30.0

    # -------------------------------------------------
    # Material temperature margin
    # -------------------------------------------------

    if material_limit is not None and max_twg is not None:
        if max_twg > material_limit:
            over_temp = max_twg - material_limit
            reasons.append(
                f"Recommended hot-gas wall temperature exceeds material limit by {over_temp:.3g} K."
            )
            recommendations.append("Increase coolant-side heat transfer or choose a higher-temperature material.")
            recommendations.append("Consider increasing coolant mass flow, channel coverage, or adding film cooling.")
            score -= min(45.0, 15.0 + 30.0 * (over_temp / max(material_limit, 1e-9)))

        elif material_margin is not None and material_margin < 100.0:
            warnings.append("Recommended material margin is low.")
            recommendations.append("Increase material margin before treating the design as reusable.")
            score -= 10.0

    else:
        warnings.append("Material temperature limit or recommended wall temperature is missing.")
        score -= 10.0

    # -------------------------------------------------
    # Reynolds / coolant-side validity
    # -------------------------------------------------

    if min_re is not None and target_re is not None:
        re_ratio = min_re / max(target_re, 1e-9)
        results["recommended_regen_reynolds_target_ratio"] = re_ratio

        if re_ratio < 0.5:
            reasons.append(
                f"Recommended minimum Reynolds number is far below target ({min_re:.3g} vs {target_re:.3g})."
            )
            recommendations.append("Increase coolant velocity or reduce total coolant flow area.")
            score -= 20.0

        elif re_ratio < 1.0:
            warnings.append(
                f"Recommended minimum Reynolds number is below target ({min_re:.3g} vs {target_re:.3g})."
            )
            recommendations.append("Improve coolant-side heat transfer or lower the target if justified by engine scale.")
            score -= 8.0

    else:
        warnings.append("Recommended Reynolds number or target Reynolds number is missing.")
        score -= 8.0

    # -------------------------------------------------
    # Pressure drop
    # -------------------------------------------------

    if pressure_drop is not None and pressure_drop_limit is not None and pressure_drop_limit > 0:
        dp_ratio = pressure_drop / pressure_drop_limit
        results["recommended_regen_pressure_drop_limit_ratio"] = dp_ratio

        if dp_ratio > 1.0:
            reasons.append("Recommended coolant pressure drop exceeds the derived pressure-drop limit.")
            recommendations.append("Increase total coolant flow area, reduce channel length losses, or relax pressure-drop allowance.")
            score -= 20.0

        elif dp_ratio > 0.8:
            warnings.append("Recommended coolant pressure drop is close to the limit.")
            score -= 5.0

    # -------------------------------------------------
    # Thermal bottleneck
    # -------------------------------------------------

    if bottleneck == "coolant_side":
        warnings.append("Recommended design is still coolant-side heat-transfer limited.")
        recommendations.append("Increase coolant-side heat-transfer coefficient using higher velocity, smaller hydraulic diameter, or better coolant.")

        # Do not hard-fail for this alone, because most regen systems are
        # intentionally coolant-side controlled to some degree.
        score -= 5.0

    # -------------------------------------------------
    # Heat pickup sanity
    # -------------------------------------------------

    if heat_absorbed is None or heat_absorbed <= 0:
        reasons.append("Recommended design absorbs no useful heat.")
        recommendations.append("Check heat-flux calculation and coolant geometry.")
        score -= 20.0

    if coolant_temp_rise is not None and coolant_temp_rise < 1.0:
        warnings.append("Recommended coolant temperature rise is very small.")
        recommendations.append("Check whether heat transfer area or heat flux is being under-predicted.")
        score -= 5.0

    # -------------------------------------------------
    # Final classification
    # -------------------------------------------------

    score = max(0.0, min(100.0, score))

    if reasons:
        status = "FAIL"
    elif score < 70.0:
        status = "MARGINAL"
    else:
        status = "PASS"

    results["recommended_regen_viability_status"] = status
    results["recommended_regen_viability_score"] = score
    results["recommended_regen_viability_reasons"] = reasons
    results["recommended_regen_viability_warnings"] = warnings
    results["recommended_regen_viability_recommendations"] = recommendations

    return results

def calculate_propellant_mass_flow_split(results):
    """
    Calculates fuel and oxidizer mass flow from total mass flow and mixture ratio.

    mixture_ratio = oxidizer_mass_flow / fuel_mass_flow
    total_mass_flow = fuel_mass_flow + oxidizer_mass_flow
    """

    if results is None:
        return results

    # R2D-B-R2:
    # This owner certifies whether the CURRENT results state produced
    # a valid propellant split. Fuel/oxidizer numerical outputs are
    # shared with solve_engine and are therefore not deleted here.
    results["propellant_mass_flow_split_valid"] = 0.0

    total_mdot = (
        results.get("mass_flow_rate")
        or results.get("total_mass_flow_rate")
        or results.get("mass_flow")
    )

    mixture_ratio = (
        results.get("mixture_ratio")
        or results.get("oxidizer_fuel_ratio")
        or results.get("of_ratio")
    )

    try:
        total_mdot = float(total_mdot)
        mixture_ratio = float(mixture_ratio)
    except Exception:
        return results

    if total_mdot <= 0 or mixture_ratio <= 0:
        return results

    fuel_mdot = total_mdot / (1.0 + mixture_ratio)
    oxidizer_mdot = total_mdot - fuel_mdot

    results["fuel_mass_flow_rate"] = fuel_mdot
    results["oxidizer_mass_flow_rate"] = oxidizer_mdot
    results["propellant_mass_flow_split_valid"] = 1.0

    return results

def solve_regen_cooling_feasibility(results):
    """
    System-level regen feasibility solver.

    Determines whether the current engine can be cooled by regenerative
    propellant cooling alone, and estimates what must change if not.

    This is a feasibility model, not a replacement for the detailed axial solver.
    """

    if results is None:
        return results

    status = "UNKNOWN"
    reasons = []
    recommendations = []

    material_limit = results.get("material_max_wall_temperature")
    max_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")
    current_mdot_coolant = results.get("coolant_mass_flow_rate")
    current_heat_absorbed = results.get("recommended_regen_axial_total_heat_absorbed")
    coolant_cp = results.get("coolant_specific_heat_cp")

    pressure_drop = results.get("recommended_regen_axial_total_pressure_drop")
    pressure_drop_limit = results.get("regen_derived_pressure_drop_limit")

    recommended_profile = results.get("recommended_regen_axial_profile") or []

    if (
        material_limit is None
        or max_twg is None
        or current_mdot_coolant is None
        or current_heat_absorbed is None
        or current_mdot_coolant <= 0
        or current_heat_absorbed <= 0
    ):
        results["regen_feasibility_status"] = "INSUFFICIENT_DATA"
        results["regen_feasibility_reasons"] = [
            "Missing recommended thermal preview, material, coolant, or heat absorption data."
        ]
        results["regen_feasibility_recommendations"] = [
            "Run CEA, apply regen, generate recommended geometry, and run thermal preview."
        ]
        return results

    over_temperature = max_twg - material_limit
    results["regen_feasibility_wall_over_temperature"] = over_temperature

    if over_temperature <= 0:
        status = "REGEN_ONLY_FEASIBLE"
        reasons.append("Recommended regenerative cooling keeps wall temperature below material limit.")
    else:
        status = "REGEN_ONLY_NOT_FEASIBLE"
        reasons.append(
            f"Recommended hot wall temperature exceeds material limit by {over_temperature:.3g} K."
        )

    # -------------------------------------------------
    # Robust recovery-temperature estimate
    # -------------------------------------------------

    recovery_temperatures = []

    for station in recommended_profile:
        try:
            value = station.get("recovery_temperature")
            if value is not None:
                recovery_temperatures.append(float(value))
        except Exception:
            pass

    gas_recovery_temp = None

    if recovery_temperatures:
        gas_recovery_temp = max(recovery_temperatures)

    if gas_recovery_temp is None:
        gas_recovery_temp = results.get("selected_gas_side_recovery_temperature")

    if gas_recovery_temp is None:
        gas_recovery_temp = results.get("chamber_temperature")

    results["regen_feasibility_reference_recovery_temperature"] = gas_recovery_temp

    # -------------------------------------------------
    # Required cooling improvement estimate
    # -------------------------------------------------

    required_cooling_factor = None

    if (
        gas_recovery_temp is not None
        and gas_recovery_temp > material_limit
        and gas_recovery_temp > max_twg
    ):
        current_temp_drop = gas_recovery_temp - max_twg
        required_temp_drop = gas_recovery_temp - material_limit

        if current_temp_drop > 0:
            required_cooling_factor = required_temp_drop / current_temp_drop

    # Fallback if recovery temperature cannot produce a stable estimate.
    if required_cooling_factor is None and material_limit is not None and max_twg is not None:
        if material_limit > 0 and max_twg > material_limit:
            required_cooling_factor = max_twg / material_limit

    if required_cooling_factor is not None:
        results["regen_required_cooling_improvement_factor"] = required_cooling_factor

        if required_cooling_factor > 1.0:
            reasons.append(
                f"Cooling effectiveness must increase by approximately {required_cooling_factor:.3g}x."
            )

    # -------------------------------------------------
    # Required coolant mass-flow estimate
    # -------------------------------------------------

    required_coolant_mdot = None

    if required_cooling_factor is not None and required_cooling_factor > 0:
        required_coolant_mdot = current_mdot_coolant * required_cooling_factor

        results["regen_required_coolant_mass_flow_rate"] = required_coolant_mdot
        results["regen_required_coolant_mass_flow_increase"] = (
            required_coolant_mdot - current_mdot_coolant
        )
        results["regen_required_coolant_mass_flow_factor"] = (
            required_coolant_mdot / current_mdot_coolant
        )

    # -------------------------------------------------
    # Coolant mass-flow fraction
    # -------------------------------------------------

    # R2D-B-R3-R1:
    # These values are derived from the current engine/coolant flow
    # state and must never survive from a previous feasibility pass.
    results["regen_current_coolant_mass_flow_fraction"] = None
    results["regen_required_coolant_mass_flow_fraction"] = None
    results["regen_current_coolant_available_flow_fraction"] = None
    results["regen_required_coolant_available_flow_fraction"] = None

    results = calculate_propellant_mass_flow_split(results)

    split_valid = (
        results.get("propellant_mass_flow_split_valid") == 1.0
    )

    engine_mdot = (
            results.get("mass_flow_rate")
            or results.get("total_mass_flow_rate")
            or results.get("mass_flow")
    )

    if split_valid:
        fuel_mdot = results.get("fuel_mass_flow_rate")
        oxidizer_mdot = results.get("oxidizer_mass_flow_rate")
    else:
        fuel_mdot = None
        oxidizer_mdot = None

    def _availability_fluid_identity(value):
        """
        Resolves coolant-availability identity using LEAF's existing
        canonical fluid-property name owner.

        No local alias table is owned here.
        """
        name = str(value or "").strip()

        if not name:
            return None

        properties = (
            get_fluid_properties(name)
            if get_fluid_properties is not None
            else None
        )

        if isinstance(properties, dict):
            canonical_name = str(
                properties.get("name")
                or ""
            ).strip()

            if canonical_name:
                return (
                    "fluid",
                    canonical_name.casefold(),
                )

        return (
            "name",
            name.casefold(),
        )

    coolant_identity = _availability_fluid_identity(
        results.get("selected_coolant_name")
    )

    fuel_identity = _availability_fluid_identity(
        results.get(
            "fuel",
            results.get("selected_fuel"),
        )
    )

    oxidizer_identity = _availability_fluid_identity(
        results.get(
            "oxidizer",
            results.get("selected_oxidizer"),
        )
    )

    available_coolant_mdot = None
    available_coolant_basis = "unknown"

    if not split_valid:
        available_coolant_basis = "invalid_propellant_mass_flow_split"

    elif (
        fuel_mdot is not None
        and coolant_identity is not None
        and coolant_identity == fuel_identity
    ):
        available_coolant_mdot = fuel_mdot
        available_coolant_basis = "fuel"

    elif (
        oxidizer_mdot is not None
        and coolant_identity is not None
        and coolant_identity == oxidizer_identity
    ):
        available_coolant_mdot = oxidizer_mdot
        available_coolant_basis = "oxidizer"

    elif coolant_identity is None:
        available_coolant_basis = "missing_selected_coolant"

    else:
        available_coolant_basis = "unmatched_selected_coolant"

    results["regen_available_coolant_mass_flow_rate"] = (
        available_coolant_mdot
    )

    results["regen_available_coolant_basis"] = (
        available_coolant_basis
    )

    if engine_mdot is not None and engine_mdot > 0:
        results["regen_current_coolant_mass_flow_fraction"] = (
                current_mdot_coolant / engine_mdot
        )

        if required_coolant_mdot is not None:
            results["regen_required_coolant_mass_flow_fraction"] = (
                    required_coolant_mdot / engine_mdot
            )

    if available_coolant_mdot is not None and available_coolant_mdot > 0:
        results["regen_current_coolant_available_flow_fraction"] = (
                current_mdot_coolant / available_coolant_mdot
        )

        if required_coolant_mdot is not None:
            required_available_fraction = required_coolant_mdot / available_coolant_mdot
            results["regen_required_coolant_available_flow_fraction"] = required_available_fraction

            if required_available_fraction > 1.0:
                reasons.append(
                    f"Required coolant mass flow exceeds available {available_coolant_basis} flow."
                )
                recommendations.append(
                    "Regen-only cooling cannot be achieved using the current propellant flow split."
                )
                recommendations.append(
                    "Evaluate film cooling, lower chamber heat load, higher-temperature material, or a redesigned mixture ratio/engine scale."
                )

            elif required_available_fraction > 0.8:
                reasons.append(
                    f"Required coolant uses more than 80% of available {available_coolant_basis} flow."
                )
                recommendations.append(
                    "Check injector mixture-ratio impact before accepting the cooling design."
                )

    # -------------------------------------------------
    # Pressure-drop feasibility
    # -------------------------------------------------

    if pressure_drop is not None and pressure_drop_limit is not None and pressure_drop_limit > 0:
        pressure_ratio = pressure_drop / pressure_drop_limit
        results["regen_feasibility_pressure_drop_ratio"] = pressure_ratio

        if pressure_ratio > 1.0:
            reasons.append("Recommended cooling pressure drop exceeds allowed pressure-drop budget.")
            recommendations.append("Increase channel flow area or raise feed-system pressure capability.")

    # -------------------------------------------------
    # Film cooling estimate
    # -------------------------------------------------

    if over_temperature > 0 and gas_recovery_temp is not None and gas_recovery_temp > material_limit:
        denominator = max(gas_recovery_temp - material_limit, 1e-9)
        film_fraction_estimate = min(0.5, max(0.0, over_temperature / denominator))
        results["regen_estimated_film_cooling_fraction"] = film_fraction_estimate

        if film_fraction_estimate > 0:
            recommendations.append(
                f"Consider adding film cooling. First-pass estimated film fraction: {film_fraction_estimate:.3g}."
            )

    # -------------------------------------------------
    # Material requirement
    # -------------------------------------------------

    results["regen_required_material_temperature_limit"] = max_twg

    if max_twg > material_limit:
        recommendations.append(
            f"Material system would need to tolerate at least {max_twg:.3g} K at the hot wall, before safety margin."
        )

    # -------------------------------------------------
    # Final recommendations
    # -------------------------------------------------

    if status == "REGEN_ONLY_FEASIBLE":
        recommendations.append("Proceed to material-margin optimisation and axial thermal visualisation.")
    else:
        recommendations.append("Do not accept this engine as regen-cooled yet.")
        recommendations.append("Run a material-aware optimiser before proceeding to final engine design.")
        recommendations.append("Evaluate higher coolant mass flow, variable channels, film cooling, or reduced chamber thermal load.")

    results["regen_feasibility_status"] = status
    results["regen_feasibility_reasons"] = reasons
    results["regen_feasibility_recommendations"] = recommendations

    return results

def calculate_regen_cross_section_outer_radius(
        cross_sectional_area=None,
        throat_radius=None,
        hot_gas_wall_thickness=None,
        coolant_channel_height=None,
        outer_jacket_thickness=None,
        coating_thickness=None
):
    """
    Estimated outside radius of the regen wall stack at the selected station.

    Inner gas radius comes from local area if available,
    otherwise throat radius is used as fallback.

    Rout = Rgas + coating + twg + channel_height + jacket
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coating_thickness,
            coolant_channel_height,
            cross_sectional_area,
            hot_gas_wall_thickness,
            outer_jacket_thickness,
        )
    ):
        return None


    gas_radius = None

    if cross_sectional_area is not None and cross_sectional_area > 0:
        gas_radius = math.sqrt(cross_sectional_area / math.pi)
    elif throat_radius is not None and throat_radius > 0:
        gas_radius = throat_radius

    if gas_radius is None:
        return None

    coating = coating_thickness if coating_thickness is not None else 0.0
    wall = hot_gas_wall_thickness if hot_gas_wall_thickness is not None else 0.0
    channel = coolant_channel_height if coolant_channel_height is not None else 0.0
    jacket = outer_jacket_thickness if outer_jacket_thickness is not None else 0.0

    return gas_radius + coating + wall + channel + jacket

# =========================================================
# REGENERATIVE COOLING THERMAL MODEL
# =========================================================

def select_regen_cooling_strategy(results):
    """
    Selects the next realistic cooling strategy after regen feasibility analysis.

    This is a design decision layer. It does not replace the thermal solver.
    """

    if results is None:
        return results

    feasibility = results.get("regen_feasibility_status")
    viability = results.get("recommended_regen_viability_status")

    required_available_fraction = results.get("regen_required_coolant_available_flow_fraction")
    required_material_limit = results.get("regen_required_material_temperature_limit")
    current_material_limit = results.get("material_max_wall_temperature")
    film_fraction = results.get("regen_estimated_film_cooling_fraction")
    pressure_ratio = results.get("regen_feasibility_pressure_drop_ratio")

    strategy = "UNKNOWN"
    reasons = []
    next_actions = []

    if feasibility == "REGEN_ONLY_FEASIBLE" and solver_pass(viability):
        strategy = "REGEN_ONLY_ACCEPTABLE"
        reasons.append("Recommended regen geometry is thermally viable.")
        next_actions.append("Proceed to material-margin optimisation and axial thermal visualisation.")

    elif required_available_fraction is not None and required_available_fraction > 1.0:
        strategy = "REGEN_PLUS_FILM_OR_REDUCED_HEAT_LOAD_REQUIRED"
        reasons.append(
            "Required coolant mass flow exceeds available propellant coolant flow."
        )
        next_actions.append(
            "Evaluate regen plus film cooling because regen-only cannot supply enough coolant."
        )
        next_actions.append(
            "Evaluate reduced chamber pressure, reduced chamber temperature, or lower heat-flux design."
        )

    elif required_material_limit is not None and current_material_limit is not None:
        if required_material_limit > current_material_limit * 1.5:
            strategy = "MATERIAL_UPGRADE_ALONE_INSUFFICIENT"
            reasons.append(
                "Required material temperature capability is far above the selected material limit."
            )
            next_actions.append(
                "Do not rely on material change alone; combine better material with film cooling or lower heat load."
            )
        else:
            strategy = "MATERIAL_UPGRADE_CANDIDATE"
            reasons.append(
                "A higher-temperature material may make the design viable."
            )
            next_actions.append(
                "Evaluate a material with higher allowable wall temperature and conductivity."
            )

    elif film_fraction is not None and film_fraction > 0.0:
        strategy = "FILM_COOLING_CANDIDATE"
        reasons.append("Film cooling is likely required.")
        next_actions.append("Run film cooling effectiveness model.")

    else:
        strategy = "FURTHER_ANALYSIS_REQUIRED"
        reasons.append("Cooling strategy could not be selected from available data.")
        next_actions.append("Check feasibility outputs and material/coolant inputs.")

    if pressure_ratio is not None and pressure_ratio > 0.8:
        reasons.append("Cooling pressure drop is close to the design limit.")
        next_actions.append("Pressure drop must be included in the next optimisation pass.")

    results["regen_selected_cooling_strategy"] = strategy
    results["regen_cooling_strategy_reasons"] = reasons
    results["regen_cooling_strategy_next_actions"] = next_actions

    return results

def estimate_film_cooling_requirement(results):
    """
    First-pass film cooling requirement model.

    This estimates how much film cooling effectiveness is required to bring
    the recommended hot wall temperature down to the material limit.

    This is not a final CFD film model. It is a system-level screening tool.
    """

    if results is None:
        return results

    max_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")
    material_limit = results.get("material_max_wall_temperature")
    recovery_temp = results.get("regen_feasibility_reference_recovery_temperature")
    available_coolant_mdot = results.get("regen_available_coolant_mass_flow_rate")
    fuel_mdot = results.get("fuel_mass_flow_rate")

    if (
        max_twg is None
        or material_limit is None
        or recovery_temp is None
        or recovery_temp <= material_limit
    ):
        results["film_cooling_status"] = "INSUFFICIENT_DATA"
        return results

    required_wall_temperature_drop = max_twg - material_limit

    required_effectiveness = required_wall_temperature_drop / max(
        recovery_temp - material_limit,
        1e-9
    )

    required_effectiveness = max(0.0, min(1.0, required_effectiveness))

    results["film_required_wall_temperature_drop"] = required_wall_temperature_drop
    results["film_required_effectiveness"] = required_effectiveness

    # First-pass mass fraction estimate.
    # Conservative screening: film fraction roughly scales with effectiveness.
    # Clamp because very high film fractions usually mean "not practical".
    estimated_film_fraction = min(0.5, required_effectiveness)

    results["film_estimated_film_fraction_of_available_fuel"] = estimated_film_fraction

    if available_coolant_mdot is not None:
        results["film_estimated_mass_flow_rate"] = (
            estimated_film_fraction * available_coolant_mdot
        )

    if fuel_mdot is not None and fuel_mdot > 0:
        film_mdot = results.get("film_estimated_mass_flow_rate")

        if film_mdot is not None:
            results["film_estimated_fraction_of_fuel_flow"] = film_mdot / fuel_mdot

    if required_effectiveness > 0.5:
        status = "FILM_COOLING_SEVERE"
    elif required_effectiveness > 0.25:
        status = "FILM_COOLING_REQUIRED"
    elif required_effectiveness > 0.0:
        status = "FILM_COOLING_LIGHT"
    else:
        status = "NO_FILM_REQUIRED"

    results["film_cooling_status"] = status

    recommendations = []

    if status == "FILM_COOLING_SEVERE":
        recommendations.append(
            "Required film cooling effectiveness is severe; film cooling alone may not be sufficient."
        )
        recommendations.append(
            "Combine film cooling with reduced chamber heat load, material upgrade, or variable channel geometry."
        )

    elif status == "FILM_COOLING_REQUIRED":
        recommendations.append(
            "Film cooling may make the engine thermally plausible but will reduce combustion efficiency."
        )

    elif status == "FILM_COOLING_LIGHT":
        recommendations.append(
            "Light film cooling may be sufficient if material margin and injector design are acceptable."
        )

    else:
        recommendations.append("Film cooling is not required by this first-pass estimate.")

    results["film_cooling_recommendations"] = recommendations

    return results

def build_axial_film_cooling_preview(results):
    """
    First-pass axial film-cooling preview.

    Applies a decaying film-cooling effectiveness along the recommended
    regen axial profile. This gives LEAF a station-by-station estimate instead
    of a single global film factor.
    """

    if results is None:
        return results

    profile = results.get("recommended_regen_axial_profile")

    if not profile:
        results["film_axial_preview_status"] = "NO_RECOMMENDED_PROFILE"
        return results

    film_effectiveness_initial = results.get("combined_film_effectiveness_target")

    if film_effectiveness_initial is None:
        film_effectiveness_initial = results.get("film_required_effectiveness")

    if film_effectiveness_initial is None:
        results["film_axial_preview_status"] = "NO_FILM_EFFECTIVENESS"
        return results

    film_effectiveness_initial = max(0.0, min(0.95, film_effectiveness_initial))

    material_limit = results.get("material_max_wall_temperature")
    material_factor = (
            results.get("combined_material_factor_target")
            or results.get("combined_max_material_factor")
            or 1.0
    )

    if material_limit is None:
        results["film_axial_preview_status"] = "NO_MATERIAL_LIMIT"
        return results

    improved_material_limit = material_limit * material_factor

    nozzle_length = results.get("nozzle_length")

    if nozzle_length is None or nozzle_length <= 0:
        nozzle_length = max([station.get("x", 0.0) for station in profile] or [1.0])

    film_decay_length_fraction = results.get("film_decay_length_fraction", 0.45)
    film_decay_length = max(nozzle_length * film_decay_length_fraction, 1e-9)

    coolant_reference_temperature = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    film_profile = []

    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None
    failed_station_count = 0

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)

        try:
            x = float(x)
        except Exception:
            x = 0.0

        twg = station.get("hot_gas_side_wall_temperature")

        if twg is None:
            twg = station.get("Twg")

        try:
            twg = float(twg)
        except Exception:
            film_profile.append(new_station)
            continue

        # x = 0 is throat/chamber-side in LEAF's axial convention.
        # Film is strongest near injection and decays downstream.
        local_effectiveness = film_effectiveness_initial * math.exp(-x / film_decay_length)
        local_effectiveness = max(0.0, min(0.95, local_effectiveness))

        film_cooled_twg = twg - local_effectiveness * (twg - coolant_reference_temperature)
        film_cooled_twg = max(film_cooled_twg, coolant_reference_temperature)

        margin = improved_material_limit - film_cooled_twg

        new_station["film_effectiveness"] = local_effectiveness
        new_station["film_cooled_hot_wall_temperature"] = film_cooled_twg
        new_station["film_material_limit"] = improved_material_limit
        new_station["film_material_margin"] = margin
        new_station["film_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_station_count += 1

        if max_twg is None or film_cooled_twg > max_twg:
            max_twg = film_cooled_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        film_profile.append(new_station)

    results["film_axial_profile"] = film_profile
    results["film_axial_station_count"] = len(film_profile)
    results["film_axial_preview_status"] = "PASS" if failed_station_count == 0 else "FAIL"
    results["film_axial_failed_station_count"] = failed_station_count
    results["film_axial_max_hot_wall_temperature"] = max_twg
    results["film_axial_max_hot_wall_temperature_location"] = max_twg_location
    results["film_axial_worst_material_margin"] = worst_margin
    results["film_axial_worst_material_margin_location"] = worst_margin_location
    results["film_axial_initial_effectiveness"] = film_effectiveness_initial
    results["film_axial_decay_length"] = film_decay_length

    return results

def build_film_material_axial_preview(results):
    """
    Axial preview for film cooling plus material upgrade.

    This checks whether the film-cooled wall temperature becomes acceptable
    when the material capability target is also applied.
    """

    if results is None:
        return results

    film_profile = results.get("film_axial_profile")

    if not film_profile:
        results["film_material_axial_preview_status"] = "NO_FILM_PROFILE"
        return results

    material_limit = results.get("material_max_wall_temperature")
    material_factor = results.get("combined_material_factor_target", 1.0)

    if material_limit is None:
        results["film_material_axial_preview_status"] = "NO_MATERIAL_LIMIT"
        return results

    improved_material_limit = material_limit * material_factor

    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None
    failed_station_count = 0

    combined_profile = []

    for station in film_profile:
        new_station = dict(station)

        x = station.get("x", 0.0)
        film_twg = station.get("film_cooled_hot_wall_temperature")

        try:
            film_twg = float(film_twg)
        except Exception:
            combined_profile.append(new_station)
            continue

        margin = improved_material_limit - film_twg

        new_station["film_material_hot_wall_temperature"] = film_twg
        new_station["film_material_limit"] = improved_material_limit
        new_station["film_material_margin"] = margin
        new_station["film_material_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_station_count += 1

        if max_twg is None or film_twg > max_twg:
            max_twg = film_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        combined_profile.append(new_station)

    results["film_material_axial_profile"] = combined_profile
    results["film_material_axial_station_count"] = len(combined_profile)
    results["film_material_axial_preview_status"] = "PASS" if failed_station_count == 0 else "FAIL"
    results["film_material_axial_failed_station_count"] = failed_station_count
    results["film_material_axial_max_hot_wall_temperature"] = max_twg
    results["film_material_axial_max_hot_wall_temperature_location"] = max_twg_location
    results["film_material_axial_worst_material_margin"] = worst_margin
    results["film_material_axial_worst_material_margin_location"] = worst_margin_location
    results["film_material_axial_material_limit"] = improved_material_limit

    return results

def build_full_combined_component_axial_preview(results):
    """
    Axial preview applying the full combined cooling stack:

    - film cooling
    - material upgrade
    - heat-load reduction
    - further regen/channel improvement

    This is more honest than the older single combined_factor preview because
    each contribution is applied separately and reported separately.
    """

    if results is None:
        return results

    profile = results.get("recommended_regen_axial_profile")

    if not profile:
        results["full_combined_component_preview_status"] = "NO_RECOMMENDED_PROFILE"
        return results

    material_limit = results.get("material_max_wall_temperature")
    coolant_ref = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or results.get("combined_prediction_coolant_reference_temperature")
        or 293.0
    )

    material_factor = results.get("combined_material_factor_target") or 1.0
    film_initial = results.get("combined_film_effectiveness_target") or 0.0
    heat_load_reduction = results.get("combined_heat_load_reduction_target") or 0.0
    regen_improvement = results.get("combined_regen_improvement_factor_target") or 1.0

    if material_limit is None:
        results["full_combined_component_preview_status"] = "NO_MATERIAL_LIMIT"
        return results

    material_factor = max(0.1, material_factor)
    film_initial = max(0.0, min(0.95, film_initial))
    heat_load_reduction = max(0.0, min(0.95, heat_load_reduction))
    regen_improvement = max(0.1, regen_improvement)

    improved_material_limit = material_limit * material_factor

    nozzle_length = results.get("nozzle_length")

    if nozzle_length is None or nozzle_length <= 0:
        nozzle_length = max([station.get("x", 0.0) for station in profile] or [1.0])

    film_decay_length_fraction = results.get("film_decay_length_fraction", 0.45)
    film_decay_length = max(nozzle_length * film_decay_length_fraction, 1e-9)

    full_profile = []

    max_twg = None
    max_twg_location = None
    worst_margin = None
    worst_margin_location = None
    failed_station_count = 0

    for station in profile:
        new_station = dict(station)

        x = station.get("x", 0.0)

        try:
            x = float(x)
        except Exception:
            x = 0.0

        twg = (
            station.get("hot_gas_side_wall_temperature")
            or station.get("Twg")
        )

        try:
            twg = float(twg)
        except Exception:
            full_profile.append(new_station)
            continue

        # 1) Film cooling, with axial decay
        local_film_effectiveness = film_initial * math.exp(-x / film_decay_length)
        local_film_effectiveness = max(0.0, min(0.95, local_film_effectiveness))

        after_film_twg = twg - local_film_effectiveness * (twg - coolant_ref)
        after_film_twg = max(after_film_twg, coolant_ref)

        # 2) Reduced heat load
        # Reduces remaining wall-coolant thermal gap.
        after_heat_load_twg = coolant_ref + (
            (after_film_twg - coolant_ref) * (1.0 - heat_load_reduction)
        )

        # 3) Further regen/channel improvement
        # Also reduces remaining wall-coolant thermal gap.
        final_twg = coolant_ref + (
            (after_heat_load_twg - coolant_ref) / regen_improvement
        )

        final_twg = max(final_twg, coolant_ref)

        margin = improved_material_limit - final_twg

        new_station["full_combined_film_effectiveness"] = local_film_effectiveness
        new_station["full_combined_after_film_twg"] = after_film_twg
        new_station["full_combined_after_heat_load_twg"] = after_heat_load_twg
        new_station["full_combined_hot_wall_temperature"] = final_twg
        new_station["full_combined_material_limit"] = improved_material_limit
        new_station["full_combined_material_margin"] = margin
        new_station["full_combined_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_station_count += 1

        if max_twg is None or final_twg > max_twg:
            max_twg = final_twg
            max_twg_location = x

        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
            worst_margin_location = x

        full_profile.append(new_station)

    results["full_combined_component_axial_profile"] = full_profile
    results["full_combined_component_station_count"] = len(full_profile)
    results["full_combined_component_material_limit"] = improved_material_limit
    results["full_combined_component_max_hot_wall_temperature"] = max_twg
    results["full_combined_component_max_hot_wall_temperature_location"] = max_twg_location
    results["full_combined_component_worst_material_margin"] = worst_margin
    results["full_combined_component_worst_material_margin_location"] = worst_margin_location
    results["full_combined_component_failed_station_count"] = failed_station_count
    results["full_combined_component_film_effectiveness_target"] = film_initial
    results["full_combined_component_heat_load_reduction_target"] = heat_load_reduction
    results["full_combined_component_regen_improvement_target"] = regen_improvement

    if failed_station_count == 0:
        results["full_combined_component_preview_status"] = "PASS"
    else:
        results["full_combined_component_preview_status"] = "FAIL"

    return results

def evaluate_material_candidates_for_cooling(results):
    """
    Tests real database materials against the current thermal requirement.

    This replaces the abstract question:
        "What if material factor = 1.6?"

    with:
        "Which real material in the database can survive this?"
    """

    if results is None:
        return results

    if get_material_names is None or get_material_properties is None:
        results["material_candidate_status"] = "IMPORT_FAILED"
        return results

    required_limit = results.get("regen_required_material_temperature_limit")
    film_material_max_twg = results.get("film_material_axial_max_hot_wall_temperature")
    recommended_max_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")

    full_combined_twg = results.get("full_combined_component_max_hot_wall_temperature")

    target_temperature = (
            full_combined_twg
            or film_material_max_twg
            or recommended_max_twg
            or required_limit
    )

    if target_temperature is None:
        results["material_candidate_status"] = "INSUFFICIENT_DATA"
        return results

    candidates = []

    for name in get_material_names():
        material = get_material_properties(name)

        if material is None:
            continue

        limit = material.get("max_recommended_wall_temperature")
        conductivity = material.get("thermal_conductivity")

        if limit is None:
            continue

        margin = limit - target_temperature

        if margin >= 100.0:
            status = "PASS_WITH_MARGIN"
        elif margin >= 0.0:
            status = "PASS_LOW_MARGIN"
        else:
            status = "FAIL"

        score = margin

        if conductivity is not None:
            score += 0.1 * conductivity

        candidates.append({
            "name": material.get("name"),
            "family": material.get("family"),
            "max_wall_temperature": limit,
            "thermal_conductivity": conductivity,
            "margin": margin,
            "status": status,
            "score": score,
            "notes": material.get("notes"),
        })

    candidates.sort(key=lambda item: item.get("score", -1e99), reverse=True)

    passing = [
        item for item in candidates
        if item.get("status") in ("PASS_WITH_MARGIN", "PASS_LOW_MARGIN")
    ]

    results["material_candidate_status"] = "COMPLETE"
    results["material_candidate_target_temperature"] = target_temperature
    results["material_candidate_count"] = len(candidates)
    results["material_candidate_passing_count"] = len(passing)
    results["material_candidate_best"] = candidates[0] if candidates else None
    results["material_candidate_passing"] = passing[:5]
    results["material_candidate_all"] = candidates
    results["material_candidate_best_candidate"] = candidates[0] if candidates else None
    results["material_candidate_passing_candidates"] = passing[:5]
    results["material_candidate_screened_candidates"] = candidates
    results["material_screened_candidates"] = candidates

    if passing:
        results["material_candidate_recommendation"] = (
            "At least one real database material passes the current film/material screening temperature."
        )
    else:
        results["material_candidate_recommendation"] = (
            "No current database material passes. Cooling strategy still requires heat-load reduction, better film model, or new materials."
        )

    return results

def run_material_aware_combined_cooling_optimiser(results):
    """
    Material-aware combined cooling optimiser v1.

    This is a conservative screening optimiser.

    It searches combinations of:
    - real database material temperature limits
    - film cooling effectiveness
    - heat-load reduction
    - regen-side improvement factor

    Important:
    - This does NOT create a final validation pass unless source validation is ready.
    - Placeholder / partial source data can only produce a development target.
    """

    if results is None:
        return results

    def safe_float(value, default=None):
        try:
            if value in (None, ""):
                return default
            return float(value)
        except Exception:
            return default

    def bool_from_source(value):
        if isinstance(value, str):
            return value.strip().lower() in ("true", "yes", "1", "pass")
        return bool(value)

    def get_first_number(*keys, default=None):
        for key in keys:
            value = safe_float(results.get(key), None)
            if value is not None:
                return value
        return default

    base_hot_wall_temperature = get_first_number(
        "best_full_engine_regen_max_hot_wall_temperature",
        "variable_thermal_max_hot_wall_temperature",
        "recommended_regen_axial_max_hot_wall_temperature",
        "regen_axial_max_hot_wall_temperature",
        "hot_gas_side_wall_temperature",
    )

    coolant_reference_temperature = get_first_number(
        "coolant_inlet_temperature",
        "coolant_bulk_temperature",
        "coolant_mean_temperature",
        default=293.0,
    )

    selected_material_limit = get_first_number(
        "material_max_wall_temperature",
        default=None,
    )

    if base_hot_wall_temperature is None or coolant_reference_temperature is None:
        results["material_aware_combined_status"] = "INSUFFICIENT_THERMAL_DATA"
        results["material_aware_combined_pass"] = 0
        results["material_aware_combined_reason"] = (
            "Cannot run material-aware optimiser because the base hot-wall temperature "
            "or coolant reference temperature is missing."
        )
        return results

    source_mode = str(
        results.get("source_validation_mode")
        or results.get("material_validation_mode")
        or "PLACEHOLDER_MODE"
    ).upper()

    source_validation_ready = (
        source_mode == "SOURCED_VALIDATION_MODE"
        and not bool_from_source(results.get("material_source_is_placeholder"))
    )

    material_candidates = []

    existing_candidates = []

    for key in (
        "material_candidate_screened_candidates",
        "material_candidate_all",
        "material_screened_candidates",
        "material_candidate_passing_candidates",
        "material_candidate_best_candidate",
        "material_candidate_best",
    ):
        value = results.get(key)

        if isinstance(value, list):
            existing_candidates.extend(value)
        elif isinstance(value, dict):
            existing_candidates.append(value)

    if get_material_names is not None and get_material_properties is not None:
        for name in get_material_names():
            material = get_material_properties(name)

            if not isinstance(material, dict):
                continue

            existing_candidates.append(material)

    if selected_material_limit is not None:
        existing_candidates.append({
            "name": results.get("selected_material") or results.get("material_name") or "Selected Material",
            "family": results.get("material_family", "Selected material"),
            "max_wall_temperature": selected_material_limit,
            "thermal_conductivity": results.get("material_thermal_conductivity"),
            "source_quality": results.get("material_source_quality"),
            "notes": results.get("material_notes"),
            "selected_material": True,
        })

    unique_materials = {}

    for material in existing_candidates:
        if not isinstance(material, dict):
            continue

        name = (
            material.get("name")
            or material.get("material")
            or material.get("display_name")
            or "Unknown Material"
        )

        limit = safe_float(
            material.get("max_wall_temperature")
            or material.get("max_recommended_wall_temperature")
            or material.get("material_max_wall_temperature")
            or material.get("temperature_limit"),
            None,
        )

        if limit is None:
            continue

        conductivity = safe_float(
            material.get("thermal_conductivity")
            or material.get("material_thermal_conductivity"),
            None,
        )

        source_quality = (
            material.get("source_quality")
            or material.get("material_source_quality")
            or material.get("source")
            or "UNKNOWN"
        )

        key = str(name).strip().upper()

        unique_materials[key] = {
            "name": name,
            "family": material.get("family", "Unknown"),
            "max_wall_temperature": limit,
            "thermal_conductivity": conductivity,
            "source_quality": source_quality,
            "notes": material.get("notes", ""),
            "selected_material": bool(material.get("selected_material")),
        }

    material_candidates = list(unique_materials.values())

    if not material_candidates:
        results["material_aware_combined_status"] = "FAIL_NO_MATERIAL_CANDIDATES"
        results["material_aware_combined_pass"] = 0
        results["material_aware_combined_reason"] = (
            "No usable material candidates with wall-temperature limits were available."
        )
        return results

    max_film_effectiveness = safe_float(
        results.get("material_aware_max_film_effectiveness"),
        0.45,
    )
    max_heat_load_reduction = safe_float(
        results.get("material_aware_max_heat_load_reduction"),
        0.45,
    )
    max_regen_improvement = safe_float(
        results.get("material_aware_max_regen_improvement_factor"),
        1.8,
    )

    max_film_effectiveness = max(0.0, min(max_film_effectiveness, 0.85))
    max_heat_load_reduction = max(0.0, min(max_heat_load_reduction, 0.85))
    max_regen_improvement = max(1.0, min(max_regen_improvement, 4.0))

    film_values = [
        value for value in
        (0.0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45)
        if value <= max_film_effectiveness + 1.0e-12
    ]

    heat_load_values = [
        value for value in
        (0.0, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45)
        if value <= max_heat_load_reduction + 1.0e-12
    ]

    regen_values = [
        value for value in
        (1.0, 1.05, 1.10, 1.15, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80)
        if value <= max_regen_improvement + 1.0e-12
    ]

    options = []

    for material in material_candidates:
        material_limit = material["max_wall_temperature"]

        for film_effectiveness in film_values:
            for heat_load_reduction in heat_load_values:
                for regen_improvement in regen_values:

                    predicted_hot_wall = (
                        coolant_reference_temperature
                        + (
                            base_hot_wall_temperature
                            - coolant_reference_temperature
                        )
                        * (1.0 - film_effectiveness)
                        * (1.0 - heat_load_reduction)
                        / max(regen_improvement, 1.0e-9)
                    )

                    thermal_margin = material_limit - predicted_hot_wall
                    thermal_pass = thermal_margin >= 0.0

                    film_penalty = film_effectiveness * 250.0
                    heat_penalty = heat_load_reduction * 220.0
                    regen_penalty = (regen_improvement - 1.0) * 160.0

                    material_bonus = 0.0
                    if material.get("thermal_conductivity") is not None:
                        material_bonus = min(material["thermal_conductivity"] * 0.02, 10.0)

                    if thermal_pass:
                        score = (
                            film_penalty
                            + heat_penalty
                            + regen_penalty
                            - min(thermal_margin * 0.02, 30.0)
                            - material_bonus
                        )
                    else:
                        score = (
                            100000.0
                            + abs(thermal_margin) * 100.0
                            + film_penalty
                            + heat_penalty
                            + regen_penalty
                        )

                    options.append({
                        "material_name": material["name"],
                        "material_family": material.get("family"),
                        "material_limit": material_limit,
                        "material_source_quality": material.get("source_quality"),
                        "film_effectiveness": film_effectiveness,
                        "heat_load_reduction": heat_load_reduction,
                        "regen_improvement_factor": regen_improvement,
                        "predicted_hot_wall_temperature": predicted_hot_wall,
                        "thermal_margin": thermal_margin,
                        "thermal_pass": thermal_pass,
                        "score": score,
                    })

    options.sort(key=lambda item: item.get("score", 1.0e99))

    best = options[0] if options else None
    passing_options = [item for item in options if item.get("thermal_pass")]

    if best is None:
        results["material_aware_combined_status"] = "FAIL_NO_OPTIONS"
        results["material_aware_combined_pass"] = 0
        results["material_aware_combined_reason"] = "No combined cooling options were generated."
        return results

    if best.get("thermal_pass") and source_validation_ready:
        status = "SCREENING_PASS_SOURCED_VALIDATION_READY"
        pass_flag = 1
        reason = (
            "Material-aware combined cooling found a thermally passing screening target "
            "and source validation mode allows validation support."
        )
    elif best.get("thermal_pass"):
        status = "DEVELOPMENT_TARGET_SOURCE_BLOCKED"
        pass_flag = 0
        reason = (
            "Material-aware combined cooling found a thermally passing development target, "
            "but source validation is not ready. This must not be treated as final validation."
        )
    else:
        status = "FAIL_NO_PHYSICAL_SCREENING_SOLUTION"
        pass_flag = 0
        reason = (
            "No scanned material/film/heat-load/regen combination produced a thermal pass "
            "within the current screening limits."
        )

    results["material_aware_combined_status"] = status
    results["material_aware_combined_pass"] = pass_flag
    results["material_aware_combined_source_validation_ready"] = 1 if source_validation_ready else 0
    results["material_aware_combined_source_mode"] = source_mode
    results["material_aware_combined_reason"] = reason

    results["material_aware_combined_candidate_count"] = len(options)
    results["material_aware_combined_passing_count"] = len(passing_options)

    results["material_aware_combined_best_material"] = best.get("material_name")
    results["material_aware_combined_best_material_limit"] = best.get("material_limit")
    results["material_aware_combined_best_material_source_quality"] = best.get("material_source_quality")

    results["material_aware_combined_best_film_effectiveness"] = best.get("film_effectiveness")
    results["material_aware_combined_best_heat_load_reduction"] = best.get("heat_load_reduction")
    results["material_aware_combined_best_regen_improvement_factor"] = best.get("regen_improvement_factor")

    results["material_aware_combined_base_hot_wall_temperature"] = base_hot_wall_temperature
    results["material_aware_combined_predicted_hot_wall_temperature"] = best.get("predicted_hot_wall_temperature")
    results["material_aware_combined_thermal_margin"] = best.get("thermal_margin")
    results["material_aware_combined_score"] = best.get("score")

    results["material_aware_combined_best_option"] = best
    results["material_aware_combined_top_options"] = options[:10]

    profile = (
        results.get("variable_geometry_thermal_profile")
        or results.get("recommended_regen_axial_profile")
        or results.get("regen_axial_profile")
        or []
    )

    material_aware_profile = []

    if isinstance(profile, list):
        for station in profile:
            if not isinstance(station, dict):
                continue

            station_twg = safe_float(
                station.get("variable_thermal_hot_wall_temperature")
                or station.get("hot_gas_side_wall_temperature")
                or station.get("Twg")
                or station.get("twg"),
                None,
            )

            if station_twg is None:
                continue

            predicted_station_twg = (
                coolant_reference_temperature
                + (station_twg - coolant_reference_temperature)
                * (1.0 - best.get("film_effectiveness", 0.0))
                * (1.0 - best.get("heat_load_reduction", 0.0))
                / max(best.get("regen_improvement_factor", 1.0), 1.0e-9)
            )

            material_aware_profile.append({
                **station,
                "material_aware_hot_wall_temperature": predicted_station_twg,
                "material_aware_material_limit": best.get("material_limit"),
                "material_aware_thermal_margin": best.get("material_limit") - predicted_station_twg,
                "material_aware_thermal_pass": 1 if predicted_station_twg <= best.get("material_limit") else 0,
                "material_aware_film_effectiveness": best.get("film_effectiveness"),
                "material_aware_heat_load_reduction": best.get("heat_load_reduction"),
                "material_aware_regen_improvement_factor": best.get("regen_improvement_factor"),
            })

    if material_aware_profile:
        failed_stations = [
            station for station in material_aware_profile
            if station.get("material_aware_thermal_pass") != 1
        ]

        max_station_twg = max(
            station.get("material_aware_hot_wall_temperature")
            for station in material_aware_profile
        )

        worst_margin = min(
            station.get("material_aware_thermal_margin")
            for station in material_aware_profile
        )

        results["material_aware_combined_profile"] = material_aware_profile
        results["material_aware_combined_station_count"] = len(material_aware_profile)
        results["material_aware_combined_failed_station_count"] = len(failed_stations)
        results["material_aware_combined_max_hot_wall_temperature"] = max_station_twg
        results["material_aware_combined_worst_margin"] = worst_margin
    else:
        results["material_aware_combined_station_count"] = 0
        results["material_aware_combined_failed_station_count"] = None

    return results

def safe_source_score(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def safe_get_material_properties(material_name, temperature_k=None):
    if get_material_properties is None or not material_name:
        return None

    try:
        return get_material_properties(material_name, temperature_k=temperature_k)
    except TypeError:
        return get_material_properties(material_name)
    except Exception:
        return None


def safe_get_coating_properties(coating_name, temperature_k=None):
    if get_coating_material_properties is None or not coating_name:
        return None

    try:
        return get_coating_material_properties(coating_name, temperature_k=temperature_k)
    except TypeError:
        return get_coating_material_properties(coating_name)
    except Exception:
        return None


def safe_get_bond_coat_properties(bond_name, temperature_k=None):
    if get_bond_coat_properties is None or not bond_name:
        return None

    try:
        return get_bond_coat_properties(bond_name, temperature_k=temperature_k)
    except TypeError:
        return get_bond_coat_properties(bond_name)
    except Exception:
        return None


def apply_material_source_validation_authority(results):
    selected_material_name = (
        results.get("selected_material_name")
        or results.get("selected_material")
        or results.get("wall_material")
        or results.get("material_name")
    )

    material_temperature = (
        results.get("recommended_regen_axial_max_hot_wall_temperature")
        or results.get("film_material_axial_max_hot_wall_temperature")
        or results.get("combined_axial_max_hot_wall_temperature")
        or results.get("hot_gas_side_wall_temperature")
    )

    material = safe_get_material_properties(
        selected_material_name,
        temperature_k=material_temperature
    )

    if material:
        results["material_validation_mode"] = material.get("source_validation_mode", PLACEHOLDER_MODE)
        results["material_source_validation_score"] = material.get("source_validation_score", 0)
        results["material_source_has_citation"] = material.get("source_has_citation", False)
        results["material_source_has_temperature_table"] = material.get("source_has_temperature_table", False)
        results["material_source_is_placeholder"] = material.get("source_is_placeholder", True)
        results["material_source_validation_recommendation"] = material.get(
            "source_validation_recommendation",
            "Material source validation incomplete."
        )
        results["material_property_temperature_k"] = material.get("property_temperature_k")
        results["material_temperature_interpolation_used"] = material.get(
            "temperature_interpolation_used",
            False
        )
    else:
        results["material_validation_mode"] = PLACEHOLDER_MODE
        results["material_source_validation_score"] = 0
        results["material_source_has_citation"] = False
        results["material_source_has_temperature_table"] = False
        results["material_source_is_placeholder"] = True
        results["material_source_validation_recommendation"] = (
            "No selected material source-validation record available."
        )
    results["material_source_validation_mode"] = results.get("material_validation_mode", PLACEHOLDER_MODE)
    return results
def apply_material_and_coating_source_validation_modes(results):
    """
    Standardises material/coating validation modes and conservatively blocks
    final PASS whenever placeholder material/coating data is present.
    """

    if results is None:
        return results

    results = apply_material_source_validation_authority(results)

    material_temperature = (
        results.get("recommended_regen_axial_max_hot_wall_temperature")
        or results.get("film_material_axial_max_hot_wall_temperature")
        or results.get("combined_axial_max_hot_wall_temperature")
        or results.get("hot_gas_side_wall_temperature")
    )

    coating_name = (
        results.get("explicit_coating_liner_material_name")
        or results.get("coating_material")
        or results.get("selected_coating_material")
    )

    bond_name = (
        results.get("bond_coat_best_candidate_name")
        or results.get("bond_coat_candidate")
        or results.get("selected_bond_coat")
    )

    no_active_coating_stack = (
        results.get("active_coating_stack_status") == "NO_ACTIVE_COATING_STACK"
        and results.get("active_coating_source_mode") == "NOT_APPLICABLE"
        and results.get("active_bond_coat_source_mode") == "NOT_APPLICABLE"
    )

    if no_active_coating_stack:
        coating = None
        bond = None
        coating_mode = "NOT_APPLICABLE"
        coating_score = 0.0
    else:
        coating = safe_get_coating_properties(coating_name, temperature_k=material_temperature)
        bond = safe_get_bond_coat_properties(bond_name, temperature_k=material_temperature)
        coating_mode = results.get("coating_stack_data_mode") or PLACEHOLDER_MODE
        coating_score = safe_source_score(results.get("coating_stack_data_mode_score"), 0.0)

    if no_active_coating_stack:
        results["coating_source_has_citation"] = False
        results["coating_source_has_temperature_table"] = False
        results["coating_source_is_placeholder"] = False
        results["coating_source_validation_recommendation"] = (
            "No coating is selected; coating source validation is not applicable."
        )
    elif coating:
        coating_mode = coating.get("source_validation_mode", coating_mode)
        coating_score = max(
            coating_score,
            safe_source_score(coating.get("source_validation_score"), 0.0)
        )

        results["coating_source_has_citation"] = coating.get("source_has_citation", False)
        results["coating_source_has_temperature_table"] = coating.get("source_has_temperature_table", False)
        results["coating_source_is_placeholder"] = coating.get("source_is_placeholder", True)
        results["coating_source_validation_recommendation"] = coating.get(
            "source_validation_recommendation",
            "Coating source validation incomplete."
        )
    else:
        results["coating_source_has_citation"] = False
        results["coating_source_has_temperature_table"] = False
        results["coating_source_is_placeholder"] = True
        results["coating_source_validation_recommendation"] = (
            "No selected coating source-validation record available."
        )

    if no_active_coating_stack:
        bond_mode = "NOT_APPLICABLE"
        bond_score = 0.0
        results["bond_coat_validation_mode"] = "NOT_APPLICABLE"
        results["bond_coat_source_validation_score"] = 0.0
        results["bond_coat_source_has_citation"] = False
        results["bond_coat_source_has_temperature_table"] = False
        results["bond_coat_source_is_placeholder"] = False
        results["bond_coat_source_validation_recommendation"] = (
            "No bond coat is selected; bond-coat source validation is not applicable."
        )
    elif bond:
        bond_mode = bond.get("source_validation_mode", PLACEHOLDER_MODE)
        bond_score = safe_source_score(bond.get("source_validation_score"), 0.0)

        results["bond_coat_validation_mode"] = bond_mode
        results["bond_coat_source_validation_score"] = bond_score
        results["bond_coat_source_has_citation"] = bond.get("source_has_citation", False)
        results["bond_coat_source_has_temperature_table"] = bond.get("source_has_temperature_table", False)
        results["bond_coat_source_is_placeholder"] = bond.get("source_is_placeholder", True)
        results["bond_coat_source_validation_recommendation"] = bond.get(
            "source_validation_recommendation",
            "Bond coat source validation incomplete."
        )
    else:
        bond_mode = PLACEHOLDER_MODE
        bond_score = 0.0
        results["bond_coat_validation_mode"] = PLACEHOLDER_MODE
        results["bond_coat_source_validation_score"] = 0.0
        results["bond_coat_source_has_citation"] = False
        results["bond_coat_source_has_temperature_table"] = False
        results["bond_coat_source_is_placeholder"] = True
        results["bond_coat_source_validation_recommendation"] = (
            "No selected bond-coat source-validation record available."
        )

    if no_active_coating_stack:
        combined_coating_mode = "NOT_APPLICABLE"
    elif coating_mode == PLACEHOLDER_MODE or bond_mode == PLACEHOLDER_MODE:
        combined_coating_mode = PLACEHOLDER_MODE
    elif coating_mode == SOURCED_VALIDATION_MODE and bond_mode == SOURCED_VALIDATION_MODE:
        combined_coating_mode = SOURCED_VALIDATION_MODE
    else:
        combined_coating_mode = PARTIAL_SOURCE_MODE

    results["coating_validation_mode"] = combined_coating_mode
    results["coating_source_validation_score"] = min(
        100.0,
        round((coating_score + bond_score) / 2.0, 2)
    )

    material_mode = results.get("material_validation_mode", PLACEHOLDER_MODE)

    if combined_coating_mode == "NOT_APPLICABLE":
        if material_mode == PLACEHOLDER_MODE:
            source_mode = PLACEHOLDER_MODE
        elif material_mode == SOURCED_VALIDATION_MODE:
            source_mode = SOURCED_VALIDATION_MODE
        else:
            source_mode = PARTIAL_SOURCE_MODE
    elif material_mode == PLACEHOLDER_MODE or combined_coating_mode == PLACEHOLDER_MODE:
        source_mode = PLACEHOLDER_MODE
    elif material_mode == SOURCED_VALIDATION_MODE and combined_coating_mode == SOURCED_VALIDATION_MODE:
        source_mode = SOURCED_VALIDATION_MODE
    else:
        source_mode = PARTIAL_SOURCE_MODE

    results["source_validation_mode"] = source_mode

    if source_mode == PLACEHOLDER_MODE:
        results["source_validation_conservative_gate"] = "BLOCK_PASS_PLACEHOLDER_DATA"
        results["regen_source_validation_status"] = "DEVELOPMENT_ROUTE_ONLY"
        results["regen_source_validation_recommendation"] = (
            "Placeholder material/coating data is present. Final engineering PASS is blocked."
        )
    elif source_mode == PARTIAL_SOURCE_MODE:
        results["source_validation_conservative_gate"] = "ALLOW_LIMITED_REVIEW"
        results["regen_source_validation_status"] = "PARTIAL_SOURCE_MODE"
        results["regen_source_validation_recommendation"] = (
            "Some sourced data exists, but validation evidence is incomplete."
        )
    else:
        results["source_validation_conservative_gate"] = "ALLOW_SOURCED_VALIDATION_REVIEW"
        results["regen_source_validation_status"] = "SOURCED_VALIDATION_MODE"
        results["regen_source_validation_recommendation"] = (
            "Sourced material/coating data is available for validation review."
        )

    pass_like_statuses = {
        "PASS",
        "PASS_WITH_MARGIN",
        "PASS_LOW_MARGIN",
        "PLAUSIBLE",
    }

    current_final = str(results.get("final_regen_design_verdict", "")).upper()
    current_overall = str(results.get("regen_overall_status", "")).upper()

    if source_mode == PLACEHOLDER_MODE:
        if current_final in pass_like_statuses:
            results["final_regen_design_verdict_without_source_gate"] = current_final
            results["final_regen_design_verdict"] = "DEVELOPMENT_ROUTE_ONLY_SOURCE_BLOCKED"

        if current_overall in pass_like_statuses:
            results["regen_overall_status_without_source_gate"] = current_overall
            results["regen_overall_status"] = "DEVELOPMENT_ROUTE_ONLY_SOURCE_BLOCKED"

    return results

def safe_percent_error(predicted, reference):
    try:
        predicted = float(predicted)
        reference = float(reference)

        if abs(reference) < 1.0e-12:
            return None

        return abs(predicted - reference) / abs(reference) * 100.0
    except Exception:
        return None


def compare_reference_quantity(results, reference, result_keys, reference_key, output_key):
    reference_value = reference.get(reference_key)

    if reference_value is None:
        results[output_key] = None
        return None

    predicted_value = None

    for key in result_keys:
        if results.get(key) not in (None, ""):
            predicted_value = results.get(key)
            break

    error = safe_percent_error(predicted_value, reference_value)
    results[output_key] = error

    return error

def evaluate_reference_comparison_run_gate(results, reference):
    comparison_pairs = [
        ("recommended_channel_width", "channel_width_m"),
        ("recommended_channel_height", "channel_height_m"),
        ("recommended_channel_count", "channel_count"),
        ("recommended_hot_gas_wall_thickness", "wall_thickness_m"),
        ("recommended_coolant_velocity", "coolant_velocity_m_s"),
        ("regen_total_pressure_drop", "pressure_drop_pa"),
        ("coolant_temperature_rise", "coolant_temperature_rise_k"),
    ]

    missing_leaf = []
    missing_reference = []

    for leaf_key, reference_key in comparison_pairs:
        if results.get(leaf_key) in (None, ""):
            missing_leaf.append(leaf_key)

        if reference.get(reference_key) in (None, ""):
            missing_reference.append(reference_key)

    if missing_reference and missing_leaf:
        status = "REFERENCE_AND_LEAF_DATA_MISSING"
        ready = False
    elif missing_reference:
        status = "REFERENCE_DATA_MISSING"
        ready = False
    elif missing_leaf:
        status = "LEAF_DATA_MISSING"
        ready = False
    else:
        status = "READY_TO_COMPARE"
        ready = True

    return {
        "status": status,
        "ready": ready,
        "missing_leaf": missing_leaf,
        "missing_reference": missing_reference,
    }

def build_regen_optimisation_proof(results):
    """
    Builds a trust/audit summary proving whether LEAF has searched the available
    regen design space before declaring FAIL.

    This does not change pass/fail results.
    It explains why the current best result is accepted or rejected.
    """

    if results is None:
        return results

    def safe_float(value, default=None):
        try:
            if value in (None, ""):
                return default
            return float(value)
        except Exception:
            return default

    manual_geometry_valid = safe_float(results.get("channel_geometry_valid"), 0.0) == 1.0
    recommended_fit_count = safe_float(results.get("full_engine_regen_failed_fit_count"), None)
    recommended_geometry_valid = recommended_fit_count == 0

    hard_re_fail_count = safe_float(results.get("full_engine_regen_failed_reynolds_count"), None)
    below_target_re_count = safe_float(results.get("full_engine_regen_below_target_reynolds_count"), None)
    thermal_fail_count = safe_float(results.get("full_engine_regen_failed_thermal_count"), None)

    pressure_drop_pass = safe_float(results.get("full_engine_regen_pressure_drop_pass"), 0.0) == 1.0

    best_status = str(results.get("best_full_engine_regen_status", "UNKNOWN"))
    best_design = str(results.get("best_full_engine_regen_design", "UNKNOWN"))

    explicit_liner_temperature = safe_float(
        results.get("explicit_coating_liner_hot_wall_temperature"),
        None
    )
    explicit_surface_temperature = safe_float(
        results.get("explicit_coating_surface_temperature"),
        None
    )
    explicit_coating_status = str(
        results.get("explicit_coating_preview_status", "NOT_RUN")
    )

    coating_physically_plausible = True
    coating_issue = "No coating sanity issue detected."

    if explicit_coating_status not in ("NO_COATING_SELECTED", "NOT_RUN"):
        if explicit_liner_temperature is None or explicit_surface_temperature is None:
            coating_physically_plausible = False
            coating_issue = "Coating preview is missing liner or surface temperature."
        elif explicit_liner_temperature < 200.0:
            coating_physically_plausible = False
            coating_issue = (
                "Coating preview predicted an unrealistically low liner temperature. "
                "The coating thermal-resistance model is being over-applied and must be treated as diagnostic only."
            )
        elif explicit_liner_temperature > explicit_surface_temperature:
            coating_physically_plausible = False
            coating_issue = (
                "Coating preview predicted liner temperature above surface temperature under positive heat flux."
            )

    proof_lines = []

    proof_lines.append(
        f"Manual geometry valid: {manual_geometry_valid}"
    )
    proof_lines.append(
        f"Recommended/full-engine fit failures: {recommended_fit_count}"
    )
    proof_lines.append(
        f"Hard Reynolds failures: {hard_re_fail_count}"
    )
    proof_lines.append(
        f"Below-target Reynolds warnings: {below_target_re_count}"
    )
    proof_lines.append(
        f"Pressure drop pass: {pressure_drop_pass}"
    )
    proof_lines.append(
        f"Thermal failed stations: {thermal_fail_count}"
    )
    proof_lines.append(
        f"Best available design: {best_design}"
    )
    proof_lines.append(
        f"Best available status: {best_status}"
    )
    proof_lines.append(
        f"Coating physical sanity: {coating_physically_plausible}"
    )
    proof_lines.append(
        f"Coating sanity note: {coating_issue}"
    )

    if (
        recommended_geometry_valid
        and hard_re_fail_count == 0
        and pressure_drop_pass
        and thermal_fail_count is not None
        and thermal_fail_count > 0
    ):
        status = "OPTIMISED_FAIL_THERMAL_LIMITED"
        reason = (
            "LEAF found a physically fitting full-engine geometry with no hard Reynolds failures "
            "and acceptable pressure drop, but all available full-engine thermal candidates still fail."
        )
    elif not recommended_geometry_valid:
        status = "NOT_OPTIMISED_GEOMETRY_BLOCKED"
        reason = "LEAF has not found a full-engine geometry with zero fit failures."
    elif hard_re_fail_count is not None and hard_re_fail_count > 0:
        status = "NOT_OPTIMISED_HARD_REYNOLDS_BLOCKED"
        reason = "LEAF still has hard Reynolds failures below the turbulent minimum."
    elif not pressure_drop_pass:
        status = "NOT_OPTIMISED_PRESSURE_DROP_BLOCKED"
        reason = "LEAF still fails the pressure-drop gate."
    else:
        status = "OPTIMISATION_STATE_UNCLEAR"
        reason = "LEAF could not clearly classify the current optimisation state."

    if not coating_physically_plausible:
        status = status + "_COATING_PREVIEW_DIAGNOSTIC_ONLY"

    results["regen_optimisation_proof_status"] = status
    results["regen_optimisation_proof_reason"] = reason
    results["regen_optimisation_proof_lines"] = proof_lines
    results["regen_optimisation_manual_geometry_valid"] = 1 if manual_geometry_valid else 0
    results["regen_optimisation_recommended_geometry_valid"] = 1 if recommended_geometry_valid else 0
    results["regen_optimisation_pressure_drop_pass"] = 1 if pressure_drop_pass else 0
    results["regen_optimisation_coating_preview_physical"] = 1 if coating_physically_plausible else 0
    results["regen_optimisation_coating_sanity_note"] = coating_issue

    return results

def build_reference_comparison_evidence(results, reference):
    comparison_rows = [
        {
            "label": "Channel width",
            "leaf_keys": ["recommended_channel_width", "recommended_coolant_channel_width"],
            "reference_key": "channel_width_m",
            "error_key": "reference_engine_channel_width_error_percent",
        },
        {
            "label": "Channel height",
            "leaf_keys": ["recommended_channel_height", "recommended_coolant_channel_height"],
            "reference_key": "channel_height_m",
            "error_key": "reference_engine_channel_height_error_percent",
        },
        {
            "label": "Channel count",
            "leaf_keys": ["recommended_channel_count", "recommended_number_of_coolant_channels"],
            "reference_key": "channel_count",
            "error_key": "reference_engine_channel_count_error_percent",
        },
        {
            "label": "Wall thickness",
            "leaf_keys": ["recommended_hot_gas_wall_thickness", "hot_gas_wall_thickness"],
            "reference_key": "wall_thickness_m",
            "error_key": "reference_engine_wall_thickness_error_percent",
        },
        {
            "label": "Coolant velocity",
            "leaf_keys": ["recommended_coolant_velocity", "coolant_velocity"],
            "reference_key": "coolant_velocity_m_s",
            "error_key": "reference_engine_coolant_velocity_error_percent",
        },
        {
            "label": "Pressure drop",
            "leaf_keys": ["regen_total_pressure_drop", "total_pressure_drop_so_far"],
            "reference_key": "pressure_drop_pa",
            "error_key": "reference_engine_pressure_drop_error_percent",
        },
        {
            "label": "Coolant temperature rise",
            "leaf_keys": ["coolant_temperature_rise", "regen_coolant_temperature_rise"],
            "reference_key": "coolant_temperature_rise_k",
            "error_key": "reference_engine_coolant_temperature_rise_error_percent",
        },
    ]

    evidence = []

    for row in comparison_rows:
        leaf_value = None
        leaf_key_used = None

        for leaf_key in row["leaf_keys"]:
            if results.get(leaf_key) not in (None, ""):
                leaf_value = results.get(leaf_key)
                leaf_key_used = leaf_key
                break

        reference_value = reference.get(row["reference_key"])

        leaf_present = leaf_value not in (None, "")
        reference_present = reference_value not in (None, "")

        error_percent = None

        if leaf_present and reference_present:
            error_percent = safe_percent_error(leaf_value, reference_value)

        evidence.append({
            "label": row["label"],
            "leaf_key": leaf_key_used or row["leaf_keys"][0],
            "reference_key": row["reference_key"],
            "leaf_value": leaf_value,
            "reference_value": reference_value,
            "leaf_present": leaf_present,
            "reference_present": reference_present,
            "ready": bool(leaf_present and reference_present),
            "error_percent": error_percent,
            "error_key": row["error_key"],
        })

    return evidence

def evaluate_reference_comparison_quality(evidence):
    if not isinstance(evidence, list) or not evidence:
        return {
            "status": "NOT_READY",
            "ready_count": 0,
            "total_count": 0,
            "average_error_percent": None,
            "agreement_percent": None,
            "best_field": "N/A",
            "worst_field": "N/A",
            "recommendation": "No reference comparison evidence is available.",
        }

    ready_rows = [
        row for row in evidence
        if row.get("ready") and row.get("error_percent") is not None
    ]

    total_count = len(evidence)
    ready_count = len(ready_rows)

    if ready_count == 0:
        return {
            "status": "NOT_READY",
            "ready_count": 0,
            "total_count": total_count,
            "average_error_percent": None,
            "agreement_percent": None,
            "best_field": "N/A",
            "worst_field": "N/A",
            "recommendation": "No comparison fields have both LEAF and reference values.",
        }

    errors = []

    for row in ready_rows:
        try:
            errors.append((row.get("label", "Unknown"), float(row.get("error_percent"))))
        except Exception:
            pass

    if not errors:
        return {
            "status": "NOT_READY",
            "ready_count": ready_count,
            "total_count": total_count,
            "average_error_percent": None,
            "agreement_percent": None,
            "best_field": "N/A",
            "worst_field": "N/A",
            "recommendation": "Comparison fields are marked ready but error values are unavailable.",
        }

    average_error = sum(error for _, error in errors) / len(errors)
    agreement = max(0.0, 100.0 - average_error)

    best_label, best_error = min(errors, key=lambda item: item[1])
    worst_label, worst_error = max(errors, key=lambda item: item[1])

    coverage = ready_count / max(total_count, 1)

    if coverage < 0.5:
        status = "PARTIAL_DATA_ONLY"
        recommendation = "Too few comparison fields are populated for strong validation."
    elif average_error <= 10.0:
        status = "EXCELLENT_MATCH"
        recommendation = "Reference comparison agrees strongly at current populated fields."
    elif average_error <= 25.0:
        status = "GOOD_MATCH"
        recommendation = "Reference comparison is plausible; review worst-error fields."
    elif average_error <= 50.0:
        status = "PARTIAL_MATCH"
        recommendation = "Reference comparison is weak; check assumptions, source data, and scaling."
    else:
        status = "POOR_MATCH"
        recommendation = "Reference comparison does not agree. Investigate solver scaling or source data."

    return {
        "status": status,
        "ready_count": ready_count,
        "total_count": total_count,
        "average_error_percent": average_error,
        "agreement_percent": agreement,
        "best_field": f"{best_label} ({best_error:.2f}%)",
        "worst_field": f"{worst_label} ({worst_error:.2f}%)",
        "recommendation": recommendation,
    }

def determine_reference_validation_verdict(results):
    status = str(results.get("reference_comparison_run_gate_status", "NOT_SELECTED")).upper()
    quality = str(results.get("reference_comparison_quality_status", "NOT_READY")).upper()
    source_status = str(results.get("reference_engine_source_status", "UNKNOWN")).upper()

    ledger_status = str(
        results.get("reference_source_ledger_status", "NO_FILLED_VALUES")
    ).upper()

    quality_band = str(
        results.get("reference_data_quality_band", "PLACEHOLDER")
    ).upper()

    ready_count = results.get("reference_comparison_ready_field_count") or 0
    total_count = results.get("reference_comparison_total_field_count") or 0

    try:
        ready_count = int(ready_count)
        total_count = int(total_count)
    except Exception:
        ready_count = 0
        total_count = 0

    if status == "NOT_SELECTED":
        verdict = "REFERENCE_NOT_SELECTED"
        recommendation = "Select a reference engine before running reference validation."

    elif "REFERENCE_DATA_MISSING" in status:
        verdict = "REFERENCE_DATA_REQUIRED"
        recommendation = "Add sourced reference-engine comparison values before validation."

    elif "LEAF_DATA_MISSING" in status:
        verdict = "LEAF_DATA_REQUIRED"
        recommendation = "Run LEAF regen calculations so predicted comparison fields exist."

    elif ready_count < max(3, total_count // 2):
        verdict = "REFERENCE_PARTIAL_ONLY"
        recommendation = "Too few comparison fields are populated for a meaningful validation verdict."

    elif quality in ("EXCELLENT_MATCH", "GOOD_MATCH"):
        verdict = "REFERENCE_ORDER_OF_MAGNITUDE_PASS"
        recommendation = "Reference comparison is plausible at order-of-magnitude level."

    elif quality in ("PARTIAL_MATCH", "PARTIAL_DATA_ONLY"):
        verdict = "REFERENCE_ORDER_OF_MAGNITUDE_WARN"
        recommendation = "Reference comparison is incomplete or weak; review worst-field errors."

    elif quality == "POOR_MATCH":
        verdict = "REFERENCE_ORDER_OF_MAGNITUDE_FAIL"
        recommendation = "Reference comparison mismatch is large. Review source data and solver assumptions."

    else:
        verdict = "REFERENCE_VALIDATION_INCOMPLETE"
        recommendation = "Reference validation could not produce a final verdict."

    if "PLACEHOLDER" in source_status and verdict.endswith("PASS"):
        verdict = "REFERENCE_SOURCE_BLOCKED"
        recommendation = "Reference source status is placeholder; PASS is blocked."

    if ledger_status not in ("LEDGER_COMPLETE", "NO_FILLED_VALUES") and verdict.endswith("PASS"):
        verdict = "REFERENCE_LEDGER_BLOCKED"
        recommendation = (
            "Reference comparison has values, but not all filled values have source-ledger notes."
        )

    if quality_band in ("PLACEHOLDER", "LOW_CONFIDENCE_PUBLIC") and verdict.endswith("PASS"):
        verdict = "REFERENCE_QUALITY_BLOCKED"
        recommendation = (
            "Reference comparison appears numerically acceptable, but data quality is too low for PASS."
        )

    results["reference_validation_verdict"] = verdict
    results["reference_validation_recommendation"] = recommendation

    return results

def validate_against_reference_engine(results):
    if results is None:
        return results

    reference_name = (
        results.get("reference_engine_name")
        or results.get("selected_reference_engine")
        or results.get("validation_reference_engine")
    )

    if not reference_name:
        results["regen_scalability_validation_status"] = "NOT_SELECTED"
        return results

    if get_reference_engine is None:
        results["regen_scalability_validation_status"] = "REFERENCE_DATABASE_MISSING"
        return results

    reference = get_reference_engine(reference_name)

    if not reference:
        results["regen_scalability_validation_status"] = "REFERENCE_ENGINE_NOT_FOUND"
        results["reference_engine_name"] = reference_name
        return results

    results["reference_engine_name"] = reference_name
    results["reference_engine_display_name"] = reference.get("display_name", reference_name)
    results["reference_engine_source_status"] = reference.get("source_status", "UNKNOWN")

    if evaluate_reference_source_ledger_coverage is not None:
        ledger = evaluate_reference_source_ledger_coverage(reference)
    else:
        ledger = {
            "status": "LEDGER_HELPER_MISSING",
            "covered_count": 0,
            "filled_count": 0,
            "coverage_percent": 0.0,
            "missing_ledger_notes": [],
            "recommendation": "Ledger coverage helper unavailable.",
        }

    results["reference_source_ledger_status"] = ledger.get("status")
    results["reference_source_ledger_covered_count"] = ledger.get("covered_count")
    results["reference_source_ledger_filled_count"] = ledger.get("filled_count")
    results["reference_source_ledger_coverage_percent"] = ledger.get("coverage_percent")
    results["reference_source_ledger_missing_notes"] = ", ".join(
        ledger.get("missing_ledger_notes", [])
    ) or "None"
    results["reference_source_ledger_recommendation"] = ledger.get("recommendation")

    if evaluate_reference_data_quality is not None:
        data_quality = evaluate_reference_data_quality(reference)
    else:
        data_quality = {
            "band": "PLACEHOLDER",
            "score": 0,
            "status": "QUALITY_HELPER_MISSING",
            "recommendation": "Reference data-quality helper unavailable.",
        }

    results["reference_data_quality_band"] = data_quality.get("band")
    results["reference_data_quality_score"] = data_quality.get("score")
    results["reference_data_quality_status"] = data_quality.get("status")
    results["reference_data_quality_recommendation"] = data_quality.get("recommendation")

    run_gate = evaluate_reference_comparison_run_gate(results, reference)

    results["reference_comparison_run_gate_status"] = run_gate["status"]
    results["reference_comparison_ready"] = run_gate["ready"]
    results["reference_comparison_missing_leaf_fields"] = ", ".join(run_gate["missing_leaf"]) or "None"
    results["reference_comparison_missing_reference_fields"] = ", ".join(run_gate["missing_reference"]) or "None"

    evidence = build_reference_comparison_evidence(results, reference)
    results["reference_comparison_evidence"] = evidence

    quality = evaluate_reference_comparison_quality(evidence)

    results["reference_comparison_quality_status"] = quality["status"]
    results["reference_comparison_average_error_percent"] = quality["average_error_percent"]
    results["reference_comparison_agreement_percent"] = quality["agreement_percent"]
    results["reference_comparison_best_field"] = quality["best_field"]
    results["reference_comparison_worst_field"] = quality["worst_field"]
    results["reference_comparison_quality_recommendation"] = quality["recommendation"]

    ready_count = len([row for row in evidence if row.get("ready")])
    results["reference_comparison_ready_field_count"] = ready_count
    results["reference_comparison_total_field_count"] = len(evidence)

    results = determine_reference_validation_verdict(results)

    reference_geometry = reference.get("reference_geometry", {})

    if isinstance(reference_geometry, dict):
        results["reference_engine_throat_area_m2"] = reference_geometry.get("throat_area_m2")
        results["reference_engine_exit_area_m2"] = reference_geometry.get("exit_area_m2")
        results["reference_engine_throat_radius_m"] = reference_geometry.get("throat_radius_m")
        results["reference_engine_exit_radius_m"] = reference_geometry.get("exit_radius_m")
        results["reference_engine_nozzle_length_m"] = reference_geometry.get("nozzle_length_m")

    if not run_gate["ready"]:
        results["regen_scalability_validation_status"] = run_gate["status"]
        results["reference_engine_overall_agreement_percent"] = None
        results["reference_engine_mean_error_percent"] = None
        results["reference_engine_comparison_count"] = 0
        results["reference_engine_validation_note"] = (
            "Reference comparison cannot run until both LEAF prediction values and sourced reference values exist."
        )
        results = determine_reference_validation_verdict(results)
        return results

    errors = []

    comparisons = [
        (
            ["recommended_channel_width", "recommended_coolant_channel_width"],
            "channel_width_m",
            "reference_engine_channel_width_error_percent",
        ),
        (
            ["recommended_channel_height", "recommended_coolant_channel_height"],
            "channel_height_m",
            "reference_engine_channel_height_error_percent",
        ),
        (
            ["recommended_channel_count", "recommended_number_of_coolant_channels"],
            "channel_count",
            "reference_engine_channel_count_error_percent",
        ),
        (
            ["recommended_hot_gas_wall_thickness", "hot_gas_wall_thickness"],
            "wall_thickness_m",
            "reference_engine_wall_thickness_error_percent",
        ),
        (
            ["recommended_coolant_velocity", "coolant_velocity"],
            "coolant_velocity_m_s",
            "reference_engine_coolant_velocity_error_percent",
        ),
        (
            ["regen_total_pressure_drop", "total_pressure_drop_so_far"],
            "pressure_drop_pa",
            "reference_engine_pressure_drop_error_percent",
        ),
        (
            ["coolant_temperature_rise", "regen_coolant_temperature_rise"],
            "coolant_temperature_rise_k",
            "reference_engine_coolant_temperature_rise_error_percent",
        ),
    ]

    for result_keys, reference_key, output_key in comparisons:
        error = compare_reference_quantity(
            results,
            reference,
            result_keys,
            reference_key,
            output_key,
        )

        if error is not None:
            errors.append(error)

    if not errors:
        results["regen_scalability_validation_status"] = "REFERENCE_DATA_REQUIRED"
        results["reference_engine_overall_agreement_percent"] = None
        results["reference_engine_validation_note"] = (
            "Reference engine exists, but no sourced comparison values have been added yet."
        )
        return results

    mean_error = sum(errors) / len(errors)
    agreement = max(0.0, 100.0 - mean_error)

    results["reference_engine_mean_error_percent"] = mean_error
    results["reference_engine_overall_agreement_percent"] = agreement
    results["reference_engine_comparison_count"] = len(errors)

    if agreement >= 80.0:
        status = "PASS_ORDER_OF_MAGNITUDE"
    elif agreement >= 60.0:
        status = "PARTIAL_AGREEMENT"
    else:
        status = "SCALING_MISMATCH"

    results["regen_scalability_validation_status"] = status
    results["reference_engine_validation_note"] = (
        "Reference comparison is order-of-magnitude only unless complete sourced geometry data is available."
    )

    return results

def evaluate_cooling_strategy_trade_study(results):
    """
    Compares practical cooling recovery paths after regen-only failure.

    This does not replace detailed thermal simulation.
    It ranks what type of design change is most plausible:
    - regen only
    - regen + film
    - material upgrade
    - reduced heat load
    - combined solution
    """

    if results is None:
        return results

    options = []
    recommendations = []

    max_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")
    material_limit = results.get("material_max_wall_temperature")
    required_material_limit = results.get("regen_required_material_temperature_limit")
    required_film_effectiveness = results.get("film_required_effectiveness")
    film_fraction = results.get("film_estimated_fraction_of_fuel_flow")
    required_cooling_factor = results.get("regen_required_cooling_improvement_factor")
    required_available_fraction = results.get("regen_required_coolant_available_flow_fraction")
    pressure_ratio = results.get("regen_feasibility_pressure_drop_ratio")

    if max_twg is None or material_limit is None:
        results["cooling_trade_study_status"] = "INSUFFICIENT_DATA"
        return results

    # -------------------------------------------------
    # Option 1: Regen only
    # -------------------------------------------------

    if max_twg <= material_limit:
        options.append({
            "name": "Regen only",
            "status": "PASS",
            "score": 100,
            "reason": "Recommended regen geometry is below material temperature limit."
        })
    else:
        options.append({
            "name": "Regen only",
            "status": "FAIL",
            "score": 0,
            "reason": "Recommended regen wall temperature exceeds material limit."
        })

    # -------------------------------------------------
    # Option 2: Material upgrade
    # -------------------------------------------------

    material_score = 0
    material_status = "FAIL"
    material_reason = "Material upgrade data unavailable."

    if required_material_limit is not None and material_limit is not None and material_limit > 0:
        material_factor = required_material_limit / material_limit
        results["cooling_trade_required_material_factor"] = material_factor

        if material_factor <= 1.1:
            material_score = 90
            material_status = "PASS"
            material_reason = "Only a small material temperature capability increase is required."
        elif material_factor <= 1.5:
            material_score = 65
            material_status = "MARGINAL"
            material_reason = "A higher-temperature material may plausibly help."
        else:
            material_score = 20
            material_status = "FAIL"
            material_reason = "Required material capability is far above the selected material limit."

    options.append({
        "name": "Material upgrade",
        "status": material_status,
        "score": material_score,
        "reason": material_reason
    })

    # -------------------------------------------------
    # Option 3: Film cooling
    # -------------------------------------------------

    film_score = 0
    film_status = "FAIL"
    film_reason = "Film cooling data unavailable."

    if required_film_effectiveness is not None:
        if required_film_effectiveness <= 0.20:
            film_score = 85
            film_status = "PASS"
            film_reason = "Light film cooling may be sufficient."
        elif required_film_effectiveness <= 0.40:
            film_score = 60
            film_status = "MARGINAL"
            film_reason = "Moderate film cooling required; performance loss likely."
        elif required_film_effectiveness <= 0.60:
            film_score = 35
            film_status = "SEVERE"
            film_reason = "Heavy film cooling required."
        else:
            film_score = 15
            film_status = "FAIL"
            film_reason = "Film cooling requirement is extremely severe."

    if film_fraction is not None and film_fraction > 0.25:
        film_score = min(film_score, 25)
        film_reason += " Estimated film flow consumes a large fraction of fuel flow."

    options.append({
        "name": "Film cooling",
        "status": film_status,
        "score": film_score,
        "reason": film_reason
    })

    # -------------------------------------------------
    # Option 4: Reduced chamber heat load
    # -------------------------------------------------

    heat_load_score = 0
    heat_load_status = "FAIL"
    heat_load_reason = "Cooling improvement factor unavailable."

    if required_cooling_factor is not None and required_cooling_factor > 0:
        required_heat_load_fraction = 1.0 / required_cooling_factor
        heat_load_reduction_fraction = 1.0 - required_heat_load_fraction

        results["cooling_trade_required_heat_load_fraction"] = required_heat_load_fraction
        results["cooling_trade_required_heat_load_reduction_fraction"] = heat_load_reduction_fraction

        if heat_load_reduction_fraction <= 0.15:
            heat_load_score = 80
            heat_load_status = "PASS"
            heat_load_reason = "Only a small chamber heat-load reduction is required."
        elif heat_load_reduction_fraction <= 0.35:
            heat_load_score = 55
            heat_load_status = "MARGINAL"
            heat_load_reason = "Moderate chamber heat-load reduction required."
        else:
            heat_load_score = 20
            heat_load_status = "FAIL"
            heat_load_reason = "Required chamber heat-load reduction is very large."

    options.append({
        "name": "Reduced chamber heat load",
        "status": heat_load_status,
        "score": heat_load_score,
        "reason": heat_load_reason
    })

    # -------------------------------------------------
    # Option 5: Combined strategy
    # -------------------------------------------------

    combined_score = max(material_score, film_score, heat_load_score)

    if (
        required_available_fraction is not None
        and required_available_fraction > 1.0
        and required_film_effectiveness is not None
        and required_film_effectiveness > 0.4
    ):
        combined_status = "REQUIRED"
        combined_score = max(combined_score, 50)
        combined_reason = (
            "No single simple change appears sufficient; combine material upgrade, "
            "film cooling, variable channels, or reduced chamber heat load."
        )
    else:
        combined_status = "CANDIDATE"
        combined_reason = "Combined strategy may improve design margin."

    options.append({
        "name": "Combined cooling strategy",
        "status": combined_status,
        "score": combined_score,
        "reason": combined_reason
    })

    # -------------------------------------------------
    # Pressure-drop note
    # -------------------------------------------------

    if pressure_ratio is not None and pressure_ratio < 0.2:
        recommendations.append(
            "Pressure-drop budget has margin; more aggressive channel optimisation may be possible."
        )

    if film_fraction is not None and film_fraction > 0.25:
        recommendations.append(
            "Film cooling demand is high enough that injector and performance penalties must be modelled."
        )

    if required_available_fraction is not None and required_available_fraction > 1.0:
        recommendations.append(
            "Regen-only cooling is rejected because required coolant flow exceeds available propellant coolant flow."
        )

    recommendations.append(
        "Next development should add material-aware and film-aware optimisation rather than further geometry-only optimisation."
    )

    # Best option = highest score
    best_option = max(options, key=lambda item: item.get("score", 0))

    results["cooling_trade_study_status"] = "COMPLETE"
    results["cooling_trade_options"] = options
    results["cooling_trade_selected_option"] = best_option.get("name")
    results["cooling_trade_selected_status"] = best_option.get("status")
    results["cooling_trade_selected_reason"] = best_option.get("reason")
    results["cooling_trade_recommendations"] = recommendations

    return results

def allocate_combined_cooling_targets(results):
    """
    Allocates a realistic combined cooling recovery path.

    Instead of asking one method to solve the full thermal failure, this splits
    the required improvement across:
    - material capability
    - film cooling
    - heat-load reduction
    - further channel/regen improvement
    """

    if results is None:
        return results

    required_cooling_factor = results.get("regen_required_cooling_improvement_factor")
    required_material_factor = results.get("cooling_trade_required_material_factor")
    required_heat_load_reduction = results.get("cooling_trade_required_heat_load_reduction_fraction")
    required_film_effectiveness = results.get("film_required_effectiveness")

    if required_cooling_factor is None or required_cooling_factor <= 1.0:
        results["combined_cooling_allocation_status"] = "NOT_REQUIRED"
        results["combined_cooling_allocation_summary"] = (
            "Combined cooling allocation is not required because regen cooling is already feasible."
        )
        return results

    # Scalable default design caps.
    # These are not hard physical limits; they represent first-pass practical
    # design targets for an engine-level trade study.
    max_material_factor = results.get("combined_max_material_factor", 1.6)
    max_film_effectiveness = results.get("combined_max_film_effectiveness", 0.35)
    max_heat_load_reduction = results.get("combined_max_heat_load_reduction_fraction", 0.25)
    max_regen_improvement = results.get("combined_max_regen_improvement_factor", 1.4)

    # Convert each method into a cooling contribution factor.
    material_contribution = min(
        max_material_factor,
        required_material_factor if required_material_factor is not None else max_material_factor
    )

    film_contribution = 1.0 / max(1.0 - min(max_film_effectiveness, 0.95), 1e-9)

    heat_load_contribution = 1.0 / max(1.0 - min(max_heat_load_reduction, 0.95), 1e-9)

    regen_contribution = max_regen_improvement

    combined_factor = (
        material_contribution
        * film_contribution
        * heat_load_contribution
        * regen_contribution
    )

    remaining_factor = required_cooling_factor / max(combined_factor, 1e-9)

    results["combined_material_factor_target"] = material_contribution
    results["combined_film_effectiveness_target"] = max_film_effectiveness
    results["combined_heat_load_reduction_target"] = max_heat_load_reduction
    results["combined_regen_improvement_factor_target"] = regen_contribution
    results["combined_total_cooling_factor"] = combined_factor
    results["combined_remaining_cooling_factor"] = remaining_factor

    if combined_factor >= required_cooling_factor:
        status = "PLAUSIBLE"
        summary = (
            "A combined cooling strategy may plausibly close the thermal gap "
            "within the selected first-pass design caps."
        )
    else:
        status = "INSUFFICIENT"
        summary = (
            "Even the combined first-pass strategy does not fully close the thermal gap. "
            "The engine requires deeper redesign."
        )

    recommendations = []

    recommendations.append(
        f"Target material capability factor: {material_contribution:.3g}x current material limit."
    )
    recommendations.append(
        f"Target film effectiveness: {max_film_effectiveness:.3g}."
    )
    recommendations.append(
        f"Target chamber/nozzle heat-load reduction: {max_heat_load_reduction:.3g}."
    )
    recommendations.append(
        f"Target further regen/channel improvement: {regen_contribution:.3g}x."
    )

    if status == "INSUFFICIENT":
        recommendations.append(
            "Reduce chamber pressure/temperature, increase engine scale, change propellant/cooling architecture, or use a higher-performance material system."
        )

    results["combined_cooling_allocation_status"] = status
    results["combined_cooling_allocation_summary"] = summary
    results["combined_cooling_allocation_recommendations"] = recommendations

    return results

def predict_combined_cooling_outcome(results):
    """
    Bounded first-pass wall temperature prediction after combined cooling.

    This avoids impossible predictions such as wall temperature below coolant
    temperature. It is a screening estimate, not a full axial solve.
    """

    if results is None:
        return results

    recovery_temp = results.get("regen_feasibility_reference_recovery_temperature")
    current_twg = results.get("recommended_regen_axial_max_hot_wall_temperature")
    material_limit = results.get("material_max_wall_temperature")

    combined_factor = results.get("combined_total_cooling_factor")
    material_factor = results.get("combined_material_factor_target")

    coolant_inlet_temp = (
        results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or results.get("coolant_initial_temperature")
        or 293.0
    )

    if (
        recovery_temp is None
        or current_twg is None
        or material_limit is None
        or combined_factor is None
        or combined_factor <= 0
    ):
        results["combined_cooling_prediction_status"] = "INSUFFICIENT_DATA"
        return results

    current_thermal_gap = current_twg - coolant_inlet_temp

    if current_thermal_gap <= 0:
        results["combined_cooling_prediction_status"] = "INVALID_TEMPERATURE_GAP"
        return results

    # Improved cooling reduces the gap between wall and coolant.
    predicted_twg = coolant_inlet_temp + (current_thermal_gap / combined_factor)

    # Physical lower bound: hot wall cannot sensibly be below coolant inlet temp
    # in this simplified steady model.
    predicted_twg = max(predicted_twg, coolant_inlet_temp)

    improved_material_limit = material_limit

    if material_factor is not None and material_factor > 0:
        improved_material_limit = material_limit * material_factor

    predicted_margin = improved_material_limit - predicted_twg

    results["combined_prediction_coolant_reference_temperature"] = coolant_inlet_temp
    results["combined_predicted_hot_wall_temperature"] = predicted_twg
    results["combined_predicted_material_limit"] = improved_material_limit
    results["combined_predicted_material_margin"] = predicted_margin

    if predicted_margin >= 100.0:
        status = "PASS_WITH_MARGIN"
    elif predicted_margin >= 0.0:
        status = "PASS_LOW_MARGIN"
    else:
        status = "FAIL"

    results["combined_cooling_prediction_status"] = status

    recommendations = []

    if status == "PASS_WITH_MARGIN":
        recommendations.append(
            "Combined cooling allocation gives positive material margin in first-pass screening."
        )
    elif status == "PASS_LOW_MARGIN":
        recommendations.append(
            "Combined cooling allocation barely passes; increase safety margin before accepting design."
        )
    else:
        recommendations.append(
            "Combined cooling allocation does not pass; deeper engine redesign is still required."
        )

    recommendations.append(
        "Next step should convert this estimate into an axial combined-cooling preview."
    )

    results["combined_cooling_prediction_recommendations"] = recommendations

    return results

def build_combined_cooling_axial_preview(results):
    """
    Builds a station-by-station combined cooling preview from the recommended
    regen axial profile.

    This applies the combined cooling factor to every station, giving LEAF a
    full axial pass/fail estimate instead of only a single worst-point estimate.
    """

    if results is None:
        return results

    profile = results.get("recommended_regen_axial_profile")

    if not profile:
        results["combined_axial_preview_status"] = "NO_RECOMMENDED_PROFILE"
        return results

    combined_factor = results.get("combined_total_cooling_factor")
    material_factor = results.get("combined_material_factor_target")
    material_limit = results.get("material_max_wall_temperature")

    coolant_ref = (
        results.get("combined_prediction_coolant_reference_temperature")
        or results.get("coolant_inlet_temperature")
        or results.get("coolant_temperature")
        or 293.0
    )

    if combined_factor is None or combined_factor <= 0 or material_limit is None:
        results["combined_axial_preview_status"] = "INSUFFICIENT_DATA"
        return results

    improved_material_limit = material_limit

    if material_factor is not None and material_factor > 0:
        improved_material_limit = material_limit * material_factor

    combined_profile = []

    max_twg = None
    max_twg_location = None
    min_margin = None
    min_margin_location = None
    failed_station_count = 0

    for station in profile:
        new_station = dict(station)

        x = station.get("x")
        twg = station.get("hot_gas_side_wall_temperature")

        if twg is None:
            twg = station.get("Twg")

        try:
            twg = float(twg)
        except Exception:
            combined_profile.append(new_station)
            continue

        thermal_gap = twg - coolant_ref

        if thermal_gap > 0:
            combined_twg = coolant_ref + thermal_gap / combined_factor
        else:
            combined_twg = twg

        combined_twg = max(combined_twg, coolant_ref)

        margin = improved_material_limit - combined_twg

        new_station["combined_hot_gas_side_wall_temperature"] = combined_twg
        new_station["combined_material_limit"] = improved_material_limit
        new_station["combined_material_margin"] = margin
        new_station["combined_pass"] = 1.0 if margin >= 0.0 else 0.0

        if margin < 0.0:
            failed_station_count += 1

        if max_twg is None or combined_twg > max_twg:
            max_twg = combined_twg
            max_twg_location = x

        if min_margin is None or margin < min_margin:
            min_margin = margin
            min_margin_location = x

        combined_profile.append(new_station)

    results["combined_axial_profile"] = combined_profile
    results["combined_axial_station_count"] = len(combined_profile)
    results["combined_axial_max_hot_wall_temperature"] = max_twg
    results["combined_axial_max_hot_wall_temperature_location"] = max_twg_location
    results["combined_axial_worst_material_margin"] = min_margin
    results["combined_axial_worst_material_margin_location"] = min_margin_location
    results["combined_axial_failed_station_count"] = failed_station_count

    if failed_station_count == 0:
        results["combined_axial_preview_status"] = "PASS"
    else:
        results["combined_axial_preview_status"] = "FAIL"

    return results

def determine_final_regen_design_verdict(results):
    """
    Final high-level regen cooling verdict.

    The controlling gate is:
    1. Regen-only pass
    2. Coupled split strategy
    3. Explicit coating/liner preview
    4. Otherwise fail
    """

    if results is None:
        return results

    recommended_status = results.get("recommended_regen_viability_status")
    coupled_status = results.get("coupled_split_strategy_status")
    explicit_coating_status = results.get("explicit_coating_liner_status")
    bond_coat_validation_status = results.get("bond_coat_validation_status")
    coating_stack_development_status = results.get("coating_stack_development_status")
    coating_stack_unresolved_blockers = (
            results.get("coating_stack_unresolved_blockers") or []
    )

    coating_stack_validation_gate_status = results.get(
        "coating_stack_validation_gate_status"
    )
    coating_stack_validation_priority = results.get(
        "coating_stack_validation_priority"
    )
    coating_stack_final_acceptance_status = results.get(
        "coating_stack_final_acceptance_status"
    )
    coating_stack_final_validation_blocker_gate = results.get(
        "coating_stack_final_validation_blocker_gate"
    )
    coating_stack_final_validation_blockers = (
        results.get("coating_stack_final_validation_blockers") or []
    )
    coating_stack_data_mode = results.get("coating_stack_data_mode")
    coating_stack_data_mode_score = results.get("coating_stack_data_mode_score")
    coating_stack_certification_status = results.get(
        "coating_stack_certification_status"
    )
    coating_stack_certification_score = results.get(
        "coating_stack_certification_score"
    )
    coating_stack_certification_critical_failed_count = results.get(
        "coating_stack_certification_critical_failed_count"
    )
    coating_stack_risk_status = results.get("coating_stack_risk_status")
    coating_stack_top_risk_title = results.get("coating_stack_top_risk_title")
    coating_stack_validation_phase = results.get("coating_stack_validation_phase")
    coating_stack_next_work_package_name = results.get(
        "coating_stack_next_work_package_name"
    )
    coating_stack_acceptance_label = results.get("coating_stack_acceptance_label")
    coating_stack_plain_language_summary = results.get(
        "coating_stack_plain_language_summary"
    )
    coating_stack_dashboard_status = results.get("coating_stack_dashboard_status")
    coating_stack_dashboard_compact_lines = (
        results.get("coating_stack_dashboard_compact_lines") or []
    )
    coating_stack_ui_severity = results.get("coating_stack_ui_severity")
    coating_stack_ui_top_message = results.get("coating_stack_ui_top_message")

    reasons = []
    recommendations = []

    if recommended_status == "PASS":
        verdict = "PASS_REGEN_ONLY"
        reasons.append("Recommended regen geometry is thermally viable without combined cooling assumptions.")
        recommendations.append("Proceed to axial visualisation, material margin refinement, and validation.")

    elif coupled_status == "PASS":
        verdict = "SCREENING_PASS_COUPLED_SPLIT_STRATEGY"
        reasons.append("Coupled axial split-strategy marching preview passes all axial stations.")

        coupled_margin = results.get("coupled_split_strategy_worst_material_margin")
        coupled_failed = results.get("coupled_split_strategy_failed_station_count")

        if coupled_failed is not None:
            reasons.append(f"Coupled split strategy failed station count: {coupled_failed}.")

        if coupled_margin is not None:
            reasons.append(f"Worst coupled split strategy material margin is {coupled_margin:.3g} K.")

        recommendations.append("Treat this as a strong screening pass, not final validation.")
        recommendations.append("Replace simplified film/material assumptions with explicit physical models.")

    elif explicit_coating_status == "PASS":
        verdict = "SCREENING_PASS_EXPLICIT_COATING_LINER"
        reasons.append("Explicit coating/liner preview passes using sourced coating data.")

        recommendations.append("Proceed to coating surface temperature, erosion, adhesion, fatigue, and thermal stress validation.")
        recommendations.append("Check chamber performance penalty and coating manufacturability.")

    elif explicit_coating_status == "PLACEHOLDER_DATA_NOT_QUALIFIABLE":
        verdict = "PROVISIONAL_PASS_EXPLICIT_COATING_PLACEHOLDER_DATA"
        reasons.append("Explicit coating/liner preview closes the thermal gap, but coating data is still placeholder engineering data.")

        coating_name = results.get("explicit_coating_liner_material_name")
        coating_quality = results.get("explicit_coating_liner_source_quality")

        if coating_name:
            reasons.append(f"Selected coating/liner candidate: {coating_name}.")

        if coating_quality:
            reasons.append(f"Coating source quality: {coating_quality}.")

        recommendations.append("Do not accept this as a validated pass.")
        recommendations.append("Replace placeholder coating data with sourced, temperature-dependent material properties.")
        recommendations.append("Add coating surface temperature, erosion, adhesion, thermal stress, and manufacturability checks.")


    elif (

            explicit_coating_status == "FAIL_THERMAL_STRESS"

            and bond_coat_validation_status == "PLACEHOLDER_DATA_NOT_QUALIFIABLE"

    ):

        verdict = "RECOVERABLE_WITH_PLACEHOLDER_BOND_COAT_DATA"

        reasons.append(

            "Explicit coating/liner preview fails first-pass thermal stress, but bond-coat/interlayer screening finds a placeholder candidate that can close the stress-reduction gap."

        )

        bond_name = results.get("bond_coat_best_candidate_name")

        bond_quality = results.get("bond_coat_best_source_quality")

        bond_candidate = results.get("bond_coat_best_candidate") or {}
        bond_margin = bond_candidate.get("stress_reduction_margin")

        if bond_margin is None:
            bond_margin = results.get("explicit_bond_coat_recovery_margin")

        if bond_name:
            reasons.append(f"Best bond-coat/interlayer candidate: {bond_name}.")

        if bond_quality:
            reasons.append(f"Bond-coat source quality: {bond_quality}.")

        if bond_margin is not None:
            reasons.append(f"Bond-coat stress-reduction margin is {bond_margin:.3g}.")

        if coating_stack_development_status:
            reasons.append(
                f"Coating-stack development status: {coating_stack_development_status}."
            )

        if coating_stack_unresolved_blockers:
            reasons.append(
                "Unresolved coating-stack blockers: "
                + "; ".join(str(item) for item in coating_stack_unresolved_blockers)
                + "."
            )

        if coating_stack_validation_priority:
            reasons.append(
                f"Coating-stack validation priority: {coating_stack_validation_priority}."
            )

        if coating_stack_validation_gate_status:
            reasons.append(
                f"Coating-stack validation gate status: {coating_stack_validation_gate_status}."
            )

        if coating_stack_validation_gate_status == "ADVISORY_ONLY":
            recommendations.append(
                "Treat the coating-stack route as advisory only; it may guide development but must not validate the design yet."
            )
        else:
            recommendations.append("Do not accept this as validated.")

        recommendations.append("Replace generic/placeholder bond-coat data with sourced material data.")

        recommendations.append(
            "Bond-coat and coating-stack mass/thickness checks now pass at placeholder level; next add sourced adhesion, thermal fatigue, spallation, and manufacturing checks."
        )

        recommendations.append(
            "Re-run final verdict only after the coating-stack unresolved blockers have been cleared."
        )


    elif explicit_coating_status == "FAIL_THERMAL_STRESS":

        verdict = "FAIL_EXPLICIT_COATING_THERMAL_STRESS"

        reasons.append(
            "Explicit coating/liner preview is thermally recoverable by thickness, but the first-pass coating thermal-stress check fails."
        )

        max_stress = results.get("explicit_coating_max_thermal_stress")
        allowable_stress = results.get("explicit_coating_allowable_stress")
        stress_margin = results.get("explicit_coating_worst_stress_margin")
        failed_stations = results.get("explicit_coating_thermal_stress_failed_station_count")

        if max_stress is not None:
            reasons.append(f"Maximum coating thermal stress is {max_stress:.3g} Pa.")

        if allowable_stress is not None:
            reasons.append(f"Allowable coating stress is {allowable_stress:.3g} Pa.")

        if stress_margin is not None:
            reasons.append(f"Worst coating stress margin is {stress_margin:.3g} Pa.")

        if failed_stations is not None:
            reasons.append(f"{failed_stations} axial stations fail the coating thermal-stress check.")

        recommendations.append("Do not accept the coating path as recoverable until stress failure is resolved.")
        recommendations.append(
            "Reduce coating temperature drop, reduce thermal-expansion mismatch, use a lower-modulus coating, increase allowable coating stress, or add a compliant/bond coat model.")
        recommendations.append(
            "Replace placeholder coating mechanical properties with sourced temperature-dependent values.")

    elif (

            explicit_coating_status == "FAIL_LINER_LIMIT_BUT_THICKNESS_RECOVERABLE"

    ):

        verdict = "RECOVERABLE_WITH_PLACEHOLDER_COATING_DATA"

        reasons.append(

            "Coupled split-strategy marching preview fails, but explicit coating/liner sizing indicates the remaining liner margin can be recovered within the coating practical thickness limit."

        )

        coating_name = results.get("explicit_coating_liner_material_name")

        coating_quality = results.get("explicit_coating_liner_source_quality")

        required_total_thickness = results.get("explicit_coating_total_thickness_required_for_margin")

        max_practical_thickness = results.get("explicit_coating_max_practical_thickness")

        thickness_margin = results.get("explicit_coating_thickness_margin")

        if coating_name:
            reasons.append(f"Recoverable coating candidate: {coating_name}.")

        if coating_quality:
            reasons.append(f"Coating source quality: {coating_quality}.")

        if required_total_thickness is not None:
            reasons.append(

                f"Total coating thickness required for safety margin is {required_total_thickness:.3g} m."

            )

        if max_practical_thickness is not None:
            reasons.append(

                f"Maximum practical coating thickness is {max_practical_thickness:.3g} m."

            )

        if thickness_margin is not None:
            reasons.append(

                f"Coating thickness margin is {thickness_margin:.3g} m."

            )

        recommendations.append("Do not accept this as a validated pass.")

        recommendations.append(
            "Replace placeholder coating data with sourced, temperature-dependent coating properties.")

        recommendations.append("Add adhesion, erosion, thermal stress, cyclic fatigue, and manufacturability checks.")

        recommendations.append("Re-run coupled marching using explicit film, heat-load reduction, and coating physics.")


    elif coupled_status == "FAIL":

        verdict = "FAIL_COUPLED_SPLIT_STRATEGY"

        reasons.append(

            "Coupled axial split-strategy marching preview fails."

        )

        coupled_margin = results.get(

            "coupled_split_strategy_worst_material_margin"

        )

        coupled_failed = results.get(

            "coupled_split_strategy_failed_station_count"

        )

        if coupled_failed is not None:
            reasons.append(

                f"{coupled_failed} axial stations fail the coupled split-strategy preview."

            )

        if coupled_margin is not None:
            reasons.append(

                f"Worst coupled split-strategy material margin is {coupled_margin:.3g} K."

            )

        if explicit_coating_status:
            reasons.append(

                f"Explicit coating/liner status: {explicit_coating_status}."

            )

        recommendations.append(

            "Use the coupled split-strategy marching preview as the controlling design gate."

        )

        recommendations.append(

            "Increase film effectiveness, reduce heat load, improve material capability, or improve coolant-side heat transfer."

        )


    else:
        verdict = "FAIL"
        reasons.append("Neither regen-only cooling nor combined cooling currently provides an acceptable validated design.")
        recommendations.append("Revise cooling architecture, material, film cooling, chamber conditions, or geometry.")

    if solver_pass(results.get("coupled_split_auto_tuned_status")):
        auto_margin = results.get("coupled_split_auto_tuned_worst_material_margin")

        reasons.append("Coupled auto-tuned design-target preview passes, but it is not validation.")

        if auto_margin is not None:
            reasons.append(f"Coupled auto-tuned worst material margin is {auto_margin:.3g} K.")

        recommendations.append("Use the coupled auto-tuned preview only as a design target.")

    coating_dependent_verdicts = (
        "SCREENING_PASS_EXPLICIT_COATING_LINER",
        "PROVISIONAL_PASS_EXPLICIT_COATING_PLACEHOLDER_DATA",
        "RECOVERABLE_WITH_PLACEHOLDER_BOND_COAT_DATA",
        "RECOVERABLE_WITH_PLACEHOLDER_COATING_DATA",
        "DEVELOPMENT_ROUTE_ONLY_COATING_STACK_BLOCKED",
    )

    coating_stack_blocks_final_validation = False
    coating_stack_final_validation_blocker_gate = "NOT_APPLICABLE"

    coating_gate_failures = []

    if verdict in coating_dependent_verdicts:
        if coating_stack_final_acceptance_status != "VALIDATION_SUPPORT_ALLOWED":
            coating_gate_failures.append(
                f"Final acceptance status is {coating_stack_final_acceptance_status}."
            )
            coating_stack_final_validation_blocker_gate = (
                coating_stack_final_validation_blocker_gate
                if coating_stack_final_validation_blocker_gate != "NOT_APPLICABLE"
                else "FINAL_ACCEPTANCE_NOT_ALLOWED"
            )

        if coating_stack_data_mode != "SOURCED_VALIDATION_MODE":
            coating_gate_failures.append(
                f"Data mode is {coating_stack_data_mode}; required SOURCED_VALIDATION_MODE."
            )

        if coating_stack_certification_status != "CERTIFICATION_READY":
            coating_gate_failures.append(
                f"Certification status is {coating_stack_certification_status}."
            )

        if coating_stack_risk_status in ("CRITICAL_RISK", "HIGH_RISK"):
            coating_gate_failures.append(
                f"Risk status is {coating_stack_risk_status}."
            )

        if coating_stack_validation_phase != "PHASE_5_VALIDATION_SUPPORT_ALLOWED":
            coating_gate_failures.append(
                f"Validation phase is {coating_stack_validation_phase}."
            )

        if coating_stack_acceptance_label != "CAN_SUPPORT_FINAL_VALIDATION":
            coating_gate_failures.append(
                f"Acceptance label is {coating_stack_acceptance_label}."
            )

        for blocker in coating_stack_final_validation_blockers[:5]:
            coating_gate_failures.append(f"Blocker: {blocker}")

    if coating_gate_failures:
        coating_stack_blocks_final_validation = True
        verdict = "DEVELOPMENT_ROUTE_ONLY_COATING_STACK_BLOCKED"

        if coating_stack_final_validation_blocker_gate == "NOT_APPLICABLE":
            coating_stack_final_validation_blocker_gate = "BLOCKED_PENDING_VALIDATION_DATA"

        reasons.append(
            "Coating-stack final validation is blocked by unresolved validation gates."
        )

        for failure in coating_gate_failures:
            if failure not in reasons:
                reasons.append(failure)

        recommendations.append(
            "Keep the coating/liner route as DEVELOPMENT_ROUTE_ONLY until sourced coating data, sourced bond-coat data, adhesion, fatigue, spallation, thermal-stress, risk, and certification gates are cleared."
        )

        if coating_stack_next_work_package_name:
            recommendations.append(
                f"Next coating-stack work package: {coating_stack_next_work_package_name}."
            )

        if coating_stack_plain_language_summary:
            recommendations.append(coating_stack_plain_language_summary)

    results["final_regen_design_verdict"] = verdict
    results["final_regen_design_reasons"] = reasons
    results["final_regen_design_recommendations"] = recommendations
    results["coating_stack_blocks_final_validation"] = coating_stack_blocks_final_validation
    results["coating_stack_final_validation_blocker_gate"] = coating_stack_final_validation_blocker_gate
    results["final_regen_design_uses_coating_stack"] = (
        verdict in coating_dependent_verdicts
        or explicit_coating_status in ("PASS", "FAIL_THERMAL_STRESS")
    )
    results["final_regen_design_coating_stack_acceptance_status"] = (
        coating_stack_final_acceptance_status
    )
    results["final_regen_design_coating_stack_data_mode"] = coating_stack_data_mode
    results["final_regen_design_coating_stack_data_mode_score"] = coating_stack_data_mode_score
    results["final_regen_design_coating_stack_certification_status"] = (
        coating_stack_certification_status
    )
    results["final_regen_design_coating_stack_certification_score"] = (
        coating_stack_certification_score
    )
    results["final_regen_design_coating_stack_risk_status"] = coating_stack_risk_status
    results["final_regen_design_coating_stack_top_risk"] = coating_stack_top_risk_title
    results["final_regen_design_coating_stack_validation_phase"] = (
        coating_stack_validation_phase
    )
    results["final_regen_design_coating_stack_next_work_package"] = (
        coating_stack_next_work_package_name
    )
    results["final_regen_design_coating_stack_acceptance_label"] = (
        coating_stack_acceptance_label
    )
    results["final_regen_design_coating_stack_summary"] = (
        coating_stack_plain_language_summary
    )

    return results

def update_regen_required_next_steps(results):
    """
    Updates required next steps based on the current controlling regen verdict.
    """

    if results is None:
        return results

    verdict = results.get("final_regen_design_verdict")

    if verdict == "DEVELOPMENT_ROUTE_ONLY_COATING_STACK_BLOCKED":
        next_priority_summary = results.get(
            "coating_stack_next_priority_action_summary"
        )

        steps = [
            "Keep the coating/liner route as DEVELOPMENT_ROUTE_ONLY. Do not use it as final validation yet.",
            "Replace placeholder coating material data with sourced temperature-dependent coating data.",
            "Replace placeholder bond-coat/interlayer data with sourced stress-relief and compatibility data.",
            "Resolve coating thermal stress using sourced coating and bond-coat mechanical properties.",
            "Add coating/bond-coat adhesion, cyclic fatigue, and spallation-life models.",
            "Re-run the coating-stack certification checklist and final acceptance gate after sourced data is added.",
        ]

        if next_priority_summary:
            steps.insert(1, next_priority_summary)

    elif verdict == "RECOVERABLE_WITH_PLACEHOLDER_BOND_COAT_DATA":
        steps = [
            "Replace generic compliant interlayer with a real sourced bond-coat/interlayer material.",
            "Add sourced temperature-dependent bond-coat stress-reduction, modulus, CTE, density, and thickness data.",
            "Replace placeholder Hafnia coating properties with sourced temperature-dependent coating data.",
            "Add coating/bond-coat adhesion model using bond strength, CTE mismatch, and thermal-cycle data.",
            "Add coating cyclic fatigue and spallation-life model.",
            "Raise coating-stack validation gate status above ADVISORY_ONLY before allowing the coating path to support final validation.",
        ]

    elif verdict == "FAIL_EXPLICIT_COATING_THERMAL_STRESS":
        steps = [
            "Replace placeholder coating elastic modulus, thermal expansion coefficient, Poisson ratio, and allowable stress with sourced temperature-dependent data.",
            "Add a compliant bond-coat or graded-layer model to reduce coating thermal stress.",
            "Reduce coating temperature drop per layer or evaluate multi-layer coating architecture.",
            "Evaluate alternative thermal barrier coatings with lower stiffness or better thermal-expansion compatibility.",
            "Add coating cyclic thermal fatigue and spallation checks before accepting coating-based recovery.",
        ]

    elif verdict == "RECOVERABLE_WITH_PLACEHOLDER_COATING_DATA":
        steps = [
            "Replace placeholder Hafnia/ceramic coating values with sourced temperature-dependent data.",
            "Add explicit coating thermal-stress and adhesion checks.",
            "Add erosion/spallation risk checks for the hot-gas-side coating surface.",
            "Add coating mass penalty using coating density and coated surface area.",
            "Re-run explicit coating/liner preview using the total required coating thickness for margin.",
            "Only then re-run the final coupled marching verdict.",
        ]

    elif verdict == "PROVISIONAL_PASS_EXPLICIT_COATING_PLACEHOLDER_DATA":
        steps = [
            "Replace placeholder coating/liner values with sourced material data.",
            "Add temperature-dependent coating thermal conductivity and surface limit data.",
            "Add coating erosion, adhesion, thermal stress, and cyclic fatigue checks.",
            "Add coating/liner density and mass penalty calculations.",
            "Re-run explicit coating/liner preview only after sourced coating data is available.",
        ]

    elif verdict == "SCREENING_PASS_EXPLICIT_COATING_LINER":
        steps = [
            "Validate coating/liner thermal model against sourced material data.",
            "Add erosion, adhesion, thermal stress, and cyclic fatigue checks.",
            "Add manufacturing and maximum practical thickness checks.",
            "Evaluate chamber performance penalty from coating surface temperature and roughness.",
        ]

    elif verdict == "FAIL_COUPLED_SPLIT_STRATEGY":
        steps = [
            "Use the coupled auto-tuned and balanced rebalance outputs as design targets only.",
            "Improve explicit film cooling modelling.",
            "Improve explicit heat-load reduction modelling.",
            "Use sourced coating/liner material data before accepting coating-based results.",
            "Re-run coupled marching using only explicit physical mechanisms.",
        ]

    elif verdict == "SCREENING_PASS_COUPLED_SPLIT_STRATEGY":
        steps = [
            "Validate coupled split-strategy marching output against exported station data.",
            "Add pressure-drop-coupled channel marching.",
            "Replace simplified film assumptions with injection-location and film mass-flow modelling.",
            "Connect material candidate screening to coupled split target temperature.",
            "Compare LEAF output against a known RP-1/LOX regenerative engine reference case.",
        ]

    else:
        steps = [
            "Run recommended geometry and thermal preview.",
            "Check geometry fit, Reynolds number, pressure drop, and material margin.",
        ]

    results["required_regen_next_steps"] = steps
    results["required_next_steps"] = steps
    results["combined_cooling_required_next_steps"] = steps

    return results

def assess_combined_cooling_confidence(results):
    """
    Rates confidence in the combined cooling result.

    A combined cooling pass is still not final validation, but confidence should
    improve when axial film + material preview also passes.
    """

    if results is None:
        return results

    verdict = results.get("final_regen_design_verdict")
    film_status = results.get("film_cooling_status")
    trade_status = results.get("cooling_trade_selected_status")
    combined_status = (
            results.get("vl_split_strategy_status")
            or results.get("velocity_limited_combined_preview_status")
            or results.get("full_combined_component_preview_status")
            or results.get("combined_axial_preview_status")
    )
    film_material_status = results.get("film_material_axial_preview_status")

    film_effectiveness = results.get("combined_film_effectiveness_target")
    heat_load_reduction = results.get("combined_heat_load_reduction_target")
    material_factor = results.get("combined_material_factor_target")
    regen_factor = results.get("combined_regen_improvement_factor_target")

    reasons = []
    next_steps = []
    confidence_score = 100.0

    if not solver_pass(combined_status):
        confidence_score -= 60.0
        reasons.append("Combined axial preview does not pass.")

    if solver_fail(results.get("velocity_limited_combined_preview_status")):
        reasons.append(
            "Physically velocity-limited combined preview fails, even though abstract combined preview may pass."
        )
        confidence_score -= 25.0

    if verdict in (
        "SCREENING_PASS_COMBINED_COOLING",
        "MARGINAL_SCREENING_PASS_COMBINED_COOLING",
    ):
        reasons.append("Cooling only passes after applying combined first-pass assumptions.")
        confidence_score -= 20.0

    if film_material_status == "PASS":
        reasons.append("Axial film + material preview passes all stations.")
        confidence_score += 15.0
    else:
        reasons.append("Axial film + material preview does not pass.")
        confidence_score -= 15.0

    if film_status == "FILM_COOLING_SEVERE":
        reasons.append("Film cooling requirement is severe and needs a dedicated model.")
        next_steps.append("Improve axial film-cooling effectiveness model.")
        confidence_score -= 20.0

    if trade_status == "REQUIRED":
        reasons.append("No single cooling method is sufficient; combined strategy is required.")
        confidence_score -= 10.0

    if film_effectiveness is not None and film_effectiveness > 0.30:
        reasons.append("Film effectiveness target is high.")
        confidence_score -= 10.0

    if heat_load_reduction is not None and heat_load_reduction > 0.20:
        reasons.append("Required heat-load reduction is significant.")
        confidence_score -= 10.0

    if material_factor is not None and material_factor > 1.4:
        reasons.append("Material capability target is significantly above the current material.")
        next_steps.append("Implement material database with selectable high-temperature alloys.")
        confidence_score -= 10.0

    if regen_factor is not None and regen_factor > 1.25:
        reasons.append("Further regen/channel improvement is required beyond current recommended geometry.")
        next_steps.append("Implement variable channel geometry optimisation.")
        confidence_score -= 10.0

    if solver_fail(results.get("coupled_split_strategy_status")):
        reasons.append(
            "Coupled split-strategy marching preview fails and overrides the earlier split screening pass."
        )
        confidence_score -= 35.0

    if solver_pass(results.get("vl_split_strategy_status")):
        split_margin = results.get("vl_split_strategy_worst_material_margin")

        reasons.append(
            "Velocity-limited split strategy passes, but it is still a screening model."
        )

        confidence_score += 35.0

        if split_margin is not None and split_margin > 50.0:
            reasons.append(
                "Velocity-limited split strategy has positive margin above 50 K."
            )
            confidence_score += 10.0

    confidence_score = max(0.0, min(100.0, confidence_score))

    if confidence_score >= 75.0:
        confidence = "HIGH"
    elif confidence_score >= 50.0:
        confidence = "MEDIUM"
    elif confidence_score >= 25.0:
        confidence = "LOW"
    else:
        confidence = "VERY_LOW"

    if not next_steps:
        next_steps.append("Proceed to axial thermal visualisation and detailed validation.")

    results["combined_cooling_confidence"] = confidence
    results["combined_cooling_confidence_score"] = confidence_score
    results["combined_cooling_confidence_reasons"] = reasons
    results["combined_cooling_required_next_steps"] = next_steps

    return results

def calculate_coolant_velocity(
        coolant_mass_flow_rate=None,
        coolant_density=None,
        total_coolant_flow_area=None
):
    """
    Coolant bulk velocity.

    Equation:
        v_c = mdot_c / (rho_c * A_total)
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_density,
            coolant_mass_flow_rate,
            total_coolant_flow_area,
        )
    ):
        return None


    if (
        coolant_mass_flow_rate is None
        or coolant_density is None
        or total_coolant_flow_area is None
        or coolant_density <= 0
        or total_coolant_flow_area <= 0
    ):
        return None

    return coolant_mass_flow_rate / (coolant_density * total_coolant_flow_area)


def calculate_coolant_reynolds_number(
        coolant_density=None,
        coolant_velocity=None,
        coolant_hydraulic_diameter=None,
        coolant_dynamic_viscosity=None
):
    """
    Coolant Reynolds number.

    Equation:
        Re = rho * v * Dh / mu
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_density,
            coolant_dynamic_viscosity,
            coolant_hydraulic_diameter,
            coolant_velocity,
        )
    ):
        return None


    if (
        coolant_density is None
        or coolant_velocity is None
        or coolant_hydraulic_diameter is None
        or coolant_dynamic_viscosity is None
        or coolant_density <= 0
        or coolant_velocity <= 0
        or coolant_hydraulic_diameter <= 0
        or coolant_dynamic_viscosity <= 0
    ):
        return None

    return (
        coolant_density
        * coolant_velocity
        * coolant_hydraulic_diameter
        / coolant_dynamic_viscosity
    )

def calculate_required_velocity_for_reynolds(
        target_reynolds_number=None,
        coolant_density=None,
        coolant_hydraulic_diameter=None,
        coolant_dynamic_viscosity=None
):
    """
    Rearranged Reynolds equation.

    Re = rho*v*Dh/mu

    v = Re*mu/(rho*Dh)
    """

    if (
        target_reynolds_number is None
        or coolant_density is None
        or coolant_hydraulic_diameter is None
        or coolant_dynamic_viscosity is None
        or target_reynolds_number <= 0
        or coolant_density <= 0
        or coolant_hydraulic_diameter <= 0
        or coolant_dynamic_viscosity <= 0
    ):
        return None

    return (
        target_reynolds_number
        * coolant_dynamic_viscosity
        / (
            coolant_density
            * coolant_hydraulic_diameter
        )
    )

def calculate_required_total_flow_area_for_velocity(
        coolant_mass_flow_rate=None,
        coolant_density=None,
        target_velocity=None
):
    """
    Rearranged velocity equation.

    v = mdot/(rho*A)

    A = mdot/(rho*v)
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_density,
            coolant_mass_flow_rate,
            target_velocity,
        )
    ):
        return None


    if (
        coolant_mass_flow_rate is None
        or coolant_density is None
        or target_velocity is None
        or coolant_mass_flow_rate <= 0
        or coolant_density <= 0
        or target_velocity <= 0
    ):
        return None

    return (
        coolant_mass_flow_rate
        / (
            coolant_density
            * target_velocity
        )
    )

def calculate_coolant_prandtl_number(
        coolant_specific_heat_cp=None,
        coolant_dynamic_viscosity=None,
        coolant_thermal_conductivity=None
):
    """
    Coolant Prandtl number.

    Equation:
        Pr = Cp * mu / k
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_dynamic_viscosity,
            coolant_specific_heat_cp,
            coolant_thermal_conductivity,
        )
    ):
        return None


    if (
        coolant_specific_heat_cp is None
        or coolant_dynamic_viscosity is None
        or coolant_thermal_conductivity is None
        or coolant_specific_heat_cp <= 0
        or coolant_dynamic_viscosity <= 0
        or coolant_thermal_conductivity <= 0
    ):
        return None

    return (
        coolant_specific_heat_cp
        * coolant_dynamic_viscosity
        / coolant_thermal_conductivity
    )


def calculate_coolant_nusselt_number(
        coolant_reynolds_number=None,
        coolant_prandtl_number=None
):
    """
    Coolant internal-flow Nusselt model.

    Qualified branches:

    Laminar:
        0 < Re < 2300
        Nu = 3.66

        This is the fully developed, constant-wall-temperature
        laminar approximation. The hydraulic-diameter treatment for
        non-circular regen channels remains an explicit qualification
        limitation.

    Transitional / unqualified:
        2300 <= Re < 10000
        No qualified interpolation is currently owned by LEAF.
        Fail closed by returning None.

    Turbulent Dittus-Boelter:
        Re >= 10000
        0.6 <= Pr <= 160

        Nu = 0.023 * Re^0.8 * Pr^0.4

        This is retained as a fully developed, smooth internal-flow
        approximation.
    """

    if (
        coolant_reynolds_number is None
        or coolant_prandtl_number is None
    ):
        return None

    try:
        reynolds = float(
            coolant_reynolds_number
        )

        prandtl = float(
            coolant_prandtl_number
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            reynolds
        )
        or not math.isfinite(
            prandtl
        )
        or reynolds <= 0.0
        or prandtl <= 0.0
    ):
        return None

    if reynolds < 2300.0:
        return 3.66

    if reynolds < 10000.0:
        return None

    if (
        prandtl < 0.6
        or prandtl > 160.0
    ):
        return None

    return (
        0.023
        * (reynolds ** 0.8)
        * (prandtl ** 0.4)
    )


def calculate_coolant_heat_transfer_coefficient(
        coolant_nusselt_number=None,
        coolant_thermal_conductivity=None,
        coolant_hydraulic_diameter=None
):
    """
    Coolant-side convective heat-transfer coefficient.

    Equation:
        hc = Nu * k / Dh
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_hydraulic_diameter,
            coolant_nusselt_number,
            coolant_thermal_conductivity,
        )
    ):
        return None


    if (
        coolant_nusselt_number is None
        or coolant_thermal_conductivity is None
        or coolant_hydraulic_diameter is None
        or coolant_nusselt_number <= 0
        or coolant_thermal_conductivity <= 0
        or coolant_hydraulic_diameter <= 0
    ):
        return None

    return (
        coolant_nusselt_number
        * coolant_thermal_conductivity
        / coolant_hydraulic_diameter
    )


def calculate_regen_total_thermal_resistance(
        hot_gas_heat_transfer_coefficient=None,
        hot_gas_wall_thickness=None,
        wall_thermal_conductivity=None,
        coolant_heat_transfer_coefficient=None
):
    """
    Total area-normalised thermal resistance.

    Equation:
        R_total = 1/hg + tw/kw + 1/hc

    Units:
        m² K / W
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_heat_transfer_coefficient,
            hot_gas_heat_transfer_coefficient,
            hot_gas_wall_thickness,
            wall_thermal_conductivity,
        )
    ):
        return None


    if (
        hot_gas_heat_transfer_coefficient is None
        or hot_gas_wall_thickness is None
        or wall_thermal_conductivity is None
        or coolant_heat_transfer_coefficient is None
        or hot_gas_heat_transfer_coefficient <= 0
        or hot_gas_wall_thickness <= 0
        or wall_thermal_conductivity <= 0
        or coolant_heat_transfer_coefficient <= 0
    ):
        return None

    return (
        (1.0 / hot_gas_heat_transfer_coefficient)
        + (hot_gas_wall_thickness / wall_thermal_conductivity)
        + (1.0 / coolant_heat_transfer_coefficient)
    )

def calculate_regen_thermal_resistance_breakdown(
        hot_gas_heat_transfer_coefficient=None,
        hot_gas_wall_thickness=None,
        wall_thermal_conductivity=None,
        coolant_heat_transfer_coefficient=None
):
    """
    Breaks the regen thermal resistance into components.

    Rg = 1 / hg
    Rw = tw / kw
    Rc = 1 / hc

    Units:
        m² K / W
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_heat_transfer_coefficient,
            hot_gas_heat_transfer_coefficient,
            hot_gas_wall_thickness,
            wall_thermal_conductivity,
        )
    ):
        return None


    if (
        hot_gas_heat_transfer_coefficient is None
        or hot_gas_wall_thickness is None
        or wall_thermal_conductivity is None
        or coolant_heat_transfer_coefficient is None
        or hot_gas_heat_transfer_coefficient <= 0
        or hot_gas_wall_thickness <= 0
        or wall_thermal_conductivity <= 0
        or coolant_heat_transfer_coefficient <= 0
    ):
        return None

    gas_resistance = 1.0 / hot_gas_heat_transfer_coefficient
    wall_resistance = hot_gas_wall_thickness / wall_thermal_conductivity
    coolant_resistance = 1.0 / coolant_heat_transfer_coefficient

    total = gas_resistance + wall_resistance + coolant_resistance

    if total <= 0:
        return None

    values = {
        "gas_side_resistance": gas_resistance,
        "wall_conduction_resistance": wall_resistance,
        "coolant_side_resistance": coolant_resistance,
        "total_thermal_resistance": total,
        "gas_side_resistance_fraction": gas_resistance / total,
        "wall_conduction_resistance_fraction": wall_resistance / total,
        "coolant_side_resistance_fraction": coolant_resistance / total,
    }

    controlling = max(
        [
            ("gas_side", values["gas_side_resistance_fraction"]),
            ("wall_conduction", values["wall_conduction_resistance_fraction"]),
            ("coolant_side", values["coolant_side_resistance_fraction"]),
        ],
        key=lambda item: item[1]
    )

    values["controlling_thermal_resistance"] = controlling[0]

    return values

def calculate_regen_heat_flux(
        selected_gas_side_recovery_temperature=None,
        coolant_bulk_temperature=None,
        regen_total_thermal_resistance=None
):
    """
    Regenerative cooling heat flux.

    Equation:
        q'' = (Tr_gas - Tcoolant_bulk) / R_total
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_bulk_temperature,
            regen_total_thermal_resistance,
            selected_gas_side_recovery_temperature,
        )
    ):
        return None


    if (
        selected_gas_side_recovery_temperature is None
        or coolant_bulk_temperature is None
        or regen_total_thermal_resistance is None
        or regen_total_thermal_resistance <= 0
    ):
        return None

    delta_t = selected_gas_side_recovery_temperature - coolant_bulk_temperature

    if delta_t <= 0:
        return None

    return delta_t / regen_total_thermal_resistance


def calculate_hot_gas_side_wall_temperature(
        selected_gas_side_recovery_temperature=None,
        regen_heat_flux=None,
        hot_gas_heat_transfer_coefficient=None
):
    """
    Gas-side metal wall temperature.

    Equation:
        Twg = Tr_gas - q'' / hg
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            hot_gas_heat_transfer_coefficient,
            regen_heat_flux,
            selected_gas_side_recovery_temperature,
        )
    ):
        return None


    if (
        selected_gas_side_recovery_temperature is None
        or regen_heat_flux is None
        or hot_gas_heat_transfer_coefficient is None
        or hot_gas_heat_transfer_coefficient <= 0
    ):
        return None

    return selected_gas_side_recovery_temperature - (
        regen_heat_flux / hot_gas_heat_transfer_coefficient
    )


def calculate_coolant_side_wall_temperature_calculated(
        coolant_bulk_temperature=None,
        regen_heat_flux=None,
        coolant_heat_transfer_coefficient=None
):
    """
    Coolant-side metal wall temperature.

    Equation:
        Twc = Tcoolant_bulk + q'' / hc
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_bulk_temperature,
            coolant_heat_transfer_coefficient,
            regen_heat_flux,
        )
    ):
        return None


    if (
        coolant_bulk_temperature is None
        or regen_heat_flux is None
        or coolant_heat_transfer_coefficient is None
        or coolant_heat_transfer_coefficient <= 0
    ):
        return None

    return coolant_bulk_temperature + (
        regen_heat_flux / coolant_heat_transfer_coefficient
    )


def calculate_local_hot_gas_surface_area(
        cross_sectional_area=None,
        throat_radius=None,
        selected_station_length=None
):
    """
    Approximate local hot-gas wetted surface area for a station band.

    Equation:
        A_hot = 2*pi*r*dx
    """
    # PFQ-5 direct-dependency finite-real containment.
    # Invalid/non-finite non-None values collapse to existing None semantics.
    if (
        cross_sectional_area is not None
        and not _pfq_finite_real(cross_sectional_area)
    ):
        cross_sectional_area = None

    if (
        selected_station_length is not None
        and not _pfq_finite_real(selected_station_length)
    ):
        selected_station_length = None

    if (
        throat_radius is not None
        and not _pfq_finite_real(throat_radius)
    ):
        throat_radius = None


    if selected_station_length is None:
        selected_station_length = 0.001

    gas_radius = None

    if cross_sectional_area is not None and cross_sectional_area > 0:
        gas_radius = math.sqrt(cross_sectional_area / math.pi)
    elif throat_radius is not None and throat_radius > 0:
        gas_radius = throat_radius

    if gas_radius is None or selected_station_length <= 0:
        return None

    return 2.0 * math.pi * gas_radius * selected_station_length


def calculate_coolant_temperature_rise(
        regen_heat_flux=None,
        local_hot_gas_surface_area=None,
        coolant_mass_flow_rate=None,
        coolant_specific_heat_cp=None
):
    """
    Coolant temperature rise across the selected station band.

    Equation:
        delta_T = q'' * A_hot / (mdot_c * Cp_c)
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_mass_flow_rate,
            coolant_specific_heat_cp,
            local_hot_gas_surface_area,
            regen_heat_flux,
        )
    ):
        return None


    if (
        regen_heat_flux is None
        or local_hot_gas_surface_area is None
        or coolant_mass_flow_rate is None
        or coolant_specific_heat_cp is None
        or regen_heat_flux <= 0
        or local_hot_gas_surface_area <= 0
        or coolant_mass_flow_rate <= 0
        or coolant_specific_heat_cp <= 0
    ):
        return None

    return (
        regen_heat_flux
        * local_hot_gas_surface_area
        / (coolant_mass_flow_rate * coolant_specific_heat_cp)
    )


def calculate_coolant_outlet_temperature(
        coolant_bulk_temperature=None,
        coolant_temperature_rise=None
):
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_bulk_temperature,
            coolant_temperature_rise,
        )
    ):
        return None

    if (
        coolant_bulk_temperature is None
        or coolant_temperature_rise is None
    ):
        return None

    return coolant_bulk_temperature + coolant_temperature_rise

def calculate_coolant_mean_temperature(
        coolant_inlet_temperature=None,
        coolant_outlet_temperature=None,
        coolant_bulk_temperature=None
):
    """
    Mean coolant temperature for single-station property evaluation.

    For a station band:
        T_mean = (T_in + T_out) / 2

    If inlet is unavailable, falls back to coolant_bulk_temperature.
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_inlet_temperature,
            coolant_outlet_temperature,
        )
    ):
        return None


    inlet = coolant_inlet_temperature

    if inlet is None:
        inlet = coolant_bulk_temperature

    if inlet is None or coolant_outlet_temperature is None:
        return None

    return 0.5 * (inlet + coolant_outlet_temperature)

def calculate_material_temperature_margin(
        material_max_wall_temperature=None,
        hot_gas_side_wall_temperature=None
):
    """
    Positive margin = material is below recommended temperature.
    Negative margin = material exceeds recommended temperature.
    """
    # PFQ-5 direct-dependency finite-real containment.
    # Invalid/non-finite non-None values collapse to existing None semantics.
    if (
        hot_gas_side_wall_temperature is not None
        and not _pfq_finite_real(hot_gas_side_wall_temperature)
    ):
        hot_gas_side_wall_temperature = None

    if (
        material_max_wall_temperature is not None
        and not _pfq_finite_real(material_max_wall_temperature)
    ):
        material_max_wall_temperature = None


    if (
        material_max_wall_temperature is None
        or hot_gas_side_wall_temperature is None
    ):
        return None

    return material_max_wall_temperature - hot_gas_side_wall_temperature

def validate_regen_consistency(results):
    """
    Checks whether regen outputs are physically trustworthy.

    This does not replace the solver.
    It tells the user whether the solver result is design-valid,
    diagnostic-only, or invalid.
    """

    issues = []
    warnings = []

    geometry_valid = results.get("channel_geometry_valid")
    reynolds = results.get("regen_axial_min_reynolds_number")
    bottleneck = results.get("regen_axial_primary_thermal_bottleneck")
    heat_absorbed = results.get("regen_axial_total_heat_absorbed")
    coolant_temp_rise = results.get("regen_axial_coolant_total_temperature_rise")
    coolant_mdot = results.get("coolant_mass_flow_rate")
    coolant_cp = results.get("coolant_specific_heat_cp")

    # -------------------------
    # 1. Geometry validity
    # -------------------------
    if geometry_valid != 1 and geometry_valid != 1.0:
        issues.append(
            "Cooling channel geometry is invalid. Thermal results are diagnostic only until channel pitch/rib width physically fit."
        )

    # -------------------------
    # 2. Flow validity
    # -------------------------
    if reynolds is None:
        issues.append("Minimum axial Reynolds number is missing.")
    elif reynolds < 2300:
        issues.append(
            "Coolant flow is laminar. Regen cooling should normally use turbulent coolant flow."
        )
    elif reynolds < 10000:
        warnings.append(
            "Coolant flow is transitional. Heat transfer prediction has reduced confidence."
        )

    # -------------------------
    # 3. Energy consistency
    # -------------------------
    if (
        heat_absorbed is not None
        and coolant_temp_rise is not None
        and coolant_mdot is not None
        and coolant_cp is not None
        and coolant_mdot > 0
        and coolant_cp > 0
    ):
        expected_delta_t = heat_absorbed / (coolant_mdot * coolant_cp)

        results["regen_energy_balance_expected_delta_t"] = expected_delta_t
        results["regen_energy_balance_error"] = coolant_temp_rise - expected_delta_t

        if abs(expected_delta_t) > 1e-9:
            results["regen_energy_balance_error_percent"] = (
                abs(coolant_temp_rise - expected_delta_t)
                / abs(expected_delta_t)
                * 100.0
            )
        else:
            results["regen_energy_balance_error_percent"] = None

    else:
        warnings.append("Energy balance could not be fully checked.")

    # -------------------------
    # 4. Thermal bottleneck
    # -------------------------
    if bottleneck == "coolant_side":
        warnings.append(
            "Coolant-side heat transfer is the dominant thermal bottleneck."
        )

    results["regen_consistency_issues"] = issues
    results["regen_consistency_warnings"] = warnings

    if issues:
        results["regen_result_confidence"] = "DIAGNOSTIC_ONLY"
    elif warnings:
        results["regen_result_confidence"] = "LOW_TO_MEDIUM"
    else:
        results["regen_result_confidence"] = "DESIGN_VALID"

    return results

def apply_regen_material_fallbacks(results):
    """
    Emergency material fallback for regen validation.

    This prevents regen validation from silently producing None when
    the GUI material panel has not passed material metadata into the solver.

    Default fallback represents a copper alloy / GRCop-style liner.
    These values should later be replaced by the material database authority.
    """

    if results is None:
        return results

    if results.get("selected_material_name") in [None, "", "N/A"]:
        results["selected_material_name"] = "Fallback Copper Alloy / GRCop-style"

    if results.get("material_yield_strength") is None:
        results["material_yield_strength"] = 230_000_000.0

    if results.get("wall_thermal_conductivity") is None:
        results["wall_thermal_conductivity"] = 344.0

    if results.get("material_density") is None:
        results["material_density"] = 8890.0

    if results.get("material_max_wall_temperature") is None:
        results["material_max_wall_temperature"] = 900.0

    return results

def apply_regen_failure_statuses(results):
    """
    Final hard-gate regen validation.

    This deliberately marks the design as FAIL if:
    - channel geometry does not physically fit
    - coolant flow is laminar / too weak
    - wall temperature exceeds material limit
    - key regen data is missing
    """

    if results is None:
        return results

    geometry_valid = results.get("channel_geometry_valid")
    reynolds = results.get("coolant_reynolds_number")
    axial_min_reynolds = results.get("regen_axial_min_reynolds_number")

    material_limit = results.get("material_max_wall_temperature")
    local_twg = results.get("hot_gas_side_wall_temperature")
    axial_twg = results.get("regen_axial_max_hot_wall_temperature")

    # -------------------------
    # Geometry status
    # -------------------------
    if geometry_valid == 1 or geometry_valid == 1.0:
        results["regen_geometry_status"] = "PASS"
    else:
        results["regen_geometry_status"] = "FAIL"

    # -------------------------
    # Coolant status
    # -------------------------
    governing_reynolds = axial_min_reynolds if axial_min_reynolds is not None else reynolds

    if governing_reynolds is None:
        results["regen_coolant_status"] = "FAIL"
    elif governing_reynolds < 2300:
        results["regen_coolant_status"] = "FAIL"
    elif governing_reynolds < 10000:
        results["regen_coolant_status"] = "WARN"
    else:
        results["regen_coolant_status"] = "PASS"

    # -------------------------
    # Thermal / material status
    # -------------------------
    governing_twg = axial_twg if axial_twg is not None else local_twg

    if material_limit is None or governing_twg is None:
        results["regen_thermal_status"] = "FAIL"
        results["regen_material_status"] = "FAIL"
    else:
        margin = material_limit - governing_twg

        results["material_temperature_margin"] = margin
        results["regen_axial_material_temperature_margin"] = margin
        results["regen_axial_worst_material_margin"] = margin

        if results.get("regen_axial_worst_material_margin_location") is None:
            results["regen_axial_worst_material_margin_location"] = (
                results.get("regen_axial_max_hot_wall_temperature_location")
            )

        if margin < 0:
            results["regen_thermal_status"] = "FAIL"
            results["regen_material_status"] = "FAIL"
        else:
            results["regen_thermal_status"] = "PASS"
            results["regen_material_status"] = "PASS"

    # -------------------------
    # Overall status
    # -------------------------
    statuses = [
        results.get("regen_geometry_status"),
        results.get("regen_thermal_status"),
        results.get("regen_coolant_status"),
        results.get("regen_material_status"),
    ]

    if solver_highest_severity(statuses) == "FAIL":
        results["regen_overall_status"] = "FAIL"
    elif solver_highest_severity(statuses) == "WARN":
        results["regen_overall_status"] = "WARN"
    else:
        results["regen_overall_status"] = "PASS"

    return results

def calculate_bartz_gas_side_heat_transfer_coefficient(
        throat_diameter=None,
        gas_dynamic_viscosity=None,
        gas_specific_heat_cp=None,
        gas_prandtl_number=None,
        chamber_pressure=None,
        characteristic_velocity=None,
        throat_radius_of_curvature=None,
        throat_area=None,
        cross_sectional_area=None,
        bartz_sigma=None
):
    """
    Full Bartz gas-side heat-transfer coefficient.

    Equation:
        hg = 0.026 / Dt^0.2
             * (mu^0.2 * cp / Pr^0.6)
             * (Pc / c*)^0.8
             * (Dt / rc)^0.1
             * (At / A)^0.9
             * sigma

    All correlation inputs must be finite and strictly positive.
    """

    values = [
        throat_diameter,
        gas_dynamic_viscosity,
        gas_specific_heat_cp,
        gas_prandtl_number,
        chamber_pressure,
        characteristic_velocity,
        throat_radius_of_curvature,
        throat_area,
        cross_sectional_area,
        bartz_sigma,
    ]

    if any(
        value is None
        for value
        in values
    ):
        return None

    try:
        (
            throat_diameter_value,
            gas_dynamic_viscosity_value,
            gas_specific_heat_cp_value,
            gas_prandtl_number_value,
            chamber_pressure_value,
            characteristic_velocity_value,
            throat_radius_of_curvature_value,
            throat_area_value,
            cross_sectional_area_value,
            bartz_sigma_value,
        ) = (
            tuple(
                float(
                    value
                )
                for value
                in values
            )
        )

    except (TypeError, ValueError):
        return None

    numeric_values = (
        throat_diameter_value,
        gas_dynamic_viscosity_value,
        gas_specific_heat_cp_value,
        gas_prandtl_number_value,
        chamber_pressure_value,
        characteristic_velocity_value,
        throat_radius_of_curvature_value,
        throat_area_value,
        cross_sectional_area_value,
        bartz_sigma_value,
    )

    if any(
        (
            not math.isfinite(
                value
            )
            or value <= 0.0
        )
        for value
        in numeric_values
    ):
        return None

    return (
        (
            0.026
            / (
                throat_diameter_value
                ** 0.2
            )
        )
        * (
            (
                gas_dynamic_viscosity_value
                ** 0.2
            )
            * gas_specific_heat_cp_value
            / (
                gas_prandtl_number_value
                ** 0.6
            )
        )
        * (
            (
                chamber_pressure_value
                / characteristic_velocity_value
            )
            ** 0.8
        )
        * (
            (
                throat_diameter_value
                / throat_radius_of_curvature_value
            )
            ** 0.1
        )
        * (
            (
                throat_area_value
                / cross_sectional_area_value
            )
            ** 0.9
        )
        * bartz_sigma_value
    )


def calculate_coolant_mass_flow_rate_auto(
        coolant_mass_flow_rate=None,
        fuel_mass_flow_rate=None,
        coolant_flow_fraction=1.0
):
    """
    Auto coolant mass flow.

    For fuel-regenerative cooling:
        mdot_c = mdot_fuel * fraction
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_flow_fraction,
            fuel_mass_flow_rate,
        )
    ):
        return None


    if coolant_mass_flow_rate is not None and coolant_mass_flow_rate > 0:
        return coolant_mass_flow_rate

    if fuel_mass_flow_rate is None or fuel_mass_flow_rate <= 0:
        return None

    if coolant_flow_fraction is None:
        coolant_flow_fraction = 1.0

    if coolant_flow_fraction <= 0:
        return None

    return fuel_mass_flow_rate * coolant_flow_fraction


def calculate_coolant_mass_flow_per_channel(
        coolant_mass_flow_rate=None,
        number_of_coolant_channels=None
):
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_mass_flow_rate,
            number_of_coolant_channels,
        )
    ):
        return None

    if (
        coolant_mass_flow_rate is None
        or number_of_coolant_channels is None
        or coolant_mass_flow_rate <= 0
        or number_of_coolant_channels <= 0
    ):
        return None

    return coolant_mass_flow_rate / number_of_coolant_channels


def calculate_coolant_friction_factor(
        coolant_reynolds_number=None
):
    """
    Darcy coolant friction factor.

    Qualified branches:

    Laminar:
        0 < Re < 2300
        f = 64 / Re

    Transitional / unqualified:
        2300 <= Re < 4000
        No qualified transition correlation is currently owned by LEAF.
        Fail closed by returning None.

    Turbulent smooth-wall Blasius:
        4000 <= Re <= 100000
        f = 0.3164 / Re^0.25

    Above the qualified Blasius range:
        Re > 100000
        Fail closed pending a deliberately sourced broader-range
        smooth/rough-wall friction model.
    """

    if coolant_reynolds_number is None:
        return None

    try:
        reynolds = float(
            coolant_reynolds_number
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            reynolds
        )
        or reynolds <= 0.0
    ):
        return None

    if reynolds < 2300.0:
        return 64.0 / reynolds

    if reynolds < 4000.0:
        return None

    if reynolds <= 100000.0:
        return (
            0.3164
            / (reynolds ** 0.25)
        )

    return None


def calculate_coolant_pressure_drop(
        coolant_friction_factor=None,
        selected_station_length=None,
        coolant_hydraulic_diameter=None,
        coolant_density=None,
        coolant_velocity=None
):
    """
    Darcy-Weisbach coolant pressure drop.

    Equation:
        deltaP = f * (L/Dh) * (rho*v^2/2)
    """
    # PFQ-5 fail-closed scalar containment guard.
    if any(
        value is not None and not _pfq_finite_real(value)
        for value in (
            coolant_density,
            coolant_friction_factor,
            coolant_hydraulic_diameter,
            coolant_velocity,
            selected_station_length,
        )
    ):
        return None


    if (
        coolant_friction_factor is None
        or selected_station_length is None
        or coolant_hydraulic_diameter is None
        or coolant_density is None
        or coolant_velocity is None
        or coolant_friction_factor <= 0
        or selected_station_length <= 0
        or coolant_hydraulic_diameter <= 0
        or coolant_density <= 0
        or coolant_velocity <= 0
    ):
        return None

    return (
        coolant_friction_factor
        * (selected_station_length / coolant_hydraulic_diameter)
        * (0.5 * coolant_density * coolant_velocity ** 2)
    )

# Phase 16W.3 extraction: calculate_selected_station_length_default moved to engine_solver_extracted_helpers.py

# Phase 16W.2 dry-run placeholder: extracted calculate_selected_station_length_default above.


# Phase 16W.10 extraction: calculate_coolant_flow_fraction_default moved to engine_solver_extracted_helpers.py

# Phase 16W.2 dry-run placeholder: extracted calculate_coolant_flow_fraction_default above.

def apply_coolant_database_properties(results):
    coolant_name = results.get("selected_coolant_name")

    if coolant_name in [None, "", "N/A"]:
        coolant_name = (
            results.get("fuel")
            or results.get("fuel_type")
            or results.get("fuel_name")
            or "RP-1 / Kerosene"
        )

    if get_coolant_properties is None:
        return results

    coolant_bulk_temperature = (
        results.get("coolant_bulk_temperature")
        or results.get("coolant_inlet_temperature")
    )

    if coolant_bulk_temperature is None:
        base_coolant = get_coolant_properties(coolant_name)

        if base_coolant is not None:
            coolant_bulk_temperature = base_coolant.get("default_inlet_temperature")

    if get_coolant_properties_at_temperature is not None:
        coolant = get_coolant_properties_at_temperature(
            coolant_name,
            coolant_bulk_temperature
        )
    else:
        coolant = get_coolant_properties(coolant_name)

    if coolant is None:
        return results

    results["selected_coolant_name"] = coolant_name

    if results.get("coolant_inlet_temperature") is None:
        results["coolant_inlet_temperature"] = coolant.get("default_inlet_temperature")

    if results.get("coolant_bulk_temperature") is None:
        results["coolant_bulk_temperature"] = results.get("coolant_inlet_temperature")

    results["coolant_property_temperature"] = (
        coolant.get("property_temperature")
        or results.get("coolant_bulk_temperature")
    )

    results["coolant_density"] = coolant.get("density")
    results["coolant_dynamic_viscosity"] = coolant.get("dynamic_viscosity")
    results["coolant_specific_heat_cp"] = coolant.get("specific_heat_cp")
    results["coolant_thermal_conductivity"] = coolant.get("thermal_conductivity")

    return results

def refresh_coolant_properties_for_temperature(results, temperature_k):
    """
    Updates coolant properties using the temperature-dependent coolant database.

    This is used after the first regen thermal pass so that the coolant-side
    heat-transfer model responds to the heated coolant temperature.
    """

    if results is None:
        return results

    if get_coolant_properties_at_temperature is None:
        return results

    coolant_name = results.get("selected_coolant_name")

    if coolant_name in [None, "", "N/A"]:
        coolant_name = (
            results.get("fuel")
            or results.get("fuel_type")
            or results.get("fuel_name")
            or "RP-1 / Kerosene"
        )

    coolant = get_coolant_properties_at_temperature(
        coolant_name,
        temperature_k
    )

    if coolant is None:
        return results

    results["selected_coolant_name"] = coolant_name
    results["coolant_property_temperature"] = coolant.get(
        "property_temperature",
        temperature_k
    )

    results["coolant_density"] = coolant.get("density")
    results["coolant_dynamic_viscosity"] = coolant.get("dynamic_viscosity")
    results["coolant_specific_heat_cp"] = coolant.get("specific_heat_cp")
    results["coolant_thermal_conductivity"] = coolant.get("thermal_conductivity")

    return results

def recalculate_single_station_regen_chain(
        final_results,
        additional_thermal_resistance=0.0
):
    """
    Recalculates the single-station regen chain after coolant properties change.

    This keeps the current selected-station solver structure, but makes it more
    physically consistent by allowing warmer coolant properties to affect:

    - velocity
    - Reynolds number
    - Prandtl number
    - Nusselt number
    - coolant-side heat-transfer coefficient
    - pressure drop
    - thermal resistance
    - heat flux
    - wall temperatures
    - coolant outlet temperature
    """
    if not isinstance(final_results, dict):
        return None


    final_results["coolant_velocity"] = calculate_coolant_velocity(
        coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
        coolant_density=final_results.get("coolant_density"),
        total_coolant_flow_area=final_results.get("total_coolant_flow_area")
    )

    final_results["coolant_reynolds_number"] = calculate_coolant_reynolds_number(
        coolant_density=final_results.get("coolant_density"),
        coolant_velocity=final_results.get("coolant_velocity"),
        coolant_hydraulic_diameter=final_results.get("coolant_hydraulic_diameter"),
        coolant_dynamic_viscosity=final_results.get("coolant_dynamic_viscosity")
    )

    final_results["coolant_prandtl_number"] = calculate_coolant_prandtl_number(
        coolant_specific_heat_cp=final_results.get("coolant_specific_heat_cp"),
        coolant_dynamic_viscosity=final_results.get("coolant_dynamic_viscosity"),
        coolant_thermal_conductivity=final_results.get("coolant_thermal_conductivity")
    )

    final_results["coolant_nusselt_number"] = calculate_coolant_nusselt_number(
        coolant_reynolds_number=final_results.get("coolant_reynolds_number"),
        coolant_prandtl_number=final_results.get("coolant_prandtl_number")
    )

    final_results["coolant_heat_transfer_coefficient"] = calculate_coolant_heat_transfer_coefficient(
        coolant_nusselt_number=final_results.get("coolant_nusselt_number"),
        coolant_thermal_conductivity=final_results.get("coolant_thermal_conductivity"),
        coolant_hydraulic_diameter=final_results.get("coolant_hydraulic_diameter")
    )

    final_results["coolant_friction_factor"] = calculate_coolant_friction_factor(
        coolant_reynolds_number=final_results.get("coolant_reynolds_number")
    )

    final_results["coolant_pressure_drop"] = calculate_coolant_pressure_drop(
        coolant_friction_factor=final_results.get("coolant_friction_factor"),
        selected_station_length=final_results.get("selected_station_length"),
        coolant_hydraulic_diameter=final_results.get("coolant_hydraulic_diameter"),
        coolant_density=final_results.get("coolant_density"),
        coolant_velocity=final_results.get("coolant_velocity")
    )

    # -------------------------------------------------------------------------
    # Canonical local Bartz / wall-temperature coupling
    # -------------------------------------------------------------------------

    try:
        extra_thermal_resistance = float(
            additional_thermal_resistance
        )

    except (
        TypeError,
        ValueError,
    ):
        extra_thermal_resistance = None


    additional_resistance_valid = (
        extra_thermal_resistance is not None
        and extra_thermal_resistance >= 0
        and extra_thermal_resistance == extra_thermal_resistance
        and abs(extra_thermal_resistance) != float("inf")
    )


    gas_dynamic_viscosity = (
        final_results.get("gas_dynamic_viscosity")
        or final_results.get("cea_selected_viscosity")
    )

    gas_specific_heat_cp = (
        final_results.get("gas_specific_heat_cp")
        or final_results.get("specific_heat_cp")
        or final_results.get("cea_selected_cp")
    )

    gas_prandtl_number = (
        final_results.get("gas_prandtl_number")
        or final_results.get("cea_selected_prandtl")
    )

    throat_radius_of_curvature = (
        final_results.get("throat_radius_of_curvature")
        or final_results.get("radius_3")
    )


    bartz_inputs_ready = (
        additional_resistance_valid

        and not (
            final_results.get("selected_station_length") is not None
            and _pfq_finite_real(final_results.get("selected_station_length"))
            and final_results.get("selected_station_length") <= 0
        )

        and not (
            _pfq_finite_real(final_results.get("coolant_bulk_temperature"))
            and final_results.get("coolant_bulk_temperature") <= 0
        )

        and final_results.get("Gamma") is not None
        and final_results.get("selected_mach_number") is not None
        and final_results.get("chamber_temperature") is not None

        and final_results.get("throat_diameter") is not None

        and gas_dynamic_viscosity is not None
        and gas_specific_heat_cp is not None
        and gas_prandtl_number is not None

        and final_results.get("chamber_pressure") is not None
        and final_results.get("characteristic_velocity") is not None

        and throat_radius_of_curvature is not None

        and final_results.get("throat_area") is not None
        and final_results.get("cross_sectional_area") is not None

        and final_results.get("coolant_heat_transfer_coefficient") is not None
        and final_results.get("hot_gas_wall_thickness") is not None
        and final_results.get("wall_thermal_conductivity") is not None

        and final_results.get("selected_gas_side_recovery_temperature") is not None
        and final_results.get("coolant_bulk_temperature") is not None
    )


    final_results[
        "bartz_coupling_converged"
    ] = False

    final_results[
        "bartz_coupling_iterations"
    ] = 0

    final_results[
        "bartz_coupling_residual"
    ] = None

    final_results[
        "bartz_coupling_status"
    ] = (
        "READY"
        if bartz_inputs_ready
        else "INPUTS_INCOMPLETE"
    )


    def _local_bartz_hg(
        local_sigma,
    ):

        return calculate_bartz_gas_side_heat_transfer_coefficient(
            throat_diameter=final_results.get("throat_diameter"),
            gas_dynamic_viscosity=gas_dynamic_viscosity,
            gas_specific_heat_cp=gas_specific_heat_cp,
            gas_prandtl_number=gas_prandtl_number,
            chamber_pressure=final_results.get("chamber_pressure"),
            characteristic_velocity=final_results.get("characteristic_velocity"),
            throat_radius_of_curvature=throat_radius_of_curvature,
            throat_area=final_results.get("throat_area"),
            cross_sectional_area=final_results.get("cross_sectional_area"),
            bartz_sigma=local_sigma
        )


    def _local_thermal_state(
        local_hg,
    ):

        base_resistance = (
            calculate_regen_total_thermal_resistance(
                hot_gas_heat_transfer_coefficient=local_hg,
                hot_gas_wall_thickness=final_results.get(
                    "hot_gas_wall_thickness"
                ),
                wall_thermal_conductivity=final_results.get(
                    "wall_thermal_conductivity"
                ),
                coolant_heat_transfer_coefficient=final_results.get(
                    "coolant_heat_transfer_coefficient"
                )
            )
        )

        if (
            base_resistance is None
            or base_resistance <= 0
            or not additional_resistance_valid
        ):
            return (
                None,
                None,
                None,
                None,
            )

        effective_resistance = (
            base_resistance
            +
            extra_thermal_resistance
        )

        if effective_resistance <= 0:
            return (
                None,
                None,
                None,
                None,
            )

        local_heat_flux = (
            calculate_regen_heat_flux(
                selected_gas_side_recovery_temperature=final_results.get(
                    "selected_gas_side_recovery_temperature"
                ),
                coolant_bulk_temperature=final_results.get(
                    "coolant_bulk_temperature"
                ),
                regen_total_thermal_resistance=effective_resistance
            )
        )

        local_twg = (
            calculate_hot_gas_side_wall_temperature(
                selected_gas_side_recovery_temperature=final_results.get(
                    "selected_gas_side_recovery_temperature"
                ),
                regen_heat_flux=local_heat_flux,
                hot_gas_heat_transfer_coefficient=local_hg
            )
        )

        return (
            base_resistance,
            effective_resistance,
            local_heat_flux,
            local_twg,
        )


    coupling_applied = False


    if bartz_inputs_ready:

        sigma = 1.0

        hg = _local_bartz_hg(
            sigma
        )

        if (
            hg is None
            or hg <= 0
        ):

            final_results[
                "bartz_coupling_status"
            ] = "INITIAL_BARTZ_UNAVAILABLE"

        else:

            maximum_iterations = 50
            convergence_tolerance = 1.0e-7
            relaxation_factor = 0.5

            final_results[
                "bartz_coupling_status"
            ] = "ITERATING"

            for iteration in range(
                1,
                maximum_iterations + 1,
            ):

                (
                    base_resistance,
                    effective_resistance,
                    heat_flux,
                    twg,
                ) = _local_thermal_state(
                    hg
                )

                if (
                    base_resistance is None
                    or effective_resistance is None
                    or heat_flux is None
                    or twg is None
                ):

                    final_results[
                        "bartz_coupling_status"
                    ] = "THERMAL_STATE_UNAVAILABLE"

                    break


                sigma_target = (
                    calculate_compressibility_correlation_factor(
                        Gamma=final_results.get("Gamma"),
                        selected_mach_number=final_results.get(
                            "selected_mach_number"
                        ),
                        chamber_temperature=final_results.get(
                            "chamber_temperature"
                        ),
                        hot_gas_side_wall_temperature=twg
                    )
                )


                hg_target = (
                    _local_bartz_hg(
                        sigma_target
                    )
                    if sigma_target is not None
                    else None
                )


                if (
                    sigma_target is None
                    or hg_target is None
                    or sigma_target <= 0
                    or hg_target <= 0
                ):

                    final_results[
                        "bartz_coupling_status"
                    ] = "BARTZ_STATE_UNAVAILABLE"

                    break


                sigma_residual = (
                    abs(
                        sigma_target
                        -
                        sigma
                    )
                    /
                    max(
                        abs(
                            sigma_target
                        ),
                        1.0e-12,
                    )
                )

                hg_residual = (
                    abs(
                        hg_target
                        -
                        hg
                    )
                    /
                    max(
                        abs(
                            hg_target
                        ),
                        1.0e-12,
                    )
                )

                residual = max(
                    sigma_residual,
                    hg_residual,
                )


                final_results[
                    "bartz_coupling_iterations"
                ] = iteration

                final_results[
                    "bartz_coupling_residual"
                ] = residual


                if (
                    residual
                    <= convergence_tolerance
                ):

                    sigma = sigma_target
                    hg = hg_target


                    (
                        base_resistance,
                        effective_resistance,
                        heat_flux,
                        twg,
                    ) = _local_thermal_state(
                        hg
                    )


                    sigma_check = (
                        calculate_compressibility_correlation_factor(
                            Gamma=final_results.get("Gamma"),
                            selected_mach_number=final_results.get(
                                "selected_mach_number"
                            ),
                            chamber_temperature=final_results.get(
                                "chamber_temperature"
                            ),
                            hot_gas_side_wall_temperature=twg
                        )
                        if twg is not None
                        else None
                    )


                    hg_check = (
                        _local_bartz_hg(
                            sigma_check
                        )
                        if sigma_check is not None
                        else None
                    )


                    if (
                        sigma_check is None
                        or hg_check is None
                        or base_resistance is None
                        or effective_resistance is None
                        or heat_flux is None
                        or twg is None
                    ):

                        final_results[
                            "bartz_coupling_status"
                        ] = "FINAL_CLOSURE_UNAVAILABLE"

                        break


                    closure_residual = max(
                        abs(
                            sigma_check
                            -
                            sigma
                        )
                        /
                        max(
                            abs(
                                sigma_check
                            ),
                            1.0e-12,
                        ),

                        abs(
                            hg_check
                            -
                            hg
                        )
                        /
                        max(
                            abs(
                                hg_check
                            ),
                            1.0e-12,
                        ),
                    )


                    final_results[
                        "bartz_coupling_residual"
                    ] = closure_residual


                    if (
                        closure_residual
                        <= 1.0e-6
                    ):

                        sigma = sigma_check
                        hg = hg_check


                        (
                            base_resistance,
                            effective_resistance,
                            heat_flux,
                            twg,
                        ) = _local_thermal_state(
                            hg
                        )


                        if (
                            base_resistance is not None
                            and effective_resistance is not None
                            and heat_flux is not None
                            and twg is not None
                        ):

                            final_results[
                                "bartz_sigma"
                            ] = sigma

                            final_results[
                                "compressibility_correlation_factor"
                            ] = sigma

                            final_results[
                                "bartz_gas_side_heat_transfer_coefficient"
                            ] = hg

                            final_results[
                                "hot_gas_heat_transfer_coefficient"
                            ] = hg

                            final_results[
                                "regen_total_thermal_resistance"
                            ] = base_resistance

                            final_results[
                                "regen_effective_heat_flux_resistance"
                            ] = effective_resistance

                            final_results[
                                "regen_heat_flux"
                            ] = heat_flux

                            final_results[
                                "hot_gas_side_wall_temperature"
                            ] = twg

                            final_results[
                                "bartz_coupling_converged"
                            ] = True

                            final_results[
                                "bartz_coupling_status"
                            ] = "CONVERGED"

                            coupling_applied = True

                        else:

                            final_results[
                                "bartz_coupling_status"
                            ] = "FINAL_THERMAL_STATE_UNAVAILABLE"

                    else:

                        final_results[
                            "bartz_coupling_status"
                        ] = "FINAL_CLOSURE_NOT_CONVERGED"


                    break


                sigma = (
                    (1.0 - relaxation_factor)
                    *
                    sigma
                    +
                    relaxation_factor
                    *
                    sigma_target
                )

                hg = (
                    (1.0 - relaxation_factor)
                    *
                    hg
                    +
                    relaxation_factor
                    *
                    hg_target
                )


            else:

                final_results[
                    "bartz_coupling_status"
                ] = "MAX_ITERATIONS_REACHED"


    # -------------------------------------------------------------------------
    # Explicit fallback to the historical thermal chain.
    #
    # This fallback is not labelled as canonical convergence.  The status fields
    # above remain available so downstream validation can distinguish it.
    # -------------------------------------------------------------------------

    if not coupling_applied:

        final_results[
            "regen_total_thermal_resistance"
        ] = calculate_regen_total_thermal_resistance(
            hot_gas_heat_transfer_coefficient=final_results.get(
                "hot_gas_heat_transfer_coefficient"
            ),
            hot_gas_wall_thickness=final_results.get(
                "hot_gas_wall_thickness"
            ),
            wall_thermal_conductivity=final_results.get(
                "wall_thermal_conductivity"
            ),
            coolant_heat_transfer_coefficient=final_results.get(
                "coolant_heat_transfer_coefficient"
            )
        )


        base_resistance = final_results.get(
            "regen_total_thermal_resistance"
        )


        effective_resistance = (
            (
                base_resistance
                +
                extra_thermal_resistance
            )
            if (
                base_resistance is not None
                and additional_resistance_valid
            )
            else None
        )


        final_results[
            "regen_effective_heat_flux_resistance"
        ] = effective_resistance


        final_results[
            "regen_heat_flux"
        ] = calculate_regen_heat_flux(
            selected_gas_side_recovery_temperature=final_results.get(
                "selected_gas_side_recovery_temperature"
            ),
            coolant_bulk_temperature=final_results.get(
                "coolant_bulk_temperature"
            ),
            regen_total_thermal_resistance=effective_resistance
        )


        final_results[
            "hot_gas_side_wall_temperature"
        ] = calculate_hot_gas_side_wall_temperature(
            selected_gas_side_recovery_temperature=final_results.get(
                "selected_gas_side_recovery_temperature"
            ),
            regen_heat_flux=final_results.get(
                "regen_heat_flux"
            ),
            hot_gas_heat_transfer_coefficient=final_results.get(
                "hot_gas_heat_transfer_coefficient"
            )
        )

    final_results["coolant_side_wall_temperature_calculated"] = calculate_coolant_side_wall_temperature_calculated(
        coolant_bulk_temperature=final_results.get("coolant_bulk_temperature"),
        regen_heat_flux=final_results.get("regen_heat_flux"),
        coolant_heat_transfer_coefficient=final_results.get("coolant_heat_transfer_coefficient")
    )

    final_results["local_hot_gas_surface_area"] = calculate_local_hot_gas_surface_area(
        cross_sectional_area=final_results.get("cross_sectional_area"),
        throat_radius=final_results.get("throat_radius"),
        selected_station_length=final_results.get("selected_station_length", 0.001)
    )

    final_results["coolant_temperature_rise"] = calculate_coolant_temperature_rise(
        regen_heat_flux=final_results.get("regen_heat_flux"),
        local_hot_gas_surface_area=final_results.get("local_hot_gas_surface_area"),
        coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
        coolant_specific_heat_cp=final_results.get("coolant_specific_heat_cp")
    )

    final_results["coolant_outlet_temperature"] = calculate_coolant_outlet_temperature(
        coolant_bulk_temperature=final_results.get("coolant_bulk_temperature"),
        coolant_temperature_rise=final_results.get("coolant_temperature_rise")
    )

    final_results["coolant_mean_temperature"] = calculate_coolant_mean_temperature(
        coolant_inlet_temperature=final_results.get("coolant_inlet_temperature"),
        coolant_outlet_temperature=final_results.get("coolant_outlet_temperature"),
        coolant_bulk_temperature=final_results.get("coolant_bulk_temperature")
    )

    final_results["material_temperature_margin"] = calculate_material_temperature_margin(
        material_max_wall_temperature=final_results.get("material_max_wall_temperature"),
        hot_gas_side_wall_temperature=final_results.get("hot_gas_side_wall_temperature")
    )

    return final_results

def calculate_nozzle_radius_at_x(
        x=None,
        radius_3=None,
        throat_radius=None,
        exit_radius=None,
        nozzle_length=None,
        expansion_ratio=None,
        nozzle_geometry_model=None,
        rao_length_fraction=0.8
):
    """
    Returns local nozzle gas radius at axial position x.

    Priority:
    1. Rao bell approximation
    2. Canonical conical linear profile equation
    3. Existing legacy throat-blend fallback
    4. Legacy cross-sectional-area fallback
    """

    if x is None or throat_radius is None:
        return None

    if x <= 0:
        return throat_radius

    if (
        exit_radius is not None
        and nozzle_length is not None
        and nozzle_length > 0
        and x >= nozzle_length
    ):
        return exit_radius

    if str(nozzle_geometry_model).upper() == "RAO_BELL_APPROXIMATION":
        rao_radius = calculate_rao_bell_radius_at_x(
            x=x,
            throat_radius=throat_radius,
            exit_radius=exit_radius,
            nozzle_length=nozzle_length,
            expansion_ratio=expansion_ratio,
            rao_length_fraction=rao_length_fraction,
        )

        if rao_radius is not None:
            return rao_radius

    # Canonical Conical arbitrary-x geometry.
    # Keep this equation identical to build_conical_nozzle_profile().
    if str(nozzle_geometry_model).upper().startswith("CONICAL"):
        if (
            exit_radius is not None
            and nozzle_length is not None
            and nozzle_length > 0
        ):
            x_value = max(
                0.0,
                min(
                    float(x),
                    float(nozzle_length),
                ),
            )
            fraction = (
                x_value
                /
                float(nozzle_length)
            )
            return (
                throat_radius
                +
                fraction
                *
                (
                    exit_radius
                    -
                    throat_radius
                )
            )

    if (
        exit_radius is not None
        and nozzle_length is not None
        and nozzle_length > 0
        and radius_3 is not None
    ):
        blend_length = math.sin(math.radians(15)) * radius_3

        if 0 < x <= blend_length:
            return (
                -math.sqrt(max(radius_3**2 - x**2, 0.0))
                + radius_3
                + throat_radius
            )

        blend_radius = (
            -math.sqrt(max(radius_3**2 - blend_length**2, 0.0))
            + radius_3
            + throat_radius
        )

        remaining_length = nozzle_length - blend_length

        if remaining_length <= 0:
            return exit_radius

        progress = (x - blend_length) / remaining_length
        progress = max(0.0, min(1.0, progress))

        return blend_radius + progress * (exit_radius - blend_radius)

    area = calculate_cross_sectional_area(
        radius_3=radius_3,
        selected_length=x,
        throat_radius=throat_radius,
    )

    if area is None or area <= 0:
        return None

    return math.sqrt(area / math.pi)

def get_regen_coolant_properties(coolant_name, temperature_k=None):
    """
    Unified coolant property lookup.

    Priority:
    1. fluid_property_database.py
    2. legacy coolant_database.py

    This prevents the axial marcher from depending only on the old
    coolant database while LEAF transitions to fluid_property_database.py.
    """

    if get_fluid_properties_at_temperature is not None:
        properties = get_fluid_properties_at_temperature(
            coolant_name,
            temperature_k
        )

        if properties is not None:
            return properties

    if get_coolant_properties_at_temperature is not None:
        properties = get_coolant_properties_at_temperature(
            coolant_name,
            temperature_k
        )

        if properties is not None:
            return properties

    if get_fluid_properties is not None:
        properties = get_fluid_properties(coolant_name)

        if properties is not None:
            return properties

    if get_coolant_properties is not None:
        properties = get_coolant_properties(coolant_name)

        if properties is not None:
            return properties

    return None


DEFAULT_REGEN_AXIAL_STATION_COUNT = 400


def calculate_regen_axial_marching_profile(
    results,
    station_count=DEFAULT_REGEN_AXIAL_STATION_COUNT,
    required_axial_positions=None,
):
    """
    Axial regenerative cooling marching solver.

    Gas-side coordinate:
        x < 0  -> chamber / convergent
        x = 0  -> throat
        x > 0  -> divergent nozzle

    Canonical chamber and active-nozzle geometry form one continuous
    thrust-chamber thermal domain when both profiles are available.

    Geometric x ordering and coolant-path ordering remain independent.

    The legacy coolant direction values remain accepted for compatibility,
    while regen_coolant_flow_direction_effective reports the actual
    full-domain path endpoints.

    Stored output:
        results["regen_axial_profile"]
    """

    if not isinstance(
        results,
        dict,
    ):
        return None

    required_keys = [
        "nozzle_length",
        "radius_3",
        "throat_radius",
        "throat_area",
        "Gamma",
        "chamber_temperature",
        "chamber_pressure",
        "characteristic_velocity",
        "selected_coolant_name",
        "coolant_inlet_temperature",
        "coolant_mass_flow_rate",
        "coolant_channel_width",
        "coolant_channel_height",
        "number_of_coolant_channels",
        "hot_gas_wall_thickness",
        "wall_thermal_conductivity",
    ]

    for key in required_keys:
        if results.get(key) is None:
            return results

    nozzle_length = results.get("nozzle_length")

    if nozzle_length is None or nozzle_length <= 0:
        return results

    try:
        station_count = int(station_count)
    except Exception:
        station_count = DEFAULT_REGEN_AXIAL_STATION_COUNT

    station_count = max(2, min(station_count, 2000))

    required_axial_positions_normalized = []

    if required_axial_positions is not None:
        if isinstance(
            required_axial_positions,
            (
                str,
                bytes,
                dict,
            ),
        ):
            raise ValueError(
                "required_axial_positions must be an iterable "
                "of finite numeric axial coordinates in metres."
            )

        try:
            requested_position_values = list(
                required_axial_positions
            )

        except TypeError as exc:
            raise ValueError(
                "required_axial_positions must be an iterable "
                "of finite numeric axial coordinates in metres."
            ) from exc

        for requested_position in requested_position_values:
            if isinstance(
                requested_position,
                bool,
            ):
                raise ValueError(
                    "required_axial_positions may not contain bool values."
                )

            try:
                requested_x = float(
                    requested_position
                )

            except (
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError(
                    "required_axial_positions must contain only "
                    "numeric axial coordinates in metres."
                ) from exc

            if not math.isfinite(
                requested_x
            ):
                raise ValueError(
                    "required_axial_positions must contain only "
                    "finite axial coordinates."
                )

            if requested_x in required_axial_positions_normalized:
                continue

            required_axial_positions_normalized.append(
                requested_x
            )

        required_axial_positions_normalized.sort()

        for (
            previous_requested_x,
            requested_x,
        ) in zip(
            required_axial_positions_normalized,
            required_axial_positions_normalized[1:],
        ):
            if math.isclose(
                previous_requested_x,
                requested_x,
                rel_tol=0.0,
                abs_tol=1.0e-14,
            ):
                raise ValueError(
                    "required_axial_positions contains distinct "
                    "coordinates closer than the canonical 1e-14 m "
                    "axial matching tolerance."
                )

    required_axial_positions_applied = False

    # -----------------------------------------------------
    # Canonical full thrust-chamber regen domain.
    #
    # Geometry ownership remains external to this march:
    #
    #   build_combustion_chamber_geometry -> chamber_profile
    #   active nozzle owner               -> nozzle profile
    #
    # Coordinate:
    #   chamber   x < 0
    #   throat    x = 0
    #   nozzle    x > 0
    # -----------------------------------------------------

    default_dx = (
        nozzle_length
        /
        max(
            1,
            station_count - 1,
        )
    )

    def normalise_regen_contour(
        profile,
        source_name,
    ):
        points = []

        if not isinstance(
            profile,
            list,
        ):
            return points

        for source_index, item in enumerate(
            profile
        ):
            if not isinstance(
                item,
                dict,
            ):
                continue

            try:
                x_value = float(
                    item.get("x")
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            radius_value = None

            for radius_key in (
                "radius",
                "gas_radius",
                "local_radius",
                "inner_radius",
                "hot_gas_radius",
                "r",
            ):
                try:
                    candidate_radius = float(
                        item.get(
                            radius_key
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if (
                    math.isfinite(
                        candidate_radius
                    )
                    and
                    candidate_radius > 0.0
                ):
                    radius_value = (
                        candidate_radius
                    )
                    break

            if radius_value is None:
                try:
                    local_area = float(
                        item.get(
                            "area"
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    local_area = None

                if (
                    local_area is not None
                    and
                    math.isfinite(
                        local_area
                    )
                    and
                    local_area > 0.0
                ):
                    radius_value = math.sqrt(
                        local_area
                        /
                        math.pi
                    )

            if (
                not math.isfinite(
                    x_value
                )
                or
                radius_value is None
            ):
                continue

            points.append(
                {
                    "x":
                        x_value,

                    "radius":
                        radius_value,

                    "source":
                        source_name,

                    "source_station_index":
                        source_index,
                }
            )

        points.sort(
            key=lambda point:
                point["x"]
        )

        return points

    active_nozzle_model = str(
        results.get(
            "nozzle_geometry_model"
        )
        or
        ""
    ).upper()

    active_nozzle_key = (
        "conical_nozzle_profile"
        if
        active_nozzle_model.startswith(
            "CONICAL"
        )
        else
        "rao_nozzle_profile"
    )

    chamber_contour = (
        normalise_regen_contour(
            results.get(
                "chamber_profile"
            ),
            "chamber_profile",
        )
    )

    nozzle_contour = (
        normalise_regen_contour(
            results.get(
                active_nozzle_key
            ),
            active_nozzle_key,
        )
    )

    canonical_regen_contour = []

    full_thrust_chamber_domain = False

    if (
        chamber_contour
        and
        nozzle_contour
    ):
        chamber_throat = (
            chamber_contour[-1]
        )

        nozzle_throat = (
            nozzle_contour[0]
        )

        throat_x_continuous = (
            math.isclose(
                chamber_throat["x"],
                nozzle_throat["x"],
                rel_tol=1.0e-10,
                abs_tol=1.0e-10,
            )
        )

        throat_radius_continuous = (
            math.isclose(
                chamber_throat["radius"],
                nozzle_throat["radius"],
                rel_tol=1.0e-9,
                abs_tol=1.0e-12,
            )
        )

        if not (
            throat_x_continuous
            and
            throat_radius_continuous
        ):
            results[
                "regen_axial_domain_status"
            ] = (
                "BLOCKED_CANONICAL_THRUST_CHAMBER_"
                "THROAT_DISCONTINUITY"
            )

            results[
                "regen_axial_domain_source"
            ] = (
                f"chamber_profile+"
                f"{active_nozzle_key}"
            )

            return results

        canonical_regen_contour = (
            chamber_contour
            +
            nozzle_contour[1:]
        )

        full_thrust_chamber_domain = True

        results[
            "regen_axial_domain_status"
        ] = (
            "FULL_THRUST_CHAMBER"
        )

        results[
            "regen_axial_domain_source"
        ] = (
            f"chamber_profile+"
            f"{active_nozzle_key}"
        )

    elif nozzle_contour:
        canonical_regen_contour = (
            nozzle_contour
        )

        results[
            "regen_axial_domain_status"
        ] = (
            "NOZZLE_ONLY_CHAMBER_PROFILE_UNAVAILABLE"
        )

        results[
            "regen_axial_domain_source"
        ] = active_nozzle_key

    else:
        fallback_radius_3 = results.get(
            "radius_3"
        )

        if (
            not _pfq_finite_real(
                fallback_radius_3
            )
            or
            fallback_radius_3 <= 0.0
        ):
            results[
                "regen_axial_domain_status"
            ] = (
                "NOZZLE_ONLY_CANONICAL_PROFILE_UNAVAILABLE"
            )

            results[
                "regen_axial_domain_source"
            ] = (
                "legacy_nozzle_radius_evaluation"
            )

            return results

        for fallback_index in range(
            station_count
        ):
            fallback_x = (
                default_dx
                *
                fallback_index
            )

            fallback_radius = (
                calculate_nozzle_radius_at_x(
                    x=fallback_x,
                    radius_3=results.get(
                        "radius_3"
                    ),
                    throat_radius=results.get(
                        "throat_radius"
                    ),
                    exit_radius=results.get(
                        "exit_radius"
                    ),
                    nozzle_length=results.get(
                        "nozzle_length"
                    ),
                    expansion_ratio=results.get(
                        "expansion_ratio"
                    ),
                    nozzle_geometry_model=results.get(
                        "nozzle_geometry_model"
                    ),
                    rao_length_fraction=results.get(
                        "rao_length_fraction",
                        0.8,
                    ),
                )
            )

            if (
                fallback_radius is None
                or
                fallback_radius <= 0.0
            ):
                continue

            canonical_regen_contour.append(
                {
                    "x":
                        fallback_x,

                    "radius":
                        fallback_radius,

                    "source":
                        "legacy_nozzle_radius_evaluation",

                    "source_station_index":
                        fallback_index,
                }
            )

        results[
            "regen_axial_domain_status"
        ] = (
            "NOZZLE_ONLY_CANONICAL_PROFILE_UNAVAILABLE"
        )

        results[
            "regen_axial_domain_source"
        ] = (
            "legacy_nozzle_radius_evaluation"
        )

    if not canonical_regen_contour:
        return results

    # -----------------------------------------------------
    # Regen-owned numerical thermal grid.
    #
    # Canonical chamber/nozzle profiles own physical shape.
    # Their source-point density must not own thermal resolution.
    #
    # The requested axial station count therefore defines the
    # numerical Regen grid while radius is interpolated from the
    # authoritative canonical contour.
    #
    # For a full thrust chamber the throat remains an explicit,
    # exact x=0 station shared by chamber and nozzle regions.
    # -----------------------------------------------------

    if (
        full_thrust_chamber_domain
        and
        len(canonical_regen_contour) >= 3
    ):
        source_regen_contour = list(
            canonical_regen_contour
        )

        thermal_station_count = max(
            3,
            int(station_count),
        )

        x_min = float(
            source_regen_contour[0]["x"]
        )

        x_max = float(
            source_regen_contour[-1]["x"]
        )

        if (
            x_min < 0.0
            and
            x_max > 0.0
        ):
            def interpolate_regen_radius(
                target_x,
            ):
                for source_station in (
                    source_regen_contour
                ):
                    source_x = float(
                        source_station["x"]
                    )

                    if math.isclose(
                        source_x,
                        target_x,
                        rel_tol=0.0,
                        abs_tol=1.0e-14,
                    ):
                        return float(
                            source_station[
                                "radius"
                            ]
                        )

                for (
                    left,
                    right,
                ) in zip(
                    source_regen_contour,
                    source_regen_contour[1:],
                ):
                    left_x = float(
                        left["x"]
                    )

                    right_x = float(
                        right["x"]
                    )

                    if (
                        left_x
                        <=
                        target_x
                        <=
                        right_x
                    ):
                        if math.isclose(
                            left_x,
                            right_x,
                            rel_tol=0.0,
                            abs_tol=1.0e-15,
                        ):
                            return float(
                                right["radius"]
                            )

                        fraction = (
                            (
                                target_x
                                -
                                left_x
                            )
                            /
                            (
                                right_x
                                -
                                left_x
                            )
                        )

                        return (
                            float(
                                left["radius"]
                            )
                            +
                            fraction
                            *
                            (
                                float(
                                    right[
                                        "radius"
                                    ]
                                )
                                -
                                float(
                                    left[
                                        "radius"
                                    ]
                                )
                            )
                        )

                return float(
                    source_regen_contour[-1][
                        "radius"
                    ]
                )

            total_intervals = (
                thermal_station_count
                -
                1
            )

            chamber_length = abs(
                x_min
            )

            nozzle_length_domain = (
                x_max
            )

            full_domain_length = (
                chamber_length
                +
                nozzle_length_domain
            )

            chamber_intervals = int(
                round(
                    total_intervals
                    *
                    chamber_length
                    /
                    full_domain_length
                )
            )

            chamber_intervals = max(
                1,
                min(
                    chamber_intervals,
                    total_intervals - 1,
                ),
            )

            nozzle_intervals = (
                total_intervals
                -
                chamber_intervals
            )

            chamber_x_values = [
                x_min
                +
                (
                    -x_min
                    *
                    grid_index
                    /
                    chamber_intervals
                )
                for grid_index
                in range(
                    chamber_intervals + 1
                )
            ]

            # Floating-point arithmetic must not decide
            # ownership of the common chamber/nozzle throat.
            chamber_x_values[-1] = 0.0

            nozzle_x_values = [
                x_max
                *
                grid_index
                /
                nozzle_intervals
                for grid_index
                in range(
                    1,
                    nozzle_intervals + 1,
                )
            ]

            thermal_x_values = (
                chamber_x_values
                +
                nozzle_x_values
            )

            if required_axial_positions_normalized:
                for requested_x in (
                    required_axial_positions_normalized
                ):
                    if (
                        requested_x < x_min
                        or
                        requested_x > x_max
                    ):
                        raise ValueError(
                            "required_axial_positions contains an "
                            "axial coordinate outside the canonical "
                            "regen domain."
                        )

                enriched_thermal_x_values = []

                for base_x in thermal_x_values:
                    base_x = float(
                        base_x
                    )

                    if any(
                        math.isclose(
                            base_x,
                            requested_x,
                            rel_tol=0.0,
                            abs_tol=1.0e-14,
                        )
                        for requested_x in
                        required_axial_positions_normalized
                    ):
                        continue

                    enriched_thermal_x_values.append(
                        base_x
                    )

                enriched_thermal_x_values.extend(
                    required_axial_positions_normalized
                )

                enriched_thermal_x_values.sort()

                if (
                    len(
                        enriched_thermal_x_values
                    )
                    >
                    2000
                ):
                    raise ValueError(
                        "required_axial_positions would increase the "
                        "effective regen thermal grid above the canonical "
                        "2000-station limit."
                    )

                thermal_x_values = (
                    enriched_thermal_x_values
                )

                required_axial_positions_applied = True

            canonical_regen_contour = [
                {
                    "x":
                        (
                            0.0
                            if
                            abs(
                                float(
                                    x_value
                                )
                            )
                            <
                            1.0e-14
                            else
                            float(
                                x_value
                            )
                        ),

                    "radius":
                        interpolate_regen_radius(
                            0.0
                            if
                            abs(
                                float(
                                    x_value
                                )
                            )
                            <
                            1.0e-14
                            else
                            float(
                                x_value
                            )
                        ),

                    "source":
                        "regen_thermal_grid_interpolation",

                    "source_station_index":
                        thermal_index,
                }

                for (
                    thermal_index,
                    x_value,
                )
                in enumerate(
                    thermal_x_values
                )
            ]

    if (
        required_axial_positions_normalized
        and
        not required_axial_positions_applied
    ):
        raise ValueError(
            "required_axial_positions requires the canonical "
            "full-thrust-chamber regen thermal-grid path."
        )

    # -----------------------------------------------------
    # Local physical axial control volume for every
    # Regen thermal-grid point.
    # -----------------------------------------------------

    for contour_index, contour_station in enumerate(
        canonical_regen_contour
    ):
        x_here = float(
            contour_station["x"]
        )

        if (
            len(canonical_regen_contour)
            ==
            1
        ):
            local_dx = default_dx

        elif contour_index == 0:
            x_next = float(
                canonical_regen_contour[
                    contour_index + 1
                ]["x"]
            )

            local_dx = (
                0.5
                *
                abs(
                    x_next
                    -
                    x_here
                )
            )

        elif (
            contour_index
            ==
            len(canonical_regen_contour) - 1
        ):
            x_previous = float(
                canonical_regen_contour[
                    contour_index - 1
                ]["x"]
            )

            local_dx = (
                0.5
                *
                abs(
                    x_here
                    -
                    x_previous
                )
            )

        else:
            x_previous = float(
                canonical_regen_contour[
                    contour_index - 1
                ]["x"]
            )

            x_next = float(
                canonical_regen_contour[
                    contour_index + 1
                ]["x"]
            )

            local_dx = (
                0.5
                *
                abs(
                    x_next
                    -
                    x_previous
                )
            )

        contour_station[
            "station_dx"
        ] = max(
            local_dx,
            1.0e-12,
        )

    results[
        "regen_axial_full_thrust_chamber"
    ] = (
        full_thrust_chamber_domain
    )

    results[
        "regen_axial_domain_x_min"
    ] = (
        canonical_regen_contour[0]["x"]
    )

    results[
        "regen_axial_domain_x_max"
    ] = (
        canonical_regen_contour[-1]["x"]
    )

    station_count = len(
        canonical_regen_contour
    )

    coolant_flow_direction = results.get(
        "regen_coolant_flow_direction",
        "exit_to_throat"
    )

    if coolant_flow_direction not in ["exit_to_throat", "throat_to_exit"]:
        coolant_flow_direction = "exit_to_throat"

    results["regen_coolant_flow_direction"] = coolant_flow_direction

    if (
        results.get(
            "regen_axial_full_thrust_chamber"
        )
        is True
    ):
        if (
            coolant_flow_direction
            ==
            "exit_to_throat"
        ):
            results[
                "regen_coolant_flow_direction_effective"
            ] = (
                "exit_to_chamber"
            )

            results[
                "regen_coolant_path_start_region"
            ] = (
                "nozzle_exit"
            )

            results[
                "regen_coolant_path_end_region"
            ] = (
                "chamber_head"
            )

        else:
            results[
                "regen_coolant_flow_direction_effective"
            ] = (
                "chamber_to_exit"
            )

            results[
                "regen_coolant_path_start_region"
            ] = (
                "chamber_head"
            )

            results[
                "regen_coolant_path_end_region"
            ] = (
                "nozzle_exit"
            )

    else:
        results[
            "regen_coolant_flow_direction_effective"
        ] = coolant_flow_direction

        results[
            "regen_coolant_path_start_region"
        ] = (
            "nozzle_exit"
            if
            coolant_flow_direction
            ==
            "exit_to_throat"
            else
            "throat"
        )

        results[
            "regen_coolant_path_end_region"
        ] = (
            "throat"
            if
            coolant_flow_direction
            ==
            "exit_to_throat"
            else
            "nozzle_exit"
        )

    single_channel_area = calculate_single_channel_flow_area(
        coolant_channel_width=results.get("coolant_channel_width"),
        coolant_channel_height=results.get("coolant_channel_height")
    )

    total_flow_area = calculate_total_coolant_flow_area(
        single_channel_flow_area=single_channel_area,
        number_of_coolant_channels=results.get("number_of_coolant_channels")
    )

    wetted_perimeter = calculate_coolant_wetted_perimeter(
        coolant_channel_width=results.get("coolant_channel_width"),
        coolant_channel_height=results.get("coolant_channel_height")
    )

    hydraulic_diameter = calculate_coolant_hydraulic_diameter(
        single_channel_flow_area=single_channel_area,
        coolant_wetted_perimeter=wetted_perimeter
    )

    if (
        single_channel_area is None
        or total_flow_area is None
        or wetted_perimeter is None
        or hydraulic_diameter is None
    ):
        return results

    # -----------------------------------------------------
    # Build gas-side stations in physical x order:
    # throat -> exit
    # -----------------------------------------------------

    gas_stations = []

    for index, contour_station in enumerate(canonical_regen_contour):
        dx = contour_station["station_dx"]
        x = contour_station["x"]

        radius = contour_station["radius"]

        if radius is None or radius <= 0:
            continue

        area = math.pi * radius ** 2

        selected_expansion_ratio = calculate_selected_expansion_ratio(
            throat_area=results.get("throat_area"),
            cross_sectional_area=area
        )

        if selected_expansion_ratio is not None and abs(selected_expansion_ratio - 1.0) < 1e-6:
            mach = 1.0
        else:
            mach = calculate_selected_mach_number(
                Gamma=results.get("Gamma"),
                selected_expansion_ratio=selected_expansion_ratio,
                branch=(
                    "subsonic"
                    if x < -1.0e-12
                    else "supersonic"
                ),
            )

        static_temperature = calculate_static_temperature(
            Gamma=results.get("Gamma"),
            selected_mach_number=mach,
            chamber_temperature=results.get("chamber_temperature")
        )

        static_pressure = calculate_static_pressure(
            Gamma=results.get("Gamma"),
            selected_mach_number=mach,
            chamber_pressure=results.get("chamber_pressure")
        )

        adiabatic_wall_temperature = calculate_adiabatic_wall_temperature(
            Gamma=results.get("Gamma"),
            Prandtl=results.get("gas_prandtl_number"),
            cea_selected_prandtl=results.get("cea_selected_prandtl"),
            chamber_temperature=results.get("chamber_temperature"),
            selected_mach_number=mach
        )

        # For the no-film-cooling axial Regen model, the gas-side
        # recovery temperature is the adiabatic-wall temperature.
        #
        # Regenerative cooling is resolved subsequently by the actual
        # gas-film / wall / coolant thermal-resistance circuit; applying
        # an assumed cooling effectiveness here would double-count the
        # coolant's thermal effect.
        recovery_temperature = adiabatic_wall_temperature

        # Neutral initial Bartz seed.
        # The physical sigma is resolved after q'' and Twg become available.
        sigma = 1.0

        gas_dynamic_viscosity = (
            results.get("gas_dynamic_viscosity")
            or results.get("cea_selected_viscosity")
        )

        gas_specific_heat_cp = (
            results.get("gas_specific_heat_cp")
            or results.get("specific_heat_cp")
            or results.get("cea_selected_cp")
        )

        gas_prandtl_number = (
            results.get("gas_prandtl_number")
            or results.get("cea_selected_prandtl")
        )

        throat_diameter = results.get("throat_diameter")

        if throat_diameter is None and results.get("throat_radius") is not None:
            throat_diameter = 2.0 * results.get("throat_radius")

        throat_radius_of_curvature = (
            results.get("throat_radius_of_curvature")
            or results.get("radius_3")
        )

        hg = calculate_bartz_gas_side_heat_transfer_coefficient(
            throat_diameter=throat_diameter,
            gas_dynamic_viscosity=gas_dynamic_viscosity,
            gas_specific_heat_cp=gas_specific_heat_cp,
            gas_prandtl_number=gas_prandtl_number,
            chamber_pressure=results.get("chamber_pressure"),
            characteristic_velocity=results.get("characteristic_velocity"),
            throat_radius_of_curvature=throat_radius_of_curvature,
            throat_area=results.get("throat_area"),
            cross_sectional_area=area,
            bartz_sigma=sigma
        )

        if hg is None:
            hg = results.get("hot_gas_heat_transfer_coefficient")

        surface_area = calculate_local_hot_gas_surface_area(
            cross_sectional_area=area,
            throat_radius=results.get("throat_radius"),
            selected_station_length=dx
        )

        gas_stations.append({
            "station_index": index,
            "station_label": f"Station {index:03d}",
            "x": x,
            "station_dx": dx,
            "radius": radius,
            "area": area,
            "mach": mach,
            "static_temperature": static_temperature,
            "static_pressure": static_pressure,
            "adiabatic_wall_temperature": adiabatic_wall_temperature,
            "recovery_temperature": recovery_temperature,
            "hg": hg,
            "local_hot_gas_surface_area": surface_area,
        })

    if not gas_stations:
        return results

    if coolant_flow_direction == "exit_to_throat":
        march_order = list(reversed(gas_stations))
    else:
        march_order = list(gas_stations)

    coolant_temperature = results.get("coolant_inlet_temperature")

    coolant_pressure = results.get("coolant_inlet_pressure")

    if coolant_pressure is not None:
        try:
            coolant_pressure = float(coolant_pressure)
        except (TypeError, ValueError):
            coolant_pressure = None

    coolant_pressure_drop_total = 0.0
    cumulative_heat_absorbed = 0.0

    marched_by_x = {}

    max_twg = None
    max_twg_x = None

    max_twc = None
    max_twc_x = None

    max_heat_flux = None
    max_heat_flux_x = None

    min_reynolds = None
    min_reynolds_x = None

    max_coolant_temperature = coolant_temperature
    max_coolant_temperature_x = None

    thermal_bottleneck_counts = {
        "gas_side": 0,
        "wall_conduction": 0,
        "coolant_side": 0,
    }

    for coolant_path_index, station in enumerate(march_order):
        dx = station.get("station_dx", default_dx)
        try:
            dx = float(dx)
        except (TypeError, ValueError):
            dx = default_dx
        dx = max(abs(dx), 1.0e-12)
        coolant_temperature_in = coolant_temperature
        coolant_pressure_in = coolant_pressure

        coolant_properties = get_regen_coolant_properties(
            results.get("selected_coolant_name"),
            coolant_temperature_in
        )

        if coolant_properties is None:
            continue

        coolant_density = coolant_properties.get("density")
        coolant_viscosity = coolant_properties.get("dynamic_viscosity")
        coolant_cp = coolant_properties.get("specific_heat_cp")
        coolant_k = coolant_properties.get("thermal_conductivity")

        velocity = calculate_coolant_velocity(
            coolant_mass_flow_rate=results.get("coolant_mass_flow_rate"),
            coolant_density=coolant_density,
            total_coolant_flow_area=total_flow_area
        )

        reynolds = calculate_coolant_reynolds_number(
            coolant_density=coolant_density,
            coolant_velocity=velocity,
            coolant_hydraulic_diameter=hydraulic_diameter,
            coolant_dynamic_viscosity=coolant_viscosity
        )

        prandtl = calculate_coolant_prandtl_number(
            coolant_specific_heat_cp=coolant_cp,
            coolant_dynamic_viscosity=coolant_viscosity,
            coolant_thermal_conductivity=coolant_k
        )

        nusselt = calculate_coolant_nusselt_number(
            coolant_reynolds_number=reynolds,
            coolant_prandtl_number=prandtl
        )

        hc = calculate_coolant_heat_transfer_coefficient(
            coolant_nusselt_number=nusselt,
            coolant_thermal_conductivity=coolant_k,
            coolant_hydraulic_diameter=hydraulic_diameter
        )

        friction_factor = calculate_coolant_friction_factor(
            coolant_reynolds_number=reynolds
        )

        pressure_drop = calculate_coolant_pressure_drop(
            coolant_friction_factor=friction_factor,
            selected_station_length=dx,
            coolant_hydraulic_diameter=hydraulic_diameter,
            coolant_density=coolant_density,
            coolant_velocity=velocity
        )

        if pressure_drop is not None:
            coolant_pressure_drop_total += pressure_drop

            if coolant_pressure is not None:
                coolant_pressure -= pressure_drop

        coolant_pressure_out = coolant_pressure

        resistance = calculate_regen_total_thermal_resistance(
            hot_gas_heat_transfer_coefficient=station.get("hg"),
            hot_gas_wall_thickness=results.get("hot_gas_wall_thickness"),
            wall_thermal_conductivity=results.get("wall_thermal_conductivity"),
            coolant_heat_transfer_coefficient=hc
        )

        resistance_breakdown = calculate_regen_thermal_resistance_breakdown(
            hot_gas_heat_transfer_coefficient=station.get("hg"),
            hot_gas_wall_thickness=results.get("hot_gas_wall_thickness"),
            wall_thermal_conductivity=results.get("wall_thermal_conductivity"),
            coolant_heat_transfer_coefficient=hc
        )

        if resistance_breakdown is None:
            resistance_breakdown = {}

        heat_flux_resistance = resistance

        local_hot_gas_surface_area = (
            station.get(
                "local_hot_gas_surface_area"
            )
        )

        coolant_mass_flow_rate = (
            results.get(
                "coolant_mass_flow_rate"
            )
        )

        if (
            resistance is not None
            and
            local_hot_gas_surface_area
            is not None
            and
            coolant_mass_flow_rate
            is not None
            and
            coolant_cp is not None
            and
            resistance > 0
            and
            local_hot_gas_surface_area > 0
            and
            coolant_mass_flow_rate > 0
            and
            coolant_cp > 0
        ):
            coolant_mean_bulk_coupling_resistance = (
                local_hot_gas_surface_area
                /
                (
                    2.0
                    *
                    coolant_mass_flow_rate
                    *
                    coolant_cp
                )
            )

            heat_flux_resistance = (
                resistance
                +
                coolant_mean_bulk_coupling_resistance
            )

        # Resolve the canonical Bartz / Twg fixed point through the existing
        # single-station thermal owner.
        #
        # The axial march's existing mean-bulk coolant coupling resistance is retained
        # as an additional resistance rather than being removed or duplicated.

        additional_thermal_resistance = 0.0

        if (
            resistance is not None
            and heat_flux_resistance is not None
        ):
            additional_thermal_resistance = (
                heat_flux_resistance
                -
                resistance
            )

            if additional_thermal_resistance < 0:
                additional_thermal_resistance = 0.0


        coupled_station_state = dict(
            results
        )

        coupled_station_state.update({
            "selected_mach_number":
                station.get("mach"),

            "cross_sectional_area":
                (
                    station.get("area")
                    if station.get("area") is not None
                    else station.get("cross_sectional_area")
                ),

            "selected_gas_side_recovery_temperature":
                station.get("recovery_temperature"),

            "coolant_bulk_temperature":
                coolant_temperature_in,

            "coolant_inlet_temperature":
                coolant_temperature_in,

            "selected_station_length":
                dx,

            "coolant_density":
                coolant_density,

            "coolant_dynamic_viscosity":
                coolant_viscosity,

            "coolant_specific_heat_cp":
                coolant_cp,

            "coolant_thermal_conductivity":
                coolant_k,

            "coolant_hydraulic_diameter":
                hydraulic_diameter,

            "total_coolant_flow_area":
                total_flow_area,

            "hot_gas_heat_transfer_coefficient":
                station.get("hg"),

            "bartz_gas_side_heat_transfer_coefficient":
                station.get("hg"),

            "local_hot_gas_surface_area":
                local_hot_gas_surface_area,
        })


        coupled_station_state = (
            recalculate_single_station_regen_chain(
                coupled_station_state,
                additional_thermal_resistance=(
                    additional_thermal_resistance
                )
            )
        )


        if (
            coupled_station_state.get(
                "bartz_coupling_converged"
            )
            is True
        ):

            station["hg"] = (
                coupled_station_state.get(
                    "hot_gas_heat_transfer_coefficient"
                )
            )

            station["sigma"] = (
                coupled_station_state.get(
                    "bartz_sigma"
                )
            )

            station["bartz_sigma"] = (
                coupled_station_state.get(
                    "bartz_sigma"
                )
            )

            station[
                "compressibility_correlation_factor"
            ] = coupled_station_state.get(
                "compressibility_correlation_factor"
            )

            station[
                "bartz_coupling_converged"
            ] = True

            station[
                "bartz_coupling_iterations"
            ] = coupled_station_state.get(
                "bartz_coupling_iterations"
            )

            station[
                "bartz_coupling_residual"
            ] = coupled_station_state.get(
                "bartz_coupling_residual"
            )

            station[
                "bartz_coupling_status"
            ] = coupled_station_state.get(
                "bartz_coupling_status"
            )


            resistance = (
                coupled_station_state.get(
                    "regen_total_thermal_resistance"
                )
            )


            heat_flux_resistance = (
                coupled_station_state.get(
                    "regen_effective_heat_flux_resistance"
                )
            )


            heat_flux = (
                coupled_station_state.get(
                    "regen_heat_flux"
                )
            )


            resistance_breakdown = (
                calculate_regen_thermal_resistance_breakdown(
                    hot_gas_heat_transfer_coefficient=station.get("hg"),
                    hot_gas_wall_thickness=results.get(
                        "hot_gas_wall_thickness"
                    ),
                    wall_thermal_conductivity=results.get(
                        "wall_thermal_conductivity"
                    ),
                    coolant_heat_transfer_coefficient=hc
                )
            )


            if resistance_breakdown is None:
                resistance_breakdown = {}


        else:

            station[
                "bartz_coupling_converged"
            ] = False

            station[
                "bartz_coupling_iterations"
            ] = coupled_station_state.get(
                "bartz_coupling_iterations"
            )

            station[
                "bartz_coupling_residual"
            ] = coupled_station_state.get(
                "bartz_coupling_residual"
            )

            station[
                "bartz_coupling_status"
            ] = coupled_station_state.get(
                "bartz_coupling_status"
            )


            # Explicit legacy thermal fallback.
            # It is not marked as canonical Bartz convergence.
            heat_flux = calculate_regen_heat_flux(
                selected_gas_side_recovery_temperature=station.get(
                    "recovery_temperature"
                ),
                coolant_bulk_temperature=coolant_temperature_in,
                regen_total_thermal_resistance=heat_flux_resistance
            )

        heat_absorbed = None

        if (
            heat_flux is not None
            and
            local_hot_gas_surface_area is not None
            and
            heat_flux > 0
            and
            local_hot_gas_surface_area > 0
        ):
            heat_absorbed = (
                heat_flux
                *
                local_hot_gas_surface_area
            )

        delta_t_coolant = None

        if (
            heat_absorbed is not None
            and
            coolant_mass_flow_rate is not None
            and
            coolant_cp is not None
            and
            coolant_mass_flow_rate > 0
            and
            coolant_cp > 0
        ):
            delta_t_coolant = (
                heat_absorbed
                /
                (
                    coolant_mass_flow_rate
                    *
                    coolant_cp
                )
            )

        coolant_temperature_out = coolant_temperature_in

        if delta_t_coolant is not None:
            coolant_temperature_out = coolant_temperature_in + delta_t_coolant
            cumulative_heat_absorbed += heat_absorbed

        coolant_temperature_mean = 0.5 * (
            coolant_temperature_in + coolant_temperature_out
        )

        twg = calculate_hot_gas_side_wall_temperature(
            selected_gas_side_recovery_temperature=station.get("recovery_temperature"),
            regen_heat_flux=heat_flux,
            hot_gas_heat_transfer_coefficient=station.get("hg")
        )

        twc = calculate_coolant_side_wall_temperature_calculated(
            coolant_bulk_temperature=coolant_temperature_mean,
            regen_heat_flux=heat_flux,
            coolant_heat_transfer_coefficient=hc
        )

        material_margin = calculate_material_temperature_margin(
            material_max_wall_temperature=results.get("material_max_wall_temperature"),
            hot_gas_side_wall_temperature=twg
        )

        x = station.get("x")

        if twg is not None and (max_twg is None or twg > max_twg):
            max_twg = twg
            max_twg_x = x

        if twc is not None and (max_twc is None or twc > max_twc):
            max_twc = twc
            max_twc_x = x

        if heat_flux is not None and (max_heat_flux is None or heat_flux > max_heat_flux):
            max_heat_flux = heat_flux
            max_heat_flux_x = x

        if reynolds is not None and (min_reynolds is None or reynolds < min_reynolds):
            min_reynolds = reynolds
            min_reynolds_x = x

        if (
            coolant_temperature_out is not None
            and max_coolant_temperature is not None
            and coolant_temperature_out > max_coolant_temperature
        ):
            max_coolant_temperature = coolant_temperature_out
            max_coolant_temperature_x = x

        controlling_resistance = resistance_breakdown.get("controlling_thermal_resistance")

        if controlling_resistance in thermal_bottleneck_counts:
            thermal_bottleneck_counts[controlling_resistance] += 1

        station_result = dict(station)

        station_result.update({
            "coolant_path_index": coolant_path_index,
            "coolant_flow_direction": coolant_flow_direction,

            "coolant_temperature": coolant_temperature_out,
            "coolant_temperature_in": coolant_temperature_in,
            "coolant_temperature_out": coolant_temperature_out,
            "coolant_temperature_mean": coolant_temperature_mean,
            "coolant_temperature_rise": delta_t_coolant,

            "coolant_density": coolant_density,
            "coolant_dynamic_viscosity": coolant_viscosity,
            "coolant_specific_heat_cp": coolant_cp,
            "coolant_thermal_conductivity": coolant_k,
            "coolant_velocity": velocity,
            "coolant_reynolds_number": reynolds,
            "coolant_prandtl_number": prandtl,
            "coolant_nusselt_number": nusselt,
            "coolant_heat_transfer_coefficient": hc,

            "friction_factor": friction_factor,
            "station_pressure_drop": pressure_drop,
            "total_pressure_drop_so_far": coolant_pressure_drop_total,
            "coolant_pressure_in": coolant_pressure_in,
            "coolant_pressure_out": coolant_pressure_out,

            "thermal_resistance": resistance,
            "gas_side_thermal_resistance": resistance_breakdown.get("gas_side_resistance"),
            "wall_conduction_thermal_resistance": resistance_breakdown.get("wall_conduction_resistance"),
            "coolant_side_thermal_resistance": resistance_breakdown.get("coolant_side_resistance"),

            "gas_side_resistance_fraction": resistance_breakdown.get("gas_side_resistance_fraction"),
            "wall_conduction_resistance_fraction": resistance_breakdown.get("wall_conduction_resistance_fraction"),
            "coolant_side_resistance_fraction": resistance_breakdown.get("coolant_side_resistance_fraction"),
            "controlling_thermal_resistance": resistance_breakdown.get("controlling_thermal_resistance"),

            "regen_heat_flux": heat_flux,
            "station_heat_absorbed": heat_absorbed,
            "cumulative_heat_absorbed": cumulative_heat_absorbed,

            "hot_gas_side_wall_temperature": twg,
            "coolant_side_wall_temperature": twc,
            "material_temperature_margin": material_margin,
        })

        marched_by_x[x] = station_result

        coolant_temperature = coolant_temperature_out

    profile = []

    for station in gas_stations:
        x = station.get("x")

        if x in marched_by_x:
            profile.append(marched_by_x[x])

    if not profile:
        return results

    coolant_outlet_temperature = coolant_temperature
    coolant_total_temperature_rise = (
        coolant_outlet_temperature - results.get("coolant_inlet_temperature")
        if coolant_outlet_temperature is not None
        and results.get("coolant_inlet_temperature") is not None
        else None
    )

    results["regen_axial_profile"] = profile

    results["regen_axial_station_count"] = len(profile)
    results["regen_axial_coolant_inlet_temperature"] = results.get("coolant_inlet_temperature")
    results["regen_axial_coolant_outlet_temperature"] = coolant_outlet_temperature
    results["regen_axial_coolant_total_temperature_rise"] = coolant_total_temperature_rise

    results["regen_axial_total_pressure_drop"] = coolant_pressure_drop_total
    results["coolant_outlet_pressure"] = coolant_pressure
    results["regen_axial_total_heat_absorbed"] = cumulative_heat_absorbed

    results["regen_axial_thermal_bottleneck_counts"] = thermal_bottleneck_counts

    results["regen_axial_primary_thermal_bottleneck"] = max(
        thermal_bottleneck_counts,
        key=thermal_bottleneck_counts.get
    )

    results["regen_axial_thermal_bottleneck_note"] = (
        "Thermal bottleneck is determined from the largest fraction of "
        "area-normalised thermal resistance: 1/hg, tw/kw, or 1/hc."
    )

    axial_coolant_velocities = [
        float(row["coolant_velocity"])
        for row in profile
        if isinstance(row, dict)
        and isinstance(row.get("coolant_velocity"), (int, float))
        and not isinstance(row.get("coolant_velocity"), bool)
        and math.isfinite(float(row["coolant_velocity"]))
    ]

    results["regen_axial_max_coolant_velocity"] = (
        max(axial_coolant_velocities)
        if axial_coolant_velocities
        else None
    )

    results["regen_axial_max_hot_wall_temperature"] = max_twg
    results["regen_axial_max_hot_wall_temperature_location"] = max_twg_x

    results["regen_axial_max_coolant_wall_temperature"] = max_twc
    results["regen_axial_max_coolant_wall_temperature_location"] = max_twc_x

    results["regen_axial_max_heat_flux"] = max_heat_flux
    results["regen_axial_max_heat_flux_location"] = max_heat_flux_x

    results["regen_axial_min_reynolds_number"] = min_reynolds
    target_reynolds = (
            results.get("regen_derived_target_reynolds_number")
            or results.get("regen_target_reynolds_number")
            or 10000.0
    )

    required_velocity = calculate_required_velocity_for_reynolds(
        target_reynolds_number=target_reynolds,
        coolant_density=results.get("coolant_density"),
        coolant_hydraulic_diameter=hydraulic_diameter,
        coolant_dynamic_viscosity=results.get("coolant_dynamic_viscosity")
    )

    required_flow_area = calculate_required_total_flow_area_for_velocity(
        coolant_mass_flow_rate=results.get("coolant_mass_flow_rate"),
        coolant_density=results.get("coolant_density"),
        target_velocity=required_velocity
    )

    results["regen_target_reynolds_number"] = target_reynolds
    results["regen_required_velocity_for_target_reynolds"] = required_velocity
    results["regen_required_total_flow_area"] = required_flow_area
    results["regen_axial_min_reynolds_number_location"] = min_reynolds_x

    results["regen_axial_max_coolant_temperature"] = max_coolant_temperature
    results["regen_axial_max_coolant_temperature_location"] = max_coolant_temperature_x

    if results.get("material_max_wall_temperature") is not None and max_twg is not None:
        results["regen_axial_material_temperature_margin"] = (
            results.get("material_max_wall_temperature") - max_twg
        )

        results["regen_axial_worst_material_margin"] = (
            results.get("material_max_wall_temperature") - max_twg
        )

        results["regen_axial_worst_material_margin_location"] = max_twg_x

    results["regen_axial_energy_audit_note"] = (
        "Axial heat pickup uses Q_station = q'' * A_hot and "
        "dT = Q_station / (mdot_coolant * Cp_coolant). "
        "Local heat flux is coupled consistently to the station mean "
        "coolant bulk temperature through the analytical station energy "
        "balance. Coolant properties are updated station-by-station."
    )

    return results



def calculate_compressibility_correlation_factor(
        Gamma=None,
        selected_mach_number=None,
        chamber_temperature=None,
        hot_gas_side_wall_temperature=None
):
    """
    Canonical Bartz variable-property correction factor.

    sigma = [
        0.5
        * (Twg / T0)
        * (1 + ((gamma - 1) / 2) * M^2)
        + 0.5
    ]^-0.68
    * [
        1 + ((gamma - 1) / 2) * M^2
    ]^-0.12

    Twg is the actual gas-side wall temperature.
    It is not the adiabatic-wall / recovery temperature.
    """

    if (
        Gamma is None
        or selected_mach_number is None
        or chamber_temperature is None
        or hot_gas_side_wall_temperature is None
    ):
        return None

    try:
        gamma = float(
            Gamma
        )

        mach = float(
            selected_mach_number
        )

        total_temperature = float(
            chamber_temperature
        )

        wall_temperature = float(
            hot_gas_side_wall_temperature
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            gamma
        )
        or not math.isfinite(
            mach
        )
        or not math.isfinite(
            total_temperature
        )
        or not math.isfinite(
            wall_temperature
        )
        or gamma <= 1.0
        or mach < 0.0
        or total_temperature <= 0.0
        or wall_temperature <= 0.0
    ):
        return None

    mach_temperature_factor = (
        1.0
        + (
            (
                gamma - 1.0
            )
            / 2.0
        )
        * mach ** 2
    )

    if (
        not math.isfinite(
            mach_temperature_factor
        )
        or mach_temperature_factor <= 0.0
    ):
        return None

    wall_property_factor = (
        0.5
        * (
            wall_temperature
            / total_temperature
        )
        * mach_temperature_factor
        + 0.5
    )

    if (
        not math.isfinite(
            wall_property_factor
        )
        or wall_property_factor <= 0.0
    ):
        return None

    sigma = (
        wall_property_factor
        ** -0.68
        * mach_temperature_factor
        ** -0.12
    )

    if (
        not math.isfinite(
            sigma
        )
        or sigma <= 0.0
    ):
        return None

    return sigma


def calculate_ambient_pressure(ambient_pressure=None):

    if ambient_pressure is not None:
        return ambient_pressure

    return 101325.0


def calculate_exit_pressure(
        chamber_pressure=None,
        Gamma=None,
        mach_number=None,
        static_pressure=None
):
    """
    Calculates nozzle exit pressure from exit Mach number.
    """

    if chamber_pressure is not None and Gamma is not None and mach_number is not None:
        if not all(math.isfinite(float(value)) for value in (chamber_pressure, Gamma, mach_number)):
            return None
        if chamber_pressure <= 0 or Gamma <= 1 or mach_number < 0:
            return None

        term = 1 + ((Gamma - 1) / 2) * mach_number ** 2
        exponent = -Gamma / (Gamma - 1)

        return chamber_pressure * (term ** exponent)

    if static_pressure is not None:
        return static_pressure

    return None


def calculate_momentum_thrust(mass_flow_rate=None, exhaust_velocity=None):
    if mass_flow_rate is not None and exhaust_velocity is not None:
        return mass_flow_rate * exhaust_velocity

    return None


def calculate_pressure_thrust(exit_pressure=None, ambient_pressure=None, exit_area=None):
    if exit_pressure is not None and ambient_pressure is not None and exit_area is not None:
        return (exit_pressure - ambient_pressure) * exit_area

    return None


def calculate_thrust(
        momentum_thrust=None,
        pressure_thrust=None,
        mass_flow_rate=None,
        exhaust_velocity=None,
        exit_pressure=None,
        ambient_pressure=None,
        exit_area=None
):
    if momentum_thrust is not None and pressure_thrust is not None:
        return momentum_thrust + pressure_thrust

    if (
        mass_flow_rate is not None
        and exhaust_velocity is not None
        and exit_pressure is not None
        and ambient_pressure is not None
        and exit_area is not None
    ):
        return (mass_flow_rate * exhaust_velocity) + ((exit_pressure - ambient_pressure) * exit_area)

    return None


def calculate_specific_impulse(thrust=None, mass_flow_rate=None):
    if thrust is not None and mass_flow_rate is not None:
        if mass_flow_rate == 0:
            return None

        return thrust / (mass_flow_rate * Gravity)

    return None


def calculate_effective_exhaust_velocity(thrust=None, mass_flow_rate=None):
    if thrust is not None and mass_flow_rate is not None:
        if mass_flow_rate == 0:
            return None

        return thrust / mass_flow_rate

    return None


def calculate_thrust_coefficient(thrust=None, chamber_pressure=None, throat_area=None):
    if thrust is not None and chamber_pressure is not None and throat_area is not None:
        denominator = chamber_pressure * throat_area

        if denominator == 0:
            return None

        return thrust / denominator

    return None


def calculate_vacuum_specific_impulse(
        mass_flow_rate=None,
        exhaust_velocity=None,
        exit_pressure=None,
        exit_area=None
):
    if (
        mass_flow_rate is not None
        and exhaust_velocity is not None
        and exit_pressure is not None
        and exit_area is not None
    ):
        if mass_flow_rate == 0:
            return None

        vacuum_thrust = (mass_flow_rate * exhaust_velocity) + (exit_pressure * exit_area)

        return vacuum_thrust / (mass_flow_rate * Gravity)

    return None


def calculate_sea_level_specific_impulse(
        mass_flow_rate=None,
        exhaust_velocity=None,
        exit_pressure=None,
        exit_area=None
):
    if (
        mass_flow_rate is not None
        and exhaust_velocity is not None
        and exit_pressure is not None
        and exit_area is not None
    ):
        if mass_flow_rate == 0:
            return None

        sea_level_thrust = (
            mass_flow_rate * exhaust_velocity
            + ((exit_pressure - Ambient_Pressure) * exit_area)
        )

        return sea_level_thrust / (mass_flow_rate * Gravity)

    return None

def calculate_mixture_ratio(fuel_mass_flow_rate=None, oxidizer_mass_flow_rate=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if fuel_mass_flow_rate is not None and oxidizer_mass_flow_rate is not None:
        if not _finite(fuel_mass_flow_rate, oxidizer_mass_flow_rate):
            return None
        if fuel_mass_flow_rate <= 0 or oxidizer_mass_flow_rate < 0:
            return None

        result = oxidizer_mass_flow_rate / fuel_mass_flow_rate
        return result if _finite(result) and result >= 0 else None

    return None


def calculate_fuel_mass_flow_rate(mass_flow_rate=None, mixture_ratio=None, oxidizer_mass_flow_rate=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if mass_flow_rate is not None and mixture_ratio is not None:
        if not _finite(mass_flow_rate, mixture_ratio):
            return None
        if mass_flow_rate < 0 or mixture_ratio < 0:
            return None

        denominator = 1 + mixture_ratio
        if denominator <= 0:
            return None

        result = mass_flow_rate / denominator
        return result if _finite(result) and result >= 0 else None

    elif oxidizer_mass_flow_rate is not None and mixture_ratio is not None:
        if not _finite(oxidizer_mass_flow_rate, mixture_ratio):
            return None
        if oxidizer_mass_flow_rate < 0 or mixture_ratio <= 0:
            return None

        result = oxidizer_mass_flow_rate / mixture_ratio
        return result if _finite(result) and result >= 0 else None

    return None


def calculate_oxidizer_mass_flow_rate(mass_flow_rate=None, mixture_ratio=None, fuel_mass_flow_rate=None):
    def _finite(*values):
        try:
            return all(math.isfinite(float(value)) for value in values)
        except (TypeError, ValueError, OverflowError):
            return False

    if mass_flow_rate is not None and mixture_ratio is not None:
        if not _finite(mass_flow_rate, mixture_ratio):
            return None
        if mass_flow_rate < 0 or mixture_ratio < 0:
            return None

        denominator = 1 + mixture_ratio
        if denominator <= 0:
            return None

        fuel_component = mass_flow_rate / denominator
        result = mass_flow_rate - fuel_component

        return result if _finite(result) and result >= 0 else None

    elif fuel_mass_flow_rate is not None and mixture_ratio is not None:
        if not _finite(fuel_mass_flow_rate, mixture_ratio):
            return None
        if fuel_mass_flow_rate < 0 or mixture_ratio < 0:
            return None

        result = fuel_mass_flow_rate * mixture_ratio
        return result if _finite(result) and result >= 0 else None

    return None

# =========================================================
# REAL ENGINE CORRECTION MODELS
# =========================================================

def calculate_combustion_efficiency(
        mixture_ratio=None,
        fuel_type="Kerosene"
):
    """
    Simplified combustion efficiency model.

    Represents real combustion losses:
    - imperfect mixing
    - finite burn rates
    - injector inefficiencies
    - unburned fuel
    """

    if mixture_ratio is None:
        return None

    try:
        mixture_ratio_value = float(
            mixture_ratio
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            mixture_ratio_value
        )
        or mixture_ratio_value <= 0.0
    ):
        return None

    if not isinstance(
        fuel_type,
        str,
    ):
        return None

    fuel_type = fuel_type.lower()

    # -----------------------------------------------------
    # KEROSENE / GOX
    # -----------------------------------------------------

    if "kerosene" in fuel_type:

        optimum = 2.7

        deviation = abs(
            mixture_ratio_value
            - optimum
        )

        efficiency = (
            0.98
            - 0.03
            * deviation
        )

        return max(
            0.80,
            min(
                0.98,
                efficiency,
            ),
        )

    # -----------------------------------------------------
    # METHANE / GOX
    # -----------------------------------------------------

    if "methane" in fuel_type:

        optimum = 3.2

        deviation = abs(
            mixture_ratio_value
            - optimum
        )

        efficiency = (
            0.985
            - 0.025
            * deviation
        )

        return max(
            0.82,
            min(
                0.985,
                efficiency,
            ),
        )

    return 0.95



def calculate_mixture_quality_factor(
        mixture_ratio=None,
        fuel_type="Kerosene"
):
    """
    Represents injector mixing quality and combustion completeness.
    """

    if mixture_ratio is None:
        return None

    try:
        mixture_ratio_value = float(
            mixture_ratio
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            mixture_ratio_value
        )
        or mixture_ratio_value <= 0.0
    ):
        return None

    if not isinstance(
        fuel_type,
        str,
    ):
        return None

    fuel_type = fuel_type.lower()

    # -----------------------------------------------------
    # KEROSENE
    # -----------------------------------------------------

    if "kerosene" in fuel_type:

        optimum = 2.7
        width = 1.2

        penalty = (
            (
                mixture_ratio_value
                - optimum
            )
            / width
        ) ** 2

        factor = (
            1.0
            - 0.12
            * penalty
        )

        return max(
            0.70,
            min(
                1.0,
                factor,
            ),
        )

    # -----------------------------------------------------
    # METHANE
    # -----------------------------------------------------

    if "methane" in fuel_type:

        optimum = 3.2
        width = 1.5

        penalty = (
            (
                mixture_ratio_value
                - optimum
            )
            / width
        ) ** 2

        factor = (
            1.0
            - 0.08
            * penalty
        )

        return max(
            0.75,
            min(
                1.0,
                factor,
            ),
        )

    return 1.0



def calculate_soot_risk_factor(
        mixture_ratio=None,
        fuel_type="Kerosene"
):
    """
    0 = no soot risk
    1 = extreme soot/coking risk
    """

    if mixture_ratio is None:
        return None

    try:
        mixture_ratio_value = float(
            mixture_ratio
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            mixture_ratio_value
        )
        or mixture_ratio_value <= 0.0
    ):
        return None

    if not isinstance(
        fuel_type,
        str,
    ):
        return None

    fuel_type = fuel_type.lower()

    if "kerosene" in fuel_type:

        if mixture_ratio_value >= 2.4:
            return 0.0

        if mixture_ratio_value <= 1.2:
            return 1.0

        return (
            2.4
            - mixture_ratio_value
        ) / (
            2.4
            - 1.2
        )

    return 0.0



def calculate_thermal_risk_factor(
        mixture_ratio=None,
        stoichiometric_ratio=3.4
):
    """
    Represents thermal stress tendency.

    0 = cool/safe
    1 = very thermally aggressive
    """

    if mixture_ratio is None:
        return None

    try:
        mixture_ratio_value = float(
            mixture_ratio
        )

        stoichiometric_ratio_value = float(
            stoichiometric_ratio
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            mixture_ratio_value
        )
        or not math.isfinite(
            stoichiometric_ratio_value
        )
        or mixture_ratio_value <= 0.0
        or stoichiometric_ratio_value <= 2.6
    ):
        return None

    if mixture_ratio_value <= 2.6:
        return 0.2

    if (
        mixture_ratio_value
        >= stoichiometric_ratio_value
    ):
        return 1.0

    return (
        0.2
        + 0.8
        * (
            mixture_ratio_value
            - 2.6
        )
        / (
            stoichiometric_ratio_value
            - 2.6
        )
    )



def calculate_corrected_thrust(
        thrust=None,
        combustion_efficiency=None,
        mixture_quality_factor=None
):
    """
    Corrected real-engine thrust estimate.
    """

    if thrust is None:
        return None

    if combustion_efficiency is None:
        combustion_efficiency = 1.0

    if mixture_quality_factor is None:
        mixture_quality_factor = 1.0

    try:
        thrust_value = float(
            thrust
        )

        combustion_efficiency_value = float(
            combustion_efficiency
        )

        mixture_quality_value = float(
            mixture_quality_factor
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            thrust_value
        )
        or not math.isfinite(
            combustion_efficiency_value
        )
        or not math.isfinite(
            mixture_quality_value
        )
        or thrust_value < 0.0
        or combustion_efficiency_value < 0.0
        or combustion_efficiency_value > 1.0
        or mixture_quality_value < 0.0
        or mixture_quality_value > 1.0
    ):
        return None

    return (
        thrust_value
        * combustion_efficiency_value
        * mixture_quality_value
    )



def calculate_corrected_specific_impulse(
        corrected_thrust=None,
        mass_flow_rate=None,
        gravity=9.81
):
    """
    Corrected real-engine Isp.
    """

    if (
        corrected_thrust is None
        or mass_flow_rate is None
        or gravity is None
    ):
        return None

    try:
        corrected_thrust_value = float(
            corrected_thrust
        )

        mass_flow_rate_value = float(
            mass_flow_rate
        )

        gravity_value = float(
            gravity
        )

    except (TypeError, ValueError):
        return None

    if (
        not math.isfinite(
            corrected_thrust_value
        )
        or not math.isfinite(
            mass_flow_rate_value
        )
        or not math.isfinite(
            gravity_value
        )
        or corrected_thrust_value < 0.0
        or mass_flow_rate_value <= 0.0
        or gravity_value <= 0.0
    ):
        return None

    return (
        corrected_thrust_value
        / (
            mass_flow_rate_value
            * gravity_value
        )
    )


# =========================================================
# DIRECTED ENGINE SOLVER
# =========================================================




def calculate_total_propellant_volume_flow_rate(
        fuel_mass_flow_rate=None,
        oxidizer_mass_flow_rate=None,
        fuel_density=None,
        oxidizer_density=None
):
    """
    Total propellant volume flow rate.

    This estimates how much physical propellant volume must pass through
    the feed system per second.

    Equation:
        Vdot_total = mdot_fuel / rho_fuel + mdot_oxidizer / rho_oxidizer

    Units:
        m³/s
    """

    if (
        fuel_mass_flow_rate is None
        or oxidizer_mass_flow_rate is None
        or fuel_density is None
        or oxidizer_density is None
    ):
        return None

    if fuel_density <= 0 or oxidizer_density <= 0:
        return None

    return (
        fuel_mass_flow_rate / fuel_density
        +
        oxidizer_mass_flow_rate / oxidizer_density
    )


def calculate_volumetric_corrected_thrust(
        corrected_thrust=None,
        total_propellant_volume_flow_rate=None
):
    """
    Corrected thrust per required propellant volume flow.

    This is useful for fuel comparison because it includes the storage/feed
    penalty of low-density fuels such as hydrogen.

    Equation:
        F_vol = F_corrected / Vdot_total

    Units:
        N / (m³/s) = N·s/m³
    """

    if (
        corrected_thrust is None
        or total_propellant_volume_flow_rate is None
        or total_propellant_volume_flow_rate <= 0
    ):
        return None

    return corrected_thrust / total_propellant_volume_flow_rate

def calculate_ideal_engine_thrust(thrust=None):
    """
    Ideal engine thrust before empirical real-engine correction factors.

    For now this is equal to the solver's raw thrust value.
    """

    return thrust


def calculate_ideal_engine_specific_impulse(
        ideal_engine_thrust=None,
        mass_flow_rate=None,
        gravity=9.81
):
    """
    Ideal engine specific impulse before correction factors.

    Equation:
        Isp_ideal = F_ideal / (mdot * g0)
    """

    if (
        ideal_engine_thrust is None
        or mass_flow_rate is None
        or mass_flow_rate == 0
    ):
        return None

    return ideal_engine_thrust / (mass_flow_rate * gravity)


def calculate_ideal_volumetric_thrust(
        ideal_engine_thrust=None,
        total_propellant_volume_flow_rate=None
):
    """
    Ideal thrust per total propellant volume flow.

    Equation:
        F_ideal_vol = F_ideal / Vdot_total
    """

    if (
        ideal_engine_thrust is None
        or total_propellant_volume_flow_rate is None
        or total_propellant_volume_flow_rate <= 0
    ):
        return None

    return ideal_engine_thrust / total_propellant_volume_flow_rate

# =========================================================
# CEA-AUTHORITATIVE PERFORMANCE HELPERS
# =========================================================

def first_available_numeric(results, keys):
    """
    Returns the first valid numeric value found in results for any key in keys.
    This lets the solver accept slightly different names from cea_runner.py.
    """

    for key in keys:
        value = results.get(key)

        if isinstance(value, (int, float)) and not math.isnan(value) and not math.isinf(value):
            return value

    return None

def apply_cea_authoritative_thermochemistry(results):
    """
    Forces CEA outputs to overwrite manual/default thermochemistry.

    CEA should own:
    - chamber temperature
    - gamma
    - molecular weight
    - gas constant R
    - gas Cp
    - gas viscosity
    - gas conductivity
    - gas Prandtl number
    """

    if not results.get("cea_authoritative_mode"):
        return results

    cea_gamma = first_available_numeric(results, [
        "cea_selected_gamma",
        "cea_chamber_gamma",
        "cea_throat_gamma",
        "cea_exit_gamma",
    ])

    cea_mw = first_available_numeric(results, [
        "cea_selected_molecular_weight",
        "cea_molecular_weight",
        "cea_chamber_molecular_weight",
        "cea_throat_molecular_weight",
        "cea_exit_molecular_weight",
    ])

    cea_temp = first_available_numeric(results, [
        "cea_chamber_temperature",
        "cea_combustion_temperature",
        "cea_adiabatic_flame_temperature",
    ])

    cea_cp = first_available_numeric(results, [
        "cea_selected_cp",
        "cea_cp_frozen",
        "cea_throat_cp",
        "cea_exit_cp",
    ])

    cea_viscosity = first_available_numeric(results, [
        "cea_selected_viscosity",
        "cea_throat_viscosity",
        "cea_exit_viscosity",
    ])

    cea_conductivity = first_available_numeric(results, [
        "cea_selected_conductivity",
        "cea_throat_conductivity",
        "cea_exit_conductivity",
    ])

    cea_prandtl = first_available_numeric(results, [
        "cea_selected_prandtl",
        "cea_throat_prandtl",
        "cea_exit_prandtl",
        "gas_prandtl_number",
    ])

    if cea_gamma is not None:
        results["Gamma"] = cea_gamma

    if cea_mw is not None and cea_mw > 0:
        results["cea_selected_molecular_weight"] = cea_mw
        results["R"] = Universal_Gas_Constant / cea_mw

    if cea_temp is not None:
        results["chamber_temperature"] = cea_temp

    if cea_cp is not None:
        results["specific_heat_cp"] = cea_cp
        results["gas_specific_heat_cp"] = cea_cp

    if cea_viscosity is not None:
        results["gas_dynamic_viscosity"] = cea_viscosity

    if cea_conductivity is not None:
        results["gas_thermal_conductivity"] = cea_conductivity

    if cea_prandtl is not None:
        results["gas_prandtl_number"] = cea_prandtl

    return results

def apply_cea_authoritative_performance(results):
    """
    When CEA data is available, use direct CEA performance values as the
    authority for engine performance instead of only using simplified
    constant-gamma ideal-gas nozzle reconstruction.

    This keeps manual mode unchanged.

    Supported CEA-like keys include multiple possible names so this works
    even if cea_runner.py labels outputs slightly differently.
    """

    cea_mode_active = bool(results.get("cea_authoritative_mode"))

    has_cea_data = any(
        results.get(key) is not None
        for key in [
            "cea_selected_gamma",
            "cea_selected_molecular_weight",
            "cea_molecular_weight",
            "cea_characteristic_velocity",
            "cea_thrust_coefficient",
            "cea_specific_impulse",
            "cea_vacuum_specific_impulse",
            "cea_exit_velocity",
            "cea_exit_pressure",
        ]
    )

    if not cea_mode_active and not has_cea_data:
        return results

    results["cea_authoritative_used"] = False

    mass_flow_rate = results.get("mass_flow_rate")
    chamber_pressure = results.get("chamber_pressure")
    throat_area = results.get("throat_area")
    exit_area = results.get("exit_area")
    ambient_pressure = results.get("ambient_pressure")

    if ambient_pressure is None:
        ambient_pressure = Ambient_Pressure
        results["ambient_pressure"] = ambient_pressure

    cea_cstar = first_available_numeric(
        results,
        [
            "cea_characteristic_velocity",
            "cea_cstar",
            "cea_c_star",
            "characteristic_velocity_cea",
            "cstar",
            "c_star",
        ]
    )

    cea_cf = first_available_numeric(
        results,
        [
            "cea_thrust_coefficient",
            "cea_cf",
            "thrust_coefficient_cea",
            "cf",
        ]
    )

    cea_isp = first_available_numeric(
        results,
        [
            "cea_specific_impulse",
            "cea_isp",
            "specific_impulse_cea",
            "isp",
        ]
    )

    cea_vac_isp = first_available_numeric(
        results,
        [
            "cea_vacuum_specific_impulse",
            "cea_isp_vac",
            "vacuum_specific_impulse_cea",
            "isp_vac",
        ]
    )

    cea_exit_velocity = first_available_numeric(
        results,
        [
            "cea_exit_velocity",
            "cea_exhaust_velocity",
            "exhaust_velocity_cea",
            "exit_velocity",
        ]
    )

    cea_exit_pressure = first_available_numeric(
        results,
        [
            "cea_exit_pressure",
            "exit_pressure_cea",
            "pe",
        ]
    )

    cea_chamber_temperature = first_available_numeric(
        results,
        [
            "cea_chamber_temperature",
            "cea_combustion_temperature",
            "cea_adiabatic_flame_temperature",
            "combustion_temperature",
            "adiabatic_flame_temperature",
        ]
    )

    if cea_chamber_temperature is not None:
        results["chamber_temperature"] = cea_chamber_temperature

    if cea_cstar is not None:
        results["characteristic_velocity"] = cea_cstar

        if (
            mass_flow_rate is None
            and chamber_pressure is not None
            and throat_area is not None
            and cea_cstar > 0
        ):
            mass_flow_rate = (chamber_pressure * throat_area) / cea_cstar
            results["mass_flow_rate"] = mass_flow_rate

    if cea_exit_pressure is not None:
        results["exit_pressure"] = cea_exit_pressure

    if cea_exit_velocity is not None:
        results["exhaust_velocity"] = cea_exit_velocity

    if cea_cf is not None:
        results["thrust_coefficient"] = cea_cf

        if (
            chamber_pressure is not None
            and throat_area is not None
        ):
            results["thrust"] = cea_cf * chamber_pressure * throat_area
            results["cea_authoritative_used"] = True

            if mass_flow_rate is not None and mass_flow_rate > 0:
                results["specific_impulse"] = results["thrust"] / (mass_flow_rate * Gravity)
                results["effective_exhaust_velocity"] = results["thrust"] / mass_flow_rate

    elif cea_isp is not None:
        results["specific_impulse"] = cea_isp

        if mass_flow_rate is not None:
            results["thrust"] = cea_isp * mass_flow_rate * Gravity
            results["cea_authoritative_used"] = True
            results["effective_exhaust_velocity"] = results["thrust"] / mass_flow_rate

    elif cea_exit_velocity is not None:
        if (
            mass_flow_rate is not None
            and exit_area is not None
            and results.get("exit_pressure") is not None
        ):
            results["momentum_thrust"] = mass_flow_rate * cea_exit_velocity
            results["pressure_thrust"] = (
                results["exit_pressure"] - ambient_pressure
            ) * exit_area
            results["thrust"] = results["momentum_thrust"] + results["pressure_thrust"]
            results["cea_authoritative_used"] = True
            if mass_flow_rate > 0:
                results["specific_impulse"] = results["thrust"] / (mass_flow_rate * Gravity)
                results["effective_exhaust_velocity"] = results["thrust"] / mass_flow_rate

    if cea_vac_isp is not None:
        results["vacuum_specific_impulse"] = cea_vac_isp

    if (
        results.get("thrust") is not None
        and chamber_pressure is not None
        and throat_area is not None
        and chamber_pressure * throat_area != 0
    ):
        results["thrust_coefficient"] = results["thrust"] / (chamber_pressure * throat_area)

    if (
        results.get("exhaust_velocity") is None
        and results.get("effective_exhaust_velocity") is not None
    ):
        results["exhaust_velocity"] = results["effective_exhaust_velocity"]

    return results

def module_execution_enabled(module_execution_policy, module_id):
    """Return whether an engineering module may derive values in this run."""
    if module_execution_policy is None:
        return True

    return module_execution_policy.get(module_id) is True


def solve_engine(inputs, module_execution_policy=None):
    """
    Directed rocket engine physics solver.

    This replaces circular iterative solving with a staged
    propulsion calculation pipeline.

    Physics flow:

    Inputs
    -> Combustion
    -> Geometry
    -> Exit Conditions
    -> Thrust
    -> Performance
    """

    results = dict(inputs)

    combustion_chamber_active = module_execution_enabled(
        module_execution_policy, "combustion_chamber"
    )
    nozzle_active = module_execution_enabled(
        module_execution_policy, "nozzle"
    )
    regen_active = module_execution_enabled(
        module_execution_policy, "regen"
    )

    # =====================================================
    # THERMODYNAMIC PROPERTY CONSISTENCY
    # =====================================================

    results = solve_thermodynamic_properties(results)
    results = apply_cea_authoritative_thermochemistry(results)
    results = solve_thermodynamic_properties(results)

    # =====================================================
    # CEA PERFORMANCE AUTHORITY — EARLY PASS
    # =====================================================

    results = apply_cea_authoritative_performance(results)

    # =====================================================
    # STAGE 1 — BASIC DEFAULTS
    # =====================================================

    if results.get("ambient_pressure") is None:
        results["ambient_pressure"] = 101325.0

    # =====================================================
    # STAGE 2 — GEOMETRY
    # =====================================================

    if nozzle_active:
        # Expansion ratio
        if (
            results.get("expansion_ratio") is None
            and results.get("throat_area") is not None
            and results.get("exit_area") is not None
        ):

            results["expansion_ratio"] = (
                calculate_expansion_ratio(
                    throat_area=results["throat_area"],
                    exit_area=results["exit_area"]
                )
            )

        # Exit area
        if (
            results.get("exit_area") is None
            and results.get("throat_area") is not None
            and results.get("expansion_ratio") is not None
        ):

            results["exit_area"] = (
                results["throat_area"]
                * results["expansion_ratio"]
            )

        # Throat radius
        if (
            results.get("throat_radius") is None
            and results.get("throat_area") is not None
        ):

            results["throat_radius"] = (
                calculate_throat_radius(
                    throat_area=results["throat_area"]
                )
            )

        # Exit radius
        if (
            results.get("exit_radius") is None
            and results.get("exit_area") is not None
        ):

            results["exit_radius"] = (
                calculate_exit_radius(
                    exit_area=results["exit_area"]
                )
            )

        # Radius 2
        if (
            results.get("radius_2") is None
            and results.get("throat_radius") is not None
        ):
            results["radius_2"] = calculate_radius_2(
                throat_radius=results["throat_radius"]
            )

        # Radius 3
        if (
            results.get("radius_3") is None
            and results.get("throat_radius") is not None
        ):
            results["radius_3"] = calculate_radius_3(
                throat_radius=results["throat_radius"]
            )

        # Active nozzle geometry model
        if results.get("nozzle_geometry_model") is None:
            results["nozzle_geometry_model"] = "RAO_BELL_APPROXIMATION"

        if results.get("conical_half_angle_deg") is None:
            results["conical_half_angle_deg"] = 15.0

        if results.get("rao_length_fraction") is None:
            results["rao_length_fraction"] = 0.8

        active_nozzle_model = str(results.get("nozzle_geometry_model")).upper()

        if active_nozzle_model == "CONICAL":
            results = build_conical_nozzle_profile(
                results,
                station_count=100,
            )
        else:
            results = build_rao_nozzle_profile(
                results,
                station_count=100,
            )

        results = evaluate_nozzle_geometry_smoothness(results)

        # Selected station area from active nozzle geometry profile
        # IMPORTANT:
        # Always recompute this after geometry model selection.
        # Otherwise switching Rao/Conical leaves stale area and Mach values.
        if results.get("selected_length") is not None:
            local_radius = calculate_nozzle_radius_at_x(
                x=results.get("selected_length"),
                radius_3=results.get("radius_3"),
                throat_radius=results.get("throat_radius"),
                exit_radius=results.get("exit_radius"),
                nozzle_length=results.get("nozzle_length"),
                expansion_ratio=results.get("expansion_ratio"),
                nozzle_geometry_model=results.get("nozzle_geometry_model"),
                rao_length_fraction=results.get("rao_length_fraction", 0.8),
            )

            if local_radius is not None:
                results["cross_sectional_area"] = math.pi * local_radius ** 2
                results["selected_nozzle_radius"] = local_radius

                results["selected_expansion_ratio"] = calculate_selected_expansion_ratio(
                    throat_area=results.get("throat_area"),
                    cross_sectional_area=results.get("cross_sectional_area"),
                )

                results["selected_mach_number"] = calculate_selected_mach_number(
                    Gamma=results.get("Gamma"),
                    selected_expansion_ratio=results.get("selected_expansion_ratio"),
                )

    if combustion_chamber_active:
        results = build_combustion_chamber_geometry(
            results,
            module_execution_policy=module_execution_policy,
        )

    if regen_active:
        results = build_geometry_aware_recommended_regen_design(results)

    if combustion_chamber_active:
        # =====================================================
        # STAGE 3 — MIXTURE FLOW SPLIT
        # =====================================================

        if (
            results.get("fuel_mass_flow_rate") is None
            and results.get("mass_flow_rate") is not None
            and results.get("mixture_ratio") is not None
        ):

            results["fuel_mass_flow_rate"] = (
                calculate_fuel_mass_flow_rate(
                    mass_flow_rate=results["mass_flow_rate"],
                    mixture_ratio=results["mixture_ratio"]
                )
            )

        if (
            results.get("oxidizer_mass_flow_rate") is None
            and results.get("mass_flow_rate") is not None
            and results.get("mixture_ratio") is not None
        ):

            results["oxidizer_mass_flow_rate"] = (
                calculate_oxidizer_mass_flow_rate(
                    mass_flow_rate=results["mass_flow_rate"],
                    mixture_ratio=results["mixture_ratio"]
                )
            )

        # =====================================================
        # STAGE 4 — CHARACTERISTIC VELOCITY
        # =====================================================

        if (
            results.get("characteristic_velocity") is None
            and results.get("Gamma") is not None
            and results.get("R") is not None
            and results.get("chamber_temperature") is not None
        ):

            results["characteristic_velocity"] = (
                calculate_characteristic_velocity(
                    chamber_temperature=results["chamber_temperature"],
                    Gamma=results["Gamma"],
                    R=results["R"]
                )
            )

        # =====================================================
        # STAGE 4B — MASS FLOW RATE
        # =====================================================

        if (
            results.get("mass_flow_rate") is None
            and results.get("chamber_pressure") is not None
            and results.get("throat_area") is not None
            and results.get("characteristic_velocity") is not None
        ):

            results["mass_flow_rate"] = (
                calculate_mass_flow_rate(
                    chamber_pressure=results["chamber_pressure"],
                    throat_area=results["throat_area"],
                    characteristic_velocity=results["characteristic_velocity"]
                )
            )

    if nozzle_active:
        # =====================================================
        # STAGE 5 — EXIT MACH NUMBER
        # =====================================================

        if (
            results.get("mach_number") is None
            and results.get("Gamma") is not None
            and results.get("expansion_ratio") is not None
        ):

            results["mach_number"] = (
                calculate_selected_mach_number(
                    Gamma=results["Gamma"],
                    selected_expansion_ratio=results["expansion_ratio"],
                    branch="supersonic",
                )
            )

        # =====================================================
        # STAGE 5B — SELECTED / LOCAL NOZZLE AREA RATIO
        # =====================================================

        if (
            results.get("selected_expansion_ratio") is None
            and results.get("throat_area") is not None
            and results.get("cross_sectional_area") is not None
        ):

            results["selected_expansion_ratio"] = (
                calculate_selected_expansion_ratio(
                    throat_area=results["throat_area"],
                    cross_sectional_area=results["cross_sectional_area"]
                )
            )

        # =====================================================
        # STAGE 5C — SELECTED / LOCAL MACH NUMBER
        # =====================================================

        if (
            results.get("selected_mach_number") is None
            and results.get("Gamma") is not None
            and results.get("selected_expansion_ratio") is not None
        ):

            results["selected_mach_number"] = (
                calculate_selected_mach_number(
                    Gamma=results["Gamma"],
                    selected_expansion_ratio=results["selected_expansion_ratio"]
                )
            )

        # =====================================================
        # STAGE 5D — LOCAL STATIC TEMPERATURE
        # =====================================================

        if (
            results.get("static_temperature") is None
            and results.get("Gamma") is not None
            and results.get("selected_mach_number") is not None
            and results.get("chamber_temperature") is not None
        ):

            results["static_temperature"] = (
                calculate_static_temperature(
                    Gamma=results["Gamma"],
                    selected_mach_number=results["selected_mach_number"],
                    chamber_temperature=results["chamber_temperature"]
                )
            )

        # =====================================================
        # STAGE 5E — LOCAL STATIC PRESSURE
        # =====================================================

        if (
            results.get("static_pressure") is None
            and results.get("Gamma") is not None
            and results.get("selected_mach_number") is not None
            and results.get("chamber_pressure") is not None
        ):

            results["static_pressure"] = (
                calculate_static_pressure(
                    Gamma=results["Gamma"],
                    selected_mach_number=results["selected_mach_number"],
                    chamber_pressure=results["chamber_pressure"]
                )
            )

        # =====================================================
        # STAGE 5F — LOCAL STATIC DENSITY
        # =====================================================

        if (
            results.get("static_density") is None
            and results.get("R") is not None
            and results.get("static_temperature") is not None
            and results.get("static_pressure") is not None
        ):

            results["static_density"] = (
                calculate_static_density(
                    R=results["R"],
                    static_temperature=results["static_temperature"],
                    static_pressure=results["static_pressure"]
                )
            )

        # =====================================================
        # STAGE 6 — EXIT PRESSURE
        # =====================================================

        if (
            results.get("exit_pressure") is None
            and results.get("chamber_pressure") is not None
            and results.get("Gamma") is not None
            and results.get("mach_number") is not None
        ):

            results["exit_pressure"] = (
                calculate_exit_pressure(
                    chamber_pressure=results["chamber_pressure"],
                    Gamma=results["Gamma"],
                    mach_number=results["mach_number"]
                )
            )

    # =====================================================
    # STAGE 7 — EXIT VELOCITY
    # =====================================================

    if (
        results.get("exhaust_velocity") is None
        and results.get("chamber_temperature") is not None
        and results.get("Gamma") is not None
        and results.get("R") is not None
        and results.get("mach_number") is not None
    ):

        results["exhaust_velocity"] = (
            calculate_exhaust_velocity(
                chamber_temperature=results["chamber_temperature"],
                mach_number=results["mach_number"],
                Gamma=results["Gamma"],
                R=results["R"]
            )
        )

    # =====================================================
    # STAGE 8 — MOMENTUM THRUST
    # =====================================================

    if (
        results.get("momentum_thrust") is None
        and results.get("mass_flow_rate") is not None
        and results.get("exhaust_velocity") is not None
    ):

        results["momentum_thrust"] = (
            calculate_momentum_thrust(
                mass_flow_rate=results["mass_flow_rate"],
                exhaust_velocity=results["exhaust_velocity"]
            )
        )

    # =====================================================
    # STAGE 9 — PRESSURE THRUST
    # =====================================================

    if (
        results.get("pressure_thrust") is None
        and results.get("exit_pressure") is not None
        and results.get("ambient_pressure") is not None
        and results.get("exit_area") is not None
    ):

        results["pressure_thrust"] = (
            calculate_pressure_thrust(
                exit_pressure=results["exit_pressure"],
                ambient_pressure=results["ambient_pressure"],
                exit_area=results["exit_area"]
            )
        )

    # =====================================================
    # STAGE 10 — TOTAL THRUST
    # =====================================================

    if (
        results.get("thrust") is None
        and results.get("momentum_thrust") is not None
        and results.get("pressure_thrust") is not None
    ):

        results["thrust"] = (
            results["momentum_thrust"]
            + results["pressure_thrust"]
        )

    # =====================================================
    # STAGE 11 — ISP
    # =====================================================

    if (
        results.get("specific_impulse") is None
        and results.get("thrust") is not None
        and results.get("mass_flow_rate") is not None
    ):

        results["specific_impulse"] = (
            calculate_specific_impulse(
                thrust=results["thrust"],
                mass_flow_rate=results["mass_flow_rate"]
            )
        )

    # =====================================================
    # STAGE 12 — EFFECTIVE EXHAUST VELOCITY
    # =====================================================

    if (
        results.get("effective_exhaust_velocity") is None
        and results.get("thrust") is not None
        and results.get("mass_flow_rate") is not None
    ):

        results["effective_exhaust_velocity"] = (
            calculate_effective_exhaust_velocity(
                thrust=results["thrust"],
                mass_flow_rate=results["mass_flow_rate"]
            )
        )

    # =====================================================
    # STAGE 12B — VACUUM AND SEA-LEVEL ISP
    # =====================================================

    if (
        results.get("vacuum_specific_impulse") is None
        and results.get("mass_flow_rate") is not None
        and results.get("exhaust_velocity") is not None
        and results.get("exit_pressure") is not None
        and results.get("exit_area") is not None
    ):

        results["vacuum_specific_impulse"] = (
            calculate_vacuum_specific_impulse(
                mass_flow_rate=results["mass_flow_rate"],
                exhaust_velocity=results["exhaust_velocity"],
                exit_pressure=results["exit_pressure"],
                exit_area=results["exit_area"]
            )
        )

    if (
        results.get("sea_level_specific_impulse") is None
        and results.get("mass_flow_rate") is not None
        and results.get("exhaust_velocity") is not None
        and results.get("exit_pressure") is not None
        and results.get("exit_area") is not None
    ):

        results["sea_level_specific_impulse"] = (
            calculate_sea_level_specific_impulse(
                mass_flow_rate=results["mass_flow_rate"],
                exhaust_velocity=results["exhaust_velocity"],
                exit_pressure=results["exit_pressure"],
                exit_area=results["exit_area"]
            )
        )

    # =====================================================
    # STAGE 12C — CEA PERFORMANCE AUTHORITY FINAL PASS
    # =====================================================

    #results = apply_cea_authoritative_performance(results)

    # =====================================================
    # STAGE 13 — THRUST COEFFICIENT
    # =====================================================

    if (
        results.get("thrust_coefficient") is None
        and results.get("thrust") is not None
        and results.get("chamber_pressure") is not None
        and results.get("throat_area") is not None
    ):

        results["thrust_coefficient"] = (
            calculate_thrust_coefficient(
                thrust=results["thrust"],
                chamber_pressure=results["chamber_pressure"],
                throat_area=results["throat_area"]
            )
        )

    if regen_active:
        # =====================================================
        # STAGE 13B — ADIABATIC WALL TEMPERATURE
        # =====================================================

        if (
            results.get("adiabatic_wall_temperature") is None
            and results.get("Gamma") is not None
            and results.get("chamber_temperature") is not None
            and results.get("selected_mach_number") is not None
        ):

            results["adiabatic_wall_temperature"] = (
                calculate_adiabatic_wall_temperature(
                    Gamma=results["Gamma"],
                    Prandtl=results.get("gas_prandtl_number"),
                    cea_selected_prandtl=results.get("cea_selected_prandtl"),
                    chamber_temperature=results["chamber_temperature"],
                    selected_mach_number=results["selected_mach_number"]
                )
            )

        # =====================================================
        # STAGE 13C — BARTZ COMPRESSIBILITY CORRELATION FACTOR
        # =====================================================

        # Canonical Bartz sigma is deferred until Twg exists.
        # The coupled station owner resolves the physical sigma downstream.
        pass

        # =====================================================
        # STAGE 13D — SELECTED GAS SIDE RECOVERY TEMPERATURE
        # =====================================================

        if (
            results.get("selected_gas_side_recovery_temperature") is None
            and results.get("adiabatic_wall_temperature") is not None
        ):
            # Canonical no-film-cooling gas-side recovery temperature.
            # Regenerative cooling is resolved by the downstream
            # thermal-resistance circuit and must not be pre-applied here.
            results["selected_gas_side_recovery_temperature"] = (
                results["adiabatic_wall_temperature"]
            )

    # =====================================================
    # STAGE 14 — REAL ENGINE CORRECTION FACTORS
    # =====================================================

    if combustion_chamber_active:
        if results.get("combustion_efficiency") is None:
            results["combustion_efficiency"] = calculate_combustion_efficiency(
                mixture_ratio=results.get("mixture_ratio"),
                fuel_type=results.get("fuel_type", "Kerosene")
            )

        if results.get("mixture_quality_factor") is None:
            results["mixture_quality_factor"] = calculate_mixture_quality_factor(
                mixture_ratio=results.get("mixture_ratio"),
                fuel_type=results.get("fuel_type", "Kerosene")
            )

        if results.get("soot_risk_factor") is None:
            results["soot_risk_factor"] = calculate_soot_risk_factor(
                mixture_ratio=results.get("mixture_ratio"),
                fuel_type=results.get("fuel_type", "Kerosene")
            )

    if regen_active and results.get("thermal_risk_factor") is None:
        results["thermal_risk_factor"] = calculate_thermal_risk_factor(
            mixture_ratio=results.get("mixture_ratio")
        )

    if results.get("corrected_thrust") is None:
        results["corrected_thrust"] = calculate_corrected_thrust(
            thrust=results.get("thrust"),
            combustion_efficiency=results.get("combustion_efficiency"),
            mixture_quality_factor=results.get("mixture_quality_factor")
        )

    if results.get("corrected_specific_impulse") is None:
        results["corrected_specific_impulse"] = calculate_corrected_specific_impulse(
            corrected_thrust=results.get("corrected_thrust"),
            mass_flow_rate=results.get("mass_flow_rate")
        )

    return results

SOLVER_DEBUG = False
LEGACY_MAX_ITERATIONS = 8
LEGACY_FALLBACK_ENABLED = True

def legacy_iterative_solver(
        params,
        *,
        max_iterations=LEGACY_MAX_ITERATIONS,
        keep_history=False,
        debug=SOLVER_DEBUG,
        module_execution_policy=None,
):
    functions = {
        "mass_flow_rate": calculate_mass_flow_rate,
        "mixture_ratio": calculate_mixture_ratio,
        "fuel_mass_flow_rate": calculate_fuel_mass_flow_rate,
        "oxidizer_mass_flow_rate": calculate_oxidizer_mass_flow_rate,
        "throat_area": calculate_throat_area,
        "exit_area": calculate_exit_area,
        "expansion_ratio": calculate_expansion_ratio,
        "selected_expansion_ratio": calculate_selected_expansion_ratio,
        "nozzle_length": calculate_nozzle_length,
        "cross_sectional_area": calculate_cross_sectional_area,
        "throat_radius": calculate_throat_radius,
        "exit_radius": calculate_exit_radius,
        "radius_2": calculate_radius_2,
        "radius_3": calculate_radius_3,
        "chamber_temperature": calculate_chamber_temperature,
        "chamber_pressure": calculate_chamber_pressure,
        "static_temperature": calculate_static_temperature,
        "static_pressure": calculate_static_pressure,
        "static_density": calculate_static_density,
        "estimated_residence_time": calculate_estimated_residence_time,
        "characteristic_length": calculate_characteristic_length,
        "characteristic_velocity": calculate_characteristic_velocity,
        "exhaust_velocity": calculate_exhaust_velocity,
        "ambient_pressure": calculate_ambient_pressure,
        "exit_pressure": calculate_exit_pressure,
        "momentum_thrust": calculate_momentum_thrust,
        "pressure_thrust": calculate_pressure_thrust,
        "thrust": calculate_thrust,
        "specific_impulse": calculate_specific_impulse,
        "vacuum_specific_impulse": calculate_vacuum_specific_impulse,
        "sea_level_specific_impulse": calculate_sea_level_specific_impulse,
        "effective_exhaust_velocity": calculate_effective_exhaust_velocity,
        "thrust_coefficient": calculate_thrust_coefficient,
        "mach_number": calculate_mach_number,
        "selected_mach_number": calculate_selected_mach_number,
        "adiabatic_wall_temperature": calculate_adiabatic_wall_temperature,
        "compressibility_correlation_factor": calculate_compressibility_correlation_factor
    }

    module_owned_legacy_keys = {
        "combustion_chamber": {
            "mass_flow_rate", "mixture_ratio", "fuel_mass_flow_rate",
            "oxidizer_mass_flow_rate",
            "chamber_temperature", "chamber_pressure", "estimated_residence_time",
            "characteristic_length", "characteristic_velocity",
        },
        "nozzle": {
            "throat_area", "exit_area", "expansion_ratio",
            "selected_expansion_ratio", "nozzle_length", "cross_sectional_area",
            "throat_radius", "exit_radius", "radius_2", "radius_3",
            "static_temperature", "static_pressure", "static_density",
            "exit_pressure", "mach_number", "selected_mach_number",
        },
        "regen": {
            "adiabatic_wall_temperature",
            "selected_gas_side_recovery_temperature",
            "compressibility_correlation_factor",
        },
    }

    for module_id, keys in module_owned_legacy_keys.items():
        if not module_execution_enabled(module_execution_policy, module_id):
            for key in keys:
                functions.pop(key, None)

    known = {k: v for k, v in params.items() if v not in [None, "N/A"]}
    unknown = {k: v for k, v in params.items() if v in [None, "N/A"]}

    history = {key: [params.get(key)] for key in params} if keep_history else {}
    previous_values = {}
    iteration_count = 0

    while unknown and iteration_count < max_iterations:
        iteration_count += 1
        if debug:
            print(f"\n--- Legacy fill iteration {iteration_count} ---")
        solved_something = False

        for key, func in functions.items():
            if key in unknown:
                func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
                kwargs = {k: known[k] for k in func_args if k in known}

                try:
                    new_value = func(**kwargs)

                    # Skip invalid, None, or runaway values
                    if new_value in [None, float('inf'), float('-inf')]:
                        if keep_history:
                            history[key].append(None)
                        continue
                    if abs(new_value) > 1e12:
                        if keep_history:
                            history[key].append(None)
                        continue

                    # Skip oscillating values
                    if key in previous_values and abs(previous_values[key] - new_value) < 1e-12:
                        if keep_history:
                            history[key].append(None)
                        continue

                    # Accept new value
                    params[key] = new_value
                    known[key] = new_value
                    unknown.pop(key, None)
                    previous_values[key] = new_value
                    solved_something = True
                    if debug:
                        print(f"{key} updated to {new_value}")
                    if keep_history:
                        history[key].append(new_value)

                except ZeroDivisionError:
                    if keep_history:
                        history[key].append(None)
                    continue
                except Exception as e:
                    print(f"Error calculating {key}: {e}")
                    if keep_history:
                        history[key].append(None)

        if not solved_something:
            if debug:
                print("No further solvable unknowns in this iteration.")
            break

    if iteration_count >= max_iterations:
        print("Warning: Maximum iterations reached. Some unknowns may not be solved.")

    # --- Step 3: Optional legacy diagnostics ---
    if debug:
        print("\n--- Final Parameters ---")
        for key, value in params.items():
            print(f"{key}: {value}")

        if keep_history:
            print("\n--- Iteration History ---")
            for key, values in history.items():
                print(f"{key}: {values}")

    return params, history


def attach_regen_off_nominal_qualification(
    params,
    results,
    execution_scope=None,
    module_execution_policy=None,
    scenario_solver=None,
):
    """Evaluate the authoritative regen off-nominal operating envelope.

    No degradation magnitude is invented here.

    The policy must explicitly provide all four required scenario
    families. Scenario states are copied before perturbation.

    Nominal ROBUST reserve may be consumed by an off-nominal case.
    Therefore off-nominal cases must remain within absolute feasibility
    and hard pressure-system limits, but need not themselves remain
    ROBUST.
    """

    import copy
    import math

    authoritative_modes = {
        "SOURCED_OPERATING_ENVELOPE",
        "VERIFIED_TEST_ENVELOPE",
        "VERIFIED_DESIGN_REQUIREMENT",
    }

    required_families = {
        "REDUCED_COOLANT_FLOW",
        "INCREASED_COOLANT_INLET_TEMPERATURE",
        "REDUCED_COOLANT_INLET_PRESSURE",
        "INCREASED_HYDRAULIC_RESISTANCE",
    }

    allowed_keys = {
        "REDUCED_COOLANT_FLOW": {
            "coolant_mass_flow_rate",
            "coolant_flow_fraction",
        },

        "INCREASED_COOLANT_INLET_TEMPERATURE": {
            "coolant_inlet_temperature",
        },

        "REDUCED_COOLANT_INLET_PRESSURE": {
            "coolant_inlet_pressure",
        },

        "INCREASED_HYDRAULIC_RESISTANCE": {
            "coolant_friction_factor",
        },
    }

    blockers = []
    scenario_reports = []

    report = {
        "passed":
            False,

        "status":
            "UNPROVEN_REGEN_OFF_NOMINAL_QUALIFICATION",

        "blockers":
            blockers,

        "policy_status":
            None,

        "source":
            None,

        "required_scenario_families":
            sorted(
                required_families
            ),

        "scenario_count":
            0,

        "failed_scenario_count":
            0,

        "scenarios":
            scenario_reports,
    }

    def first_number(
        mappings,
        *keys,
    ):
        for mapping in mappings:
            if not isinstance(
                mapping,
                dict,
            ):
                continue

            for key in keys:
                value = mapping.get(
                    key
                )

                if value is None:
                    continue

                try:
                    value = float(
                        value
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if math.isfinite(
                    value
                ):
                    return value

        return None

    def attach_report():
        results[
            "regen_off_nominal_qualification_pass"
        ] = bool(
            report.get(
                "passed",
                False,
            )
        )

        results[
            "regen_off_nominal_qualification_status"
        ] = report.get(
            "status"
        )

        results[
            "regen_off_nominal_qualification_blockers"
        ] = list(
            report.get(
                "blockers"
            )
            or
            []
        )

        results[
            "regen_off_nominal_qualification_evidence"
        ] = report

        return results

    # ------------------------------------------------------------
    # OPTIONAL NOMINAL COOLANT PRESSURE BOUNDARY
    # ------------------------------------------------------------

    nominal_coolant_inlet_pressure = first_number(
        (
            params,
            results,
        ),
        "coolant_inlet_pressure",
    )

    if nominal_coolant_inlet_pressure is not None:
        results[
            "coolant_inlet_pressure"
        ] = nominal_coolant_inlet_pressure

    # ------------------------------------------------------------
    # POLICY
    # ------------------------------------------------------------

    policy = (
        results.get(
            "regen_off_nominal_qualification_policy"
        )
        or
        params.get(
            "regen_off_nominal_qualification_policy"
        )
    )

    if not isinstance(
        policy,
        dict,
    ):
        blockers.append(
            "Authoritative off-nominal qualification policy is unavailable."
        )

        return attach_report()

    policy_status = str(
        policy.get(
            "status"
        )
        or
        ""
    ).strip().upper()

    source_name = str(
        policy.get(
            "source"
        )
        or
        ""
    ).strip()

    report[
        "policy_status"
    ] = policy_status

    report[
        "source"
    ] = (
        source_name
        or
        None
    )

    authoritative = (
        policy_status
        in
        authoritative_modes
    )

    if not source_name:
        blockers.append(
            "Off-nominal qualification policy has no provenance source."
        )

    scenarios = policy.get(
        "scenarios"
    )

    if not isinstance(
        scenarios,
        (
            list,
            tuple,
        ),
    ):
        blockers.append(
            "Off-nominal qualification policy has no scenario list."
        )

        return attach_report()

    families_present = {
        str(
            scenario.get(
                "family"
            )
            or
            ""
        ).strip().upper()

        for scenario in scenarios

        if isinstance(
            scenario,
            dict,
        )
    }

    missing_families = sorted(
        required_families
        -
        families_present
    )

    if missing_families:
        blockers.append(
            "Required off-nominal scenario families are missing: "
            +
            ", ".join(
                missing_families
            )
        )

    if not authoritative:
        blockers.append(
            "Off-nominal policy is not authoritative and cannot qualify the design."
        )

    if (
        not source_name
        or
        missing_families
    ):
        return attach_report()

    # ------------------------------------------------------------
    # SOLVER CALLBACK
    # ------------------------------------------------------------

    if scenario_solver is None:

        def scenario_solver(
            scenario_params,
        ):
            return iterative_solver(
                scenario_params,
                execution_scope=execution_scope,
                module_execution_policy=module_execution_policy,
            )

    # ------------------------------------------------------------
    # SCENARIOS
    # ------------------------------------------------------------

    for index, scenario in enumerate(
        scenarios,
        1,
    ):
        scenario_blockers = []

        if not isinstance(
            scenario,
            dict,
        ):
            scenario_reports.append(
                {
                    "scenario_index":
                        index,

                    "name":
                        None,

                    "family":
                        None,

                    "passed":
                        False,

                    "blockers":
                        [
                            "Scenario payload is not a dictionary."
                        ],
                }
            )

            continue

        family = str(
            scenario.get(
                "family"
            )
            or
            ""
        ).strip().upper()

        name = str(
            scenario.get(
                "name"
            )
            or
            family
            or
            f"SCENARIO_{index}"
        ).strip()

        perturbations = scenario.get(
            "perturbations"
        )

        scenario_params = copy.deepcopy(
            params
        )

        scenario_params[
            "_leaf_48s_off_nominal_scenario_active"
        ] = True

        for stale_key in (
            "regen_qualification_state",
            "regen_qualification_pass",
            "regen_qualification_blockers",
            "regen_qualification_enforcement_ready",
            "regen_off_nominal_qualification_pass",
            "regen_off_nominal_qualification_status",
            "regen_off_nominal_qualification_blockers",
            "regen_off_nominal_qualification_evidence",
        ):
            scenario_params.pop(
                stale_key,
                None,
            )

        if family not in required_families:
            scenario_blockers.append(
                f"Unsupported off-nominal scenario family: "
                f"{family or 'UNKNOWN'}."
            )

        if not isinstance(
            perturbations,
            (
                list,
                tuple,
            ),
        ):
            scenario_blockers.append(
                "Scenario perturbations are unavailable."
            )

            perturbations = []

        applied = []

        for perturbation in perturbations:

            if not isinstance(
                perturbation,
                dict,
            ):
                scenario_blockers.append(
                    "Scenario perturbation is not a dictionary."
                )

                continue

            result_key = str(
                perturbation.get(
                    "result_key"
                )
                or
                ""
            ).strip()

            mode = str(
                perturbation.get(
                    "mode"
                )
                or
                ""
            ).strip().upper()

            try:
                value = float(
                    perturbation.get(
                        "value"
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                scenario_blockers.append(
                    f"Perturbation value is invalid for "
                    f"{result_key or 'UNKNOWN'}."
                )

                continue

            if not math.isfinite(
                value
            ):
                scenario_blockers.append(
                    f"Perturbation value is not finite for "
                    f"{result_key or 'UNKNOWN'}."
                )

                continue

            if (
                family in allowed_keys
                and
                result_key
                not in
                allowed_keys[
                    family
                ]
            ):
                scenario_blockers.append(
                    f"{result_key or 'UNKNOWN'} is not an allowed "
                    f"perturbation key for {family}."
                )

                continue

            nominal_value = first_number(
                (
                    scenario_params,
                    results,
                ),
                result_key,
            )

            if mode == "SET":
                actual = value

            elif mode == "ADD":
                if nominal_value is None:
                    scenario_blockers.append(
                        f"ADD requires a nominal value for {result_key}."
                    )

                    continue

                actual = (
                    nominal_value
                    +
                    value
                )

            elif mode == "SUBTRACT":
                if nominal_value is None:
                    scenario_blockers.append(
                        f"SUBTRACT requires a nominal value for {result_key}."
                    )

                    continue

                actual = (
                    nominal_value
                    -
                    value
                )

            elif mode in {
                "MULTIPLY",
                "SCALE",
            }:
                if nominal_value is None:
                    scenario_blockers.append(
                        f"{mode} requires a nominal value for {result_key}."
                    )

                    continue

                actual = (
                    nominal_value
                    *
                    value
                )

            else:
                scenario_blockers.append(
                    f"Unsupported perturbation mode "
                    f"{mode or 'UNKNOWN'} for {result_key}."
                )

                continue

            if (
                not math.isfinite(
                    actual
                )
                or
                actual <= 0.0
            ):
                scenario_blockers.append(
                    f"Perturbed physical value is invalid for {result_key}."
                )

                continue

            # ----------------------------------------------------
            # DIRECTIONAL SEMANTICS
            # ----------------------------------------------------

            if family == "REDUCED_COOLANT_FLOW":

                if nominal_value is None:
                    scenario_blockers.append(
                        "Reduced coolant-flow scenario requires "
                        "an existing nominal flow value."
                    )

                    continue

                if actual >= nominal_value:
                    scenario_blockers.append(
                        "Reduced coolant-flow scenario does not "
                        "reduce coolant flow."
                    )

                    continue

            elif family == "INCREASED_COOLANT_INLET_TEMPERATURE":

                if nominal_value is None:
                    scenario_blockers.append(
                        "Increased inlet-temperature scenario requires "
                        "an existing nominal temperature."
                    )

                    continue

                if actual <= nominal_value:
                    scenario_blockers.append(
                        "Increased inlet-temperature scenario does not "
                        "increase temperature."
                    )

                    continue

            elif family == "REDUCED_COOLANT_INLET_PRESSURE":

                if (
                    nominal_value is not None
                    and
                    actual >= nominal_value
                ):
                    scenario_blockers.append(
                        "Reduced coolant-inlet-pressure scenario does "
                        "not reduce inlet pressure."
                    )

                    continue

                if (
                    nominal_value is None
                    and
                    mode != "SET"
                ):
                    scenario_blockers.append(
                        "Without a nominal coolant inlet pressure, the "
                        "authoritative scenario must provide an absolute "
                        "SET pressure."
                    )

                    continue

            elif family == "INCREASED_HYDRAULIC_RESISTANCE":

                if nominal_value is None:
                    scenario_blockers.append(
                        "Increased hydraulic-resistance scenario requires "
                        "an existing nominal friction factor."
                    )

                    continue

                if actual <= nominal_value:
                    scenario_blockers.append(
                        "Increased hydraulic-resistance scenario does not "
                        "increase resistance."
                    )

                    continue

            scenario_params[
                result_key
            ] = actual

            applied.append(
                {
                    "result_key":
                        result_key,

                    "mode":
                        mode,

                    "specified_value":
                        value,

                    "nominal_value":
                        nominal_value,

                    "scenario_value":
                        actual,
                }
            )

        if not applied:
            scenario_blockers.append(
                "Scenario contains no valid perturbation."
            )

        if scenario_blockers:
            scenario_reports.append(
                {
                    "scenario_index":
                        index,

                    "name":
                        name,

                    "family":
                        family,

                    "applied_perturbations":
                        applied,

                    "passed":
                        False,

                    "blockers":
                        scenario_blockers,
                }
            )

            continue

        # --------------------------------------------------------
        # EXISTING PHYSICS RE-SOLVE
        # --------------------------------------------------------

        try:
            scenario_results = scenario_solver(
                scenario_params
            )

        except Exception as exc:
            scenario_reports.append(
                {
                    "scenario_index":
                        index,

                    "name":
                        name,

                    "family":
                        family,

                    "applied_perturbations":
                        applied,

                    "passed":
                        False,

                    "blockers":
                        [
                            "Existing regen solver could not evaluate "
                            "the off-nominal scenario."
                        ],

                    "error":
                        repr(exc),
                }
            )

            continue

        if not isinstance(
            scenario_results,
            dict,
        ):
            scenario_reports.append(
                {
                    "scenario_index":
                        index,

                    "name":
                        name,

                    "family":
                        family,

                    "applied_perturbations":
                        applied,

                    "passed":
                        False,

                    "blockers":
                        [
                            "Existing regen solver returned an invalid "
                            "scenario result."
                        ],
                }
            )

            continue

        safety_blockers = []

        # --------------------------------------------------------
        # ABSOLUTE FEASIBILITY
        # --------------------------------------------------------

        feasibility_pass = (
            scenario_results.get(
                "regen_feasibility_pass"
            )
            is True
        )

        if not feasibility_pass:
            safety_blockers.append(
                "Off-nominal scenario fails absolute regen feasibility."
            )

        # --------------------------------------------------------
        # EXISTING PRESSURE-DROP LIMIT
        # --------------------------------------------------------

        pressure_drop = first_number(
            (
                scenario_results,
            ),
            "recommended_regen_axial_total_pressure_drop",
            "regen_axial_total_pressure_drop",
            "coolant_pressure_drop_total",
            "coolant_pressure_drop",
        )

        pressure_drop_limit = first_number(
            (
                scenario_results,
            ),
            "regen_derived_pressure_drop_limit",
            "regen_pressure_drop_limit",
        )

        pressure_ratio = first_number(
            (
                scenario_results,
            ),
            "regen_feasibility_pressure_drop_ratio",
        )

        if (
            pressure_ratio is None
            and
            pressure_drop is not None
            and
            pressure_drop_limit is not None
            and
            pressure_drop_limit > 0.0
        ):
            pressure_ratio = (
                pressure_drop
                /
                pressure_drop_limit
            )

        pressure_budget_pass = (
            pressure_ratio is not None
            and
            pressure_ratio <= 1.0
        )

        if not pressure_budget_pass:
            safety_blockers.append(
                "Off-nominal scenario exceeds or cannot prove the "
                "existing regen pressure-drop system limit."
            )

        # --------------------------------------------------------
        # EXPLICIT COOLANT INLET PRESSURE HEAD
        # --------------------------------------------------------

        inlet_pressure = first_number(
            (
                scenario_params,
                scenario_results,
            ),
            "coolant_inlet_pressure",
        )

        chamber_pressure = first_number(
            (
                scenario_results,
                scenario_params,
                results,
            ),
            "chamber_pressure",
        )

        available_pressure_head = None
        inlet_pressure_pass = None

        if family == "REDUCED_COOLANT_INLET_PRESSURE":

            if inlet_pressure is None:
                safety_blockers.append(
                    "Reduced coolant-inlet-pressure scenario has no "
                    "explicit coolant inlet pressure."
                )

            elif chamber_pressure is None:
                safety_blockers.append(
                    "Chamber pressure is unavailable as the downstream "
                    "minimum-pressure reference."
                )

            elif pressure_drop is None:
                safety_blockers.append(
                    "Calculated regen coolant pressure drop is unavailable."
                )

            else:
                available_pressure_head = (
                    inlet_pressure
                    -
                    chamber_pressure
                )

                inlet_pressure_pass = (
                    available_pressure_head > 0.0
                    and
                    pressure_drop
                    <=
                    available_pressure_head
                )

                if not inlet_pressure_pass:
                    safety_blockers.append(
                        "Available coolant inlet pressure head is "
                        "insufficient for the calculated regen pressure drop."
                    )

        passed = (
            not safety_blockers
        )

        scenario_reports.append(
            {
                "scenario_index":
                    index,

                "name":
                    name,

                "family":
                    family,

                "applied_perturbations":
                    applied,

                "feasibility_pass":
                    feasibility_pass,

                "pressure_drop":
                    pressure_drop,

                "pressure_drop_limit":
                    pressure_drop_limit,

                "pressure_drop_ratio":
                    pressure_ratio,

                "pressure_budget_pass":
                    pressure_budget_pass,

                "coolant_inlet_pressure":
                    inlet_pressure,

                "downstream_chamber_pressure":
                    chamber_pressure,

                "available_coolant_pressure_head":
                    available_pressure_head,

                "coolant_inlet_pressure_pass":
                    inlet_pressure_pass,

                "passed":
                    passed,

                "blockers":
                    safety_blockers,
            }
        )

    failed_scenarios = [
        scenario
        for scenario in scenario_reports
        if not scenario.get(
            "passed",
            False,
        )
    ]

    report[
        "scenario_count"
    ] = len(
        scenario_reports
    )

    report[
        "failed_scenario_count"
    ] = len(
        failed_scenarios
    )

    if failed_scenarios:
        blockers.append(
            f"{len(failed_scenarios)} of "
            f"{len(scenario_reports)} off-nominal scenarios failed."
        )

        report[
            "status"
        ] = (
            "FAIL_REGEN_OFF_NOMINAL_QUALIFICATION"
            if authoritative
            else
            "UNPROVEN_REGEN_OFF_NOMINAL_QUALIFICATION"
        )

        return attach_report()

    if not authoritative:
        report[
            "status"
        ] = (
            "UNPROVEN_REGEN_OFF_NOMINAL_QUALIFICATION"
        )

        return attach_report()

    report[
        "passed"
    ] = True

    report[
        "status"
    ] = (
        "PASS_REGEN_OFF_NOMINAL_QUALIFICATION"
    )

    return attach_report()




def run_regen_geometry_material_automatic_design(
    results,
    execution_scope="full",
    module_execution_policy=None,
):
    """Run the canonical Geometry + Materials automatic-design search.

    The caller supplies an isolated solved/input-state snapshot.

    This function owns no new engineering equations, qualification criteria,
    ranking policy, or UI state. It only selects the existing candidate design
    mode and re-enters the canonical iterative solver.
    """

    if not isinstance(
        results,
        dict,
    ):
        raise TypeError(
            "Geometry + Materials automatic design requires a result dictionary."
        )

    working = dict(
        results
    )

    working[
        "regen_candidate_design_mode"
    ] = (
        "GEOMETRY_AND_MATERIALS"
    )

    working[
        "regen_automatic_design_mode"
    ] = (
        "GEOMETRY_AND_MATERIALS"
    )

    # Remove previous automatic candidate-result products from the isolated
    # snapshot so an earlier Selected-Material run cannot masquerade as the
    # result of this search.
    stale_exact = (
        "regen_candidate_evaluated_population",
        "regen_candidate_evaluated_population_count",
        "regen_candidate_qualified_population",
        "regen_candidate_qualified_population_count",
        "regen_candidate_ranked_population",
        "regen_candidate_ranked_population_count",
        "regen_candidate_recommendation",
        "regen_candidate_application_patch",
        "regen_candidate_selector_requested_candidate_id",
        "regen_candidate_selector_user_selected_candidate_id",
    )

    for key in stale_exact:
        working.pop(
            key,
            None,
        )

    solved, _solver_history = iterative_solver(
        working,
        execution_scope=execution_scope,
        module_execution_policy=module_execution_policy,
    )

    if not isinstance(
        solved,
        dict,
    ):
        raise RuntimeError(
            "Geometry + Materials automatic design did not return "
            "a canonical solver result dictionary."
        )

    solved[
        "regen_candidate_design_mode"
    ] = (
        "GEOMETRY_AND_MATERIALS"
    )

    solved[
        "regen_automatic_design_mode"
    ] = (
        "GEOMETRY_AND_MATERIALS"
    )

    evaluated = (
        solved.get(
            "regen_candidate_evaluated_population"
        )
        or
        []
    )

    qualified = (
        solved.get(
            "regen_candidate_qualified_population"
        )
        or
        []
    )

    ranked = (
        solved.get(
            "regen_candidate_ranked_population"
        )
        or
        []
    )

    solved[
        "regen_geometry_material_automatic_design_complete"
    ] = bool(
        solved.get(
            "regen_candidate_population_qualification_complete"
        )
    )

    solved[
        "regen_geometry_material_automatic_design_evaluated_count"
    ] = len(
        evaluated
    )

    solved[
        "regen_geometry_material_automatic_design_qualified_count"
    ] = len(
        qualified
    )

    solved[
        "regen_geometry_material_automatic_design_ranked_count"
    ] = len(
        ranked
    )

    solved[
        "regen_geometry_material_automatic_design_status"
    ] = (
        "COMPLETE_QUALIFIED_DESIGNS_AVAILABLE"
        if ranked
        else
        "COMPLETE_NO_QUALIFIED_DESIGN"
    )

    return solved


def attach_regen_qualified_candidate_population(
    results,
    base_params=None,
    execution_scope=None,
    module_execution_policy=None,
    candidate_solver=None,
):
    """Solve and qualify generated regen candidates before ranking.

    This function owns orchestration only.

    Candidate -> application patch:
        regen_candidate_application_owner.py

    Patch -> cloned candidate state:
        regen_candidate_resolve_owner.py

    Clone -> solver execution:
        regen_candidate_resolve_execution_owner.py

    Qualification truth:
        regen_candidate_validator.py

    Ranking is not permitted to own engineering physics.
    """

    if not isinstance(
        results,
        dict,
    ):
        return results

    population = results.get(
        "regen_candidate_population"
    )

    evaluated_population = []
    qualified_population = []
    blockers = []

    if not isinstance(
        population,
        list,
    ):
        blockers.append(
            "Canonical regen candidate population is unavailable."
        )
        population = []

    required_owners = (
        attach_regen_candidate_application_owner,
        attach_regen_candidate_resolve_owner,
        attach_regen_candidate_resolve_execution_owner,
    )

    if any(
        owner is None
        for owner in required_owners
    ):
        blockers.append(
            "Required existing candidate application/resolve "
            "owners are unavailable."
        )

    base_params = (
        dict(base_params)
        if isinstance(
            base_params,
            dict,
        )
        else
        {}
    )

    def default_candidate_solver(
        candidate_state,
    ):
        candidate_params = dict(
            base_params
        )

        material_candidate_active = (
            isinstance(
                candidate_state,
                dict,
            )
            and
            candidate_state.get(
                "_leaf_candidate_material_search_active"
            )
            is True
        )

        if material_candidate_active:
            explicit_stale_material_keys = {
                "selected_material",
                "selected_material_name",
                "material_name",
                "hot_gas_liner",
                "hot_gas_liner_material",
                "wall_material",
                "wall_thermal_conductivity",
                "selected_material_max_temperature",
                "effective_material_temperature_limit",
                "effective_material_yield_strength",
                "sourced_material_temperature_limit",
            }

            for key in list(
                candidate_params
            ):
                if (
                    key in explicit_stale_material_keys
                    or
                    key.startswith(
                        "material_"
                    )
                ):
                    candidate_params.pop(
                        key,
                        None,
                    )

        if isinstance(
            candidate_state,
            dict,
        ):
            candidate_params.update(
                candidate_state
            )

        candidate_params[
            "_leaf_48u_candidate_qualification_solve_active"
        ] = True

        candidate_params.pop(
            "_leaf_48s_off_nominal_scenario_active",
            None,
        )

        stale_exact = {
            "regen_feasibility_pass",
            "regen_robust_qualification_pass",
            "regen_manufacturing_tolerance_qualification_pass",
            "regen_off_nominal_qualification_pass",
        }

        for key in list(
            candidate_params
        ):
            if (
                key in stale_exact
                or
                key.startswith(
                    "regen_qualification_"
                )
            ):
                candidate_params.pop(
                    key,
                    None,
                )

        return iterative_solver(
            candidate_params,
            execution_scope=execution_scope,
            module_execution_policy=module_execution_policy,
        )

    solve = (
        candidate_solver
        or
        default_candidate_solver
    )

    if not blockers:
        for index, candidate in enumerate(
            population
        ):
            candidate_blockers = []

            if not isinstance(
                candidate,
                dict,
            ):
                evaluated_population.append(
                    {
                        "candidate_id":
                            f"INVALID-{index + 1}",

                        "regen_qualification_state":
                            "FAILED",

                        "regen_qualification_pass":
                            False,

                        "regen_qualification_enforcement_ready":
                            False,

                        "regen_qualification_blockers":
                            [
                                "Candidate payload is not a dictionary."
                            ],

                        "candidate_solver_executed":
                            False,

                        "candidate_status":
                            "FAILED_QUALIFICATION_INPUT",
                    }
                )

                continue

            candidate_id = str(
                candidate.get(
                    "candidate_id"
                )
                or
                f"RPOP-{index + 1:04d}"
            )

            geometry = (
                candidate.get(
                    "candidate_geometry"
                )
                or
                {}
            )

            if (
                not isinstance(
                    geometry,
                    dict,
                )
                or
                not geometry
            ):
                candidate_blockers.append(
                    "Candidate geometry is unavailable."
                )

            raw_design_inputs = (
                candidate.get(
                    "candidate_design_inputs"
                )
            )

            if isinstance(
                raw_design_inputs,
                dict,
            ):
                candidate_design_inputs = dict(
                    raw_design_inputs
                )

                # Physical geometry remains owned by
                # candidate_geometry.
                candidate_design_inputs.update(
                    geometry
                )

            else:
                candidate_design_inputs = dict(
                    geometry
                )

            working = dict(
                results
            )

            working[
                "_leaf_48u_candidate_qualification_evaluation_active"
            ] = True

            working[
                "regen_candidate_recommendation"
            ] = {
                "candidate_id":
                    candidate_id,

                "inputs":
                    dict(
                        candidate_design_inputs
                    ),
            }

            solve_result = None

            if not candidate_blockers:
                working = (
                    attach_regen_candidate_application_owner(
                        working
                    )
                )

                if (
                    working.get(
                        "regen_candidate_application_ready"
                    )
                    is not True
                ):
                    candidate_blockers.extend(
                        working.get(
                            "regen_candidate_application_blocking_reasons"
                        )
                        or
                        [
                            "Candidate application patch is not ready."
                        ]
                    )

            if not candidate_blockers:
                working = (
                    attach_regen_candidate_resolve_owner(
                        working
                    )
                )

                if (
                    working.get(
                        "regen_candidate_resolve_ready"
                    )
                    is not True
                ):
                    candidate_blockers.extend(
                        working.get(
                            "regen_candidate_resolve_blocking_reasons"
                        )
                        or
                        [
                            "Candidate resolve clone is not ready."
                        ]
                    )

            if not candidate_blockers:

                def solve_candidate(
                    patched_clone,
                ):
                    candidate_solve_state = (
                        dict(
                            patched_clone
                        )
                        if isinstance(
                            patched_clone,
                            dict,
                        )
                        else
                        {}
                    )

                    # Preserve the canonical physical geometry patch
                    # contract while allowing evaluation-only candidate
                    # variables such as coolant_flow_fraction to reach
                    # the ephemeral solver state.
                    candidate_solve_state.update(
                        dict(
                            candidate_design_inputs
                        )
                    )

                    return solve(
                        candidate_solve_state
                    )

                working = (
                    attach_regen_candidate_resolve_execution_owner(
                        working,
                        solver_callable=solve_candidate,
                    )
                )

                if (
                    working.get(
                        "regen_candidate_resolve_execution_executed"
                    )
                    is not True
                ):
                    candidate_blockers.extend(
                        working.get(
                            "regen_candidate_resolve_execution_blocking_reasons"
                        )
                        or
                        [
                            "Candidate solver execution did not complete."
                        ]
                    )

                solve_result = working.get(
                    "regen_candidate_resolve_execution_result"
                )

            if not isinstance(
                solve_result,
                dict,
            ):
                if not candidate_blockers:
                    candidate_blockers.append(
                        "Candidate solver did not return a result dictionary."
                    )

                solve_result = {}

            state = str(
                solve_result.get(
                    "regen_qualification_state"
                )
                or
                ""
            ).strip().upper()

            enforcement_ready = (
                solve_result.get(
                    "regen_qualification_enforcement_ready"
                )
                is True
            )

            canonical_pass = (
                solve_result.get(
                    "regen_qualification_pass"
                )
                is True
            )

            canonical_blockers = list(
                solve_result.get(
                    "regen_qualification_blockers"
                )
                or
                []
            )

            candidate_blockers.extend(
                canonical_blockers
            )

            is_qualified = (
                not candidate_blockers
                and
                enforcement_ready
                and
                canonical_pass
                and
                state
                ==
                "QUALIFIED"
            )

            evaluated = dict(
                candidate
            )

            evaluated[
                "regen_qualification_state"
            ] = (
                state
                or
                "FAILED"
            )

            evaluated[
                "regen_qualification_pass"
            ] = is_qualified

            evaluated[
                "regen_qualification_enforcement_ready"
            ] = enforcement_ready

            evaluated[
                "regen_qualification_blockers"
            ] = candidate_blockers

            evaluated[
                "regen_qualification_report"
            ] = solve_result.get(
                "regen_qualification_report"
            )

            evaluated[
                "candidate_solver_executed"
            ] = bool(
                working.get(
                    "regen_candidate_resolve_execution_executed"
                )
            )

            evaluated[
                "candidate_status"
            ] = (
                "QUALIFIED_READY_FOR_AUTOMATIC_RANKING"
                if is_qualified
                else
                "NOT_QUALIFIED_EXCLUDED_FROM_AUTOMATIC_RANKING"
            )

            evaluated_population.append(
                evaluated
            )

            if is_qualified:
                qualified_population.append(
                    evaluated
                )

    complete = (
        not blockers
        and
        isinstance(
            population,
            list,
        )
    )

    results[
        "regen_candidate_population_qualification_complete"
    ] = complete

    results[
        "regen_candidate_population_qualification_ready"
    ] = (
        complete
        and
        bool(
            qualified_population
        )
    )

    results[
        "regen_candidate_population_qualification_blockers"
    ] = blockers

    results[
        "regen_candidate_evaluated_population"
    ] = evaluated_population

    results[
        "regen_candidate_evaluated_population_count"
    ] = len(
        evaluated_population
    )

    results[
        "regen_candidate_qualified_population"
    ] = qualified_population

    results[
        "regen_candidate_qualified_population_count"
    ] = len(
        qualified_population
    )

    results[
        "regen_candidate_population_qualification_report"
    ] = {
        "complete":
            complete,

        "raw_candidate_count":
            len(
                population
            ),

        "evaluated_candidate_count":
            len(
                evaluated_population
            ),

        "qualified_candidate_count":
            len(
                qualified_population
            ),

        "excluded_candidate_count":
            len(
                evaluated_population
            )
            -
            len(
                qualified_population
            ),

        "blockers":
            blockers,

        "candidate_to_patch_owner":
            "regen_candidate_application_owner.py",

        "candidate_clone_owner":
            "regen_candidate_resolve_owner.py",

        "solver_execution_owner":
            "regen_candidate_resolve_execution_owner.py",

        "qualification_truth_owner":
            "regen_candidate_validator.py",

        "ranking_policy":
            "QUALIFIED_ONLY",
    }

    return results


def attach_structural_component_masses(results):
    """
    Attach canonical hot-gas wall masses from existing chamber/nozzle geometry.

    Ownership boundary:
    - consumes canonical chamber/nozzle profiles;
    - consumes hot_gas_wall_thickness and material_density;
    - does not derive jacket/rib-channel mass;
    - does not calculate cost;
    - does not alter geometry or solver physics.
    """
    if not isinstance(results, dict):
        return results

    results["chamber_wall_mass"] = None
    results["nozzle_wall_mass"] = None
    results["base_wall_mass"] = None

    try:
        thickness = float(
            results.get(
                "hot_gas_wall_thickness"
            )
        )

        density = float(
            results.get(
                "material_density"
            )
        )

    except (
        TypeError,
        ValueError,
    ):
        return results

    if (
        not math.isfinite(
            thickness
        )

        or
        not math.isfinite(
            density
        )

        or
        thickness <= 0.0

        or
        density <= 0.0
    ):
        return results

    def profile_mass(
        profile,
    ):
        if (
            not isinstance(
                profile,
                (
                    list,
                    tuple,
                ),
            )

            or
            len(profile) < 2
        ):
            return None

        points = []

        for station in profile:
            if not isinstance(
                station,
                dict,
            ):
                return None

            x = station.get(
                "x"
            )

            radius = station.get(
                "radius"
            )

            if radius is None:
                radius = station.get(
                    "gas_radius"
                )

            if radius is None:
                radius = station.get(
                    "r"
                )

            try:
                x = float(
                    x
                )

                radius = float(
                    radius
                )

            except (
                TypeError,
                ValueError,
            ):
                return None

            if (
                not math.isfinite(
                    x
                )

                or
                not math.isfinite(
                    radius
                )

                or
                radius <= 0.0
            ):
                return None

            points.append(
                (
                    x,
                    radius,
                )
            )

        volume = 0.0

        for (
            (
                x1,
                r1,
            ),
            (
                x2,
                r2,
            ),
        ) in zip(
            points,
            points[1:],
        ):
            dx = (
                x2
                -
                x1
            )

            if (
                not math.isfinite(
                    dx
                )

                or
                dx < 0.0
            ):
                return None

            inner_volume = (
                math.pi
                *
                dx
                *
                (
                    r1 * r1
                    +
                    r1 * r2
                    +
                    r2 * r2
                )
                /
                3.0
            )

            outer_r1 = (
                r1
                +
                thickness
            )

            outer_r2 = (
                r2
                +
                thickness
            )

            outer_volume = (
                math.pi
                *
                dx
                *
                (
                    outer_r1 * outer_r1
                    +
                    outer_r1 * outer_r2
                    +
                    outer_r2 * outer_r2
                )
                /
                3.0
            )

            shell_volume = (
                outer_volume
                -
                inner_volume
            )

            if (
                not math.isfinite(
                    shell_volume
                )

                or
                shell_volume
                <
                -1.0e-15
            ):
                return None

            volume += max(
                0.0,
                shell_volume,
            )

        mass = (
            volume
            *
            density
        )

        if (
            not math.isfinite(
                mass
            )

            or
            mass < 0.0
        ):
            return None

        return mass

    chamber_mass = (
        profile_mass(
            results.get(
                "chamber_profile"
            )
        )
    )

    model = str(
        results.get(
            "nozzle_geometry_model"
        )
        or
        "RAO_BELL_APPROXIMATION"
    ).upper()

    if model == "CONICAL":
        nozzle_profile = (
            results.get(
                "conical_nozzle_profile"
            )
        )

    else:
        nozzle_profile = (
            results.get(
                "rao_nozzle_profile"
            )
        )

    nozzle_mass = (
        profile_mass(
            nozzle_profile
        )
    )

    results[
        "chamber_wall_mass"
    ] = chamber_mass

    results[
        "nozzle_wall_mass"
    ] = nozzle_mass

    if (
        chamber_mass is not None

        and
        nozzle_mass is not None
    ):
        results[
            "base_wall_mass"
        ] = (
            chamber_mass
            +
            nozzle_mass
        )

    return results


def iterative_solver(
        params,
        execution_scope="full",
        module_execution_policy=None,
):
    """
    Main solver wrapper.

    Directed solver is now the authority.
    Legacy solver is temporarily used only to fill missing values.
    Protected directed outputs are restored after legacy solving.
    """

    combustion_chamber_active = module_execution_enabled(
        module_execution_policy, "combustion_chamber"
    )
    regen_active = module_execution_enabled(
        module_execution_policy, "regen"
    )

    directed_results = solve_engine(
        params,
        module_execution_policy=module_execution_policy,
    )

    legacy_fill_inputs = dict(directed_results)

    legacy_results, legacy_history = legacy_iterative_solver(
        legacy_fill_inputs,
        module_execution_policy=module_execution_policy,
    )

    protected_directed_outputs = {

        # =====================================================
        # THERMODYNAMIC PROPERTIES
        # =====================================================

        "Gamma",
        "R",
        "specific_heat_cp",
        "specific_heat_cv",
        "thermo_r_error",
        "thermo_r_error_percent",
        "thermo_model_note",

        # =====================================================
        # FLOW PROPERTIES
        # =====================================================

        "mach_number",
        "selected_expansion_ratio",
        "selected_mach_number",

        "static_temperature",
        "static_pressure",
        "static_density",

        # =====================================================
        # PERFORMANCE
        # =====================================================

        "exit_pressure",
        "exhaust_velocity",

        "momentum_thrust",
        "pressure_thrust",
        "thrust",

        "specific_impulse",
        "vacuum_specific_impulse",
        "sea_level_specific_impulse",
        "effective_exhaust_velocity",

        "thrust_coefficient",
        "characteristic_velocity",

        # =====================================================
        # COMBUSTION CHAMBER GEOMETRY
        # =====================================================

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

        # =====================================================
        # CEA PERFORMANCE
        # =====================================================

        "cea_characteristic_velocity",
        "cea_thrust_coefficient",
        "cea_specific_impulse",
        "cea_vacuum_specific_impulse",
        "cea_exit_velocity",
        "cea_exit_pressure",
        "cea_chamber_temperature",

        # =====================================================
        # IDEAL PERFORMANCE
        # =====================================================

        "ideal_engine_thrust",
        "ideal_engine_specific_impulse",
        "ideal_volumetric_thrust",

        # =====================================================
        # HOT-GAS THERMAL MODEL
        # =====================================================

        "adiabatic_wall_temperature",
        "selected_gas_side_recovery_temperature",
        "compressibility_correlation_factor",

        # =====================================================
        # BARTZ MODEL
        # =====================================================

        "throat_diameter",
        "throat_radius_of_curvature",

        "gas_dynamic_viscosity",
        "gas_specific_heat_cp",
        "gas_prandtl_number",

        "bartz_sigma",
        "bartz_gas_side_heat_transfer_coefficient",

        # =====================================================
        # WALL THICKNESS MODEL
        # =====================================================

        "allowable_wall_stress",
        "pressure_required_wall_thickness",
        "conduction_required_wall_thickness",
        "hot_gas_wall_thickness",

        # =====================================================
        # HEAT FLUX
        # =====================================================

        "hot_gas_heat_flux",

        # =====================================================
        # REGENERATIVE COOLING GEOMETRY
        # =====================================================

        "single_channel_flow_area",
        "total_coolant_flow_area",

        "coolant_wetted_perimeter",
        "coolant_hydraulic_diameter",

        "channel_pitch",
        "regen_cross_section_outer_radius",

        "channel_mid_radius",
        "circumferential_channel_pitch",

        "effective_rib_width",
        "channel_fit_ratio",

        "channel_geometry_valid",

        # =====================================================
        # COOLANT FLOW MODEL
        # =====================================================

        "selected_station_length",

        "coolant_flow_fraction",

        "coolant_bulk_temperature",

        "coolant_velocity",

        "coolant_reynolds_number",
        "coolant_prandtl_number",

        "coolant_nusselt_number",

        "coolant_heat_transfer_coefficient",

        "coolant_mass_flow_per_channel",

        "coolant_friction_factor",

        "coolant_pressure_drop",

        # =====================================================
        # REGEN THERMAL RESISTANCE MODEL
        # =====================================================

        "regen_total_thermal_resistance",

        "regen_heat_flux",

        "hot_gas_side_wall_temperature",
        "coolant_side_wall_temperature_calculated",

        "local_hot_gas_surface_area",

        "coolant_temperature_rise",
        "coolant_outlet_temperature",

        "material_temperature_margin",
    }

    final_results = dict(legacy_results)

    for key in protected_directed_outputs:
        if directed_results.get(key) is not None:
            final_results[key] = directed_results[key]

    if combustion_chamber_active:
        final_results = build_combustion_chamber_geometry(
            final_results,
            module_execution_policy=module_execution_policy,
        )

    # Re-establish canonical nozzle state after legacy missing-value fill.
    #
    # The directed nozzle builder may initially be blocked because throat/exit
    # geometry is not yet available. Legacy is permitted to fill those missing
    # geometry values, but it must not remain the owner of the resulting nozzle
    # status/profile. Once geometry exists, rebuild the active nozzle profile
    # through the existing canonical nozzle owner.
    if module_execution_enabled(module_execution_policy, "nozzle"):
        active_nozzle_model = str(
            final_results.get("nozzle_geometry_model")
        ).upper()

        if active_nozzle_model == "CONICAL":
            final_results = build_conical_nozzle_profile(
                final_results,
                station_count=100,
            )
        else:
            final_results = build_rao_nozzle_profile(
                final_results,
                station_count=100,
            )

    # CEA authority must be applied after legacy fill as well,
    # because legacy fill may populate values that CEA performance needs.
    final_results = apply_cea_authoritative_performance(final_results)

    # Final correction pass after all values are available
    if combustion_chamber_active:
        final_results["combustion_efficiency"] = calculate_combustion_efficiency(
            mixture_ratio=final_results.get("mixture_ratio"),
            fuel_type=final_results.get("fuel_type", "Kerosene")
        )

        final_results["mixture_quality_factor"] = calculate_mixture_quality_factor(
            mixture_ratio=final_results.get("mixture_ratio"),
            fuel_type=final_results.get("fuel_type", "Kerosene")
        )

        final_results["soot_risk_factor"] = calculate_soot_risk_factor(
            mixture_ratio=final_results.get("mixture_ratio"),
            fuel_type=final_results.get("fuel_type", "Kerosene")
        )

    # PFQ-2D-R5E — early material/property authority chain
    final_results = apply_selected_material_properties(final_results)
    final_results = apply_material_source_validation_authority(final_results)
    final_results = attach_material_property_interpolation_owner(final_results)
    final_results = attach_material_property_consumption_audit_owner(final_results)
    final_results = attach_material_thermal_conductivity_integration_owner(final_results)
    final_results = attach_material_specific_heat_integration_owner(final_results)
    final_results = attach_material_density_integration_owner(final_results)
    final_results = attach_material_temperature_limit_integration_owner(final_results)
    final_results = attach_material_strength_limit_integration_owner(final_results)
    if regen_active:
        final_results["allowable_wall_stress"] = calculate_allowable_wall_stress(
            material_yield_strength=final_results.get("material_yield_strength"),
            wall_safety_factor=final_results.get("wall_safety_factor"),
            wall_joint_efficiency=final_results.get("wall_joint_efficiency")
        )

        final_results["pressure_required_wall_thickness"] = calculate_pressure_required_wall_thickness(
            chamber_pressure=final_results.get("chamber_pressure"),
            static_pressure=final_results.get("static_pressure"),
            throat_radius=final_results.get("throat_radius"),
            cross_sectional_area=final_results.get("cross_sectional_area"),
            allowable_wall_stress=final_results.get("allowable_wall_stress")
        )

    if execution_scope == "graph_core":
        return final_results, legacy_history

    if regen_active:
        final_results["hot_gas_heat_flux"] = None

        final_results["conduction_required_wall_thickness"] = None

        final_results["hot_gas_wall_thickness"] = calculate_hot_gas_wall_thickness(
            pressure_required_wall_thickness=final_results.get("pressure_required_wall_thickness"),
            conduction_required_wall_thickness=final_results.get("conduction_required_wall_thickness"),
            minimum_wall_thickness=final_results.get("minimum_wall_thickness"),
            corrosion_allowance=final_results.get("corrosion_allowance"),
            coating_thickness=final_results.get("coating_thickness")
        )

        final_results["regen_cross_section_outer_radius"] = calculate_regen_cross_section_outer_radius(
            cross_sectional_area=final_results.get("cross_sectional_area"),
            throat_radius=final_results.get("throat_radius"),
            hot_gas_wall_thickness=final_results.get("hot_gas_wall_thickness"),
            coolant_channel_height=final_results.get("coolant_channel_height"),
            outer_jacket_thickness=final_results.get("outer_jacket_thickness"),
            coating_thickness=final_results.get("coating_thickness")
        )

        # =====================================================
        # COMPLETE SINGLE-STATION REGEN THERMAL MODEL
        # =====================================================

        if final_results.get("coolant_bulk_temperature") is None:
            final_results["coolant_bulk_temperature"] = final_results.get(
                "coolant_inlet_temperature"
            )

        # =====================================================
        # BARTZ GAS-SIDE HEAT TRANSFER
        # =====================================================

        if (
            final_results.get("throat_diameter") is None
            and final_results.get("throat_radius") is not None
        ):
            final_results["throat_diameter"] = 2.0 * final_results["throat_radius"]

        if (
            final_results.get("throat_radius_of_curvature") is None
            and final_results.get("radius_3") is not None
        ):
            final_results["throat_radius_of_curvature"] = final_results["radius_3"]

        # Neutral Bartz seed only.
        #
        # The actual physical sigma is calculated later from Twg by
        # recalculate_single_station_regen_chain.
        final_results["bartz_sigma"] = 1.0
        final_results["compressibility_correlation_factor"] = None

        if final_results.get("gas_dynamic_viscosity") is None:
            final_results["gas_dynamic_viscosity"] = (
                final_results.get("cea_selected_viscosity")
                or final_results.get("cea_throat_viscosity")
                or final_results.get("cea_exit_viscosity")
            )

        if final_results.get("gas_specific_heat_cp") is None:
            final_results["gas_specific_heat_cp"] = (
                final_results.get("specific_heat_cp")
                or final_results.get("cea_selected_cp")
                or final_results.get("cea_throat_cp")
                or final_results.get("cea_exit_cp")
            )

        if final_results.get("gas_prandtl_number") is None:
            final_results["gas_prandtl_number"] = (
                final_results.get("gas_prandtl_number")
                or final_results.get("cea_selected_prandtl")
                or final_results.get("cea_throat_prandtl")
                or final_results.get("cea_exit_prandtl")
            )

        final_results["bartz_gas_side_heat_transfer_coefficient"] = (
            calculate_bartz_gas_side_heat_transfer_coefficient(
                throat_diameter=final_results.get("throat_diameter"),
                gas_dynamic_viscosity=final_results.get("gas_dynamic_viscosity"),
                gas_specific_heat_cp=final_results.get("gas_specific_heat_cp"),
                gas_prandtl_number=final_results.get("gas_prandtl_number"),
                chamber_pressure=final_results.get("chamber_pressure"),
                characteristic_velocity=final_results.get("characteristic_velocity"),
                throat_radius_of_curvature=final_results.get("throat_radius_of_curvature"),
                throat_area=final_results.get("throat_area"),
                cross_sectional_area=final_results.get("cross_sectional_area"),
                bartz_sigma=final_results.get("bartz_sigma")
            )
        )

        if final_results.get("bartz_gas_side_heat_transfer_coefficient") is not None:
            final_results["hot_gas_heat_transfer_coefficient"] = final_results[
                "bartz_gas_side_heat_transfer_coefficient"
            ]
        final_results = apply_coolant_database_properties(final_results)

        final_results["coolant_mass_flow_rate"] = calculate_coolant_mass_flow_rate_auto(
            coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
            fuel_mass_flow_rate=final_results.get("fuel_mass_flow_rate"),
            coolant_flow_fraction=final_results.get("coolant_flow_fraction", 1.0)
        )

        # ---------------------------------------------------------
        # D2C2-R4B — EARLY SINGLE-STATION HYDRAULIC PREREQUISITES
        # Existing geometry equations relocated from the later
        # geometry section. No equation duplication.
        # ---------------------------------------------------------
        final_results["single_channel_flow_area"] = calculate_single_channel_flow_area(
            coolant_channel_width=final_results.get("coolant_channel_width"),
            coolant_channel_height=final_results.get("coolant_channel_height")
        )

        final_results["total_coolant_flow_area"] = calculate_total_coolant_flow_area(
            single_channel_flow_area=final_results.get("single_channel_flow_area"),
            number_of_coolant_channels=final_results.get("number_of_coolant_channels")
        )

        final_results["coolant_wetted_perimeter"] = calculate_coolant_wetted_perimeter(
            coolant_channel_width=final_results.get("coolant_channel_width"),
            coolant_channel_height=final_results.get("coolant_channel_height")
        )

        final_results["coolant_hydraulic_diameter"] = calculate_coolant_hydraulic_diameter(
            single_channel_flow_area=final_results.get("single_channel_flow_area"),
            coolant_wetted_perimeter=final_results.get("coolant_wetted_perimeter")
        )

        final_results["coolant_velocity"] = calculate_coolant_velocity(
            coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
            coolant_density=final_results.get("coolant_density"),
            total_coolant_flow_area=final_results.get("total_coolant_flow_area")
        )

        final_results["coolant_reynolds_number"] = calculate_coolant_reynolds_number(
            coolant_density=final_results.get("coolant_density"),
            coolant_velocity=final_results.get("coolant_velocity"),
            coolant_hydraulic_diameter=final_results.get("coolant_hydraulic_diameter"),
            coolant_dynamic_viscosity=final_results.get("coolant_dynamic_viscosity")
        )

        final_results["coolant_mass_flow_per_channel"] = calculate_coolant_mass_flow_per_channel(
            coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
            number_of_coolant_channels=final_results.get("number_of_coolant_channels")
        )

        final_results["coolant_friction_factor"] = calculate_coolant_friction_factor(
            coolant_reynolds_number=final_results.get("coolant_reynolds_number")
        )

        final_results["coolant_pressure_drop"] = calculate_coolant_pressure_drop(
            coolant_friction_factor=final_results.get("coolant_friction_factor"),
            selected_station_length=final_results.get("selected_station_length"),
            coolant_hydraulic_diameter=final_results.get("coolant_hydraulic_diameter"),
            coolant_density=final_results.get("coolant_density"),
            coolant_velocity=final_results.get("coolant_velocity")
        )

        final_results["coolant_prandtl_number"] = calculate_coolant_prandtl_number(
            coolant_specific_heat_cp=final_results.get("coolant_specific_heat_cp"),
            coolant_dynamic_viscosity=final_results.get("coolant_dynamic_viscosity"),
            coolant_thermal_conductivity=final_results.get("coolant_thermal_conductivity")
        )

        final_results["coolant_nusselt_number"] = calculate_coolant_nusselt_number(
            coolant_reynolds_number=final_results.get("coolant_reynolds_number"),
            coolant_prandtl_number=final_results.get("coolant_prandtl_number")
        )

        final_results["coolant_heat_transfer_coefficient"] = calculate_coolant_heat_transfer_coefficient(
            coolant_nusselt_number=final_results.get("coolant_nusselt_number"),
            coolant_thermal_conductivity=final_results.get("coolant_thermal_conductivity"),
            coolant_hydraulic_diameter=final_results.get("coolant_hydraulic_diameter")
        )

        final_results["regen_total_thermal_resistance"] = calculate_regen_total_thermal_resistance(
            hot_gas_heat_transfer_coefficient=final_results.get("hot_gas_heat_transfer_coefficient"),
            hot_gas_wall_thickness=final_results.get("hot_gas_wall_thickness"),
            wall_thermal_conductivity=final_results.get("wall_thermal_conductivity"),
            coolant_heat_transfer_coefficient=final_results.get("coolant_heat_transfer_coefficient")
        )

        final_results["regen_heat_flux"] = calculate_regen_heat_flux(
            selected_gas_side_recovery_temperature=final_results.get("selected_gas_side_recovery_temperature"),
            coolant_bulk_temperature=final_results.get("coolant_bulk_temperature"),
            regen_total_thermal_resistance=final_results.get("regen_total_thermal_resistance")
        )

        final_results["hot_gas_side_wall_temperature"] = calculate_hot_gas_side_wall_temperature(
            selected_gas_side_recovery_temperature=final_results.get("selected_gas_side_recovery_temperature"),
            regen_heat_flux=final_results.get("regen_heat_flux"),
            hot_gas_heat_transfer_coefficient=final_results.get("hot_gas_heat_transfer_coefficient")
        )

        final_results["coolant_side_wall_temperature_calculated"] = calculate_coolant_side_wall_temperature_calculated(
            coolant_bulk_temperature=final_results.get("coolant_bulk_temperature"),
            regen_heat_flux=final_results.get("regen_heat_flux"),
            coolant_heat_transfer_coefficient=final_results.get("coolant_heat_transfer_coefficient")
        )

        final_results["local_hot_gas_surface_area"] = calculate_local_hot_gas_surface_area(
            cross_sectional_area=final_results.get("cross_sectional_area"),
            throat_radius=final_results.get("throat_radius"),
            selected_station_length=final_results.get("selected_station_length", 0.001)
        )

        final_results["coolant_temperature_rise"] = calculate_coolant_temperature_rise(
            regen_heat_flux=final_results.get("regen_heat_flux"),
            local_hot_gas_surface_area=final_results.get("local_hot_gas_surface_area"),
            coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
            coolant_specific_heat_cp=final_results.get("coolant_specific_heat_cp")
        )

        final_results["coolant_outlet_temperature"] = calculate_coolant_outlet_temperature(
            coolant_bulk_temperature=final_results.get("coolant_bulk_temperature"),
            coolant_temperature_rise=final_results.get("coolant_temperature_rise")
        )

        final_results["coolant_mean_temperature"] = calculate_coolant_mean_temperature(
            coolant_inlet_temperature=final_results.get("coolant_inlet_temperature"),
            coolant_outlet_temperature=final_results.get("coolant_outlet_temperature"),
            coolant_bulk_temperature=final_results.get("coolant_bulk_temperature")
        )
        # Close the canonical local Bartz / Twg fixed point before the existing
        # coolant-property feedback passes.
        # ---------------------------------------------------------
        # D2C2-R4B — EARLY WALL-CONDUCTIVITY PREREQUISITE
        # Existing material fallback owner only.
        # ---------------------------------------------------------
        if final_results.get("wall_thermal_conductivity") is None:
            final_results = apply_regen_material_fallbacks(final_results)

        final_results = recalculate_single_station_regen_chain(
            final_results
        )

        # ---------------------------------------------------------
        # Single-station coolant property feedback pass
        # ---------------------------------------------------------
        # First pass:
        #   properties are based on coolant bulk/inlet temperature.
        #
        # Feedback pass:
        #   use mean station coolant temperature to update coolant
        #   properties, then recalculate Re, Nu, hc, q'', Twg, Twc,
        #   pressure drop, and outlet temperature.
        # ---------------------------------------------------------

        if final_results.get("coolant_mean_temperature") is not None:
            refresh_coolant_properties_for_temperature(
                final_results,
                final_results.get("coolant_mean_temperature")
            )

            final_results = recalculate_single_station_regen_chain(final_results)

            # One additional correction pass improves stability without creating
            # a full iterative solver yet.
            if final_results.get("coolant_mean_temperature") is not None:
                refresh_coolant_properties_for_temperature(
                    final_results,
                    final_results.get("coolant_mean_temperature")
                )

                final_results = recalculate_single_station_regen_chain(final_results)

        # Preserve legacy/public thermal result keys from the canonical regen thermal authority.
        final_results["hot_gas_heat_flux"] = final_results.get("regen_heat_flux")

        final_results["conduction_required_wall_thickness"] = (
            calculate_conduction_required_wall_thickness(
                wall_thermal_conductivity=final_results.get("wall_thermal_conductivity"),
                hot_gas_side_wall_temperature=final_results.get("hot_gas_side_wall_temperature"),
                coolant_side_wall_temperature=final_results.get("coolant_side_wall_temperature_calculated"),
                hot_gas_heat_flux=final_results.get("hot_gas_heat_flux"),
            )
        )

        final_results["material_temperature_margin"] = calculate_material_temperature_margin(
            material_max_wall_temperature=final_results.get("material_max_wall_temperature"),
            hot_gas_side_wall_temperature=final_results.get("hot_gas_side_wall_temperature")
        )

        final_results["thermal_risk_factor"] = calculate_thermal_risk_factor(
            mixture_ratio=final_results.get("mixture_ratio")
        )

    final_results["corrected_thrust"] = calculate_corrected_thrust(
        thrust=final_results.get("thrust"),
        combustion_efficiency=final_results.get("combustion_efficiency"),
        mixture_quality_factor=final_results.get("mixture_quality_factor")
    )

    final_results["corrected_specific_impulse"] = calculate_corrected_specific_impulse(
        corrected_thrust=final_results.get("corrected_thrust"),
        mass_flow_rate=final_results.get("mass_flow_rate")
    )

    if execution_scope == "graph_corrected":
        return final_results, legacy_history

    if final_results.get("fuel_density") is None:
        final_results["fuel_density"] = get_propellant_density_from_temperature(
            final_results.get("fuel_type", "RP-1 / Kerosene"),
            final_results.get("fuel_temperature_k")
        )

    if final_results.get("oxidizer_density") is None:
        final_results["oxidizer_density"] = get_propellant_density_from_temperature(
            final_results.get("oxidizer_type", "O2(L)"),
            final_results.get("oxidizer_temperature_k")
        )

    if regen_active:
        # =====================================================
        # FINAL PASS — REGEN DEFAULTS
        # =====================================================

        final_results["selected_station_length"] = calculate_selected_station_length_default(
            selected_station_length=final_results.get("selected_station_length")
        )

        final_results["coolant_flow_fraction"] = calculate_coolant_flow_fraction_default(
            coolant_flow_fraction=final_results.get("coolant_flow_fraction")
        )

        # =====================================================
        # FINAL PASS — REGENERATIVE COOLING GEOMETRY
        # =====================================================


        final_results["channel_pitch"] = calculate_channel_pitch(
            coolant_channel_width=final_results.get("coolant_channel_width"),
            rib_width=final_results.get("rib_width")
        )

        final_results["channel_mid_radius"] = calculate_channel_mid_radius(
            cross_sectional_area=final_results.get("cross_sectional_area"),
            throat_radius=final_results.get("throat_radius"),
            coating_thickness=final_results.get("coating_thickness"),
            hot_gas_wall_thickness=final_results.get("hot_gas_wall_thickness"),
            coolant_channel_height=final_results.get("coolant_channel_height")
        )

        final_results["circumferential_channel_pitch"] = calculate_circumferential_channel_pitch(
            channel_mid_radius=final_results.get("channel_mid_radius"),
            number_of_coolant_channels=final_results.get("number_of_coolant_channels")
        )

        final_results["effective_rib_width"] = calculate_effective_rib_width(
            circumferential_channel_pitch=final_results.get("circumferential_channel_pitch"),
            coolant_channel_width=final_results.get("coolant_channel_width")
        )

        final_results["channel_fit_ratio"] = calculate_channel_fit_ratio(
            required_channel_pitch=final_results.get("channel_pitch"),
            circumferential_channel_pitch=final_results.get("circumferential_channel_pitch")
        )

        final_results["channel_geometry_valid"] = calculate_channel_geometry_valid(
            effective_rib_width=final_results.get("effective_rib_width"),
            requested_rib_width=final_results.get("rib_width"),
            channel_fit_ratio=final_results.get("channel_fit_ratio"),
            required_channel_pitch=final_results.get("channel_pitch"),
            circumferential_channel_pitch=final_results.get("circumferential_channel_pitch")
        )

        # =====================================================
        # FINAL PASS — SCALABLE REGEN DESIGN CONSTRAINTS
        # =====================================================
        # User requirements override these derived values.
        # The optimiser should use derived constraints, not fixed universal values.
        # =====================================================

        final_results = derive_regen_design_constraints(final_results)

        auto_geometry = calculate_regen_geometry_auto_sizing(
            channel_mid_radius=final_results.get("channel_mid_radius"),
            coolant_mass_flow_rate=final_results.get("coolant_mass_flow_rate"),
            coolant_density=final_results.get("coolant_density"),
            coolant_dynamic_viscosity=final_results.get("coolant_dynamic_viscosity"),
            target_reynolds_number=final_results.get("regen_target_reynolds_number"),
            minimum_rib_width=final_results.get("regen_derived_minimum_rib_width"),
            minimum_channel_width=final_results.get("regen_derived_minimum_channel_width"),
            maximum_channel_height=final_results.get("regen_derived_maximum_channel_height"),
            channel_aspect_ratio=final_results.get("regen_channel_aspect_ratio"),
            minimum_channel_count=final_results.get("regen_derived_minimum_channel_count"),
            maximum_channel_count=final_results.get("regen_derived_maximum_channel_count"),
            maximum_coolant_velocity=final_results.get("regen_derived_maximum_coolant_velocity"),
            minimum_hydraulic_diameter=final_results.get("regen_derived_minimum_hydraulic_diameter"),
            pressure_drop_limit=final_results.get("regen_derived_pressure_drop_limit"),
            nozzle_length=final_results.get("nozzle_length"),
            minimum_cooling_coverage=final_results.get("regen_derived_minimum_cooling_coverage")
        )

        if auto_geometry is not None:
            final_results.update(auto_geometry)

            # =====================================================
            # FINAL PASS — RECOMMENDED GEOMETRY THERMAL PREVIEW
            # =====================================================
            # Runs a second non-destructive axial solve using recommended geometry.
            # Manual regen results remain unchanged.
            # =====================================================

            pass  # PFQ-2D-R5E: authority call moved to pre-consumer chain

            final_results = calculate_base_wall_thermal_expansion_strain(final_results)
            final_results = apply_regen_material_fallbacks(final_results)
            final_results = calculate_recommended_regen_thermal_preview(final_results)
            final_results = build_variable_channel_geometry_profile(final_results)
            final_results = build_velocity_limited_variable_channel_geometry_profile(final_results)
            final_results = build_variable_geometry_thermal_preview(final_results)

            final_results = evaluate_full_engine_regen_geometry_gates(
                final_results,
                geometry_profile_key="velocity_limited_variable_geometry_profile",
                thermal_profile_key="variable_geometry_thermal_profile",
            )

            final_results = select_best_full_engine_regen_design(final_results)

            final_results = build_velocity_limited_combined_thermal_preview(final_results)
            final_results = calculate_velocity_limited_required_improvements(final_results)
            final_results = evaluate_velocity_limited_improvement_options(final_results)
            final_results = build_velocity_limited_split_strategy_preview(final_results)
            final_results = build_coupled_split_strategy_marching_preview(final_results)
            final_results = calculate_coupled_split_required_improvements(final_results)
            final_results = build_coupled_split_auto_tuned_preview(final_results)
            final_results = translate_coupled_auto_tuned_target(final_results)
            final_results = screen_materials_against_coupled_auto_target(final_results)
            final_results = rebalance_coupled_auto_target_if_material_fails(final_results)
            final_results = evaluate_coupled_auto_rebalance_options(final_results)
            final_results = build_coupled_auto_balanced_rebalance_preview(final_results)
            final_results = evaluate_coating_liner_gap_for_balanced_rebalance(final_results)
            final_results = size_required_coating_liner_for_balanced_rebalance(final_results)
            final_results = screen_coating_materials_for_required_liner(final_results)
            final_results = assess_coating_material_data_quality(final_results)
            final_results = build_explicit_coating_liner_preview(final_results)
            final_results = finalize_coating_stack_validation_gate(final_results)
            final_results = build_coating_stack_evidence_matrix(final_results)
            final_results = build_coating_stack_validation_roadmap(final_results)
            final_results = classify_coating_stack_data_mode(final_results)
            final_results = build_coating_stack_certification_checklist(final_results)
            final_results = build_coating_stack_risk_register(final_results)
            final_results = build_coating_stack_risk_burndown_plan(final_results)
            final_results = build_coating_stack_priority_action_plan(final_results)
            final_results = build_coating_stack_source_data_checklist(final_results)
            final_results = build_coating_stack_executive_summary(final_results)
            final_results = build_coating_stack_dashboard_payload(final_results)
            final_results = build_coating_stack_ui_warning_cards(final_results)
            final_results = build_coating_stack_export_summary(final_results)
            final_results = validate_recommended_regen_viability(final_results)
            final_results = solve_regen_cooling_feasibility(final_results)
            final_results = select_regen_cooling_strategy(final_results)
            final_results = estimate_film_cooling_requirement(final_results)
            final_results = build_axial_film_cooling_preview(final_results)
            final_results = evaluate_cooling_strategy_trade_study(final_results)
            final_results = allocate_combined_cooling_targets(final_results)
            final_results = build_film_material_axial_preview(final_results)
            final_results = build_full_combined_component_axial_preview(final_results)
            final_results = evaluate_material_candidates_for_cooling(final_results)
            final_results = run_material_aware_combined_cooling_optimiser(final_results)
            final_results = predict_combined_cooling_outcome(final_results)
            final_results = build_combined_cooling_axial_preview(final_results)
            final_results = determine_final_regen_design_verdict(final_results)

            final_results = apply_material_and_coating_source_validation_modes(final_results)

            final_results = validate_against_reference_engine(final_results)

            final_results = audit_coating_stack_validation_system(final_results)
            final_results = build_final_regen_verdict_review_summary(final_results)
            final_results = build_report_system_completion_status(final_results)
            final_results = update_regen_required_next_steps(final_results)
            final_results = assess_combined_cooling_confidence(final_results)

            manual_re = final_results.get("regen_axial_min_reynolds_number") or final_results.get("coolant_reynolds_number")
            recommended_re = final_results.get("recommended_coolant_reynolds_number")

            if manual_re is not None and recommended_re is not None and manual_re > 0:
                final_results["recommended_reynolds_improvement_factor"] = recommended_re / manual_re

            manual_valid = final_results.get("channel_geometry_valid")
            recommended_valid = final_results.get("recommended_channel_geometry_valid")

            if manual_valid != 1 and recommended_valid == 1:
                final_results["recommended_geometry_note"] = (
                    "Recommended geometry physically fits, while current manual geometry does not."
                )
            elif recommended_re is not None and manual_re is not None and recommended_re > manual_re:
                final_results["recommended_geometry_note"] = (
                    "Recommended geometry improves Reynolds number compared with current manual geometry."
                )
            else:
                final_results["recommended_geometry_note"] = (
                    "Recommended geometry is available for comparison."
                )

        final_results["regen_cross_section_outer_radius"] = calculate_regen_cross_section_outer_radius(
            cross_sectional_area=final_results.get("cross_sectional_area"),
            throat_radius=final_results.get("throat_radius"),
            hot_gas_wall_thickness=final_results.get("hot_gas_wall_thickness"),
            coolant_channel_height=final_results.get("coolant_channel_height"),
            outer_jacket_thickness=final_results.get("outer_jacket_thickness"),
            coating_thickness=final_results.get("coating_thickness")
        )

    # =====================================================
    # FINAL PASS — VOLUMETRIC FLOW
    # =====================================================

    final_results["total_propellant_volume_flow_rate"] = calculate_total_propellant_volume_flow_rate(
        fuel_mass_flow_rate=final_results.get("fuel_mass_flow_rate"),
        oxidizer_mass_flow_rate=final_results.get("oxidizer_mass_flow_rate"),
        fuel_density=final_results.get("fuel_density"),
        oxidizer_density=final_results.get("oxidizer_density")
    )

    # =====================================================
    # FINAL PASS — IDEAL ENGINE OUTPUTS
    # =====================================================

    final_results["ideal_engine_thrust"] = calculate_ideal_engine_thrust(
        thrust=final_results.get("thrust")
    )

    final_results["ideal_engine_specific_impulse"] = calculate_ideal_engine_specific_impulse(
        ideal_engine_thrust=final_results.get("ideal_engine_thrust"),
        mass_flow_rate=final_results.get("mass_flow_rate")
    )

    final_results["ideal_volumetric_thrust"] = calculate_ideal_volumetric_thrust(
        ideal_engine_thrust=final_results.get("ideal_engine_thrust"),
        total_propellant_volume_flow_rate=final_results.get("total_propellant_volume_flow_rate")
    )

    # =====================================================
    # FINAL PASS — CORRECTED ENGINE OUTPUTS
    # =====================================================

    final_results["volumetric_corrected_thrust"] = calculate_volumetric_corrected_thrust(
        corrected_thrust=final_results.get("corrected_thrust"),
        total_propellant_volume_flow_rate=final_results.get("total_propellant_volume_flow_rate")
    )

    if regen_active:
        # =====================================================
        # FINAL PASS — AXIAL REGENERATIVE COOLING PROFILE
        # =====================================================
        # This does not replace the selected-station regen model.
        # It adds whole-nozzle marching outputs for later plotting,
        # diagnostics, and station-table display.
        # =====================================================

        # =====================================================
        # FINAL PASS — REGEN MATERIAL FALLBACKS
        # =====================================================

        final_results = apply_regen_material_fallbacks(final_results)

        if attach_material_thermal_conductivity_integration_owner is not None:
            pass  # PFQ-2D-R5E: authority call moved to pre-consumer chain

        if attach_material_specific_heat_integration_owner is not None:
            pass  # PFQ-2D-R5E: authority call moved to pre-consumer chain

        if attach_material_density_integration_owner is not None:
            pass  # PFQ-2D-R5E: authority call moved to pre-consumer chain

        if attach_material_temperature_limit_integration_owner is not None:
            pass  # PFQ-2D-R5E: authority call moved to pre-consumer chain

        if attach_material_strength_limit_integration_owner is not None:
            pass  # PFQ-2D-R5E: authority call moved to pre-consumer chain

        if attach_coating_thermal_conductivity_integration_owner is not None:
            final_results = attach_coating_thermal_conductivity_integration_owner(final_results)

        if attach_coating_thickness_integration_owner is not None:
            final_results = attach_coating_thickness_integration_owner(final_results)

        if attach_coating_thermal_resistance_integration_owner is not None:
            final_results = attach_coating_thermal_resistance_integration_owner(final_results)

        if attach_coating_temperature_limit_integration_owner is not None:
            final_results = attach_coating_temperature_limit_integration_owner(final_results)

        if attach_bond_coat_integration_owner is not None:
            final_results = attach_bond_coat_integration_owner(final_results)

        regen_axial_station_count_setting = final_results.get(
            "regen_axial_requested_station_count",
            final_results.get(
                "axial_station_count",
                DEFAULT_REGEN_AXIAL_STATION_COUNT,
            )
        )

        final_results["regen_axial_requested_station_count"] = regen_axial_station_count_setting

        final_results = calculate_regen_axial_marching_profile(
            final_results,
            station_count=regen_axial_station_count_setting
        )

        # =====================================================
        # FINAL PASS — HARD REGEN VALIDATION GATE
        # =====================================================

        regen_station_count = final_results.get("regen_axial_requested_station_count")

        if regen_station_count is None:
            regen_station_count = (
                DEFAULT_REGEN_AXIAL_STATION_COUNT
            )

        final_results["regen_axial_requested_station_count"] = regen_station_count

        final_results = calculate_regen_axial_marching_profile(
            final_results,
            station_count=regen_station_count
        )
        final_results = evaluate_coating_database_visibility(final_results)
        final_results = evaluate_active_coating_stack_selection(final_results)
        final_results = evaluate_explicit_coating_thermal_resistance_preview(final_results)
        final_results = recommend_coating_stack_candidate(final_results)
        final_results = build_recommended_design_package(final_results)
        final_results = build_regen_optimisation_proof(final_results)
        final_results = ensure_coating_stack_source_data_gate_outputs(final_results)
        final_results = validate_regen_consistency(final_results)
        final_results = apply_regen_failure_statuses(final_results)

        # =====================================================
        # FINAL PASS — BEST FULL-ENGINE REGEN DESIGN SELECTOR
        # =====================================================
        # Run this at the very end so the best-design outputs are always
        # populated from the latest available axial/candidate profiles.
        # This does not fake a PASS; it only selects the best available
        # candidate and reports FAIL_BEST_AVAILABLE when hard gates fail.
        # =====================================================

        final_results = select_best_full_engine_regen_design(final_results)

        # =====================================================
        # PHASE 11B.1A — FULL ENGINE REGEN CANDIDATE GENERATOR
        # =====================================================
        # Generates non-destructive candidate alternatives when
        # the current regen design cannot pass. This does not
        # validate, rank, select, or apply geometry yet.
        # =====================================================

        if execution_scope == "graph":
            return final_results, legacy_history

        if attach_regen_candidate_generator is not None:
            final_results = attach_regen_candidate_generator(final_results)

        if attach_regen_candidate_validator is not None:
            if not bool(params.get("_leaf_48s_off_nominal_scenario_active", False)):
                attach_regen_off_nominal_qualification(
                    params=params,
                    results=final_results,
                    execution_scope=execution_scope,
                    module_execution_policy=module_execution_policy,
                )

            final_results = attach_regen_candidate_validator(final_results)

        if bool(
            params.get(
                "_leaf_48u_candidate_qualification_solve_active",
                False,
            )
        ):
            return final_results


        if attach_regen_candidate_ranker is not None:
            final_results = attach_regen_candidate_ranker(final_results)

        if attach_regen_candidate_selector is not None:
            final_results = attach_regen_candidate_selector(final_results)

        if attach_regen_candidate_recommendation_owner is not None:
            final_results = attach_regen_candidate_recommendation_owner(final_results)

        if attach_regen_candidate_application_owner is not None:
            final_results = attach_regen_candidate_application_owner(final_results)

        if attach_regen_candidate_resolve_owner is not None:
            final_results = attach_regen_candidate_resolve_owner(final_results)

        if attach_regen_candidate_resolve_execution_owner is not None:
            final_results = attach_regen_candidate_resolve_execution_owner(final_results)

        if attach_regen_candidate_post_resolve_validation_owner is not None:
            final_results = attach_regen_candidate_post_resolve_validation_owner(final_results)

        if attach_regen_candidate_decision_gate_owner is not None:
            final_results = attach_regen_candidate_decision_gate_owner(final_results)










        if attach_regen_candidate_population_generation_owner is not None:
            final_results = attach_regen_candidate_population_generation_owner(final_results)


        if attach_regen_candidate_population_report_owner is not None:
            final_results = attach_regen_candidate_population_report_owner(final_results)


        if attach_regen_candidate_population_registration_owner is not None:
            final_results = attach_regen_candidate_population_registration_owner(final_results)


        if attach_regen_candidate_population_completion_audit is not None:
            final_results = attach_regen_candidate_population_completion_audit(final_results)


        if attach_regen_candidate_population_master_gate is not None:
            final_results = attach_regen_candidate_population_master_gate(final_results)


        if attach_regen_candidate_ranking_input_audit is not None:
            final_results = attach_regen_candidate_ranking_input_audit(final_results)

        final_results = attach_regen_qualified_candidate_population(
            final_results,
            base_params=params,
            execution_scope=execution_scope,
            module_execution_policy=module_execution_policy,
        )

        if attach_regen_candidate_ranking_owner is not None:
            final_results = attach_regen_candidate_ranking_owner(final_results)


        if attach_regen_candidate_ranking_report_owner is not None:
            final_results = attach_regen_candidate_ranking_report_owner(final_results)


        if attach_regen_candidate_ranking_registration_owner is not None:
            final_results = attach_regen_candidate_ranking_registration_owner(final_results)


        if attach_regen_candidate_ranking_completion_audit is not None:
            final_results = attach_regen_candidate_ranking_completion_audit(final_results)


        if attach_regen_candidate_ranking_master_gate is not None:
            final_results = attach_regen_candidate_ranking_master_gate(final_results)
        # ============================================================
        # RH3 — FINAL AUTOMATIC GEOMETRY FINALISATION
        # ============================================================
        # The earlier selector/recommendation/application pass remains
        # the precursor optimisation checkpoint.
        #
        # Once RPOP qualification and ranking settle, the same
        # canonical owners consume final ranked state.
        #
        # AutonomousGeometryCommit executes once here and owns final
        # user-facing staged automatic geometry.
        # ============================================================

        if attach_regen_candidate_selector is not None:
            final_results = attach_regen_candidate_selector(
                final_results
            )

        if attach_regen_candidate_recommendation_owner is not None:
            final_results = attach_regen_candidate_recommendation_owner(
                final_results
            )

        if attach_regen_candidate_application_owner is not None:
            final_results = attach_regen_candidate_application_owner(
                final_results
            )

        if attach_regen_autonomous_geometry_commit_controller is not None:
            final_results = attach_regen_autonomous_geometry_commit_controller(
                final_results
            )

        if attach_regen_autonomous_geometry_commit_history_owner is not None:
            final_results = attach_regen_autonomous_geometry_commit_history_owner(
                final_results
            )

        if attach_regen_autonomous_geometry_commit_report_owner is not None:
            final_results = attach_regen_autonomous_geometry_commit_report_owner(
                final_results
            )

        if attach_regen_autonomous_geometry_commit_master_gate is not None:
            final_results = attach_regen_autonomous_geometry_commit_master_gate(
                final_results
            )


        candidate_count = final_results.get("regen_candidate_generator_candidate_count", 0)
        pass_count = final_results.get("regen_candidate_validator_pass_count", 0)
        ranked_count = final_results.get("regen_candidate_ranker_ranked_count", 0)
        selected_id = final_results.get("regen_candidate_selector_selected_candidate_id")
        recommendation_id = final_results.get("regen_candidate_recommendation_id")
        application_ready = final_results.get("regen_candidate_application_ready", False)
        resolve_ready = final_results.get("regen_candidate_resolve_ready", False)

        if (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and resolve_ready
        ):
            final_results["best_full_engine_regen_status"] = (
                "PASS_RECOMMENDED_CANDIDATE_RESOLVE_READY"
            )
            final_results["best_full_engine_regen_reason"] = (
                "A full-engine regen candidate has been generated, validated, ranked, "
                "selected, published, converted into an application patch, and prepared "
                "as a cloned patched state for future solver execution. The solver has "
                "not yet been re-run on the cloned candidate."
            )

        elif (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and application_ready
        ):
            final_results["best_full_engine_regen_status"] = (
                "PASS_RECOMMENDED_CANDIDATE_APPLICATION_PATCH_READY"
            )
            final_results["best_full_engine_regen_reason"] = (
                "A full-engine regen candidate has been generated, validated, ranked, "
                "selected, published as a recommendation, and converted into a validated "
                "non-destructive application patch. The active engine geometry has not "
                "yet been overwritten."
            )

        elif (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and recommendation_id
        ):
            final_results["best_full_engine_regen_status"] = (
                "PASS_RECOMMENDED_CANDIDATE_READY_REQUIRES_APPLICATION"
            )
            final_results["best_full_engine_regen_reason"] = (
                "A full-engine regen candidate has been generated, validated, ranked, "
                "selected, and published as the current recommendation. Geometry "
                "application is not yet enabled."
            )

        elif (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and selected_id
        ):
            final_results["best_full_engine_regen_status"] = (
                "PASS_RECOMMENDED_CANDIDATE_SELECTED_REQUIRES_APPLICATION"
            )
            final_results["best_full_engine_regen_reason"] = (
                "A full-engine regen candidate has been generated, validated, ranked, "
                "and selected as the recommended candidate. Geometry application is not "
                "yet enabled."
            )

        elif (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and candidate_count > 0
                and pass_count <= 0
        ):
            final_results["best_full_engine_regen_status"] = (
                "FAIL_CANDIDATES_GENERATED_BUT_NONE_VALIDATED"
            )
            final_results["best_full_engine_regen_reason"] = (
                "Full-engine regen candidates were generated and validated, but no "
                "candidate passed the conservative Phase 11B validator."
            )
        elif (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and pass_count > 0
                and ranked_count <= 0
        ):
            final_results["best_full_engine_regen_status"] = (
                "PASS_VALIDATED_CANDIDATES_FOUND_REQUIRES_RANKING"
            )
            final_results["best_full_engine_regen_reason"] = (
                "One or more regen candidates passed validation, but no candidate ranking "
                "has been completed yet."
            )

        elif (
                final_results.get("best_full_engine_regen_status") == "FAIL_NO_CANDIDATES"
                and ranked_count > 0
        ):
            final_results["best_full_engine_regen_status"] = (
                "PASS_RANKED_CANDIDATES_FOUND_REQUIRES_SELECTION"
            )
            final_results["best_full_engine_regen_reason"] = (
                "One or more full-engine regen candidates passed validation and were ranked. "
                "Best-candidate selection/application is not yet enabled."
            )
    final_results = attach_structural_component_masses(final_results)

    try:
        from leaf_qt.cost_intelligence_owner import (
            attach_cost_intelligence_owner,
        )
    except ImportError:
        from cost_intelligence_owner import (
            attach_cost_intelligence_owner,
        )

    final_results = attach_cost_intelligence_owner(
        final_results
    )

    return final_results, legacy_history

# --------- Main ----------
if __name__ == "__main__":
    params = get_inputs()

    final_params, history = iterative_solver(params)

    print("\n--- Directed Solver Final Parameters ---")
    for key, value in final_params.items():
        print(f"{key}: {value}")

# ============================================================
# PHASE 16T.3K.9 — ENGINE SOLVER STATUS ADAPTER
# ============================================================
#
# This section intentionally sits at the end of engine_solver.py so it can
# wrap the existing solver entry points without rewriting the physics solver.
#
# Legacy contracts preserved:
# - solve_engine(inputs) -> dict
# - iterative_solver(params) -> (dict, history)
#
# New status-adapter outputs:
# - engine_solver_structured_findings
# - engine_solver_global_status
# - engine_solver_global_status_payload
# - engine_solver_status_adapter_report
# - phase_16t3k9_status_adapter_complete


try:
    from leaf_qt.global_status_classification_engine import (
        classify_status as _leaf_status_classify_status,
        make_finding as _leaf_status_make_finding,
    )
except Exception:  # pragma: no cover - defensive fallback for unusual launch contexts
    _leaf_status_classify_status = None
    _leaf_status_make_finding = None
