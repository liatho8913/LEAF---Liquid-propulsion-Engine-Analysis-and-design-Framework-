import sys
from PySide6.QtWidgets import QApplication

from regen_cross_section_viewer import RegenCrossSectionCanvas


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_regen_geometry_candidate_viewer_bridge_reads_11a5_candidate():
    get_app()

    results = {
        "throat_radius": 0.02,
        "nozzle_length": 0.1,
        "selected_length": 0.0,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "number_of_coolant_channels": 80,
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry": {
            "channel_count": 60,
            "channel_width": 0.0012,
            "channel_height": 0.0017,
            "rib_width": 0.0008,
            "fit_ratio": 0.82,
            "effective_rib_width": 0.0006,
        },
    }

    canvas = RegenCrossSectionCanvas(results)
    canvas.set_geometry_source("candidate")

    geometry = canvas.get_geometry("candidate")

    assert geometry["source"] == "candidate"
    assert geometry["channel_count"] == 60
    assert abs(geometry["channel_width"] - 0.0012) < 1.0e-12
    assert abs(geometry["channel_height"] - 0.0017) < 1.0e-12
    assert abs(geometry["requested_rib_width"] - 0.0008) < 1.0e-12

    canvas.close()


def test_regen_geometry_candidate_viewer_bridge_falls_back_to_manual_when_candidate_missing():
    get_app()

    results = {
        "throat_radius": 0.02,
        "nozzle_length": 0.1,
        "selected_length": 0.0,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "number_of_coolant_channels": 80,
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry": {},
    }

    canvas = RegenCrossSectionCanvas(results)
    canvas.set_geometry_source("candidate")

    geometry = canvas.get_geometry("candidate")

    assert geometry["source"] == "manual"
    assert geometry["channel_count"] == 80

    canvas.close()


if __name__ == "__main__":
    test_regen_geometry_candidate_viewer_bridge_reads_11a5_candidate()
    test_regen_geometry_candidate_viewer_bridge_falls_back_to_manual_when_candidate_missing()
    print("PASS_REGEN_GEOMETRY_CANDIDATE_VIEWER_BRIDGE")