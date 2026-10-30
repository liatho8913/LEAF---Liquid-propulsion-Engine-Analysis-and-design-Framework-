from collections import OrderedDict


FUEL_DATABASE = OrderedDict({
    "LCH4": {
        "display_name": "Liquid Methane",
        "aliases": ["CH4", "Methane"],
        "cea_name": "CH4",
        "default_temperature_k": 111.0,
        "density_kg_m3": 422.0,
        "compatible_oxidizers": ["O2(L)", "LOX", "O2", "GOX", "N2O"],
    },
    "GCH4": {
        "display_name": "Gaseous Methane",
        "aliases": ["Gaseous Methane"],
        "cea_name": "CH4",
        "default_temperature_k": 298.0,
        "density_kg_m3": 0.656,
        "compatible_oxidizers": ["O2", "GOX", "O2(L)", "LOX", "N2O"],
    },

    "LH2": {
        "display_name": "Liquid Hydrogen",
        "aliases": ["H2", "Hydrogen"],
        "cea_name": "H2",
        "default_temperature_k": 20.0,
        "density_kg_m3": 70.85,
        "compatible_oxidizers": ["O2(L)", "LOX", "O2", "GOX"],
    },
    "GH2": {
        "display_name": "Gaseous Hydrogen",
        "aliases": ["Gaseous Hydrogen"],
        "cea_name": "H2",
        "default_temperature_k": 298.0,
        "density_kg_m3": 0.08375,
        "compatible_oxidizers": ["O2", "GOX", "O2(L)", "LOX"],
    },

    "RP-1 / Kerosene": {
        "display_name": "RP-1 / Kerosene",
        "aliases": ["RP-1", "RP1", "Kerosene"],
        "cea_name": "RP-1 / Kerosene",
        "default_temperature_k": 298.0,
        "density_kg_m3": 810.0,
        "compatible_oxidizers": ["O2(L)", "LOX", "O2", "GOX", "N2O", "H2O2", "90_H2O2", "98_H2O2"],
    },
    "Jet-A": {
        "display_name": "Jet-A",
        "aliases": ["JetA", "Jet A"],
        "cea_name": "Jet-A",
        "default_temperature_k": 298.0,
        "density_kg_m3": 804.0,
        "compatible_oxidizers": ["O2(L)", "LOX", "O2", "GOX", "N2O", "H2O2", "90_H2O2", "98_H2O2"],
    },

    "Ethanol": {
        "display_name": "Ethanol",
        "aliases": ["C2H5OH"],
        "cea_name": "Ethanol",
        "default_temperature_k": 298.0,
        "density_kg_m3": 789.0,
        "compatible_oxidizers": ["O2(L)", "LOX", "O2", "GOX", "N2O", "H2O2", "90_H2O2", "98_H2O2"],
    },
    "Methanol": {
        "display_name": "Methanol",
        "aliases": ["CH3OH"],
        "cea_name": "Methanol",
        "default_temperature_k": 298.0,
        "density_kg_m3": 792.0,
        "compatible_oxidizers": ["O2(L)", "LOX", "O2", "GOX", "N2O", "H2O2", "90_H2O2", "98_H2O2"],
    },

    "MMH": {
        "display_name": "MMH",
        "aliases": ["Monomethylhydrazine"],
        "cea_name": "MMH",
        "default_temperature_k": 298.0,
        "density_kg_m3": 880.0,
        "compatible_oxidizers": ["N2O4", "MON3", "MON15", "MON25"],
    },
    "UDMH": {
        "display_name": "UDMH",
        "aliases": ["Unsymmetrical Dimethylhydrazine"],
        "cea_name": "UDMH",
        "default_temperature_k": 298.0,
        "density_kg_m3": 793.0,
        "compatible_oxidizers": ["N2O4", "MON3", "MON15", "MON25"],
    },
    "N2H4": {
        "display_name": "Hydrazine",
        "aliases": ["Hydrazine"],
        "cea_name": "N2H4",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1004.0,
        "compatible_oxidizers": ["N2O4", "MON3", "MON15", "MON25", "H2O2", "90_H2O2", "98_H2O2"],
    },
})


OXIDIZER_DATABASE = OrderedDict({
    "O2(L)": {
        "display_name": "O2 (L)",
        "aliases": ["LOX", "LO2", "O2 (L)"],
        "cea_name": "O2(L)",
        "default_temperature_k": 90.0,
        "density_kg_m3": 1141.0,
    },
    "O2": {
        "display_name": "O2 (G)",
        "aliases": ["GOX", "O2 (G)"],
        "cea_name": "O2",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1.429,
    },
    "N2O": {
        "display_name": "Nitrous Oxide",
        "aliases": ["Nitrous Oxide"],
        "cea_name": "N2O",
        "default_temperature_k": 184.0,
        "density_kg_m3": 750.0,
    },
    "N2O4": {
        "display_name": "Nitrogen Tetroxide",
        "aliases": ["NTO"],
        "cea_name": "N2O4",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1440.0,
    },
    "MON3": {
        "display_name": "MON3",
        "aliases": [],
        "cea_name": "MON3",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1440.0,
    },
    "MON15": {
        "display_name": "MON15",
        "aliases": [],
        "cea_name": "MON15",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1430.0,
    },
    "MON25": {
        "display_name": "MON25",
        "aliases": [],
        "cea_name": "MON25",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1420.0,
    },
    "H2O2": {
        "display_name": "Hydrogen Peroxide",
        "aliases": [],
        "cea_name": "H2O2",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1450.0,
    },
    "90_H2O2": {
        "display_name": "90% H2O2",
        "aliases": ["90% Hydrogen Peroxide"],
        "cea_name": "90_H2O2",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1390.0,
    },
    "98_H2O2": {
        "display_name": "98% H2O2",
        "aliases": ["98% Hydrogen Peroxide"],
        "cea_name": "98_H2O2",
        "default_temperature_k": 298.0,
        "density_kg_m3": 1430.0,
    },
})


def _normalise_text(value):
    return str(value or "").strip()


def _normalise_key(value):
    return _normalise_text(value).upper().replace(" ", "").replace("-", "").replace("_", "").replace("/", "")


def _find_canonical(value, database, fallback):
    value = _normalise_text(value)

    if not value:
        return fallback

    if value in database:
        return value

    value_key = _normalise_key(value)

    for canonical, data in database.items():
        if value_key == _normalise_key(canonical):
            return canonical

        if value_key == _normalise_key(data.get("display_name")):
            return canonical

        for alias in data.get("aliases", []):
            if value_key == _normalise_key(alias):
                return canonical

    return value


def canonical_fuel(value):
    return _find_canonical(value, FUEL_DATABASE, "LCH4")


def canonical_oxidizer(value):
    return _find_canonical(value, OXIDIZER_DATABASE, "O2(L)")


def get_all_fuel_options():
    return list(FUEL_DATABASE.keys())


def get_all_oxidizer_options():
    return list(OXIDIZER_DATABASE.keys())


def get_oxidizer_display_name(oxidizer):
    canonical = canonical_oxidizer(oxidizer)

    return str(
        OXIDIZER_DATABASE
        .get(canonical, {})
        .get("display_name", canonical)
    )


def get_all_oxidizer_display_options():
    return [
        get_oxidizer_display_name(oxidizer)
        for oxidizer
        in get_all_oxidizer_options()
    ]


def get_compatible_oxidizer_display_options_for_fuel(fuel):
    display_options = []
    seen_canonical = set()

    for oxidizer in get_compatible_oxidizers_for_fuel(fuel):
        canonical = canonical_oxidizer(oxidizer)

        if canonical in seen_canonical:
            continue

        seen_canonical.add(
            canonical
        )

        display_options.append(
            get_oxidizer_display_name(
                canonical
            )
        )

    return display_options


def get_compatible_oxidizers_for_fuel(fuel):
    fuel = canonical_fuel(fuel)

    if fuel not in FUEL_DATABASE:
        return get_all_oxidizer_options()

    return list(FUEL_DATABASE[fuel]["compatible_oxidizers"])


def get_compatible_fuels_for_oxidizer(oxidizer):
    oxidizer = canonical_oxidizer(oxidizer)

    compatible = []

    for fuel, data in FUEL_DATABASE.items():
        if oxidizer in data["compatible_oxidizers"]:
            compatible.append(fuel)

    return compatible or get_all_fuel_options()


def get_default_fuel_temperature_k(fuel):
    fuel = canonical_fuel(fuel)
    return float(FUEL_DATABASE.get(fuel, {}).get("default_temperature_k", 298.0))


def get_default_oxidizer_temperature_k(oxidizer):
    oxidizer = canonical_oxidizer(oxidizer)
    return float(OXIDIZER_DATABASE.get(oxidizer, {}).get("default_temperature_k", 298.0))


def get_cea_fuel_name(fuel):
    fuel = canonical_fuel(fuel)
    return FUEL_DATABASE.get(fuel, {}).get("cea_name", fuel)


def get_cea_oxidizer_name(oxidizer):
    oxidizer = canonical_oxidizer(oxidizer)
    return OXIDIZER_DATABASE.get(oxidizer, {}).get("cea_name", oxidizer)


def is_compatible_pair(fuel, oxidizer):
    fuel = canonical_fuel(fuel)
    oxidizer = canonical_oxidizer(oxidizer)
    return oxidizer in get_compatible_oxidizers_for_fuel(fuel)

def get_fuel_density_kg_m3(fuel):
    fuel = canonical_fuel(fuel)
    return float(
        FUEL_DATABASE.get(fuel, {}).get("density_kg_m3", 1000.0)
    )


def get_oxidizer_density_kg_m3(oxidizer):
    oxidizer = canonical_oxidizer(oxidizer)
    return float(
        OXIDIZER_DATABASE.get(oxidizer, {}).get("density_kg_m3", 1000.0)
    )

def get_propellant_state_note(fuel, oxidizer):
    fuel = canonical_fuel(fuel)
    oxidizer = canonical_oxidizer(oxidizer)

    notes = []

    if fuel.startswith("G"):
        notes.append("Fuel is stored as gas; volume metrics will be very large.")

    if oxidizer == "O2":
        notes.append("Oxidizer is gaseous oxygen / GOX; tank-volume metrics will be very large.")

    if oxidizer == "O2(L)":
        notes.append("Oxidizer is liquid oxygen / LOX; volume metrics use liquid storage density.")

    return " ".join(notes)

def get_of_ratio_range_for_pair(fuel, oxidizer):
    fuel = canonical_fuel(fuel)
    oxidizer = canonical_oxidizer(oxidizer)

    oxygen_oxidizers = {"O2(L)", "O2"}
    peroxide_oxidizers = {"H2O2", "90_H2O2", "98_H2O2"}
    nitrous_oxidizers = {"N2O"}
    nitrogen_tetroxide_oxidizers = {"N2O4", "MON3", "MON15", "MON25"}

    if oxidizer in oxygen_oxidizers:
        if fuel in {"LH2", "GH2"}:
            return 3.0, 8.5
        if fuel in {"LCH4", "GCH4"}:
            return 1.5, 4.5
        if fuel in {"RP-1 / Kerosene", "Jet-A"}:
            return 1.2, 3.8
        if fuel in {"Ethanol", "Methanol"}:
            return 0.8, 3.5

    if oxidizer in nitrous_oxidizers:
        if fuel in {"LCH4", "GCH4"}:
            return 3.0, 8.0
        if fuel in {"RP-1 / Kerosene", "Jet-A"}:
            return 3.0, 8.5
        if fuel in {"Ethanol", "Methanol"}:
            return 2.0, 7.0

    if oxidizer in peroxide_oxidizers:
        if fuel in {"RP-1 / Kerosene", "Jet-A"}:
            return 4.0, 9.0
        if fuel in {"Ethanol", "Methanol", "N2H4"}:
            return 2.5, 8.0

    if oxidizer in nitrogen_tetroxide_oxidizers:
        if fuel in {"MMH", "UDMH", "N2H4"}:
            return 1.0, 3.5

    return 0.5, 6.0