# =========================================================
# REGENERATIVE COOLING MATERIAL DATABASE
# =========================================================
#
# Units:
# density                         kg/m^3
# yield_strength                  Pa
# ultimate_tensile_strength       Pa
# thermal_conductivity            W/(m*K)
# specific_heat                   J/(kg*K)
# melting_point                   K
# max_recommended_wall_temperature K
# thermal_expansion               1/K
# elastic_modulus                 Pa
# poisson_ratio                   dimensionless
#
# Important:
# These are engineering reference defaults.
# Real properties depend heavily on temperature, heat treatment,
# manufacturing method, build direction, and supplier data.

# =========================================================
# SOURCE VALIDATION MODES
# =========================================================

PLACEHOLDER_MODE = "PLACEHOLDER_MODE"
PARTIAL_SOURCE_MODE = "PARTIAL_SOURCE_MODE"
SOURCED_VALIDATION_MODE = "SOURCED_VALIDATION_MODE"
INSUFFICIENT_SOURCE_MODE = "INSUFFICIENT_SOURCE_MODE"

SOURCE_QUALITY_RANKS = {
    "placeholder": 0,
    "engineering_reference_placeholder": 5,
    "engineering estimate": 10,
    "engineering_reference": 15,
    "engineering reference default": 15,
    "manufacturer": 55,
    "manufacturer datasheet": 65,
    "peer reviewed": 80,
    "nasa": 90,
    "nasa reference": 90,
}

MATERIAL_ALIASES = {
    "grcop42": "GRCop-42",
    "gr cop 42": "GRCop-42",
    "nasa grcop-42": "GRCop-42",

    "grcop84": "GRCop-84",
    "gr cop 84": "GRCop-84",
    "nasa grcop-84": "GRCop-84",

    "narloyz": "NARloy-Z",
    "narloy z": "NARloy-Z",

    "glidcop": "GlidCop AL-15",
    "glidcop al15": "GlidCop AL-15",

    "in718": "Inconel 718",
    "inconel718": "Inconel 718",

    "in625": "Inconel 625",
    "inconel625": "Inconel 625",

    "haynes230": "Haynes 230",
    "h230": "Haynes 230",

    "hastelloyx": "Hastelloy X",
    "hastelloy x": "Hastelloy X",

    "304ss": "304 Stainless Steel",
    "316ss": "316 Stainless Steel",
    "321ss": "321 Stainless Steel",
    "17-4ph": "17-4PH Stainless Steel",
}

MATERIAL_DATABASE = {
    # -----------------------------------------------------
    # Copper and copper rocket chamber liner alloys
    # -----------------------------------------------------
    "NARloy-Z": {
        "family": "Copper rocket liner alloy",
        "density": 8910.0,
        "yield_strength": 170e6,
        "ultimate_tensile_strength": 320e6,
        "thermal_conductivity": 296.0,
        "specific_heat": 385.0,
        "melting_point": 1356.0,
        "max_recommended_wall_temperature": 800.0,
        "thermal_expansion": 17.0e-6,
        "elastic_modulus": 117e9,
        "poisson_ratio": 0.34,
        "source_quality": "NASA reference / approximate room-temperature default",
        "notes": "Traditional copper-silver-zirconium rocket combustion chamber liner alloy."
    },

    "GRCop-84": {
        "family": "NASA copper-chromium-niobium liner alloy",
        "density": 8850.0,
        "yield_strength": 240e6,
        "ultimate_tensile_strength": 420e6,
        "thermal_conductivity": 280.0,
        "specific_heat": 385.0,
        "melting_point": 1356.0,
        "max_recommended_wall_temperature": 900.0,
        "thermal_expansion": 16.8e-6,
        "elastic_modulus": 120e9,
        "poisson_ratio": 0.34,
        "source_quality": "NASA reference / approximate room-temperature default",
        "notes": "High-strength copper alloy developed for reusable rocket chamber liners."
    },

    "GRCop-42": {
        "family": "NASA copper-chromium-niobium liner alloy",
        "density": 8890.0,
        "yield_strength": 230e6,
        "ultimate_tensile_strength": 400e6,
        "thermal_conductivity": 344.0,
        "specific_heat": 385.0,
        "melting_point": 1356.0,
        "max_recommended_wall_temperature": 900.0,
        "thermal_expansion": 17.0e-6,
        "elastic_modulus": 120e9,
        "poisson_ratio": 0.34,
        "source_quality": "NASA reference / approximate room-temperature default",
        "notes": "Higher-conductivity GRCop variant with slightly reduced strength compared with GRCop-84."
    },

    "GlidCop AL-15": {
        "family": "Oxide-dispersion-strengthened copper",
        "density": 8900.0,
        "yield_strength": 280e6,
        "ultimate_tensile_strength": 360e6,
        "thermal_conductivity": 365.0,
        "specific_heat": 385.0,
        "melting_point": 1356.0,
        "max_recommended_wall_temperature": 850.0,
        "thermal_expansion": 16.6e-6,
        "elastic_modulus": 128e9,
        "poisson_ratio": 0.34,
        "source_quality": "Manufacturer datasheet / approximate default",
        "notes": "Very high thermal conductivity with good elevated-temperature strength."
    },

    "CuCrZr": {
        "family": "Copper chromium zirconium alloy",
        "density": 8900.0,
        "yield_strength": 300e6,
        "ultimate_tensile_strength": 430e6,
        "thermal_conductivity": 320.0,
        "specific_heat": 385.0,
        "melting_point": 1356.0,
        "max_recommended_wall_temperature": 750.0,
        "thermal_expansion": 17.0e-6,
        "elastic_modulus": 120e9,
        "poisson_ratio": 0.34,
        "source_quality": "Engineering reference default",
        "notes": "High-conductivity copper alloy, but heat treatment condition matters strongly."
    },

    "OFHC Copper": {
        "family": "High-purity copper",
        "density": 8960.0,
        "yield_strength": 70e6,
        "ultimate_tensile_strength": 220e6,
        "thermal_conductivity": 390.0,
        "specific_heat": 385.0,
        "melting_point": 1356.0,
        "max_recommended_wall_temperature": 600.0,
        "thermal_expansion": 16.5e-6,
        "elastic_modulus": 117e9,
        "poisson_ratio": 0.34,
        "source_quality": "Engineering reference default",
        "notes": "Excellent conductivity but weak compared with strengthened chamber liner alloys."
    },

    # -----------------------------------------------------
    # Nickel superalloys / jackets
    # -----------------------------------------------------
    "Inconel 718": {
        "family": "Nickel superalloy",
        "density": 8190.0,
        "yield_strength": 1030e6,
        "ultimate_tensile_strength": 1240e6,
        "thermal_conductivity": 11.4,
        "specific_heat": 435.0,
        "melting_point": 1609.0,
        "max_recommended_wall_temperature": 980.0,
        "thermal_expansion": 13.0e-6,
        "elastic_modulus": 200e9,
        "poisson_ratio": 0.29,
        "source_quality": "Engineering reference default",
        "notes": "Strong jacket/shell alloy but poor thermal conductor."
    },

    "Inconel 625": {
        "family": "Nickel superalloy",
        "density": 8440.0,
        "yield_strength": 460e6,
        "ultimate_tensile_strength": 930e6,
        "thermal_conductivity": 9.8,
        "specific_heat": 410.0,
        "melting_point": 1623.0,
        "max_recommended_wall_temperature": 980.0,
        "thermal_expansion": 12.8e-6,
        "elastic_modulus": 207e9,
        "poisson_ratio": 0.30,
        "source_quality": "Engineering reference default",
        "notes": "Corrosion-resistant nickel alloy; useful for jackets and manifolds."
    },

    "Haynes 230": {
        "family": "Nickel superalloy",
        "density": 8970.0,
        "yield_strength": 360e6,
        "ultimate_tensile_strength": 760e6,
        "thermal_conductivity": 8.9,
        "specific_heat": 397.0,
        "melting_point": 1588.0,
        "max_recommended_wall_temperature": 1200.0,
        "thermal_expansion": 13.0e-6,
        "elastic_modulus": 211e9,
        "poisson_ratio": 0.31,
        "source_quality": "Engineering reference default",
        "notes": "Good high-temperature oxidation resistance."
    },

    "Hastelloy X": {
        "family": "Nickel superalloy",
        "density": 8220.0,
        "yield_strength": 360e6,
        "ultimate_tensile_strength": 760e6,
        "thermal_conductivity": 9.1,
        "specific_heat": 486.0,
        "melting_point": 1573.0,
        "max_recommended_wall_temperature": 1170.0,
        "thermal_expansion": 13.3e-6,
        "elastic_modulus": 205e9,
        "poisson_ratio": 0.30,
        "source_quality": "Engineering reference default",
        "notes": "High-temperature nickel alloy often used in hot structures."
    },

    # -----------------------------------------------------
    # Stainless steels
    # -----------------------------------------------------
    "304 Stainless Steel": {
        "family": "Austenitic stainless steel",
        "density": 8000.0,
        "yield_strength": 215e6,
        "ultimate_tensile_strength": 505e6,
        "thermal_conductivity": 16.2,
        "specific_heat": 500.0,
        "melting_point": 1670.0,
        "max_recommended_wall_temperature": 870.0,
        "thermal_expansion": 17.3e-6,
        "elastic_modulus": 193e9,
        "poisson_ratio": 0.29,
        "source_quality": "Engineering reference default",
        "notes": "General stainless option; poor conductivity for chamber liners."
    },

    "316 Stainless Steel": {
        "family": "Austenitic stainless steel",
        "density": 8000.0,
        "yield_strength": 290e6,
        "ultimate_tensile_strength": 580e6,
        "thermal_conductivity": 16.3,
        "specific_heat": 500.0,
        "melting_point": 1670.0,
        "max_recommended_wall_temperature": 870.0,
        "thermal_expansion": 16.0e-6,
        "elastic_modulus": 193e9,
        "poisson_ratio": 0.30,
        "source_quality": "Engineering reference default",
        "notes": "Better corrosion resistance than 304."
    },

    "321 Stainless Steel": {
        "family": "Austenitic stainless steel",
        "density": 8000.0,
        "yield_strength": 240e6,
        "ultimate_tensile_strength": 620e6,
        "thermal_conductivity": 16.1,
        "specific_heat": 500.0,
        "melting_point": 1670.0,
        "max_recommended_wall_temperature": 900.0,
        "thermal_expansion": 16.6e-6,
        "elastic_modulus": 193e9,
        "poisson_ratio": 0.30,
        "source_quality": "Engineering reference default",
        "notes": "Titanium-stabilised stainless steel."
    },

    "17-4PH Stainless Steel": {
        "family": "Precipitation-hardened stainless steel",
        "density": 7800.0,
        "yield_strength": 1000e6,
        "ultimate_tensile_strength": 1100e6,
        "thermal_conductivity": 18.0,
        "specific_heat": 460.0,
        "melting_point": 1670.0,
        "max_recommended_wall_temperature": 620.0,
        "thermal_expansion": 10.8e-6,
        "elastic_modulus": 200e9,
        "poisson_ratio": 0.27,
        "source_quality": "Engineering reference default",
        "notes": "High strength, but not ideal for very hot chamber liner surfaces."
    },
}

COATING_MATERIAL_DATABASE = [
    {
        "name": "YSZ Thermal Barrier Coating",
        "family": "Ceramic thermal barrier coating",
        "thermal_conductivity": 2.0,
        "max_surface_temperature": 1473.0,
        "max_practical_thickness": 0.0005,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Yttria-stabilized zirconia thermal barrier coating; replace/confirm values with final cited source.",
        "coating_role": "thermal_barrier",
        "density": 5600.0,
        "elastic_modulus": 2.0e11,
        "poisson_ratio": 0.25,
        "thermal_expansion_coefficient": 10.0e-6,
        "allowable_coating_stress": 1.0e8,
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "mechanical_data_available": False,
        "failure_data_available": False,
    },
    {
        "name": "Alumina Ceramic Coating",
        "family": "Ceramic coating",
        "thermal_conductivity": 6.0,
        "max_surface_temperature": 1700.0,
        "max_practical_thickness": 0.0003,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Alumina ceramic coating; replace/confirm values with final cited source.",
        "coating_role": "thermal_barrier",
        "density": 3950.0,
        "elastic_modulus": 3.0e11,
        "poisson_ratio": 0.22,
        "thermal_expansion_coefficient": 8.0e-6,
        "allowable_coating_stress": 1.0e8,
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "mechanical_data_available": False,
        "failure_data_available": False,
    },
    {
        "name": "Hafnia Thermal Barrier Coating",
        "family": "High-temperature ceramic coating",
        "thermal_conductivity": 1.5,
        "max_surface_temperature": 2000.0,
        "max_practical_thickness": 0.0005,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Hafnia-based high-temperature ceramic coating; replace/confirm values with final cited source.",
        "coating_role": "thermal_barrier",
        "density": 9680.0,
        "elastic_modulus": 2.0e11,
        "poisson_ratio": 0.25,
        "thermal_expansion_coefficient": 6.0e-6,
        "allowable_coating_stress": 1.0e8,
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "mechanical_data_available": False,
        "failure_data_available": False,
    },
    {
        "name": "Rhenium Refractory Liner",
        "family": "Refractory metal liner",
        "thermal_conductivity": 48.0,
        "max_surface_temperature": 2200.0,
        "max_practical_thickness": 0.001,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Refractory liner candidate; high density and fabrication difficulty must be penalised later.",
        "coating_role": "refractory_liner",
        "density": 21020.0,
        "elastic_modulus": 4.6e11,
        "poisson_ratio": 0.30,
        "thermal_expansion_coefficient": 6.2e-6,
        "allowable_coating_stress": 2.0e8,
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "mechanical_data_available": False,
        "failure_data_available": False,
    },
]

BOND_COAT_DATABASE = [
    {
        "name": "NiCoCrAlY Bond Coat",
        "family": "MCrAlY bond coat",
        "max_stress_reduction_fraction": 0.30,
        "max_practical_thickness": 0.00015,
        "density": 7600.0,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Common thermal-barrier bond coat candidate; replace with sourced temperature-dependent data.",
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "stress_relief_data_available": False,
        "adhesion_data_available": False,
        "fatigue_data_available": False,
    },
    {
        "name": "Pt-Aluminide Bond Coat",
        "family": "Diffusion aluminide bond coat",
        "max_stress_reduction_fraction": 0.22,
        "max_practical_thickness": 0.00008,
        "density": 8200.0,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Oxidation-resistant bond coat candidate; replace with sourced temperature-dependent data.",
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "stress_relief_data_available": False,
        "adhesion_data_available": False,
        "fatigue_data_available": False,
    },
    {
        "name": "Compliant Metallic Interlayer",
        "family": "Compliant stress-relief layer",
        "max_stress_reduction_fraction": 0.38,
        "max_practical_thickness": 0.0002,
        "density": 8000.0,
        "source_quality": "engineering_reference_placeholder",
        "notes": "Generic compliant interlayer candidate; replace with real material and sourced data.",
        "data_source_type": "placeholder",
        "citation": None,
        "temperature_dependent_data_available": False,
        "stress_relief_data_available": False,
        "adhesion_data_available": False,
        "fatigue_data_available": False,
    },
]

def normalise_source_text(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def source_quality_score(source_quality=None, data_source_type=None):
    source_quality_text = normalise_source_text(source_quality)
    source_type_text = normalise_source_text(data_source_type)

    combined = f"{source_quality_text} {source_type_text}".strip()

    if not combined:
        return 0

    best_score = 0

    for key, score in SOURCE_QUALITY_RANKS.items():
        if key in combined:
            best_score = max(best_score, score)

    if "placeholder" in combined:
        best_score = min(best_score, 5)

    return best_score


def has_valid_citation(data):
    if not isinstance(data, dict):
        return False

    citation = data.get("citation")
    doi = data.get("doi")
    url = data.get("url")
    source_title = data.get("source_title")

    return any(value not in (None, "") for value in (citation, doi, url, source_title))


def has_temperature_table(data):
    if not isinstance(data, dict):
        return False

    table_keys = [
        "temperature_table",
        "property_table",
        "temperature_dependent_properties",
        "temperature_dependent_table",
    ]

    for key in table_keys:
        table = data.get(key)

        if isinstance(table, list) and len(table) >= 2:
            return True

        if isinstance(table, dict) and len(table) >= 2:
            return True

    return bool(data.get("temperature_dependent_data_available"))


def classify_source_validation_mode(data):
    if not isinstance(data, dict):
        return {
            "mode": PLACEHOLDER_MODE,
            "score": 0,
            "has_citation": False,
            "has_temperature_table": False,
            "is_placeholder": True,
            "recommendation": "No material/coating data dictionary was provided.",
        }

    source_quality = data.get("source_quality")
    data_source_type = data.get("data_source_type")

    score = source_quality_score(source_quality, data_source_type)
    citation_ok = has_valid_citation(data)
    temperature_ok = has_temperature_table(data)

    source_text = normalise_source_text(source_quality)
    type_text = normalise_source_text(data_source_type)

    placeholder = (
        "placeholder" in source_text
        or "placeholder" in type_text
        or score <= 5
    )

    mechanical_keys = [
        "yield_strength",
        "ultimate_tensile_strength",
        "elastic_modulus",
        "poisson_ratio",
        "thermal_expansion",
        "thermal_expansion_coefficient",
        "allowable_coating_stress",
    ]

    mechanical_count = len([
        key for key in mechanical_keys
        if data.get(key) not in (None, "")
    ])

    if citation_ok:
        score += 20

    if temperature_ok:
        score += 25

    if mechanical_count >= 3:
        score += 20
    elif mechanical_count >= 1:
        score += 10

    score = min(100, score)

    if placeholder:
        mode = PLACEHOLDER_MODE
        recommendation = "Placeholder data detected. This item cannot generate engineering PASS."
    elif score >= 85 and citation_ok and temperature_ok:
        mode = SOURCED_VALIDATION_MODE
        recommendation = "Sourced data appears sufficient for validation review."
    elif score >= 45 and citation_ok:
        mode = PARTIAL_SOURCE_MODE
        recommendation = "Partial sourced data exists, but temperature/mechanical evidence is incomplete."
    else:
        mode = INSUFFICIENT_SOURCE_MODE
        recommendation = "Source evidence is insufficient. Add citation, temperature tables, and mechanical properties."

    return {
        "mode": mode,
        "score": score,
        "has_citation": citation_ok,
        "has_temperature_table": temperature_ok,
        "is_placeholder": placeholder,
        "mechanical_property_count": mechanical_count,
        "recommendation": recommendation,
    }

def interpolate_temperature_property(data, property_name, temperature_k):
    """
    Linear interpolation helper for future sourced property tables.

    Expected supported table forms:

    1. Dict:
        {
            "temperature_dependent_properties": {
                300: {"thermal_conductivity": 340},
                600: {"thermal_conductivity": 300}
            }
        }

    2. List:
        {
            "temperature_table": [
                {"temperature": 300, "thermal_conductivity": 340},
                {"temperature": 600, "thermal_conductivity": 300}
            ]
        }

    Falls back to the constant property if no usable table exists.
    """

    if not isinstance(data, dict):
        return None

    try:
        temperature_k = float(temperature_k)
    except Exception:
        return data.get(property_name)

    table = (
        data.get("temperature_dependent_properties")
        or data.get("temperature_table")
        or data.get("property_table")
        or data.get("temperature_dependent_table")
    )

    points = []

    if isinstance(table, dict):
        for temp, values in table.items():
            try:
                temp = float(temp)
            except Exception:
                continue

            if isinstance(values, dict):
                value = values.get(property_name)
            else:
                value = None

            if value is not None:
                try:
                    points.append((temp, float(value)))
                except Exception:
                    pass

    elif isinstance(table, list):
        for row in table:
            if not isinstance(row, dict):
                continue

            temp = row.get("temperature") or row.get("temperature_k")
            value = row.get(property_name)

            try:
                points.append((float(temp), float(value)))
            except Exception:
                continue

    if not points:
        return data.get(property_name)

    points.sort(key=lambda item: item[0])

    if temperature_k <= points[0][0]:
        return points[0][1]

    if temperature_k >= points[-1][0]:
        return points[-1][1]

    for index in range(len(points) - 1):
        t0, v0 = points[index]
        t1, v1 = points[index + 1]

        if t0 <= temperature_k <= t1:
            fraction = (temperature_k - t0) / (t1 - t0)
            return v0 + fraction * (v1 - v0)

    return data.get(property_name)

def get_material_names():
    return list(MATERIAL_DATABASE.keys())

def get_coating_material_names():
    return [
        coating.get("name")
        for coating in COATING_MATERIAL_DATABASE
        if coating.get("name")
    ]


def get_bond_coat_names():
    return [
        bond.get("name")
        for bond in BOND_COAT_DATABASE
        if bond.get("name")
    ]


def get_coating_database_summary():
    return {
        "coating_candidate_count": len(COATING_MATERIAL_DATABASE),
        "bond_coat_candidate_count": len(BOND_COAT_DATABASE),
        "coating_placeholder_count": len([
            c for c in COATING_MATERIAL_DATABASE
            if classify_source_validation_mode(c).get("mode") == PLACEHOLDER_MODE
        ]),
        "bond_coat_placeholder_count": len([
            b for b in BOND_COAT_DATABASE
            if classify_source_validation_mode(b).get("mode") == PLACEHOLDER_MODE
        ]),
    }

def get_material(material_name):
    if material_name not in MATERIAL_DATABASE:
        return None

    return MATERIAL_DATABASE[material_name].copy()


def get_material_property(material_name, property_name):
    material = get_material(material_name)

    if material is None:
        return None

    return material.get(property_name)


def get_material_summary_text(material_name):
    material = get_material(material_name)

    if material is None:
        return "No material selected."

    return (
        f"Material: {material_name}\n"
        f"Family: {material.get('family', 'Unknown')}\n\n"
        f"Density: {material.get('density')} kg/m³\n"
        f"Yield Strength: {material.get('yield_strength')} Pa\n"
        f"Ultimate Tensile Strength: {material.get('ultimate_tensile_strength')} Pa\n"
        f"Thermal Conductivity: {material.get('thermal_conductivity')} W/(m·K)\n"
        f"Specific Heat: {material.get('specific_heat')} J/(kg·K)\n"
        f"Melting Point: {material.get('melting_point')} K\n"
        f"Max Recommended Wall Temperature: {material.get('max_recommended_wall_temperature')} K\n"
        f"Thermal Expansion: {material.get('thermal_expansion')} 1/K\n"
        f"Elastic Modulus: {material.get('elastic_modulus')} Pa\n"
        f"Poisson Ratio: {material.get('poisson_ratio')}\n\n"
        f"Source Quality: {material.get('source_quality')}\n"
        f"Notes: {material.get('notes')}"
    )

def normalise_material_name(material_name):
    if material_name is None:
        return None

    requested = str(material_name).strip()

    if requested in MATERIAL_DATABASE:
        return requested

    requested_key = requested.lower().replace("_", " ").replace("-", "").strip()

    if requested_key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[requested_key]

    for canonical_name in MATERIAL_DATABASE.keys():
        canonical_key = canonical_name.lower().replace("_", " ").replace("-", "").strip()
        if requested_key == canonical_key:
            return canonical_name

    return None


def get_material_properties(material_name, temperature_k=None):
    canonical_name = normalise_material_name(material_name)

    if canonical_name is None:
        return None

    material = MATERIAL_DATABASE[canonical_name].copy()
    material["name"] = canonical_name

    validation = classify_source_validation_mode(material)

    material["source_validation_mode"] = validation["mode"]
    material["source_validation_score"] = validation["score"]
    material["source_has_citation"] = validation["has_citation"]
    material["source_has_temperature_table"] = validation["has_temperature_table"]
    material["source_is_placeholder"] = validation["is_placeholder"]
    material["source_validation_recommendation"] = validation["recommendation"]

    if temperature_k is not None:
        for property_name in (
            "thermal_conductivity",
            "yield_strength",
            "elastic_modulus",
            "poisson_ratio",
            "thermal_expansion",
            "specific_heat",
        ):
            interpolated = interpolate_temperature_property(
                material,
                property_name,
                temperature_k
            )

            if interpolated is not None:
                material[property_name] = interpolated

        material["property_temperature_k"] = temperature_k
        material["temperature_interpolation_used"] = material.get(
            "source_has_temperature_table",
            False
        )

    # Compatibility aliases for engine_solver.py
    material["max_wall_temperature"] = material.get("max_recommended_wall_temperature")
    material["thermal_conductivity_k"] = material.get("thermal_conductivity")

    return material

def get_coating_material_properties(name, temperature_k=None):
    for coating in COATING_MATERIAL_DATABASE:
        if str(coating.get("name", "")).strip().lower() == str(name).strip().lower():
            data = coating.copy()
            validation = classify_source_validation_mode(data)

            data["source_validation_mode"] = validation["mode"]
            data["source_validation_score"] = validation["score"]
            data["source_has_citation"] = validation["has_citation"]
            data["source_has_temperature_table"] = validation["has_temperature_table"]
            data["source_is_placeholder"] = validation["is_placeholder"]
            data["source_validation_recommendation"] = validation["recommendation"]

            if temperature_k is not None:
                for property_name in (
                    "thermal_conductivity",
                    "elastic_modulus",
                    "poisson_ratio",
                    "thermal_expansion_coefficient",
                    "allowable_coating_stress",
                ):
                    interpolated = interpolate_temperature_property(
                        data,
                        property_name,
                        temperature_k
                    )

                    if interpolated is not None:
                        data[property_name] = interpolated

                data["property_temperature_k"] = temperature_k

            return data

    return None


def get_bond_coat_properties(name, temperature_k=None):
    for bond in BOND_COAT_DATABASE:
        if str(bond.get("name", "")).strip().lower() == str(name).strip().lower():
            data = bond.copy()
            validation = classify_source_validation_mode(data)

            data["source_validation_mode"] = validation["mode"]
            data["source_validation_score"] = validation["score"]
            data["source_has_citation"] = validation["has_citation"]
            data["source_has_temperature_table"] = validation["has_temperature_table"]
            data["source_is_placeholder"] = validation["is_placeholder"]
            data["source_validation_recommendation"] = validation["recommendation"]

            if temperature_k is not None:
                for property_name in (
                    "max_stress_reduction_fraction",
                    "max_practical_thickness",
                    "density",
                ):
                    interpolated = interpolate_temperature_property(
                        data,
                        property_name,
                        temperature_k
                    )

                    if interpolated is not None:
                        data[property_name] = interpolated

                data["property_temperature_k"] = temperature_k

            return data

    return None