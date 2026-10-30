OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_ENGINE"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_ENGINE_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_ENGINE_PHASE_14A"


def attach_regen_runtime_mutation_execution_engine(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_engine(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_engine(results):
    blockers = []

    registry = results.get("regen_runtime_mutation_execution_registry")
    packages = results.get("regen_runtime_mutation_source_packages", [])

    if not isinstance(registry, dict) or registry.get("ready") is not True:
        blockers.append("Runtime mutation execution registry is missing or not ready.")

    if not isinstance(packages, list) or not packages:
        blockers.append("Runtime mutation source packages are missing.")

    execution_records = []

    if isinstance(packages, list):
        for index, package in enumerate(packages):
            if not isinstance(package, dict):
                blockers.append(f"Mutation package at index {index} is not a dictionary.")
                continue

            record = _execute_package_as_runtime_record(package, index)
            execution_records.append(record)

    if not execution_records:
        blockers.append("No runtime mutation execution records were produced.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_mutation_execution_engine_complete": True,
        "phase_14a_runtime_mutation_execution_engine_complete": True,
        "regen_runtime_mutation_execution_engine_ready": ready,
        "regen_runtime_mutation_execution_engine_status": status,
        "regen_runtime_mutation_execution_engine_blockers": blockers,
        "regen_runtime_mutation_execution_records": execution_records if ready else [],
        "regen_runtime_mutation_execution_record_count": len(execution_records) if ready else 0,

        "regen_runtime_candidate_records": execution_records if ready else [],
        "regen_runtime_candidate_record_count": len(execution_records) if ready else 0,

        "regen_runtime_mutation_execution_performed": ready,
        "regen_runtime_mutation_solver_executed": False,
        "regen_runtime_mutation_candidate_evaluated": False,
        "regen_runtime_mutation_candidate_accepted": False,
        "regen_runtime_mutation_generation_advanced": False,
        "regen_runtime_mutation_live_geometry_committed": False,
    }


def _execute_package_as_runtime_record(package, index):
    package_id = _package_id(package, index)

    parent_candidate_id = (
        package.get("parent_candidate_id")
        or package.get("source_candidate_id")
        or package.get("candidate_id")
        or package.get("blueprint_id")
        or f"PARENT_{index:04d}"
    )

    runtime_candidate_id = f"RUNTIME_CANDIDATE_14A_{index:04d}"

    mutation_vector = _extract_mutation_vector(package)

    return {
        "runtime_candidate_id": runtime_candidate_id,
        "runtime_mutation_execution_id": f"RUNTIME_MUTATION_EXECUTION_14A_{index:04d}",
        "source_mutation_package_id": package_id,
        "parent_candidate_id": str(parent_candidate_id),
        "phase": PHASE,
        "owner": OWNER_NAME,
        "execution_state": "MUTATION_PACKAGE_TRANSLATED_TO_RUNTIME_RECORD",
        "runtime_candidate_created": True,
        "mutation_vector": mutation_vector,
        "source_package": package,

        "solver_executed": False,
        "candidate_evaluated": False,
        "candidate_accepted": False,
        "generation_advanced": False,
        "live_geometry_committed": False,
    }


def _extract_mutation_vector(package):
    explicit = package.get("mutation_vector")
    if isinstance(explicit, dict):
        return dict(explicit)

    vector = {}

    mutation_keys = [
        "channel_count",
        "coolant_channel_count",
        "channel_width",
        "coolant_channel_width",
        "channel_height",
        "coolant_channel_height",
        "rib_width",
        "wall_thickness",
        "coolant_split",
        "coolant_flow_fraction",
    ]

    for key in mutation_keys:
        if key in package:
            vector[key] = package.get(key)

    mutations = package.get("mutations")
    if isinstance(mutations, dict):
        vector.update(mutations)

    if not vector:
        vector["runtime_marker"] = "NO_GEOMETRY_CHANGE_APPLIED_IN_PHASE_14A"

    return vector


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
