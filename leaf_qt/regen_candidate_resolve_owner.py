"""
LEAF Regen Candidate Re-Solve Preparation Owner
==============================================

PHASE 11B.1G

Creates a cloned patched engine state from the validated application patch.

This module DOES:
- preserve the original engine state
- clone current results/input state
- apply recommended regen geometry patch to the clone
- publish re-solve readiness data

This module DOES NOT:
- mutate the original engine
- run the solver
- claim post-application validation has passed
"""

import copy


REQUIRED_RESOLVE_PATCH_KEYS = [
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
]


def attach_regen_candidate_resolve_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_resolve_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_resolve_owner(results):
    patch = results.get("regen_candidate_application_patch")
    patch_ready = bool(results.get("regen_candidate_application_ready", False))

    blocking_reasons = []

    if not patch:
        blocking_reasons.append("No regen candidate application patch is available.")

    if not patch_ready:
        blocking_reasons.append("Application patch is not marked ready.")

    cloned_state = None

    if patch and patch_ready:
        cloned_state = build_patched_clone_state(results, patch)
        blocking_reasons.extend(validate_patched_clone_state(cloned_state, patch))

        # Programme 48U:
        # an unchanged geometry is still a valid engineering
        # qualification candidate.  Preserve the normal no-op
        # application block except in this explicit non-mutating
        # population-evaluation scope.
        if results.get(
                "_leaf_48u_candidate_qualification_evaluation_active",
                False,
        ) is True:
            blocking_reasons = [
                reason
                for reason in blocking_reasons
                if reason != (
                    "Patched clone contains no differences from "
                    "original snapshot."
                )
            ]

    if blocking_reasons:
        status = "FAIL_REGEN_CANDIDATE_RESOLVE_PREPARATION"
        ready = False
    else:
        status = "PASS_REGEN_CANDIDATE_RESOLVE_READY"
        ready = True

    report = build_resolve_report(
        status=status,
        ready=ready,
        cloned_state=cloned_state,
        patch=patch,
        blocking_reasons=blocking_reasons,
    )

    return {
        "regen_candidate_resolve_owner_complete": True,
        "phase_11b_1g_regen_candidate_resolve_owner_complete": True,
        "regen_candidate_resolve_owner_status": status,
        "regen_candidate_resolve_ready": ready,
        "regen_candidate_resolve_blocking_reasons": blocking_reasons,
        "regen_candidate_resolve_patch": patch,
        "regen_candidate_resolve_cloned_state": cloned_state,
        "regen_candidate_resolve_report": report,

        # Explicit safety locks.
        "regen_candidate_resolve_solver_execution_allowed": ready,
        "regen_candidate_resolve_solver_executed": False,
        "regen_candidate_original_state_mutated": False,
        "regen_candidate_geometry_applied_to_live_design": False,

        # Compatibility aliases.
        "recommended_regen_resolve_state": cloned_state,
        "recommended_regen_resolve_ready": ready,
        "recommended_regen_resolve_report": report,
    }


def build_patched_clone_state(results, patch):
    original_snapshot = build_original_snapshot(results)
    cloned_state = copy.deepcopy(original_snapshot)

    patch_values = patch.get("patch_values") or {}

    for key, value in patch_values.items():
        cloned_state[key] = value

    cloned_state["_regen_candidate_resolve_metadata"] = {
        "source": "regen_candidate_resolve_owner.py",
        "phase": "PHASE_11B_1G",
        "candidate_id": patch.get("candidate_id"),
        "resolve_mode": "CLONED_PATCHED_STATE_ONLY",
        "solver_executed": False,
        "original_state_mutated": False,
        "live_geometry_modified": False,
    }

    return {
        "candidate_id": patch.get("candidate_id"),
        "source": "regen_candidate_resolve_owner.py",
        "phase": "PHASE_11B_1G",
        "resolve_status": "CLONED_STATE_PREPARED_REQUIRES_SOLVER_EXECUTION",
        "original_snapshot": original_snapshot,
        "patched_clone": cloned_state,
        "applied_patch_values": patch_values,
        "differences": build_state_differences(original_snapshot, cloned_state),
        "solver_executed": False,
        "original_state_mutated": False,
        "live_geometry_modified": False,
    }


def build_original_snapshot(results):
    snapshot = {}

    preferred_keys = [
        "Pc",
        "chamber_pressure",
        "Tc",
        "chamber_temperature",
        "m_dot",
        "mass_flow_rate",
        "mixture_ratio",
        "fuel_mass_flow_rate",
        "oxidizer_mass_flow_rate",
        "throat_area",
        "exit_area",
        "expansion_ratio",
        "number_of_coolant_channels",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
        "coolant_mass_flow_fraction",
        "selected_material",
        "selected_coating",
        "selected_bond_coat",
    ]

    for key in preferred_keys:
        if key in results:
            snapshot[key] = copy.deepcopy(results.get(key))

    return snapshot


def build_state_differences(original, patched):
    differences = {}

    all_keys = sorted(set(original.keys()) | set(patched.keys()))

    for key in all_keys:
        if key.startswith("_"):
            continue

        old = original.get(key)
        new = patched.get(key)

        if old != new:
            differences[key] = {
                "old": old,
                "new": new,
                "changed": True,
                "ratio": _ratio(new, old),
            }

    return differences


def validate_patched_clone_state(cloned_state, patch):
    reasons = []

    if not cloned_state:
        reasons.append("Patched clone state was not created.")
        return reasons

    patched = cloned_state.get("patched_clone") or {}
    original = cloned_state.get("original_snapshot") or {}
    differences = cloned_state.get("differences") or {}
    patch_values = patch.get("patch_values") or {}

    for key in REQUIRED_RESOLVE_PATCH_KEYS:
        if key not in patched:
            reasons.append(f"Patched clone missing required key: {key}.")
        elif _num(patched.get(key)) is None:
            reasons.append(f"Patched clone value is not numeric: {key}.")
        elif _num(patched.get(key)) <= 0:
            reasons.append(f"Patched clone value must be positive: {key}={patched.get(key)}.")

    for key, value in patch_values.items():
        if patched.get(key) != value:
            reasons.append(f"Patch value was not applied to clone: {key}.")

    if not differences:
        reasons.append("Patched clone contains no differences from original snapshot.")

    if cloned_state.get("original_state_mutated"):
        reasons.append("Original state mutation flag was unexpectedly true.")

    if cloned_state.get("live_geometry_modified"):
        reasons.append("Live geometry modification flag was unexpectedly true.")

    if cloned_state.get("solver_executed"):
        reasons.append("Solver execution flag was unexpectedly true.")

    return reasons


def build_resolve_report(
        status,
        ready,
        cloned_state,
        patch,
        blocking_reasons,
):
    lines = [
        "LEAF PHASE 11B.1G REGEN CANDIDATE RE-SOLVE PREPARATION OWNER",
        "=============================================================",
        "",
        f"Status: {status}",
        f"Resolve ready: {ready}",
        f"Candidate ID: {patch.get('candidate_id') if patch else None}",
        "",
        "Scope:",
        "- Builds a cloned patched state for future solver execution.",
        "- Preserves the original engine state.",
        "- Does not run the solver.",
        "- Does not modify live geometry.",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    if cloned_state:
        lines.extend([
            "",
            "Differences:",
        ])

        for key, payload in (cloned_state.get("differences") or {}).items():
            lines.append(
                f"- {key}: old={payload.get('old')}, "
                f"new={payload.get('new')}, ratio={payload.get('ratio')}"
            )

        lines.extend([
            "",
            "Safety State:",
            f"- Solver executed: {cloned_state.get('solver_executed')}",
            f"- Original state mutated: {cloned_state.get('original_state_mutated')}",
            f"- Live geometry modified: {cloned_state.get('live_geometry_modified')}",
        ])

    return "\n".join(lines)


def _num(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _ratio(new_value, old_value):
    try:
        if old_value in (None, 0):
            return None
        return float(new_value) / float(old_value)
    except Exception:
        return None