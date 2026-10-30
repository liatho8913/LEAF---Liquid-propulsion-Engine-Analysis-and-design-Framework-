from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_optimisation_foundation_registry import (
        attach_regen_optimisation_foundation_registry,
    )
except Exception:
    attach_regen_optimisation_foundation_registry = None

try:
    from regen_optimisation_foundation_validation_owner import (
        attach_regen_optimisation_foundation_validation_owner,
    )
except Exception:
    attach_regen_optimisation_foundation_validation_owner = None

try:
    from regen_optimisation_foundation_history_owner import (
        attach_regen_optimisation_foundation_history_owner,
    )
except Exception:
    attach_regen_optimisation_foundation_history_owner = None

try:
    from regen_optimisation_foundation_report_owner import (
        attach_regen_optimisation_foundation_report_owner,
    )
except Exception:
    attach_regen_optimisation_foundation_report_owner = None

try:
    from regen_optimisation_foundation_completion_audit import (
        attach_regen_optimisation_foundation_completion_audit,
    )
except Exception:
    attach_regen_optimisation_foundation_completion_audit = None

try:
    from regen_optimisation_foundation_master_gate import (
        attach_regen_optimisation_foundation_master_gate,
    )
except Exception:
    attach_regen_optimisation_foundation_master_gate = None
'''

if "attach_regen_optimisation_foundation_registry" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwargs = '''
            attach_regen_optimisation_foundation_registry=attach_regen_optimisation_foundation_registry,
            attach_regen_optimisation_foundation_validation_owner=attach_regen_optimisation_foundation_validation_owner,
            attach_regen_optimisation_foundation_history_owner=attach_regen_optimisation_foundation_history_owner,
            attach_regen_optimisation_foundation_report_owner=attach_regen_optimisation_foundation_report_owner,
            attach_regen_optimisation_foundation_completion_audit=attach_regen_optimisation_foundation_completion_audit,
            attach_regen_optimisation_foundation_master_gate=attach_regen_optimisation_foundation_master_gate,
'''

if "attach_regen_optimisation_foundation_registry=attach_regen_optimisation_foundation_registry" not in controller_text:
    marker = "            attach_regen_optimisation_selection_master_gate=attach_regen_optimisation_selection_master_gate,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwargs)

pipeline_params = '''
        attach_regen_optimisation_foundation_registry=None,
        attach_regen_optimisation_foundation_validation_owner=None,
        attach_regen_optimisation_foundation_history_owner=None,
        attach_regen_optimisation_foundation_report_owner=None,
        attach_regen_optimisation_foundation_completion_audit=None,
        attach_regen_optimisation_foundation_master_gate=None,
'''

if "attach_regen_optimisation_foundation_registry=None" not in pipeline_text:
    marker = "        attach_regen_optimisation_selection_master_gate=None,"
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_params)

pipeline_plan = '''
        (
            "regen_optimisation_foundation_registry",
            attach_regen_optimisation_foundation_registry,
            (),
            {},
        ),
        (
            "regen_optimisation_foundation_validation_owner",
            attach_regen_optimisation_foundation_validation_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_foundation_history_owner",
            attach_regen_optimisation_foundation_history_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_foundation_report_owner",
            attach_regen_optimisation_foundation_report_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_foundation_completion_audit",
            attach_regen_optimisation_foundation_completion_audit,
            (),
            {},
        ),
        (
            "regen_optimisation_foundation_master_gate",
            attach_regen_optimisation_foundation_master_gate,
            (),
            {},
        ),
'''

if '"regen_optimisation_foundation_registry"' not in pipeline_text:
    marker = '''        (
            "regen_optimisation_selection_master_gate",
            attach_regen_optimisation_selection_master_gate,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_plan)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 13L optimisation foundation into foundation pipeline.")
