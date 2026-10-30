"""
LEAF Phase 16O.2
Automatic Foundation Registry Seeder

Purpose:
- Discover framework-generated diagnostic/report keys.
- Classify them by prefix/suffix.
- Produce registry seed entries without manually registering thousands of keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DIAGNOSTIC_SUFFIXES = (
    "_attachment_status",
    "_attachment_message",
    "_attachment_error_type",
    "_attachment_traceback",
    "_status",
    "_complete",
    "_ready",
    "_allowed",
    "_enabled",
    "_blocked",
    "_blockers",
    "_warnings",
    "_warning_reasons",
    "_blocking_reasons",
    "_failed_checks",
    "_checks",
    "_text",
    "_report",
    "_summary",
    "_payload",
    "_history",
    "_evidence",
    "_snapshot",
    "_visibility",
)

DIAGNOSTIC_PREFIXES = (
    "phase_",
    "regen_",
    "material_",
    "coating_",
    "bond_coat_",
    "foundation_",
    "benchmark_",
    "public_benchmark_",
    "real_engine_benchmark_",
    "candidate_comparison_",
    "evolution_tree_",
    "optimisation_",
    "runtime_",
    "output_",
    "before_after_comparison_",
    "unified_regen_",
    "stage_",
    "selected_",
    "survives_",
    "failure_root_cause_",
    "recommendation_",
    "design_iteration_",
)


@dataclass(frozen=True)
class DynamicRegistrySeed:
    key: str
    visibility: str
    reason: str


def classify_dynamic_key(key: str, value: Any = None) -> DynamicRegistrySeed | None:
    if not isinstance(key, str) or not key:
        return None

    if key.startswith(DIAGNOSTIC_PREFIXES):
        return DynamicRegistrySeed(
            key=key,
            visibility="DIAGNOSTIC_ONLY",
            reason="Known framework/generated diagnostic prefix.",
        )

    if key.endswith(DIAGNOSTIC_SUFFIXES):
        return DynamicRegistrySeed(
            key=key,
            visibility="DIAGNOSTIC_ONLY",
            reason="Known framework/generated diagnostic suffix.",
        )

    if isinstance(value, (dict, list, tuple, set)):
        return DynamicRegistrySeed(
            key=key,
            visibility="DIAGNOSTIC_ONLY",
            reason="Non-scalar generated payload.",
        )

    return None


def build_dynamic_registry_seed(results: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(results, dict):
        results = {}

    seeds = []

    for key, value in sorted(results.items()):
        seed = classify_dynamic_key(key, value)
        if seed is not None:
            seeds.append(seed)

    return {
        "phase_16o2_dynamic_registry_seed_complete": True,
        "phase_16o2_dynamic_registry_seed_count": len(seeds),
        "phase_16o2_dynamic_registry_seed_keys": [seed.key for seed in seeds],
        "phase_16o2_dynamic_registry_seed_entries": [
            {
                "key": seed.key,
                "visibility": seed.visibility,
                "reason": seed.reason,
            }
            for seed in seeds
        ],
        "phase_16o2_dynamic_registry_seed_status": (
            "PASS_DYNAMIC_REGISTRY_SEED_AVAILABLE_PHASE_16O2"
        ),
    }
