OWNER_NAME = "REGEN_UNIFIED_VALIDATION_ROUTING_OWNER"
PHASE = "16D"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_ROUTING_OWNER_PHASE_16D"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_ROUTING_OWNER_PHASE_16D"


def attach_regen_unified_validation_routing_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_validation_integration_registry_ready") is not True:
        blockers.append("Unified validation integration registry is not ready.")

    validations = results.get("unified_regen_registered_validations", [])
    if not isinstance(validations, list) or not validations:
        blockers.append("Unified registered validations are missing.")

    routes = []

    if isinstance(validations, list):
        for index, validation in enumerate(validations):
            if not isinstance(validation, dict):
                blockers.append(f"Validation registration at index {index} is not a dictionary.")
                continue

            validation_id = validation.get("validation_id")
            source_key = validation.get("source_key")

            if not validation_id:
                blockers.append(f"Validation registration at index {index} is missing validation_id.")
                continue

            routes.append({
                "validation_route_id": f"UNIFIED_VALIDATION_ROUTE_16D_{index:04d}",
                "validation_id": validation_id,
                "source_key": source_key,
                "route_active": True,
                "displayed": False,
                "ui_created": False,
            })

    if not routes:
        blockers.append("No unified validation routes were created.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_validation_routing_owner_complete": True,
        "phase_16d_unified_validation_routing_owner_complete": True,
        "regen_unified_validation_routing_owner_ready": ready,
        "regen_unified_validation_routing_owner_status": status,
        "regen_unified_validation_routing_owner_blockers": blockers,

        "unified_regen_validation_routes": routes if ready else [],
        "unified_regen_validation_route_count": len(routes) if ready else 0,
    })

    return results
