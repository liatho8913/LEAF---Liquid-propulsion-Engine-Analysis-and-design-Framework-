from regen_manufacturability_geometry_gate_phase_16q3 import evaluate_manufacturability_geometry


def main() -> int:
    unrealistic = {
        "coolant_channel_width": 0.000624594,
        "coolant_channel_height": 0.00480312,
        "rib_width": 0.000436,
        "effective_rib_width": 0.000436,
        "cooling_coverage": 0.588,
    }

    bad = evaluate_manufacturability_geometry(unrealistic)

    assert bad["passed"] is False
    assert bad["status"] == "FAIL_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_PHASE_16Q3"
    assert bad["aspect_ratio"] > 4.0
    assert len(bad["blockers"]) >= 1

    realistic = {
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0024,
        "rib_width": 0.00035,
        "effective_rib_width": 0.00035,
        "cooling_coverage": 0.82,
    }

    good = evaluate_manufacturability_geometry(realistic)

    assert good["passed"] is True
    assert good["status"] == "PASS_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_PHASE_16Q3"




    print("PASS_REGEN_MANUFACTURABILITY_GEOMETRY_GATE_PHASE_16Q3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
