from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_candidate_base_geometry_population_repair import attach_regen_candidate_base_geometry_population_repair
except Exception:
    attach_regen_candidate_base_geometry_population_repair = None
'''

if "attach_regen_candidate_base_geometry_population_repair" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwarg = '''
            attach_regen_candidate_base_geometry_population_repair=attach_regen_candidate_base_geometry_population_repair,
'''

if "attach_regen_candidate_base_geometry_population_repair=attach_regen_candidate_base_geometry_population_repair" not in controller_text:
    marker = "            attach_regen_candidate_generator_data_source_repair=attach_regen_candidate_generator_data_source_repair,"
    if marker not in controller_text:
        marker = "            attach_regen_coolant_flow_activation_layer=attach_regen_coolant_flow_activation_layer,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwarg)

pipeline_param = '''
        attach_regen_candidate_base_geometry_population_repair=None,
'''

if "attach_regen_candidate_base_geometry_population_repair=None" not in pipeline_text:
    marker = "        attach_regen_candidate_generator_data_source_repair=None,"
    if marker not in pipeline_text:
        marker = "        attach_regen_coolant_flow_activation_layer=None,"
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_param)

pipeline_plan = '''
        (
            "regen_candidate_base_geometry_population_repair",
            attach_regen_candidate_base_geometry_population_repair,
            (),
            {},
        ),
'''

if '"regen_candidate_base_geometry_population_repair"' not in pipeline_text:
    marker = '''        (
            "regen_candidate_generator",
            attach_regen_candidate_generator,
            (),
            {},
        ),'''
    if marker in pipeline_text:
        pipeline_text = pipeline_text.replace(marker, pipeline_plan + marker)
    else:
        marker = '''        (
            "regen_candidate_generator_data_source_repair",
            attach_regen_candidate_generator_data_source_repair,
            (),
            {},
        ),'''
        pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_plan)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 16J.3C base geometry population repair.")
