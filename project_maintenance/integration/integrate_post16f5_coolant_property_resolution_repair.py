from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_coolant_property_resolution_repair import attach_regen_coolant_property_resolution_repair
except Exception:
    attach_regen_coolant_property_resolution_repair = None
'''

if "attach_regen_coolant_property_resolution_repair" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwargs = '''
            attach_regen_coolant_property_resolution_repair=attach_regen_coolant_property_resolution_repair,
'''

if "attach_regen_coolant_property_resolution_repair=attach_regen_coolant_property_resolution_repair" not in controller_text:
    marker = "            attach_regen_input_mapping_repair=attach_regen_input_mapping_repair,"
    controller_text = controller_text.replace(marker, controller_kwargs + marker)

pipeline_params = '''
        attach_regen_coolant_property_resolution_repair=None,
'''

if "attach_regen_coolant_property_resolution_repair=None" not in pipeline_text:
    marker = "        attach_regen_input_mapping_repair=None,"
    pipeline_text = pipeline_text.replace(marker, pipeline_params + marker)

pipeline_plan = '''
        (
            "regen_coolant_property_resolution_repair",
            attach_regen_coolant_property_resolution_repair,
            (),
            {},
        ),
'''

if '"regen_coolant_property_resolution_repair"' not in pipeline_text:
    marker = '''        (
            "regen_input_mapping_repair",
            attach_regen_input_mapping_repair,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, pipeline_plan + marker)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated POST-16F.5 coolant property resolution repair.")
