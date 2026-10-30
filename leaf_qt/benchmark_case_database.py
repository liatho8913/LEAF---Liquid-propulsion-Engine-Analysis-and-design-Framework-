BENCHMARK_CASES = {
    "RL10_CLASS": {
        "display_name": "RL10-class Hydrolox Upper-Stage Engine",
        "source_status": "PUBLIC_APPROXIMATE",
        "engine_family": "expander-cycle hydrolox",
        "notes": [
            "Public benchmark envelope only.",
            "Do not treat as exact internal engine design.",
        ],
        "targets": {
            "propellant_family": "LH2/LOX",
            "thrust_vacuum_range_n": (90000, 120000),
            "specific_impulse_vacuum_range_s": (440, 470),
            "chamber_pressure_range_pa": (2.0e6, 5.0e6),
            "expansion_ratio_range": (40, 300),
        },
    },

    "MERLIN_CLASS": {
        "display_name": "Merlin-class Kerolox Booster Engine",
        "source_status": "PUBLIC_APPROXIMATE",
        "engine_family": "gas-generator kerolox",
        "notes": [
            "Public benchmark envelope only.",
            "Useful for first-stage RP-1/LOX comparison.",
        ],
        "targets": {
            "propellant_family": "RP-1/LOX",
            "thrust_sea_level_range_n": (700000, 950000),
            "specific_impulse_sea_level_range_s": (275, 295),
            "specific_impulse_vacuum_range_s": (300, 330),
            "chamber_pressure_range_pa": (8.0e6, 12.0e6),
            "expansion_ratio_range": (10, 25),
        },
    },

    "RS25_CLASS": {
        "display_name": "RS-25-class Hydrolox Booster Engine",
        "source_status": "PUBLIC_APPROXIMATE",
        "engine_family": "staged-combustion hydrolox",
        "notes": [
            "Public benchmark envelope only.",
            "Complex reusable hydrolox booster-class comparison.",
        ],
        "targets": {
            "propellant_family": "LH2/LOX",
            "thrust_sea_level_range_n": (1500000, 2000000),
            "specific_impulse_sea_level_range_s": (350, 380),
            "specific_impulse_vacuum_range_s": (440, 465),
            "chamber_pressure_range_pa": (18.0e6, 23.0e6),
            "expansion_ratio_range": (60, 90),
        },
    },

    "RAPTOR_CLASS": {
        "display_name": "Raptor-class Methalox Booster Engine",
        "source_status": "PUBLIC_APPROXIMATE",
        "engine_family": "full-flow staged-combustion methalox",
        "notes": [
            "Public benchmark envelope only.",
            "Do not infer confidential internal geometry.",
        ],
        "targets": {
            "propellant_family": "CH4/LOX",
            "thrust_sea_level_range_n": (1800000, 2600000),
            "specific_impulse_sea_level_range_s": (320, 340),
            "specific_impulse_vacuum_range_s": (350, 380),
            "chamber_pressure_range_pa": (25.0e6, 35.0e6),
            "expansion_ratio_range": (20, 40),
        },
    },
}


def get_benchmark_case(case_key):
    return BENCHMARK_CASES.get(str(case_key or "").upper())


def get_benchmark_case_keys():
    return list(BENCHMARK_CASES.keys())


def get_benchmark_case_names():
    return {
        key: case["display_name"]
        for key, case in BENCHMARK_CASES.items()
    }