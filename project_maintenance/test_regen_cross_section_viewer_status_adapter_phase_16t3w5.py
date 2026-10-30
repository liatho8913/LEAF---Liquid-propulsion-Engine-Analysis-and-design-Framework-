from pathlib import Path
import ast
import importlib.util
import sys

SOURCE = Path("leaf_qt/regen_cross_section_viewer.py")


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "regen_cross_section_viewer_phase_16t3w5",
        SOURCE,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_api_preserved_and_adapter_added():
    tree = ast.parse(SOURCE.read_text(errors="replace"))

    public_classes = {
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    }

    public_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    required_classes = {
        "InspectorSplitterHandle",
        "InspectorSplitter",
        "InspectorButton",
        "InspectorScrollArea",
        "RegenCrossSectionCanvas",
        "RegenCrossSectionViewer",
    }

    required_existing_functions = {
        "fallback_apply_geometry_result_phase_16p8",
        "fallback_solver_regeneration_request_phase_16p9",
        "fallback_before_after_comparison_phase_16p10",
    }

    assert required_classes <= public_classes
    assert required_existing_functions <= public_functions
    assert "attach_regen_cross_section_viewer_status_adapter" in public_functions


def test_viewer_status_adapter_preserves_legacy_payload():
    module = _load_module()

    payload = {
        "regen_overall_status": "PASS",
        "regen_geometry_status": "PASS",
        "phase_16p20_final_runtime_signoff_status": "PASS_RUNTIME",
        "legacy_value": 123,
    }

    before = dict(payload)
    adapted = module.attach_regen_cross_section_viewer_status_adapter(dict(payload))

    for key, value in before.items():
        assert adapted.get(key) == value, f"Legacy value changed: {key}"

    assert adapted["phase_16t3w5_status_adapter_complete"] is True
    assert adapted[
        "phase_16t3w5_regen_cross_section_viewer_status_adapter_complete"
    ] is True
    assert adapted["regen_cross_section_viewer_status_adapter_complete"] is True

    assert isinstance(adapted["regen_cross_section_viewer_structured_findings"], list)
    assert adapted["regen_cross_section_viewer_global_status"] in {
        "PASS",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "FAIL",
    }
    assert isinstance(adapted["regen_cross_section_viewer_global_status_payload"], dict)
    assert "REGEN CROSS SECTION VIEWER STATUS ADAPTER" in adapted[
        "regen_cross_section_viewer_adapter_report"
    ]

    assert adapted["structured_findings"] == adapted[
        "regen_cross_section_viewer_structured_findings"
    ]
    assert adapted["global_status"] == adapted[
        "regen_cross_section_viewer_global_status"
    ]
    assert adapted["global_status_payload"] == adapted[
        "regen_cross_section_viewer_global_status_payload"
    ]
    assert adapted["adapter_report"] == adapted[
        "regen_cross_section_viewer_adapter_report"
    ]


def test_viewer_adapter_detects_failure_status():
    module = _load_module()

    payload = {
        "regen_overall_status": "FAIL",
        "regen_geometry_status": "PASS",
    }

    adapted = module.attach_regen_cross_section_viewer_status_adapter(dict(payload))

    assert adapted["regen_cross_section_viewer_global_status"] == "FAIL"
    assert adapted["global_status"] == "FAIL"


def test_file_audit_phase_tokens_present():
    text = SOURCE.read_text(errors="replace")

    required = [
        "phase_16t3w5_status_adapter_complete",
        "regen_cross_section_viewer_structured_findings",
        "regen_cross_section_viewer_global_status_payload",
        "regen_cross_section_viewer_adapter_report",
        "attach_regen_cross_section_viewer_status_adapter",
    ]

    missing = [token for token in required if token not in text]
    assert not missing, f"Missing tokens: {missing}"

    forbidden = [
        "class RegenCrossSectionViewerV2",
        "class RegenCrossSectionCanvasV2",
    ]

    present = [token for token in forbidden if token in text]
    assert not present, f"Unexpected redesign tokens: {present}"


if __name__ == "__main__":
    test_public_api_preserved_and_adapter_added()
    test_viewer_status_adapter_preserves_legacy_payload()
    test_viewer_adapter_detects_failure_status()
    test_file_audit_phase_tokens_present()
    print("PASS_PHASE_16T3W5_REGEN_CROSS_SECTION_VIEWER_STATUS_ADAPTER")
