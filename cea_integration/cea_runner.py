import math
import re
import threading
from functools import lru_cache, wraps

from rocketcea.cea_obj import CEA_Obj, set_py_cea_line
import rocketcea.py_cea as py_cea
from rocketcea.blends import makeCardForNewTemperature

# ============================================================
# Shared RocketCEA / py_cea runtime serialization
# ============================================================

_CEA_RUNTIME_LOCK = threading.RLock()


def _with_cea_runtime_lock(func):
    """
    Serialize all canonical entries into RocketCEA's mutable
    FORTRAN/common-block backend and shared CEA input buffer.
    """

    @wraps(func)
    def _locked(*args, **kwargs):

        with _CEA_RUNTIME_LOCK:

            return func(
                *args,
                **kwargs
            )

    return _locked



# ============================================================
# Unit conversion helpers
# ============================================================

def _psia_from_pa(pressure_pa):
    return float(pressure_pa) * 0.0001450377377


def _deg_r_from_k(temp_k):
    return float(temp_k) * 9.0 / 5.0


def _k_from_deg_r(temp_r):
    if temp_r is None:
        return None
    return float(temp_r) * 5.0 / 9.0


def _btulbm_r_to_jkg_k(value):
    if value is None:
        return None
    return float(value) * 4186.8


def _lbm_cuft_to_kg_m3(value):
    if value is None:
        return None
    return float(value) * 16.01846337


def _ft_s_to_m_s(value):
    if value is None:
        return None
    return float(value) * 0.3048


def _cal_g_k_to_j_kg_k(value):
    if value is None:
        return None
    return float(value) * 4184.0


def _millipoise_to_pa_s(value):
    if value is None:
        return None
    return float(value) * 1.0e-4


def _mcal_cm_s_k_to_w_m_k(value):
    if value is None:
        return None
    return float(value) * 0.4184


def _safe_float(value):
    try:
        if value is None:
            return None
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    except Exception:
        return None


def _safe_call(func, *args, default=None, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception:
        return default


# ============================================================
# Propellant naming / alias layer
# ============================================================

def _clean_name(name):
    return str(name).strip()


def _rocketcea_fuel_name(name):
    name = _clean_name(name).upper()

    aliases = {
        "CH4": "CH4",
        "METHANE": "CH4",
        "GCH4": "GCH4",
        "LCH4": "LCH4_NASA",
        "LIQUID METHANE": "LCH4_NASA",

        "H2": "H2",
        "GH2": "GH2",
        "HYDROGEN": "H2",
        "LH2": "LH2_NASA",
        "LIQUID HYDROGEN": "LH2_NASA",

        "RP-1": "RP1",
        "RP1": "RP1",
        "RP-1 / KEROSENE": "RP1",
        "KEROSENE": "RP1",
        "JET-A": "JetA",
        "JETA": "JetA",
        "JET A": "JetA",

        "ETHANOL": "Ethanol",
        "METHANOL": "Methanol",
        "MMH": "MMH",
        "UDMH": "UDMH",
        "N2H4": "N2H4",
        "HYDRAZINE": "N2H4",
    }

    return aliases.get(name, _clean_name(name))


def _rocketcea_oxidizer_name(name):
    name = _clean_name(name).upper()

    aliases = {
        "O2": "GOX",
        "GOX": "GOX",
        "GASEOUS O2": "GOX",
        "GASEOUS OXYGEN": "GOX",

        "LOX": "LOX",
        "LO2": "LOX",
        "O2(L)": "LOX",
        "LIQUID OXYGEN": "LOX",

        "N2O": "N2O",
        "NITROUS OXIDE": "N2O",

        "N2O4": "N2O4",
        "NTO": "N2O4",
        "MON3": "MON3",
        "MON15": "MON15",
        "MON25": "MON25",

        "H2O2": "H2O2",
        "90_H2O2": "90_H2O2",
        "98_H2O2": "98_H2O2",
        "PEROXIDE90": "Peroxide90",
        "PEROXIDE98": "Peroxide98",
    }

    return aliases.get(name, _clean_name(name))


# ============================================================
# Temperature adjustment
# ============================================================

_CP_AVG_BTULBM_R = {
    "CH4": 0.80,
    "GCH4": 0.80,
    "LCH4_NASA": 0.80,

    "H2": 3.40,
    "GH2": 3.40,
    "LH2_NASA": 3.40,

    "RP1": 0.50,
    "Kerosene": 0.50,
    "JetA": 0.50,

    "LOX": 0.40,
    "GOX": 0.22,

    "N2O": 0.21,
    "N2O4": 0.20,
    "MMH": 0.70,
    "UDMH": 0.70,
    "N2H4": 0.72,
    "Ethanol": 0.58,
    "Methanol": 0.60,
}


_MOL_WT = {
    "CH4": 16.043,
    "GCH4": 16.043,
    "LCH4_NASA": 16.043,

    "H2": 2.016,
    "GH2": 2.016,
    "LH2_NASA": 2.016,

    "RP1": 170.0,
    "Kerosene": 170.0,
    "JetA": 170.0,

    "LOX": 31.999,
    "GOX": 31.999,

    "N2O": 44.013,
    "N2O4": 92.011,
    "MMH": 46.07,
    "UDMH": 60.10,
    "N2H4": 32.045,
    "Ethanol": 46.069,
    "Methanol": 32.042,
}


def _should_temperature_adjust(temp_k):
    if temp_k is None:
        return False

    temp_k = _safe_float(temp_k)

    if temp_k is None:
        return False

    return temp_k > 1.0


@lru_cache(maxsize=256)
def _make_temperature_adjusted_card(base_name, temp_k):
    """
    Creates a RocketCEA temporary propellant card at the requested inlet temperature.

    RocketCEA's makeCardForNewTemperature expects:
        - newTdegR in Rankine
        - CpAve in BTU/lbm-R
        - molecular weight in lbm/lbmol
    """

    base_name = _clean_name(base_name)
    temp_k = float(temp_k)

    cp_ave = _CP_AVG_BTULBM_R.get(base_name, 0.50)
    mol_wt = _MOL_WT.get(base_name, 30.0)

    try:
        return makeCardForNewTemperature(
            ceaName=base_name,
            newTdegR=_deg_r_from_k(temp_k),
            CpAve=cp_ave,
            MolWt=mol_wt
        )
    except Exception:
        return base_name


def _prepare_propellant_names(fuel_name, fuel_temp_k, oxidizer_name, oxidizer_temp_k):
    fuel = _rocketcea_fuel_name(fuel_name)
    oxidizer = _rocketcea_oxidizer_name(oxidizer_name)

    fuel_used = fuel
    oxidizer_used = oxidizer

    if _should_temperature_adjust(fuel_temp_k):
        fuel_used = _make_temperature_adjusted_card(fuel, float(fuel_temp_k))

    if _should_temperature_adjust(oxidizer_temp_k):
        oxidizer_used = _make_temperature_adjusted_card(oxidizer, float(oxidizer_temp_k))

    return fuel, oxidizer, fuel_used, oxidizer_used


# ============================================================
# RocketCEA parsing helpers
# ============================================================

def _transport_to_si(transport_values):
    """
    RocketCEA transport tuple:
        Cp           approx cal/(g*K)
        viscosity    millipoise
        conductivity millical/(cm*K*s)
        Prandtl      dimensionless
    """

    if not transport_values:
        return None, None, None, None

    try:
        cp = _cal_g_k_to_j_kg_k(transport_values[0])
        viscosity = _millipoise_to_pa_s(transport_values[1])
        conductivity = _mcal_cm_s_k_to_w_m_k(transport_values[2])
        prandtl = _safe_float(transport_values[3])
        return cp, viscosity, conductivity, prandtl
    except Exception:
        return None, None, None, None


def _normalise_species_result(result):
    """
    RocketCEA species calls can return dictionaries/tuples depending on version.
    This normalises the result into JSON-friendly data.
    """

    if result is None:
        return {}

    if isinstance(result, dict):
        output = {}
        for key, value in result.items():
            if isinstance(value, (list, tuple)):
                output[str(key)] = [_safe_float(v) for v in value]
            else:
                output[str(key)] = _safe_float(value)
        return output

    if isinstance(result, tuple) and len(result) == 2:
        species, values = result
        output = {}

        try:
            for name, value in zip(species, values):
                output[str(name)] = _safe_float(value)
            return output
        except Exception:
            return {
                "raw_species_result": str(result)
            }

    return {
        "raw_species_result": str(result)
    }


def _estimate_cv_from_cp_gamma(cp, gamma):
    cp = _safe_float(cp)
    gamma = _safe_float(gamma)

    if cp is None or gamma is None or gamma == 0:
        return None

    return cp / gamma


def _extract_mw_gamma(pair):
    if pair is None:
        return None, None

    try:
        return _safe_float(pair[0]), _safe_float(pair[1])
    except Exception:
        return None, None



# ============================================================
# General equilibrium assigned-state thermochemistry
# ============================================================

_CEA_HSUM_TO_J_PER_KG = 8314.51
_CEA_INPUT_LINE_LIMIT = 140


def _evaluate_equilibrium_assigned_state(
        problem_type,
        fuel_name,
        fuel_temp_k,
        oxidizer_name,
        oxidizer_temp_k,
        mixture_ratio,
        pressure_pa,
        temperature_k=None,
        specific_enthalpy_j_per_kg=None
):
    """
    Evaluate one non-rocket equilibrium CEA state using the same
    canonical RocketCEA propellant context as run_cea_rocket_case.

    Supported problem types:
        TP — assigned temperature and pressure.
        HP — assigned specific enthalpy and pressure.

    NASA/source-specific reference-state equations do not belong here.
    """

    mode = str(
        problem_type
    ).strip().upper()


    if mode not in {
        "TP",
        "HP",
    }:

        raise ValueError(
            "problem_type must be 'TP' or 'HP'"
        )


    try:

        mixture_ratio = float(
            mixture_ratio
        )

        pressure_pa = float(
            pressure_pa
        )

    except Exception as exc:

        raise ValueError(
            "mixture_ratio and pressure_pa must be numeric"
        ) from exc


    if (
        not math.isfinite(
            mixture_ratio
        )
        or
        mixture_ratio
        <=
        0.0
    ):

        raise ValueError(
            "mixture_ratio must be finite and positive"
        )


    if (
        not math.isfinite(
            pressure_pa
        )
        or
        pressure_pa
        <=
        0.0
    ):

        raise ValueError(
            "pressure_pa must be finite and positive"
        )


    if mode == "TP":

        try:

            temperature_k = float(
                temperature_k
            )

        except Exception as exc:

            raise ValueError(
                "temperature_k must be numeric for TP"
            ) from exc


        if (
            not math.isfinite(
                temperature_k
            )
            or
            temperature_k
            <=
            0.0
        ):

            raise ValueError(
                "temperature_k must be finite and positive"
            )


    else:

        try:

            specific_enthalpy_j_per_kg = float(
                specific_enthalpy_j_per_kg
            )

        except Exception as exc:

            raise ValueError(
                "specific_enthalpy_j_per_kg must be numeric for HP"
            ) from exc


        if not math.isfinite(
            specific_enthalpy_j_per_kg
        ):

            raise ValueError(
                "specific_enthalpy_j_per_kg must be finite"
            )


    with _CEA_RUNTIME_LOCK:

        (
            fuel_input,
            oxidizer_input,
            fuel_used,
            oxidizer_used,
        ) = _prepare_propellant_names(
            fuel_name=fuel_name,
            fuel_temp_k=fuel_temp_k,
            oxidizer_name=oxidizer_name,
            oxidizer_temp_k=oxidizer_temp_k
        )


        cea_obj = CEA_Obj(
            oxName=oxidizer_used,
            fuelName=fuel_used,
            makeOutput=1
        )


        reactant_deck = []


        for entry in cea_obj.cea_deck:

            if isinstance(
                entry,
                str
            ):

                reactant_deck.append(
                    entry
                )

            else:

                reactant_deck.extend(
                    str(line)
                    for line in entry
                )


        for line_number in range(
            1,
            _CEA_INPUT_LINE_LIMIT + 1
        ):

            set_py_cea_line(
                line_number,
                "    "
            )


        common_arrays = (
            py_cea.prtout.ttt,
            py_cea.prtout.hsum,
            py_cea.trpts.cpeql,
            py_cea.trpts.vis,
            py_cea.trpts.coneql,
            py_cea.trpts.preql,
        )


        for array in common_arrays:

            for index in range(
                min(
                    len(array),
                    20
                )
            ):

                array[index] = 0.0


        pressure_bar = (
            pressure_pa
            /
            100000.0
        )


        if mode == "TP":

            problem_line = (
                "prob case=LEAF_ASSIGNED_TP "
                "tp "
                f"p,bar={pressure_bar:.15g} "
                f"t,k={temperature_k:.15g} "
                f"o/f={mixture_ratio:.15g}"
            )

            output_line = (
                "output siunits"
            )


        else:

            h_over_r = (
                specific_enthalpy_j_per_kg
                /
                _CEA_HSUM_TO_J_PER_KG
            )

            problem_line = (
                "prob case=LEAF_ASSIGNED_HP "
                "hp "
                f"p,bar={pressure_bar:.15g} "
                f"o/f={mixture_ratio:.15g} "
                f"h/r={h_over_r:.15g}"
            )

            output_line = (
                "output calories transport"
            )


        deck = [
            *reactant_deck,
            "   ",
            problem_line,
            output_line,
            "end",
        ]


        for line_number, line in enumerate(
            deck,
            start=1
        ):

            set_py_cea_line(
                line_number,
                line
            )


        py_cea.py_cea(
            cea_obj.pathPrefix,
            "f.inp ",
            1,
            1
        )


        scan_count = min(
            len(
                py_cea.prtout.ttt
            ),
            len(
                py_cea.prtout.hsum
            ),
            len(
                py_cea.trpts.cpeql
            ),
            len(
                py_cea.trpts.vis
            ),
            len(
                py_cea.trpts.coneql
            ),
            len(
                py_cea.trpts.preql
            ),
            20
        )


        candidates = []


        for index in range(
            scan_count
        ):

            state_temperature = float(
                py_cea.prtout.ttt[
                    index
                ]
            )

            raw_enthalpy = float(
                py_cea.prtout.hsum[
                    index
                ]
            )


            if not (
                math.isfinite(
                    state_temperature
                )
                and
                state_temperature
                >
                0.0
                and
                math.isfinite(
                    raw_enthalpy
                )
            ):

                continue


            candidate = {
                "index":
                    index,

                "temperature_k":
                    state_temperature,

                "raw_enthalpy_hsum":
                    raw_enthalpy,
            }


            if mode == "HP":

                cp_raw = float(
                    py_cea.trpts.cpeql[
                        index
                    ]
                )

                viscosity_raw = float(
                    py_cea.trpts.vis[
                        index
                    ]
                )

                conductivity_raw = float(
                    py_cea.trpts.coneql[
                        index
                    ]
                )

                prandtl = float(
                    py_cea.trpts.preql[
                        index
                    ]
                )


                if not all(
                    (
                        math.isfinite(
                            cp_raw
                        )
                        and
                        cp_raw
                        >
                        0.0,

                        math.isfinite(
                            viscosity_raw
                        )
                        and
                        viscosity_raw
                        >
                        0.0,

                        math.isfinite(
                            conductivity_raw
                        )
                        and
                        conductivity_raw
                        >
                        0.0,

                        math.isfinite(
                            prandtl
                        )
                        and
                        prandtl
                        >
                        0.0,
                    )
                ):

                    continue


                candidate[
                    "transport_raw"
                ] = (
                    cp_raw,
                    viscosity_raw,
                    conductivity_raw,
                    prandtl,
                )


            candidates.append(
                candidate
            )


        if len(
            candidates
        ) != 1:

            raise RuntimeError(
                "Assigned-state CEA evaluation must produce "
                "exactly one valid equilibrium state; "
                f"found {len(candidates)}"
            )


        candidate = candidates[
            0
        ]


        specific_enthalpy = (
            candidate[
                "raw_enthalpy_hsum"
            ]
            *
            _CEA_HSUM_TO_J_PER_KG
        )


        result = {
            "problem_type":
                mode,

            "temperature_k":
                candidate[
                    "temperature_k"
                ],

            "pressure_pa":
                pressure_pa,

            "specific_enthalpy_j_per_kg":
                specific_enthalpy,

            "fuel_input":
                fuel_input,

            "oxidizer_input":
                oxidizer_input,

            "fuel_used_by_rocketcea":
                fuel_used,

            "oxidizer_used_by_rocketcea":
                oxidizer_used,

            "backend_provenance": {
                "backend":
                    "rocketcea.py_cea",

                "chemistry":
                    "equilibrium",

                "rocket_mode":
                    False,

                "problem_type":
                    mode,

                "enthalpy_internal_unit":
                    "CEA_INTERNAL_HSUM_H_OVER_R",

                "enthalpy_to_j_per_kg_factor":
                    _CEA_HSUM_TO_J_PER_KG,
            },
        }


        if mode == "HP":

            (
                cp_si,
                viscosity_si,
                conductivity_si,
                prandtl_si,
            ) = _transport_to_si(
                candidate[
                    "transport_raw"
                ]
            )


            converted_values = (
                cp_si,
                viscosity_si,
                conductivity_si,
                prandtl_si,
            )


            if not all(
                (
                    value is not None
                    and
                    math.isfinite(
                        float(value)
                    )
                    and
                    float(value)
                    >
                    0.0
                )

                for value in converted_values
            ):

                raise RuntimeError(
                    "Assigned-state HP transport conversion "
                    "returned invalid values"
                )


            result.update(
                {
                    "specific_heat_cp_j_per_kg_k":
                        float(
                            cp_si
                        ),

                    "dynamic_viscosity_pa_s":
                        float(
                            viscosity_si
                        ),

                    "thermal_conductivity_w_per_m_k":
                        float(
                            conductivity_si
                        ),

                    "prandtl_number":
                        float(
                            prandtl_si
                        ),
                }
            )


        return result


def evaluate_equilibrium_tp_enthalpy(
        fuel_name,
        fuel_temp_k,
        oxidizer_name,
        oxidizer_temp_k,
        mixture_ratio,
        temperature_k,
        pressure_pa
):
    """
    Return equilibrium gas enthalpy at an assigned T,P state.

    This is a general CEA capability and contains no source-specific
    NASA D-2832 reference-state equation.
    """

    state = _evaluate_equilibrium_assigned_state(
        problem_type="TP",
        fuel_name=fuel_name,
        fuel_temp_k=fuel_temp_k,
        oxidizer_name=oxidizer_name,
        oxidizer_temp_k=oxidizer_temp_k,
        mixture_ratio=mixture_ratio,
        temperature_k=temperature_k,
        pressure_pa=pressure_pa
    )


    return {
        "temperature_k":
            state[
                "temperature_k"
            ],

        "pressure_pa":
            state[
                "pressure_pa"
            ],

        "specific_enthalpy_j_per_kg":
            state[
                "specific_enthalpy_j_per_kg"
            ],

        "backend_provenance":
            state[
                "backend_provenance"
            ],
    }


def evaluate_equilibrium_hp_transport(
        fuel_name,
        fuel_temp_k,
        oxidizer_name,
        oxidizer_temp_k,
        mixture_ratio,
        specific_enthalpy_j_per_kg,
        pressure_pa
):
    """
    Return equilibrium transport properties at an assigned H,P state.

    This is a general CEA capability and contains no source-specific
    NASA D-2832 reference-state equation.
    """

    state = _evaluate_equilibrium_assigned_state(
        problem_type="HP",
        fuel_name=fuel_name,
        fuel_temp_k=fuel_temp_k,
        oxidizer_name=oxidizer_name,
        oxidizer_temp_k=oxidizer_temp_k,
        mixture_ratio=mixture_ratio,
        specific_enthalpy_j_per_kg=
            specific_enthalpy_j_per_kg,
        pressure_pa=pressure_pa
    )


    return {
        "temperature_k":
            state[
                "temperature_k"
            ],

        "pressure_pa":
            state[
                "pressure_pa"
            ],

        "specific_enthalpy_j_per_kg":
            state[
                "specific_enthalpy_j_per_kg"
            ],

        "specific_heat_cp_j_per_kg_k":
            state[
                "specific_heat_cp_j_per_kg_k"
            ],

        "dynamic_viscosity_pa_s":
            state[
                "dynamic_viscosity_pa_s"
            ],

        "thermal_conductivity_w_per_m_k":
            state[
                "thermal_conductivity_w_per_m_k"
            ],

        "prandtl_number":
            state[
                "prandtl_number"
            ],

        "backend_provenance":
            state[
                "backend_provenance"
            ],
    }


# ============================================================
# Main public function used by the calculator
# ============================================================

@_with_cea_runtime_lock
def run_cea_rocket_case(
        fuel_name,
        fuel_temp_k,
        oxidizer_name,
        oxidizer_temp_k,
        chamber_pressure_pa,
        mixture_ratio,
        expansion_ratio
):
    fuel_base, oxidizer_base, fuel_used, oxidizer_used = _prepare_propellant_names(
        fuel_name=fuel_name,
        fuel_temp_k=fuel_temp_k,
        oxidizer_name=oxidizer_name,
        oxidizer_temp_k=oxidizer_temp_k
    )

    pc_psia = _psia_from_pa(chamber_pressure_pa)

    cea_obj = CEA_Obj(
        oxName=oxidizer_used,
        fuelName=fuel_used
    )

    chamber_mw_gamma = _safe_call(
        cea_obj.get_Chamber_MolWt_gamma,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    throat_mw_gamma = _safe_call(
        cea_obj.get_Throat_MolWt_gamma,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    exit_mw_gamma = _safe_call(
        cea_obj.get_exit_MolWt_gamma,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    chamber_mw, chamber_gamma = _extract_mw_gamma(chamber_mw_gamma)
    throat_mw, throat_gamma = _extract_mw_gamma(throat_mw_gamma)
    exit_mw, exit_gamma = _extract_mw_gamma(exit_mw_gamma)

    gas_constant = None
    if chamber_mw is not None and chamber_mw != 0:
        gas_constant = 8314.462618 / chamber_mw

    characteristic_velocity = _ft_s_to_m_s(
        _safe_call(
            cea_obj.get_Cstar,
            Pc=pc_psia,
            MR=mixture_ratio
        )
    )

    chamber_temp_r = _safe_call(
        cea_obj.get_Tcomb,
        Pc=pc_psia,
        MR=mixture_ratio
    )

    chamber_temperature_k = _k_from_deg_r(chamber_temp_r)

    temperatures = _safe_call(
        cea_obj.get_Temperatures,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    chamber_temp_k_2 = throat_temp_k = exit_temp_k = None

    if temperatures is not None:
        try:
            chamber_temp_k_2 = _k_from_deg_r(temperatures[0])
            throat_temp_k = _k_from_deg_r(temperatures[1])
            exit_temp_k = _k_from_deg_r(temperatures[2])
        except Exception:
            pass

    if chamber_temperature_k is None:
        chamber_temperature_k = chamber_temp_k_2

    chamber_cp_raw = _safe_call(
        cea_obj.get_Chamber_Cp,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    chamber_cp = _btulbm_r_to_jkg_k(chamber_cp_raw)

    densities = _safe_call(
        cea_obj.get_Densities,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    chamber_density = throat_density = exit_density = None

    if densities is not None:
        try:
            chamber_density = _lbm_cuft_to_kg_m3(densities[0])
            throat_density = _lbm_cuft_to_kg_m3(densities[1])
            exit_density = _lbm_cuft_to_kg_m3(densities[2])
        except Exception:
            pass

    if chamber_density is None:
        chamber_density_raw = _safe_call(
            cea_obj.get_Chamber_Density,
            Pc=pc_psia,
            MR=mixture_ratio,
            eps=expansion_ratio
        )
        chamber_density = _lbm_cuft_to_kg_m3(chamber_density_raw)

    heat_capacities = _safe_call(
        cea_obj.get_HeatCapacities,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    chamber_cp_eq = chamber_cp
    throat_cp = None
    exit_cp = None

    if heat_capacities is not None:
        try:
            chamber_cp_eq = _btulbm_r_to_jkg_k(heat_capacities[0])
            throat_cp = _btulbm_r_to_jkg_k(heat_capacities[1])
            exit_cp = _btulbm_r_to_jkg_k(heat_capacities[2])
        except Exception:
            pass

    sonic_velocities = _safe_call(
        cea_obj.get_SonicVelocities,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio
    )

    chamber_sonic_velocity = throat_sonic_velocity = exit_sonic_velocity = None

    if sonic_velocities is not None:
        try:
            chamber_sonic_velocity = _ft_s_to_m_s(sonic_velocities[0])
            throat_sonic_velocity = _ft_s_to_m_s(sonic_velocities[1])
            exit_sonic_velocity = _ft_s_to_m_s(sonic_velocities[2])
        except Exception:
            pass

    chamber_transport = _safe_call(
        cea_obj.get_Chamber_Transport,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio,
        frozen=0
    )

    throat_transport = _safe_call(
        cea_obj.get_Throat_Transport,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio,
        frozen=0
    )

    exit_transport = _safe_call(
        cea_obj.get_Exit_Transport,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio,
        frozen=0
    )

    chamber_cp_transport, chamber_mu, chamber_k, chamber_pr = _transport_to_si(chamber_transport)
    throat_cp_transport, throat_mu, throat_k, throat_pr = _transport_to_si(throat_transport)
    exit_cp_transport, exit_mu, exit_k, exit_pr = _transport_to_si(exit_transport)

    selected_cp = chamber_cp_transport if chamber_cp_transport is not None else chamber_cp_eq

    chamber_cv_eq = _estimate_cv_from_cp_gamma(chamber_cp_eq, chamber_gamma)
    throat_cv_eq = _estimate_cv_from_cp_gamma(throat_cp, throat_gamma)
    exit_cv_eq = _estimate_cv_from_cp_gamma(exit_cp, exit_gamma)

    species_mole_fractions = _normalise_species_result(
        _safe_call(
            cea_obj.get_SpeciesMoleFractions,
            Pc=pc_psia,
            MR=mixture_ratio,
            eps=expansion_ratio,
            frozen=0,
            min_fraction=1.0e-12
        )
    )

    species_mass_fractions = _normalise_species_result(
        _safe_call(
            cea_obj.get_SpeciesMassFractions,
            Pc=pc_psia,
            MR=mixture_ratio,
            eps=expansion_ratio,
            frozen=0,
            min_fraction=1.0e-12
        )
    )

    full_cea_output = _safe_call(
        cea_obj.get_full_cea_output,
        Pc=pc_psia,
        MR=mixture_ratio,
        eps=expansion_ratio,
        short_output=1,
        pc_units="psia",
        output="siunits"
    )

    cea_results = {
        "Gamma": _safe_float(chamber_gamma),
        "specific_heat_cp": _safe_float(selected_cp),
        "R": _safe_float(gas_constant),
        "cea_characteristic_velocity": _safe_float(characteristic_velocity),

        "chamber_temperature": _safe_float(chamber_temperature_k),

        "cea_density": _safe_float(chamber_density),
        "cea_molecular_weight": _safe_float(chamber_mw),

        "cea_cp_frozen": _safe_float(chamber_cp_transport),
        "cea_cv_equilibrium": _safe_float(chamber_cv_eq),
        "cea_cv_frozen": _safe_float(chamber_cv_eq),


        "cea_selected_cp": _safe_float(selected_cp),
        "cea_selected_viscosity": _safe_float(chamber_mu),
        "cea_selected_conductivity": _safe_float(chamber_k),
        "cea_selected_prandtl": _safe_float(chamber_pr),

        "cea_throat_cp": _safe_float(throat_cp_transport if throat_cp_transport is not None else throat_cp),
        "cea_throat_viscosity": _safe_float(throat_mu),
        "cea_throat_conductivity": _safe_float(throat_k),
        "cea_throat_prandtl": _safe_float(throat_pr),

        "cea_exit_cp": _safe_float(exit_cp_transport if exit_cp_transport is not None else exit_cp),
        "cea_exit_viscosity": _safe_float(exit_mu),
        "cea_exit_conductivity": _safe_float(exit_k),
        "cea_exit_prandtl": _safe_float(exit_pr),

        "cea_chamber_gamma": _safe_float(chamber_gamma),
        "cea_throat_gamma": _safe_float(throat_gamma),
        "cea_exit_gamma": _safe_float(exit_gamma),

        "cea_chamber_molecular_weight": _safe_float(chamber_mw),
        "cea_throat_molecular_weight": _safe_float(throat_mw),
        "cea_exit_molecular_weight": _safe_float(exit_mw),

        "cea_chamber_temperature": _safe_float(chamber_temperature_k),
        "cea_throat_temperature": _safe_float(throat_temp_k),
        "cea_exit_temperature": _safe_float(exit_temp_k),

        "cea_chamber_density": _safe_float(chamber_density),
        "cea_throat_density": _safe_float(throat_density),
        "cea_exit_density": _safe_float(exit_density),

        "cea_chamber_sonic_velocity": _safe_float(chamber_sonic_velocity),
        "cea_throat_sonic_velocity": _safe_float(throat_sonic_velocity),
        "cea_exit_sonic_velocity": _safe_float(exit_sonic_velocity),
    }

    raw_output = {
        "fuel_input": fuel_name,
        "oxidizer_input": oxidizer_name,

        "fuel_base": fuel_base,
        "oxidizer_base": oxidizer_base,

        "fuel_used_by_rocketcea": fuel_used,
        "oxidizer_used_by_rocketcea": oxidizer_used,

        "fuel_temperature_k": _safe_float(fuel_temp_k),
        "oxidizer_temperature_k": _safe_float(oxidizer_temp_k),

        "chamber_pressure_pa": _safe_float(chamber_pressure_pa),
        "chamber_pressure_psia": _safe_float(pc_psia),

        "mixture_ratio": _safe_float(mixture_ratio),
        "expansion_ratio": _safe_float(expansion_ratio),

        "mole_fractions": species_mole_fractions,
        "mass_fractions": species_mass_fractions,

        "full_cea_output": full_cea_output,

        "backend": "RocketCEA",
        "note": (
            "Legacy local 'cea' package removed. This file now uses RocketCEA only, "
            "including temperature-adjusted propellant cards where possible."
        )
    }

    return cea_results, raw_output