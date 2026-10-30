from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import hashlib
import math

import numpy as np
from scipy.optimize import brentq
import teqp


ETHANOL_FLD_SHA256 = (
    "15767630c6995519a8b7975cbb649be0"
    "dc9ea316a9c69f7d1440e90018e54c1e"
)

ETHANOL_MOLAR_MASS_KG_MOL = 0.0460684

ETHANOL_CERTIFIED_TEMPERATURE_MIN_K = 273.0
ETHANOL_CERTIFIED_TEMPERATURE_MAX_K = 333.0

ETHANOL_CERTIFIED_PRESSURE_PA = 101325.0

_DENSE_SCAN_MIN_MOL_M3 = 6000.0
_DENSE_SCAN_MAX_MOL_M3 = 30000.0
_DENSE_SCAN_POINTS = 8000


class SourceQualificationError(RuntimeError):
    pass


def _repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _ethanol_fld_path() -> Path:
    return (
        _repository_root()
        / "LEAF_Validation"
        / "preinjector_stage1_requalification"
        / (
            "MR6F_R2E_R6A_R2_R4_R1_STAGE1_"
            "ENG02_AUTHORITATIVE_PROPERTY_SOURCE_SELECTION_AND_MAPPING"
        )
        / "external_sources"
        / "ETHANOL.FLD"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _verified_ethanol_fld() -> Path:
    path = _ethanol_fld_path()

    if not path.is_file():
        raise SourceQualificationError(
            "ETHANOL_FLD_SOURCE_PACKAGE_MISSING"
        )

    if _sha256(path) != ETHANOL_FLD_SHA256:
        raise SourceQualificationError(
            "ETHANOL_FLD_SOURCE_PACKAGE_HASH_MISMATCH"
        )

    return path


@lru_cache(maxsize=1)
def _ethanol_model():
    fld = _verified_ethanol_fld()

    converted = teqp.convert_FLD(
        str(fld),
        name="ETHANOL",
    )

    model = teqp.make_model(
        {
            "kind": "multifluid",
            "model": {
                "components": [converted],
                "BIP": [],
                "departure": [],
            },
        }
    )

    z = np.array(
        [1.0],
        dtype=float,
    )

    return model, z


def _pressure_pa(
    model,
    z,
    temperature_k: float,
    rho_mol_m3: float,
) -> float:

    R = float(
        model.get_R(z)
    )

    Ar01 = float(
        model.get_Ar01(
            temperature_k,
            rho_mol_m3,
            z,
        )
    )

    return (
        rho_mol_m3
        *
        R
        *
        temperature_k
        *
        (
            1.0
            +
            Ar01
        )
    )


def _dpdrho(
    model,
    z,
    temperature_k: float,
    rho_mol_m3: float,
) -> float:

    R = float(
        model.get_R(z)
    )

    Ar01 = float(
        model.get_Ar01(
            temperature_k,
            rho_mol_m3,
            z,
        )
    )

    Ar02 = float(
        model.get_Ar02(
            temperature_k,
            rho_mol_m3,
            z,
        )
    )

    return (
        R
        *
        temperature_k
        *
        (
            1.0
            +
            2.0
            *
            Ar01
            +
            Ar02
        )
    )


def _ethanol_density_exact_tp(
    temperature_k: float,
    pressure_pa: float,
) -> float:

    model, z = _ethanol_model()

    def residual(
        rho_mol_m3: float,
    ) -> float:

        return (
            _pressure_pa(
                model,
                z,
                temperature_k,
                rho_mol_m3,
            )
            -
            pressure_pa
        )

    scan = np.linspace(
        _DENSE_SCAN_MIN_MOL_M3,
        _DENSE_SCAN_MAX_MOL_M3,
        _DENSE_SCAN_POINTS,
    )

    roots: list[float] = []

    prior_rho = float(
        scan[0]
    )

    prior_value = residual(
        prior_rho
    )

    for current in scan[1:]:

        current_rho = float(
            current
        )

        current_value = residual(
            current_rho
        )

        if (
            math.isfinite(
                prior_value
            )
            and
            math.isfinite(
                current_value
            )
            and
            prior_value
            *
            current_value
            <
            0.0
        ):

            root = brentq(
                residual,
                prior_rho,
                current_rho,
                xtol=1.0e-10,
                rtol=1.0e-12,
                maxiter=200,
            )

            if not any(
                abs(
                    root
                    -
                    existing
                )
                <
                1.0e-5
                for existing
                in roots
            ):
                roots.append(
                    root
                )

        prior_rho = current_rho
        prior_value = current_value

    stable_roots = [
        root
        for root
        in roots
        if _dpdrho(
            model,
            z,
            temperature_k,
            root,
        )
        >
        0.0
    ]

    if not stable_roots:
        raise SourceQualificationError(
            "ETHANOL_FEQ_NO_STABLE_LIQUID_ROOT"
        )

    liquid_root = max(
        stable_roots
    )

    return (
        liquid_root
        *
        ETHANOL_MOLAR_MASS_KG_MOL
    )


def get_source_qualified_density(
    fluid_name,
    temperature_k,
    pressure_pa,
):
    fluid = str(
        fluid_name
    ).strip().lower()

    if fluid != "ethanol":
        raise SourceQualificationError(
            "UNSUPPORTED_SOURCE_QUALIFIED_FLUID"
        )

    try:
        temperature_k = float(
            temperature_k
        )

        pressure_pa = float(
            pressure_pa
        )
    except (TypeError, ValueError) as exc:
        raise SourceQualificationError(
            "INVALID_THERMOPHYSICAL_STATE"
        ) from exc

    if not math.isfinite(
        temperature_k
    ):
        raise SourceQualificationError(
            "INVALID_TEMPERATURE"
        )

    if not math.isfinite(
        pressure_pa
    ):
        raise SourceQualificationError(
            "INVALID_PRESSURE"
        )

    if not (
        ETHANOL_CERTIFIED_TEMPERATURE_MIN_K
        <=
        temperature_k
        <=
        ETHANOL_CERTIFIED_TEMPERATURE_MAX_K
    ):
        raise SourceQualificationError(
            "ETHANOL_TEMPERATURE_OUTSIDE_CERTIFIED_DOMAIN"
        )

    if pressure_pa != ETHANOL_CERTIFIED_PRESSURE_PA:
        raise SourceQualificationError(
            "ETHANOL_PRESSURE_OUTSIDE_CERTIFIED_CONTRACT"
        )

    return _ethanol_density_exact_tp(
        temperature_k,
        pressure_pa,
    )
