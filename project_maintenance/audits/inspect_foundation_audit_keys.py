import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))

from leaf_qt.calculation_bridge import calculate_with_full_bridge

results = calculate_with_full_bridge({
    "fuel_name": "RP-1",
    "oxidizer_name": "LOX",
    "chamber_pressure": 6.895e6,
    "mass_flow_rate": 1.15,
    "mixture_ratio": 1.875,
    "throat_area": 3.01e-4,
    "expansion_ratio": 9.12,
    "number_of_coolant_channels": 80,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.0020,
    "rib_width": 0.0010,
    "hot_gas_wall_thickness": 0.0010,
    "coolant_flow_fraction": 0.35,
})

for key in sorted(results):
    if "unregistered" in key.lower():
        print(key, "=", results.get(key))

print("\nPOST16F5 KEYS")
for key in sorted(results):
    if "coolant_property_resolution" in key or key == "recommended_geometry_status_previous":
        print(key, "=", results.get(key))
