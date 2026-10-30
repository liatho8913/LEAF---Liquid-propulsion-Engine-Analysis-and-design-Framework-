import math


FLUID_PROPERTY_DATABASE = {
    "RP-1 / Kerosene": {
    "aliases": ["RP-1", "RP1", "Kerosene", "RP-1 / KEROSENE"],
        "phase": "liquid",
        "density": 810.0,
        "dynamic_viscosity": 0.0016,
        "specific_heat_cp": 2000.0,
        "thermal_conductivity": 0.13,
        "reference_temperature": 293.0,
        "default_temperature": 293.0,
        "model": "rp1",
    },
    "Liquid Methane": {
        "aliases": ["LCH4", "Methane", "CH4"],
        "phase": "liquid",
        "density": 422.0,
        "dynamic_viscosity": 0.00011,
        "specific_heat_cp": 3500.0,
        "thermal_conductivity": 0.20,
        "reference_temperature": 111.0,
        "default_temperature": 111.0,
        "model": "methane",
    },
    "Liquid Hydrogen": {
        "aliases": ["LH2", "Hydrogen", "H2"],
        "phase": "liquid",
        "density": 70.85,
        "dynamic_viscosity": 0.000013,
        "specific_heat_cp": 9700.0,
        "thermal_conductivity": 0.10,
        "reference_temperature": 20.0,
        "default_temperature": 20.0,
        "model": "hydrogen",
    },
    "Liquid Oxygen": {
    "aliases": ["LOX", "LO2", "O2(L)"],
        "phase": "liquid",
        "density": 1141.0,
        "dynamic_viscosity": 0.00020,
        "specific_heat_cp": 1700.0,
        "thermal_conductivity": 0.15,
        "reference_temperature": 90.0,
        "default_temperature": 90.0,
        "model": "oxygen",
    },
    "Water": {
        "aliases": [],
        "phase": "liquid",
        "density": 997.0,
        "dynamic_viscosity": 0.00089,
        "specific_heat_cp": 4180.0,
        "thermal_conductivity": 0.60,
        "reference_temperature": 293.0,
        "default_temperature": 293.0,
        "model": "water",
    },
    "Ethanol": {
            'aliases': [],
            'phase': 'liquid',
            'density': 789.5490982765879,
            'dynamic_viscosity': 0.001204548052505962,
            'specific_heat_cp': 2394.849170714777,
            'thermal_conductivity': 0.16450136474831714,
            'reference_temperature': 293.0,
            'default_temperature': 293.0,
            'model': 'ethanol',
            'reference_pressure': 101325.0,
            'source_authority': 'NIST_REFPROP_ETHANOL_FLD',
            'source_model': 'FEQ_SCHROEDER_2014',
            "transport_models": {
                'dynamic_viscosity': 'VS7_SOTIRIADOU_2022_WITH_PUBLISHED_CORRECTION',
                'thermal_conductivity': 'TC1_ASSAEL_2013_BASE_CORRELATION_TARGET_DOMAIN',
            },
            "source_state": {
                'phase': 'liquid',
                'pressure_Pa': 101325.0,
                'temperature_K': 293.0,
            },
            "source_identity": {
                'ETHANOL_FLD_sha256': '15767630c6995519a8b7975cbb649be0dc9ea316a9c69f7d1440e90018e54c1e',
            },
            "temperature_model_status": 'LEGACY_ENGINEERING_APPROXIMATION_NOT_SOURCE_QUALIFIED',
        },
}


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def normalise_fluid_name(fluid_name):
    if fluid_name is None:
        return None

    requested = str(fluid_name).strip().lower()

    for canonical, data in FLUID_PROPERTY_DATABASE.items():
        if requested == canonical.lower():
            return canonical

        for alias in data.get("aliases", []):
            if requested == alias.lower():
                return canonical

    return None


def get_fluid_properties(fluid_name):
    canonical = normalise_fluid_name(fluid_name)

    if canonical is None:
        return None

    data = dict(FLUID_PROPERTY_DATABASE[canonical])
    data["name"] = canonical
    return data


def get_fluid_properties_at_temperature(fluid_name, temperature_k=None):
    data = get_fluid_properties(fluid_name)

    if data is None:
        return None

    if temperature_k is None:
        temperature_k = data.get("default_temperature")

    try:
        temperature_k = float(temperature_k)
    except Exception:
        temperature_k = data.get("default_temperature")

    if not math.isfinite(temperature_k):
        temperature_k = data.get("default_temperature")

    reference_temperature = data.get("reference_temperature", temperature_k)
    delta_t = temperature_k - reference_temperature

    rho_ref = data.get("density")
    mu_ref = data.get("dynamic_viscosity")
    cp_ref = data.get("specific_heat_cp")
    k_ref = data.get("thermal_conductivity")

    model = data.get("model")

    if model == "rp1":
        density = rho_ref * (1.0 - 0.00095 * delta_t)
        viscosity = mu_ref * math.exp(-0.020 * delta_t)
        cp = cp_ref * (1.0 + 0.00050 * delta_t)
        conductivity = k_ref * (1.0 - 0.00030 * delta_t)

    elif model == "methane":
        density = rho_ref * (1.0 - 0.00200 * delta_t)
        viscosity = mu_ref * math.exp(-0.015 * delta_t)
        cp = cp_ref * (1.0 + 0.00100 * delta_t)
        conductivity = k_ref * (1.0 - 0.00050 * delta_t)

    elif model == "hydrogen":
        density = rho_ref * (1.0 - 0.00400 * delta_t)
        viscosity = mu_ref * math.exp(-0.010 * delta_t)
        cp = cp_ref * (1.0 + 0.00030 * delta_t)
        conductivity = k_ref * (1.0 - 0.00020 * delta_t)

    elif model == "oxygen":
        density = rho_ref * (1.0 - 0.00300 * delta_t)
        viscosity = mu_ref * math.exp(-0.012 * delta_t)
        cp = cp_ref * (1.0 + 0.00040 * delta_t)
        conductivity = k_ref * (1.0 - 0.00025 * delta_t)

    elif model == "water":
        density = rho_ref * (1.0 - 0.00030 * delta_t)
        viscosity = mu_ref * math.exp(-0.025 * delta_t)
        cp = cp_ref * (1.0 + 0.00010 * delta_t)
        conductivity = k_ref * (1.0 - 0.00020 * delta_t)

    elif model == "ethanol":
        density = rho_ref * (1.0 - 0.00110 * delta_t)
        viscosity = mu_ref * math.exp(-0.020 * delta_t)
        cp = cp_ref * (1.0 + 0.00060 * delta_t)
        conductivity = k_ref * (1.0 - 0.00030 * delta_t)

    else:
        density = rho_ref
        viscosity = mu_ref
        cp = cp_ref
        conductivity = k_ref

    data["property_temperature"] = temperature_k
    data["density"] = clamp(density, rho_ref * 0.05, rho_ref * 1.5)
    data["dynamic_viscosity"] = clamp(viscosity, mu_ref * 0.05, mu_ref * 20.0)
    data["specific_heat_cp"] = clamp(cp, cp_ref * 0.5, cp_ref * 3.0)
    data["thermal_conductivity"] = clamp(conductivity, k_ref * 0.25, k_ref * 2.0)

    return data


def get_fluid_density(fluid_name, temperature_k=None):
    canonical = normalise_fluid_name(fluid_name)

    if canonical is None:
        return None

    if canonical == "Ethanol":
        if temperature_k is None:
            properties = get_fluid_properties(canonical)

            if properties is None:
                return None

            return properties.get("density")

        from leaf_qt.thermophysical_property_backend import (
            get_source_qualified_density,
        )

        return get_source_qualified_density(
            canonical,
            temperature_k,
            101325.0,
        )

    properties = get_fluid_properties_at_temperature(
        fluid_name,
        temperature_k,
    )

    if properties is None:
        return None

    return properties.get("density")