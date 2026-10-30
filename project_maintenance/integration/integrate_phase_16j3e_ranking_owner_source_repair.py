from pathlib import Path

root = Path("leaf_qt")
controller = root / "foundation_layer_controller.py"
pipeline = root / "foundation_attachment_pipeline.py"

controller_text = controller.read_text()
pipeline_text = pipeline.read_text()

imports = '''
try:
    from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
except Exception:
    attach_regen_ranking_owner_source_repair = None
'''

if "attach_regen_ranking_owner_source_repair" not in controller_text:
    marker = "try:\n    from foundation_verification_harness import run_foundation_verification_harness"
    controller_text = controller_text.replace(marker, imports + "\n" + marker)

controller_kwarg = '''
            attach_regen_ranking_owner_source_repair=attach_regen_ranking_owner_source_repair,
'''

if "attach_regen_ranking_owner_source_repair=attach_regen_ranking_owner_source_repair" not in controller_text:
    marker = "            attach_regen_ranking_input_feed_bridge=attach_regen_ranking_input_feed_bridge,"
    controller_text = controller_text.replace(marker, marker + "\n" + controller_kwarg)

pipeline_param = '''
        attach_regen_ranking_owner_source_repair=None,
'''

if "attach_regen_ranking_owner_source_repair=None" not in pipeline_text:
    marker = "        attach_regen_ranking_input_feed_bridge=None,"
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_param)

pipeline_plan = '''
        (
            "regen_ranking_owner_source_repair",
            attach_regen_ranking_owner_source_repair,
            (),
            {},
        ),
'''

if '"regen_ranking_owner_source_repair"' not in pipeline_text:
    marker = '''        (
            "regen_ranking_input_feed_bridge",
            attach_regen_ranking_input_feed_bridge,
            (),
            {},
        ),'''
    pipeline_text = pipeline_text.replace(marker, marker + "\n" + pipeline_plan)

controller.write_text(controller_text)
pipeline.write_text(pipeline_text)

print("Integrated Phase 16J.3E ranking owner source repair.")
