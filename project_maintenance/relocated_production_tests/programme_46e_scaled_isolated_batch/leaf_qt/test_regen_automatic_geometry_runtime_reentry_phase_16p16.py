from regen_automatic_geometry_runtime_reentry_owner_phase_16p16 import (
    build_runtime_reentry_candidate,
    purge_stale_automatic_geometry,
)


def main() -> int:
    stale = {
        "regen_geometry_commit_staged_geometry": {
            "coolant_channel_width": 0.001425,
            "coolant_channel_height": 0.0021,
            "rib_width": 0.001,
            "number_of_coolant_channels": 80,
        },
        "regen_autonomous_geometry_staged_candidate": {
            "ready": True,
            "staged_geometry": {
                "coolant_channel_width": 0.001425,
                "coolant_channel_height": 0.0021,
            },
        },
    }

    purge_stale_automatic_geometry(stale)

    assert "regen_geometry_commit_staged_geometry" not in stale
    assert "regen_autonomous_geometry_staged_candidate" not in stale
    assert stale["phase_16p16_stale_payload_removed_count"] == 2

    results = {
        "regen_geometry_commit_staged_geometry": {
            "coolant_channel_width": 0.001425,
            "coolant_channel_height": 0.0021,
        }
    }

    manual = {
        "channel_width": 0.0015,
        "channel_height": 0.002,
        "requested_rib_width": 0.001,
        "channel_count": 80,
        "wall": 0.001104,
        "gas_radius": 0.01,
        "minimum_gas_radius": 0.01,
    }

    build_runtime_reentry_candidate(results, manual)

    assert results["phase_16p16_runtime_reentry_status"] == (
        "PASS_REGEN_AUTOMATIC_GEOMETRY_RUNTIME_REENTRY_PHASE_16P16"
    )
    assert results["phase_16p16_runtime_reentry_pass"] is True

    staged = results["regen_geometry_commit_staged_geometry"]

    assert staged["coolant_channel_width"] != 0.001425
    assert staged["coolant_channel_height"] != 0.0021
    assert staged["channel_geometry_valid"] == 1.0
    assert staged["channel_fit_ratio"] >= 1.0
    assert staged["effective_rib_width"] > 0.0

    print("PASS_REGEN_AUTOMATIC_GEOMETRY_RUNTIME_REENTRY_PHASE_16P16")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
