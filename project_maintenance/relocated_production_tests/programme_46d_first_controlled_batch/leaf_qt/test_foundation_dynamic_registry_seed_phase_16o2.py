from foundation_dynamic_registry_seed_phase_16o2 import (
    classify_dynamic_key,
    build_dynamic_registry_seed,
)


def main() -> int:
    assert classify_dynamic_key("phase_16m4_status") is not None
    assert classify_dynamic_key("regen_final_master_gate_report") is not None
    assert classify_dynamic_key("random_scalar_value", 123.0) is None
    assert classify_dynamic_key("some_payload", {"x": 1}) is not None

    results = {
        "phase_16m4_status": "PASS",
        "regen_final_master_gate_report": "text",
        "random_scalar_value": 123.0,
        "nested_payload": {"x": 1},
    }

    seed = build_dynamic_registry_seed(results)

    assert seed["phase_16o2_dynamic_registry_seed_complete"] is True
    assert seed["phase_16o2_dynamic_registry_seed_count"] == 3
    assert "phase_16m4_status" in seed["phase_16o2_dynamic_registry_seed_keys"]
    assert "random_scalar_value" not in seed["phase_16o2_dynamic_registry_seed_keys"]

    print("PASS_FOUNDATION_DYNAMIC_REGISTRY_SEED_PHASE_16O2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
