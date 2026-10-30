from core.contracts.base_contracts import validate_contract_metadata
from core.solver_adapters.engine_solver_adapter import (
    EngineSolverReadOnlyAdapter,
    make_engine_solver_read_only_adapter,
)


def demo_solver(inputs):
    return {
        "thrust_n": inputs["mass_flow_kg_s"] * inputs["effective_velocity_m_s"],
        "source": "demo_solver",
    }


def test_engine_solver_adapter_metadata():
    adapter = EngineSolverReadOnlyAdapter(solver_callable=demo_solver)

    metadata = adapter.contract_metadata()

    assert metadata["subsystem"] == "ENGINE_SOLVER"
    assert metadata["contract_name"] == "SOLVER_CONTRACT"
    assert metadata["mode"] == "READ_ONLY_ADAPTER"
    assert metadata["mutates_legacy_solver"] is False

    result = validate_contract_metadata(adapter)
    assert result.passed is True


def test_engine_solver_adapter_solves_without_mutating_inputs():
    adapter = make_engine_solver_read_only_adapter(demo_solver)

    inputs = {
        "mass_flow_kg_s": 2.0,
        "effective_velocity_m_s": 3000.0,
    }

    original = dict(inputs)
    result = adapter.solve(inputs)

    assert inputs == original
    assert result["thrust_n"] == 6000.0
    assert result["source"] == "demo_solver"


def test_engine_solver_adapter_records_evidence():
    adapter = make_engine_solver_read_only_adapter(demo_solver)

    adapter.solve(
        {
            "mass_flow_kg_s": 1.5,
            "effective_velocity_m_s": 2500.0,
        }
    )

    assert adapter.evidence["last_input_keys"] == [
        "effective_velocity_m_s",
        "mass_flow_kg_s",
    ]
    assert adapter.evidence["last_output_keys"] == [
        "source",
        "thrust_n",
    ]


def test_engine_solver_adapter_rejects_non_mapping_result():
    def bad_solver(inputs):
        return 123

    adapter = make_engine_solver_read_only_adapter(bad_solver)

    try:
        adapter.solve({"x": 1})
    except TypeError as exc:
        assert "Mapping" in str(exc)
    else:
        raise AssertionError("Expected TypeError for non-mapping solver result")


if __name__ == "__main__":
    test_engine_solver_adapter_metadata()
    test_engine_solver_adapter_solves_without_mutating_inputs()
    test_engine_solver_adapter_records_evidence()
    test_engine_solver_adapter_rejects_non_mapping_result()
    print("PASS_ENGINE_SOLVER_READ_ONLY_CONTRACT_ADAPTER_TEST")
