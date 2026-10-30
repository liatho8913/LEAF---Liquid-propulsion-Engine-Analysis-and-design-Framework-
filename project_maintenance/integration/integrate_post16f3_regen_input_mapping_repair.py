from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_input_mapping_repair import attach_regen_input_mapping_repair
except Exception:
    attach_regen_input_mapping_repair = None
'''

if "attach_regen_input_mapping_repair" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwargs = '''
            attach_regen_input_mapping_repair=attach_regen_input_mapping_repair,
'''

if "attach_regen_input_mapping_repair=attach_regen_input_mapping_repair" not in controller_text:
    marker = "            attach_regen_completion_master_gate=attach_regen_completion_master_gate,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwargs)

pipeline_params = '''
        attach_regen_input_mapping_repair=None,
'''

if "attach_regen_input_mapping_repair=None" not in pipeline_text:
    marker = "        attach_regen_completion_master_gate=None,"
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_params)

pipeline_plan = '''
        (
            "regen_input_mapping_repair",
            attach_regen_input_mapping_repair,
            (),
            {},
        ),
'''

if '"regen_input_mapping_repair"' not in pipeline_text:
    marker = '''        (
            "regen_completion_master_gate",
            attach_regen_completion_master_gate,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_plan)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated POST-16F.3 regen input mapping repair.")
