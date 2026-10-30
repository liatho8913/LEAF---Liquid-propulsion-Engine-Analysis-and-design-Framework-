import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "leaf_qt"))

from foundation_layer_controller import FoundationLayerController

controller = FoundationLayerController(
    get_benchmark_case_callback=lambda: "Merlin_1D",
    get_startup_health_callback=lambda: {},
)

result = controller.run_foundation_verification()

print("\nFOUNDATION RESULT KEY AUDIT STATUS")
print(result.get("foundation_result_key_audit_status"))

print("\nUNREGISTERED COUNT")
print(result.get("foundation_result_key_audit_unregistered_count"))

print("\nUNREGISTERED KEYS")
keys = result.get("foundation_result_key_audit_unregistered_keys")
if keys is None:
    text = result.get("foundation_result_key_audit_text", "")
    print(text)
else:
    for key in keys:
        print(key)

print("\nVISIBILITY COUNTS")
print(result.get("foundation_result_key_audit_visibility_counts"))
