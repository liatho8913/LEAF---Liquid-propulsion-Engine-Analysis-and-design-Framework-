from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_unified_viewer_integration_registry import attach_regen_unified_viewer_integration_registry
except Exception:
    attach_regen_unified_viewer_integration_registry = None

try:
    from regen_unified_viewer_routing_owner import attach_regen_unified_viewer_routing_owner
except Exception:
    attach_regen_unified_viewer_routing_owner = None

try:
    from regen_unified_viewer_synchronisation_owner import attach_regen_unified_viewer_synchronisation_owner
except Exception:
    attach_regen_unified_viewer_synchronisation_owner = None

try:
    from regen_unified_viewer_session_owner import attach_regen_unified_viewer_session_owner
except Exception:
    attach_regen_unified_viewer_session_owner = None

try:
    from regen_unified_viewer_state_owner import attach_regen_unified_viewer_state_owner
except Exception:
    attach_regen_unified_viewer_state_owner = None

try:
    from regen_unified_viewer_integration_completion_audit import attach_regen_unified_viewer_integration_completion_audit
except Exception:
    attach_regen_unified_viewer_integration_completion_audit = None

try:
    from regen_unified_viewer_integration_master_gate import attach_regen_unified_viewer_integration_master_gate
except Exception:
    attach_regen_unified_viewer_integration_master_gate = None
'''

if "attach_regen_unified_viewer_integration_registry" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwargs = '''
            attach_regen_unified_viewer_integration_registry=attach_regen_unified_viewer_integration_registry,
            attach_regen_unified_viewer_routing_owner=attach_regen_unified_viewer_routing_owner,
            attach_regen_unified_viewer_synchronisation_owner=attach_regen_unified_viewer_synchronisation_owner,
            attach_regen_unified_viewer_session_owner=attach_regen_unified_viewer_session_owner,
            attach_regen_unified_viewer_state_owner=attach_regen_unified_viewer_state_owner,
            attach_regen_unified_viewer_integration_completion_audit=attach_regen_unified_viewer_integration_completion_audit,
            attach_regen_unified_viewer_integration_master_gate=attach_regen_unified_viewer_integration_master_gate,
'''

if "attach_regen_unified_viewer_integration_registry=attach_regen_unified_viewer_integration_registry" not in controller_text:
    marker = "            attach_regen_unified_ecosystem_master_gate=attach_regen_unified_ecosystem_master_gate,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwargs)

pipeline_params = '''
        attach_regen_unified_viewer_integration_registry=None,
        attach_regen_unified_viewer_routing_owner=None,
        attach_regen_unified_viewer_synchronisation_owner=None,
        attach_regen_unified_viewer_session_owner=None,
        attach_regen_unified_viewer_state_owner=None,
        attach_regen_unified_viewer_integration_completion_audit=None,
        attach_regen_unified_viewer_integration_master_gate=None,
'''

if "attach_regen_unified_viewer_integration_registry=None" not in pipeline_text:
    marker = "        attach_regen_unified_ecosystem_master_gate=None,"
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_params)

pipeline_plan = '''
        (
            "regen_unified_viewer_integration_registry",
            attach_regen_unified_viewer_integration_registry,
            (),
            {},
        ),
        (
            "regen_unified_viewer_routing_owner",
            attach_regen_unified_viewer_routing_owner,
            (),
            {},
        ),
        (
            "regen_unified_viewer_synchronisation_owner",
            attach_regen_unified_viewer_synchronisation_owner,
            (),
            {},
        ),
        (
            "regen_unified_viewer_session_owner",
            attach_regen_unified_viewer_session_owner,
            (),
            {},
        ),
        (
            "regen_unified_viewer_state_owner",
            attach_regen_unified_viewer_state_owner,
            (),
            {},
        ),
        (
            "regen_unified_viewer_integration_completion_audit",
            attach_regen_unified_viewer_integration_completion_audit,
            (),
            {},
        ),
        (
            "regen_unified_viewer_integration_master_gate",
            attach_regen_unified_viewer_integration_master_gate,
            (),
            {},
        ),
'''

if '"regen_unified_viewer_integration_registry"' not in pipeline_text:
    marker = '''        (
            "regen_unified_ecosystem_master_gate",
            attach_regen_unified_ecosystem_master_gate,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_plan)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 16B unified viewer integration into foundation pipeline.")
