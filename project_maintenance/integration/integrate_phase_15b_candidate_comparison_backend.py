from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_candidate_comparison_registry import attach_regen_candidate_comparison_registry
except Exception:
    attach_regen_candidate_comparison_registry = None

try:
    from regen_candidate_comparison_baseline_owner import attach_regen_candidate_comparison_baseline_owner
except Exception:
    attach_regen_candidate_comparison_baseline_owner = None

try:
    from regen_candidate_comparison_current_owner import attach_regen_candidate_comparison_current_owner
except Exception:
    attach_regen_candidate_comparison_current_owner = None

try:
    from regen_candidate_comparison_best_owner import attach_regen_candidate_comparison_best_owner
except Exception:
    attach_regen_candidate_comparison_best_owner = None

try:
    from regen_candidate_comparison_metrics_owner import attach_regen_candidate_comparison_metrics_owner
except Exception:
    attach_regen_candidate_comparison_metrics_owner = None

try:
    from regen_candidate_comparison_history_owner import attach_regen_candidate_comparison_history_owner
except Exception:
    attach_regen_candidate_comparison_history_owner = None

try:
    from regen_candidate_comparison_report_owner import attach_regen_candidate_comparison_report_owner
except Exception:
    attach_regen_candidate_comparison_report_owner = None

try:
    from regen_candidate_comparison_completion_audit import attach_regen_candidate_comparison_completion_audit
except Exception:
    attach_regen_candidate_comparison_completion_audit = None

try:
    from regen_candidate_comparison_master_gate import attach_regen_candidate_comparison_master_gate
except Exception:
    attach_regen_candidate_comparison_master_gate = None
'''

if "attach_regen_candidate_comparison_registry" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwargs = '''
            attach_regen_candidate_comparison_registry=attach_regen_candidate_comparison_registry,
            attach_regen_candidate_comparison_baseline_owner=attach_regen_candidate_comparison_baseline_owner,
            attach_regen_candidate_comparison_current_owner=attach_regen_candidate_comparison_current_owner,
            attach_regen_candidate_comparison_best_owner=attach_regen_candidate_comparison_best_owner,
            attach_regen_candidate_comparison_metrics_owner=attach_regen_candidate_comparison_metrics_owner,
            attach_regen_candidate_comparison_history_owner=attach_regen_candidate_comparison_history_owner,
            attach_regen_candidate_comparison_report_owner=attach_regen_candidate_comparison_report_owner,
            attach_regen_candidate_comparison_completion_audit=attach_regen_candidate_comparison_completion_audit,
            attach_regen_candidate_comparison_master_gate=attach_regen_candidate_comparison_master_gate,
'''

if "attach_regen_candidate_comparison_registry=attach_regen_candidate_comparison_registry" not in controller_text:
    marker = "            attach_regen_optimisation_viewer_master_gate=attach_regen_optimisation_viewer_master_gate,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwargs)

pipeline_params = '''
        attach_regen_candidate_comparison_registry=None,
        attach_regen_candidate_comparison_baseline_owner=None,
        attach_regen_candidate_comparison_current_owner=None,
        attach_regen_candidate_comparison_best_owner=None,
        attach_regen_candidate_comparison_metrics_owner=None,
        attach_regen_candidate_comparison_history_owner=None,
        attach_regen_candidate_comparison_report_owner=None,
        attach_regen_candidate_comparison_completion_audit=None,
        attach_regen_candidate_comparison_master_gate=None,
'''

if "attach_regen_candidate_comparison_registry=None" not in pipeline_text:
    marker = "        attach_regen_optimisation_viewer_master_gate=None,"
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_params)

pipeline_plan = '''
        (
            "regen_candidate_comparison_registry",
            attach_regen_candidate_comparison_registry,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_baseline_owner",
            attach_regen_candidate_comparison_baseline_owner,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_current_owner",
            attach_regen_candidate_comparison_current_owner,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_best_owner",
            attach_regen_candidate_comparison_best_owner,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_metrics_owner",
            attach_regen_candidate_comparison_metrics_owner,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_history_owner",
            attach_regen_candidate_comparison_history_owner,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_report_owner",
            attach_regen_candidate_comparison_report_owner,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_completion_audit",
            attach_regen_candidate_comparison_completion_audit,
            (),
            {},
        ),
        (
            "regen_candidate_comparison_master_gate",
            attach_regen_candidate_comparison_master_gate,
            (),
            {},
        ),
'''

if '"regen_candidate_comparison_registry"' not in pipeline_text:
    marker = '''        (
            "regen_optimisation_viewer_master_gate",
            attach_regen_optimisation_viewer_master_gate,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_plan)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 15B candidate comparison backend into foundation pipeline.")
