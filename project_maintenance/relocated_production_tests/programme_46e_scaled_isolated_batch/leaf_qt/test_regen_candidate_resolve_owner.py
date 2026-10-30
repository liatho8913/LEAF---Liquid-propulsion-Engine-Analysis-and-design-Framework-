from regen_candidate_resolve_owner import attach_regen_candidate_resolve_owner


def test_resolve_owner_builds_patched_clone_state():
    results = {
        "Pc": 6895000.0,
        "m_dot": 1.15,
        "mixture_ratio": 1.875,
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0010,
        "regen_candidate_application_ready": True,
        "regen_candidate_application_patch": {
            "candidate_id": "RCG-0001",
            "patch_values": {
                "number_of_coolant_channels": 96,
                "coolant_channel_width": 0.0012,
                "coolant_channel_height": 0.0025,
                "rib_width": 0.0008,
                "hot_gas_wall_thickness": 0.00125,
            },
        },
    }

    updated = attach_regen_candidate_resolve_owner(results)

    assert updated["phase_11b_1g_regen_candidate_resolve_owner_complete"] is True
    assert updated["regen_candidate_resolve_owner_complete"] is True
    assert updated["regen_candidate_resolve_owner_status"] == (
        "PASS_REGEN_CANDIDATE_RESOLVE_READY"
    )
    assert updated["regen_candidate_resolve_ready"] is True
    assert updated["regen_candidate_resolve_solver_executed"] is False
    assert updated["regen_candidate_original_state_mutated"] is False
    assert updated["regen_candidate_geometry_applied_to_live_design"] is False

    state = updated["regen_candidate_resolve_cloned_state"]
    patched = state["patched_clone"]

    assert patched["number_of_coolant_channels"] == 96
    assert patched["coolant_channel_width"] == 0.0012
    assert state["original_snapshot"]["number_of_coolant_channels"] == 80
    assert state["differences"]["number_of_coolant_channels"]["old"] == 80
    assert state["differences"]["number_of_coolant_channels"]["new"] == 96

    assert results["number_of_coolant_channels"] == 80


def test_resolve_owner_blocks_without_ready_patch():
    results = {
        "regen_candidate_application_ready": False,
        "regen_candidate_application_patch": None,
    }

    updated = attach_regen_candidate_resolve_owner(results)

    assert updated["regen_candidate_resolve_owner_status"] == (
        "FAIL_REGEN_CANDIDATE_RESOLVE_PREPARATION"
    )
    assert updated["regen_candidate_resolve_ready"] is False
    assert updated["regen_candidate_resolve_cloned_state"] is None