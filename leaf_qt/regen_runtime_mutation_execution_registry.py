OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_REGISTRY"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_REGISTRY_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_REGISTRY_PHASE_14A"


def attach_regen_runtime_mutation_execution_registry(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_registry(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_registry(results):
    blockers = []

    allowed = results.get("phase_14a_runtime_mutation_execution_allowed") is True
    foundation_complete = (
        results.get("phase_13l_complete") is True
        or results.get("regen_optimisation_foundation_complete") is True
        or results.get("phase_13l_status") == "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L"
    )

    if not allowed:
        blockers.append("Phase 14A runtime mutation execution has not been unlocked by Phase 13L.")

    if not foundation_complete:
        blockers.append("Phase 13L optimisation foundation is not complete.")

    mutation_packages = _collect_mutation_packages(results)

    if not mutation_packages:
        blockers.append("No mutation packages are available for controlled runtime execution.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    registry = None

    if ready:
        registry = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": True,
            "runtime_mutation_execution_registry_id": "RUNTIME_MUTATION_EXECUTION_REGISTRY_PHASE_14A",
            "source_mutation_package_count": len(mutation_packages),
            "source_package_ids": [
                _package_id(package, index)
                for index, package in enumerate(mutation_packages)
            ],
            "permissions": {
                "runtime_mutation_execution_allowed": True,
                "runtime_candidate_record_creation_allowed": True,
                "solver_execution_allowed": False,
                "candidate_evaluation_allowed": False,
                "candidate_acceptance_allowed": False,
                "generation_advance_allowed": False,
                "live_geometry_commit_allowed": False,
                "full_runtime_optimisation_allowed": False,
            },
        }

    return {
        "regen_runtime_mutation_execution_registry_complete": True,
        "phase_14a_runtime_mutation_execution_registry_complete": True,
        "regen_runtime_mutation_execution_registry_ready": ready,
        "regen_runtime_mutation_execution_registry_status": status,
        "regen_runtime_mutation_execution_registry_blockers": blockers,
        "regen_runtime_mutation_execution_registry": registry,
        "regen_runtime_mutation_source_packages": mutation_packages if ready else [],

        "regen_runtime_mutation_solver_executed": False,
        "regen_runtime_mutation_candidate_evaluated": False,
        "regen_runtime_mutation_candidate_accepted": False,
        "regen_runtime_mutation_generation_advanced": False,
        "regen_runtime_mutation_live_geometry_committed": False,
    }


def _collect_mutation_packages(results):
    keys = [
        "regen_multi_variable_mutation_packages",
        "regen_candidate_mutation_packages",
        "regen_mutation_package_records",
        "regen_candidate_improvement_validation_records",
        "regen_optimisation_parent_pool",
    ]

    for key in keys:
        value = results.get(key)
        if isinstance(value, list) and value:
            return [item for item in value if isinstance(item, dict)]

    container_keys = [
        "regen_multi_variable_mutation_framework",
        "regen_candidate_mutation_framework",
        "regen_optimisation_selection_state",
    ]

    for key in container_keys:
        value = results.get(key)
        if isinstance(value, dict):
            for inner_key in ("packages", "mutation_packages", "records", "candidates"):
                inner = value.get(inner_key)
                if isinstance(inner, list) and inner:
                    return [item for item in inner if isinstance(item, dict)]

    return []


def _package_id(package, index):
    for key in (
        "mutation_package_id",
        "package_id",
        "candidate_id",
        "blueprint_id",
        "record_id",
    ):
        value = package.get(key)
        if value:
            return str(value)

    return f"RUNTIME_MUTATION_PACKAGE_{index:04d}"
