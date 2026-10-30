from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_optimisation_selection_ranking_engine import (
        attach_regen_optimisation_selection_ranking_engine,
    )
except Exception:
    attach_regen_optimisation_selection_ranking_engine = None

try:
    from regen_optimisation_selection_registry import (
        attach_regen_optimisation_selection_registry,
    )
except Exception:
    attach_regen_optimisation_selection_registry = None

try:
    from regen_optimisation_selection_validation_owner import (
        attach_regen_optimisation_selection_validation_owner,
    )
except Exception:
    attach_regen_optimisation_selection_validation_owner = None

try:
    from regen_optimisation_selection_parent_pool_builder import (
        attach_regen_optimisation_selection_parent_pool_builder,
    )
except Exception:
    attach_regen_optimisation_selection_parent_pool_builder = None

try:
    from regen_optimisation_selection_state_owner import (
        attach_regen_optimisation_selection_state_owner,
    )
except Exception:
    attach_regen_optimisation_selection_state_owner = None

try:
    from regen_optimisation_selection_history_owner import (
        attach_regen_optimisation_selection_history_owner,
    )
except Exception:
    attach_regen_optimisation_selection_history_owner = None

try:
    from regen_optimisation_selection_report_owner import (
        attach_regen_optimisation_selection_report_owner,
    )
except Exception:
    attach_regen_optimisation_selection_report_owner = None

try:
    from regen_optimisation_selection_completion_audit import (
        attach_regen_optimisation_selection_completion_audit,
    )
except Exception:
    attach_regen_optimisation_selection_completion_audit = None

try:
    from regen_optimisation_selection_master_gate import (
        attach_regen_optimisation_selection_master_gate,
    )
except Exception:
    attach_regen_optimisation_selection_master_gate = None
'''

if "attach_regen_optimisation_selection_ranking_engine" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwargs = '''
            attach_regen_optimisation_selection_ranking_engine=attach_regen_optimisation_selection_ranking_engine,
            attach_regen_optimisation_selection_registry=attach_regen_optimisation_selection_registry,
            attach_regen_optimisation_selection_validation_owner=attach_regen_optimisation_selection_validation_owner,
            attach_regen_optimisation_selection_parent_pool_builder=attach_regen_optimisation_selection_parent_pool_builder,
            attach_regen_optimisation_selection_state_owner=attach_regen_optimisation_selection_state_owner,
            attach_regen_optimisation_selection_history_owner=attach_regen_optimisation_selection_history_owner,
            attach_regen_optimisation_selection_report_owner=attach_regen_optimisation_selection_report_owner,
            attach_regen_optimisation_selection_completion_audit=attach_regen_optimisation_selection_completion_audit,
            attach_regen_optimisation_selection_master_gate=attach_regen_optimisation_selection_master_gate,
'''

if "attach_regen_optimisation_selection_ranking_engine=attach_regen_optimisation_selection_ranking_engine" not in controller_text:
    marker = "            attach_regen_optimisation_session_owner=attach_regen_optimisation_session_owner,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwargs)

pipeline_params = '''
        attach_regen_optimisation_selection_ranking_engine=None,
        attach_regen_optimisation_selection_registry=None,
        attach_regen_optimisation_selection_validation_owner=None,
        attach_regen_optimisation_selection_parent_pool_builder=None,
        attach_regen_optimisation_selection_state_owner=None,
        attach_regen_optimisation_selection_history_owner=None,
        attach_regen_optimisation_selection_report_owner=None,
        attach_regen_optimisation_selection_completion_audit=None,
        attach_regen_optimisation_selection_master_gate=None,
'''

if "attach_regen_optimisation_selection_ranking_engine=None" not in pipeline_text:
    marker = "        attach_material_property_interpolation_owner=None,"
    pipeline_text = pipeline_text.replace(marker, pipeline_params + marker)

pipeline_plan = '''
        (
            "regen_optimisation_selection_ranking_engine",
            attach_regen_optimisation_selection_ranking_engine,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_registry",
            attach_regen_optimisation_selection_registry,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_validation_owner",
            attach_regen_optimisation_selection_validation_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_parent_pool_builder",
            attach_regen_optimisation_selection_parent_pool_builder,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_state_owner",
            attach_regen_optimisation_selection_state_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_history_owner",
            attach_regen_optimisation_selection_history_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_report_owner",
            attach_regen_optimisation_selection_report_owner,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_completion_audit",
            attach_regen_optimisation_selection_completion_audit,
            (),
            {},
        ),
        (
            "regen_optimisation_selection_master_gate",
            attach_regen_optimisation_selection_master_gate,
            (),
            {},
        ),
'''

if '"regen_optimisation_selection_ranking_engine"' not in pipeline_text:
    marker = '''        (
            "material_property_interpolation_owner",
            attach_material_property_interpolation_owner,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, pipeline_plan + marker)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 13K selection framework into foundation pipeline.")
