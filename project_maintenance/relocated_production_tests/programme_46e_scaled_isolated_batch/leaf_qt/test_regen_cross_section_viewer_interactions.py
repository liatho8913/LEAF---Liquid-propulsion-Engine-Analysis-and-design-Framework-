import sys

from PySide6.QtWidgets import QApplication

from regen_cross_section_viewer import RegenCrossSectionViewer


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_viewer_buttons_and_slider_change_live_canvas_state():
    get_app()

    results = {
        "nozzle_length": 0.1,
        "throat_radius": 0.02,
        "exit_radius": 0.04,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "number_of_coolant_channels": 80,
        "recommended_geometry_status": "PASS",
        "recommended_geometry_valid": 1,
        "recommended_channel_width": 0.0011,
        "recommended_channel_height": 0.0018,
        "recommended_rib_width": 0.0008,
        "recommended_channel_count": 64,
        "regen_axial_profile": [
            {"x": 0.0, "radius": 0.02},
            {"x": 0.05, "radius": 0.03},
            {"x": 0.1, "radius": 0.04},
        ],
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry": {
            "channel_count": 60,
            "channel_width": 0.0012,
            "channel_height": 0.0017,
            "rib_width": 0.0007,
            "fit_ratio": 1.1,
            "effective_rib_width": 0.0009,
        },
    }

    viewer = RegenCrossSectionViewer(results)

    viewer.set_geometry_source("manual")
    assert viewer.canvas.geometry_source == "manual"
    assert viewer.canvas.get_geometry()["source"] == "manual"

    viewer.set_geometry_source("recommended")
    assert viewer.canvas.geometry_source == "recommended"
    assert viewer.canvas.get_geometry()["source"] == "recommended"
    assert viewer.canvas.get_geometry()["channel_count"] == 64

    viewer.set_geometry_source("candidate")
    assert viewer.canvas.geometry_source == "candidate"
    assert viewer.canvas.get_geometry()["source"] == "candidate"
    assert viewer.canvas.get_geometry()["channel_count"] == 60

    viewer.on_station_slider_changed(500)
    selected = viewer.results.get("regen_viewer_selected_length")
    assert selected is not None
    assert 0.045 <= selected <= 0.055

    viewer.close()


if __name__ == "__main__":
    test_viewer_buttons_and_slider_change_live_canvas_state()
    print("PASS_REGEN_CROSS_SECTION_VIEWER_INTERACTIONS")