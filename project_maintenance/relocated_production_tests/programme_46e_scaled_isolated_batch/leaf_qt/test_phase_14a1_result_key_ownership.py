from foundation_result_key_audit import audit_result_keys


def main():
    results = {
        "phase_13k_status": "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K",
        "phase_13l_status": "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L",
        "phase_14a_status": "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A",

        "regen_optimisation_selection_registry_ready": True,
        "regen_optimisation_selection_ranked_candidates": [],
        "regen_optimisation_parent_pool": [],
        "regen_optimisation_foundation_complete": True,

        "regen_runtime_mutation_execution_records": [],
        "regen_runtime_candidate_records": [],
        "regen_runtime_candidate_record_count": 0,

        "selection_rank": 1,
        "selection_score": 100.0,
        "selected_for_parent_pool": True,
        "survives_generation": True,
    }

    audit = audit_result_keys(results)

    assert audit["foundation_result_key_audit_status"] == "PASS", audit
    assert audit["foundation_result_key_audit_unregistered_count"] == 0, audit

    print("PASS_PHASE_14A1_RESULT_KEY_OWNERSHIP_INTEGRATION")


if __name__ == "__main__":
    main()
