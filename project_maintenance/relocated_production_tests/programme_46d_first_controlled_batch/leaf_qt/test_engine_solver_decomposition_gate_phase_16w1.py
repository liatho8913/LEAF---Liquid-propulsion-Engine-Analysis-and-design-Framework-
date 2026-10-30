from pathlib import Path
import json
import tempfile

from project_maintenance.production_historical_artifacts.leaf_qt.engine_solver_decomposition_gate import (
    PASS,
    analyse_engine_solver_decomposition_readiness,
    write_engine_solver_first_extraction_gate_report,
    simulate_engine_solver_first_extraction_dry_run,
    write_engine_solver_first_extraction_dry_run_report,
    apply_engine_solver_first_extraction,
    write_engine_solver_first_extraction_apply_report,
    evaluate_engine_solver_post_extraction_regression,
    write_engine_solver_post_extraction_regression_report,
    update_engine_solver_extraction_registry,
    audit_engine_solver_extraction_registry,
    write_engine_solver_extraction_registry_report,
    generate_engine_solver_extraction_closeout_certificate,
    write_engine_solver_extraction_closeout_certificate,
    evaluate_engine_solver_second_extraction_candidate_gate,
    write_engine_solver_second_extraction_candidate_report,
    simulate_engine_solver_second_extraction_dry_run,
    write_engine_solver_second_extraction_dry_run_report,
    apply_engine_solver_second_extraction,
    write_engine_solver_second_extraction_apply_report,
    evaluate_engine_solver_second_extraction_regression_registry_gate,
    write_engine_solver_second_extraction_regression_registry_report,
    generate_engine_solver_second_extraction_closeout_certificate,
    write_engine_solver_second_extraction_closeout_certificate,
)


def test_phase_16w1_engine_solver_first_extraction_gate_passes_on_safe_source():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "engine_solver.py"
        source.write_text(
            '''
def _regen_helper(value):
    return value + 1

def _geometry_helper(value):
    return value * 2

def solve_engine(inputs=None):
    return {"status": "PASS", "value": _regen_helper(1)}
''',
            encoding="utf-8",
        )

        gate = analyse_engine_solver_decomposition_readiness(source)

        assert gate.gate_status == PASS
        assert gate.compile_passed is True
        assert gate.public_contract_present is True
        assert gate.public_contract_move_allowed is False
        assert gate.low_risk_candidate_count >= 1
        assert gate.selected_first_extraction is not None
        assert gate.selected_first_extraction.name in {"_regen_helper", "_geometry_helper"}

        output_json = root / "gate.json"
        output_txt = root / "gate.txt"
        write_engine_solver_first_extraction_gate_report(gate, output_json, output_txt)

        assert output_json.exists()
        assert output_txt.exists()

        data = json.loads(output_json.read_text(encoding="utf-8"))
        assert data["phase"] == "16W.1"
        assert data["gate_status"] == PASS
        assert data["public_contract"] == "solve_engine"


def test_phase_16w1_engine_solver_gate_fails_without_public_contract():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "engine_solver.py"
        source.write_text(
            '''
def _regen_helper(value):
    return value + 1
''',
            encoding="utf-8",
        )

        gate = analyse_engine_solver_decomposition_readiness(source)

        assert gate.gate_status == "FAIL"
        assert gate.public_contract_present is False

def test_phase_16w11_second_extraction_regression_registry_gate_registers_second_helper():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "engine_solver.py"
        helper = root / "engine_solver_extracted_helpers.py"
        registry_path = root / "engine_solver_extraction_registry.json"

        source.write_text(
            """
def calculate_selected_station_length_default(value=1.0):
    return value

def calculate_coolant_flow_fraction_default(value=0.15):
    return value

def solve_engine(inputs=None):
    return {
        "status": "PASS",
        "a": calculate_selected_station_length_default(1.0),
        "b": calculate_coolant_flow_fraction_default(0.15),
    }
""",
            encoding="utf-8",
        )

        first_apply = apply_engine_solver_first_extraction(source_path=source, target_module_path=helper)
        assert first_apply.apply_status == PASS

        first_regression = evaluate_engine_solver_post_extraction_regression(
            source_path=source,
            helper_module_path=helper,
            helper_name="calculate_selected_station_length_default",
        )
        assert first_regression.regression_status == PASS

        first_registry = update_engine_solver_extraction_registry(first_regression, registry_path=registry_path)
        assert first_registry.registry_status == PASS

        second_apply = apply_engine_solver_second_extraction(
            source_path=source,
            helper_module_path=helper,
            registry_path=registry_path,
        )
        assert second_apply.apply_status == PASS

        gate = evaluate_engine_solver_second_extraction_regression_registry_gate(
            source_path=source,
            helper_module_path=helper,
            registry_path=registry_path,
            helper_name="calculate_coolant_flow_fraction_default",
        )

        assert gate.gate_status == PASS
        assert gate.regression_status == PASS
        assert gate.registry_update_status == PASS
        assert gate.registry_audit_status == PASS
        assert gate.registered_extraction_count == 2
        assert gate.public_contract_preserved is True

        output_json = root / "second_registry.json"
        output_txt = root / "second_registry.txt"
        write_engine_solver_second_extraction_regression_registry_report(gate, output_json, output_txt)

        assert output_json.exists()
        assert output_txt.exists()
        assert json.loads(output_json.read_text(encoding="utf-8"))["phase"] == "16W.11"

def test_phase_16w12_second_extraction_closeout_certificate_passes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "engine_solver.py"
        helper = root / "engine_solver_extracted_helpers.py"
        registry_path = root / "engine_solver_extraction_registry.json"

        source.write_text(
            """
def calculate_selected_station_length_default(value=1.0):
    return value

def calculate_coolant_flow_fraction_default(value=0.15):
    return value

def solve_engine(inputs=None):
    return {
        "status": "PASS",
        "a": calculate_selected_station_length_default(1.0),
        "b": calculate_coolant_flow_fraction_default(0.15),
    }
""",
            encoding="utf-8",
        )

        first_apply = apply_engine_solver_first_extraction(source_path=source, target_module_path=helper)
        assert first_apply.apply_status == PASS

        first_regression = evaluate_engine_solver_post_extraction_regression(
            source_path=source,
            helper_module_path=helper,
            helper_name="calculate_selected_station_length_default",
        )
        assert first_regression.regression_status == PASS

        first_registry = update_engine_solver_extraction_registry(first_regression, registry_path=registry_path)
        assert first_registry.registry_status == PASS

        second_apply = apply_engine_solver_second_extraction(
            source_path=source,
            helper_module_path=helper,
            registry_path=registry_path,
        )
        assert second_apply.apply_status == PASS

        second_gate = evaluate_engine_solver_second_extraction_regression_registry_gate(
            source_path=source,
            helper_module_path=helper,
            registry_path=registry_path,
            helper_name="calculate_coolant_flow_fraction_default",
        )
        assert second_gate.gate_status == PASS

        closeout = generate_engine_solver_second_extraction_closeout_certificate(
            source_path=source,
            helper_module_path=helper,
            registry_path=registry_path,
        )

        assert closeout.certificate_status == PASS
        assert closeout.certificate_decision == "SECOND_ENGINE_SOLVER_EXTRACTION_COMPLETE"
        assert closeout.registered_extraction_count == 2
        assert "calculate_selected_station_length_default" in closeout.registered_helpers
        assert "calculate_coolant_flow_fraction_default" in closeout.registered_helpers
        assert closeout.public_contract_preserved is True

        output_json = root / "second_closeout.json"
        output_txt = root / "second_closeout.txt"
        write_engine_solver_second_extraction_closeout_certificate(closeout, output_json, output_txt)

        assert output_json.exists()
        assert output_txt.exists()
        assert json.loads(output_json.read_text(encoding="utf-8"))["phase"] == "16W.12"


if __name__ == "__main__":
    test_phase_16w1_engine_solver_first_extraction_gate_passes_on_safe_source()
    test_phase_16w1_engine_solver_gate_fails_without_public_contract()
    print("PASS_PHASE_16W1_ENGINE_SOLVER_DECOMPOSITION_GATE_TESTS")