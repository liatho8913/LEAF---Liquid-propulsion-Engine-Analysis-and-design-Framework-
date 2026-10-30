from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_coolant_flow_activation_layer import attach_regen_coolant_flow_activation_layer
except Exception:
    attach_regen_coolant_flow_activation_layer = None
'''

if "attach_regen_coolant_flow_activation_layer" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwarg = '''
            attach_regen_coolant_flow_activation_layer=attach_regen_coolant_flow_activation_layer,
'''

if "attach_regen_coolant_flow_activation_layer=attach_regen_coolant_flow_activation_layer" not in controller_text:
    marker = "            attach_regen_coolant_property_resolution_repair=attach_regen_coolant_property_resolution_repair,"
    if marker not in controller_text:
        marker = "            attach_regen_input_mapping_repair=attach_regen_input_mapping_repair,"
    controller_text = controller_text.replace(marker, controller_kwarg + marker)

pipeline_param = '''
        attach_regen_coolant_flow_activation_layer=None,
'''

if "attach_regen_coolant_flow_activation_layer=None" not in pipeline_text:
    marker = "        attach_regen_coolant_property_resolution_repair=None,"
    if marker not in pipeline_text:
        marker = "        attach_regen_input_mapping_repair=None,"
    pipeline_text = pipeline_text.replace(marker, pipeline_param + marker)

pipeline_plan = '''
        (
            "regen_coolant_flow_activation_layer",
            attach_regen_coolant_flow_activation_layer,
            (),
            {},
        ),
'''

if '"regen_coolant_flow_activation_layer"' not in pipeline_text:
    marker = '''        (
            "regen_coolant_property_resolution_repair",
            attach_regen_coolant_property_resolution_repair,
            (),
            {},
        ),'''
    if marker not in pipeline_text:
        marker = '''        (
            "regen_input_mapping_repair",
            attach_regen_input_mapping_repair,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, pipeline_plan + marker)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 16J.2A coolant flow activation layer.")
