from __future__ import annotations

import math
from typing import Any


OWNER_NAME = "LEAF_COST_INTELLIGENCE_OWNER"
CONTRACT_VERSION = "51D.1"

UNACCEPTABLE_SOURCE_QUALITIES = {
    "",
    "UNKNOWN",
    "PLACEHOLDER",
    "ASSUMED",
    "USER_ASSUMED",
    "UNSOURCED",
}

BASE_MATERIAL_MASS_KEYS = (
    "base_wall_mass",
    "chamber_wall_mass",
    "liner_mass",
    "regen_wall_mass",
)

BASE_MATERIAL_NAME_KEYS = (
    "selected_material",
    "material_name",
)

COATING_MATERIAL_NAME_KEYS = (
    "explicit_coating_material",
    "selected_coating_material",
    "coating_material",
    "coating_material_name",
)


def _num(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(number):
        return None

    return number


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    value = value.strip()

    return value or None


def _first_text(
    results: dict[str, Any],
    keys: tuple[str, ...],
) -> str | None:
    for key in keys:
        value = _text(
            results.get(key)
        )

        if value is not None:
            return value

    return None


def _first_quantity(
    results: dict[str, Any],
    keys: tuple[str, ...],
) -> tuple[str | None, float | None]:
    for key in keys:
        value = _num(
            results.get(key)
        )

        if value is None:
            continue

        if value < 0.0:
            continue

        return key, value

    return None, None


def _lookup_record(
    mapping: Any,
    identity: str | None,
) -> dict[str, Any] | None:
    if not isinstance(mapping, dict):
        return None

    if identity is None:
        return None

    direct = mapping.get(identity)

    if isinstance(direct, dict):
        return direct

    wanted = identity.casefold()

    for key, value in mapping.items():
        if (
            isinstance(key, str)
            and
            key.casefold() == wanted
            and
            isinstance(value, dict)
        ):
            return value

    return None


def _source_record(
    record: Any,
    value_key: str,
) -> dict[str, Any]:
    if not isinstance(record, dict):
        return {
            "valid": False,
            "value": None,
            "currency": None,
            "source": None,
            "timestamp": None,
            "source_quality": None,
        }

    value = _num(
        record.get(value_key)
    )

    currency = _text(
        record.get("currency")
    )

    source = _text(
        record.get("source")
    )

    timestamp = _text(
        record.get("timestamp")
    )

    source_quality = (
        _text(
            record.get("source_quality")
        )
        or
        "UNKNOWN"
    ).upper()

    valid = (
        value is not None
        and
        value >= 0.0
        and
        currency is not None
        and
        source is not None
        and
        timestamp is not None
        and
        source_quality
        not in
        UNACCEPTABLE_SOURCE_QUALITIES
    )

    return {
        "valid": valid,
        "value": value,
        "currency": (
            currency.upper()
            if currency is not None
            else None
        ),
        "source": source,
        "timestamp": timestamp,
        "source_quality": source_quality,
    }


def _process_identity(
    results: dict[str, Any],
) -> str | None:
    policy = results.get(
        "regen_manufacturing_tolerance_policy"
    )

    if isinstance(policy, dict):
        for key in (
            "process",
            "manufacturing_process",
            "process_name",
            "process_id",
        ):
            value = _text(
                policy.get(key)
            )

            if value is not None:
                return value

    for key in (
        "manufacturing_process",
        "process_name",
        "process_id",
    ):
        value = _text(
            results.get(key)
        )

        if value is not None:
            return value

    return None


def _material_component(
    *,
    component_name: str,
    material_name: str | None,
    quantity_key: str | None,
    mass_kg: float | None,
    price_record: Any,
) -> dict[str, Any]:
    if mass_kg is None:
        return {
            "component": component_name,
            "status":
                "NOT_EVALUATED_MISSING_CANONICAL_MATERIAL_QUANTITY",
            "calculated": False,
            "material": material_name,
            "quantity_key": quantity_key,
            "mass_kg": None,
            "unit_price_per_kg": None,
            "currency": None,
            "cost": None,
            "source": None,
            "timestamp": None,
            "source_quality": None,
        }

    if material_name is None:
        return {
            "component": component_name,
            "status":
                "NOT_EVALUATED_MISSING_MATERIAL_IDENTITY",
            "calculated": False,
            "material": None,
            "quantity_key": quantity_key,
            "mass_kg": mass_kg,
            "unit_price_per_kg": None,
            "currency": None,
            "cost": None,
            "source": None,
            "timestamp": None,
            "source_quality": None,
        }

    evidence = _source_record(
        price_record,
        "unit_price_per_kg",
    )

    if not evidence["valid"]:
        return {
            "component": component_name,
            "status":
                "NOT_EVALUATED_MISSING_SOURCED_UNIT_PRICE",
            "calculated": False,
            "material": material_name,
            "quantity_key": quantity_key,
            "mass_kg": mass_kg,
            "unit_price_per_kg":
                evidence["value"],
            "currency":
                evidence["currency"],
            "cost": None,
            "source":
                evidence["source"],
            "timestamp":
                evidence["timestamp"],
            "source_quality":
                evidence["source_quality"],
        }

    cost = (
        mass_kg
        *
        evidence["value"]
    )

    return {
        "component": component_name,
        "status":
            "CALCULATED_SOURCED_MATERIAL_COST",
        "calculated": True,
        "material": material_name,
        "quantity_key": quantity_key,
        "mass_kg": mass_kg,
        "unit_price_per_kg":
            evidence["value"],
        "currency":
            evidence["currency"],
        "cost": cost,
        "source":
            evidence["source"],
        "timestamp":
            evidence["timestamp"],
        "source_quality":
            evidence["source_quality"],
    }


def _manufacturing_component(
    *,
    process: str | None,
    process_record: Any,
) -> dict[str, Any]:
    if process is None:
        return {
            "status":
                "NOT_EVALUATED_MISSING_MANUFACTURING_PROCESS",
            "calculated": False,
            "process": None,
            "cost_basis_unit": None,
            "currency": None,
            "cost": None,
            "source": None,
            "timestamp": None,
            "source_quality": None,
        }

    if not isinstance(
        process_record,
        dict,
    ):
        return {
            "status":
                "NOT_EVALUATED_MISSING_SOURCED_PROCESS_COST_BASIS",
            "calculated": False,
            "process": process,
            "cost_basis_unit": None,
            "currency": None,
            "cost": None,
            "source": None,
            "timestamp": None,
            "source_quality": None,
        }

    basis = (
        _text(
            process_record.get(
                "cost_basis_unit"
            )
        )
        or
        ""
    ).upper()

    if basis not in {
        "PER_PART",
        "PART",
        "COST_PER_PART",
    }:
        return {
            "status":
                "NOT_EVALUATED_UNSUPPORTED_PROCESS_COST_BASIS",
            "calculated": False,
            "process": process,
            "cost_basis_unit":
                basis or None,
            "currency": None,
            "cost": None,
            "source":
                _text(
                    process_record.get(
                        "source"
                    )
                ),
            "timestamp":
                _text(
                    process_record.get(
                        "timestamp"
                    )
                ),
            "source_quality":
                _text(
                    process_record.get(
                        "source_quality"
                    )
                ),
        }

    evidence = _source_record(
        process_record,
        "cost_per_part",
    )

    if not evidence["valid"]:
        return {
            "status":
                "NOT_EVALUATED_MISSING_SOURCED_PROCESS_COST_BASIS",
            "calculated": False,
            "process": process,
            "cost_basis_unit":
                basis,
            "currency":
                evidence["currency"],
            "cost": None,
            "source":
                evidence["source"],
            "timestamp":
                evidence["timestamp"],
            "source_quality":
                evidence["source_quality"],
        }

    return {
        "status":
            "CALCULATED_SOURCED_MANUFACTURING_COST",
        "calculated": True,
        "process": process,
        "cost_basis_unit":
            "PER_PART",
        "currency":
            evidence["currency"],
        "cost":
            evidence["value"],
        "source":
            evidence["source"],
        "timestamp":
            evidence["timestamp"],
        "source_quality":
            evidence["source_quality"],
    }


def build_cost_intelligence(
    results: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    inputs = results.get(
        "cost_intelligence_inputs"
    )

    if not isinstance(inputs, dict):
        inputs = {}

    material_prices = inputs.get(
        "material_unit_prices"
    )

    if not isinstance(
        material_prices,
        dict,
    ):
        material_prices = {}

    process_costs = inputs.get(
        "manufacturing_process_costs"
    )

    if not isinstance(
        process_costs,
        dict,
    ):
        process_costs = {}

    base_material_name = _first_text(
        results,
        BASE_MATERIAL_NAME_KEYS,
    )

    base_quantity_key, base_mass = (
        _first_quantity(
            results,
            BASE_MATERIAL_MASS_KEYS,
        )
    )

    base_price_record = _lookup_record(
        material_prices,
        base_material_name,
    )

    base_component = _material_component(
        component_name="base_material",
        material_name=base_material_name,
        quantity_key=base_quantity_key,
        mass_kg=base_mass,
        price_record=base_price_record,
    )

    coating_material_name = _first_text(
        results,
        COATING_MATERIAL_NAME_KEYS,
    )

    coating_mass = _num(
        results.get(
            "explicit_coating_mass_total"
        )
    )

    if (
        coating_mass is not None
        and
        coating_mass < 0.0
    ):
        coating_mass = None

    coating_price_record = _lookup_record(
        material_prices,
        coating_material_name,
    )

    coating_component = _material_component(
        component_name="explicit_coating",
        material_name=coating_material_name,
        quantity_key=(
            "explicit_coating_mass_total"
            if coating_mass is not None
            else None
        ),
        mass_kg=coating_mass,
        price_record=coating_price_record,
    )

    process = _process_identity(
        results
    )

    process_record = _lookup_record(
        process_costs,
        process,
    )

    manufacturing_component = (
        _manufacturing_component(
            process=process,
            process_record=process_record,
        )
    )

    components = (
        base_component,
        coating_component,
        manufacturing_component,
    )

    calculated = [
        component
        for component in components
        if component.get(
            "calculated"
        )
        is True
    ]

    currencies = {
        component.get(
            "currency"
        )
        for component in calculated
        if component.get(
            "currency"
        )
    }

    if calculated and len(currencies) == 1:
        partial_currency = next(
            iter(currencies)
        )

        partial_total = sum(
            float(
                component["cost"]
            )
            for component in calculated
        )

        partial_status = (
            "CALCULATED_PARTIAL_COST"
            if len(calculated)
            <
            len(components)
            else
            "CALCULATED_COMPLETE_COST"
        )

    elif calculated:
        partial_currency = None
        partial_total = None
        partial_status = (
            "NOT_EVALUATED_MIXED_CURRENCY_COMPONENTS"
        )

    else:
        partial_currency = None
        partial_total = None
        partial_status = (
            "NOT_EVALUATED_NO_CALCULABLE_COST_COMPONENTS"
        )

    all_components_calculated = (
        len(calculated)
        ==
        len(components)
    )

    total_calculable = (
        all_components_calculated
        and
        len(currencies)
        ==
        1
    )

    total_cost = (
        partial_total
        if total_calculable
        else None
    )

    total_currency = (
        partial_currency
        if total_calculable
        else None
    )

    if total_calculable:
        total_status = (
            "CALCULATED_COMPLETE_SOURCED_COST"
        )

    elif (
        all_components_calculated
        and
        len(currencies)
        >
        1
    ):
        total_status = (
            "NOT_EVALUATED_MIXED_CURRENCY_COMPONENTS"
        )

    else:
        total_status = (
            "NOT_EVALUATED_INCOMPLETE_COST_COMPONENTS"
        )

    missing_requirements = []

    for component in components:
        if component.get(
            "calculated"
        ):
            continue

        missing_requirements.append(
            {
                "component":
                    component.get(
                        "component",
                        (
                            "manufacturing"
                            if component
                            is manufacturing_component
                            else "unknown"
                        ),
                    ),

                "status":
                    component.get(
                        "status"
                    ),
            }
        )

    return {
        "cost_intelligence_owner_complete":
            True,

        "cost_intelligence_owner":
            OWNER_NAME,

        "cost_intelligence_contract_version":
            CONTRACT_VERSION,

        "cost_intelligence_input_contract":
            (
                "cost_intelligence_inputs"
                ".material_unit_prices + "
                "cost_intelligence_inputs"
                ".manufacturing_process_costs"
            ),

        "cost_intelligence_live_market_fetch_performed":
            False,

        "cost_intelligence_physics_modified":
            False,

        "cost_base_material_component":
            base_component,

        "cost_base_material_status":
            base_component["status"],

        "cost_base_material":
            base_component["cost"],

        "cost_coating_material_component":
            coating_component,

        "cost_coating_material_status":
            coating_component["status"],

        "cost_coating_material":
            coating_component["cost"],

        "cost_manufacturing_component":
            manufacturing_component,

        "cost_manufacturing_status":
            manufacturing_component["status"],

        "cost_manufacturing":
            manufacturing_component["cost"],

        "cost_partial_status":
            partial_status,

        "cost_partial_total":
            partial_total,

        "cost_partial_currency":
            partial_currency,

        "cost_total_status":
            total_status,

        "cost_total":
            total_cost,

        "cost_total_currency":
            total_currency,

        "cost_total_complete":
            total_calculable,

        "cost_calculated_component_count":
            len(calculated),

        "cost_declared_component_count":
            len(components),

        "cost_missing_requirements":
            missing_requirements,
    }


def attach_cost_intelligence_owner(
    results: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    results.update(
        build_cost_intelligence(
            results
        )
    )

    return results
