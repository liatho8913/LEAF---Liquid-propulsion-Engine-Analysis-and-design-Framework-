from fluid_property_database import (
    get_fluid_properties,
    get_fluid_properties_at_temperature,
)


def get_coolant_properties(coolant_name):
    properties = get_fluid_properties(coolant_name)

    if properties is None:
        return None

    return {
        "density": properties.get("density"),
        "dynamic_viscosity": properties.get("dynamic_viscosity"),
        "specific_heat_cp": properties.get("specific_heat_cp"),
        "thermal_conductivity": properties.get("thermal_conductivity"),
        "default_inlet_temperature": properties.get("default_temperature"),
    }


def get_coolant_properties_at_temperature(coolant_name, temperature_k=None):
    properties = get_fluid_properties_at_temperature(coolant_name, temperature_k)

    if properties is None:
        return None

    return {
        "density": properties.get("density"),
        "dynamic_viscosity": properties.get("dynamic_viscosity"),
        "specific_heat_cp": properties.get("specific_heat_cp"),
        "thermal_conductivity": properties.get("thermal_conductivity"),
        "default_inlet_temperature": properties.get("default_temperature"),
        "property_temperature": properties.get("property_temperature"),
    }