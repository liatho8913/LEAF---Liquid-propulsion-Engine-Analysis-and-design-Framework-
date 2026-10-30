import sys

from PySide6.QtWidgets import QApplication

from regen_geometry_output_window import RegenGeometryOutputWindow


def get_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_regen_geometry_output_window_instantiates_with_full_visual_recommendation_tab():
    get_app()

    results = {
        "phase_11a6_regen_geometry_output_architecture_owner_report": {
            "summary": {
                "discovered_constraint_count": 18,
                "recommendation_count": 1,
                "candidate_changed_count": 2,
            },
            "validation": {
                "grouped_results": {
                    "WARN": [
                        {
                            "validation_state": "WARN",
                            "constraint_id": "coolant_velocity",
                            "label": "Coolant velocity",
                            "value": 0.5,
                            "unit": "m/s",
                            "reason": "Coolant velocity is low.",
                        }
                    ],
                    "PASS": [],
                    "FAIL": [],
                    "NOT_AVAILABLE": [],
                }
            },
            "explanations": {
                "explanations": [
                    {
                        "constraint_id": "coolant_velocity",
                        "failure_mode": "COOLANT_VELOCITY_OUT_OF_GUIDANCE",
                        "engineering_meaning": (
                            "Coolant velocity may be too low for strong heat transfer."
                        ),
                    }
                ]
            },
            "recommendations": {
                "recommendations": [
                    {
                        "priority": "MEDIUM",
                        "recommendation_id": "correct_coolant_velocity",
                        "title": "Correct coolant velocity",
                        "source_state": "WARN",
                        "source_constraint": "coolant_velocity",
                        "target_variables": ["channel_width", "channel_height"],
                        "proposed_direction": "decrease total coolant flow area",
                        "expected_benefit": "Raises coolant velocity.",
                    }
                ]
            },
            "candidate": {
                "comparison_rows": [
                    {
                        "variable": "channel_width",
                        "before": 0.0015,
                        "after": 0.001275,
                        "delta": -0.000225,
                        "changed": True,
                    },
                    {
                        "variable": "channel_height",
                        "before": 0.002,
                        "after": 0.0017,
                        "delta": -0.0003,
                        "changed": True,
                    },
                ]
            },
        },
        "phase_11a6_regen_geometry_output_architecture_owner_text": (
            "Example regen geometry report."
        ),
        "phase_11a8_regen_geometry_candidate_acceptance_owner_ready": True,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_engineering_status": (
            "WARN_REGEN_GEOMETRY_CANDIDATE_READY_FOR_USER_ACCEPTANCE"
        ),
        "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch": {
            "coolant_channel_width": 0.001275,
            "coolant_channel_height": 0.0017,
            "number_of_coolant_channels": 60,
        },
        "phase_11a8_regen_geometry_candidate_acceptance_owner_record": {
            "acceptance_ready": True,
            "recommendation_count": 1,
            "changed_keys": ["channel_width", "channel_height", "channel_count"],
            "design_history_event_type": "REGEN_GEOMETRY_CANDIDATE_ACCEPTANCE",
            "design_history_summary": (
                "Candidate regen geometry is ready for explicit user acceptance."
            ),
        },
    }

    window = RegenGeometryOutputWindow(results=results)

    assert window.windowTitle() == "LEAF Regen Geometry Diagnostics"
    assert window.tabs.count() == 7

    tab_names = [
        window.tabs.tabText(index)
        for index in range(window.tabs.count())
    ]

    assert "Acceptance" in tab_names
    assert "Visual Recommendation" in tab_names

    visual_text = window.visual_recommendation_detail_text.toPlainText()

    assert "Coolant velocity is low" in visual_text
    assert "Correct coolant velocity" in visual_text
    assert "channel_width" in visual_text
    assert "coolant_channel_width" in window.acceptance_patch_text.toPlainText()

    window.close()


if __name__ == "__main__":
    test_regen_geometry_output_window_instantiates_with_full_visual_recommendation_tab()
    print("PASS_REGEN_GEOMETRY_FULL_VISUAL_RECOMMENDATION_INTEGRATION")