from leaf_qt.status_presentation import status_severity
from leaf_qt.runtime.notification_centre import runtime_notification_centre
try:
    from regen_result_replacement_verification_phase_16p5a import (
        verify_result_replacement,
    )
except Exception:
    verify_result_replacement = None



try:
    from regen_accept_recommendation_owner_phase_16n6 import (
        attach_accept_recommendation_result_phase_16n6,
    )
except Exception:
    attach_accept_recommendation_result_phase_16n6 = None


try:
    from regen_cross_section_live_feed_validator_phase_16n4 import (
        RegenCrossSectionLiveFeedValidatorPhase16N4,
    )
except Exception:
    RegenCrossSectionLiveFeedValidatorPhase16N4 = None

import math
import os
import json

try:
    from leaf_qt.status_presentation import (
        LegacyCompatibilityProducer,
    )
except Exception:
    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value):
            return "PASS" if bool(value) else "FAIL"

def _leaf_16u38_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "INVALID" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "MARGINAL" in text or "PARTIAL" in text or "MISSING" in text:
            return "WARN"
        if "PASS" in text or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u38_marker_from_bool(value, false_marker="FAIL"):
    try:
        if bool(value):
            return LegacyCompatibilityProducer.marker_from_bool(True)
        return false_marker
    except Exception:
        return "PASS" if bool(value) else false_marker


def _leaf_16u38_is_fail_like(value):
    return _leaf_16u38_status_severity(value) == "FAIL"


def _leaf_16u38_is_pass_like(value):
    return _leaf_16u38_status_severity(value) == "PASS"





try:
    from reference_engine_database import (
        get_reference_engine_names,
        get_reference_engine,
        get_reference_engine_input_overrides,
        build_reference_engine_input_summary,
        build_reference_engine_source_template,
        validate_reference_engine_source_record,
        parse_reference_engine_template_text,
        validate_reference_engine_record_data,
        build_reference_engine_database_patch,
        evaluate_reference_engine_readiness,
        evaluate_reference_engine_database_record,
        evaluate_reference_source_ledger_coverage,
        evaluate_reference_data_quality,
        normalise_reference_engine_record,
        evaluate_reference_database_status_consistency,
        evaluate_reference_value_origin_coverage,
        build_reference_value_entry_checklist,
        get_reference_engine_candidate_values,
        audit_reference_engine_schema,
        audit_all_reference_engine_schemas,
        build_reference_schema_repair_patch,
        build_reference_database_self_test_report,
        evaluate_candidate_promotion_readiness,
        build_candidate_promotion_readiness_report,
        build_candidate_promotion_patch,
        build_candidate_promotion_apply_preview,
        evaluate_candidate_promotion_completeness_delta,
        build_candidate_promotion_completeness_delta_report,
        evaluate_reference_rebuild_readiness,
        build_reference_rebuild_readiness_report,
        build_reference_rebuild_input_export,
        build_reference_rebuild_input_apply_plan,
        build_reference_rebuild_session_record,
        build_reference_rebuild_session_report,
        build_reference_rebuild_run_record,
        build_reference_rebuild_run_record_report,
        build_reference_rebuild_result_export,
        evaluate_reference_geometry_comparison,
        build_reference_geometry_comparison_report,
        evaluate_reference_regen_geometry_comparison,
        build_reference_regen_geometry_comparison_report,
    )
except ImportError:
    get_reference_engine_names = None
    get_reference_engine = None
    build_reference_engine_source_template = None
    get_reference_engine_input_overrides = None
    build_reference_engine_input_summary = None
    validate_reference_engine_source_record = None
    parse_reference_engine_template_text = None
    validate_reference_engine_record_data = None
    build_reference_engine_database_patch = None
    evaluate_reference_engine_readiness = None
    evaluate_reference_engine_database_record = None
    evaluate_reference_source_ledger_coverage = None
    evaluate_reference_data_quality = None
    normalise_reference_engine_record = None
    evaluate_reference_database_status_consistency = None
    evaluate_reference_value_origin_coverage = None
    build_reference_value_entry_checklist = None
    get_reference_engine_candidate_values = None
    audit_reference_engine_schema = None
    audit_all_reference_engine_schemas = None
    build_reference_schema_repair_patch = None
    build_reference_database_self_test_report = None
    evaluate_candidate_promotion_readiness = None
    build_candidate_promotion_readiness_report = None
    build_candidate_promotion_patch = None
    build_candidate_promotion_apply_preview = None
    evaluate_candidate_promotion_completeness_delta = None
    build_candidate_promotion_completeness_delta_report = None
    evaluate_reference_rebuild_readiness = None
    build_reference_rebuild_readiness_report = None
    build_reference_rebuild_input_export = None
    build_reference_rebuild_input_apply_plan = None
    build_reference_rebuild_session_record = None
    build_reference_rebuild_session_report = None
    build_reference_rebuild_run_record = None
    build_reference_rebuild_run_record_report = None
    build_reference_rebuild_result_export = None
    evaluate_reference_geometry_comparison = None
    build_reference_geometry_comparison_report = None
    evaluate_reference_regen_geometry_comparison = None
    build_reference_regen_geometry_comparison_report = None
from PySide6.QtCore import Qt, QRectF, QPointF, QSignalBlocker, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QSizePolicy,
    QCheckBox,
    QPushButton,
    QSlider,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QScrollArea,
    QFrame,
    QComboBox,
    QSplitter,
    QTabWidget,
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QSplitterHandle,
    QApplication,
)

class InspectorSplitterHandle(QSplitterHandle):
    """
    Visible resize grip between the geometry viewport and right inspector.
    """








class InspectorSplitter(QSplitter):
    """
    QSplitter with a visible engineering/workspace-style resize grip.
    """

    def createHandle(self):
        return InspectorSplitterHandle(self.orientation(), self)

class InspectorButton(QPushButton):
    """
    Button that can shrink to the inspector width without forcing horizontal scroll.
    Full text remains available through tooltip.
    """

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setToolTip(text)
        self.setMinimumWidth(0)
        self.setMinimumHeight(30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def minimumSizeHint(self):
        return QSize(0, 30)

    def sizeHint(self):
        return QSize(120, 30)


class InspectorScrollArea(QScrollArea):
    """
    Vertical-only scroll area.
    Forces contained tab content to match viewport width so no horizontal scroll appears.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setFrameShape(QFrame.NoFrame)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        widget = self.widget()
        if widget is not None:
            viewport_width = max(0, self.viewport().width())
            widget.setMinimumWidth(viewport_width)
            widget.setMaximumWidth(viewport_width)

class RegenCrossSectionCanvas(QWidget):
    def __init__(self, results):
        super().__init__()
        self.results = results or {}

        self.show_dimensions = True
        self.show_legend = True
        self.show_station_inspector = False
        self.view_mode = "full"
        automatic_geometry = self.results.get("regen_geometry_commit_staged_geometry", {})

        if isinstance(automatic_geometry, dict) and automatic_geometry:
            self.geometry_source = "automatic"
        else:
            self.geometry_source = "manual"
        self.zoom_factor = 1.0
        self.scale_mode = "fit"
        self.overlay_mode = "geometry"
        self.station_profile_key = "regen_axial_profile"

        self.setMinimumSize(760, 600)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def value(self, key, default=None):
        try:
            value = self.results.get(key, default)
            if value is None:
                return default
            return float(value)
        except Exception:
            return default

    def value_any(self, keys, default=None):
        for key in keys:
            value = self.value(key, None)

            if value is not None:
                return value

        return default

    def text_any(self, keys, default="UNKNOWN"):
        for key in keys:
            value = self.results.get(key)

            if value not in (None, ""):
                return str(value)

        return default

    def text_value(self, key, default="UNKNOWN"):
        value = self.results.get(key, default)
        if value in (None, ""):
            return default
        return str(value)

    def format_engineering_value(self, value, unit="", precision=5):
        if value in (None, ""):
            return "N/A"

        try:
            value = float(value)
        except Exception:
            return str(value)

        if abs(value) >= 1.0e5 or (abs(value) < 1.0e-3 and value != 0.0):
            text = f"{value:.{precision}e}"
        else:
            text = f"{value:.{precision}g}"

        if unit:
            return f"{text} {unit}"

        return text

    def set_scale_mode(self, mode):
        if mode not in ("fit", "true"):
            mode = "fit"

        self.scale_mode = mode
        self.update()

    def set_overlay_mode(self, mode):
        if mode not in ("geometry", "gas", "thermal", "coolant", "validation"):
            mode = "geometry"

        self.overlay_mode = mode
        self.update()

    def set_station_profile_key(self, profile_key):
        available = self.available_station_profiles()

        if profile_key not in available:
            profile_key = "regen_axial_profile"

        self.station_profile_key = profile_key
        self.update()

    def available_station_profiles(self):
        options = {
            "rao_nozzle_profile": "Rao Bell Nozzle Geometry",
            "conical_nozzle_profile": "Conical Nozzle Geometry",
            "regen_axial_profile": "Base Regen Axial Profile",
            "variable_channel_geometry_profile": "Variable Channel Geometry",
            "variable_geometry_thermal_profile": "Variable Geometry Thermal",
            "velocity_limited_variable_geometry_profile": "Velocity-Limited Geometry",
            "coupled_split_strategy_profile": "Coupled Split Strategy",
            "explicit_coating_liner_profile": "Coating / Liner Profile",
        }

        available = {}

        for key, label in options.items():
            profile = self.results.get(key)

            if isinstance(profile, list) and profile:
                available[key] = label

        if not available:
            available["regen_axial_profile"] = "Base Regen Axial Profile"

        return available

    def active_station_profile(self):
        profile = self.results.get(self.station_profile_key)

        if isinstance(profile, list) and profile:
            return profile

        fallback = self.results.get("regen_axial_profile")

        if isinstance(fallback, list):
            return fallback

        return []

    def selected_station_fraction(self):
        selected_length = self.value_any(
            ["regen_viewer_selected_length", "selected_length"],
            0.0
        )

        station = self.selected_station()

        if station and station.get("x") is not None:
            try:
                profile = self.active_station_profile()
                max_x = max(
                    float(item.get("x"))
                    for item in profile
                    if isinstance(item, dict) and item.get("x") is not None
                )

                if max_x > 0:
                    return max(
                        0.0,
                        min(
                            1.0,
                            float(station.get("x")) / max_x
                        )
                    )
            except Exception:
                pass

        nozzle_length = self.value("nozzle_length", 0.0)

        if nozzle_length is None or nozzle_length <= 0:
            return 0.0

        return max(0.0, min(1.0, selected_length / nozzle_length))

    def selected_station(self):
        profile = self.active_station_profile()

        if not profile:
            return None

        selected_length = self.value_any(
            ["regen_viewer_selected_length", "selected_length"],
            0.0
        )

        try:
            selected_length = float(selected_length)
        except Exception:
            selected_length = 0.0

        stations_with_x = [
            station for station in profile
            if isinstance(station, dict) and station.get("x") is not None
        ]

        if stations_with_x:
            return min(
                stations_with_x,
                key=lambda station: abs(float(station.get("x") or 0.0) - selected_length)
            )

        index = int(round(self.selected_station_fraction() * (len(profile) - 1)))
        index = max(0, min(index, len(profile) - 1))

        station = profile[index]

        if isinstance(station, dict):
            return station

        return None

    def station_value(self, keys, default=None):
        station = self.selected_station()

        if station:
            for key in keys:
                value = station.get(key)

                if value not in (None, ""):
                    return value

        for key in keys:
            value = self.results.get(key)

            if value not in (None, ""):
                return value

        return default

    def station_status_text(self, geometry=None):
        station = self.selected_station()

        if station:
            for key in (
                    "variable_geometry_valid",
                    "safe_variable_geometry_valid",
                    "variable_thermal_pass",
                    "coupled_split_pass",
                    "explicit_coating_thermal_stress_pass",
            ):
                if key in station:
                    return str(station.get(key))

        if geometry is not None:
            valid = geometry.get("channel_geometry_valid")
        else:
            valid = self.value_any(
                ["recommended_geometry_valid", "channel_geometry_valid"],
                0.0
            )

        if valid == 1.0:
            return "VALID"

        return "INVALID"

    def validation_colour(self, status):
        status = str(status).upper()

        if status in ("1", "TRUE", "PASS", "VALID"):
            return QColor(45, 145, 85)

        if "PASS" in status and "FAIL" not in status:
            return QColor(45, 145, 85)

        if "WARN" in status or "MARGINAL" in status or "PARTIAL" in status or "PLAUSIBLE" in status:
            return QColor(210, 155, 45)

        if "FAIL" in status or "INVALID" in status or "BLOCKED" in status:
            return QColor(185, 65, 65)

        return QColor(120, 120, 120)

    def value_at_station(self, keys, default=None):
        station = self.selected_station()

        if station:
            for key in keys:
                value = station.get(key)

                if value in (None, ""):
                    continue

                try:
                    return float(value)
                except Exception:
                    return value

        profile = self.active_station_profile()
        selected_length = self.value_any(
            ["regen_viewer_selected_length", "selected_length"],
            0.0
        )

        max_x = None
        x_values = []

        for item in profile:
            if not isinstance(item, dict):
                continue

            try:
                x_values.append(float(item.get("x")))
            except Exception:
                continue

        if x_values:
            max_x = max(x_values)

        station_fraction = 0.0
        if max_x and max_x > 0:
            station_fraction = max(0.0, min(1.0, float(selected_length) / max_x))
        else:
            nozzle_length = self.value("nozzle_length", 0.0)
            if nozzle_length and nozzle_length > 0:
                station_fraction = max(0.0, min(1.0, float(selected_length) / nozzle_length))

        for key in keys:
            value = self.results.get(key)

            if isinstance(value, (list, tuple)) and len(value) > 0:
                index = int(round(station_fraction * (len(value) - 1)))
                index = max(0, min(index, len(value) - 1))

                try:
                    return float(value[index])
                except Exception:
                    continue

            try:
                if value not in (None, ""):
                    return float(value)
            except Exception:
                continue

        return default

    def thermal_colour(self, value, low, high):
        if value is None:
            return QColor(120, 120, 120)

        if high <= low:
            return QColor(120, 120, 120)

        t = max(0.0, min(1.0, (value - low) / (high - low)))

        red = int(80 + 175 * t)
        green = int(180 - 120 * t)
        blue = int(220 - 180 * t)

        return QColor(red, green, blue)

    def clamp01(self, value):
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def gradient_colour(self, value, low, high, cold=None, hot=None):
        if cold is None:
            cold = QColor(40, 130, 210)

        if hot is None:
            hot = QColor(210, 70, 45)

        try:
            value = float(value)
            low = float(low)
            high = float(high)
        except Exception:
            return QColor(120, 120, 120)

        if high <= low:
            return QColor(120, 120, 120)

        t = self.clamp01((value - low) / (high - low))

        r = int(cold.red() + (hot.red() - cold.red()) * t)
        g = int(cold.green() + (hot.green() - cold.green()) * t)
        b = int(cold.blue() + (hot.blue() - cold.blue()) * t)

        return QColor(r, g, b)

    def overlay_colours(self, g):
        c = self.palette()

        gas_colour = c["gas"]
        wall_colour = c["hot_wall"]
        coating_colour = c["coating"]
        channel_band_colour = c["channel_band"]
        channel_void_colour = c["coolant_void"]
        jacket_colour = c["outer_jacket"]

        if self.overlay_mode == "gas":
            mach = self.station_value(["mach"], None)
            static_temperature = self.station_value(["static_temperature"], None)

            if mach is not None:
                gas_colour = self.gradient_colour(
                    mach,
                    0.0,
                    5.0,
                    QColor(35, 80, 150),
                    QColor(230, 190, 60)
                )
            elif static_temperature is not None:
                gas_colour = self.gradient_colour(
                    static_temperature,
                    300.0,
                    3500.0,
                    QColor(35, 80, 150),
                    QColor(230, 120, 55)
                )

        elif self.overlay_mode == "thermal":
            twg = self.station_value(
                [
                    "hot_gas_side_wall_temperature",
                    "variable_thermal_hot_wall_temperature",
                    "coupled_split_hot_wall_temperature",
                    "explicit_coating_liner_liner_temperature",
                ],
                None
            )

            twc = self.station_value(["coolant_side_wall_temperature"], None)

            if twg is not None:
                wall_colour = self.gradient_colour(
                    twg,
                    300.0,
                    1800.0,
                    QColor(70, 120, 210),
                    QColor(230, 65, 45)
                )

            if twc is not None:
                channel_band_colour = self.gradient_colour(
                    twc,
                    100.0,
                    900.0,
                    QColor(35, 135, 220),
                    QColor(220, 130, 45)
                )

        elif self.overlay_mode == "coolant":
            coolant_temperature = self.station_value(
                [
                    "coolant_temperature_mean",
                    "coolant_temperature_out",
                    "coolant_temperature",
                    "coupled_split_coolant_out_temperature",
                ],
                None
            )

            reynolds = self.station_value(
                [
                    "coolant_reynolds_number",
                    "variable_reynolds_number",
                    "safe_variable_reynolds_number",
                ],
                None
            )

            if coolant_temperature is not None:
                channel_void_colour = self.gradient_colour(
                    coolant_temperature,
                    90.0,
                    900.0,
                    QColor(20, 155, 215),
                    QColor(230, 150, 45)
                )

            if reynolds is not None:
                try:
                    reynolds = float(reynolds)
                    if reynolds < 2300:
                        channel_band_colour = QColor(185, 65, 65)
                    elif reynolds < 4000:
                        channel_band_colour = QColor(210, 155, 45)
                    else:
                        channel_band_colour = QColor(45, 145, 85)
                except Exception:
                    pass

        elif self.overlay_mode == "validation":
            status = self.station_status_text(g)
            status_colour = self.validation_colour(status)

            jacket_colour = status_colour
            channel_band_colour = status_colour

        return {
            "gas": gas_colour,
            "wall": wall_colour,
            "coating": coating_colour,
            "channel_band": channel_band_colour,
            "channel_void": channel_void_colour,
            "jacket": jacket_colour,
        }

    def palette(self):
        return {
            "background": QColor(43, 43, 43),
            "gas": QColor(18, 18, 18),
            "coating": QColor(235, 220, 90),
            "hot_wall": QColor(165, 70, 70),
            "channel_band": QColor(190, 125, 35),
            "coolant_void": QColor(20, 155, 215),
            "outer_jacket": QColor(95, 95, 95),
            "text": QColor(235, 235, 235),
        }

    def visible_layer_px(self, physical_thickness, scale, minimum_px=3.0):
        if physical_thickness is None or physical_thickness <= 0:
            return 0.0

        return max(physical_thickness * scale, minimum_px)

    def set_show_dimensions(self, enabled):
        self.show_dimensions = bool(enabled)
        self.update()

    def set_show_legend(self, enabled):
        self.show_legend = bool(enabled)
        self.update()

    def set_view_mode(self, mode):
        self.view_mode = mode
        self.update()

    def set_geometry_source(self, source):
        """
        Canvas-owned geometry source switch.

        The viewer owns buttons and signals.
        The canvas owns the actual geometry source used for drawing.
        """
        if source not in ("manual", "automatic"):
            source = "manual"

        self.geometry_source = source

        self.results["viewer_geometry_source"] = source

        self.update()
        self.repaint()

    def set_zoom_percent(self, percent):
        self.zoom_factor = max(0.4, min(3.0, percent / 100.0))
        self.update()

    def get_phase_11a_candidate_geometry(self):
        """
        Return the best candidate geometry dictionary available from Phase 11A.
        This is intentionally tolerant because candidate data has existed under
        several owner/output keys during 11A development.
        """
        candidate_keys = [
            "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry",
            "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch",
            "accepted_regen_geometry_candidate",
            "regen_geometry_candidate",
            "candidate_regen_geometry",
            "recommended_geometry_candidate",
            "phase_11a_candidate_geometry",
            "regen_geometry_recommended_candidate",
        ]

        for key in candidate_keys:
            candidate = self.results.get(key)
            if isinstance(candidate, dict) and candidate:
                return candidate

        geometry_markers = {
            "channel_width",
            "coolant_channel_width",
            "channel_height",
            "coolant_channel_height",
            "channel_count",
            "number_of_coolant_channels",
            "rib_width",
            "requested_rib_width",
        }

        for key, value in self.results.items():
            if not isinstance(value, dict) or not value:
                continue
            key_text = str(key).lower()
            if "candidate" not in key_text and "recommend" not in key_text:
                continue
            if geometry_markers.intersection(value.keys()):
                return value

        return {}

    def automatic_geometry_display_state(self):
        """Return the explicit automatic-geometry presentation state."""

        mode = str(
            self.results.get(
                "regen_design_mode"
            )
            or
            "manual"
        ).strip()

        state = str(
            self.results.get(
                "regen_design_mode_generation_state"
            )
            or
            "NOT_GENERATED"
        ).strip().upper()

        selected_material = str(
            self.results.get(
                "selected_material"
            )
            or
            "not specified"
        )

        if (
            mode
            ==
            "automatic_selected_material"
        ):
            mode_label = (
                "Automatic — Selected Material"
                f" ({selected_material})"
            )

        elif (
            mode
            ==
            "automatic_geometry_materials"
        ):
            mode_label = (
                "Automatic — Geometry + Materials"
            )

        else:
            mode_label = "Manual"

        if state == "RUNNING":
            message = (
                "Generating automatic design…"
            )

        elif state == "NO_FEASIBLE_DESIGN":
            message = (
                "No geometry could be generated"
            )

        elif state == "ERROR":
            message = (
                "Automatic geometry generation failed"
            )

        elif state == "GENERATED":
            message = (
                "Generated automatic geometry unavailable"
            )

        else:
            state = "NOT_GENERATED"

            message = (
                "Automatic geometry not generated — press Generate"
            )

        return {
            "mode":
                mode,

            "mode_label":
                mode_label,

            "generation_state":
                state,

            "message":
                message,
        }


    def automatic_geometry_payload_for_display(self):
        """Return only geometry genuinely generated for the active mode."""

        display = (
            self.automatic_geometry_display_state()
        )

        if (
            display.get(
                "generation_state"
            )
            !=
            "GENERATED"
        ):
            return {}

        mode = display.get(
            "mode"
        )

        if (
            mode
            ==
            "automatic_geometry_materials"
        ):
            geometry = (
                self.results.get(
                    "regen_geometry_material_display_geometry"
                )
                or
                {}
            )

            return (
                dict(
                    geometry
                )
                if isinstance(
                    geometry,
                    dict,
                )
                else
                {}
            )

        if (
            mode
            ==
            "automatic_selected_material"
        ):
            geometry = (
                self.results.get(
                    "regen_ui_applied_geometry"
                )
                or
                self.results.get(
                    "regen_viewer_accepted_geometry"
                )
                or
                self.results.get(
                    "regen_geometry_commit_staged_geometry"
                )
                or
                (
                    self.results.get(
                        "regen_autonomous_geometry_staged_candidate"
                    )
                    or
                    {}
                ).get(
                    "staged_geometry",
                    {},
                )
                or
                {}
            )

            return (
                dict(
                    geometry
                )
                if isinstance(
                    geometry,
                    dict,
                )
                else
                {}
            )

        return {}


    def get_geometry(self, source=None):
        if source is None:
            source = self.geometry_source

        if source not in ("manual", "automatic"):
            source = "manual"

        selected_length = self.value_any(
            ["regen_viewer_selected_length", "selected_length"],
            0.0
        )

        nozzle_length = self.value_any([
            "nozzle_length",
            "rao_nozzle_length",
            "conical_nozzle_length",
            "regen_nozzle_length",
            "selected_nozzle_length",
            "engine_nozzle_length",
        ], None)

        throat_radius = self.value_any([
            "throat_radius",
            "nozzle_throat_radius",
        ], None)

        exit_radius = self.value_any([
            "exit_radius",
            "nozzle_exit_radius",
            "rao_exit_radius",
            "conical_exit_radius",
        ], None)

        throat_area = self.value_any([
            "throat_area",
            "At",
            "nozzle_throat_area",
        ], None)

        exit_area = self.value_any([
            "exit_area",
            "Ae",
            "nozzle_exit_area",
        ], None)

        expansion_ratio = self.value_any([
            "expansion_ratio",
            "area_ratio",
            "epsilon",
        ], None)

        if throat_radius is None and throat_area is not None and throat_area > 0:
            throat_radius = math.sqrt(throat_area / math.pi)

        if exit_radius is None and exit_area is not None and exit_area > 0:
            exit_radius = math.sqrt(exit_area / math.pi)

        if (
                exit_radius is None
                and throat_radius is not None
                and expansion_ratio is not None
                and throat_radius > 0
                and expansion_ratio > 1
        ):
            exit_radius = throat_radius * math.sqrt(expansion_ratio)

        def first_float(keys, default=None):
            for key in keys:
                value = self.results.get(key)
                if value in (None, ""):
                    continue
                try:
                    return float(value)
                except Exception:
                    continue
            return default

        def first_int(keys, default=0):
            value = first_float(keys, None)
            if value is None:
                return default
            try:
                return int(round(value))
            except Exception:
                return default

        def dict_float(data, keys, default=None):
            if not isinstance(data, dict):
                return default

            for key in keys:
                value = data.get(key)
                if value in (None, ""):
                    continue
                try:
                    return float(value)
                except Exception:
                    continue

            return default

        def dict_int(data, keys, default=0):
            value = dict_float(data, keys, None)
            if value is None:
                return default
            try:
                return int(round(value))
            except Exception:
                return default

        def radius_from_profile(profile_key):
            profile = self.results.get(profile_key)

            if not isinstance(profile, list) or not profile:
                return None

            stations = []

            for station in profile:
                if not isinstance(station, dict):
                    continue

                try:
                    x = float(
                        station.get("x")
                        if station.get("x") is not None
                        else station.get("station_x")
                    )
                except Exception:
                    continue

                radius = None

                for key in (
                        "radius",
                        "gas_radius",
                        "local_radius",
                        "inner_radius",
                        "hot_gas_radius",
                ):
                    try:
                        value = station.get(key)
                        if value not in (None, "") and float(value) > 0:
                            radius = float(value)
                            break
                    except Exception:
                        pass

                if radius is None:
                    try:
                        area = station.get("area")
                        if area not in (None, "") and float(area) > 0:
                            radius = math.sqrt(float(area) / math.pi)
                    except Exception:
                        pass

                if radius is not None and radius > 0:
                    stations.append((x, radius))

            if not stations:
                return None

            stations.sort(key=lambda item: item[0])

            try:
                selected_x = float(selected_length or 0.0)
            except Exception:
                selected_x = 0.0

            if selected_x <= stations[0][0]:
                return stations[0][1]

            if selected_x >= stations[-1][0]:
                return stations[-1][1]

            for i in range(len(stations) - 1):
                x0, r0 = stations[i]
                x1, r1 = stations[i + 1]

                if x0 <= selected_x <= x1:
                    if x1 == x0:
                        return r0

                    t = (selected_x - x0) / (x1 - x0)
                    return r0 + (r1 - r0) * t

            return stations[-1][1]

        # Station geometry must follow the currently selected station profile first.
        # Previously the viewer preferred Rao/conical profiles before the active
        # profile, which allowed X to move while Rgas stayed effectively constant.
        active_model = str(
            self.results.get("nozzle_geometry_model")
            or "RAO_BELL_APPROXIMATION"
        ).upper()

        radius_profile_order = []

        if self.station_profile_key:
            radius_profile_order.append(self.station_profile_key)

        radius_profile_order.extend([
            "variable_channel_geometry_profile",
            "variable_geometry_thermal_profile",
            "regen_axial_profile",
        ])

        if active_model == "CONICAL":
            radius_profile_order.extend([
                "conical_nozzle_profile",
                "rao_nozzle_profile",
            ])
        else:
            radius_profile_order.extend([
                "rao_nozzle_profile",
                "conical_nozzle_profile",
            ])

        # De-duplicate while preserving order.
        _seen_profiles = set()
        radius_profile_order = [
            key for key in radius_profile_order
            if key and not (key in _seen_profiles or _seen_profiles.add(key))
        ]

        def profile_radius_span(profile_key):
            profile = self.results.get(profile_key)

            if not isinstance(profile, list):
                return None

            radii = []

            for station in profile:
                if not isinstance(station, dict):
                    continue

                for key in (
                        "radius",
                        "gas_radius",
                        "local_radius",
                        "inner_radius",
                        "hot_gas_radius",
                ):
                    try:
                        value = station.get(key)
                        if value not in (None, "") and float(value) > 0:
                            radii.append(float(value))
                            break
                    except Exception:
                        pass

                try:
                    area = station.get("area")
                    if area not in (None, "") and float(area) > 0:
                        radii.append(math.sqrt(float(area) / math.pi))
                except Exception:
                    pass

            if not radii:
                return None

            return min(radii), max(radii)

        def effective_station_length_from_profiles():
            x_candidates = []

            for profile_key in (
                    "rao_nozzle_profile",
                    "conical_nozzle_profile",
                    "regen_axial_profile",
                    "variable_channel_geometry_profile",
                    "variable_geometry_thermal_profile",
                    "velocity_limited_variable_geometry_profile",
                    "coupled_split_strategy_profile",
                    "explicit_coating_liner_profile",
            ):
                profile = self.results.get(profile_key)

                if not isinstance(profile, list):
                    continue

                for station in profile:
                    if not isinstance(station, dict):
                        continue

                    for x_key in ("x", "station_x", "axial_position", "selected_length"):
                        try:
                            x_value = station.get(x_key)
                            if x_value not in (None, "") and float(x_value) > 0:
                                x_candidates.append(float(x_value))
                        except Exception:
                            pass

            if x_candidates:
                return max(x_candidates)

            return None

        def derive_radius_bounds_from_available_data():
            radius_candidates = []

            for value in (throat_radius, exit_radius):
                try:
                    if value is not None and float(value) > 0:
                        radius_candidates.append(float(value))
                except Exception:
                    pass

            for area_value in (throat_area, exit_area):
                try:
                    if area_value is not None and float(area_value) > 0:
                        radius_candidates.append(math.sqrt(float(area_value) / math.pi))
                except Exception:
                    pass

            for profile_key in (
                    "rao_nozzle_profile",
                    "conical_nozzle_profile",
                    "regen_axial_profile",
                    "variable_channel_geometry_profile",
                    "variable_geometry_thermal_profile",
            ):
                span = profile_radius_span(profile_key)
                if span is not None:
                    radius_candidates.extend(span)

            if not radius_candidates:
                base_radius = self.value_any(
                    ["throat_radius", "nozzle_throat_radius"],
                    0.01
                )
                return base_radius, base_radius * 2.25

            r_min = min(radius_candidates)
            r_max = max(radius_candidates)

            if r_min <= 0:
                r_min = 0.01

            # If all available data is effectively constant, create a visible viewer
            # envelope rather than letting the slider appear dead.
            if r_max <= r_min or abs(r_max - r_min) / max(r_max, 1.0e-9) < 0.05:
                r_max = r_min * 2.25

            return r_min, r_max

        gas_radius = None
        profile_radius_source = "none"

        # 1) Prefer a real varying station profile.
        for profile_key in radius_profile_order:
            span = profile_radius_span(profile_key)

            if span is None:
                continue

            r_min, r_max = span

            if r_max <= 0:
                continue

            # Ignore effectively constant profiles.
            if abs(r_max - r_min) / r_max < 0.02:
                continue

            candidate_radius = radius_from_profile(profile_key)

            if candidate_radius is not None:
                gas_radius = candidate_radius
                profile_radius_source = profile_key
                break

        # 2) If no real varying profile exists, derive a viewer-side throat-to-exit curve.
        if gas_radius is None:
            effective_length = nozzle_length

            if effective_length is None or effective_length <= 0:
                effective_length = effective_station_length_from_profiles()

            if effective_length is None or effective_length <= 0:
                effective_length = 1.0

            r_start, r_end = derive_radius_bounds_from_available_data()

            try:
                t = float(selected_length or 0.0) / float(effective_length)
            except Exception:
                t = 0.0

            t = max(0.0, min(1.0, t))

            # Bell-like viewer curve. This is intentionally visible so the station
            # slider cannot appear dead when solver profiles are missing/constant.
            gas_radius = r_start + (r_end - r_start) * (t ** 0.72)
            profile_radius_source = "viewer_derived_station_curve"

        manual = {
            "channel_width": first_float(["coolant_channel_width", "channel_width"], 0.0015),
            "channel_height": first_float(["coolant_channel_height", "channel_height"], 0.0020),
            "requested_rib_width": first_float(["rib_width", "requested_rib_width"], 0.0010),
            "channel_count": first_int(["number_of_coolant_channels", "channel_count"], 80),
            "wall": first_float(["hot_gas_wall_thickness", "wall_thickness"], 0.0010),
            "jacket": first_float(["outer_jacket_thickness", "jacket_thickness"], 0.0020),
            "data_origin": "manual_inputs",
        }

        automatic_data = (
            self.automatic_geometry_payload_for_display()
        )

        if not isinstance(
            automatic_data,
            dict,
        ):
            automatic_data = {}

        automatic = {
            "channel_width":
                dict_float(
                    automatic_data,
                    [
                        "coolant_channel_width",
                        "channel_width",
                    ],
                    None,
                ),

            "channel_height":
                dict_float(
                    automatic_data,
                    [
                        "coolant_channel_height",
                        "channel_height",
                    ],
                    None,
                ),

            "requested_rib_width":
                dict_float(
                    automatic_data,
                    [
                        "rib_width",
                        "requested_rib_width",
                    ],
                    None,
                ),

            "channel_count":
                dict_int(
                    automatic_data,
                    [
                        "channel_count",
                        "number_of_channels",
                        "number_of_coolant_channels",
                    ],
                    0,
                ),

            "wall":
                dict_float(
                    automatic_data,
                    [
                        "hot_gas_wall_thickness",
                        "inner_wall_thickness",
                        "wall_thickness",
                    ],
                    None,
                ),

            "jacket":
                dict_float(
                    automatic_data,
                    [
                        "outer_jacket_thickness",
                        "jacket_thickness",
                    ],
                    0.0,
                ),

            "data_origin":
                "generated_automatic_geometry",
        }

        automatic_complete = bool(
            isinstance(
                automatic_data,
                dict,
            )
            and
            automatic_data
            and
            automatic.get(
                "channel_width"
            )
            is not None
            and
            automatic.get(
                "channel_width"
            )
            >
            0.0
            and
            automatic.get(
                "channel_height"
            )
            is not None
            and
            automatic.get(
                "channel_height"
            )
            >
            0.0
            and
            automatic.get(
                "requested_rib_width"
            )
            is not None
            and
            automatic.get(
                "requested_rib_width"
            )
            >=
            0.0
            and
            automatic.get(
                "channel_count",
                0,
            )
            >
            0
            and
            automatic.get(
                "wall"
            )
            is not None
            and
            automatic.get(
                "wall"
            )
            >
            0.0
        )

        if (
            source
            ==
            "automatic"
            and
            not automatic_complete
        ):
            display = (
                self.automatic_geometry_display_state()
            )

            self.results[
                "regen_viewer_requested_geometry_source"
            ] = "automatic"

            self.results[
                "regen_viewer_actual_geometry_source"
            ] = (
                "automatic_unavailable"
            )

            self.results[
                "regen_viewer_automatic_geometry_display_state"
            ] = display.get(
                "generation_state"
            )

            return {
                "source":
                    "automatic_unavailable",

                "requested_source":
                    "automatic",

                "geometry_available":
                    False,

                "data_origin":
                    "automatic_geometry_unavailable",

                "empty_state_message":
                    display.get(
                        "message"
                    ),

                "empty_state_mode_label":
                    display.get(
                        "mode_label"
                    ),

                "generation_state":
                    display.get(
                        "generation_state"
                    ),

                "selected_length":
                    selected_length,

                "profile_radius_source":
                    profile_radius_source,

                "gas_radius":
                    gas_radius,

                "wall":
                    0.0,

                "channel_height":
                    0.0,

                "jacket":
                    0.0,

                "coating":
                    0.0,

                "thermal_barrier_coating":
                    0.0,

                "bond_coat":
                    0.0,

                "liner":
                    0.0,

                "channel_width":
                    0.0,

                "requested_rib_width":
                    0.0,

                "effective_rib_width":
                    None,

                "channel_count":
                    0,

                "channel_fit_ratio":
                    None,

                "available_pitch":
                    None,

                "requested_pitch":
                    None,

                "channel_geometry_valid":
                    0.0,

                "cooling_coverage":
                    None,

                "channel_topology_status":
                    "NOT_AVAILABLE",

                "channel_topology_severity":
                    "UNKNOWN",

                "channel_topology_reason":
                    display.get(
                        "message"
                    ),

                "channel_topology_transition_count":
                    0,

                "channel_topology_counts":
                    [],
            }

        if source == "automatic":
            selected = automatic
            actual_source = "automatic"

        else:
            selected = manual
            actual_source = "manual"

        thermal_barrier_coating = first_float(
            [
                "thermal_barrier_coating_thickness",
                "tbc_thickness",
                "coating_thickness",
                "explicit_coating_liner_thickness",
            ],
            0.0
        )

        bond_coat = first_float(
            [
                "bond_coat_thickness",
                "bondcoat_thickness",
                "explicit_bond_coat_thickness",
            ],
            0.0
        )

        liner = first_float(
            [
                "liner_thickness",
                "inner_liner_thickness",
                "explicit_liner_thickness",
            ],
            0.0
        )

        coating = thermal_barrier_coating + bond_coat + liner

        channel_width = float(selected["channel_width"])
        channel_height = float(selected["channel_height"])
        requested_rib_width = float(selected["requested_rib_width"])
        channel_count = int(selected["channel_count"])
        wall = float(selected["wall"])
        jacket = float(selected["jacket"])

        channel_mid_radius = gas_radius + coating + wall + 0.5 * channel_height

        available_pitch = None
        if channel_count > 0 and channel_mid_radius > 0:
            available_pitch = 2.0 * math.pi * channel_mid_radius / channel_count

        requested_pitch = channel_width + requested_rib_width

        effective_rib_width = None
        if available_pitch is not None:
            effective_rib_width = available_pitch - channel_width

        channel_fit_ratio = None
        if available_pitch is not None and requested_pitch > 0:
            channel_fit_ratio = available_pitch / requested_pitch

        channel_geometry_valid = 1.0 if (
                effective_rib_width is not None
                and effective_rib_width >= 0.0
                and channel_fit_ratio is not None
                and channel_fit_ratio >= 0.999
        ) else 0.0

        cooling_coverage = None
        if channel_mid_radius > 0:
            cooling_coverage = (channel_width * channel_count) / (2.0 * math.pi * channel_mid_radius)

        self.results["regen_viewer_requested_geometry_source"] = source
        self.results["regen_viewer_actual_geometry_source"] = actual_source
        self.results["regen_viewer_data_origin"] = selected.get("data_origin")

        topology = self.evaluate_channel_topology_status()

        self.results["regen_viewer_debug_channel_count"] = channel_count
        self.results["regen_viewer_debug_channel_width"] = channel_width
        self.results["regen_viewer_debug_channel_height"] = channel_height
        self.results["regen_viewer_debug_gas_radius"] = gas_radius
        self.results["regen_viewer_debug_selected_length"] = selected_length
        self.results["regen_viewer_debug_profile_radius_source"] = profile_radius_source
        self.results["regen_viewer_debug_topology_status"] = topology.get("status")
        self.results["regen_viewer_debug_topology_transitions"] = topology.get("transition_count")

        return {
            "source": actual_source,
            "geometry_available": True,
            "requested_source": source,
            "data_origin": selected.get("data_origin"),
            "channel_topology_status": topology.get("status"),
            "channel_topology_severity": topology.get("severity"),
            "channel_topology_reason": topology.get("reason"),
            "channel_topology_transition_count": topology.get("transition_count"),
            "channel_topology_counts": topology.get("channel_counts"),
            "selected_length": selected_length,
            "profile_radius_source": profile_radius_source,
            "gas_radius": gas_radius,
            "wall": wall,
            "channel_height": channel_height,
            "jacket": jacket,
            "coating": coating,
            "thermal_barrier_coating": thermal_barrier_coating,
            "bond_coat": bond_coat,
            "liner": liner,
            "channel_width": channel_width,
            "requested_rib_width": requested_rib_width,
            "effective_rib_width": effective_rib_width,
            "channel_count": channel_count,
            "channel_fit_ratio": channel_fit_ratio,
            "available_pitch": available_pitch,
            "requested_pitch": requested_pitch,
            "channel_geometry_valid": channel_geometry_valid,
            "cooling_coverage": cooling_coverage,
        }

    def annular_sector_polygon(self, cx, cy, r_inner, r_outer, angle_1, angle_2, steps=6):
        points = []

        for i in range(steps + 1):
            t = angle_1 + (angle_2 - angle_1) * i / steps
            points.append(QPointF(cx + math.cos(t) * r_outer, cy + math.sin(t) * r_outer))

        for i in range(steps, -1, -1):
            t = angle_1 + (angle_2 - angle_1) * i / steps
            points.append(QPointF(cx + math.cos(t) * r_inner, cy + math.sin(t) * r_inner))

        return QPolygonF(points)

    def draw_annular_layer(self, painter, cx, cy, outer_r, inner_r, colour, cutout_colour):
        painter.setPen(QPen(QColor(5, 5, 5), 2))
        painter.setBrush(QBrush(colour))
        painter.drawEllipse(QRectF(cx - outer_r, cy - outer_r, 2 * outer_r, 2 * outer_r))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(cutout_colour))
        painter.drawEllipse(QRectF(cx - inner_r, cy - inner_r, 2 * inner_r, 2 * inner_r))

    def draw_dimension_line(self, painter, x1, y1, x2, y2, text):
        painter.setPen(QPen(QColor(235, 235, 235), 1))
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.drawText(int((x1 + x2) / 2) + 6, int((y1 + y2) / 2) - 4, text)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.fillRect(
            self.rect(),
            QColor(
                43,
                43,
                43,
            ),
        )

        geometry = (
            self.get_geometry()
        )

        if (
            self.geometry_source
            ==
            "automatic"
            and
            geometry.get(
                "geometry_available"
            )
            is False
        ):
            painter.setPen(
                QPen(
                    QColor(
                        235,
                        235,
                        235,
                    ),
                    1,
                )
            )

            mode_label = str(
                geometry.get(
                    "empty_state_mode_label"
                )
                or
                "Automatic"
            )

            message = str(
                geometry.get(
                    "empty_state_message"
                )
                or
                "Automatic geometry unavailable"
            )

            generation_state = str(
                geometry.get(
                    "generation_state"
                )
                or
                ""
            ).upper()

            guidance_lines = (
                self.results.get(
                    "regen_viewer_canonical_failure_guidance_lines"
                )
                or
                []
            )

            if not isinstance(
                guidance_lines,
                list,
            ):
                guidance_lines = []

            if (
                generation_state
                in
                {
                    "NO_FEASIBLE_DESIGN",
                    "ERROR",
                }
                and
                guidance_lines
            ):
                visible = [
                    str(line)
                    for line in guidance_lines[:18]
                ]

                remaining = (
                    len(guidance_lines)
                    -
                    len(visible)
                )

                if remaining > 0:
                    visible.append(
                        f"... +{remaining} additional "
                        "canonical guidance line(s)."
                    )

                text = (
                    f"{mode_label}\n"
                    f"{message}\n\n"
                    +
                    "\n".join(
                        visible
                    )
                )

                alignment = (
                    Qt.AlignLeft
                    |
                    Qt.AlignVCenter
                    |
                    Qt.TextWordWrap
                )

            else:
                text = (
                    f"{mode_label}\n\n"
                    f"{message}\n\n"
                    "Manual geometry remains preserved and can be "
                    "restored by selecting Manual."
                )

                alignment = (
                    Qt.AlignCenter
                    |
                    Qt.TextWordWrap
                )

            rect = (
                self.rect()
                .adjusted(
                    48,
                    40,
                    -48,
                    -40,
                )
            )

            painter.drawText(
                rect,
                alignment,
                text,
            )

            painter.end()
            return

        if self.view_mode == "detail":
            self.draw_detail_view(
                painter
            )

        else:
            self.draw_full_view(
                painter
            )



    def draw_full_geometry_in_rect(
            self,
            painter,
            rect,
            g,
            title,
    ):
        cx = rect.center().x()
        cy = rect.center().y() + 30
        c = self.palette()

        gas_radius = g["gas_radius"]
        wall = g["wall"]
        channel_height = g["channel_height"]
        jacket = g["jacket"]
        coating = g["coating"]

        channel_width = g["channel_width"]
        channel_count = g["channel_count"]

        wall_inner = gas_radius + coating
        wall_outer = wall_inner + wall
        channel_inner = wall_outer
        channel_outer = channel_inner + channel_height
        jacket_inner = channel_outer
        jacket_outer = jacket_inner + jacket

        outer_radius = jacket_outer

        if outer_radius <= 0:
            return

        scale = min(rect.width() * 0.84, rect.height() * 0.74) / (2.0 * outer_radius)
        scale *= self.zoom_factor

        gas_px = gas_radius * scale

        coating_px = self.visible_layer_px(coating, scale, minimum_px=3.0)
        wall_inner_px = gas_px + coating_px
        wall_outer_px = wall_inner_px + max(wall * scale, 3.0)
        channel_inner_px = wall_outer_px
        channel_outer_px = channel_inner_px + max(channel_height * scale, 8.0)
        jacket_inner_px = channel_outer_px
        jacket_outer_px = jacket_inner_px + max(jacket * scale, 8.0)

        background = c["background"]

        overlay = self.overlay_colours(g)

        jacket_colour = overlay["jacket"]
        rib_colour = overlay["channel_band"]
        wall_colour = overlay["wall"]
        coating_colour = overlay["coating"]
        channel_colour = overlay["channel_void"]
        gas_colour = overlay["gas"]

        status = "PASS" if g.get("channel_geometry_valid") == 1.0 else "FAIL"

        painter.setPen(QPen(c["text"], 1))
        painter.drawText(
            int(rect.left() + 12),
            int(rect.top() + 22),
            f"{title} — Geometry {status}"
        )

        self.draw_annular_layer(painter, cx, cy, jacket_outer_px, jacket_inner_px, jacket_colour, background)
        self.draw_annular_layer(painter, cx, cy, channel_outer_px, channel_inner_px, rib_colour, background)
        self.draw_annular_layer(painter, cx, cy, wall_outer_px, wall_inner_px, wall_colour, background)
        if coating > 0:
            self.draw_annular_layer(painter, cx, cy, wall_inner_px, gas_px, coating_colour, background)

        painter.setBrush(QBrush(gas_colour))
        painter.setPen(QPen(QColor(10, 10, 10), 2))
        painter.drawEllipse(QRectF(cx - gas_px, cy - gas_px, 2 * gas_px, 2 * gas_px))

        if channel_count > 0 and channel_width > 0:
            channel_mid_radius = channel_inner + 0.5 * channel_height
            channel_angle_width = channel_width / channel_mid_radius
            max_angle_width = (2.0 * math.pi / channel_count) * 0.95
            channel_angle_width = min(channel_angle_width, max_angle_width)

            painter.setPen(QPen(QColor(15, 15, 15), 1))
            painter.setBrush(QBrush(channel_colour))

            for i in range(channel_count):
                centre_angle = (2.0 * math.pi * i) / channel_count
                polygon = self.annular_sector_polygon(
                    cx,
                    cy,
                    channel_inner_px + 1.2,
                    channel_outer_px - 1.2,
                    centre_angle - 0.5 * channel_angle_width,
                    centre_angle + 0.5 * channel_angle_width,
                )
                painter.drawPolygon(polygon)

        coverage = g.get("cooling_coverage")

        coverage_text = "N/A"
        if coverage is not None:
            coverage_text = f"{coverage * 100.0:.1f}%"

        y = int(rect.bottom() - 92)

        painter.setPen(QPen(Qt.white, 1))
        painter.drawText(int(rect.left() + 12), y, f"Channels: {channel_count}")
        painter.drawText(int(rect.left() + 12), y + 20, f"Width: {channel_width:.6g} m")
        painter.drawText(int(rect.left() + 12), y + 40, f"Height: {channel_height:.6g} m")
        painter.drawText(int(rect.left() + 12), y + 60, f"Coverage: {coverage_text} | Geometry: {status}")

    def build_diagnostics_lines(self, g):
        lines = []

        profile = self.active_station_profile()
        station = self.selected_station()
        available_profiles = self.available_station_profiles()

        lines.append(f"Geometry source: {self.geometry_source}")
        acceptance_status = self.results.get(
            "regen_viewer_geometry_acceptance_status",
            "NO_ACTION",
        )

        acceptance_message = self.results.get(
            "regen_viewer_geometry_acceptance_message",
            "",
        )

        lines.append(f"Geometry acceptance status: {acceptance_status}")

        if acceptance_message:
            lines.append(f"Geometry acceptance message: {acceptance_message}")
        automatic_warning = self.results.get("regen_viewer_automatic_geometry_warning")

        if automatic_warning:
            lines.append(f"Automatic geometry warning: {automatic_warning}")
        lines.append(f"View mode: {self.view_mode}")
        lines.append(f"Overlay mode: {self.overlay_mode}")
        lines.append(f"Scale mode: {self.scale_mode}")
        lines.append(f"Active profile: {self.station_profile_key}")
        lines.append(
            f"Full-engine regen status: {self.results.get('full_engine_regen_geometry_status', 'N/A')}"
        )
        lines.append(
            f"Full-engine failed fit stations: {self.results.get('full_engine_regen_failed_fit_count', 'N/A')}"
        )
        lines.append(
            f"Full-engine failed thermal stations: {self.results.get('full_engine_regen_failed_thermal_count', 'N/A')}"
        )
        lines.append(
            f"Best full-engine regen status: {self.results.get('best_full_engine_regen_status', 'N/A')}"
        )
        lines.append(
            f"Best full-engine regen design: {self.results.get('best_full_engine_regen_design', 'N/A')}"
        )
        lines.append(
            f"Best full-engine thermal failures: {self.results.get('best_full_engine_regen_failed_thermal_count', 'N/A')}"
        )
        lines.append(
            f"Best full-engine reason: {self.results.get('best_full_engine_regen_reason', 'N/A')}"
        )
        full_engine_reasons = self.results.get("full_engine_regen_geometry_reasons")

        if isinstance(full_engine_reasons, list) and full_engine_reasons:
            lines.append(f"Full-engine reason: {full_engine_reasons[0]}")
        else:
            lines.append("Full-engine reason: N/A")
        lines.append(f"Available profiles: {len(available_profiles)}")
        lines.append(f"Station profile length: {len(profile) if profile else 0}")
        lines.append(f"Selected station found: {'YES' if station else 'NO'}")

        required_geometry = [
            ("gas radius", g.get("gas_radius")),
            ("wall thickness", g.get("wall")),
            ("channel width", g.get("channel_width")),
            ("channel height", g.get("channel_height")),
            ("rib width", g.get("effective_rib_width")),
            ("channel count", g.get("channel_count")),
            ("available pitch", g.get("available_pitch")),
        ]

        missing_geometry = [
            name for name, value in required_geometry
            if value in (None, "", 0)
        ]

        if missing_geometry:
            lines.append("Missing geometry: " + ", ".join(missing_geometry))
        else:
            lines.append("Missing geometry: none")

        if station:
            overlay_keys = {
                "geometry": ["radius", "area"],
                "gas": ["mach", "static_temperature", "static_pressure"],
                "thermal": ["hot_gas_side_wall_temperature", "coolant_side_wall_temperature", "regen_heat_flux"],
                "coolant": ["coolant_temperature_out", "coolant_velocity", "coolant_reynolds_number"],
                "validation": [
                    "variable_geometry_valid",
                    "safe_variable_geometry_valid",
                    "variable_thermal_pass",
                    "coupled_split_pass",
                    "explicit_coating_thermal_stress_pass",
                ],
            }

            keys = overlay_keys.get(self.overlay_mode, [])
            missing_overlay = [
                key for key in keys
                if station.get(key) in (None, "")
            ]

            if missing_overlay:
                lines.append("Overlay data source: PARTIAL / FALLBACK")
                lines.append("Missing overlay keys: " + ", ".join(missing_overlay))
            else:
                lines.append("Overlay data source: STATION PROFILE")
                lines.append("Missing overlay keys: none")
        else:
            lines.append("Overlay data source: STATIC FALLBACK")
            lines.append("Missing overlay keys: station profile unavailable")

        validity = g.get("channel_geometry_valid")
        fit_ratio = g.get("channel_fit_ratio")

        lines.append(f"Geometry valid: {validity}")
        lines.append(f"Fit ratio: {self.format_engineering_value(fit_ratio)}")
        lines.append(f"Cooling coverage: {self.format_engineering_value(g.get('cooling_coverage'))}")
        lines.append(
            f"Channel topology: {g.get('channel_topology_status', 'UNKNOWN')}"
        )
        lines.append(
            f"Topology transitions: {g.get('channel_topology_transition_count', 'N/A')}"
        )

        lines.append("")
        lines.append(
            "Canonical Regen Engineering Status"
        )

        lines.extend(
            self.canonical_regen_failure_lines()
        )

        return lines

    def build_validation_checklist(self, g):
        station = self.selected_station()
        profile = self.active_station_profile()

        def has_result_any(keys):
            for key in keys:
                if self.results.get(key) not in (None, ""):
                    return True
            return False

        def has_station_any(keys):
            if not station:
                return False

            for key in keys:
                if station.get(key) not in (None, ""):
                    return True
            return False

        checklist = []

        geometry_ready = (
                g.get("gas_radius") not in (None, "", 0)
                and g.get("wall") not in (None, "", 0)
                and g.get("channel_width") not in (None, "", 0)
                and g.get("channel_height") not in (None, "", 0)
                and g.get("channel_count") not in (None, "", 0)
                and g.get("available_pitch") not in (None, "", 0)
        )

        checklist.append((
            geometry_ready,
            "Geometry available",
            "Gas radius, wall, channel dimensions, channel count, and pitch are available."
        ))

        checklist.append((
            bool(profile),
            "Axial station profile available",
            "A station-by-station regen profile is available for inspection."
        ))

        thermal_ready = has_station_any([
            "hot_gas_side_wall_temperature",
            "coolant_side_wall_temperature",
            "regen_heat_flux",
            "thermal_resistance",
        ])

        checklist.append((
            thermal_ready,
            "Thermal station data available",
            "Twg, Twc, heat flux, or thermal resistance data exists at the selected station."
        ))

        coolant_ready = has_station_any([
            "coolant_temperature_in",
            "coolant_temperature_out",
            "coolant_temperature_mean",
            "coolant_velocity",
            "coolant_reynolds_number",
        ])

        checklist.append((
            coolant_ready,
            "Coolant station data available",
            "Coolant temperature, velocity, or Reynolds number data exists at the selected station."
        ))

        material_ready = has_result_any([
            "material_max_wall_temperature",
            "selected_material",
            "wall_material",
            "regen_material_status",
        ])

        checklist.append((
            material_ready,
            "Material limit available",
            "A material selection/status or wall temperature limit is available."
        ))

        coating_ready = has_result_any([
            "explicit_coating_liner_thickness",
            "coating_thickness",
            "explicit_coating_liner_profile",
            "explicit_coating_stack_status",
            "coating_validation_status",
        ])

        checklist.append((
            coating_ready,
            "Coating / liner data available",
            "Coating thickness, coating profile, or coating validation status is available."
        ))

        export_ready = (
                geometry_ready
                and bool(profile)
                and self.canvas_exports_ready()
        )

        checklist.append((
            export_ready,
            "Figure/export ready",
            "Viewer has enough geometry and station data to export useful figures."
        ))

        sourced_validation_ready = has_result_any([
            "material_validation_mode",
            "coating_validation_mode",
            "source_validation_mode",
        ])

        checklist.append((
            sourced_validation_ready,
            "Sourced validation mode available",
            "PLACEHOLDER/PARTIAL/SOURCED validation mode information is available."
        ))

        real_engine_validation_ready = has_result_any([
            "real_engine_validation_status",
            "regen_scalability_validation_status",
            "validation_reference_engine",
        ])

        checklist.append((
            real_engine_validation_ready,
            "Real-engine comparison ready",
            "Reference-engine/scalability validation fields are available."
        ))

        return checklist

    def evaluate_regen_signoff(self, g):
        checklist = self.build_validation_checklist(g)

        total_items = len(checklist)
        passed_items = len([item for item in checklist if item[0]])

        checklist_complete = total_items > 0 and passed_items == total_items

        regen_status = str(
            self.results.get("regen_overall_status")
            or self.results.get("final_regen_design_verdict")
            or "UNKNOWN"
        ).upper()

        material_mode = str(
            self.results.get("material_validation_mode")
            or self.results.get("source_validation_mode")
            or "PLACEHOLDER_MODE"
        ).upper()

        coating_mode = str(
            self.results.get("coating_validation_mode")
            or self.results.get("explicit_coating_validation_mode")
            or "PLACEHOLDER_MODE"
        ).upper()

        scalability_status = str(
            self.results.get("regen_scalability_validation_status")
            or self.results.get("real_engine_validation_status")
            or "NOT_RUN"
        ).upper()

        reference_verdict = str(
            self.results.get("reference_validation_verdict")
            or "REFERENCE_NOT_SELECTED"
        ).upper()

        source_maturity = self.evaluate_source_maturity_score()

        placeholder_blocked = (
                "PLACEHOLDER" in material_mode
                or "PLACEHOLDER" in coating_mode
        )

        sourced_ready = (
                "SOURCED" in material_mode
                and "SOURCED" in coating_mode
        )

        reference_ready = reference_verdict in (
            "REFERENCE_ORDER_OF_MAGNITUDE_PASS",
            "REFERENCE_ORDER_OF_MAGNITUDE_WARN",
        )

        scalability_ready = (
                "PASS" in scalability_status
                or "COMPLETE" in scalability_status
                or "READY" in scalability_status
                or reference_ready
        )

        solver_pass = (
                regen_status == "PASS"
                or "PASS_WITH_MARGIN" in regen_status
                or "PLAUSIBLE" in regen_status
        )

        if placeholder_blocked:
            status = "DEVELOPMENT_ROUTE_ONLY"
            colour = QColor(210, 155, 45)
            next_action = "Add sourced material/coating property data before allowing engineering PASS."

        elif not checklist_complete:
            status = "VIEWER_INCOMPLETE"
            colour = QColor(210, 155, 45)
            next_action = "Complete missing checklist items before subsystem sign-off."

        elif not solver_pass:
            status = "ENGINEERING_NOT_SIGNED_OFF"
            colour = QColor(185, 65, 65)
            next_action = "Resolve regen validation failures before moving to external testing."

        elif not sourced_ready:
            status = "PARTIAL_SOURCE_MODE"
            colour = QColor(210, 155, 45)
            next_action = "Upgrade material/coating data to SOURCED_VALIDATION_MODE."


        elif not scalability_ready:

            status = "SCALABILITY_VALIDATION_REQUIRED"

            colour = QColor(210, 155, 45)

            if reference_verdict in (

                    "REFERENCE_NOT_SELECTED",

                    "REFERENCE_DATA_REQUIRED",

                    "REFERENCE_PARTIAL_ONLY",

                    "REFERENCE_VALIDATION_INCOMPLETE",

            ):

                next_action = (

                    "Complete reference-engine validation before regen sign-off."

                )

            else:

                next_action = "Run small/medium/large/real-engine validation matrix."

        else:
            status = "REGEN_SIGNED_OFF"
            colour = QColor(45, 145, 85)
            next_action = "Regen subsystem is ready for workspace integration and closed-alpha preparation."

        external_testing_ready = (
                status == "REGEN_SIGNED_OFF"
                and sourced_ready
                and scalability_ready
                and solver_pass
                and reference_ready
        )

        return {
            "status": status,
            "colour": colour,
            "passed_items": passed_items,
            "total_items": total_items,
            "regen_status": regen_status,
            "material_mode": material_mode,
            "coating_mode": coating_mode,
            "scalability_status": scalability_status,
            "reference_verdict": reference_verdict,
            "placeholder_blocked": placeholder_blocked,
            "sourced_ready": sourced_ready,
            "scalability_ready": scalability_ready,
            "solver_pass": solver_pass,
            "source_maturity_score": source_maturity["overall_score"],
            "source_maturity_status": source_maturity["status"],
            "external_testing_ready": external_testing_ready,
            "next_action": next_action,
        }

    def canvas_exports_ready(self):
        return True

    def draw_diagnostics_panel(self, painter, g, x, y):
        lines = self.build_diagnostics_lines(g)

        panel_w = 390
        line_h = 18
        panel_h = 24 + line_h * min(len(lines), 14)

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(24, 24, 24)))
        painter.drawRect(int(x), int(y), int(panel_w), int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(int(x + 12), int(y + 20), "Viewer Diagnostics")

        y_cursor = y + 42

        for line in lines[:14]:
            upper = str(line).upper()

            if "MISSING" in upper or "FALLBACK" in upper or "PARTIAL" in upper or "NO" in upper:
                painter.setPen(QPen(QColor(220, 160, 70), 1))
            elif "INVALID" in upper or "FAIL" in upper:
                painter.setPen(QPen(QColor(220, 90, 90), 1))
            elif "STATION PROFILE" in upper or "YES" in upper:
                painter.setPen(QPen(QColor(120, 220, 150), 1))
            else:
                painter.setPen(QPen(QColor(205, 205, 205), 1))

            painter.drawText(int(x + 12), int(y_cursor), str(line))
            y_cursor += line_h

    def draw_validation_checklist_panel(self, painter, g, x, y):
        checklist = self.build_validation_checklist(g)

        panel_w = 430
        row_h = 22
        panel_h = 34 + row_h * len(checklist)

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(24, 24, 24)))
        painter.drawRect(int(x), int(y), int(panel_w), int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(int(x + 12), int(y + 22), "Regen Viewer Validation Checklist")

        y_cursor = y + 46

        for passed, title, description in checklist:
            if passed:
                box_colour = QColor(45, 145, 85)
                symbol = "✓"
            else:
                box_colour = QColor(185, 65, 65)
                symbol = "!"

            painter.setPen(QPen(QColor(10, 10, 10), 1))
            painter.setBrush(QBrush(box_colour))
            painter.drawRect(int(x + 12), int(y_cursor - 13), 14, 14)

            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(int(x + 15), int(y_cursor - 2), symbol)

            painter.setPen(QPen(QColor(230, 230, 230), 1))
            painter.drawText(int(x + 34), int(y_cursor), title)

            y_cursor += row_h

        failed_count = len([item for item in checklist if not item[0]])

        painter.setPen(QPen(QColor(180, 180, 180), 1))

        if failed_count:
            summary = f"{failed_count} checklist item(s) incomplete. Use diagnostics for missing data detail."
        else:
            summary = "Checklist complete for current regen viewer state."

        painter.drawText(int(x + 12), int(y + panel_h - 8), summary)

    def draw_regen_signoff_panel(self, painter, g, x, y):
        signoff = self.evaluate_regen_signoff(g)

        panel_w = 470
        panel_h = 232

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(24, 24, 24)))
        painter.drawRect(int(x), int(y), int(panel_w), int(panel_h))

        painter.setBrush(QBrush(signoff["colour"]))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(x), int(y), 10, int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(int(x + 18), int(y + 24), "Regen Subsystem Sign-Off")

        painter.setPen(QPen(signoff["colour"], 1))
        painter.drawText(int(x + 18), int(y + 50), f"Status: {signoff['status']}")

        painter.setPen(QPen(QColor(215, 215, 215), 1))
        painter.drawText(
            int(x + 18),
            int(y + 76),
            f"Checklist: {signoff['passed_items']} / {signoff['total_items']} complete"
        )

        painter.drawText(
            int(x + 18),
            int(y + 98),
            f"Regen solver status: {signoff['regen_status']}"
        )

        painter.drawText(
            int(x + 18),
            int(y + 120),
            f"Material mode: {signoff['material_mode']}"
        )

        painter.drawText(
            int(x + 18),
            int(y + 142),
            f"Coating mode: {signoff['coating_mode']}"
        )

        painter.drawText(
            int(x + 18),
            int(y + 164),
            f"Scalability validation: {signoff['scalability_status']}"
        )

        painter.drawText(
            int(x + 18),
            int(y + 186),
            f"Source maturity: {signoff['source_maturity_score']} / 100 ({signoff['source_maturity_status']})"
        )

        external_text = "YES" if signoff["external_testing_ready"] else "NO"
        painter.drawText(
            int(x + 18),
            int(y + 208),
            f"Ready for external testers: {external_text}"
        )

        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawText(
            int(x + 18),
            int(y + 228),
            f"Next: {signoff['next_action']}"
        )

    def build_source_data_checklist(self):
        def value_bool(key):
            value = self.results.get(key)
            if isinstance(value, str):
                return value.strip().lower() in ("true", "yes", "1", "pass")
            return bool(value)

        checklist = []

        checklist.append((
            value_bool("material_source_has_citation"),
            "Material citation",
            "Add source_title, citation, DOI, or URL for selected wall material."
        ))

        checklist.append((
            value_bool("material_source_has_temperature_table"),
            "Material temperature table",
            "Add temperature-dependent material properties."
        ))

        checklist.append((
            not value_bool("material_source_is_placeholder"),
            "Material is not placeholder",
            "Replace placeholder/default wall material data with sourced data."
        ))

        checklist.append((
            value_bool("coating_source_has_citation"),
            "Coating citation",
            "Add source_title, citation, DOI, or URL for selected coating."
        ))

        checklist.append((
            value_bool("coating_source_has_temperature_table"),
            "Coating temperature table",
            "Add temperature-dependent coating conductivity/stress data."
        ))

        checklist.append((
            not value_bool("coating_source_is_placeholder"),
            "Coating is not placeholder",
            "Replace placeholder/default coating data with sourced data."
        ))

        checklist.append((
            value_bool("bond_coat_source_has_citation"),
            "Bond-coat citation",
            "Add source evidence for selected bond coat."
        ))

        checklist.append((
            value_bool("bond_coat_source_has_temperature_table"),
            "Bond-coat temperature table",
            "Add temperature-dependent bond-coat data where available."
        ))

        checklist.append((
            not value_bool("bond_coat_source_is_placeholder"),
            "Bond-coat is not placeholder",
            "Replace placeholder/default bond-coat data with sourced data."
        ))

        source_mode = str(self.results.get("source_validation_mode", "PLACEHOLDER_MODE")).upper()

        checklist.append((
            source_mode != "PLACEHOLDER_MODE",
            "Source mode beyond placeholder",
            "At least partial sourced evidence is required."
        ))

        checklist.append((
            source_mode == "SOURCED_VALIDATION_MODE",
            "Sourced validation mode",
            "Full sourced validation requires citations and temperature tables."
        ))

        return checklist

    def evaluate_source_maturity_score(self):
        def bool_value(key):
            value = self.results.get(key)

            if isinstance(value, str):
                return value.strip().lower() in ("true", "yes", "1", "pass")

            return bool(value)

        def numeric_value(key, default=0.0):
            try:
                return float(self.results.get(key, default))
            except Exception:
                return default

        material_score = numeric_value("material_source_validation_score", 0.0)
        coating_score = numeric_value("coating_source_validation_score", 0.0)
        bond_score = numeric_value("bond_coat_source_validation_score", 0.0)

        material_bonus = 0.0
        coating_bonus = 0.0
        bond_bonus = 0.0

        if bool_value("material_source_has_citation"):
            material_bonus += 10.0
        if bool_value("material_source_has_temperature_table"):
            material_bonus += 15.0
        if not bool_value("material_source_is_placeholder"):
            material_bonus += 15.0

        if bool_value("coating_source_has_citation"):
            coating_bonus += 10.0
        if bool_value("coating_source_has_temperature_table"):
            coating_bonus += 15.0
        if not bool_value("coating_source_is_placeholder"):
            coating_bonus += 15.0

        if bool_value("bond_coat_source_has_citation"):
            bond_bonus += 10.0
        if bool_value("bond_coat_source_has_temperature_table"):
            bond_bonus += 15.0
        if not bool_value("bond_coat_source_is_placeholder"):
            bond_bonus += 15.0

        material_component = min(100.0, material_score + material_bonus)
        coating_component = min(100.0, coating_score + coating_bonus)
        bond_component = min(100.0, bond_score + bond_bonus)

        overall = (
            0.45 * material_component
            + 0.35 * coating_component
            + 0.20 * bond_component
        )

        source_mode = str(self.results.get("source_validation_mode", "PLACEHOLDER_MODE")).upper()

        placeholder_blocked = (
            bool_value("material_source_is_placeholder")
            or bool_value("coating_source_is_placeholder")
            or bool_value("bond_coat_source_is_placeholder")
            or source_mode == "PLACEHOLDER_MODE"
        )

        if placeholder_blocked:
            status = "PLACEHOLDER_BLOCKED"
            colour = QColor(185, 65, 65)
            recommendation = "Replace placeholder material/coating/bond-coat data with sourced evidence."
        elif overall >= 85.0 and source_mode == "SOURCED_VALIDATION_MODE":
            status = "SOURCED_VALIDATION_READY"
            colour = QColor(45, 145, 85)
            recommendation = "Source evidence is mature enough for sourced validation review."
        elif overall >= 45.0:
            status = "PARTIAL_SOURCE_EVIDENCE"
            colour = QColor(210, 155, 45)
            recommendation = "Evidence exists, but citations, tables, or source coverage remain incomplete."
        else:
            status = "INSUFFICIENT_SOURCE_EVIDENCE"
            colour = QColor(185, 65, 65)
            recommendation = "Add citations, temperature tables, and non-placeholder property records."

        return {
            "overall_score": round(overall, 2),
            "material_score": round(material_component, 2),
            "coating_score": round(coating_component, 2),
            "bond_score": round(bond_component, 2),
            "status": status,
            "colour": colour,
            "recommendation": recommendation,
            "placeholder_blocked": placeholder_blocked,
        }

    def draw_source_data_checklist_panel(self, painter, g, x, y):
        checklist = self.build_source_data_checklist()
        maturity = self.evaluate_source_maturity_score()

        panel_w = 520
        row_h = 22
        panel_h = 42 + row_h * len(checklist)

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(24, 24, 24)))
        painter.drawRect(int(x), int(y), int(panel_w), int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(
            int(x + 12),
            int(y + 24),
            f"Source-Data Checklist — Maturity {maturity['overall_score']} / 100"
        )

        y_cursor = y + 50

        for passed, title, action in checklist:
            if passed:
                colour = QColor(45, 145, 85)
                symbol = "✓"
            else:
                colour = QColor(185, 65, 65)
                symbol = "!"

            painter.setPen(QPen(QColor(10, 10, 10), 1))
            painter.setBrush(QBrush(colour))
            painter.drawRect(int(x + 12), int(y_cursor - 14), 14, 14)

            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(int(x + 15), int(y_cursor - 3), symbol)

            painter.setPen(QPen(QColor(230, 230, 230), 1))
            painter.drawText(int(x + 34), int(y_cursor), title)

            if not passed:
                painter.setPen(QPen(QColor(180, 180, 180), 1))
                painter.drawText(int(x + 220), int(y_cursor), action[:52])

            y_cursor += row_h

        failed = len([item for item in checklist if not item[0]])

        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawText(
            int(x + 12),
            int(y + panel_h - 8),
            f"{failed} source evidence item(s) incomplete. Status: {maturity['status']}"
        )

    def draw_source_validation_panel(self, painter, g, x, y):
        panel_w = 500
        panel_h = 260

        source_mode = str(self.results.get("source_validation_mode", "PLACEHOLDER_MODE")).upper()
        material_mode = str(self.results.get("material_validation_mode", "PLACEHOLDER_MODE")).upper()
        coating_mode = str(self.results.get("coating_validation_mode", "PLACEHOLDER_MODE")).upper()
        bond_mode = str(self.results.get("bond_coat_validation_mode", "PLACEHOLDER_MODE")).upper()

        gate = self.results.get("source_validation_conservative_gate", "UNKNOWN")
        status = self.results.get("regen_source_validation_status", "UNKNOWN")
        recommendation = self.results.get("regen_source_validation_recommendation", "No recommendation available.")
        maturity = self.evaluate_source_maturity_score()

        if "SOURCED" in source_mode:
            colour = QColor(45, 145, 85)
        elif "PARTIAL" in source_mode:
            colour = QColor(210, 155, 45)
        else:
            colour = QColor(185, 65, 65)

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(24, 24, 24)))
        painter.drawRect(int(x), int(y), int(panel_w), int(panel_h))

        painter.setBrush(QBrush(colour))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(x), int(y), 10, int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(int(x + 18), int(y + 24), "Material / Coating Source Validation")

        painter.setPen(QPen(colour, 1))
        painter.drawText(int(x + 18), int(y + 52), f"Source mode: {source_mode}")

        painter.setPen(QPen(QColor(215, 215, 215), 1))
        painter.drawText(int(x + 18), int(y + 78), f"Material mode: {material_mode}")
        painter.drawText(int(x + 18), int(y + 100), f"Coating mode: {coating_mode}")
        painter.drawText(int(x + 18), int(y + 122), f"Bond-coat mode: {bond_mode}")
        painter.drawText(int(x + 18), int(y + 144), f"Conservative gate: {gate}")
        painter.drawText(int(x + 18), int(y + 166), f"Source status: {status}")
        painter.drawText(
            int(x + 18),
            int(y + 188),
            f"Maturity score: {maturity['overall_score']} / 100   ({maturity['status']})"
        )

        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawText(int(x + 18), int(y + 216), "Next source action:")

        painter.setPen(QPen(QColor(220, 220, 220), 1))
        painter.drawText(int(x + 18), int(y + 238), str(maturity["recommendation"] or recommendation)[:86])

    def draw_overlay_colour_key(self, painter, x, y):
        painter.setPen(QPen(QColor(210, 210, 210), 1))
        painter.setBrush(QBrush(QColor(28, 28, 28)))
        painter.drawRect(int(x), int(y), 220, 58)

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(int(x + 8), int(y + 18), f"{self.overlay_mode.upper()} Key")

        if self.overlay_mode == "thermal":
            left_label = "Cooler"
            right_label = "Hotter"
            cold = QColor(70, 120, 210)
            hot = QColor(230, 65, 45)

        elif self.overlay_mode == "coolant":
            left_label = "Cold / turbulent"
            right_label = "Hot / weak"
            cold = QColor(20, 155, 215)
            hot = QColor(230, 150, 45)

        elif self.overlay_mode == "gas":
            left_label = "Low Mach/T"
            right_label = "High Mach/T"
            cold = QColor(35, 80, 150)
            hot = QColor(230, 190, 60)

        elif self.overlay_mode == "validation":
            painter.setBrush(QBrush(QColor(45, 145, 85)))
            painter.drawRect(int(x + 12), int(y + 34), 18, 14)
            painter.setPen(QPen(QColor(245, 245, 245), 1))
            painter.drawText(int(x + 38), int(y + 46), "PASS / valid")

            painter.setBrush(QBrush(QColor(210, 155, 45)))
            painter.setPen(QPen(QColor(10, 10, 10), 1))
            painter.drawRect(int(x + 112), int(y + 34), 18, 14)
            painter.setPen(QPen(QColor(245, 245, 245), 1))
            painter.drawText(int(x + 138), int(y + 46), "Warning")

            painter.setBrush(QBrush(QColor(185, 65, 65)))
            painter.setPen(QPen(QColor(10, 10, 10), 1))
            painter.drawRect(int(x + 12), int(y + 56), 18, 14)
            painter.setPen(QPen(QColor(245, 245, 245), 1))
            painter.drawText(int(x + 38), int(y + 68), "FAIL / invalid")
            return

        else:
            painter.setPen(QPen(QColor(180, 180, 180), 1))
            painter.drawText(int(x + 8), int(y + 40), "Physical layer colours")
            return

        bar_x = x + 12
        bar_y = y + 36
        bar_w = 160
        bar_h = 14

        for i in range(int(bar_w)):
            t = i / max(1, bar_w - 1)
            r = int(cold.red() + (hot.red() - cold.red()) * t)
            g = int(cold.green() + (hot.green() - cold.green()) * t)
            b = int(cold.blue() + (hot.blue() - cold.blue()) * t)

            painter.setPen(QPen(QColor(r, g, b), 1))
            painter.drawLine(
                int(bar_x + i),
                int(bar_y),
                int(bar_x + i),
                int(bar_y + bar_h)
            )

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(int(bar_x), int(bar_y + 34), left_label)
        painter.drawText(int(bar_x + bar_w - 40), int(bar_y + 34), right_label)

    def station_numeric_value(self, station, keys, default=None):
        if not isinstance(station, dict):
            return default

        for key in keys:
            value = station.get(key)

            if value in (None, ""):
                continue

            try:
                return float(value)
            except Exception:
                continue

        return default

    def profile_numeric_range(self, profile, keys):
        values = []

        for station in profile:
            value = self.station_numeric_value(station, keys, None)

            if value is not None:
                values.append(value)

        if not values:
            return None, None

        low = min(values)
        high = max(values)

        if abs(high - low) < 1.0e-12:
            high = low + 1.0

        return low, high

    def trend_keys_for_overlay(self):
        if self.overlay_mode == "thermal":
            return [
                "hot_gas_side_wall_temperature",
                "variable_thermal_hot_wall_temperature",
                "coupled_split_hot_wall_temperature",
                "explicit_coating_liner_liner_temperature",
            ], "Twg axial trend"

        if self.overlay_mode == "coolant":
            return [
                "coolant_temperature_out",
                "coolant_temperature_mean",
                "coolant_temperature",
                "coupled_split_coolant_out_temperature",
            ], "Coolant temperature axial trend"

        if self.overlay_mode == "gas":
            return [
                "mach",
            ], "Mach axial trend"

        if self.overlay_mode == "geometry":
            return [
                "radius",
            ], "Radius axial trend"

        return [], "Validation axial trend"

    def station_validation_status(self, station):
        if not isinstance(station, dict):
            return "UNKNOWN"

        for key in (
            "variable_geometry_valid",
            "safe_variable_geometry_valid",
            "variable_thermal_pass",
            "coupled_split_pass",
            "explicit_coating_thermal_stress_pass",
        ):
            if key in station:
                return str(station.get(key))

        return self.station_status_text()

    def draw_station_minimap(self, painter, g, x, y, w):
        h = 76

        painter.setPen(QPen(QColor(70, 70, 70), 1))
        painter.setBrush(QBrush(QColor(28, 28, 28)))
        painter.drawRect(int(x), int(y), int(w), h)

        profile = self.active_station_profile()

        canonical = extract_canonical_full_engine_profile(
            self.results
        )

        bar_x = x + 18
        bar_y = y + 34
        bar_w = w - 36
        bar_h = 12

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(
            int(x + 12),
            int(y + 18),
            "Axial Station Position + Trend"
        )

        if not (
            canonical.get("available")
            and
            canonical.get("authoritative")
            and
            canonical.get("exact_canonical")
            and
            canonical.get("full_engine")
        ):
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawText(
                int(x + 12),
                int(y + 46),
                "Canonical full-engine geometry unavailable"
            )
            return

        try:
            x_min = float(
                canonical["x_min"]
            )
            x_max = float(
                canonical["x_max"]
            )
            selected_x = float(
                canonical["selected_x"]
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawText(
                int(x + 12),
                int(y + 46),
                "Canonical full-engine geometry unavailable"
            )
            return

        x_span = (
            x_max
            - x_min
        )

        if not (
            x_span > 0.0
        ):
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawText(
                int(x + 12),
                int(y + 46),
                "Canonical full-engine geometry unavailable"
            )
            return

        station_x = self.station_value(
            ["x"],
            selected_x,
        )

        try:
            station_x = float(
                station_x
            )
        except Exception:
            station_x = selected_x

        def canonical_fraction(
            axial_x,
        ):
            try:
                axial_x = float(
                    axial_x
                )
            except (
                TypeError,
                ValueError,
            ):
                return None

            return max(
                0.0,
                min(
                    1.0,
                    (
                        axial_x
                        - x_min
                    )
                    / x_span,
                ),
            )

        fraction = canonical_fraction(
            selected_x
        )

        station_fraction = canonical_fraction(
            station_x
        )

        if fraction is None:
            fraction = 0.0

        if station_fraction is None:
            station_fraction = fraction

        # Trend strip.
        # Geometry / axial placement is owned exclusively by the
        # canonical full-engine x-domain above. The selected regen
        # station profile remains a data source for trend values only.
        trend_keys, trend_label = self.trend_keys_for_overlay()

        if profile and self.overlay_mode != "validation":
            low, high = self.profile_numeric_range(
                profile,
                trend_keys,
            )

            if low is not None and high is not None:
                previous_x = None

                for station in profile:
                    station_x_value = self.station_numeric_value(
                        station,
                        ["x"],
                        None,
                    )

                    t = canonical_fraction(
                        station_x_value
                    )

                    if t is None:
                        continue

                    px = (
                        bar_x
                        + t
                        * bar_w
                    )

                    value = self.station_numeric_value(
                        station,
                        trend_keys,
                        None,
                    )

                    colour = self.gradient_colour(
                        value,
                        low,
                        high,
                    )

                    if previous_x is not None:
                        painter.setPen(
                            QPen(
                                colour,
                                5,
                            )
                        )

                        painter.drawLine(
                            int(previous_x),
                            int(bar_y + bar_h / 2),
                            int(px),
                            int(bar_y + bar_h / 2),
                        )

                    previous_x = px

            else:
                painter.setPen(
                    QPen(
                        QColor(
                            120,
                            120,
                            120,
                        ),
                        5,
                    )
                )

                painter.drawLine(
                    int(bar_x),
                    int(bar_y + bar_h / 2),
                    int(bar_x + bar_w),
                    int(bar_y + bar_h / 2),
                )

        elif (
            profile
            and
            self.overlay_mode == "validation"
        ):
            previous_x = None

            for station in profile:
                station_x_value = self.station_numeric_value(
                    station,
                    ["x"],
                    None,
                )

                t = canonical_fraction(
                    station_x_value
                )

                if t is None:
                    continue

                px = (
                    bar_x
                    + t
                    * bar_w
                )

                status = self.station_validation_status(
                    station
                )

                colour = self.validation_colour(
                    status
                )

                if previous_x is not None:
                    painter.setPen(
                        QPen(
                            colour,
                            5,
                        )
                    )

                    painter.drawLine(
                        int(previous_x),
                        int(bar_y + bar_h / 2),
                        int(px),
                        int(bar_y + bar_h / 2),
                    )

                previous_x = px

        else:
            painter.setPen(
                QPen(
                    QColor(
                        120,
                        120,
                        120,
                    ),
                    5,
                )
            )

            painter.drawLine(
                int(bar_x),
                int(bar_y + bar_h / 2),
                int(bar_x + bar_w),
                int(bar_y + bar_h / 2),
            )

        # Canonical axial-domain track outline.
        # No engine/nozzle silhouette is reconstructed here.
        painter.setPen(
            QPen(
                QColor(
                    170,
                    170,
                    170,
                ),
                1,
            )
        )

        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawRect(
            int(bar_x),
            int(bar_y - 6),
            int(bar_w),
            int(bar_h + 12),
        )

        selected_marker_x = (
            bar_x
            + fraction
            * bar_w
        )

        nearest_marker_x = (
            bar_x
            + station_fraction
            * bar_w
        )

        # Nearest solved station marker.
        painter.setPen(
            QPen(
                QColor(
                    220,
                    180,
                    70,
                ),
                2,
            )
        )

        painter.drawLine(
            int(nearest_marker_x),
            int(bar_y - 16),
            int(nearest_marker_x),
            int(bar_y + bar_h + 16),
        )

        # Slider-selected marker.
        painter.setPen(
            QPen(
                QColor(
                    90,
                    170,
                    240,
                ),
                2,
            )
        )

        painter.drawLine(
            int(selected_marker_x),
            int(bar_y - 20),
            int(selected_marker_x),
            int(bar_y + bar_h + 20),
        )

        painter.setPen(
            QPen(
                QColor(
                    190,
                    190,
                    190,
                ),
                1,
            )
        )

        painter.drawText(
            int(x + 12),
            int(y + 62),
            (
                f"{trend_label}"
                "   |   Blue = slider position"
                "   |   Gold = nearest solved station"
                f"   |   x = {self.format_engineering_value(selected_x, 'm')}"
            ),
        )



    def draw_station_overlay_panel(self, painter, g, x, y, w):
        station = self.selected_station()
        profile_label = self.available_station_profiles().get(
            self.station_profile_key,
            self.station_profile_key
        )

        painter.setPen(QPen(QColor(70, 70, 70), 1))
        painter.setBrush(QBrush(QColor(28, 28, 28)))
        painter.drawRect(int(x), int(y), int(w), 96)

        status = self.station_status_text(g)
        status_colour = self.validation_colour(status)

        painter.setBrush(QBrush(status_colour))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(x), int(y), 8, 96)

        selected_x = g.get("selected_length", 0.0)

        station_x = self.station_value(["x"], selected_x)
        station_index = self.station_value(
            ["station_index", "source_station_index", "coolant_path_index"],
            "N/A"
        )

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(
            int(x + 18),
            int(y + 24),
            f"Station Inspector  |  {profile_label}  |  Mode: {self.overlay_mode.upper()}"
        )

        painter.setPen(QPen(QColor(190, 190, 190), 1))
        painter.drawText(
            int(x + 18),
            int(y + 46),
            f"Selected x: {self.format_engineering_value(selected_x, 'm')}     "
            f"Nearest station x: {self.format_engineering_value(station_x, 'm')}     "
            f"Station index/path: {station_index}     "
            f"Status: {status}"
        )

        if self.overlay_mode == "geometry":
            line = (
                f"Radius: {self.format_engineering_value(self.station_value(['radius'], g.get('gas_radius')), 'm')}     "
                f"Area: {self.format_engineering_value(self.station_value(['area']), 'm²')}     "
                f"Channel width: {self.format_engineering_value(g.get('channel_width'), 'm')}     "
                f"Rib: {self.format_engineering_value(g.get('effective_rib_width'), 'm')}     "
                f"Pitch: {self.format_engineering_value(g.get('available_pitch'), 'm')}"
            )

        elif self.overlay_mode == "gas":
            line = (
                f"Mach: {self.format_engineering_value(self.station_value(['mach']))}     "
                f"Static T: {self.format_engineering_value(self.station_value(['static_temperature']), 'K')}     "
                f"Static P: {self.format_engineering_value(self.station_value(['static_pressure']), 'Pa')}     "
                f"Taw: {self.format_engineering_value(self.station_value(['adiabatic_wall_temperature']), 'K')}     "
                f"hg: {self.format_engineering_value(self.station_value(['hg', 'hot_gas_heat_transfer_coefficient']), 'W/m²K')}"
            )

        elif self.overlay_mode == "thermal":
            line = (
                f"Twg: {self.format_engineering_value(self.station_value(['hot_gas_side_wall_temperature', 'variable_thermal_hot_wall_temperature', 'coupled_split_hot_wall_temperature']), 'K')}     "
                f"Twc: {self.format_engineering_value(self.station_value(['coolant_side_wall_temperature']), 'K')}     "
                f"q'': {self.format_engineering_value(self.station_value(['regen_heat_flux', 'heat_flux']), 'W/m²')}     "
                f"Thermal R: {self.format_engineering_value(self.station_value(['thermal_resistance']), 'm²K/W')}     "
                f"Bottleneck: {self.station_value(['controlling_thermal_resistance'], 'N/A')}"
            )

        elif self.overlay_mode == "coolant":
            line = (
                f"Tc in: {self.format_engineering_value(self.station_value(['coolant_temperature_in', 'coupled_split_coolant_in_temperature']), 'K')}     "
                f"Tc out: {self.format_engineering_value(self.station_value(['coolant_temperature_out', 'coolant_temperature', 'coupled_split_coolant_out_temperature']), 'K')}     "
                f"Velocity: {self.format_engineering_value(self.station_value(['coolant_velocity', 'variable_coolant_velocity', 'safe_variable_coolant_velocity']), 'm/s')}     "
                f"Re: {self.format_engineering_value(self.station_value(['coolant_reynolds_number', 'variable_reynolds_number', 'safe_variable_reynolds_number']))}     "
                f"ΔP total: {self.format_engineering_value(self.station_value(['total_pressure_drop_so_far']), 'Pa')}"
            )

        else:
            line = (
                f"Overall: {self.text_any(['regen_overall_status', 'overall_status'])}     "
                f"Geometry: {self.text_any(['regen_geometry_status', 'geometry_status'])}     "
                f"Thermal: {self.text_any(['regen_thermal_status', 'thermal_status'])}     "
                f"Coolant: {self.text_any(['regen_coolant_status', 'coolant_status'])}     "
                f"Material: {self.text_any(['regen_material_status', 'material_status'])}"
            )

        painter.setPen(QPen(QColor(235, 235, 235), 1))
        painter.drawText(int(x + 18), int(y + 76), line)

        painter.setPen(QPen(QColor(170, 170, 170), 1))

        if self.overlay_mode == "thermal":
            overlay_note = "Colour overlay: wall ≈ local Twg, channel band ≈ coolant-side temperature."
        elif self.overlay_mode == "coolant":
            overlay_note = "Colour overlay: coolant void ≈ coolant temperature, channel band ≈ Reynolds validity."
        elif self.overlay_mode == "gas":
            overlay_note = "Colour overlay: gas bore ≈ local Mach/static-temperature intensity."
        elif self.overlay_mode == "validation":
            overlay_note = "Colour overlay: jacket/channel band show local validation status."
        else:
            overlay_note = "Colour overlay: physical material/layer colours."

        painter.drawText(
            int(x + 18),
            int(y + 92),
            overlay_note
        )

        if station is None:
            painter.setPen(QPen(QColor(220, 160, 70), 1))
            painter.drawText(
                int(x + 18),
                int(y + 92),
                "No axial station profile found. Viewer is using static result values only."
            )

    def get_reference_gas_radius_for_view(self):
        """
        Fixed drawing reference radius for the whole nozzle.

        This prevents each selected station from being auto-scaled to fill the
        viewport, which made the station slider look like it changed X but not
        geometry.
        """
        candidate_values = []

        for key in (
                "exit_radius",
                "nozzle_exit_radius",
                "rao_exit_radius",
                "conical_exit_radius",
                "throat_radius",
        ):
            value = self.value(key, None)
            if value is not None and value > 0:
                candidate_values.append(value)

        for profile_key in (
                "rao_nozzle_profile",
                "conical_nozzle_profile",
                "regen_axial_profile",
                "variable_channel_geometry_profile",
                "variable_geometry_thermal_profile",
        ):
            profile = self.results.get(profile_key)

            if not isinstance(profile, list):
                continue

            for station in profile:
                if not isinstance(station, dict):
                    continue

                for radius_key in (
                        "radius",
                        "gas_radius",
                        "local_radius",
                        "inner_radius",
                        "hot_gas_radius",
                ):
                    try:
                        value = station.get(radius_key)
                        if value not in (None, "") and float(value) > 0:
                            candidate_values.append(float(value))
                    except Exception:
                        pass

                try:
                    area = station.get("area")
                    if area not in (None, "") and float(area) > 0:
                        candidate_values.append(math.sqrt(float(area) / math.pi))
                except Exception:
                    pass

        if candidate_values:
            return max(candidate_values)

        return 0.01

    def evaluate_channel_topology_status(self):
        """
        Phase 11A.11:
        Evaluates whether the viewed channel-count behaviour is topologically believable.

        Current limitation:
        The cross-section viewer can show N channels at a station, but it does not
        yet model physical split/merge/manifold transitions between stations.
        """
        profile = self.active_station_profile()

        if not isinstance(profile, list) or len(profile) < 2:
            return {
                "status": "TOPOLOGY_UNKNOWN",
                "severity": "WARN",
                "reason": "No usable axial station profile is available.",
                "transition_count": 0,
                "channel_counts": [],
            }

        channel_counts = []

        for station in profile:
            if not isinstance(station, dict):
                continue

            for key in (
                    "channel_count",
                    "number_of_coolant_channels",
                    "recommended_channel_count",
                    "coolant_channel_count",
            ):
                value = station.get(key)

                if value in (None, ""):
                    continue

                try:
                    count = int(round(float(value)))
                    if count > 0:
                        channel_counts.append(count)
                        break
                except Exception:
                    pass

        if not channel_counts:
            return {
                "status": "CONSTANT_COUNT_ASSUMED",
                "severity": "WARN",
                "reason": (
                    "Station profile does not contain axial channel-count topology data. "
                    "Viewer assumes one constant channel count until split/merge modelling exists."
                ),
                "transition_count": 0,
                "channel_counts": [],
            }

        unique_counts = sorted(set(channel_counts))

        if len(unique_counts) == 1:
            return {
                "status": "CONSTANT_CHANNEL_TOPOLOGY",
                "severity": "PASS",
                "reason": "Channel count is constant across available stations.",
                "transition_count": 0,
                "channel_counts": unique_counts,
            }

        transition_count = 0
        previous = channel_counts[0]

        for count in channel_counts[1:]:
            if count != previous:
                transition_count += 1
            previous = count

        return {
            "status": "TOPOLOGY_TRANSITIONS_NOT_MODELLED",
            "severity": "FAIL",
            "reason": (
                "Channel count changes along the nozzle, but split/merge transition "
                "geometry is not yet modelled."
            ),
            "transition_count": transition_count,
            "channel_counts": unique_counts,
        }

    def draw_channel_topology_warning(self, painter, x, y):
        topology = self.evaluate_channel_topology_status()

        status = topology.get("status", "UNKNOWN")
        severity = topology.get("severity", "WARN")
        reason = topology.get("reason", "No topology reason available.")
        counts = topology.get("channel_counts", [])
        transitions = topology.get("transition_count", 0)

        severity_role = _leaf_16u38_status_severity(severity)
        if severity_role == "PASS":
            colour = QColor(45, 145, 85)
        elif severity_role == "FAIL":
            colour = QColor(185, 65, 65)
        else:
            colour = QColor(210, 155, 45)

        panel_w = min(
            560,
            self.width() - 40
        )
        panel_h = 92

        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(24, 24, 24)))
        painter.drawRect(int(x), int(y), int(panel_w), int(panel_h))

        painter.setBrush(QBrush(colour))
        painter.setPen(Qt.NoPen)
        painter.drawRect(int(x), int(y), 8, int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(
            int(x + 16),
            int(y + 22),
            "Channel Topology Status"
        )

        painter.setPen(QPen(colour, 1))
        painter.drawText(
            int(x + 16),
            int(y + 44),
            f"{status} | transitions={transitions} | counts={counts}"
        )

        painter.setPen(QPen(QColor(190, 190, 190), 1))
        painter.drawText(
            int(x + 16),
            int(y + 68),
            reason[:95]
        )

    def draw_full_view(self, painter):
        g = self.get_geometry()

        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(
            18,
            24,
            (
                f"REQUESTED: {self.geometry_source} | "
                f"ACTUAL: {g.get('source')} | "
                f"ORIGIN: {g.get('data_origin')} | "
                f"N={g.get('channel_count')} | "
                f"W={g.get('channel_width'):.6g} m | "
                f"H={g.get('channel_height'):.6g} m | "
                f"Rgas={g.get('gas_radius'):.6g} m | "
                f"X={g.get('selected_length'):.6g} m | "
                f"RSRC={g.get('profile_radius_source')} | "
                f"TBC={g.get('thermal_barrier_coating', 0.0):.3g} | "
                f"BOND={g.get('bond_coat', 0.0):.3g} | "
                f"LINER={g.get('liner', 0.0):.3g}"
            )
        )

        width = self.width()
        height = self.height()

        cx = width * 0.50
        cy = height * 0.52

        gas_radius = g["gas_radius"]
        wall = g["wall"]
        channel_height = g["channel_height"]
        jacket = g["jacket"]
        coating = g["coating"]

        channel_width = g["channel_width"]
        channel_count = g["channel_count"]

        wall_inner = gas_radius + coating
        wall_outer = wall_inner + wall
        channel_inner = wall_outer
        channel_outer = channel_inner + channel_height
        jacket_inner = channel_outer
        jacket_outer = jacket_inner + jacket

        outer_radius = jacket_outer

        # Use a full-engine reference envelope rather than auto-fitting every
        # local station. Otherwise the station slider appears broken because the
        # throat, mid-nozzle, and exit all expand to fill the same viewport.
        reference_radius = self.get_reference_gas_radius_for_view()

        reference_outer_radius = (
                reference_radius
                + coating
                + wall
                + channel_height
                + jacket
        )

        if reference_outer_radius <= 0:
            reference_outer_radius = max(outer_radius, 0.01)

        if self.scale_mode == "fit":
            scale = min(width * 0.72, height * 0.72) / (2.0 * outer_radius)
        else:
            scale = min(width * 0.72, height * 0.72) / (2.0 * reference_outer_radius)

        scale *= self.zoom_factor

        gas_px = gas_radius * scale

        coating_px = self.visible_layer_px(coating, scale, minimum_px=4.0)
        wall_inner_px = gas_px + coating_px
        wall_outer_px = wall_inner_px + max(wall * scale, 4.0)
        channel_inner_px = wall_outer_px
        channel_outer_px = channel_inner_px + max(channel_height * scale, 10.0)
        jacket_inner_px = channel_outer_px
        jacket_outer_px = jacket_inner_px + max(jacket * scale, 10.0)

        c = self.palette()
        background = c["background"]
        overlay = self.overlay_colours(g)

        gas_colour = overlay["gas"]
        wall_colour = overlay["wall"]
        coating_colour = overlay["coating"]
        channel_band_colour = overlay["channel_band"]
        channel_void_colour = overlay["channel_void"]
        jacket_colour = overlay["jacket"]

        self.draw_annular_layer(painter, cx, cy, jacket_outer_px, jacket_inner_px, jacket_colour, background)
        self.draw_annular_layer(painter, cx, cy, channel_outer_px, channel_inner_px, channel_band_colour, background)
        self.draw_annular_layer(painter, cx, cy, wall_outer_px, wall_inner_px, wall_colour, background)

        if coating > 0:
            self.draw_annular_layer(painter, cx, cy, wall_inner_px, gas_px, coating_colour, background)

        painter.setBrush(QBrush(gas_colour))
        painter.setPen(QPen(QColor(10, 10, 10), 2))
        painter.drawEllipse(QRectF(cx - gas_px, cy - gas_px, 2 * gas_px, 2 * gas_px))

        if channel_count > 0 and channel_width > 0:
            channel_mid_radius = channel_inner + 0.5 * channel_height
            channel_angle_width = channel_width / channel_mid_radius
            max_angle_width = (2.0 * math.pi / channel_count) * 0.95
            channel_angle_width = min(channel_angle_width, max_angle_width)

            painter.setPen(QPen(QColor(15, 15, 15), 1))
            painter.setBrush(QBrush(channel_void_colour))

            for i in range(channel_count):
                centre_angle = (2.0 * math.pi * i) / channel_count
                polygon = self.annular_sector_polygon(
                    cx,
                    cy,
                    channel_inner_px + 1.5,
                    channel_outer_px - 1.5,
                    centre_angle - 0.5 * channel_angle_width,
                    centre_angle + 0.5 * channel_angle_width,
                )
                painter.drawPolygon(polygon)

        self.draw_channel_topology_warning(
            painter,
            18,
            self.height() - 150
        )

        if self.show_station_inspector:
            self.draw_station_overlay_panel(
                painter,
                g,
                24,
                self.height() - 104,
                self.width() - 48
            )

        if self.show_legend:
            self.draw_legend(painter, 24, 28)
            self.draw_overlay_colour_key(painter, self.width() - 245, 18)

    def canvas_debug_source_text(self):
        g = self.get_geometry()
        return (
            f"{self.geometry_source} / actual={g.get('source')} / "
            f"N={g.get('channel_count')} / "
            f"w={g.get('channel_width')} / "
            f"h={g.get('channel_height')}"
        )

    def draw_detail_view(self, painter):
        g = self.get_geometry()

        width = self.width()
        height = self.height()
        c = self.palette()
        overlay = self.overlay_colours(g)

        channel_width = g["channel_width"] or 0.0
        requested_rib = g["requested_rib_width"] or 0.0
        effective_rib = g["effective_rib_width"]

        if effective_rib is None:
            effective_rib = requested_rib

        channel_height = g["channel_height"] or 0.0
        wall = g["wall"] or 0.0
        jacket = g["jacket"] or 0.0
        coating = g.get("coating", 0.0) or 0.0

        pitch = max(channel_width + max(effective_rib, 0.0), 1e-9)
        model_w = pitch * 4.0
        model_h = max(jacket + channel_height + wall + coating, 1e-9)

        drawing_w = width * 0.58
        drawing_h = height * 0.38

        scale = min(drawing_w / model_w, drawing_h / model_h) * self.zoom_factor

        jacket_h = max(34, jacket * scale)
        channel_h = max(56, channel_height * scale)
        wall_h = max(38, wall * scale)
        coating_h = self.visible_layer_px(coating, scale, minimum_px=7.0)

        channel_w = max(52, channel_width * scale)
        rib_w = max(38, effective_rib * scale)

        full_w = channel_w * 4.0 + rib_w * 3.0
        full_h = jacket_h + channel_h + wall_h + coating_h + 36

        base_x = width * 0.17
        top_y = height * 0.24

        y_jacket = top_y
        y_channel = y_jacket + jacket_h
        y_wall = y_channel + channel_h
        y_coating = y_wall + wall_h
        y_gas = y_coating + coating_h

        panel_x = base_x - 36
        panel_y = top_y - 72
        panel_w = full_w + 410
        panel_h = full_h + 245

        painter.setPen(QPen(QColor(210, 210, 210), 2))
        painter.setBrush(QBrush(QColor(32, 32, 32)))
        painter.drawRect(int(panel_x), int(panel_y), int(panel_w), int(panel_h))

        painter.setPen(QPen(QColor(245, 245, 245), 1))
        painter.drawText(
            int(base_x),
            int(panel_y + 30),
            "Unwrapped Regen Channel Detail at Selected Station"
        )

        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawText(
            int(base_x),
            int(panel_y + 50),
            "Flattened circumferential wall strip — full circular section shown in Full Cross-Section mode."
        )

        painter.setPen(QPen(QColor(10, 10, 10), 1))

        painter.setBrush(QBrush(overlay["jacket"]))
        painter.drawRect(int(base_x), int(y_jacket), int(full_w), int(jacket_h))

        painter.setBrush(QBrush(overlay["channel_band"]))
        painter.drawRect(int(base_x), int(y_channel), int(full_w), int(channel_h))

        painter.setBrush(QBrush(overlay["wall"]))
        painter.drawRect(int(base_x), int(y_wall), int(full_w), int(wall_h))

        if coating > 0:
            painter.setBrush(QBrush(overlay["coating"]))
            painter.drawRect(int(base_x), int(y_coating), int(full_w), int(coating_h))

        painter.setBrush(QBrush(overlay["gas"]))
        painter.drawRect(int(base_x), int(y_gas), int(full_w), 36)

        painter.setBrush(QBrush(overlay["channel_void"]))

        x = base_x
        first_channel_x = base_x
        first_rib_x = base_x + channel_w

        for _ in range(4):
            painter.drawRect(int(x), int(y_channel), int(channel_w), int(channel_h))
            x += channel_w + rib_w

        dim_pen = QPen(QColor(235, 235, 235), 1)
        guide_pen = QPen(QColor(150, 150, 150), 1, Qt.DashLine)
        text_pen = QPen(QColor(245, 245, 245), 1)

        def horizontal_dimension(x1, x2, y, label):
            painter.setPen(dim_pen)
            painter.drawLine(int(x1), int(y), int(x2), int(y))

            tick = 7
            painter.drawLine(int(x1), int(y - tick), int(x1), int(y + tick))
            painter.drawLine(int(x2), int(y - tick), int(x2), int(y + tick))

            painter.drawLine(int(x1), int(y), int(x1 + 7), int(y - 4))
            painter.drawLine(int(x1), int(y), int(x1 + 7), int(y + 4))
            painter.drawLine(int(x2), int(y), int(x2 - 7), int(y - 4))
            painter.drawLine(int(x2), int(y), int(x2 - 7), int(y + 4))

            painter.setPen(text_pen)
            painter.drawText(
                int((x1 + x2) / 2 - 72),
                int(y - 10),
                label
            )

        def vertical_dimension(x, y1, y2, label):
            painter.setPen(dim_pen)
            painter.drawLine(int(x), int(y1), int(x), int(y2))

            tick = 7
            painter.drawLine(int(x - tick), int(y1), int(x + tick), int(y1))
            painter.drawLine(int(x - tick), int(y2), int(x + tick), int(y2))

            painter.drawLine(int(x), int(y1), int(x - 4), int(y1 + 7))
            painter.drawLine(int(x), int(y1), int(x + 4), int(y1 + 7))
            painter.drawLine(int(x), int(y2), int(x - 4), int(y2 - 7))
            painter.drawLine(int(x), int(y2), int(x + 4), int(y2 - 7))

            painter.setPen(text_pen)
            painter.drawText(
                int(x + 16),
                int((y1 + y2) / 2 + 5),
                label
            )

        def callout(label, from_x, from_y, to_x, to_y):
            painter.setPen(guide_pen)
            painter.drawLine(int(from_x), int(from_y), int(to_x), int(to_y))

            painter.setPen(text_pen)
            painter.drawText(int(to_x + 8), int(to_y + 5), label)

        # Horizontal dimensions above channel band
        hdim_y_1 = y_channel - 28
        hdim_y_2 = y_channel - 52

        horizontal_dimension(
            first_channel_x,
            first_channel_x + channel_w,
            hdim_y_1,
            f"channel width = {channel_width:.6g} m"
        )

        horizontal_dimension(
            first_rib_x,
            first_rib_x + rib_w,
            hdim_y_2,
            f"rib width = {effective_rib:.6g} m"
        )

        # Vertical thickness dimensions, neatly aligned on right
        dim_x = base_x + full_w + 45
        label_gap = 46

        vertical_dimension(
            dim_x,
            y_jacket,
            y_jacket + jacket_h,
            f"outer jacket = {jacket:.6g} m"
        )

        vertical_dimension(
            dim_x + label_gap,
            y_channel,
            y_channel + channel_h,
            f"channel height = {channel_height:.6g} m"
        )

        vertical_dimension(
            dim_x + label_gap * 2,
            y_wall,
            y_wall + wall_h,
            f"hot-gas wall = {wall:.6g} m"
        )

        if coating > 0:
            vertical_dimension(
                dim_x + label_gap * 3,
                y_coating,
                y_coating + coating_h,
                f"coating = {coating:.6g} m"
            )

        # External callout labels
        callout(
            "outer jacket",
            base_x + full_w * 0.18,
            y_jacket + jacket_h * 0.50,
            base_x - 128,
            y_jacket + jacket_h * 0.45
        )

        callout(
            "coolant channel void",
            first_channel_x + channel_w * 0.50,
            y_channel + channel_h * 0.50,
            base_x - 155,
            y_channel + channel_h * 0.35
        )

        callout(
            "rib",
            first_rib_x + rib_w * 0.50,
            y_channel + channel_h * 0.50,
            base_x - 90,
            y_channel + channel_h * 0.82
        )

        callout(
            "hot-gas wall",
            base_x + full_w * 0.18,
            y_wall + wall_h * 0.50,
            base_x - 120,
            y_wall + wall_h * 0.55
        )

        if coating > 0:
            callout(
                "coating / liner",
                base_x + full_w * 0.18,
                y_coating + coating_h * 0.50,
                base_x - 130,
                y_coating + coating_h + 8
            )

        callout(
            "gas passage / bore",
            base_x + full_w * 0.18,
            y_gas + 18,
            base_x - 145,
            y_gas + 28
        )

        # Bottom status strip
        status_text = "VALID" if g.get("channel_geometry_valid") == 1.0 else "INVALID"

        painter.setPen(QPen(QColor(210, 210, 210), 1))
        painter.drawLine(
            int(base_x),
            int(y_gas + 58),
            int(base_x + full_w),
            int(y_gas + 58)
        )

        painter.setPen(text_pen)
        painter.drawText(
            int(base_x),
            int(y_gas + 70),
            f"Selected station: {g.get('selected_length', 0.0):.6g} m     "
            f"Requested pitch: {g.get('requested_pitch', 0.0):.6g} m     "
            f"Available pitch: {g.get('available_pitch', 0.0):.6g} m     "
            f"Geometry: {status_text}"
        )

        self.draw_station_minimap(
            painter,
            g,
            panel_x + 16,
            panel_y + panel_h - 234,
            panel_w - 32
        )

        self.draw_station_overlay_panel(
            painter,
            g,
            panel_x + 16,
            panel_y + panel_h - 146,
            panel_w - 32
        )

        if self.show_legend:
            self.draw_legend(painter, 24, 28)
            self.draw_overlay_colour_key(painter, self.width() - 245, 18)

    def draw_legend(self, painter, x, y):
        c = self.palette()

        items = [
            ("Gas passage / bore", c["gas"]),
            ("Coating / liner", c["coating"]),
            ("Hot-gas wall", c["hot_wall"]),
            ("Coolant channel void", c["coolant_void"]),
            ("Rib/channel band", c["channel_band"]),
            ("Outer jacket", c["outer_jacket"]),
        ]

        painter.setPen(QPen(c["text"], 1))
        painter.drawText(x, y, "Legend")

        y += 16

        for label, colour in items:
            painter.setBrush(QBrush(colour))
            painter.setPen(QPen(QColor(10, 10, 10), 1))
            painter.drawRect(x, y, 14, 14)

            painter.setPen(QPen(c["text"], 1))
            painter.drawText(x + 22, y + 12, label)

            y += 22



# Phase 16P.8 fallback for missing Phase 16N.7 apply owner.


def fallback_apply_geometry_result_phase_16p8(results):
    """
    Phase 16P.8
    Local fallback apply-geometry owner used when the older 16N.7 owner
    function is unavailable.
    """
    if not isinstance(results, dict):
        return results

    staged = (
        results.get("regen_geometry_commit_staged_geometry")
        or results.get("regen_autonomous_geometry_staged_candidate", {}).get("staged_geometry")
        or results.get("regen_geometry_commit_candidate_geometry")
        or results.get("regen_viewer_accepted_geometry")
        or {}
    )

    if not isinstance(staged, dict) or not staged:
        results["phase_16n7_apply_geometry_status"] = (
            "FAIL_APPLY_GEOMETRY_NO_STAGED_GEOMETRY_PHASE_16P8"
        )
        results["phase_16n7_geometry_applied"] = False
        return results

    applied = dict(staged)

    results["regen_ui_applied_geometry"] = applied
    results["regen_current_geometry"] = applied
    results["regen_viewer_accepted_geometry"] = applied
    results["phase_16n7_apply_geometry_status"] = (
        "PASS_APPLY_GEOMETRY_RECORDED_PHASE_16P8"
    )
    results["phase_16n7_geometry_applied"] = True
    results["phase_16p8_apply_geometry_fallback_used"] = True
    results["phase_16p8_apply_geometry_applied_keys"] = sorted(applied.keys())

    return results




# Phase 16P.9 fallback for missing Phase 16N.8 solver-regeneration request owner.


def fallback_solver_regeneration_request_phase_16p9(results):
    """
    Phase 16P.9
    Local fallback solver-regeneration request owner used when the older 16N.8
    owner function is unavailable.
    """
    if not isinstance(results, dict):
        return results

    geometry = (
        results.get("regen_ui_applied_geometry")
        or results.get("regen_current_geometry")
        or results.get("regen_viewer_accepted_geometry")
        or {}
    )

    results["phase_16n8_solver_regeneration_request_status"] = (
        "PASS_SOLVER_REGENERATION_REQUEST_RECORDED_PHASE_16P9"
    )
    results["phase_16n8_solver_regeneration_requested"] = True
    results["phase_16p9_solver_regeneration_fallback_used"] = True
    results["phase_16p9_solver_regeneration_requested_geometry"] = dict(geometry)

    return results



# Phase 16P.10 global missing-owner safety net.
# Prevents legacy optional owner hooks from raising NameError at runtime.


def fallback_before_after_comparison_phase_16p10(results):
    """
    Phase 16P.10
    Local fallback before/after comparison owner used when legacy 16N.9 owner
    function is unavailable.
    """
    if not isinstance(results, dict):
        return results

    before_geometry = (
        results.get("phase_16p4d_live_ui_acceptance_before_geometry")
        or results.get("regen_manual_geometry")
        or {}
    )

    after_geometry = (
        results.get("regen_ui_applied_geometry")
        or results.get("regen_current_geometry")
        or results.get("regen_viewer_accepted_geometry")
        or {}
    )

    changed = {}

    keys = sorted(set(before_geometry.keys()) | set(after_geometry.keys()))

    for key in keys:
        if before_geometry.get(key) != after_geometry.get(key):
            changed[key] = {
                "before": before_geometry.get(key),
                "after": after_geometry.get(key),
            }

    results["phase_16n9_before_after_comparison_status"] = (
        "PASS_BEFORE_AFTER_COMPARISON_AVAILABLE_PHASE_16P10"
    )
    results["phase_16n9_before_after_comparison_available"] = True
    results["phase_16p10_before_after_fallback_used"] = True
    results["phase_16p10_before_after_changed_fields"] = changed
    results["phase_16p10_before_after_changed_field_count"] = len(changed)

    return results



class RegenCrossSectionViewer(QDialog):
    def __init__(self, results, parent=None, regeneration_callback=None):
        super().__init__(parent)

        self.results = results or {}
        self.regeneration_callback = regeneration_callback

        # Feature 1 — generic runtime task reference only.
        # Engineering execution remains outside the viewer.
        self._regen_geometry_material_background_task = None
        self._regen_geometry_material_before_results = None

        self.results.setdefault("regen_viewer_geometry_acceptance_history", [])
        self.results.setdefault("regen_viewer_accepted_geometry", {})
        self.results.setdefault("regen_viewer_rollback_geometry", {})
        self.results.setdefault("regen_viewer_rejected_geometry", {})
        self.results.setdefault("regen_viewer_geometry_acceptance_status", "NO_ACTION")

        self.setWindowTitle("Regen Cross-Section Viewer")
        self.setMinimumSize(1000, 650)
        self.resize(1150, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.status_strip = QLabel()
        self.status_strip.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.status_strip.setFixedHeight(28)
        self.status_strip.setWordWrap(False)
        self.configure_status_strip()

        self.canvas = RegenCrossSectionCanvas(self.results)

        # RDSI 3J
        # Preserve the actual manual geometry built by this viewer in the
        # existing result/project engineering state. No separate persistence
        # system is introduced.
        manual_geometry_snapshot = (
            self.get_current_manual_geometry_snapshot()
        )

        if manual_geometry_snapshot:
            self.results[
                "regen_viewer_manual_geometry_snapshot"
            ] = dict(
                manual_geometry_snapshot
            )

        controls = self.build_controls()
        body = self.build_body()

        layout.addWidget(self.status_strip)
        layout.addLayout(controls)
        layout.addLayout(body)
        self.set_geometry_source("manual")
        self.set_selected_station_length(
            self.safe_float(self.results.get("regen_viewer_selected_length"), 0.0),
            source="initialise"
        )

        self.refresh_scale_button_styles()

        # RH2B-R1 — canonical consolidated viewer initialization

        # Production manufacturability presentation.
        # This was previously installed by the Phase16Q5
        # runtime __init__ wrapper.
        try:
            self.phase_16q5_manufacturability_label = QLabel(
                "MANUFACTURABILITY: NOT CHECKED"
            )

            inserted = False

            for attr in (
                "button_row",
                "controls_layout",
                "top_controls_layout",
                "main_controls_layout",
                "layout",
                "main_layout",
            ):
                target_layout = getattr(
                    self,
                    attr,
                    None,
                )

                if (
                    target_layout is not None
                    and
                    hasattr(
                        target_layout,
                        "addWidget",
                    )
                ):
                    target_layout.addWidget(
                        self.phase_16q5_manufacturability_label
                    )

                    inserted = True
                    break

            self.results[
                "phase_16q5_manufacturability_label_attached"
            ] = inserted

        except Exception as exc:
            self.results[
                "phase_16q5_manufacturability_label_error"
            ] = str(exc)

        # Canonical full-engine side-profile presentation.
        # Runtime __init__ replacement is no longer required.
        _canonical_side_profile_update_overlay(
            self
        )

    def build_controls(self):
        """
        Compact top toolbar.

        The old version placed almost every feature as a button in the main
        toolbar. This version keeps the top bar for global navigation only,
        while detailed controls move to the right-side inspector tabs.
        """

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(4, 4, 4, 4)
        outer_layout.setSpacing(3)

        view_layout = QHBoxLayout()
        view_layout.setContentsMargins(0, 0, 0, 0)
        view_layout.setSpacing(4)

        self.view_selector = QComboBox()
        self.view_selector.addItem(
            "Full Section",
            "full",
        )
        self.view_selector.addItem(
            "Channel Detail",
            "detail",
        )
        self.view_selector.setCurrentIndex(0)
        self.view_selector.setFixedWidth(145)
        self.view_selector.setFixedHeight(30)
        self.view_selector.setToolTip(
            "Choose the Regen cross-section presentation."
        )
        self.regen_design_mode_selector = QComboBox()
        self.regen_design_mode_selector.addItems([
            "Manual",
            "Automatic — Selected Material",
            "Automatic — Geometry + Materials",
        ])
        self.regen_design_mode_selector.setCurrentText("Manual")
        self.regen_design_mode_selector.setMinimumWidth(185)
        self.regen_design_mode_selector.setToolTip(
            "Choose the Regen design strategy. "
            "Manual performs no automatic generation. "
            "Automatic — Selected Material searches geometry while preserving "
            "the currently selected liner material. "
            "Automatic — Geometry + Materials searches both manufacturable "
            "geometry and eligible material choices through the canonical "
            "qualified-candidate pipeline."
        )

        self.generated_design_selector = QComboBox()
        self.generated_design_selector.setMinimumWidth(260)
        self.generated_design_selector.setToolTip(
            "Select from canonically qualified and ranked Regen "
            "designs. Rank 1 is LEAF's recommended design. "
            "Changing this control does not apply geometry or run "
            "the solver."
        )

        self.automatic_button = QPushButton("Generate")

        self.accept_automatic_button = QPushButton("Accept Automatic")
        self.reject_automatic_button = QPushButton("Reject Automatic")
        self.accept_automatic_button.setVisible(False)
        self.reject_automatic_button.setVisible(False)
        self.accept_automatic_button.setToolTip("Hidden production control. Acceptance is handled by Generate Automatic Geometry.")
        self.reject_automatic_button.setToolTip("Hidden production control. Rejection is handled by changing/rolling back geometry.")
        self.rollback_geometry_button = QPushButton("Rollback Geometry")
        pass

        self.scale_selector = QComboBox()
        self.scale_selector.addItem(
            "Fit",
            "fit",
        )
        self.scale_selector.addItem(
            "True Scale",
            "true",
        )
        self.scale_selector.setCurrentIndex(0)
        self.scale_selector.setFixedWidth(110)
        self.scale_selector.setFixedHeight(30)
        self.scale_selector.setToolTip(
            "Choose fitted or true-reference drawing scale."
        )

        toolbar_buttons = [
            self.automatic_button,
        ]

        for button in toolbar_buttons:
            button.setCheckable(False)
            button.setAutoDefault(False)
            button.setDefault(False)
            button.setFixedHeight(24)
            button.setMinimumWidth(0)

        for button in toolbar_buttons:
            button.setFixedHeight(24)
            button.setMinimumWidth(0)

        self.profile_selector = QComboBox()
        self.profile_selector.setMinimumWidth(170)
        self.profile_selector.setToolTip(
            "Selects which axial station dataset is sampled. "
            "This affects station values and may affect geometry only if that profile contains different radius/area/channel data."
        )

        for key, label in self.canvas.available_station_profiles().items():
            self.profile_selector.addItem(label, key)

        view_layout.addWidget(QLabel("View"))
        view_layout.addWidget(self.view_selector)

        view_layout.addSpacing(16)
        view_layout.addWidget(QLabel("Design Mode"))
        view_layout.addWidget(self.regen_design_mode_selector)
        view_layout.addWidget(QLabel("Candidate"))
        view_layout.addWidget(self.generated_design_selector)
        view_layout.addWidget(self.automatic_button)

        # Production UI: accept/reject are hidden compatibility controls.
        # Automatic Geometry now owns the recommendation/apply workflow.
        view_layout.addWidget(self.rollback_geometry_button)
        pass

        pass
        pass
        pass

        view_layout.addSpacing(16)
        profile_label = QLabel("Profile")
        profile_label.setToolTip(
            "Station data source. This is not the same as Manual/Recommended geometry."
        )

        view_layout.addWidget(profile_label)
        view_layout.addWidget(self.profile_selector)

        view_layout.addSpacing(16)
        view_layout.addWidget(QLabel("Scale"))
        view_layout.addWidget(self.scale_selector)
        view_layout.addStretch()

        station_layout = QHBoxLayout()
        station_layout.setContentsMargins(0, 0, 0, 0)
        station_layout.setSpacing(4)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(40)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(105)
        self.zoom_slider.setFixedHeight(22)

        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setFixedWidth(72)
        self.zoom_label.setFixedHeight(22)

        self.station_slider = QSlider(Qt.Horizontal)

        self.station_slider.setMinimum(0)

        self.station_slider.setMaximum(1000)

        self.station_slider.setSingleStep(1)

        self.station_slider.setPageStep(10)

        self.station_slider.setTracking(True)

        self.station_slider.setMinimumWidth(260)
        self.station_slider.setFixedHeight(22)

        self.station_spinbox = QDoubleSpinBox()

        self.station_spinbox.setDecimals(5)

        self.station_spinbox.setRange(
            0.0,
            self.get_effective_nozzle_length()
        )

        self.station_spinbox.setSingleStep(0.001)

        # CRITICAL FIX
        self.station_spinbox.setKeyboardTracking(False)

        # CRITICAL FIX
        self.station_spinbox.setFocusPolicy(Qt.ClickFocus)

        # CRITICAL FIX
        self.station_spinbox.clearFocus()

        # DO NOT USE valueChanged
        self.station_spinbox.editingFinished.connect(
            self.on_station_spinbox_editing_finished
        )

        nozzle_length = self.safe_float(self.results.get("nozzle_length"), 0.0)
        self.station_spinbox.setMinimum(0.0)
        effective_length = self.get_effective_nozzle_length()

        self.station_spinbox.setMaximum(
            max(effective_length, 0.001)
        )

        self.station_label = QLabel("Station: 0.0000 m")
        self.station_label.setFixedWidth(150)
        self.station_label.setFixedHeight(22)

        station_layout.addWidget(QLabel("Station"))
        station_layout.addWidget(self.station_slider, stretch=3)
        station_layout.addWidget(self.station_spinbox)
        station_layout.addWidget(self.station_label)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        station_layout.addWidget(divider)

        station_layout.addWidget(QLabel("Zoom"))
        station_layout.addWidget(self.zoom_slider, stretch=1)
        station_layout.addWidget(self.zoom_label)

        self.view_selector.currentIndexChanged.connect(
            lambda _index: self.set_view_mode(
                str(
                    self.view_selector.currentData()
                    or
                    "full"
                )
            )
        )
        self.regen_design_mode_selector.currentTextChanged.connect(
            self.set_regen_design_mode
        )

        self.generated_design_selector.currentIndexChanged.connect(
            self.set_generated_design_selection
        )

        self.automatic_button.clicked.connect(
            lambda checked=False: self.execute_selected_regen_design_mode()
        )

        self.refresh_generated_design_selector()
        self.force_enable_automatic_geometry_button_phase_16p7c()

        self.accept_automatic_button.clicked.connect(self.accept_automatic_geometry)
        self.reject_automatic_button.clicked.connect(self.reject_automatic_geometry)
        self.rollback_geometry_button.clicked.connect(self.rollback_accepted_geometry)
        self.refresh_rollback_geometry_button_state()
        pass

        self.refresh_cross_section_live_feed_validation_phase_16n4()
        self.refresh_automatic_geometry_button_state_phase_16n2()
        self.force_enable_automatic_geometry_button_phase_16p7c()
        self.scale_selector.currentIndexChanged.connect(
            lambda _index: (
                self.fit_to_window()
                if
                self.scale_selector.currentData()
                ==
                "fit"
                else
                self.set_true_scale_mode()
            )
        )
        self.profile_selector.currentIndexChanged.connect(self.on_profile_changed)

        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.station_slider.valueChanged.connect(self.on_station_slider_changed)

        outer_layout.addLayout(view_layout)
        outer_layout.addLayout(station_layout)

        return outer_layout

    def update_overlay_button_styles(self):
        buttons = {
            "geometry": self.geometry_overlay_button,
            "gas": self.gas_overlay_button,
            "thermal": self.thermal_overlay_button,
            "coolant": self.coolant_overlay_button,
            "validation": self.validation_overlay_button,
        }

        active_style = """
            QPushButton {
                background-color: #2f5f8f;
                color: white;
                font-weight: bold;
                border: 1px solid #6fa8dc;
                padding: 4px 8px;
            }
        """

        inactive_style = """
            QPushButton {
                background-color: #3a3a3a;
                color: #dddddd;
                border: 1px solid #555555;
                padding: 4px 8px;
            }
        """

        for mode, button in buttons.items():
            if self.canvas.overlay_mode == mode:
                button.setStyleSheet(active_style)
            else:
                button.setStyleSheet(inactive_style)

    def refresh_cross_section_live_feed_validation_phase_16n4(self):
        """
        Phase 16N.4B
        Record whether cross-section viewer live-feed payloads are present.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return

        if RegenCrossSectionLiveFeedValidatorPhase16N4 is None:
            self.results["phase_16n4_cross_section_live_feed_status"] = (
                "WARN_CROSS_SECTION_LIVE_FEED_VALIDATOR_IMPORT_FAILED_PHASE_16N4"
            )
            return

        validator = RegenCrossSectionLiveFeedValidatorPhase16N4()
        result = validator.validate(self.results)

        self.results["phase_16n4_cross_section_live_feed_status"] = result.status
        self.results["phase_16n4_cross_section_manual_geometry_present"] = (
            result.manual_geometry_present
        )
        self.results["phase_16n4_cross_section_automatic_geometry_present"] = (
            result.automatic_geometry_present
        )
        self.results["phase_16n4_cross_section_recommendation_present"] = (
            result.recommendation_present
        )
        self.results["phase_16n4_cross_section_button_state_present"] = (
            result.button_state_present
        )
        self.results["phase_16n4_cross_section_live_feed_notes"] = list(result.notes)


    def canonical_generated_design_candidates(self):
        """
        Return the canonical qualified ranked candidate population.

        The viewer does not qualify, score, or sort candidates.
        Ordering is owned by regen_candidate_ranking_owner.
        """
        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return []

        ranked = self.results.get(
            "regen_candidate_ranked_population"
        )

        if not isinstance(
            ranked,
            list,
        ):
            return []

        return [
            candidate
            for candidate in ranked
            if (
                isinstance(
                    candidate,
                    dict,
                )
                and
                candidate.get(
                    "candidate_id"
                )
            )
        ]

    def refresh_generated_design_selector(self):
        """
        Populate Generated Design from canonical ranking output only.

        Failed and UNPROVEN candidates live in diagnostic populations and
        never enter this control.
        """
        selector = getattr(
            self,
            "generated_design_selector",
            None,
        )

        if selector is None:
            return False

        ranked = (
            self.canonical_generated_design_candidates()
        )

        previous_requested = None

        if isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            previous_requested = (
                self.results.get(
                    "regen_candidate_selector_requested_candidate_id"
                )
            )

        selector.blockSignals(
            True
        )

        selector.clear()

        if not ranked:
            selector.addItem(
                "No feasible designs",
                None,
            )

            selector.setEnabled(
                False
            )

            selector.setCurrentIndex(
                0
            )

            selector.blockSignals(
                False
            )

            if isinstance(
                getattr(
                    self,
                    "results",
                    None,
                ),
                dict,
            ):
                self.results[
                    "regen_candidate_selector_requested_candidate_id"
                ] = None

                self.results[
                    "regen_generated_design_dropdown_status"
                ] = "NO_FEASIBLE_DESIGNS"

                self.results[
                    "regen_generated_design_dropdown_count"
                ] = 0

            self.set_generated_design_selection(
                0
            )

            return False

        requested_index = None

        for index, candidate in enumerate(
            ranked
        ):
            candidate_id = str(
                candidate.get(
                    "candidate_id"
                )
            )

            rank = candidate.get(
                "candidate_rank",
                index + 1,
            )

            if index == 0:
                label = (
                    f"Recommended — Rank {rank} — "
                    f"{candidate_id}"
                )
            else:
                label = (
                    f"Rank {rank} — "
                    f"{candidate_id}"
                )

            selector.addItem(
                label,
                candidate_id,
            )

            if (
                previous_requested is not None
                and
                str(
                    previous_requested
                )
                ==
                candidate_id
            ):
                requested_index = index

        selector.setEnabled(
            True
        )

        selector.setCurrentIndex(
            (
                requested_index
                if requested_index
                is not None
                else 0
            )
        )

        selector.blockSignals(
            False
        )

        if isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            self.results[
                "regen_generated_design_dropdown_status"
            ] = "QUALIFIED_DESIGNS_AVAILABLE"

            self.results[
                "regen_generated_design_dropdown_count"
            ] = len(
                ranked
            )

        return self.set_generated_design_selection(
            selector.currentIndex()
        )

    def set_generated_design_selection(
            self,
            index,
    ):
        """
        Record a Generated Design request through the canonical selector.

        This method performs no application, staging, solver execution,
        live commit, or engineering qualification.
        """
        selector = getattr(
            self,
            "generated_design_selector",
            None,
        )

        if (
            selector is None
            or
            not isinstance(
                getattr(
                    self,
                    "results",
                    None,
                ),
                dict,
            )
        ):
            return False

        candidate_id = (
            selector.itemData(
                index
            )
            if (
                isinstance(
                    index,
                    int,
                )
                and
                0 <= index
                < selector.count()
            )
            else None
        )

        self.results[
            "regen_candidate_selector_requested_candidate_id"
        ] = candidate_id

        self.results[
            "regen_generated_design_selection_source"
        ] = "REGEN_VIEWER_GENERATED_DESIGN_CONTROL"

        try:
            from leaf_qt.regen_candidate_selector import (
                attach_regen_candidate_selector,
            )

            self.results = (
                attach_regen_candidate_selector(
                    self.results
                )
            )

        except Exception as exc:
            self.results[
                "regen_generated_design_selection_status"
            ] = "ERROR_CANONICAL_SELECTOR"

            self.results[
                "regen_generated_design_selection_error"
            ] = str(
                exc
            )

            return False

        resolved_id = self.results.get(
            "regen_candidate_selector_user_selected_candidate_id"
        )

        canonical_status = self.results.get(
            "regen_candidate_selector_user_selection_status"
        )

        if candidate_id is None:
            self.results[
                "regen_generated_design_selection_status"
            ] = "NO_FEASIBLE_DESIGN_SELECTED"

            return False

        selected = (
            str(
                resolved_id
            )
            ==
            str(
                candidate_id
            )
        )

        self.results[
            "regen_generated_design_selection_status"
        ] = (
            "QUALIFIED_GENERATED_DESIGN_SELECTED"
            if selected
            else
            "BLOCKED_GENERATED_DESIGN_SELECTION"
        )

        self.results[
            "regen_generated_design_selected_candidate_id"
        ] = (
            resolved_id
            if selected
            else None
        )

        self.results[
            "regen_generated_design_canonical_selector_status"
        ] = canonical_status

        return selected

    def prepare_selected_generated_design_for_execution(self):
        """
        Rebind the explicitly selected qualified design through the existing
        non-destructive application and staging owners.

        No solver is run here. No live geometry is modified here.
        """
        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return False

        requested_id = self.results.get(
            "regen_candidate_selector_requested_candidate_id"
        )

        if not requested_id:
            return False

        try:
            from leaf_qt.regen_candidate_selector import (
                attach_regen_candidate_selector,
            )
            from leaf_qt.regen_candidate_application_owner import (
                attach_regen_candidate_application_owner,
            )
            from leaf_qt.regen_autonomous_geometry_commit_controller import (
                attach_regen_autonomous_geometry_commit_controller,
            )
            from leaf_qt.regen_autonomous_geometry_commit_history_owner import (
                attach_regen_autonomous_geometry_commit_history_owner,
            )
            from leaf_qt.regen_autonomous_geometry_commit_report_owner import (
                attach_regen_autonomous_geometry_commit_report_owner,
            )
            from leaf_qt.regen_autonomous_geometry_commit_master_gate import (
                attach_regen_autonomous_geometry_commit_master_gate,
            )

            for owner in (
                attach_regen_candidate_selector,
                attach_regen_candidate_application_owner,
                attach_regen_autonomous_geometry_commit_controller,
                attach_regen_autonomous_geometry_commit_history_owner,
                attach_regen_autonomous_geometry_commit_report_owner,
                attach_regen_autonomous_geometry_commit_master_gate,
            ):
                self.results = owner(
                    self.results
                )

        except Exception as exc:
            message = (
                "Generated Design could not be prepared through "
                "the canonical application/staging chain: "
                f"{exc}"
            )

            self.results[
                "regen_generated_design_execution_prepare_status"
            ] = "ERROR_CANONICAL_OWNER_CHAIN"

            self.results[
                "regen_generated_design_execution_prepare_message"
            ] = message

            self.notify_automatic_geometry_failure(
                message
            )

            return False

        selected_id = self.results.get(
            "regen_candidate_selector_user_selected_candidate_id"
        )

        patch = self.results.get(
            "regen_candidate_application_patch"
        )

        if not isinstance(
            patch,
            dict,
        ):
            patch = {}

        patch_id = patch.get(
            "candidate_id"
        )

        staged = (
            self.get_staged_automatic_geometry()
        )

        ready = bool(
            selected_id
            and
            str(
                selected_id
            )
            ==
            str(
                requested_id
            )
            and
            patch_id
            and
            str(
                patch_id
            )
            ==
            str(
                requested_id
            )
            and
            self.results.get(
                "regen_candidate_application_ready"
            )
            is True
            and
            self.results.get(
                "regen_candidate_geometry_application_allowed"
            )
            is True
            and
            self.results.get(
                "regen_autonomous_geometry_commit_ready"
            )
            is True
            and
            self.results.get(
                "regen_autonomous_geometry_commit_master_gate_ready"
            )
            is True
            and
            isinstance(
                staged,
                dict,
            )
            and
            bool(
                staged
            )
        )

        self.results[
            "regen_generated_design_execution_prepare_status"
        ] = (
            "PASS_SELECTED_GENERATED_DESIGN_STAGED"
            if ready
            else
            "FAIL_SELECTED_GENERATED_DESIGN_STAGING"
        )

        self.results[
            "regen_generated_design_execution_candidate_id"
        ] = (
            requested_id
            if ready
            else None
        )

        if not ready:
            message = (
                "The selected Generated Design could not be safely "
                "staged through the canonical application/commit chain."
            )

            self.results[
                "regen_generated_design_execution_prepare_message"
            ] = message

            self.notify_automatic_geometry_failure(
                message
            )

        return ready

    def current_regen_design_mode(self):
        """Return the viewer-selected Regen design strategy."""

        selector = getattr(
            self,
            "regen_design_mode_selector",
            None,
        )

        label = (
            selector.currentText()
            if selector is not None
            else
            self.results.get(
                "regen_design_mode_label",
                "Manual",
            )
        )

        normalised = str(
            label
        ).strip()

        if (
            normalised
            ==
            "Automatic — Selected Material"
        ):
            return (
                "automatic_selected_material"
            )

        if (
            normalised
            ==
            "Automatic — Geometry + Materials"
        ):
            return (
                "automatic_geometry_materials"
            )

        return "manual"


    def sync_regen_design_mode_controls(self):
        """Synchronise controls with the selected design strategy."""

        mode = (
            self.current_regen_design_mode()
        )

        selected_material_mode = (
            mode
            ==
            "automatic_selected_material"
        )

        geometry_material_mode = (
            mode
            ==
            "automatic_geometry_materials"
        )

        automatic_mode = (
            selected_material_mode
            or
            geometry_material_mode
        )

        task = getattr(
            self,
            "_regen_geometry_material_background_task",
            None,
        )

        background_running = bool(
            task is not None
            and
            getattr(
                task,
                "running",
                False,
            )
        )

        button = getattr(
            self,
            "automatic_button",
            None,
        )

        if button is not None:
            button.setText(
                "Generating…"
                if background_running
                else
                "Generate"
            )

            button.setEnabled(
                automatic_mode
                and
                not background_running
            )

            if geometry_material_mode:
                button.setToolTip(
                    "Generate a qualified Regen design by searching "
                    "manufacturable geometry and eligible material choices. "
                    "The search runs in LEAF's background runtime owner."
                )

            elif selected_material_mode:
                button.setToolTip(
                    "Generate Regen geometry using the canonical automatic "
                    "candidate pipeline while preserving the currently "
                    "selected material."
                )

            else:
                button.setToolTip(
                    "Manual design mode is active. Select an Automatic "
                    "design strategy to generate a candidate Regen design."
                )

        selector = getattr(
            self,
            "regen_design_mode_selector",
            None,
        )

        if selector is not None:
            selector.setEnabled(
                not background_running
            )

        if isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            self.results[
                "regen_design_mode"
            ] = mode

            if geometry_material_mode:
                label = (
                    "Automatic — Geometry + Materials"
                )

                strategy = (
                    "AUTOMATIC_GEOMETRY_AND_MATERIALS"
                )

                self.results[
                    "regen_candidate_design_mode"
                ] = (
                    "GEOMETRY_AND_MATERIALS"
                )

            elif selected_material_mode:
                label = (
                    "Automatic — Selected Material"
                )

                strategy = (
                    "AUTOMATIC_GEOMETRY_SELECTED_MATERIAL"
                )

                self.results[
                    "regen_candidate_design_mode"
                ] = (
                    "SELECTED_MATERIAL"
                )

            else:
                label = "Manual"
                strategy = "MANUAL_INPUTS"

                self.results.pop(
                    "regen_candidate_design_mode",
                    None,
                )

            self.results[
                "regen_design_mode_label"
            ] = label

            self.results[
                "regen_design_mode_strategy"
            ] = strategy

            self.results[
                "regen_design_mode_generate_enabled"
            ] = (
                automatic_mode
                and
                not background_running
            )

            self.results[
                "regen_geometry_material_background_running"
            ] = (
                background_running
            )

        return (
            automatic_mode
            and
            not background_running
        )


    @staticmethod
    def regen_design_mode_status_keys():
        """Status fields whose presentation must remain local to a design mode."""

        return (
            "regen_overall_status",
            "overall_status",
            "regen_geometry_status",
            "geometry_status",
            "regen_thermal_status",
            "thermal_status",
            "regen_coolant_status",
            "coolant_status",
            "regen_material_status",
            "material_status",
            "source_validation_mode",
        )


    def capture_regen_design_mode_status_snapshot(
            self,
            mode,
    ):
        """Capture the currently displayed engineering status for one mode."""

        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return {}

        mode = str(
            mode
            or
            ""
        ).strip()

        if not mode:
            return {}

        snapshots = getattr(
            self,
            "_regen_design_mode_status_snapshots",
            None,
        )

        if not isinstance(
            snapshots,
            dict,
        ):
            snapshots = {}

            self._regen_design_mode_status_snapshots = (
                snapshots
            )

        snapshot = {
            key:
                self.results.get(
                    key
                )
            for key in (
                self.regen_design_mode_status_keys()
            )
            if key in self.results
        }

        snapshots[
            mode
        ] = snapshot

        return dict(
            snapshot
        )


    def restore_regen_design_mode_status_snapshot(
            self,
            mode,
    ):
        """Restore one mode's status without altering its engineering geometry."""

        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return False

        snapshots = getattr(
            self,
            "_regen_design_mode_status_snapshots",
            None,
        )

        if not isinstance(
            snapshots,
            dict,
        ):
            return False

        snapshot = snapshots.get(
            str(
                mode
                or
                ""
            ).strip()
        )

        if not isinstance(
            snapshot,
            dict,
        ):
            return False

        for key in (
            self.regen_design_mode_status_keys()
        ):
            self.results.pop(
                key,
                None,
            )

        self.results.update(
            snapshot
        )

        return True


    def set_regen_design_mode(
            self,
            label,
    ):
        """Select a Regen strategy without executing engineering work."""

        normalised_label = str(
            label
        ).strip()

        if (
            normalised_label
            ==
            "Automatic — Selected Material"
        ):
            mode = (
                "automatic_selected_material"
            )

        elif (
            normalised_label
            ==
            "Automatic — Geometry + Materials"
        ):
            mode = (
                "automatic_geometry_materials"
            )

        else:
            mode = "manual"
            normalised_label = "Manual"

        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            self.results = {}

        previous_mode = str(
            self.results.get(
                "regen_design_mode"
            )
            or
            "manual"
        ).strip()

        # Capture the outgoing mode BEFORE changing presentation state.
        self.capture_regen_design_mode_status_snapshot(
            previous_mode
        )

        self.results[
            "regen_design_mode"
        ] = mode

        self.results[
            "regen_design_mode_label"
        ] = normalised_label

        self.results[
            "regen_design_mode_selection_status"
        ] = (
            "SELECTED_NO_EXECUTION"
        )

        # If this mode has previously been evaluated, restore its own
        # status identity. Otherwise the current engineering status is
        # retained until that mode is generated/evaluated.
        self.restore_regen_design_mode_status_snapshot(
            mode
        )

        if mode == "manual":
            self.results[
                "regen_design_mode_generation_state"
            ] = (
                "MANUAL"
            )

            restored = (
                self.select_manual_geometry()
            )

            if not restored:
                self.results[
                    "regen_design_mode_selection_status"
                ] = (
                    "MANUAL_RESTORE_FAILED"
                )

        else:
            self.results[
                "regen_design_mode_generation_state"
            ] = (
                "NOT_GENERATED"
            )

            if (
                mode
                ==
                "automatic_geometry_materials"
            ):
                self.results[
                    "regen_geometry_material_display_geometry"
                ] = {}

            self.set_geometry_source(
                "automatic"
            )

        self.sync_regen_design_mode_controls()

        try:
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()

        except Exception:
            pass

        return mode




    def capture_regen_candidate_population_for_strategy(
            self,
            mode,
    ):
        """
        Preserve the candidate population under the exact Regen design
        strategy that produced it.

        This is presentation/analysis provenance only. Candidate feasibility,
        qualification and ranking remain owned by the existing Regen systems.
        """
        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return False

        strategy_labels = {
            "automatic_selected_material":
                "Automatic — Selected Material",

            "automatic_geometry_materials":
                "Automatic — Geometry + Materials",
        }

        strategy_label = (
            strategy_labels.get(
                str(
                    mode
                )
            )
        )

        if not strategy_label:
            return False

        populations = self.results.get(
            "regen_candidate_populations_by_strategy"
        )

        if not isinstance(
            populations,
            dict,
        ):
            populations = {}

        def candidate_copies(
            value,
        ):
            if not isinstance(
                value,
                list,
            ):
                return []

            copied = []

            for candidate in value:

                if not isinstance(
                    candidate,
                    dict,
                ):
                    continue

                item = dict(
                    candidate
                )

                item[
                    "regen_design_strategy"
                ] = str(
                    mode
                )

                item[
                    "regen_design_strategy_label"
                ] = strategy_label

                copied.append(
                    item
                )

            return copied

        ranked = candidate_copies(
            self.results.get(
                "regen_candidate_ranked_population",
                [],
            )
        )

        evaluated = candidate_copies(
            self.results.get(
                "regen_candidate_evaluated_population",
                [],
            )
        )

        display_geometry = {}

        if (
            mode
            ==
            "automatic_geometry_materials"
        ):
            candidate = self.results.get(
                "regen_geometry_material_display_geometry"
            )

            if isinstance(
                candidate,
                dict,
            ):
                display_geometry = dict(
                    candidate
                )

        populations[
            str(
                mode
            )
        ] = {
            "strategy":
                str(
                    mode
                ),

            "strategy_label":
                strategy_label,

            "ranked_population":
                ranked,

            "evaluated_population":
                evaluated,

            "display_geometry":
                display_geometry,
        }

        self.results[
            "regen_candidate_populations_by_strategy"
        ] = populations

        return True

    def execute_selected_regen_design_mode(self):
        """Execute only the strategy explicitly selected by the user."""

        mode = (
            self.current_regen_design_mode()
        )

        if (
            mode
            ==
            "automatic_geometry_materials"
        ):
            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "STARTING_AUTOMATIC_GEOMETRY_AND_MATERIALS"
            )

            result = (
                self.start_geometry_material_automatic_design()
            )

            # Geometry + Materials executes asynchronously.  Its candidate
            # population is captured by the existing completion owner after
            # regenerated results have actually been installed.
            return result

        if (
            mode
            !=
            "automatic_selected_material"
        ):
            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "BLOCKED_MANUAL_MODE"
            )

            return False

        self.results[
            "regen_design_mode_generation_state"
        ] = "RUNNING"

        self.results[
            "regen_design_mode_execution_status"
        ] = (
            "EXECUTING_AUTOMATIC_SELECTED_MATERIAL"
        )

        self.set_geometry_source(
            "automatic"
        )

        try:
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass

        requested_candidate_id = (
            self.results.get(
                "regen_candidate_selector_requested_candidate_id"
            )
        )

        if requested_candidate_id:
            if not self.prepare_selected_generated_design_for_execution():
                self.results[
                    "regen_design_mode_generation_state"
                ] = "ERROR"

                self.results[
                    "regen_design_mode_execution_status"
                ] = (
                    "BLOCKED_SELECTED_GENERATED_DESIGN_NOT_READY"
                )

                try:
                    self.configure_status_strip()
                    self.canvas.update()
                    self.canvas.repaint()
                except Exception:
                    pass

                return False

        elif not self.canonical_generated_design_candidates():
            self.results[
                "regen_viewer_accepted_geometry"
            ] = {}

        result = (
            self.select_or_generate_automatic_geometry()
        )

        self.capture_regen_candidate_population_for_strategy(
            mode
        )

        if result:
            self.results[
                "regen_design_mode_generation_state"
            ] = "GENERATED"

            self.results[
                "regen_viewer_automatic_geometry_mode"
            ] = (
                "automatic_selected_material"
            )

        else:
            self.results[
                "regen_design_mode_generation_state"
            ] = (
                "NO_FEASIBLE_DESIGN"
            )

            self.results[
                "regen_viewer_accepted_geometry"
            ] = {}

        try:
            self.refresh_generated_design_selector()
        except Exception:
            pass

        self.results[
            "regen_design_mode_execution_status"
        ] = (
            "COMPLETE_AUTOMATIC_SELECTED_MATERIAL"
            if result
            else
            "BLOCKED_OR_FAILED_AUTOMATIC_SELECTED_MATERIAL"
        )

        self.set_geometry_source(
            "automatic"
        )

        try:
            self.refresh_values_panel()
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass

        return result



    def force_enable_automatic_geometry_button_phase_16p7c(self):
        """
        Phase 16P.7C
        Final production guard: Automatic Geometry must never remain disabled
        after viewer setup or refresh.
        """
        button = getattr(self, "automatic_button", None)
        if button is None:
            return False

        button.setEnabled(True)
        button.setDisabled(False)
        button.setText("Generate Automatic Geometry")
        button.setToolTip(
            "Generate and apply automatic regen geometry from the current design."
        )

        if isinstance(getattr(self, "results", None), dict):
            self.results["phase_16p7c_force_enabled_automatic_geometry"] = True
            self.results["phase_16p7c_force_enabled_automatic_geometry_status"] = (
                "PASS_FORCE_ENABLED_AUTOMATIC_GEOMETRY_PHASE_16P7C"
            )

        self.sync_regen_design_mode_controls()


        return True

    def refresh_automatic_geometry_button_state_phase_16n2(self):
        """
        Phase 16P.7B
        Production button-state repair.

        The Generate Automatic Geometry button must remain clickable.
        Missing staged geometry is handled by the workflow itself, which can
        build a conservative candidate or report a clear blocked state.
        """
        button = getattr(self, "automatic_button", None)
        if button is None:
            return False

        button.setEnabled(True)
        button.setText("Generate Automatic Geometry")
        button.setToolTip(
            "Use the canonical ranked regen candidate when available. "
            "If no canonical staged candidate exists, LEAF will report "
            "a blocked automatic-geometry state."
        )

        if isinstance(getattr(self, "results", None), dict):
            self.results["phase_16p7b_automatic_button_state_status"] = (
                "PASS_AUTOMATIC_BUTTON_PRODUCTION_ENABLED_PHASE_16P7B"
            )
            self.results["phase_16p7b_automatic_button_enabled"] = True
            self.results["phase_16p7b_automatic_button_text"] = (
                "Generate Automatic Geometry"
            )

        self.sync_regen_design_mode_controls()


        return True

    def get_staged_automatic_geometry(self):
        staged = (
                self.results.get("regen_geometry_commit_staged_geometry")
                or self.results.get("regen_autonomous_geometry_staged_candidate", {}).get(
            "staged_geometry",
            {}
        )
                or {}
        )

        if not isinstance(staged, dict):
            return {}

        return dict(staged)

    def get_current_manual_geometry_snapshot(self):
        """
        Return the manual geometry required for viewer comparison,
        rollback reference, and automatic runtime re-entry validation.

        This is a snapshot only. It does not create or promote
        automatic geometry.
        """

        if not hasattr(
            self,
            "canvas",
        ):
            return {}

        try:
            geometry = self.canvas.get_geometry(
                "manual"
            )

        except Exception as exc:
            if isinstance(
                getattr(
                    self,
                    "results",
                    None,
                ),
                dict,
            ):
                self.results[
                    "phase_16p16_manual_snapshot_canvas_error"
                ] = str(exc)

            return {}

        if not isinstance(
            geometry,
            dict,
        ):
            return {}

        keys = [
            "gas_radius",
            "radius",
            "profile_radius",
            "station_radius",
            "selected_radius",
            "selected_station_radius",
            "throat_radius",
            "minimum_gas_radius",
            "channel_width",
            "channel_height",
            "requested_rib_width",
            "rib_width",
            "channel_count",
            "number_of_coolant_channels",
            "wall",
            "hot_gas_wall_thickness",
            "jacket",
            "outer_wall_thickness",
        ]

        return {
            key:
                geometry.get(
                    key
                )
            for key
            in keys
            if key
            in geometry
        }

    def record_geometry_acceptance_event(self, action, geometry=None, reason=""):
        history = self.results.get("regen_viewer_geometry_acceptance_history", [])

        if not isinstance(history, list):
            history = []

        history.append({
            "action": action,
            "geometry": dict(geometry or {}),
            "reason": reason,
            "source": self.results.get("regen_viewer_actual_geometry_source"),
            "data_origin": self.results.get("regen_viewer_data_origin"),
        })

        self.results["regen_viewer_geometry_acceptance_history"] = history
        self.results["regen_viewer_geometry_acceptance_history_count"] = len(history)

    def refresh_before_after_comparison_phase_16n9(self):
        """
        Phase 16N.9B
        Build before/after comparison after accepted geometry is applied.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        fallback_before_after_comparison_phase_16p10(self.results)
        return bool(self.results.get("phase_16n9_before_after_comparison_available"))





    def start_geometry_material_automatic_design(self):
        """Start the canonical Geometry + Materials search off the UI thread."""

        task = getattr(
            self,
            "_regen_geometry_material_background_task",
            None,
        )

        if (
            task is not None
            and
            getattr(
                task,
                "running",
                False,
            )
        ):
            return False

        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return False

        self.results[
            "regen_design_mode_generation_state"
        ] = "RUNNING"

        self.results[
            "regen_geometry_material_display_geometry"
        ] = {}

        self.set_geometry_source(
            "automatic"
        )

        try:
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass

        try:
            from leaf_qt.runtime.qt_background_task import (
                QtBackgroundTaskOwner,
            )

            from leaf_qt.engine_solver import (
                run_regen_geometry_material_automatic_design,
            )

        except Exception as exc:
            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "FAILED_GEOMETRY_MATERIAL_BACKGROUND_OWNER_IMPORT"
            )

            self.results[
                "regen_geometry_material_background_error"
            ] = str(
                exc
            )

            return False

        # This is the only engineering payload handed to the worker:
        # an isolated dictionary snapshot.
        search_snapshot = dict(
            self.results
        )

        search_snapshot[
            "regen_candidate_design_mode"
        ] = (
            "GEOMETRY_AND_MATERIALS"
        )

        self._regen_geometry_material_before_results = dict(
            self.results
        )

        task = QtBackgroundTaskOwner(
            self
        )

        task.started.connect(
            self._on_geometry_material_background_started
        )

        task.completed.connect(
            self._on_geometry_material_background_completed
        )

        task.failed.connect(
            self._on_geometry_material_background_failed
        )

        task.finished.connect(
            self._on_geometry_material_background_finished
        )

        self._regen_geometry_material_background_task = (
            task
        )

        started = task.start(
            "regen_geometry_material_automatic_design",
            run_regen_geometry_material_automatic_design,
            search_snapshot,
        )

        if not started:
            self._regen_geometry_material_background_task = None

            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "FAILED_GEOMETRY_MATERIAL_BACKGROUND_START"
            )

            self.sync_regen_design_mode_controls()

            return False

        return True


    def _on_geometry_material_background_started(
            self,
            task_name,
    ):
        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return

        self.results[
            "regen_geometry_material_background_task_name"
        ] = str(
            task_name
        )

        self.results[
            "regen_geometry_material_background_running"
        ] = True

        self.results[
            "regen_design_mode_generation_state"
        ] = "RUNNING"

        self.set_geometry_source(
            "automatic"
        )

        self.results[
            "regen_design_mode_execution_status"
        ] = (
            "RUNNING_AUTOMATIC_GEOMETRY_AND_MATERIALS"
        )

        self.results[
            "regen_geometry_material_background_status"
        ] = (
            "RUNNING"
        )

        self.sync_regen_design_mode_controls()

        try:
            self.configure_status_strip()
        except Exception:
            pass


    def _on_geometry_material_background_completed(
            self,
            callback_result,
    ):
        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return

        if not isinstance(
            callback_result,
            dict,
        ):
            self._on_geometry_material_background_failed(
                "Geometry + Materials background task returned "
                "a non-dictionary result."
            )

            return

        before_results = (
            self._regen_geometry_material_before_results
            if isinstance(
                self._regen_geometry_material_before_results,
                dict,
            )
            else
            dict(
                self.results
            )
        )

        self.refresh_from_regenerated_results_phase_16p5b(
            callback_result,
            before_results=before_results,
        )

        # The background engineering task has now completed and the
        # regenerated result set is authoritative. Capture this strategy's
        # population here rather than at task-start time.
        self.capture_regen_candidate_population_for_strategy(
            "automatic_geometry_materials"
        )

        evaluated = (
            self.results.get(
                "regen_candidate_evaluated_population"
            )
            or
            []
        )

        qualified = (
            self.results.get(
                "regen_candidate_qualified_population"
            )
            or
            []
        )

        ranked = (
            self.results.get(
                "regen_candidate_ranked_population"
            )
            or
            []
        )

        self.results[
            "regen_geometry_material_background_evaluated_count"
        ] = len(
            evaluated
        )

        self.results[
            "regen_geometry_material_background_qualified_count"
        ] = len(
            qualified
        )

        self.results[
            "regen_geometry_material_background_ranked_count"
        ] = len(
            ranked
        )

        self.results[
            "regen_geometry_material_background_running"
        ] = False

        rank_one = (
            ranked[0]
            if (
                ranked
                and
                isinstance(
                    ranked[0],
                    dict,
                )
            )
            else
            {}
        )

        rank_one_geometry = (
            rank_one.get(
                "candidate_geometry"
            )
            if isinstance(
                rank_one,
                dict,
            )
            else
            {}
        )

        if not isinstance(
            rank_one_geometry,
            dict,
        ):
            rank_one_geometry = {}

        if (
            ranked
            and
            rank_one_geometry
        ):
            self.results[
                "regen_design_mode_generation_state"
            ] = "GENERATED"

            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "COMPLETE_AUTOMATIC_GEOMETRY_AND_MATERIALS"
            )

            self.results[
                "regen_geometry_material_background_status"
            ] = (
                "COMPLETE_QUALIFIED_DESIGNS_AVAILABLE"
            )

            self.results[
                "regen_geometry_material_display_geometry"
            ] = dict(
                rank_one_geometry
            )

            self.results[
                "regen_viewer_automatic_geometry_mode"
            ] = (
                "automatic_geometry_materials"
            )

            self.results[
                "regen_geometry_material_display_rank"
            ] = 1

            self.results[
                "regen_geometry_material_display_candidate_id"
            ] = rank_one.get(
                "candidate_id"
            )

            self.results[
                "regen_geometry_material_display_material"
            ] = (
                rank_one.get(
                    "candidate_material_name"
                )
                or
                (
                    rank_one.get(
                        "candidate_design_inputs"
                    )
                    or
                    {}
                ).get(
                    "selected_material"
                )
            )

        elif ranked:
            self.results[
                "regen_design_mode_generation_state"
            ] = "ERROR"

            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "FAILED_AUTOMATIC_GEOMETRY_AND_MATERIALS_"
                "RANKED_GEOMETRY_MISSING"
            )

            self.results[
                "regen_geometry_material_background_status"
            ] = (
                "FAILED_RANKED_GEOMETRY_MISSING"
            )

            self.results[
                "regen_geometry_material_display_geometry"
            ] = {}

        else:
            self.results[
                "regen_design_mode_generation_state"
            ] = (
                "NO_FEASIBLE_DESIGN"
            )

            self.results[
                "regen_design_mode_execution_status"
            ] = (
                "COMPLETE_AUTOMATIC_GEOMETRY_AND_MATERIALS_"
                "NO_FEASIBLE_DESIGN"
            )

            self.results[
                "regen_geometry_material_background_status"
            ] = (
                "COMPLETE_NO_FEASIBLE_DESIGN"
            )

            self.results[
                "regen_geometry_material_display_geometry"
            ] = {}

            self.results[
                "regen_viewer_accepted_geometry"
            ] = {}

        self.set_geometry_source(
            "automatic"
        )

        try:
            self.refresh_generated_design_selector()
        except Exception:
            pass

        try:
            self.refresh_values_panel()
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass



    def _on_geometry_material_background_failed(
            self,
            error_text,
    ):
        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            return

        self.results[
            "regen_geometry_material_background_running"
        ] = False

        self.results[
            "regen_geometry_material_background_status"
        ] = (
            "FAILED"
        )

        self.results[
            "regen_geometry_material_background_error"
        ] = str(
            error_text
            or
            "Unknown Geometry + Materials background-task failure."
        )

        self.results[
            "regen_design_mode_execution_status"
        ] = (
            "FAILED_AUTOMATIC_GEOMETRY_AND_MATERIALS"
        )

        self.results[
            "regen_design_mode_generation_state"
        ] = "ERROR"

        self.results[
            "regen_geometry_material_display_geometry"
        ] = {}

        self.results[
            "regen_viewer_accepted_geometry"
        ] = {}

        self.set_geometry_source(
            "automatic"
        )

        try:
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass



    def _on_geometry_material_background_finished(
            self,
            task_name,
    ):
        if isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            self.results[
                "regen_geometry_material_background_running"
            ] = False

            self.results[
                "regen_geometry_material_background_finished_task_name"
            ] = str(
                task_name
            )

        task = getattr(
            self,
            "_regen_geometry_material_background_task",
            None,
        )

        self._regen_geometry_material_background_task = None
        self._regen_geometry_material_before_results = None

        if task is not None:
            try:
                task.deleteLater()
            except Exception:
                pass

        self.sync_regen_design_mode_controls()

        try:
            self.configure_status_strip()
        except Exception:
            pass


    def refresh_from_regenerated_results_phase_16p5b(self, callback_result, before_results=None):
        """
        Phase 16P.5B
        Merge regenerated solver results into the viewer and refresh the UI.
        """
        if not isinstance(getattr(self, "results", None), dict):
            self.results = {}

        before_results = dict(before_results or self.results or {})

        if not isinstance(callback_result, dict):
            self.results["phase_16p5b_viewer_auto_refresh_status"] = (
                "WARN_VIEWER_AUTO_REFRESH_NO_CALLBACK_RESULT_PHASE_16P5B"
            )
            self.results["phase_16p5b_viewer_auto_refreshed"] = False
            return False

        self.results.update(callback_result)

        verification_payload = None

        if verify_result_replacement is not None:
            verification = verify_result_replacement(before_results, self.results)
            verification_payload = {
                "status": verification.status,
                "changed_keys": list(verification.changed_keys),
                "unchanged_keys": list(verification.unchanged_keys),
                "changed_count": verification.changed_count,
                "verified": verification.verified,
            }
            self.results["phase_16p5b_result_replacement_verification"] = verification_payload
            self.results["phase_16p5b_result_replacement_verified"] = bool(
                verification.verified
            )
            self.results["phase_16p5b_result_replacement_changed_keys"] = list(
                verification.changed_keys
            )
        else:
            self.results["phase_16p5b_result_replacement_verification"] = {
                "status": "WARN_RESULT_REPLACEMENT_VERIFIER_UNAVAILABLE_PHASE_16P5B",
                "verified": False,
            }
            self.results["phase_16p5b_result_replacement_verified"] = False

        self.results["phase_16p5b_viewer_auto_refresh_status"] = (
            "PASS_VIEWER_AUTO_REFRESH_PHASE_16P5B"
        )
        self.results["phase_16p5b_viewer_auto_refreshed"] = True
        self.results["phase_16p5b_viewer_auto_refresh_callback_key_count"] = len(
            callback_result
        )

        try:
            self.refresh_automatic_geometry_button_state_phase_16n2()
            self.force_enable_automatic_geometry_button_phase_16p7c()
            self.refresh_cross_section_live_feed_validation_phase_16n4()
            self.refresh_values_panel()
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception as exc:
            self.results["phase_16p5b_viewer_auto_refresh_status"] = (
                "WARN_VIEWER_AUTO_REFRESH_UI_REFRESH_ERROR_PHASE_16P5B"
            )
            self.results["phase_16p5b_viewer_auto_refresh_error"] = str(exc)
            return False

        return True



    def run_live_solver_regeneration_phase_16p3(self, geometry_override=None):
        """
        Phase 16P.3
        Request live solver/UI regeneration through an optional callback.

        This viewer does not own the main solver. It safely asks the parent/main
        window/controller to regenerate using the currently applied geometry.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        callback = getattr(self, "regeneration_callback", None)

        self.results["phase_16p3_live_solver_regeneration_requested"] = True

        if callback is None:
            self.results["phase_16p3_live_solver_regeneration_status"] = (
                "WARN_LIVE_SOLVER_REGENERATION_CALLBACK_MISSING_PHASE_16P3"
            )
            self.results["phase_16p3_live_solver_regeneration_message"] = (
                "No live solver regeneration callback is attached to the regen viewer."
            )
            self.results["phase_16p3_live_solver_regenerated"] = False
            return False

        if geometry_override is None:
            geometry = (
                self.results.get("regen_ui_applied_geometry")
                or self.results.get("regen_viewer_accepted_geometry")
                or self.results.get("regen_geometry_commit_staged_geometry")
                or {}
            )
        elif isinstance(geometry_override, dict):
            geometry = dict(geometry_override)
        else:
            geometry = {}

        try:
            callback_result = callback(dict(geometry), self.results)
        except Exception as exc:
            self.results["phase_16p3_live_solver_regeneration_status"] = (
                "FAIL_LIVE_SOLVER_REGENERATION_CALLBACK_ERROR_PHASE_16P3"
            )
            self.results["phase_16p3_live_solver_regeneration_message"] = str(exc)
            self.results["phase_16p3_live_solver_regenerated"] = False
            return False

        before_refresh_phase_16p5b = dict(self.results)

        if isinstance(callback_result, dict):
            self.refresh_from_regenerated_results_phase_16p5b(
                callback_result,
                before_results=before_refresh_phase_16p5b,
            )

        regenerated = bool(
            self.results.get("phase_16p3_live_solver_regenerated")
            or self.results.get("solver_regenerated")
            or self.results.get("calculation_complete")
        )

        if regenerated:
            self.results["phase_16p3_live_solver_regeneration_status"] = (
                "PASS_LIVE_SOLVER_REGENERATION_PHASE_16P3"
            )
            self.results["phase_16p3_live_solver_regeneration_message"] = (
                "Live solver regeneration callback completed successfully."
            )
            self.results["phase_16p3_live_solver_regenerated"] = True
        else:
            self.results["phase_16p3_live_solver_regeneration_status"] = (
                "WARN_LIVE_SOLVER_REGENERATION_CALLBACK_RETURNED_NO_SOLVE_PHASE_16P3"
            )
            self.results["phase_16p3_live_solver_regeneration_message"] = (
                "Live solver regeneration callback returned but did not mark solver regeneration complete."
            )
            self.results["phase_16p3_live_solver_regenerated"] = False

        try:
            self.refresh_values_panel()
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass

        return bool(self.results.get("phase_16p3_live_solver_regenerated"))



    def request_solver_regeneration_phase_16n8(self):
        """
        Phase 16N.8B
        Record that applied geometry is ready for solver regeneration.
        Does not directly run the solver.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        fallback_solver_regeneration_request_phase_16p9(self.results)

        try:
            self.refresh_cross_section_live_feed_validation_phase_16n4()
        except Exception:
            pass

        return bool(self.results.get("phase_16n8_solver_regeneration_requested"))


    def apply_accepted_geometry_phase_16n7(self):
        """
        Phase 16N.7B
        Apply accepted staged geometry to UI-level current geometry.
        Does not regenerate solver.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        fallback_apply_geometry_result_phase_16p8(self.results)

        try:
            self.refresh_automatic_geometry_button_state_phase_16n2()
            self.force_enable_automatic_geometry_button_phase_16p7c()
        except Exception:
            pass

        try:
            self.refresh_cross_section_live_feed_validation_phase_16n4()
        except Exception:
            pass

        return bool(self.results.get("phase_16n7_geometry_applied"))


    def accept_recommendation_phase_16n6(self):
        """
        Phase 16N.6B
        Record user acceptance of the staged automatic recommendation.
        Does not apply geometry or regenerate solver.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        if attach_accept_recommendation_result_phase_16n6 is None:
            self.results["phase_16n6_accept_recommendation_status"] = (
                "WARN_ACCEPT_RECOMMENDATION_OWNER_IMPORT_FAILED_PHASE_16N6"
            )
            return False

        attach_accept_recommendation_result_phase_16n6(self.results)

        try:
            self.refresh_automatic_geometry_button_state_phase_16n2()
            self.force_enable_automatic_geometry_button_phase_16p7c()
        except Exception:
            pass

        try:
            self.refresh_cross_section_live_feed_validation_phase_16n4()
        except Exception:
            pass

        return bool(self.results.get("phase_16n6_recommendation_accepted"))




    def show_live_acceptance_report_phase_16p4e(self):
        """
        Phase 16P.4E
        Display the latest Generate Automatic Geometry live acceptance evidence.
        """
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        except Exception:
            return False

        report = ""
        if isinstance(getattr(self, "results", None), dict):
            report = self.results.get("phase_16p4d_live_ui_acceptance_report", "")

        if not report:
            report = (
                "No live acceptance report is available yet.\n\n"
                "Click Generate Automatic Geometry first, then reopen this report."
            )

        dialog = QDialog(self)
        dialog.setWindowTitle("Live Acceptance Report")
        dialog.resize(900, 650)

        layout = QVBoxLayout(dialog)

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setPlainText(str(report))
        layout.addWidget(text_box)

        copy_button = QPushButton("Copy Report")
        close_button = QPushButton("Close")

        def copy_report():
            try:
                from PySide6.QtWidgets import QApplication
                QApplication.clipboard().setText(str(report))
            except Exception:
                pass

        copy_button.clicked.connect(copy_report)
        close_button.clicked.connect(dialog.close)

        layout.addWidget(copy_button)
        layout.addWidget(close_button)

        dialog.exec()
        return True



    def build_live_ui_acceptance_report_phase_16p4d(
            self,
            before_geometry=None,
            staged_geometry=None,
            after_geometry=None,
            accepted=False,
            applied=False,
            requested=False,
            live_regenerated=False,
            compared=False,
    ):
        """
        Phase 16P.4D
        Build a live GUI acceptance evidence report for Generate Automatic Geometry.
        """
        before_geometry = dict(before_geometry or {})
        staged_geometry = dict(staged_geometry or {})
        after_geometry = dict(after_geometry or {})

        tracked_keys = [
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "number_of_coolant_channels",
            "hot_gas_wall_thickness",
            "outer_wall_thickness",
            "outer_jacket_thickness",
            "coolant_flow_fraction",
            "channel_width",
            "channel_height",
            "requested_rib_width",
            "channel_count",
            "wall",
            "jacket",
        ]

        changed = {}

        for key in tracked_keys:
            before_value = before_geometry.get(key)
            staged_value = staged_geometry.get(key)
            after_value = after_geometry.get(key)

            if staged_value is not None and before_value != staged_value:
                changed[key] = {
                    "before": before_value,
                    "staged": staged_value,
                    "after": after_value,
                }

        status = (
            "PASS_LIVE_UI_ACCEPTANCE_VALIDATION_PHASE_16P4D"
            if accepted and applied and staged_geometry
            else "WARN_LIVE_UI_ACCEPTANCE_VALIDATION_INCOMPLETE_PHASE_16P4D"
        )

        lines = [
            "LEAF PHASE 16P.4D — LIVE UI ACCEPTANCE VALIDATION",
            "=================================================",
            "",
            f"Status: {status}",
            f"Accepted: {bool(accepted)}",
            f"Applied: {bool(applied)}",
            f"Solver regeneration requested: {bool(requested)}",
            f"Live solver regenerated: {bool(live_regenerated)}",
            f"Before/after comparison available: {bool(compared)}",
            f"Changed tracked geometry fields: {len(changed)}",
            "",
            "Changed Fields:",
        ]

        if changed:
            for key, payload in changed.items():
                lines.append(
                    f"- {key}: before={payload.get('before')} "
                    f"staged={payload.get('staged')} after={payload.get('after')}"
                )
        else:
            lines.append("- None detected.")

        report = "\n".join(lines)

        self.results["phase_16p4d_live_ui_acceptance_status"] = status
        self.results["phase_16p4d_live_ui_acceptance_report"] = report
        self.results["phase_16p4d_live_ui_acceptance_changed_fields"] = changed
        self.results["phase_16p4d_live_ui_acceptance_changed_field_count"] = len(changed)
        self.results["phase_16p4d_live_ui_acceptance_before_geometry"] = before_geometry
        self.results["phase_16p4d_live_ui_acceptance_staged_geometry"] = staged_geometry
        self.results["phase_16p4d_live_ui_acceptance_after_geometry"] = after_geometry

        pass
        pass
        pass

        return report




    def show_applied_automatic_geometry_phase_16p11(self):
        """
        Phase 16P.11
        After Generate Automatic Geometry completes, explicitly display the
        applied automatic geometry as the active viewer source.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        applied = (
            self.results.get(
                "regen_ui_applied_geometry"
            )
            or self.results.get(
                "regen_viewer_accepted_geometry"
            )
            or self.results.get(
                "regen_geometry_commit_staged_geometry"
            )
            or self.results.get(
                "regen_autonomous_geometry_staged_candidate",
                {},
            ).get(
                "staged_geometry",
                {},
            )
            or {}
        )

        if not isinstance(applied, dict) or not applied:
            self.results["phase_16p11_automatic_source_display_status"] = (
                "WARN_NO_APPLIED_AUTOMATIC_GEOMETRY_TO_DISPLAY_PHASE_16P11"
            )
            return False

        self.results["regen_geometry_source_active"] = "automatic"
        self.results["regen_viewer_actual_geometry_source"] = "automatic"
        self.results["phase_16p11_automatic_source_display_status"] = (
            "PASS_AUTOMATIC_GEOMETRY_DISPLAYED_PHASE_16P11"
        )
        self.results["phase_16p11_automatic_source_displayed"] = True
        self.results["phase_16p11_displayed_automatic_geometry"] = dict(applied)

        try:
            self.canvas.geometry_source = "automatic"

            manual_geometry = self.canvas.get_geometry("manual")
            automatic_geometry = self.canvas.get_geometry("automatic")

            pass
            pass
            pass
            pass
            pass
            pass
            pass

            self.canvas.update()
            self.canvas.repaint()
        except Exception as exc:
            self.results["phase_16p11_automatic_source_display_status"] = (
                "WARN_AUTOMATIC_GEOMETRY_CANVAS_DISPLAY_ERROR_PHASE_16P11"
            )
            self.results["phase_16p11_automatic_source_display_error"] = str(exc)

        try:
            self.refresh_geometry_source_button_styles()
            self.refresh_values_panel()
        except Exception:
            pass

        return True



    def select_manual_geometry(self):
        """Return from automatic geometry to the canonical manual-input path."""
        if not isinstance(getattr(self, "results", None), dict):
            self.results = {}

        callback = getattr(
            self,
            "regeneration_callback",
            None,
        )

        was_automatic = (
            getattr(
                getattr(
                    self,
                    "canvas",
                    None,
                ),
                "geometry_source",
                "manual",
            )
            ==
            "automatic"
        )

        if (
            was_automatic
            and callback is not None
        ):
            try:
                callback_result = callback(
                    {},
                    self.results,
                )

            except Exception as exc:
                self.results[
                    "regen_viewer_manual_geometry_restore_status"
                ] = (
                    "FAIL_MANUAL_GEOMETRY_REGENERATION"
                )

                self.results[
                    "regen_viewer_manual_geometry_restore_error"
                ] = str(exc)

                return False

            regenerated = (
                isinstance(
                    callback_result,
                    dict,
                )

                and
                callback_result.get(
                    "phase_16p3_live_solver_regenerated"
                )
                is True
            )

            if not regenerated:
                self.results[
                    "regen_viewer_manual_geometry_restore_status"
                ] = (
                    "FAIL_MANUAL_GEOMETRY_REGENERATION"
                )

                return False

        self.set_geometry_source(
            "manual"
        )

        self.results[
            "regen_viewer_manual_geometry_restore_status"
        ] = (
            "PASS_MANUAL_GEOMETRY_RESTORED"
        )

        self.results[
            "regen_viewer_manual_geometry_restored"
        ] = True

        try:
            self.refresh_values_panel()
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()

        except Exception:
            pass

        return True


    def canonical_regen_failure_presentation(self):
        """
        Build presentation-only Regen failure information from canonical
        solver and candidate-qualification payloads.

        This method does not calculate engineering limits, reproduce
        qualification criteria, change solver results, or apply fixes.
        """
        feasibility_status = str(
            self.results.get(
                "regen_feasibility_status",
                "UNKNOWN",
            )
            or "UNKNOWN"
        ).upper()

        reasons = self.results.get(
            "regen_feasibility_reasons",
            [],
        )

        recommendations = self.results.get(
            "regen_feasibility_recommendations",
            [],
        )

        if not isinstance(reasons, list):
            reasons = []

        if not isinstance(recommendations, list):
            recommendations = []

        population = self.results.get(
            "regen_candidate_evaluated_population",
            [],
        )

        if not isinstance(population, list):
            population = []

        qualification_state_counts = {}
        constraint_status_counts = {}

        for candidate in population:
            if not isinstance(candidate, dict):
                continue

            state = str(
                candidate.get(
                    "regen_qualification_state",
                    "UNKNOWN",
                )
                or "UNKNOWN"
            ).upper()

            qualification_state_counts[
                state
            ] = (
                qualification_state_counts.get(
                    state,
                    0,
                )
                + 1
            )

            report = candidate.get(
                "regen_qualification_report"
            )

            if not isinstance(
                report,
                dict,
            ):
                continue

            constraints = report.get(
                "constraints",
                {},
            )

            if not isinstance(
                constraints,
                dict,
            ):
                continue

            for (
                constraint_id,
                payload,
            ) in constraints.items():

                if not isinstance(
                    payload,
                    dict,
                ):
                    continue

                status = str(
                    payload.get(
                        "status",
                        "UNKNOWN",
                    )
                    or "UNKNOWN"
                ).upper()

                counts = (
                    constraint_status_counts
                    .setdefault(
                        str(
                            constraint_id
                        ),
                        {},
                    )
                )

                counts[status] = (
                    counts.get(
                        status,
                        0,
                    )
                    + 1
                )

        failed_constraints = sorted(
            constraint_id
            for (
                constraint_id,
                counts,
            )
            in (
                constraint_status_counts
                .items()
            )
            if (
                counts.get(
                    "FAIL",
                    0,
                )
                > 0
            )
        )

        unproven_constraints = sorted(
            constraint_id
            for (
                constraint_id,
                counts,
            )
            in (
                constraint_status_counts
                .items()
            )
            if (
                counts.get(
                    "UNPROVEN",
                    0,
                )
                > 0
            )
        )

        return {
            "feasibility_status":
                feasibility_status,

            "feasibility_reasons":
                list(
                    reasons
                ),

            "feasibility_recommendations":
                list(
                    recommendations
                ),

            "evaluated_candidate_count":
                len(
                    population
                ),

            "qualification_state_counts":
                qualification_state_counts,

            "constraint_status_counts":
                constraint_status_counts,

            "failed_constraints":
                failed_constraints,

            "unproven_constraints":
                unproven_constraints,
        }

    def canonical_regen_failure_lines(self):
        """
        Present canonical Regen failure evidence only.

        This method does not create limits, qualification criteria,
        recommendations, engineering results, or geometry changes.
        """

        summary = (
            self.canonical_regen_failure_presentation()
        )

        population = self.results.get(
            "regen_candidate_evaluated_population",
            [],
        )

        if not isinstance(population, list):
            population = []

        validation_results = self.results.get(
            "phase_11a2_regen_geometry_constraint_validation_owner_results",
            [],
        )

        if not isinstance(validation_results, list):
            validation_results = []

        explanations = self.results.get(
            "phase_11a3_regen_geometry_failure_explanation_owner_explanations",
            [],
        )

        if not isinstance(explanations, list):
            explanations = []

        recommendations = self.results.get(
            "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations",
            [],
        )

        if not isinstance(recommendations, list):
            recommendations = []

        feasibility_reasons = list(
            summary.get(
                "feasibility_reasons",
                [],
            )
            or
            []
        )

        feasibility_recommendations = list(
            summary.get(
                "feasibility_recommendations",
                [],
            )
            or
            []
        )

        failed_constraints = list(
            summary.get(
                "failed_constraints",
                [],
            )
            or
            []
        )

        unproven_constraints = list(
            summary.get(
                "unproven_constraints",
                [],
            )
            or
            []
        )

        validation_by_id = {}

        for item in validation_results:
            if not isinstance(item, dict):
                continue

            constraint_id = item.get(
                "constraint_id"
            )

            if constraint_id not in (
                None,
                "",
            ):
                validation_by_id[
                    str(constraint_id)
                ] = item

        explanation_by_id = {}

        for item in explanations:
            if not isinstance(item, dict):
                continue

            constraint_id = item.get(
                "constraint_id"
            )

            if constraint_id not in (
                None,
                "",
            ):
                explanation_by_id[
                    str(constraint_id)
                ] = item

        qualification_evidence = {}

        for candidate in population:
            if not isinstance(candidate, dict):
                continue

            report = candidate.get(
                "regen_qualification_report"
            )

            if not isinstance(report, dict):
                continue

            constraints = report.get(
                "constraints",
                {},
            )

            if not isinstance(constraints, dict):
                continue

            for constraint_id, payload in constraints.items():
                if not isinstance(payload, dict):
                    continue

                status = str(
                    payload.get(
                        "status",
                        "UNKNOWN",
                    )
                    or
                    "UNKNOWN"
                ).upper()

                if status != "FAIL":
                    continue

                qualification_evidence.setdefault(
                    str(constraint_id),
                    payload,
                )

        recommendations_by_constraint = {}

        for recommendation in recommendations:
            if not isinstance(recommendation, dict):
                continue

            constraint_id = recommendation.get(
                "source_constraint"
            )

            if constraint_id in (
                None,
                "",
            ):
                continue

            recommendations_by_constraint.setdefault(
                str(constraint_id),
                [],
            ).append(
                recommendation
            )

        def value_text(value):
            if isinstance(value, float):
                return f"{value:.6g}"

            return str(value)

        def evidence_text(
            constraint_id,
            payload,
        ):
            combined = {}

            validation = validation_by_id.get(
                constraint_id,
                {},
            )

            if isinstance(validation, dict):
                combined.update(validation)

            if isinstance(payload, dict):
                combined.update(payload)

            pieces = []

            direct_keys = (
                "value",
                "actual_value",
                "observed_value",
                "calculated_value",
                "current_value",
            )

            for key in direct_keys:
                value = combined.get(key)

                if value not in (
                    None,
                    "",
                ):
                    pieces.append(
                        f"{key}={value_text(value)}"
                    )

            for key, value in combined.items():
                if value in (
                    None,
                    "",
                ):
                    continue

                if isinstance(
                    value,
                    (
                        dict,
                        list,
                        tuple,
                        set,
                    ),
                ):
                    continue

                key_lower = str(key).lower()

                if any(
                    token in key_lower
                    for token in (
                        "limit",
                        "threshold",
                        "minimum",
                        "maximum",
                        "allowable",
                        "required_min",
                        "required_max",
                        "margin",
                    )
                ):
                    entry = (
                        f"{key}="
                        f"{value_text(value)}"
                    )

                    if entry not in pieces:
                        pieces.append(entry)

            reason = ""

            for key in (
                "reason",
                "message",
                "explanation",
                "detail",
            ):
                value = combined.get(key)

                if value not in (
                    None,
                    "",
                ):
                    reason = str(value)
                    break

            if not reason:
                explanation = explanation_by_id.get(
                    constraint_id,
                    {},
                )

                if isinstance(explanation, dict):
                    value = explanation.get(
                        "explanation"
                    )

                    if value not in (
                        None,
                        "",
                    ):
                        reason = str(value)

            if reason:
                pieces.append(reason)

            return " | ".join(
                pieces
            )

        lines = []

        # --------------------------------------------------------
        # WHAT FAILED
        # --------------------------------------------------------

        lines.append(
            "WHAT FAILED"
        )

        counts = summary.get(
            "constraint_status_counts",
            {},
        )

        if not isinstance(counts, dict):
            counts = {}

        if failed_constraints:
            for constraint_id in failed_constraints:
                payload = counts.get(
                    constraint_id,
                    {},
                )

                fail_count = (
                    payload.get(
                        "FAIL",
                        0,
                    )
                    if isinstance(
                        payload,
                        dict,
                    )
                    else
                    0
                )

                if fail_count:
                    lines.append(
                        f"- {constraint_id}: "
                        f"FAIL in {fail_count} evaluated candidate(s)"
                    )

                else:
                    lines.append(
                        f"- {constraint_id}: FAIL"
                    )

        else:
            lines.append(
                "- No explicit failed qualification "
                "constraint was exposed."
            )

        for constraint_id in unproven_constraints:
            lines.append(
                f"- {constraint_id}: UNPROVEN"
            )

        # --------------------------------------------------------
        # WHY
        # --------------------------------------------------------

        lines.append("")
        lines.append(
            "WHY"
        )

        why_lines = []

        for constraint_id in failed_constraints:
            evidence = (
                qualification_evidence.get(
                    constraint_id,
                    {},
                )
            )

            text = evidence_text(
                constraint_id,
                evidence,
            )

            if text:
                why_lines.append(
                    f"- {constraint_id}: {text}"
                )

        for reason in feasibility_reasons:
            if reason in (
                None,
                "",
            ):
                continue

            line = (
                f"- {reason}"
            )

            if line not in why_lines:
                why_lines.append(line)

        if why_lines:
            lines.extend(
                why_lines
            )

        else:
            lines.append(
                "- Canonical failure state exists, but "
                "no additional reason/value/limit evidence "
                "was exposed."
            )

        # --------------------------------------------------------
        # WHAT MIGHT FIX IT
        # --------------------------------------------------------

        lines.append("")
        lines.append(
            "WHAT MIGHT FIX IT"
        )

        guidance = []
        seen = set()

        # Prefer recommendations explicitly linked to failed
        # constraint IDs.

        for constraint_id in failed_constraints:
            for recommendation in (
                recommendations_by_constraint.get(
                    constraint_id,
                    [],
                )
            ):
                title = str(
                    recommendation.get(
                        "title"
                    )
                    or
                    recommendation.get(
                        "recommendation_id"
                    )
                    or
                    "Canonical recommendation"
                )

                direction = str(
                    recommendation.get(
                        "proposed_direction"
                    )
                    or
                    ""
                )

                expected = str(
                    recommendation.get(
                        "expected_benefit"
                    )
                    or
                    ""
                )

                text = (
                    f"[{constraint_id}] "
                    f"{title}"
                )

                if direction:
                    text += (
                        f" — {direction}"
                    )

                if expected:
                    text += (
                        f" — Expected: {expected}"
                    )

                if text not in seen:
                    seen.add(text)
                    guidance.append(text)

        # Existing canonical feasibility guidance is allowed as
        # fallback evidence, but is not rewritten or invented here.

        for recommendation in feasibility_recommendations:
            if recommendation in (
                None,
                "",
            ):
                continue

            text = str(
                recommendation
            )

            if text not in seen:
                seen.add(text)
                guidance.append(text)

        if guidance:
            lines.extend(
                f"- {item}"
                for item in guidance
            )

        else:
            lines.append(
                "- No canonical recommendation was exposed "
                "for the current failure evidence."
            )

        return lines


    def notify_automatic_geometry_failure(
            self,
            fallback_message,
    ):
        """
        Publish a user-triggered Automatic Geometry failure through the
        canonical LEAF Runtime Notification Centre.

        Engineering meaning is read only from existing canonical payloads.
        """
        summary = (
            self
            .canonical_regen_failure_presentation()
        )

        parts = []

        if fallback_message:
            parts.append(
                str(
                    fallback_message
                )
            )

        reasons = summary[
            "feasibility_reasons"
        ]

        if reasons:
            parts.append(
                str(
                    reasons[0]
                )
            )

        failed = summary[
            "failed_constraints"
        ]

        if failed:
            parts.append(
                "Failed qualification constraints: "
                + ", ".join(
                    failed
                )
                + "."
            )

        unproven = summary[
            "unproven_constraints"
        ]

        if unproven:
            parts.append(
                "Unproven qualification constraints: "
                + ", ".join(
                    unproven
                )
                + "."
            )

        message = " ".join(
            part.strip()
            for part in parts
            if str(
                part
            ).strip()
        )

        if not message:
            message = (
                "Automatic Regen Geometry "
                "could not produce an "
                "appliable design."
            )

        runtime_notification_centre.error(
            title=(
                "Automatic Regen Geometry "
                "Unavailable"
            ),
            message=message,
            source=(
                "regen_cross_section_viewer"
            ),
            target_type=(
                "regen_cross_section_viewer"
            ),
            action_ref=(
                "generate_automatic_geometry"
            ),
        )

        return message

    def select_or_generate_automatic_geometry(self):
        """
        Select the existing accepted automatic geometry when available.

        Geometry-mode selection is a lightweight viewer operation.
        Automatic geometry generation is an engineering operation and is
        performed only when no complete accepted automatic snapshot exists.
        """
        requested_candidate_id = self.results.get(
            "regen_candidate_selector_requested_candidate_id"
        )

        selected_candidate_id = self.results.get(
            "regen_candidate_selector_user_selected_candidate_id"
        )

        selected_patch = self.results.get(
            "regen_candidate_application_patch"
        )

        if not isinstance(
            selected_patch,
            dict,
        ):
            selected_patch = {}

        selected_staged = (
            self.get_staged_automatic_geometry()
        )

        selected_generated_design_ready = bool(
            requested_candidate_id
            and
            selected_candidate_id
            and
            str(
                selected_candidate_id
            )
            ==
            str(
                requested_candidate_id
            )
            and
            str(
                selected_patch.get(
                    "candidate_id"
                )
            )
            ==
            str(
                requested_candidate_id
            )
            and
            self.results.get(
                "regen_candidate_application_ready"
            )
            is True
            and
            self.results.get(
                "regen_candidate_geometry_application_allowed"
            )
            is True
            and
            (
                self.results.get(
                    "regen_geometry_commit_candidate_ready"
                )
                or
                self.results.get(
                    "regen_autonomous_geometry_commit_ready"
                )
            )
            and
            isinstance(
                selected_staged,
                dict,
            )
            and
            bool(
                selected_staged
            )
        )

        if selected_generated_design_ready:
            self.results[
                "regen_viewer_automatic_selection_status"
            ] = "SELECTED_QUALIFIED_GENERATED_DESIGN"

            self.results[
                "regen_viewer_automatic_selection_generated"
            ] = False

            return (
                self.run_automatic_geometry_workflow_phase_16p1()
            )

        accepted = self.results.get(
            "regen_viewer_accepted_geometry",
            {},
        )

        def positive_number(value):
            try:
                return float(value) > 0.0
            except (TypeError, ValueError):
                return False

        channel_count = None

        if isinstance(accepted, dict):
            channel_count = (
                accepted.get(
                    "number_of_coolant_channels"
                )
                or accepted.get(
                    "channel_count"
                )
            )

        complete = (
            isinstance(accepted, dict)
            and bool(accepted)
            and positive_number(
                accepted.get(
                    "coolant_channel_width"
                )
            )
            and positive_number(
                accepted.get(
                    "coolant_channel_height"
                )
            )
            and positive_number(
                accepted.get(
                    "rib_width"
                )
            )
            and positive_number(
                accepted.get(
                    "hot_gas_wall_thickness"
                )
            )
            and positive_number(
                channel_count
            )
        )

        if complete:
            self.results[
                "regen_viewer_automatic_selection_status"
            ] = "CACHED_ACCEPTED_GEOMETRY"

            self.results[
                "regen_viewer_automatic_selection_generated"
            ] = False

            self.set_geometry_source(
                "automatic"
            )

            return True

        self.results[
            "regen_viewer_automatic_selection_status"
        ] = "GENERATION_REQUIRED"

        self.results[
            "regen_viewer_automatic_selection_generated"
        ] = True

        return (
            self.run_automatic_geometry_workflow_phase_16p1()
        )


    def run_automatic_geometry_workflow_phase_16p1(self):
        """
        Phase 16P.1
        Production Automatic Geometry workflow.

        User-facing meaning:
        - Try to use existing staged/recommended geometry.
        - If available, accept/apply/request solver regeneration/build before-after.
        - If unavailable, keep user informed and do not pretend success.
        """
        if not isinstance(getattr(self, "results", None), dict):
            return False

        if (
            self.results.get("regen_viewer_automatic_selection_status")
            == "GENERATION_REQUIRED"
        ):
            self.run_live_solver_regeneration_phase_16p3({})

        # RH2D-R1 — canonical automatic runtime re-entry validation
        #
        # Validate only the already staged canonical automatic
        # geometry. This helper does not generate, promote, apply,
        # or commit geometry.
        try:
            from leaf_qt.regen_automatic_geometry_runtime_reentry_owner_phase_16p16 import (
                build_runtime_reentry_candidate,
            )

            manual_snapshot = (
                self.get_current_manual_geometry_snapshot()
            )

            build_runtime_reentry_candidate(
                self.results,
                manual_snapshot,
            )

        except Exception as exc:
            self.results[
                "phase_16p16_runtime_reentry_status"
            ] = (
                "ERROR_REGEN_AUTOMATIC_GEOMETRY_"
                "RUNTIME_REENTRY_PHASE_16P16"
            )

            self.results[
                "phase_16p16_runtime_reentry_error"
            ] = str(exc)
        staged = self.get_staged_automatic_geometry()

        # Canonical automatic geometry may only come from the optimiser/application/commit chain.
        canonical_application_patch = (
            self.results.get("regen_candidate_application_patch")
            or self.results.get("recommended_regen_geometry_patch")
            or {}
        )

        canonical_staging_ready = bool(
            staged
            and self.results.get(
                "regen_candidate_geometry_application_allowed"
            )
            and isinstance(canonical_application_patch, dict)
            and canonical_application_patch
            and (
                self.results.get(
                    "regen_autonomous_geometry_commit_ready"
                )
                or self.results.get(
                    "regen_geometry_commit_candidate_ready"
                )
            )
        )

        if not canonical_staging_ready:
            staged = {}

        if not staged:
            self.results["phase_16p1_automatic_geometry_workflow_status"] = (
                "BLOCKED_NO_AUTOMATIC_GEOMETRY_AVAILABLE_PHASE_16P1"
            )
            self.results["phase_16p1_automatic_geometry_workflow_message"] = (
                "Automatic Geometry could not run because no staged or recommended geometry payload is available. "
                "Run candidate generation/ranking first, then reopen this viewer."
            )
            self.results["regen_viewer_geometry_acceptance_status"] = (
                "BLOCKED_NO_STAGED_AUTOMATIC_GEOMETRY"
            )
            self.results["regen_viewer_geometry_acceptance_message"] = (
                "No staged automatic geometry exists to apply."
            )

            self.notify_automatic_geometry_failure(
                self.results.get(
                    "phase_16p1_automatic_geometry_workflow_message",
                    "",
                )
            )

            try:
                self.refresh_values_panel()
                self.configure_status_strip()
                self.canvas.update()
            except Exception:
                pass

            return False

        before_geometry_phase_16p4d = self.get_current_manual_geometry_snapshot()

        self.results["phase_16p1_automatic_geometry_workflow_started"] = True
        self.results["phase_16p1_automatic_geometry_workflow_staged_geometry"] = dict(staged)

        # Keep compatibility with the existing proven 16N chain.

        accepted = self.accept_recommendation_phase_16n6()
        applied = self.apply_accepted_geometry_phase_16n7()
        requested = self.request_solver_regeneration_phase_16n8()
        live_regenerated = self.run_live_solver_regeneration_phase_16p3()
        compared = self.refresh_before_after_comparison_phase_16n9()
        displayed = self.show_applied_automatic_geometry_phase_16p11()

        rollback = self.get_current_manual_geometry_snapshot()
        self.results["regen_viewer_rollback_geometry"] = rollback
        self.results["regen_viewer_accepted_geometry"] = dict(staged)
        self.refresh_rollback_geometry_button_state()

        self.results["phase_16p1_automatic_geometry_workflow_accepted"] = bool(accepted)
        self.results["phase_16p1_automatic_geometry_workflow_applied"] = bool(applied)
        self.results["phase_16p1_automatic_geometry_workflow_solver_regen_requested"] = bool(requested)
        self.results["phase_16p1_automatic_geometry_workflow_live_solver_regenerated"] = bool(live_regenerated)
        self.results["phase_16p1_automatic_geometry_workflow_before_after_available"] = bool(compared)

        after_geometry_phase_16p4d = (
            self.results.get("regen_ui_applied_geometry")
            or self.results.get("regen_viewer_accepted_geometry")
            or self.get_staged_automatic_geometry()
            or {}
        )

        self.build_live_ui_acceptance_report_phase_16p4d(
            before_geometry=before_geometry_phase_16p4d,
            staged_geometry=staged,
            after_geometry=after_geometry_phase_16p4d,
            accepted=accepted,
            applied=applied,
            requested=requested,
            live_regenerated=live_regenerated,
            compared=compared,
        )

        self.results["phase_16p11_automatic_display_requested"] = bool(displayed)

        if accepted and applied:
            self.results["phase_16p1_automatic_geometry_workflow_status"] = (
                "PASS_AUTOMATIC_GEOMETRY_WORKFLOW_PHASE_16P1"
            )
            self.results["phase_16p1_automatic_geometry_workflow_message"] = (
                "Automatic geometry was accepted and applied to the viewer state."
            )
        else:
            self.results["phase_16p1_automatic_geometry_workflow_status"] = (
                "WARN_AUTOMATIC_GEOMETRY_WORKFLOW_PARTIAL_PHASE_16P1"
            )
            self.results["phase_16p1_automatic_geometry_workflow_message"] = (
                "Automatic geometry workflow ran but one or more downstream ownership stages did not report success."
            )

        self.record_geometry_acceptance_event(
            "RUN_AUTOMATIC_GEOMETRY_WORKFLOW",
            staged,
            self.results.get("phase_16p1_automatic_geometry_workflow_message", ""),
        )

        self.set_geometry_source("automatic")

        try:
            self.refresh_automatic_geometry_button_state_phase_16n2()
            self.force_enable_automatic_geometry_button_phase_16p7c()
            self.refresh_cross_section_live_feed_validation_phase_16n4()
            self.refresh_values_panel()
            self.configure_status_strip()
            self.canvas.update()
            self.canvas.repaint()
        except Exception:
            pass

        return bool(accepted and applied)


    def refresh_rollback_geometry_button_state(self):
        """
        Synchronise Rollback Geometry availability with real viewer state.

        Rollback is available only while an accepted automatic geometry
        exists together with its previous manual rollback snapshot.
        This method changes UI availability only.
        """
        button = getattr(
            self,
            "rollback_geometry_button",
            None,
        )

        if button is None:
            return False

        results = getattr(
            self,
            "results",
            {},
        )

        if not isinstance(
            results,
            dict,
        ):
            results = {}

        rollback = results.get(
            "regen_viewer_rollback_geometry",
            {},
        )

        accepted = results.get(
            "regen_viewer_accepted_geometry",
            {},
        )

        rollback_available = bool(
            isinstance(
                rollback,
                dict,
            )
            and
            rollback
            and
            isinstance(
                accepted,
                dict,
            )
            and
            accepted
        )

        button.setEnabled(
            rollback_available
        )

        button.setToolTip(
            (
                "Restore the previous manual geometry."
                if rollback_available
                else
                "Rollback becomes available after an automatic "
                "geometry has been accepted."
            )
        )

        return rollback_available

    def accept_automatic_geometry(self):
        self.accept_recommendation_phase_16n6()
        self.apply_accepted_geometry_phase_16n7()
        self.request_solver_regeneration_phase_16n8()
        self.refresh_before_after_comparison_phase_16n9()
        staged = self.get_staged_automatic_geometry()

        if not staged:
            self.results["regen_viewer_geometry_acceptance_status"] = (
                "BLOCKED_NO_STAGED_AUTOMATIC_GEOMETRY"
            )
            self.results["regen_viewer_geometry_acceptance_message"] = (
                "No staged automatic geometry exists to accept."
            )
            self.refresh_values_panel()
            self.canvas.update()
            return

        rollback = self.get_current_manual_geometry_snapshot()

        self.results["regen_viewer_rollback_geometry"] = rollback
        self.results["regen_viewer_accepted_geometry"] = dict(staged)
        self.refresh_rollback_geometry_button_state()
        self.results["regen_viewer_geometry_acceptance_status"] = (
            "ACCEPTED_AUTOMATIC_GEOMETRY"
        )
        self.results["regen_viewer_geometry_acceptance_message"] = (
            "Automatic geometry accepted for preview state."
        )

        self.record_geometry_acceptance_event(
            "ACCEPT_AUTOMATIC",
            staged,
            "Automatic staged geometry accepted by user.",
        )

        self.set_geometry_source("automatic")
        self.refresh_values_panel()
        self.configure_status_strip()
        self.canvas.update()
        self.canvas.repaint()

    def reject_automatic_geometry(self):
        staged = self.get_staged_automatic_geometry()

        self.results["regen_viewer_rejected_geometry"] = dict(staged)
        self.results["regen_viewer_geometry_acceptance_status"] = (
            "REJECTED_AUTOMATIC_GEOMETRY"
        )
        self.results["regen_viewer_geometry_acceptance_message"] = (
            "Automatic geometry candidate rejected."
        )

        self.record_geometry_acceptance_event(
            "REJECT_AUTOMATIC",
            staged,
            "Automatic staged geometry rejected by user.",
        )

        self.set_geometry_source("manual")
        self.refresh_values_panel()
        self.configure_status_strip()
        self.canvas.update()
        self.canvas.repaint()

    def rollback_accepted_geometry(self):
        rollback = self.results.get("regen_viewer_rollback_geometry", {})

        if not isinstance(rollback, dict) or not rollback:
            self.results["regen_viewer_geometry_acceptance_status"] = (
                "BLOCKED_NO_ROLLBACK_GEOMETRY"
            )
            self.results["regen_viewer_geometry_acceptance_message"] = (
                "No rollback geometry exists."
            )
            self.refresh_values_panel()
            self.canvas.update()
            return

        self.results["regen_viewer_accepted_geometry"] = {}
        self.refresh_rollback_geometry_button_state()
        self.results["regen_viewer_geometry_acceptance_status"] = (
            "ROLLED_BACK_TO_MANUAL_GEOMETRY"
        )
        self.results["regen_viewer_geometry_acceptance_message"] = (
            "Viewer geometry rolled back to previous manual state."
        )

        self.record_geometry_acceptance_event(
            "ROLLBACK_GEOMETRY",
            rollback,
            "Accepted automatic geometry rolled back.",
        )

        self.set_geometry_source("manual")
        self.refresh_values_panel()
        self.configure_status_strip()
        self.canvas.update()
        self.canvas.repaint()

    def build_source_validation_summary_lines(self):
        lines = []

        maturity = self.canvas.evaluate_source_maturity_score()

        lines.append(f"Source maturity score: {maturity['overall_score']} / 100")
        lines.append(f"Source maturity status: {maturity['status']}")
        lines.append(f"Source maturity recommendation: {maturity['recommendation']}")
        lines.append(f"Material maturity component: {maturity['material_score']} / 100")
        lines.append(f"Coating maturity component: {maturity['coating_score']} / 100")
        lines.append(f"Bond-coat maturity component: {maturity['bond_score']} / 100")
        lines.append("")

        source_fields = [
            ("Source validation mode", "source_validation_mode"),
            ("Conservative gate", "source_validation_conservative_gate"),
            ("Source validation status", "regen_source_validation_status"),
            ("Source recommendation", "regen_source_validation_recommendation"),

            ("Material validation mode", "material_validation_mode"),
            ("Material source score", "material_source_validation_score"),
            ("Material has citation", "material_source_has_citation"),
            ("Material has temperature table", "material_source_has_temperature_table"),
            ("Material is placeholder", "material_source_is_placeholder"),
            ("Material recommendation", "material_source_validation_recommendation"),

            ("Coating validation mode", "coating_validation_mode"),
            ("Coating source score", "coating_source_validation_score"),
            ("Coating has citation", "coating_source_has_citation"),
            ("Coating has temperature table", "coating_source_has_temperature_table"),
            ("Coating is placeholder", "coating_source_is_placeholder"),
            ("Coating recommendation", "coating_source_validation_recommendation"),

            ("Bond-coat validation mode", "bond_coat_validation_mode"),
            ("Bond-coat source score", "bond_coat_source_validation_score"),
            ("Bond-coat has citation", "bond_coat_source_has_citation"),
            ("Bond-coat has temperature table", "bond_coat_source_has_temperature_table"),
            ("Bond-coat is placeholder", "bond_coat_source_is_placeholder"),
            ("Bond-coat recommendation", "bond_coat_source_validation_recommendation"),
        ]

        for label, key in source_fields:
            lines.append(f"{label}: {self.results.get(key, 'N/A')}")

        return lines

    def build_station_summary_text(self):
        geometry = self.canvas.get_geometry()
        station = self.canvas.selected_station()

        lines = []

        lines.append("LEAF Regen Cross-Section Viewer")
        lines.append("Selected Station Summary")
        lines.append("=" * 42)
        lines.append("")

        lines.append(f"View mode: {self.canvas.view_mode}")
        lines.append(f"Geometry source: {self.canvas.geometry_source}")
        lines.append(f"Overlay mode: {self.canvas.overlay_mode}")
        lines.append(f"Scale mode: {self.canvas.scale_mode}")
        lines.append(f"Station profile: {self.canvas.station_profile_key}")
        lines.append("")

        lines.append("Geometry")
        lines.append("-" * 42)
        lines.append(f"Selected x: {self.canvas.format_engineering_value(geometry.get('selected_length'), 'm')}")
        lines.append(f"Gas radius: {self.canvas.format_engineering_value(geometry.get('gas_radius'), 'm')}")
        lines.append(f"Wall thickness: {self.canvas.format_engineering_value(geometry.get('wall'), 'm')}")
        lines.append(f"Coating thickness: {self.canvas.format_engineering_value(geometry.get('coating'), 'm')}")
        lines.append(f"Channel height: {self.canvas.format_engineering_value(geometry.get('channel_height'), 'm')}")
        lines.append(f"Channel width: {self.canvas.format_engineering_value(geometry.get('channel_width'), 'm')}")
        lines.append(f"Requested rib width: {self.canvas.format_engineering_value(geometry.get('requested_rib_width'), 'm')}")
        lines.append(f"Effective rib width: {self.canvas.format_engineering_value(geometry.get('effective_rib_width'), 'm')}")
        lines.append(f"Channel count: {geometry.get('channel_count')}")
        lines.append(f"Requested pitch: {self.canvas.format_engineering_value(geometry.get('requested_pitch'), 'm')}")
        lines.append(f"Available pitch: {self.canvas.format_engineering_value(geometry.get('available_pitch'), 'm')}")
        lines.append(f"Fit ratio: {self.canvas.format_engineering_value(geometry.get('channel_fit_ratio'))}")
        lines.append(f"Geometry valid: {geometry.get('channel_geometry_valid')}")
        lines.append(f"Cooling coverage: {self.canvas.format_engineering_value(geometry.get('cooling_coverage'))}")
        lines.append("")

        lines.append("Selected Axial Station")
        lines.append("-" * 42)

        if station:
            preferred_keys = [
                "station_index",
                "x",
                "radius",
                "area",
                "mach",
                "static_pressure",
                "static_temperature",
                "adiabatic_wall_temperature",
                "hg",
                "hot_gas_side_wall_temperature",
                "coolant_side_wall_temperature",
                "regen_heat_flux",
                "coolant_temperature_in",
                "coolant_temperature_out",
                "coolant_temperature_mean",
                "coolant_velocity",
                "coolant_reynolds_number",
                "station_pressure_drop",
                "total_pressure_drop_so_far",
                "thermal_resistance",
                "controlling_thermal_resistance",
            ]

            for key in preferred_keys:
                if key in station:
                    lines.append(f"{key}: {station.get(key)}")
        else:
            lines.append("No axial station profile available.")

        lines.append("")
        lines.append("Validation")
        lines.append("-" * 42)
        lines.append(f"Overall: {self.results.get('regen_overall_status', 'N/A')}")
        lines.append(f"Geometry: {self.results.get('regen_geometry_status', 'N/A')}")
        lines.append(f"Thermal: {self.results.get('regen_thermal_status', 'N/A')}")
        lines.append(f"Coolant: {self.results.get('regen_coolant_status', 'N/A')}")
        lines.append(f"Material: {self.results.get('regen_material_status', 'N/A')}")
        lines.append(f"Final verdict: {self.results.get('final_regen_design_verdict', 'N/A')}")
        lines.append("")
        lines.append("Source Validation")
        lines.append("-" * 42)
        lines.extend(self.build_source_validation_summary_lines())
        lines.append("")
        lines.append("Source-Data Checklist")
        lines.append("-" * 42)

        for passed, title, action in self.canvas.build_source_data_checklist():
            status = _leaf_16u38_marker_from_bool(passed, false_marker="MISSING")
            lines.append(f"{status}: {title}")
            if not passed:
                lines.append(f"  Required action: {action}")

        signoff = self.canvas.evaluate_regen_signoff(geometry)
        lines.append("")
        lines.append("Reference Engine Validation")
        lines.append("-" * 42)
        reference_fields = [
            ("Selected reference key", "reference_engine_name"),
            ("Selected validation reference", "validation_reference_engine"),
            ("Reference engine", "reference_engine_display_name"),
            ("Scalability status", "regen_scalability_validation_status"),
            ("Reference source status", "reference_engine_source_status"),
            ("Agreement percent", "reference_engine_overall_agreement_percent"),
            ("Mean error percent", "reference_engine_mean_error_percent"),
            ("Comparison count", "reference_engine_comparison_count"),
            ("Channel width error percent", "reference_engine_channel_width_error_percent"),
            ("Channel height error percent", "reference_engine_channel_height_error_percent"),
            ("Channel count error percent", "reference_engine_channel_count_error_percent"),
            ("Wall thickness error percent", "reference_engine_wall_thickness_error_percent"),
            ("Coolant velocity error percent", "reference_engine_coolant_velocity_error_percent"),
            ("Pressure drop error percent", "reference_engine_pressure_drop_error_percent"),
            ("Coolant temperature rise error percent", "reference_engine_coolant_temperature_rise_error_percent"),
            ("Validation note", "reference_engine_validation_note"),
            ("Reference record status", "viewer_reference_record_status"),
            ("Filled comparison fields", "viewer_reference_filled_comparison_count"),
            ("Filled source fields", "viewer_reference_filled_source_count"),
            ("Missing reference inputs", "viewer_reference_missing_inputs"),
            ("Missing comparison fields", "viewer_reference_missing_comparison_fields"),
            ("Missing source metadata", "viewer_reference_missing_source_fields"),
            ("Reference recommendation", "viewer_reference_record_recommendation"),
            ("Imported reference key", "viewer_imported_reference_key"),
            ("Imported template parse status", "viewer_imported_reference_parse_status"),
            ("Imported template record status", "viewer_imported_reference_record_status"),
            ("Imported filled comparison count", "viewer_imported_reference_filled_comparison_count"),
            ("Imported filled source count", "viewer_imported_reference_filled_source_count"),
            ("Imported missing inputs", "viewer_imported_reference_missing_inputs"),
            ("Imported missing comparison fields", "viewer_imported_reference_missing_comparison_fields"),
            ("Imported missing source fields", "viewer_imported_reference_missing_source_fields"),
            ("Imported recommendation", "viewer_imported_reference_recommendation"),
            ("Reference readiness", "viewer_reference_readiness_status"),
            ("Reference input ready", "viewer_reference_input_ready"),
            ("Reference comparison ready", "viewer_reference_comparison_ready"),
            ("Reference source ready", "viewer_reference_source_ready"),
            ("Reference readiness action", "viewer_reference_readiness_recommendation"),
            ("Imported readiness", "viewer_imported_reference_readiness_status"),
            ("Imported input ready", "viewer_imported_reference_input_ready"),
            ("Imported comparison ready", "viewer_imported_reference_comparison_ready"),
            ("Imported source ready", "viewer_imported_reference_source_ready"),
            ("Imported readiness action", "viewer_imported_reference_readiness_recommendation"),
            ("Stored DB fuel", "viewer_reference_db_fuel"),
            ("Stored DB oxidizer", "viewer_reference_db_oxidizer"),
            ("Stored DB mixture ratio", "viewer_reference_db_mixture_ratio"),
            ("Stored DB mass flow rate", "viewer_reference_db_mass_flow_rate"),
            ("Stored DB chamber pressure", "viewer_reference_db_chamber_pressure"),
            ("Stored DB characteristic length", "viewer_reference_db_characteristic_length"),
            ("Stored DB ambient pressure", "viewer_reference_db_ambient_pressure"),
            ("Stored DB thrust", "viewer_reference_db_thrust_n"),
            ("Stored DB throat area", "viewer_reference_db_throat_area_m2"),
            ("Stored DB exit area", "viewer_reference_db_exit_area_m2"),
            ("Stored DB channel count", "viewer_reference_db_channel_count"),
            ("Stored DB channel width", "viewer_reference_db_channel_width_m"),
            ("Stored DB channel height", "viewer_reference_db_channel_height_m"),
            ("Stored DB wall thickness", "viewer_reference_db_wall_thickness_m"),
            ("Stored DB source title", "viewer_reference_db_source_title"),
            ("Stored DB source author", "viewer_reference_db_source_author"),
            ("Stored DB source year", "viewer_reference_db_source_year"),
            ("Stored DB URL", "viewer_reference_db_url"),
            ("Reference comparison run gate", "reference_comparison_run_gate_status"),
            ("Reference comparison ready", "reference_comparison_ready"),
            ("Missing LEAF comparison fields", "reference_comparison_missing_leaf_fields"),
            ("Missing reference comparison fields", "reference_comparison_missing_reference_fields"),
            ("Reference comparison quality", "reference_comparison_quality_status"),
            ("Reference average error percent", "reference_comparison_average_error_percent"),
            ("Reference agreement percent", "reference_comparison_agreement_percent"),
            ("Reference best matching field", "reference_comparison_best_field"),
            ("Reference worst matching field", "reference_comparison_worst_field"),
            ("Reference quality recommendation", "reference_comparison_quality_recommendation"),
            ("Reference validation verdict", "reference_validation_verdict"),
            ("Reference validation recommendation", "reference_validation_recommendation"),
            ("Reference status strip selected", "reference_engine_display_name"),
            ("Reference status strip database usefulness", "viewer_reference_db_usefulness_status"),
            ("Reference status strip readiness", "viewer_reference_readiness_status"),
            ("Reference status strip run gate", "reference_comparison_run_gate_status"),
            ("Reference status strip verdict", "reference_validation_verdict"),
            ("Reference status strip next action", "reference_validation_recommendation"),
            ("Reference source ledger status", "reference_source_ledger_status"),
            ("Reference source ledger covered count", "reference_source_ledger_covered_count"),
            ("Reference source ledger filled count", "reference_source_ledger_filled_count"),
            ("Reference source ledger coverage percent", "reference_source_ledger_coverage_percent"),
            ("Reference source ledger missing notes", "reference_source_ledger_missing_notes"),
            ("Reference source ledger recommendation", "reference_source_ledger_recommendation"),
        ]

        reference_name = self.results.get("reference_engine_name")

        if reference_name:
            lines.append("")
            lines.append("Stored Reference Database Report")
            lines.append("-" * 42)
            lines.append(self.build_reference_database_report_text(reference_name))
            lines.append("")
            lines.append("Reference Source Ledger Audit")
            lines.append("-" * 42)
            lines.append(self.build_reference_ledger_audit_text(reference_name))

        for label, key in reference_fields:
            lines.append(f"{label}: {self.results.get(key, 'N/A')}")

        evidence = self.results.get("reference_comparison_evidence")

        if isinstance(evidence, list) and evidence:
            lines.append("")
            lines.append("Reference Comparison Evidence")
            lines.append("-" * 42)

            for row in evidence:
                lines.append(f"{row.get('label', 'Unknown')}:")
                lines.append(f"  LEAF key: {row.get('leaf_key', 'N/A')}")
                lines.append(f"  LEAF value: {row.get('leaf_value', 'N/A')}")
                lines.append(f"  Reference key: {row.get('reference_key', 'N/A')}")
                lines.append(f"  Reference value: {row.get('reference_value', 'N/A')}")
                lines.append(f"  Ready: {row.get('ready', 'N/A')}")
                lines.append(f"  Error percent: {row.get('error_percent', 'N/A')}")

        lines.append("")
        lines.append("Regen Sign-Off")
        lines.append("-" * 42)
        lines.append(f"Reference validation verdict: {self.results.get('reference_validation_verdict', 'N/A')}")
        lines.append(f"Reference validation recommendation: {self.results.get('reference_validation_recommendation', 'N/A')}")
        lines.append(f"Reference verdict used by sign-off: {signoff.get('reference_verdict', 'N/A')}")
        lines.append(f"Sign-off status: {signoff['status']}")
        lines.append(f"Checklist: {signoff['passed_items']} / {signoff['total_items']}")
        lines.append(f"Material validation mode: {signoff['material_mode']}")
        lines.append(f"Coating validation mode: {signoff['coating_mode']}")
        lines.append(f"Scalability validation: {signoff['scalability_status']}")
        lines.append(f"External testing ready: {signoff['external_testing_ready']}")
        lines.append(f"Next action: {signoff['next_action']}")

        return "\n".join(lines)

    def import_reference_template_preview(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Import Reference Engine Source Template",
            "",
            "Text File (*.txt);;All Files (*)"
        )

        if not filepath:
            return

        if parse_reference_engine_template_text is None or validate_reference_engine_record_data is None:
            QMessageBox.warning(
                self,
                "Reference Parser Missing",
                "Reference template parser functions could not be imported."
            )
            return

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                template_text = file.read()
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Import Failed",
                f"Could not read template file:\n{exc}"
            )
            return

        data, parse_status = parse_reference_engine_template_text(template_text)

        self.results["viewer_imported_reference_parse_status"] = parse_status

        if data is None:
            self.results["viewer_imported_reference_key"] = "N/A"
            self.results["viewer_imported_reference_record_status"] = "PARSE_FAILED"
            self.results["viewer_imported_reference_recommendation"] = parse_status
            if hasattr(self, "export_reference_patch_button"):
                self.export_reference_patch_button.setEnabled(False)

            self.refresh_values_panel()
            return

        validation = validate_reference_engine_record_data(data)

        readiness = None

        if evaluate_reference_engine_readiness is not None:
            readiness = evaluate_reference_engine_readiness(data)

        self.imported_reference_template_data = data

        self.results["viewer_imported_reference_key"] = data.get("reference_engine_key", "N/A")
        self.results["viewer_imported_reference_record_status"] = validation.get("status")
        self.results["viewer_imported_reference_input_preset_status"] = validation.get("input_preset_status")
        self.results["viewer_imported_reference_comparison_status"] = validation.get("comparison_status")
        self.results["viewer_imported_reference_filled_input_count"] = validation.get("filled_input_count")
        self.results["viewer_imported_reference_filled_comparison_count"] = validation.get("filled_comparison_count")
        self.results["viewer_imported_reference_input_preset_status"] = validation.get("input_preset_status")
        self.results["viewer_imported_reference_comparison_status"] = validation.get("comparison_status")
        self.results["viewer_imported_reference_filled_input_count"] = validation.get("filled_input_count")
        self.results["viewer_imported_reference_filled_source_count"] = validation.get("filled_source_count")
        self.results["viewer_imported_reference_missing_inputs"] = ", ".join(validation.get("missing_inputs", [])) or "None"
        self.results["viewer_imported_reference_missing_comparison_fields"] = ", ".join(validation.get("missing_comparison_fields", [])) or "None"
        self.results["viewer_imported_reference_missing_source_fields"] = ", ".join(validation.get("missing_source_fields", [])) or "None"
        self.results["viewer_imported_reference_recommendation"] = validation.get("recommendation")

        if readiness:
            self.results["viewer_imported_reference_readiness_status"] = readiness.get("status")
            self.results["viewer_imported_reference_input_ready"] = readiness.get("input_ready")
            self.results["viewer_imported_reference_comparison_ready"] = readiness.get("comparison_ready")
            self.results["viewer_imported_reference_source_ready"] = readiness.get("source_ready")
            self.results["viewer_imported_reference_readiness_recommendation"] = readiness.get("recommendation")
        else:
            self.results["viewer_imported_reference_readiness_status"] = "READINESS_HELPER_MISSING"
            self.results["viewer_imported_reference_input_ready"] = "N/A"
            self.results["viewer_imported_reference_comparison_ready"] = "N/A"
            self.results["viewer_imported_reference_source_ready"] = "N/A"
            self.results["viewer_imported_reference_readiness_recommendation"] = "Readiness helper unavailable."

        if hasattr(self, "export_reference_patch_button"):
            self.export_reference_patch_button.setEnabled(data is not None)

        self.refresh_values_panel()

        QMessageBox.information(
            self,
            "Template Preview Complete",
            f"Imported reference key: {data.get('reference_engine_key', 'N/A')}\n"
            f"Status: {validation.get('status')}\n\n"
            f"{validation.get('recommendation')}"
        )

    def export_reference_database_patch(self):
        if build_reference_engine_database_patch is None:
            QMessageBox.warning(
                self,
                "Patch Export Missing",
                "build_reference_engine_database_patch could not be imported."
            )
            return

        data = getattr(self, "imported_reference_template_data", None)

        if not isinstance(data, dict):
            QMessageBox.warning(
                self,
                "No Imported Template",
                "Import a reference template before exporting a database patch."
            )
            return

        validation = validate_reference_engine_record_data(data)

        if validation.get("status") == "PLACEHOLDER_REQUIRED":
            confirm = QMessageBox.question(
                self,
                "Placeholder Record",
                "This template still contains no sourced comparison values.\n\n"
                "Exporting it will keep source_status as PLACEHOLDER_REQUIRED and will not improve validation.\n\n"
                "Export anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if confirm != QMessageBox.Yes:
                return

        patch_text = build_reference_engine_database_patch(data)

        if not patch_text:
            QMessageBox.warning(
                self,
                "Patch Failed",
                "Could not build a paste-ready database patch."
            )
            return

        key = data.get("reference_engine_key", "reference_engine")

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Database Patch",
            f"{key}_database_patch.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write("# Paste this block inside REFERENCE_ENGINES = {\n")
                file.write("# Replace the existing entry with the same key.\n\n")
                file.write(patch_text)
                file.write("\n")

            QMessageBox.information(
                self,
                "Patch Export Complete",
                f"Database patch exported:\n{filepath}"
            )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export database patch:\n{exc}"
            )

    def export_reference_source_template(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting a source template."
            )
            return

        if build_reference_engine_source_template is None:
            QMessageBox.warning(
                self,
                "Reference Database Missing",
                "Could not import build_reference_engine_source_template from reference_engine_database.py."
            )
            return

        template_text = build_reference_engine_source_template(reference_name)

        if not template_text:
            QMessageBox.warning(
                self,
                "Template Failed",
                "Could not build a source template for the selected reference engine."
            )
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Engine Source Template",
            f"{reference_name}_source_template.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(template_text)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Reference source template exported:\n{filepath}"
            )
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export reference source template:\n{exc}"
            )

    def export_current_canvas_png(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Regen Viewer PNG",
            "leaf_regen_view.png",
            "PNG Image (*.png)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".png"):
            filepath += ".png"

        success = self.save_canvas_png_to_path(filepath)

        if success:
            QMessageBox.information(
                self,
                "Export Complete",
                f"Regen viewer image exported:\n{filepath}"
            )
        else:
            QMessageBox.warning(
                self,
                "Export Failed",
                "Could not export the regen viewer image."
            )

    def export_station_summary_txt(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Regen Station Summary",
            "leaf_regen_station_summary.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(self.build_station_summary_text())

            source_mode = self.results.get("source_validation_mode", "UNKNOWN")

            QMessageBox.information(
                self,
                "Export Complete",
                f"Station summary exported:\n{filepath}\n\nSource mode: {source_mode}"
            )
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export station summary:\n{exc}"
            )

    def save_canvas_png_to_path(self, filepath):
        pixmap = QPixmap(self.canvas.size())
        self.canvas.render(pixmap)
        return pixmap.save(filepath, "PNG")

    def export_figure_pack(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder for Regen Figure Pack"
        )

        if not folder:
            return

        original_view_mode = self.canvas.view_mode
        original_overlay_mode = self.canvas.overlay_mode
        original_geometry_source = self.canvas.geometry_source
        original_scale_mode = self.canvas.scale_mode

        try:
            exports = []

            # 1. Full cross-section in normal geometry overlay
            self.canvas.set_view_mode("full")
            self.canvas.set_overlay_mode("geometry")
            self.canvas.update()
            filepath = os.path.join(folder, "01_full_cross_section_geometry.png")
            exports.append((filepath, self.save_canvas_png_to_path(filepath)))

            # 2. Channel detail in normal geometry overlay
            self.canvas.set_view_mode("detail")
            self.canvas.set_overlay_mode("geometry")
            self.canvas.update()
            filepath = os.path.join(folder, "02_channel_detail_geometry.png")
            exports.append((filepath, self.save_canvas_png_to_path(filepath)))

            # 3. Full cross-section overlays
            self.canvas.set_view_mode("full")

            overlay_exports = [
                ("gas", "03_full_cross_section_gas_overlay.png"),
                ("thermal", "04_full_cross_section_thermal_overlay.png"),
                ("coolant", "05_full_cross_section_coolant_overlay.png"),
                ("validation", "06_full_cross_section_validation_overlay.png"),
            ]

            for overlay_mode, filename in overlay_exports:
                self.canvas.set_overlay_mode(overlay_mode)
                self.canvas.update()
                filepath = os.path.join(folder, filename)
                exports.append((filepath, self.save_canvas_png_to_path(filepath)))

            # 4. Detail overlays
            self.canvas.set_view_mode("detail")

            detail_overlay_exports = [
                ("thermal", "07_channel_detail_thermal_overlay.png"),
                ("coolant", "08_channel_detail_coolant_overlay.png"),
                ("validation", "09_channel_detail_validation_overlay.png"),
            ]

            for overlay_mode, filename in detail_overlay_exports:
                self.canvas.set_overlay_mode(overlay_mode)
                self.canvas.update()
                filepath = os.path.join(folder, filename)
                exports.append((filepath, self.save_canvas_png_to_path(filepath)))

            # 5. Station summary text
            summary_path = os.path.join(folder, "10_selected_station_summary.txt")

            with open(summary_path, "w", encoding="utf-8") as file:
                file.write(self.build_station_summary_text())

            exports.append((summary_path, True))

            failed = [path for path, success in exports if not success]

            if failed:
                QMessageBox.warning(
                    self,
                    "Figure Pack Export Partially Failed",
                    "Some files could not be exported:\n" + "\n".join(failed)
                )
            else:
                source_mode = self.results.get("source_validation_mode", "UNKNOWN")
                source_gate = self.results.get("source_validation_conservative_gate", "UNKNOWN")

                QMessageBox.information(
                    self,
                    "Figure Pack Export Complete",
                    f"Regen figure pack exported to:\n{folder}\n\n"
                    f"Source mode: {source_mode}\n"
                    f"Conservative gate: {source_gate}"
                )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Figure Pack Export Failed",
                f"Could not export figure pack:\n{exc}"
            )

        finally:
            self.canvas.set_geometry_source(original_geometry_source)
            self.canvas.set_scale_mode(original_scale_mode)
            self.canvas.set_view_mode(original_view_mode)
            self.canvas.set_overlay_mode(original_overlay_mode)
            self.update_overlay_button_styles()
            self.clear_reference_source_validation()
            self.refresh_values_panel()

    def set_show_legend(self, enabled):
        self.canvas.set_show_legend(enabled)
        self.refresh_values_panel()

    def set_show_dimensions(self, enabled):
        self.canvas.set_show_dimensions(enabled)
        self.refresh_values_panel()

    def set_overlay_mode(self, mode):
        self.canvas.set_overlay_mode(mode)
        self.update_overlay_button_styles()
        self.refresh_values_panel()

    def get_effective_nozzle_length(self):
        """
        Robust nozzle/station length resolver.

        The station slider must never collapse to zero just because nozzle_length
        is missing. It checks every known axial profile before giving up.
        """
        direct_keys = [
            "nozzle_length",
            "rao_nozzle_length",
            "conical_nozzle_length",
            "regen_nozzle_length",
            "selected_nozzle_length",
            "engine_nozzle_length",
        ]

        for key in direct_keys:
            length = self.safe_float(self.results.get(key), 0.0)
            if length > 0:
                return length

        profile_keys = [
            getattr(self.canvas, "station_profile_key", None),
            "rao_nozzle_profile",
            "conical_nozzle_profile",
            "regen_axial_profile",
            "variable_channel_geometry_profile",
            "variable_geometry_thermal_profile",
            "velocity_limited_variable_geometry_profile",
            "coupled_split_strategy_profile",
            "explicit_coating_liner_profile",
        ]

        x_values = []

        for profile_key in profile_keys:
            if not profile_key:
                continue

            profile = self.results.get(profile_key)

            if not isinstance(profile, list):
                continue

            for station in profile:
                if not isinstance(station, dict):
                    continue

                for x_key in ("x", "station_x", "axial_position", "selected_length"):
                    try:
                        x = float(station.get(x_key))
                        if x > 0:
                            x_values.append(x)
                    except Exception:
                        pass

        if x_values:
            return max(x_values)

        # Last-resort fallback so the slider remains movable instead of locked.
        return 1.0

    def safe_float(self, value, default=0.0):
        try:
            if value in (None, ""):
                return default
            return float(value)
        except Exception:
            return default

    def set_scale_mode(self, mode):
        if mode not in ("fit", "true"):
            mode = "fit"

        self.canvas.set_scale_mode(mode)
        self.results["viewer_scale_mode"] = mode
        self.refresh_scale_button_styles()
        self.refresh_values_panel()
        self.canvas.update()
        self.canvas.repaint()

    def fit_to_window(self):
        self.zoom_slider.setValue(100)
        self.canvas.set_zoom_percent(100)
        self.set_scale_mode("fit")

    def set_true_scale_mode(self):
        self.set_scale_mode("true")

    def refresh_scale_button_styles(self):
        """Synchronise the compact Scale selector with the canvas scale mode."""
        selector = getattr(
            self,
            "scale_selector",
            None,
        )

        if selector is None:
            return

        mode = str(
            self.canvas.scale_mode
            or
            "fit"
        )

        index = selector.findData(
            mode
        )

        if (
            index >= 0
            and
            selector.currentIndex()
            !=
            index
        ):
            with QSignalBlocker(
                selector
            ):
                selector.setCurrentIndex(
                    index
                )

    def set_selected_station_length(self, selected_length, source="unknown"):
        nozzle_length = self.get_effective_nozzle_length()

        try:
            selected_length = float(selected_length)
        except Exception:
            selected_length = 0.0

        effective_length = max(
            self.get_effective_nozzle_length(),
            1.0e-9
        )

        selected_length = max(
            0.0,
            min(
                selected_length,
                effective_length
            )
        )

        self.results["regen_viewer_selected_length"] = selected_length
        self.results["selected_length"] = selected_length
        self.results["regen_viewer_station_update_source"] = source

        self.canvas.results = self.results

        slider_max = max(self.station_slider.maximum(), 1)
        effective_length = max(
            self.get_effective_nozzle_length(),
            1.0e-9
        )

        slider_value = int(
            round(
                (selected_length / effective_length)
                * slider_max
            )
        )

        if source != "slider":
            with QSignalBlocker(self.station_slider):
                self.station_slider.setValue(slider_value)

        with QSignalBlocker(self.station_spinbox):
            self.station_spinbox.setMaximum(max(effective_length, 0.001))
            self.station_spinbox.setValue(selected_length)

        self.station_label.setText(
            f"Station: {selected_length:.5g} m / {effective_length:.5g} m"
        )

        if hasattr(self, "station_spinbox"):
            self.station_spinbox.clearFocus()

        self.canvas.update()
        self.refresh_station_navigation_view()

    def refresh_station_navigation_view(self):
        """
        Lightweight station-navigation refresh.

        Moving through an already-solved axial profile is viewer navigation,
        not a new engineering solve or full validation event.

        This path updates only station-dependent geometry and station values.
        Full refresh_values_panel() remains owned by actual geometry,
        validation, source, and solver-state changes.
        """
        if (
            not hasattr(self, "canvas")
            or not hasattr(self, "value_labels")
        ):
            return

        active_source = str(
            getattr(
                self.canvas,
                "geometry_source",
                "manual",
            )
            or "manual"
        ).lower()

        if active_source not in (
            "manual",
            "automatic",
        ):
            active_source = "manual"

        geometry = self.canvas.get_geometry(
            active_source
        )

        viewer_values = {
            "regen_viewer_selected_length":
                geometry.get("selected_length"),

            "viewer_geometry_source":
                self.canvas.geometry_source,

            "viewer_station_profile":
                self.canvas.station_profile_key,

            "viewer_nearest_station_x":
                self.canvas.station_value(
                    ["x"],
                    geometry.get("selected_length"),
                ),

            "viewer_station_index":
                self.canvas.station_value(
                    [
                        "station_index",
                        "source_station_index",
                        "coolant_path_index",
                    ],
                    "N/A",
                ),

            "viewer_gas_radius":
                geometry.get("gas_radius"),

            "viewer_wall_thickness":
                geometry.get("wall"),

            "viewer_coating_thickness":
                geometry.get("coating"),

            "viewer_channel_height":
                geometry.get("channel_height"),

            "viewer_channel_width":
                geometry.get("channel_width"),

            "viewer_requested_rib_width":
                geometry.get("requested_rib_width"),

            "viewer_effective_rib_width":
                geometry.get("effective_rib_width"),

            "viewer_channel_count":
                geometry.get("channel_count"),

            "viewer_requested_pitch":
                geometry.get("requested_pitch"),

            "viewer_available_pitch":
                geometry.get("available_pitch"),

            "viewer_channel_fit_ratio":
                geometry.get("channel_fit_ratio"),

            "viewer_channel_geometry_valid":
                geometry.get("channel_geometry_valid"),

            "viewer_cooling_coverage":
                geometry.get("cooling_coverage"),

            "viewer_station_mach":
                self.canvas.station_value(
                    ["mach"],
                    "N/A",
                ),

            "viewer_station_static_pressure":
                self.canvas.station_value(
                    ["static_pressure"],
                    "N/A",
                ),

            "viewer_station_static_temperature":
                self.canvas.station_value(
                    ["static_temperature"],
                    "N/A",
                ),

            "viewer_station_adiabatic_wall_temperature":
                self.canvas.station_value(
                    ["adiabatic_wall_temperature"],
                    "N/A",
                ),

            "viewer_station_heat_flux":
                self.canvas.station_value(
                    [
                        "regen_heat_flux",
                        "heat_flux",
                    ],
                    "N/A",
                ),

            "viewer_station_coolant_temperature_in":
                self.canvas.station_value(
                    ["coolant_temperature_in"],
                    "N/A",
                ),

            "viewer_station_coolant_temperature_out":
                self.canvas.station_value(
                    [
                        "coolant_temperature_out",
                        "coolant_temperature",
                    ],
                    "N/A",
                ),

            "viewer_station_coolant_velocity":
                self.canvas.station_value(
                    [
                        "coolant_velocity",
                        "variable_coolant_velocity",
                        "safe_variable_coolant_velocity",
                    ],
                    "N/A",
                ),

            "viewer_station_reynolds_number":
                self.canvas.station_value(
                    [
                        "coolant_reynolds_number",
                        "variable_reynolds_number",
                        "safe_variable_reynolds_number",
                    ],
                    "N/A",
                ),

            "viewer_station_pressure_drop_total":
                self.canvas.station_value(
                    ["total_pressure_drop_so_far"],
                    "N/A",
                ),
        }

        self.results.update(
            viewer_values
        )

        for key, value in viewer_values.items():
            label = self.value_labels.get(key)

            if label is None:
                continue

            if isinstance(value, float):
                value = f"{value:.6g}"

            label.setText(
                str(value)
            )

    def on_station_slider_changed(self, value):
        nozzle_length = self.get_effective_nozzle_length()
        slider_max = max(self.station_slider.maximum(), 1)

        selected_length = nozzle_length * (float(value) / float(slider_max))

        self.set_selected_station_length(
            selected_length,
            source="slider"
        )

    def on_station_spinbox_editing_finished(self):
        self.set_selected_station_length(
            self.station_spinbox.value(),
            source="spinbox_editing_finished"
        )

    def on_station_spinbox_changed(self, value):
        # Legacy compatibility only.
        self.set_selected_station_length(
            value,
            source="spinbox_legacy"
        )

    def on_profile_changed(self, index):
        profile_key = self.profile_selector.itemData(index)

        if profile_key:
            self.canvas.set_station_profile_key(profile_key)

            nozzle_length = self.get_effective_nozzle_length()

            with QSignalBlocker(self.station_spinbox):
                self.station_spinbox.setMaximum(max(nozzle_length, 0.001))

            current_length = self.safe_float(
                self.results.get("regen_viewer_selected_length"),
                0.0
            )

            self.set_selected_station_length(current_length, source="profile_change")

            self.canvas.update()
            self.canvas.repaint()
            self.refresh_values_panel()

    def set_view_mode(self, mode):
        if mode not in ("full", "detail"):
            mode = "full"

        self.canvas.set_view_mode(mode)

        if self.canvas.geometry_source not in ("manual", "automatic"):
            self.set_geometry_source("manual")

        self.refresh_values_panel()
        self.canvas.update()
        self.canvas.repaint()

    def set_geometry_source(self, source):
        """
        Route geometry-source button requests into the canvas.
        Buttons are controls only; the canvas owns the actual geometry source.
        """
        if source not in ("manual", "automatic"):
            source = "manual"

        automatic_data = (
            self.results.get(
                "regen_ui_applied_geometry"
            )
            or self.results.get(
                "regen_viewer_accepted_geometry"
            )
            or self.results.get(
                "regen_geometry_commit_staged_geometry"
            )
            or self.results.get(
                "regen_autonomous_geometry_staged_candidate",
                {},
            ).get(
                "staged_geometry",
                {},
            )
            or {}
        )

        if source == "automatic" and not automatic_data:
            self.results["regen_viewer_automatic_geometry_warning"] = (
                "Automatic geometry selected, but no staged automatic geometry exists. "
                "Displaying manual fallback."
            )
        else:
            self.results["regen_viewer_automatic_geometry_warning"] = ""

        self.canvas.set_geometry_source(source)

        geometry = self.canvas.get_geometry(source)

        self.results["regen_viewer_requested_geometry_source"] = source
        self.results["regen_viewer_actual_geometry_source"] = geometry.get("source")
        self.results["regen_viewer_debug_channel_count"] = geometry.get("channel_count")
        self.results["regen_viewer_debug_channel_width"] = geometry.get("channel_width")
        self.results["regen_viewer_debug_channel_height"] = geometry.get("channel_height")
        self.results["regen_viewer_debug_gas_radius"] = geometry.get("gas_radius")

        self.refresh_geometry_source_button_styles()
        self.refresh_values_panel()

        self.canvas.update()
        self.canvas.repaint()

    def refresh_geometry_source_button_styles(self):
        """
        Visual feedback only. Buttons remain push buttons, not toggle buttons.
        """
        active = self.canvas.geometry_source

        button_map = {
            "automatic": self.automatic_button,
        }

        for source, button in button_map.items():
            if source == active:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #4d6f9f;
                        color: white;
                        font-weight: bold;
                        border: 1px solid #8fb2ff;
                        padding: 3px 8px;
                    }
                """)
            else:
                button.setStyleSheet("")

    def build_body(self):
        """
        Main workspace body:
        - canvas on the left
        - draggable inspector on the right
        - inspector has no fixed maximum width
        """

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.body_splitter = InspectorSplitter(Qt.Horizontal)
        self.body_splitter.setChildrenCollapsible(False)
        self.body_splitter.setHandleWidth(10)

        self.canvas.setMinimumWidth(520)

        inspector = self.build_inspector_panel()
        inspector.setMinimumWidth(300)
        inspector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.body_splitter.addWidget(self.canvas)
        self.body_splitter.addWidget(inspector)

        self.body_splitter.setStretchFactor(0, 5)
        self.body_splitter.setStretchFactor(1, 2)
        self.body_splitter.setSizes([900, 460])

        layout.addWidget(self.body_splitter)

        return layout

    def build_inspector_panel(self):
        inspector_container = QWidget()
        inspector_layout = QVBoxLayout(inspector_container)
        inspector_layout.setContentsMargins(0, 0, 0, 0)
        inspector_layout.setSpacing(4)

        resize_hint = QLabel("⋮⋮ Drag divider to resize inspector")
        resize_hint.setAlignment(Qt.AlignCenter)
        resize_hint.setFixedHeight(20)
        resize_hint.setStyleSheet("""
            QLabel {
                color: #b8b8b8;
                background-color: #333333;
                border-bottom: 1px solid #555555;
                font-size: 10px;
            }
        """)

        self.inspector_tabs = QTabWidget()
        self.value_labels = {}

        self.inspector_tabs.addTab(
            self.build_overview_tab(),
            "Overview"
        )

        self.inspector_tabs.addTab(
            self.build_geometry_tab(),
            "Geometry"
        )

        self.inspector_tabs.addTab(
            self.build_station_tab(),
            "Station"
        )

        self.inspector_tabs.addTab(
            self.build_validation_tab(),
            "Validation"
        )

        self.inspector_tabs.addTab(
            self.build_source_tab(),
            "Sources"
        )

        self.inspector_tabs.addTab(
            self.build_reference_tab(),
            "Reference"
        )

        self.inspector_tabs.addTab(
            self.build_export_tab(),
            "Export"
        )

        self.refresh_values_panel()

        inspector_layout.addWidget(resize_hint)
        inspector_layout.addWidget(self.inspector_tabs)

        return inspector_container

    def make_inspector_button(self, text, callback=None):
        button = InspectorButton(text)

        if callback is not None:
            button.clicked.connect(callback)

        return button

    def make_inspector_label(self, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setMinimumWidth(0)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        return label

    def add_value_row(self, form, label_text, key):
        name_label = QLabel(label_text)
        name_label.setWordWrap(True)
        name_label.setMinimumWidth(0)
        name_label.setMaximumWidth(130)
        name_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        value_label = QLabel("N/A")
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        value_label.setMinimumWidth(0)
        value_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        self.value_labels[key] = value_label
        form.addRow(name_label, value_label)

    def create_value_group(self, title, rows):
        group = QGroupBox(title)
        group.setMinimumWidth(0)
        group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)

        form = QFormLayout(group)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form.setContentsMargins(8, 8, 8, 8)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(8)

        for label_text, key in rows:
            self.add_value_row(form, label_text, key)

        return group

    def create_scroll_tab(self, groups):
        container = QWidget()
        container.setMinimumWidth(0)
        container.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        for group in groups:
            group.setMinimumWidth(0)
            group.setMaximumWidth(16777215)
            group.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)
            layout.addWidget(group)

        layout.addStretch()

        scroll = InspectorScrollArea()
        scroll.setWidget(container)

        return scroll

    def wrap_tab_in_vertical_scroll(self, tab):
        tab.setMinimumWidth(0)
        tab.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)

        scroll = InspectorScrollArea()
        scroll.setWidget(tab)

        return scroll

    def wrap_tab_in_scroll_area(self, tab):
        tab.setMinimumWidth(0)
        tab.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)

        scroll = InspectorScrollArea()
        scroll.setWidget(tab)

        return scroll

    def build_overview_tab(self):
        groups = [
            self.create_value_group(
                "Regen Status",
                [
                    ("Overall", "regen_overall_status"),
                    ("Geometry", "regen_geometry_status"),
                    ("Thermal", "regen_thermal_status"),
                    ("Coolant", "regen_coolant_status"),
                    ("Material", "regen_material_status"),
                    ("Final Verdict", "final_regen_design_verdict"),
                ],
            ),
            self.create_value_group(
                "Current Workspace",
                [
                    ("View Mode", "viewer_view_mode"),
                    ("Geometry Source", "viewer_geometry_source"),
                    ("Overlay Mode", "viewer_overlay_mode"),
                    ("Scale Mode", "viewer_scale_mode"),
                    ("Station Profile", "viewer_station_profile"),
                    ("Legend Visible", "viewer_show_legend"),
                    ("Dimensions Visible", "viewer_show_dimensions"),
                ],
            ),
            self.create_value_group(
                "Quick Health",
                [
                    ("Geometry Valid", "viewer_channel_geometry_valid"),
                    ("Fit Ratio", "viewer_channel_fit_ratio"),
                    ("Cooling Coverage", "viewer_cooling_coverage"),
                    ("Source Mode", "source_validation_mode"),
                    ("Source Gate", "source_validation_conservative_gate"),
                    ("Reference Verdict", "reference_validation_verdict"),
                    ("Source Maturity", "viewer_source_maturity_status"),
                ],
            ),
        ]

        return self.create_scroll_tab(groups)

    def build_geometry_tab(self):
        groups = [
            self.create_value_group(
                "Selected Geometry",
                [
                    ("Selected Station", "regen_viewer_selected_length"),
                    ("Gas Radius", "viewer_gas_radius"),
                    ("Wall Thickness", "viewer_wall_thickness"),
                    ("Coating Thickness", "viewer_coating_thickness"),
                    ("Channel Height", "viewer_channel_height"),
                    ("Channel Width", "viewer_channel_width"),
                    ("Requested Rib Width", "viewer_requested_rib_width"),
                    ("Effective Rib Width", "viewer_effective_rib_width"),
                    ("Channel Count", "viewer_channel_count"),
                    ("Requested Pitch", "viewer_requested_pitch"),
                    ("Available Pitch", "viewer_available_pitch"),
                    ("Fit Ratio", "viewer_channel_fit_ratio"),
                ],
            ),
            self.create_value_group(
                "Recommended Geometry",
                [
                    ("Status", "recommended_geometry_status"),
                    ("Channels", "recommended_channel_count"),
                    ("Width", "recommended_channel_width"),
                    ("Height", "recommended_channel_height"),
                    ("Rib", "recommended_rib_width"),
                    ("Pitch", "recommended_channel_pitch"),
                    ("Effective Rib", "recommended_effective_rib_width"),
                    ("Fit Ratio", "recommended_channel_fit_ratio"),
                    ("Valid", "recommended_geometry_valid"),
                    ("Coverage", "recommended_circumferential_cooling_coverage"),
                    ("Velocity", "recommended_coolant_velocity"),
                    ("Reynolds", "recommended_reynolds_number"),
                    ("Tightest Radius", "recommended_tightest_gas_radius"),
                ],
            ),
        ]

        return self.create_scroll_tab(groups)

    def build_station_tab(self):
        groups = [
            self.create_value_group(
                "Station Selection",
                [
                    ("Selected x", "regen_viewer_selected_length"),
                    ("Nearest Station x", "viewer_nearest_station_x"),
                    ("Station Index / Path", "viewer_station_index"),
                    ("Profile", "viewer_station_profile"),
                    ("Profile Meaning", "viewer_station_profile_explanation"),
                ],
            ),
            self.create_value_group(
                "Gas-Side Station Data",
                [
                    ("Mach", "viewer_station_mach"),
                    ("Static Pressure", "viewer_station_static_pressure"),
                    ("Static Temperature", "viewer_station_static_temperature"),
                    ("Adiabatic Wall Temp", "viewer_station_adiabatic_wall_temperature"),
                    ("Heat Flux", "viewer_station_heat_flux"),
                ],
            ),
            self.create_value_group(
                "Coolant Station Data",
                [
                    ("Coolant In", "viewer_station_coolant_temperature_in"),
                    ("Coolant Out", "viewer_station_coolant_temperature_out"),
                    ("Coolant Velocity", "viewer_station_coolant_velocity"),
                    ("Reynolds Number", "viewer_station_reynolds_number"),
                    ("Pressure Drop Total", "viewer_station_pressure_drop_total"),
                ],
            ),
        ]

        return self.create_scroll_tab(groups)

    def build_validation_tab(self):
        groups = [
            self.create_value_group(
                "Cooling Validation",
                [
                    ("Feasibility", "regen_feasibility_status"),
                    ("Strategy", "regen_selected_cooling_strategy"),
                    ("Film Status", "film_cooling_status"),
                    ("Combined Status", "combined_cooling_allocation_status"),
                    ("Combined Prediction", "combined_cooling_prediction_status"),
                    ("Cooling Confidence", "combined_cooling_confidence"),
                    ("Confidence Score", "combined_cooling_confidence_score"),
                ],
            ),
            self.create_value_group(
                "Sign-Off",
                [
                    ("Sign-Off Status", "viewer_signoff_status"),
                    ("Checklist", "viewer_signoff_checklist"),
                    ("Source Maturity Score", "viewer_source_maturity_score"),
                    ("Source Maturity Status", "viewer_source_maturity_status"),
                    ("Scalability Status", "regen_scalability_validation_status"),
                    ("Reference Verdict", "reference_validation_verdict"),
                    ("Reference Action", "reference_validation_recommendation"),
                    ("External Testing Ready", "viewer_external_testing_ready"),
                ],
            ),

            self.create_value_group(
                "Reference Engine Validation",
                [
                    ("Reference Engine", "reference_engine_display_name"),
                    ("Reference Status", "regen_scalability_validation_status"),
                    ("Source Status", "reference_engine_source_status"),
                    ("Agreement", "reference_engine_overall_agreement_percent"),
                    ("Mean Error", "reference_engine_mean_error_percent"),
                    ("Comparison Count", "reference_engine_comparison_count"),
                    ("Note", "reference_engine_validation_note"),
                    ("Reference Verdict", "reference_validation_verdict"),
                    ("Reference Action", "reference_validation_recommendation"),
                    ("Reference Ledger Status", "reference_source_ledger_status"),
                    ("Reference Ledger Action", "reference_source_ledger_recommendation"),
                ],
            ),

            self.create_value_group(
                "Reference Error Breakdown",
                [
                    ("Channel Width Error", "reference_engine_channel_width_error_percent"),
                    ("Channel Height Error", "reference_engine_channel_height_error_percent"),
                    ("Channel Count Error", "reference_engine_channel_count_error_percent"),
                    ("Wall Thickness Error", "reference_engine_wall_thickness_error_percent"),
                    ("Coolant Velocity Error", "reference_engine_coolant_velocity_error_percent"),
                    ("Pressure Drop Error", "reference_engine_pressure_drop_error_percent"),
                    ("Coolant ΔT Error", "reference_engine_coolant_temperature_rise_error_percent"),
                ],
            ),
        ]

        return self.create_scroll_tab(groups)

    def build_source_tab(self):
        groups = [
            self.create_value_group(
                "Source Gate",
                [
                    ("Source Mode", "source_validation_mode"),
                    ("Conservative Gate", "source_validation_conservative_gate"),
                    ("Source Status", "regen_source_validation_status"),
                    ("Recommendation", "regen_source_validation_recommendation"),
                ],
            ),
            self.create_value_group(
                "Material Evidence",
                [
                    ("Material Mode", "material_validation_mode"),
                    ("Material Score", "material_source_validation_score"),
                    ("Has Citation", "material_source_has_citation"),
                    ("Has Temp Table", "material_source_has_temperature_table"),
                    ("Is Placeholder", "material_source_is_placeholder"),
                    ("Recommendation", "material_source_validation_recommendation"),
                ],
            ),
            self.create_value_group(
                "Coating / Bond Evidence",
                [
                    ("Coating Mode", "coating_validation_mode"),
                    ("Coating Score", "coating_source_validation_score"),
                    ("Coating Citation", "coating_source_has_citation"),
                    ("Coating Temp Table", "coating_source_has_temperature_table"),
                    ("Bond Mode", "bond_coat_validation_mode"),
                    ("Bond Score", "bond_coat_source_validation_score"),
                    ("Bond Citation", "bond_coat_source_has_citation"),
                    ("Bond Temp Table", "bond_coat_source_has_temperature_table"),
                ],
            ),
        ]

        return self.create_scroll_tab(groups)

    def build_reference_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        status_strip_group = self.create_value_group(
            "Reference Validation Status",
            [
                ("Selected", "reference_engine_display_name"),
                ("Database Usefulness", "viewer_reference_db_usefulness_status"),
                ("Readiness", "viewer_reference_readiness_status"),
                ("Run Gate", "reference_comparison_run_gate_status"),
                ("Verdict", "reference_validation_verdict"),
                ("Next Action", "reference_validation_recommendation"),
            ],
        )

        selector_group = QGroupBox("Reference Engine Selection")
        selector_layout = QVBoxLayout(selector_group)

        self.reference_engine_selector = QComboBox()
        self.reference_engine_selector.addItem("None", "")

        if get_reference_engine_names is not None:
            for name in get_reference_engine_names():
                self.reference_engine_selector.addItem(name, name)

        current_reference = (
            self.results.get("reference_engine_name")
            or self.results.get("selected_reference_engine")
            or self.results.get("validation_reference_engine")
            or ""
        )

        index = self.reference_engine_selector.findData(current_reference)
        if index >= 0:
            self.reference_engine_selector.setCurrentIndex(index)

        self.reference_engine_selector.currentIndexChanged.connect(
            self.on_reference_engine_changed
        )

        selector_layout.addWidget(self.make_inspector_label(
            "Select a reference engine for order-of-magnitude validation:"
        ))
        selector_layout.addWidget(self.reference_engine_selector)

        info_group = self.create_value_group(
            "Selected Reference Engine",
            [
                ("Reference Engine", "reference_engine_display_name"),
                ("Validation Status", "regen_scalability_validation_status"),
                ("Source Status", "reference_engine_source_status"),
                ("Agreement", "reference_engine_overall_agreement_percent"),
                ("Mean Error", "reference_engine_mean_error_percent"),
                ("Comparison Count", "reference_engine_comparison_count"),
                ("Note", "reference_engine_validation_note"),
            ],
        )

        rebuild_mode_group = self.create_value_group(
            "Reference Rebuild Mode",
            [
                ("Rebuild Status", "viewer_reference_rebuild_status"),
                ("Rebuild Mode", "viewer_reference_rebuild_mode"),
                ("Input Ready", "viewer_reference_rebuild_input_ready"),
                ("Geometry Ready", "viewer_reference_rebuild_geometry_ready"),
                ("Comparison Ready", "viewer_reference_rebuild_comparison_ready"),
                ("Filled Inputs", "viewer_reference_rebuild_filled_inputs"),
                ("Filled Geometry", "viewer_reference_rebuild_filled_geometry"),
                ("Filled Comparison", "viewer_reference_rebuild_filled_comparison"),
                ("Rebuild Action", "viewer_reference_rebuild_recommendation"),
            ],
        )

        database_completeness_group = self.create_value_group(
            "Database Completeness",
            [
                ("Input Fields", "viewer_reference_db_input_completeness"),
                ("Geometry Fields", "viewer_reference_db_geometry_completeness"),
                ("Comparison Fields", "viewer_reference_db_comparison_completeness"),
                ("Source Fields", "viewer_reference_db_source_completeness"),
                ("Overall Completeness", "viewer_reference_db_overall_completeness"),
                ("Database Usefulness", "viewer_reference_db_usefulness_status"),
                ("Next Data Action", "viewer_reference_db_next_action"),
            ],
        )

        action_checklist_group = QGroupBox("Reference Data Action Checklist")
        action_checklist_layout = QVBoxLayout(action_checklist_group)

        self.reference_action_checklist_label = QLabel(
            "Select a reference engine to see required database actions."
        )
        self.reference_action_checklist_label.setWordWrap(True)

        action_checklist_layout.addWidget(self.reference_action_checklist_label)

        database_group = self.create_value_group(
            "Stored Database Record",
            [
                ("Fuel", "viewer_reference_db_fuel"),
                ("Oxidizer", "viewer_reference_db_oxidizer"),
                ("Mixture Ratio", "viewer_reference_db_mixture_ratio"),
                ("Mass Flow Rate", "viewer_reference_db_mass_flow_rate"),
                ("Chamber Pressure", "viewer_reference_db_chamber_pressure"),
                ("Characteristic Length", "viewer_reference_db_characteristic_length"),
                ("Ambient Pressure", "viewer_reference_db_ambient_pressure"),
                ("Thrust", "viewer_reference_db_thrust_n"),
                ("Throat Area", "viewer_reference_db_throat_area_m2"),
                ("Exit Area", "viewer_reference_db_exit_area_m2"),
                ("Throat Radius", "viewer_reference_db_throat_radius_m"),
                ("Exit Radius", "viewer_reference_db_exit_radius_m"),
                ("Nozzle Length", "viewer_reference_db_nozzle_length_m"),
                ("Channel Count", "viewer_reference_db_channel_count"),
                ("Channel Width", "viewer_reference_db_channel_width_m"),
                ("Channel Height", "viewer_reference_db_channel_height_m"),
                ("Wall Thickness", "viewer_reference_db_wall_thickness_m"),
                ("Coolant Velocity", "viewer_reference_db_coolant_velocity_m_s"),
                ("Pressure Drop", "viewer_reference_db_pressure_drop_pa"),
                ("Coolant ΔT", "viewer_reference_db_coolant_temperature_rise_k"),
                ("Source Title", "viewer_reference_db_source_title"),
                ("Source Author", "viewer_reference_db_source_author"),
                ("Source Year", "viewer_reference_db_source_year"),
                ("DOI", "viewer_reference_db_doi"),
                ("URL", "viewer_reference_db_url"),
                ("Notes", "viewer_reference_db_notes"),
            ],
        )

        schema_audit_group = self.create_value_group(
            "Reference Schema Audit",
            [
                ("Selected Schema Status", "viewer_reference_schema_status"),
                ("Missing Top-Level Fields", "viewer_reference_schema_missing_top_level"),
                ("Missing Nested Fields", "viewer_reference_schema_missing_nested"),
                ("Unexpected Section Types", "viewer_reference_schema_unexpected_types"),
                ("All-Engine Schema Status", "viewer_reference_all_schema_status"),
                ("Broken Engine Count", "viewer_reference_schema_broken_count"),
                ("Schema Action", "viewer_reference_schema_recommendation"),
            ],
        )

        candidate_readiness_group = self.create_value_group(
            "Candidate Promotion Readiness",
            [
                ("Candidate Status", "viewer_candidate_promotion_status"),
                ("Ready Candidates", "viewer_candidate_promotion_ready_count"),
                ("Total Candidates", "viewer_candidate_promotion_candidate_count"),
                ("Missing Requirements", "viewer_candidate_promotion_missing_requirements"),
                ("Candidate Action", "viewer_candidate_promotion_recommendation"),
            ],
        )

        candidate_delta_group = self.create_value_group(
            "Candidate Promotion Completeness Delta",
            [
                ("Delta Status", "viewer_candidate_delta_status"),
                ("Before Inputs", "viewer_candidate_delta_before_inputs"),
                ("After Inputs", "viewer_candidate_delta_after_inputs"),
                ("Before Comparison", "viewer_candidate_delta_before_comparison"),
                ("After Comparison", "viewer_candidate_delta_after_comparison"),
                ("Improved Fields", "viewer_candidate_delta_improved_fields"),
                ("Delta Action", "viewer_candidate_delta_recommendation"),
            ],
        )

        candidate_group = QGroupBox("Candidate Reference Values")
        candidate_layout = QVBoxLayout(candidate_group)

        self.reference_candidate_values_label = QLabel(
            "Select a reference engine to view candidate/public values."
        )
        self.reference_candidate_values_label.setWordWrap(True)

        candidate_layout.addWidget(self.reference_candidate_values_label)

        status_consistency_group = self.create_value_group(
            "Status Consistency",
            [
                ("Consistency", "viewer_reference_status_consistency"),
                ("Mismatch Count", "viewer_reference_status_mismatch_count"),
                ("Mismatches", "viewer_reference_status_mismatches"),
                ("Consistency Action", "viewer_reference_status_consistency_recommendation"),
                ("Raw Source Status", "viewer_reference_raw_source_status"),
                ("Raw Quality Band", "viewer_reference_raw_quality_band"),
                ("Raw Quality Score", "viewer_reference_raw_quality_score"),
            ],
        )

        auto_status_group = self.create_value_group(
            "Auto-Derived Record Status",
            [
                ("Derived Source Status", "viewer_reference_auto_source_status"),
                ("Derived Quality Band", "viewer_reference_auto_quality_band"),
                ("Derived Quality Score", "viewer_reference_auto_quality_score"),
                ("Derived Ledger Status", "viewer_reference_auto_ledger_status"),
                ("Derived Ledger Coverage", "viewer_reference_auto_ledger_coverage"),
            ],
        )

        data_quality_group = self.create_value_group(
            "Reference Data Quality",
            [
                ("Quality Band", "viewer_reference_data_quality_band"),
                ("Quality Score", "viewer_reference_data_quality_score"),
                ("Quality Status", "viewer_reference_data_quality_status"),
                ("Quality Action", "viewer_reference_data_quality_recommendation"),
                ("Solver Quality Band", "reference_data_quality_band"),
                ("Solver Quality Score", "reference_data_quality_score"),
            ],
        )

        ledger_coverage_group = self.create_value_group(
            "Source Ledger Coverage",
            [
                ("Ledger Status", "viewer_reference_ledger_status"),
                ("Covered Values", "viewer_reference_ledger_covered_count"),
                ("Filled Values", "viewer_reference_ledger_filled_count"),
                ("Coverage", "viewer_reference_ledger_coverage_percent"),
                ("Missing Notes", "viewer_reference_ledger_missing_notes"),
                ("Ledger Action", "viewer_reference_ledger_recommendation"),
                ("Solver Ledger Status", "reference_source_ledger_status"),
                ("Solver Missing Notes", "reference_source_ledger_missing_notes"),
            ],
        )

        origin_group = self.create_value_group(
            "Value Origin Coverage",
            [
                ("Origin Status", "viewer_reference_origin_status"),
                ("Filled Values", "viewer_reference_origin_filled_count"),
                ("Tagged Values", "viewer_reference_origin_tagged_count"),
                ("Missing Origin Tags", "viewer_reference_origin_missing_fields"),
                ("Blocked Fields", "viewer_reference_origin_blocked_fields"),
                ("Origin Action", "viewer_reference_origin_recommendation"),
            ],
        )

        source_ledger_group = QGroupBox("Source Ledger")
        source_ledger_layout = QVBoxLayout(source_ledger_group)

        self.reference_source_ledger_label = QLabel(
            "Select a reference engine to view value-level source notes."
        )
        self.reference_source_ledger_label.setWordWrap(True)

        source_ledger_layout.addWidget(self.reference_source_ledger_label)

        source_target_group = QGroupBox("Source Acquisition Targets")
        source_target_layout = QVBoxLayout(source_target_group)

        self.reference_source_target_label = QLabel(
            "Select a reference engine to view where each missing value should be sourced from."
        )
        self.reference_source_target_label.setWordWrap(True)

        source_target_layout.addWidget(self.reference_source_target_label)

        value_entry_group = QGroupBox("Reference Value Entry Checklist")
        value_entry_layout = QVBoxLayout(value_entry_group)

        self.reference_value_entry_label = QLabel(
            "Select a reference engine to inspect value-entry readiness."
        )
        self.reference_value_entry_label.setWordWrap(True)

        value_entry_layout.addWidget(self.reference_value_entry_label)





        source_validation_group = self.create_value_group(
            "Reference Source Validation",
            [
                ("Record Status", "viewer_reference_record_status"),
                ("Filled Comparison Fields", "viewer_reference_filled_comparison_count"),
                ("Filled Source Fields", "viewer_reference_filled_source_count"),
                ("Missing Inputs", "viewer_reference_missing_inputs"),
                ("Missing Comparison", "viewer_reference_missing_comparison_fields"),
                ("Missing Source Metadata", "viewer_reference_missing_source_fields"),
                ("Recommendation", "viewer_reference_record_recommendation"),
                ("Input Preset Status", "viewer_reference_input_preset_status"),
                ("Comparison Status", "viewer_reference_comparison_status"),
                ("Filled Input Fields", "viewer_reference_filled_input_count"),
                ("Readiness", "viewer_reference_readiness_status"),
                ("Input Ready", "viewer_reference_input_ready"),
                ("Comparison Ready", "viewer_reference_comparison_ready"),
                ("Source Ready", "viewer_reference_source_ready"),
                ("Readiness Action", "viewer_reference_readiness_recommendation"),
            ],
        )

        imported_template_group = self.create_value_group(
            "Imported Template Preview",
            [
                ("Imported Key", "viewer_imported_reference_key"),
                ("Parse Status", "viewer_imported_reference_parse_status"),
                ("Record Status", "viewer_imported_reference_record_status"),
                ("Filled Comparison", "viewer_imported_reference_filled_comparison_count"),
                ("Filled Source", "viewer_imported_reference_filled_source_count"),
                ("Missing Inputs", "viewer_imported_reference_missing_inputs"),
                ("Missing Comparison", "viewer_imported_reference_missing_comparison_fields"),
                ("Missing Source", "viewer_imported_reference_missing_source_fields"),
                ("Recommendation", "viewer_imported_reference_recommendation"),
                ("Input Preset Status", "viewer_imported_reference_input_preset_status"),
                ("Comparison Status", "viewer_imported_reference_comparison_status"),
                ("Filled Input Fields", "viewer_imported_reference_filled_input_count"),
                ("Readiness", "viewer_imported_reference_readiness_status"),
                ("Input Ready", "viewer_imported_reference_input_ready"),
                ("Comparison Ready", "viewer_imported_reference_comparison_ready"),
                ("Source Ready", "viewer_imported_reference_source_ready"),
                ("Readiness Action", "viewer_imported_reference_readiness_recommendation"),
            ],
        )

        run_gate_group = self.create_value_group(
            "Comparison Run Gate",
            [
                ("Run Gate", "reference_comparison_run_gate_status"),
                ("Ready", "reference_comparison_ready"),
                ("Missing LEAF Fields", "reference_comparison_missing_leaf_fields"),
                ("Missing Reference Fields", "reference_comparison_missing_reference_fields"),
                ("Ready Fields", "reference_comparison_ready_field_count"),
                ("Total Fields", "reference_comparison_total_field_count"),
            ],
        )

        verdict_group = self.create_value_group(
            "Reference Validation Verdict",
            [
                ("Verdict", "reference_validation_verdict"),
                ("Recommendation", "reference_validation_recommendation"),
                ("Ledger Status", "reference_source_ledger_status"),
                ("Ledger Recommendation", "reference_source_ledger_recommendation"),
            ],
        )

        quality_group = self.create_value_group(
            "Comparison Quality",
            [
                ("Quality Status", "reference_comparison_quality_status"),
                ("Average Error", "reference_comparison_average_error_percent"),
                ("Agreement", "reference_comparison_agreement_percent"),
                ("Best Field", "reference_comparison_best_field"),
                ("Worst Field", "reference_comparison_worst_field"),
                ("Recommendation", "reference_comparison_quality_recommendation"),
            ],
        )

        evidence_group = QGroupBox("Comparison Evidence")
        evidence_layout = QVBoxLayout(evidence_group)

        self.reference_evidence_label = QLabel("Select a reference engine to view comparison evidence.")
        self.reference_evidence_label.setWordWrap(True)

        evidence_layout.addWidget(self.reference_evidence_label)

        breakdown_group = self.create_value_group(
            "Error Breakdown",
            [
                ("Channel Width Error", "reference_engine_channel_width_error_percent"),
                ("Channel Height Error", "reference_engine_channel_height_error_percent"),
                ("Channel Count Error", "reference_engine_channel_count_error_percent"),
                ("Wall Thickness Error", "reference_engine_wall_thickness_error_percent"),
                ("Coolant Velocity Error", "reference_engine_coolant_velocity_error_percent"),
                ("Pressure Drop Error", "reference_engine_pressure_drop_error_percent"),
                ("Coolant ΔT Error", "reference_engine_coolant_temperature_rise_error_percent"),
            ],
        )

        preset_group = QGroupBox("Future Input Preset Preview")
        preset_layout = QVBoxLayout(preset_group)

        self.reference_input_preview_label = QLabel(
            "Select a reference engine to preview loadable minimum inputs."
        )
        self.reference_input_preview_label.setWordWrap(True)

        self.export_reference_input_summary_button = self.make_inspector_button(
            "Export Input Preset Summary",
            self.export_reference_input_summary,
        )

        self.export_reference_database_report_button = self.make_inspector_button(
            "Export Database Completeness Report",
            self.export_reference_database_report,
        )

        self.export_reference_fill_assistant_button = self.make_inspector_button(
            "Export Direct Database Fill Guide",
            self.export_reference_fill_assistant,
        )

        self.export_reference_ledger_audit_button = self.make_inspector_button(
            "Export Source Ledger Audit",
            self.export_reference_ledger_audit,
        )



        self.copy_candidate_promotion_preview_button = self.make_inspector_button(
            "Copy Candidate Promotion Preview",
            self.copy_candidate_promotion_preview,
        )

        self.copy_schema_repair_patch_button = self.make_inspector_button(
            "Copy Schema Repair Patch",
            self.copy_schema_repair_patch,
        )

        self.copy_reference_self_test_button = self.make_inspector_button(
            "Copy Reference Database Self-Test",
            self.copy_reference_database_self_test,
        )

        self.copy_candidate_readiness_button = self.make_inspector_button(
            "Copy Candidate Readiness Report",
            self.copy_candidate_readiness_report,
        )

        self.copy_candidate_promotion_patch_button = self.make_inspector_button(
            "Copy Candidate Promotion Patch",
            self.copy_candidate_promotion_patch,
        )

        self.copy_candidate_apply_preview_button = self.make_inspector_button(
            "Copy Candidate Apply Preview",
            self.copy_candidate_apply_preview,
        )

        self.copy_candidate_delta_button = self.make_inspector_button(
            "Copy Candidate Delta Report",
            self.copy_candidate_delta_report,
        )

        self.copy_reference_rebuild_report_button = self.make_inspector_button(
            "Copy Reference Rebuild Report",
            self.copy_reference_rebuild_report,
        )

        self.copy_reference_rebuild_inputs_button = self.make_inspector_button(
            "Copy Reference Rebuild Inputs",
            self.copy_reference_rebuild_inputs,
        )

        self.copy_reference_rebuild_load_preview_button = self.make_inspector_button(
            "Copy Rebuild Input Apply Plan",
            self.copy_reference_rebuild_load_preview,
        )

        self.copy_reference_rebuild_session_button = self.make_inspector_button(
            "Copy Rebuild Session Report",
            self.copy_reference_rebuild_session_report,
        )

        self.copy_reference_rebuild_run_record_button = self.make_inspector_button(
            "Copy Rebuild Run Record",
            self.copy_reference_rebuild_run_record_report,
        )

        self.copy_reference_rebuild_result_export_button = self.make_inspector_button(
            "Copy Full Rebuild Result Export",
            self.copy_reference_rebuild_result_export,
        )

        self.copy_reference_geometry_comparison_button = self.make_inspector_button(
            "Copy Reference Geometry Comparison",
            self.copy_reference_geometry_comparison_report,
        )

        self.copy_reference_regen_geometry_comparison_button = self.make_inspector_button(
            "Copy Reference Regen Geometry Comparison",
            self.copy_reference_regen_geometry_comparison_report,
        )

        self.export_reference_regen_geometry_comparison_button = self.make_inspector_button(
            "Export Regen Geometry Comparison .txt",
            self.export_reference_regen_geometry_comparison_txt,
        )

        self.export_reference_geometry_comparison_button = self.make_inspector_button(
            "Export Geometry Comparison .txt",
            self.export_reference_geometry_comparison_txt,
        )

        self.export_reference_rebuild_result_export_button = self.make_inspector_button(
            "Export Full Rebuild Result .txt",
            self.export_reference_rebuild_result_export_txt,
        )

        preset_layout.addWidget(self.reference_input_preview_label)
        preset_layout.addWidget(self.export_reference_input_summary_button)
        preset_layout.addWidget(self.export_reference_database_report_button)
        preset_layout.addWidget(self.export_reference_fill_assistant_button)
        preset_layout.addWidget(self.export_reference_ledger_audit_button)
        preset_layout.addWidget(self.copy_candidate_promotion_preview_button)
        preset_layout.addWidget(self.copy_schema_repair_patch_button)
        preset_layout.addWidget(self.copy_reference_self_test_button)
        preset_layout.addWidget(self.copy_candidate_readiness_button)
        preset_layout.addWidget(self.copy_candidate_promotion_patch_button)
        preset_layout.addWidget(self.copy_candidate_apply_preview_button)
        preset_layout.addWidget(self.copy_candidate_delta_button)
        preset_layout.addWidget(self.copy_reference_rebuild_report_button)
        preset_layout.addWidget(self.copy_reference_rebuild_inputs_button)
        preset_layout.addWidget(self.copy_reference_rebuild_load_preview_button)
        preset_layout.addWidget(self.copy_reference_rebuild_session_button)
        preset_layout.addWidget(self.copy_reference_rebuild_run_record_button)
        preset_layout.addWidget(self.copy_reference_rebuild_result_export_button)
        preset_layout.addWidget(self.copy_reference_geometry_comparison_button)
        preset_layout.addWidget(self.copy_reference_regen_geometry_comparison_button)
        preset_layout.addWidget(self.export_reference_regen_geometry_comparison_button)
        preset_layout.addWidget(self.export_reference_geometry_comparison_button)
        preset_layout.addWidget(self.export_reference_rebuild_result_export_button)

        import_group = QGroupBox("Import / Validate Filled Template")
        import_layout = QVBoxLayout(import_group)

        self.import_reference_template_button = self.make_inspector_button(
            "Import Template Preview",
            self.import_reference_template_preview,
        )

        self.export_reference_patch_button = self.make_inspector_button(
            "Export Database Patch",
            self.export_reference_database_patch,
        )
        self.export_reference_patch_button.setEnabled(False)

        import_layout.addWidget(self.make_inspector_label(
            "Load a filled exported template and preview whether it is ready to paste into reference_engine_database.py."
        ))
        import_layout.addWidget(self.import_reference_template_button)
        import_layout.addWidget(self.export_reference_patch_button)

        export_group = QGroupBox("Reference Source Template")
        export_layout = QVBoxLayout(export_group)

        self.export_reference_template_button = self.make_inspector_button(
            "Export Source Template",
            self.export_reference_source_template,
        )

        export_layout.addWidget(self.make_inspector_label(
            "Exports a blank template showing what public data must be sourced before this reference engine can produce a meaningful comparison."
        ))
        export_layout.addWidget(self.export_reference_template_button)

        layout.addWidget(status_strip_group)
        layout.addWidget(selector_group)
        layout.addWidget(info_group)
        layout.addWidget(rebuild_mode_group)
        layout.addWidget(database_completeness_group)
        layout.addWidget(action_checklist_group)
        layout.addWidget(database_group)
        layout.addWidget(schema_audit_group)
        layout.addWidget(candidate_readiness_group)
        layout.addWidget(candidate_delta_group)
        layout.addWidget(candidate_group)
        layout.addWidget(data_quality_group)
        layout.addWidget(auto_status_group)
        layout.addWidget(status_consistency_group)
        layout.addWidget(ledger_coverage_group)
        layout.addWidget(origin_group)
        layout.addWidget(source_ledger_group)
        layout.addWidget(source_target_group)
        layout.addWidget(value_entry_group)
        layout.addWidget(source_validation_group)
        layout.addWidget(imported_template_group)
        layout.addWidget(run_gate_group)
        layout.addWidget(verdict_group)
        layout.addWidget(quality_group)
        layout.addWidget(evidence_group)
        layout.addWidget(breakdown_group)
        layout.addWidget(preset_group)
        layout.addWidget(import_group)
        layout.addWidget(export_group)
        layout.addStretch()

        return self.wrap_tab_in_scroll_area(tab)

    def on_reference_engine_changed(self, index):
        reference_name = self.reference_engine_selector.itemData(index)

        self.results["reference_engine_name"] = reference_name
        self.results["selected_reference_engine"] = reference_name
        self.results["validation_reference_engine"] = reference_name

        if not reference_name:
            self.results["regen_scalability_validation_status"] = "NOT_SELECTED"
            self.results["reference_engine_display_name"] = "N/A"
            self.results["reference_engine_source_status"] = "N/A"
            self.results["reference_engine_validation_note"] = "No reference engine selected."
            self.update_reference_data_action_checklist("")
            self.update_reference_source_ledger_preview("")
            self.refresh_values_panel()
            return

        if get_reference_engine is None:
            self.results["regen_scalability_validation_status"] = "REFERENCE_DATABASE_MISSING"
            self.results["reference_engine_display_name"] = reference_name
            self.results["reference_engine_source_status"] = "UNKNOWN"
            self.results["reference_engine_validation_note"] = "reference_engine_database.py could not be imported."
            self.refresh_values_panel()
            return

        reference = get_reference_engine(reference_name)

        if not reference:
            self.results["regen_scalability_validation_status"] = "REFERENCE_ENGINE_NOT_FOUND"
            self.results["reference_engine_display_name"] = reference_name
            self.results["reference_engine_source_status"] = "UNKNOWN"
            self.results["reference_engine_validation_note"] = "Selected reference engine was not found in the database."
            self.refresh_values_panel()
            return

        self.results["reference_engine_display_name"] = reference.get("display_name", reference_name)

        self.results.setdefault("reference_comparison_run_gate_status", "NOT_RUN")
        self.results.setdefault("reference_validation_verdict", "REFERENCE_VALIDATION_NOT_RUN")
        self.results.setdefault(
            "reference_validation_recommendation",
            "Run solver/reference comparison to generate verdict."
        )
        self.results["reference_engine_source_status"] = reference.get("source_status", "UNKNOWN")
        self.update_reference_source_validation(reference_name)

        self.update_reference_database_record_preview(reference_name)
        self.update_reference_schema_audit_preview(reference_name)
        self.update_candidate_promotion_readiness_preview(reference_name)
        self.update_candidate_promotion_delta_preview(reference_name)
        self.update_reference_candidate_values_preview(reference_name)
        self.update_reference_status_consistency_preview(reference_name)
        self.update_reference_auto_status_preview(reference_name)
        self.update_reference_data_quality_preview(reference_name)
        self.update_reference_value_origin_preview(reference_name)
        self.update_reference_ledger_coverage_preview(reference_name)
        self.update_reference_source_ledger_preview(reference_name)
        self.update_reference_source_target_preview(reference_name)
        self.update_reference_value_entry_preview(reference_name)
        self.update_reference_data_action_checklist(reference_name)
        self.update_reference_rebuild_readiness_preview(reference_name)

        self.update_reference_comparison_evidence_preview()

        if reference.get("source_status") == "PLACEHOLDER_REQUIRED":
            self.results["regen_scalability_validation_status"] = "REFERENCE_DATA_REQUIRED"
            self.results["reference_engine_overall_agreement_percent"] = None
            self.results["reference_engine_mean_error_percent"] = None
            self.results["reference_engine_comparison_count"] = 0
            self.results["reference_engine_validation_note"] = (
                "Reference selected, but sourced channel/cooling values have not been added yet."
            )

        self.update_reference_input_preview(reference_name)
        self.refresh_values_panel()

    def update_reference_input_preview(self, reference_name):
        if not hasattr(self, "reference_input_preview_label"):
            return

        if not reference_name:
            self.reference_input_preview_label.setText(
                "No reference engine selected."
            )
            return

        if get_reference_engine_input_overrides is None:
            self.reference_input_preview_label.setText(
                "Reference input preset helper is unavailable."
            )
            return

        overrides = get_reference_engine_input_overrides(reference_name)

        if not overrides:
            self.reference_input_preview_label.setText(
                "No sourced minimum input overrides are available yet. "
                "This is expected until reference data is added."
            )
            return

        lines = ["Loadable minimum inputs:"]

        for key, value in overrides.items():
            lines.append(f"{key}: {value}")

        self.reference_input_preview_label.setText("\n".join(lines))

    def clear_reference_source_validation(self):
        self.results["viewer_reference_record_status"] = "NOT_SELECTED"
        self.results["viewer_reference_filled_comparison_count"] = "N/A"
        self.results["viewer_reference_filled_source_count"] = "N/A"
        self.results["viewer_reference_missing_inputs"] = "N/A"
        self.results["viewer_reference_missing_comparison_fields"] = "N/A"
        self.results["viewer_reference_missing_source_fields"] = "N/A"
        self.results["viewer_reference_record_recommendation"] = "No reference engine selected."
        self.results["viewer_reference_input_preset_status"] = "N/A"
        self.results["viewer_reference_comparison_status"] = "N/A"
        self.results["viewer_reference_filled_input_count"] = "N/A"
        self.results["viewer_reference_readiness_status"] = "NOT_SELECTED"
        self.results["viewer_reference_input_ready"] = "N/A"
        self.results["viewer_reference_comparison_ready"] = "N/A"
        self.results["viewer_reference_source_ready"] = "N/A"
        self.results["viewer_reference_readiness_recommendation"] = "No reference engine selected."
        self.results["reference_engine_display_name"] = "N/A"
        self.results["viewer_reference_db_usefulness_status"] = "NO_REFERENCE_SELECTED"
        self.results["reference_comparison_run_gate_status"] = "NOT_SELECTED"
        self.results["reference_validation_verdict"] = "REFERENCE_NOT_SELECTED"
        self.results["reference_validation_recommendation"] = "Select a reference engine."

    def update_reference_source_validation(self, reference_name):
        if validate_reference_engine_source_record is None:
            self.results["viewer_reference_record_status"] = "VALIDATOR_MISSING"
            self.results["viewer_reference_record_recommendation"] = (
                "validate_reference_engine_source_record could not be imported."
            )
            return

        validation = validate_reference_engine_source_record(reference_name)

        readiness = None

        if evaluate_reference_engine_database_record is not None:
            readiness = evaluate_reference_engine_database_record(reference_name)

        self.results["viewer_reference_record_status"] = validation.get("status")
        self.results["viewer_reference_input_preset_status"] = validation.get("input_preset_status")
        self.results["viewer_reference_comparison_status"] = validation.get("comparison_status")
        self.results["viewer_reference_filled_input_count"] = validation.get("filled_input_count")
        self.results["viewer_reference_filled_comparison_count"] = validation.get("filled_comparison_count")
        self.results["viewer_reference_input_preset_status"] = validation.get("input_preset_status")
        self.results["viewer_reference_comparison_status"] = validation.get("comparison_status")
        self.results["viewer_reference_filled_input_count"] = validation.get("filled_input_count")
        self.results["viewer_reference_filled_source_count"] = validation.get("filled_source_count")
        self.results["viewer_reference_missing_inputs"] = ", ".join(validation.get("missing_inputs", [])) or "None"
        self.results["viewer_reference_missing_comparison_fields"] = ", ".join(validation.get("missing_comparison_fields", [])) or "None"
        self.results["viewer_reference_missing_source_fields"] = ", ".join(validation.get("missing_source_fields", [])) or "None"
        self.results["viewer_reference_record_recommendation"] = validation.get("recommendation")

        if readiness:
            self.results["viewer_reference_readiness_status"] = readiness.get("status")
            self.results["viewer_reference_input_ready"] = readiness.get("input_ready")
            self.results["viewer_reference_comparison_ready"] = readiness.get("comparison_ready")
            self.results["viewer_reference_source_ready"] = readiness.get("source_ready")
            self.results["viewer_reference_readiness_recommendation"] = readiness.get("recommendation")
        else:
            self.results["viewer_reference_readiness_status"] = "READINESS_HELPER_MISSING"
            self.results["viewer_reference_input_ready"] = "N/A"
            self.results["viewer_reference_comparison_ready"] = "N/A"
            self.results["viewer_reference_source_ready"] = "N/A"
            self.results["viewer_reference_readiness_recommendation"] = "Readiness helper unavailable."

    def update_reference_comparison_evidence_preview(self):
        if not hasattr(self, "reference_evidence_label"):
            return

        evidence = self.results.get("reference_comparison_evidence")

        if not isinstance(evidence, list) or not evidence:
            self.reference_evidence_label.setText(
                "No comparison evidence available yet. Run the solver and select a reference engine."
            )
            return

        lines = []

        for row in evidence:
            label = row.get("label", "Unknown")
            leaf_key = row.get("leaf_key", "N/A")
            reference_key = row.get("reference_key", "N/A")
            leaf_value = row.get("leaf_value")
            reference_value = row.get("reference_value")
            ready = row.get("ready")
            error_percent = row.get("error_percent")

            status = "READY" if ready else "MISSING"

            if error_percent is None:
                error_text = "N/A"
            else:
                try:
                    error_text = f"{float(error_percent):.2f}%"
                except Exception:
                    error_text = str(error_percent)

            lines.append(
                f"{label}: {status}\n"
                f"  LEAF {leaf_key}: {leaf_value if leaf_value not in (None, '') else 'N/A'}\n"
                f"  Ref  {reference_key}: {reference_value if reference_value not in (None, '') else 'N/A'}\n"
                f"  Error: {error_text}"
            )

        self.reference_evidence_label.setText("\n\n".join(lines))

    def evaluate_reference_database_completeness(self, engine):
        if not isinstance(engine, dict):
            return {
                "input_text": "0 / 7",
                "geometry_text": "0 / 5",
                "comparison_text": "0 / 7",
                "source_text": "0 / 5",
                "overall_text": "0.0 %",
                "usefulness": "NO_REFERENCE_SELECTED",
                "next_action": "Select a reference engine.",
            }

        def filled_count(source, keys):
            return len([
                key for key in keys
                if source.get(key) not in (None, "")
            ])

        input_keys = [
            "fuel",
            "oxidizer",
            "mixture_ratio",
            "mass_flow_rate",
            "chamber_pressure",
            "characteristic_length",
            "ambient_pressure",
        ]

        geometry_keys = [
            "throat_area_m2",
            "exit_area_m2",
            "throat_radius_m",
            "exit_radius_m",
            "nozzle_length_m",
        ]

        comparison_keys = [
            "channel_count",
            "channel_width_m",
            "channel_height_m",
            "wall_thickness_m",
            "coolant_velocity_m_s",
            "pressure_drop_pa",
            "coolant_temperature_rise_k",
        ]

        source_keys = [
            "source_title",
            "source_author",
            "source_year",
            "doi",
            "url",
        ]

        overrides = engine.get("minimum_input_overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}

        geometry = engine.get("reference_geometry", {})
        if not isinstance(geometry, dict):
            geometry = {}

        input_count = filled_count(overrides, input_keys)
        geometry_count = filled_count(geometry, geometry_keys)
        comparison_count = filled_count(engine, comparison_keys)
        source_count = filled_count(engine, source_keys)

        total_count = input_count + geometry_count + comparison_count + source_count
        total_possible = len(input_keys) + len(geometry_keys) + len(comparison_keys) + len(source_keys)
        overall = 100.0 * total_count / max(total_possible, 1)

        if input_count == len(input_keys) and comparison_count == len(comparison_keys) and source_count == len(source_keys):
            usefulness = "FULL_REFERENCE_READY"
            next_action = "Run LEAF comparison and verify agreement."
        elif comparison_count == len(comparison_keys) and source_count == len(source_keys):
            usefulness = "COMPARISON_READY_INPUTS_INCOMPLETE"
            next_action = "Add minimum input preset fields."
        elif input_count == len(input_keys) and comparison_count == 0:
            usefulness = "INPUT_PRESET_ONLY"
            next_action = "Add regen comparison data."
        elif comparison_count > 0:
            usefulness = "PARTIAL_COMPARISON_DATA"
            next_action = "Complete missing comparison/source fields."
        elif input_count > 0:
            usefulness = "PARTIAL_INPUT_PRESET"
            next_action = "Complete minimum input preset fields."
        else:
            usefulness = "PLACEHOLDER_RECORD"
            next_action = "Add sourced reference engine values."

        return {
            "input_text": f"{input_count} / {len(input_keys)}",
            "geometry_text": f"{geometry_count} / {len(geometry_keys)}",
            "comparison_text": f"{comparison_count} / {len(comparison_keys)}",
            "source_text": f"{source_count} / {len(source_keys)}",
            "overall_text": f"{overall:.1f} %",
            "usefulness": usefulness,
            "next_action": next_action,
        }

    def update_reference_data_action_checklist(self, reference_name):
        if not hasattr(self, "reference_action_checklist_label"):
            return

        if not reference_name or get_reference_engine is None:
            self.reference_action_checklist_label.setText(
                "No reference engine selected.\n\n"
                "Action:\n"
                "- Select RL10, Merlin_1D, RS25, BE3, BE4, or Raptor."
            )
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.reference_action_checklist_label.setText(
                f"Reference engine '{reference_name}' was not found in reference_engine_database.py."
            )
            return

        overrides = engine.get("minimum_input_overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}

        geometry = engine.get("reference_geometry", {})
        if not isinstance(geometry, dict):
            geometry = {}

        input_fields = [
            "fuel",
            "oxidizer",
            "mixture_ratio",
            "mass_flow_rate",
            "chamber_pressure",
            "characteristic_length",
            "ambient_pressure",
        ]

        geometry_fields = [
            "throat_area_m2",
            "exit_area_m2",
            "throat_radius_m",
            "exit_radius_m",
            "nozzle_length_m",
        ]

        comparison_fields = [
            "channel_count",
            "channel_width_m",
            "channel_height_m",
            "wall_thickness_m",
            "coolant_velocity_m_s",
            "pressure_drop_pa",
            "coolant_temperature_rise_k",
        ]

        source_fields = [
            "source_title",
            "source_author",
            "source_year",
            "doi",
            "url",
        ]

        def missing(source, fields):
            return [
                field for field in fields
                if source.get(field) in (None, "")
            ]

        missing_inputs = missing(overrides, input_fields)
        missing_geometry = missing(geometry, geometry_fields)
        missing_comparison = missing(engine, comparison_fields)
        missing_sources = missing(engine, source_fields)

        lines = [
            f"Editing target: REFERENCE_ENGINES['{reference_name}']",
            "",
        ]

        if missing_inputs:
            lines.append("Minimum input overrides still missing:")
            for field in missing_inputs:
                lines.append(f"  - minimum_input_overrides['{field}']")
        else:
            lines.append("✓ Minimum input overrides complete")

        lines.append("")

        if missing_geometry:
            lines.append("Reference geometry still missing:")
            for field in missing_geometry:
                lines.append(f"  - reference_geometry['{field}']")
        else:
            lines.append("✓ Reference geometry complete")

        lines.append("")

        if missing_comparison:
            lines.append("Regen comparison values still missing:")
            for field in missing_comparison:
                lines.append(f"  - {field}")
        else:
            lines.append("✓ Regen comparison values complete")

        lines.append("")

        if missing_sources:
            lines.append("Source metadata still missing:")
            for field in missing_sources:
                lines.append(f"  - {field}")
        else:
            lines.append("✓ Source metadata complete")

        lines.append("")
        lines.append("Rules:")
        lines.append("- Only fill values from public sourced data.")
        lines.append("- Leave unknown values as None.")
        lines.append("- Do not manually enter CEA-derived values.")

        self.reference_action_checklist_label.setText("\n".join(lines))

    def update_reference_status_consistency_preview(self, reference_name):
        if not reference_name:
            self.results["viewer_reference_status_consistency"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_status_mismatch_count"] = "N/A"
            self.results["viewer_reference_status_mismatches"] = "N/A"
            self.results["viewer_reference_status_consistency_recommendation"] = "Select a reference engine."
            self.results["viewer_reference_raw_source_status"] = "N/A"
            self.results["viewer_reference_raw_quality_band"] = "N/A"
            self.results["viewer_reference_raw_quality_score"] = "N/A"
            return

        if evaluate_reference_database_status_consistency is None:
            self.results["viewer_reference_status_consistency"] = "CONSISTENCY_HELPER_MISSING"
            self.results["viewer_reference_status_mismatch_count"] = "N/A"
            self.results["viewer_reference_status_mismatches"] = "N/A"
            self.results[
                "viewer_reference_status_consistency_recommendation"] = "Status consistency helper unavailable."
            return

        consistency = evaluate_reference_database_status_consistency(reference_name)

        self.results["viewer_reference_status_consistency"] = consistency.get("status")
        self.results["viewer_reference_status_mismatch_count"] = consistency.get("mismatch_count")
        self.results["viewer_reference_status_mismatches"] = ", ".join(
            consistency.get("mismatches", [])
        ) or "None"
        self.results["viewer_reference_status_consistency_recommendation"] = consistency.get("recommendation")
        self.results["viewer_reference_raw_source_status"] = consistency.get("stored_source_status", "N/A")
        self.results["viewer_reference_raw_quality_band"] = consistency.get("stored_quality_band", "N/A")
        self.results["viewer_reference_raw_quality_score"] = consistency.get("stored_quality_score", "N/A")

    def update_reference_auto_status_preview(self, reference_name):
        if not reference_name or get_reference_engine is None:
            self.results["viewer_reference_auto_source_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_auto_quality_band"] = "PLACEHOLDER"
            self.results["viewer_reference_auto_quality_score"] = 0
            self.results["viewer_reference_auto_ledger_status"] = "N/A"
            self.results["viewer_reference_auto_ledger_coverage"] = "N/A"
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.results["viewer_reference_auto_source_status"] = "REFERENCE_NOT_FOUND"
            self.results["viewer_reference_auto_quality_band"] = "PLACEHOLDER"
            self.results["viewer_reference_auto_quality_score"] = 0
            self.results["viewer_reference_auto_ledger_status"] = "N/A"
            self.results["viewer_reference_auto_ledger_coverage"] = "N/A"
            return

        if normalise_reference_engine_record is not None:
            engine = normalise_reference_engine_record(engine)

        self.results["viewer_reference_auto_source_status"] = engine.get("source_status", "UNKNOWN")
        self.results["viewer_reference_auto_quality_band"] = engine.get("data_quality_band", "PLACEHOLDER")
        self.results["viewer_reference_auto_quality_score"] = engine.get("data_quality_score", 0)
        self.results["viewer_reference_auto_ledger_status"] = engine.get("ledger_status", "N/A")
        self.results["viewer_reference_auto_ledger_coverage"] = engine.get("ledger_coverage_percent", "N/A")

    def update_reference_data_quality_preview(self, reference_name):
        if not reference_name or get_reference_engine is None:
            self.results["viewer_reference_data_quality_band"] = "PLACEHOLDER"
            self.results["viewer_reference_data_quality_score"] = 0
            self.results["viewer_reference_data_quality_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_data_quality_recommendation"] = "Select a reference engine."
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.results["viewer_reference_data_quality_band"] = "PLACEHOLDER"
            self.results["viewer_reference_data_quality_score"] = 0
            self.results["viewer_reference_data_quality_status"] = "REFERENCE_NOT_FOUND"
            self.results["viewer_reference_data_quality_recommendation"] = "Reference engine not found."
            return

        if evaluate_reference_data_quality is None:
            self.results["viewer_reference_data_quality_band"] = "PLACEHOLDER"
            self.results["viewer_reference_data_quality_score"] = 0
            self.results["viewer_reference_data_quality_status"] = "QUALITY_HELPER_MISSING"
            self.results["viewer_reference_data_quality_recommendation"] = "Data quality helper unavailable."
            return

        quality = evaluate_reference_data_quality(engine)

        self.results["viewer_reference_data_quality_band"] = quality.get("band")
        self.results["viewer_reference_data_quality_score"] = quality.get("score")
        self.results["viewer_reference_data_quality_status"] = quality.get("status")
        self.results["viewer_reference_data_quality_recommendation"] = quality.get("recommendation")

    def update_reference_value_origin_preview(self, reference_name):
        if not reference_name or get_reference_engine is None:
            self.results["viewer_reference_origin_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_origin_filled_count"] = "N/A"
            self.results["viewer_reference_origin_tagged_count"] = "N/A"
            self.results["viewer_reference_origin_missing_fields"] = "N/A"
            self.results["viewer_reference_origin_blocked_fields"] = "N/A"
            self.results["viewer_reference_origin_recommendation"] = "Select a reference engine."
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.results["viewer_reference_origin_status"] = "REFERENCE_NOT_FOUND"
            self.results["viewer_reference_origin_recommendation"] = "Reference engine not found."
            return

        if evaluate_reference_value_origin_coverage is None:
            self.results["viewer_reference_origin_status"] = "ORIGIN_HELPER_MISSING"
            self.results["viewer_reference_origin_recommendation"] = "Origin helper unavailable."
            return

        origin = evaluate_reference_value_origin_coverage(engine)

        self.results["viewer_reference_origin_status"] = origin.get("status")
        self.results["viewer_reference_origin_filled_count"] = origin.get("filled_count")
        self.results["viewer_reference_origin_tagged_count"] = origin.get("origin_count")
        self.results["viewer_reference_origin_missing_fields"] = ", ".join(
            origin.get("missing_origin_fields", [])
        ) or "None"
        self.results["viewer_reference_origin_blocked_fields"] = ", ".join(
            origin.get("blocked_fields", [])
        ) or "None"
        self.results["viewer_reference_origin_recommendation"] = origin.get("recommendation")

    def update_reference_ledger_coverage_preview(self, reference_name):
        if not reference_name or get_reference_engine is None:
            self.results["viewer_reference_ledger_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_ledger_covered_count"] = "N/A"
            self.results["viewer_reference_ledger_filled_count"] = "N/A"
            self.results["viewer_reference_ledger_coverage_percent"] = "N/A"
            self.results["viewer_reference_ledger_missing_notes"] = "N/A"
            self.results["viewer_reference_ledger_recommendation"] = "Select a reference engine."
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.results["viewer_reference_ledger_status"] = "REFERENCE_NOT_FOUND"
            self.results["viewer_reference_ledger_recommendation"] = "Reference engine not found."
            return

        if evaluate_reference_source_ledger_coverage is None:
            self.results["viewer_reference_ledger_status"] = "LEDGER_HELPER_MISSING"
            self.results["viewer_reference_ledger_recommendation"] = "Ledger coverage helper unavailable."
            return

        coverage = evaluate_reference_source_ledger_coverage(engine)

        self.results["viewer_reference_ledger_status"] = coverage.get("status")
        self.results["viewer_reference_ledger_covered_count"] = coverage.get("covered_count")
        self.results["viewer_reference_ledger_filled_count"] = coverage.get("filled_count")
        self.results["viewer_reference_ledger_coverage_percent"] = coverage.get("coverage_percent")
        self.results["viewer_reference_ledger_missing_notes"] = ", ".join(
            coverage.get("missing_ledger_notes", [])
        ) or "None"
        self.results["viewer_reference_ledger_recommendation"] = coverage.get("recommendation")

    def update_reference_value_entry_preview(self, reference_name):
        if not hasattr(self, "reference_value_entry_label"):
            return

        if not reference_name or get_reference_engine is None:
            self.reference_value_entry_label.setText(
                "No reference engine selected."
            )
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.reference_value_entry_label.setText(
                f"Reference engine '{reference_name}' was not found."
            )
            return

        if build_reference_value_entry_checklist is None:
            self.reference_value_entry_label.setText(
                "Value-entry checklist helper is unavailable."
            )
            return

        rows = build_reference_value_entry_checklist(engine)

        if not rows:
            self.reference_value_entry_label.setText(
                "No value-entry checklist rows available."
            )
            return

        ready_rows = [row for row in rows if row.get("ready")]
        filled_rows = [
            row for row in rows
            if row.get("value") not in (None, "")
        ]

        lines = []
        lines.append(f"Ready values: {len(ready_rows)} / {len(rows)}")
        lines.append(f"Filled values: {len(filled_rows)} / {len(rows)}")
        lines.append("")

        for row in rows:
            if row.get("status") == "EMPTY":
                continue

            lines.append(
                f"{row.get('section')}.{row.get('field')}: {row.get('status')}"
            )
            lines.append(f"  value: {row.get('value')}")
            lines.append(f"  origin: {row.get('origin')}")
            lines.append(f"  action: {row.get('action')}")
            lines.append("")

        if len(filled_rows) == 0:
            lines.append("No filled reference values yet.")

        self.reference_value_entry_label.setText("\n".join(lines))

    def update_reference_source_target_preview(self, reference_name):
        if not hasattr(self, "reference_source_target_label"):
            return

        if not reference_name or get_reference_engine is None:
            self.reference_source_target_label.setText(
                "No reference engine selected."
            )
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.reference_source_target_label.setText(
                f"Reference engine '{reference_name}' was not found."
            )
            return

        targets = engine.get("source_targets", {})
        if not isinstance(targets, dict):
            self.reference_source_target_label.setText(
                "No source acquisition targets are defined for this engine."
            )
            return

        lines = []

        for section_name, values in targets.items():
            lines.append(section_name)
            lines.append("-" * len(section_name))

            if not isinstance(values, dict) or not values:
                lines.append("No targets defined.")
            else:
                for field, target in values.items():
                    lines.append(f"{field}: {target}")

            lines.append("")

        self.reference_source_target_label.setText("\n".join(lines))

    def update_reference_source_ledger_preview(self, reference_name):
        if not hasattr(self, "reference_source_ledger_label"):
            return

        if not reference_name or get_reference_engine is None:
            self.reference_source_ledger_label.setText(
                "No reference engine selected."
            )
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            self.reference_source_ledger_label.setText(
                f"Reference engine '{reference_name}' was not found."
            )
            return

        ledger = engine.get("source_ledger", {})

        if not isinstance(ledger, dict):
            self.reference_source_ledger_label.setText(
                "No source ledger exists for this engine."
            )
            return

        sections = [
            ("Minimum Input Overrides", "minimum_input_overrides"),
            ("Reference Geometry", "reference_geometry"),
            ("Comparison Values", "comparison_values"),
        ]

        lines = []

        for title, key in sections:
            lines.append(title)
            lines.append("-" * len(title))

            values = ledger.get(key, {})

            if not isinstance(values, dict) or not values:
                lines.append("No value-level source notes yet.")
            else:
                for field, note in values.items():
                    lines.append(f"{field}: {note}")

            lines.append("")

        self.reference_source_ledger_label.setText("\n".join(lines))

    def update_reference_rebuild_readiness_preview(self, reference_name):
        if not reference_name:
            self.results["viewer_reference_rebuild_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_rebuild_mode"] = "REFERENCE_LIBRARY_ONLY"
            self.results["viewer_reference_rebuild_input_ready"] = "N/A"
            self.results["viewer_reference_rebuild_geometry_ready"] = "N/A"
            self.results["viewer_reference_rebuild_comparison_ready"] = "N/A"
            self.results["viewer_reference_rebuild_filled_inputs"] = "N/A"
            self.results["viewer_reference_rebuild_filled_geometry"] = "N/A"
            self.results["viewer_reference_rebuild_filled_comparison"] = "N/A"
            self.results["viewer_reference_rebuild_recommendation"] = "Select a reference engine."
            return

        if evaluate_reference_rebuild_readiness is None:
            self.results["viewer_reference_rebuild_status"] = "HELPER_MISSING"
            self.results["viewer_reference_rebuild_recommendation"] = "Reference rebuild helper unavailable."
            return

        readiness = evaluate_reference_rebuild_readiness(reference_name)

        self.results["viewer_reference_rebuild_status"] = readiness.get("status")
        self.results["viewer_reference_rebuild_mode"] = readiness.get("mode")
        self.results["viewer_reference_rebuild_input_ready"] = readiness.get("input_ready")
        self.results["viewer_reference_rebuild_geometry_ready"] = readiness.get("geometry_ready")
        self.results["viewer_reference_rebuild_comparison_ready"] = readiness.get("comparison_ready")
        self.results["viewer_reference_rebuild_filled_inputs"] = readiness.get("filled_inputs")
        self.results["viewer_reference_rebuild_filled_geometry"] = readiness.get("filled_geometry")
        self.results["viewer_reference_rebuild_filled_comparison"] = readiness.get("filled_comparison")
        self.results["viewer_reference_rebuild_recommendation"] = readiness.get("recommendation")

        if build_reference_rebuild_session_record is not None:
            session = build_reference_rebuild_session_record(
                reference_name,
                self.results,
            )

            self.results["viewer_reference_rebuild_session_id"] = session.get("session_id")
            self.results["viewer_reference_rebuild_session_status"] = session.get("session_status")
            self.results["viewer_reference_rebuild_session_warning_count"] = len(
                session.get("warnings", [])
            )
            self.results["viewer_reference_rebuild_modifies_leaf_inputs"] = session.get(
                "modifies_leaf_inputs"
            )
            self.results["viewer_reference_rebuild_validation_run"] = session.get(
                "validation_run"
            )

        if build_reference_rebuild_run_record is not None:
            run = build_reference_rebuild_run_record(
                reference_name,
                self.results,
            )

            self.results["viewer_reference_rebuild_run_id"] = run.get("run_id")
            self.results["viewer_reference_rebuild_run_status"] = run.get("run_status")
            self.results["viewer_reference_rebuild_run_warning_count"] = len(
                run.get("warnings", [])
            )
            self.results["viewer_reference_rebuild_solver_ran"] = run.get(
                "rebuild_attempt", {}
            ).get("solver_ran")
            self.results["viewer_reference_rebuild_validation_status"] = run.get(
                "validation_results", {}
            ).get("geometry_comparison")

        if evaluate_reference_geometry_comparison is not None:
            geometry_comparison = evaluate_reference_geometry_comparison(
                reference_name,
                self.results,
            )

            self.results["viewer_reference_geometry_comparison_status"] = (
                geometry_comparison.get("status")
            )

            summary = geometry_comparison.get("summary", {})

            self.results["viewer_reference_geometry_compared_count"] = summary.get(
                "compared_count"
            )
            self.results["viewer_reference_geometry_pass_count"] = summary.get(
                "pass_count"
            )
            self.results["viewer_reference_geometry_warn_count"] = summary.get(
                "warn_count"
            )
            self.results["viewer_reference_geometry_missing_count"] = summary.get(
                "missing_count"
            )

        if evaluate_reference_regen_geometry_comparison is not None:
            regen_comparison = evaluate_reference_regen_geometry_comparison(
                reference_name,
                self.results,
            )

            self.results["viewer_reference_regen_geometry_comparison_status"] = (
                regen_comparison.get("status")
            )

            summary = regen_comparison.get("summary", {})

            self.results["viewer_reference_regen_geometry_compared_count"] = summary.get(
                "compared_count"
            )
            self.results["viewer_reference_regen_geometry_pass_count"] = summary.get(
                "pass_count"
            )
            self.results["viewer_reference_regen_geometry_warn_count"] = summary.get(
                "warn_count"
            )
            self.results["viewer_reference_regen_geometry_missing_count"] = summary.get(
                "missing_count"
            )

    def update_reference_schema_audit_preview(self, reference_name):
        if not reference_name:
            self.results["viewer_reference_schema_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_reference_schema_missing_top_level"] = "N/A"
            self.results["viewer_reference_schema_missing_nested"] = "N/A"
            self.results["viewer_reference_schema_unexpected_types"] = "N/A"
            self.results["viewer_reference_all_schema_status"] = "N/A"
            self.results["viewer_reference_schema_broken_count"] = "N/A"
            self.results["viewer_reference_schema_recommendation"] = "Select a reference engine."
            return

        if audit_reference_engine_schema is None:
            self.results["viewer_reference_schema_status"] = "SCHEMA_HELPER_MISSING"
            self.results["viewer_reference_schema_recommendation"] = "Schema audit helper unavailable."
            return

        selected_audit = audit_reference_engine_schema(reference_name)

        self.results["viewer_reference_schema_status"] = selected_audit.get("status")
        self.results["viewer_reference_schema_missing_top_level"] = ", ".join(
            selected_audit.get("missing_top_level", [])
        ) or "None"
        self.results["viewer_reference_schema_missing_nested"] = ", ".join(
            selected_audit.get("missing_nested", [])
        ) or "None"
        self.results["viewer_reference_schema_unexpected_types"] = ", ".join(
            selected_audit.get("unexpected_nested_type", [])
        ) or "None"

        if audit_all_reference_engine_schemas is not None:
            all_audit = audit_all_reference_engine_schemas()
            self.results["viewer_reference_all_schema_status"] = all_audit.get("status")
            self.results["viewer_reference_schema_broken_count"] = (
                f"{all_audit.get('broken_count')} / {all_audit.get('total_count')}"
            )
        else:
            self.results["viewer_reference_all_schema_status"] = "ALL_SCHEMA_HELPER_MISSING"
            self.results["viewer_reference_schema_broken_count"] = "N/A"

        self.results["viewer_reference_schema_recommendation"] = selected_audit.get("recommendation")

    def update_candidate_promotion_delta_preview(self, reference_name):
        if not reference_name:
            self.results["viewer_candidate_delta_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_candidate_delta_before_inputs"] = "N/A"
            self.results["viewer_candidate_delta_after_inputs"] = "N/A"
            self.results["viewer_candidate_delta_before_comparison"] = "N/A"
            self.results["viewer_candidate_delta_after_comparison"] = "N/A"
            self.results["viewer_candidate_delta_improved_fields"] = "N/A"
            self.results["viewer_candidate_delta_recommendation"] = "Select a reference engine."
            return

        if evaluate_candidate_promotion_completeness_delta is None:
            self.results["viewer_candidate_delta_status"] = "HELPER_MISSING"
            self.results["viewer_candidate_delta_recommendation"] = "Candidate delta helper unavailable."
            return

        delta = evaluate_candidate_promotion_completeness_delta(reference_name)
        before = delta.get("before", {})
        after = delta.get("after", {})

        self.results["viewer_candidate_delta_status"] = delta.get("status")
        self.results["viewer_candidate_delta_before_inputs"] = before.get("filled_inputs")
        self.results["viewer_candidate_delta_after_inputs"] = after.get("filled_inputs")
        self.results["viewer_candidate_delta_before_comparison"] = before.get("filled_comparison")
        self.results["viewer_candidate_delta_after_comparison"] = after.get("filled_comparison")
        self.results["viewer_candidate_delta_improved_fields"] = ", ".join(
            delta.get("improved_fields", [])
        ) or "None"
        self.results["viewer_candidate_delta_recommendation"] = delta.get("recommendation")

    def update_candidate_promotion_readiness_preview(self, reference_name):
        if not reference_name:
            self.results["viewer_candidate_promotion_status"] = "NO_REFERENCE_SELECTED"
            self.results["viewer_candidate_promotion_ready_count"] = "N/A"
            self.results["viewer_candidate_promotion_candidate_count"] = "N/A"
            self.results["viewer_candidate_promotion_missing_requirements"] = "N/A"
            self.results["viewer_candidate_promotion_recommendation"] = "Select a reference engine."
            return

        if evaluate_candidate_promotion_readiness is None:
            self.results["viewer_candidate_promotion_status"] = "HELPER_MISSING"
            self.results["viewer_candidate_promotion_recommendation"] = "Candidate readiness helper unavailable."
            return

        readiness = evaluate_candidate_promotion_readiness(reference_name)

        self.results["viewer_candidate_promotion_status"] = readiness.get("status")
        self.results["viewer_candidate_promotion_ready_count"] = readiness.get("ready_count")
        self.results["viewer_candidate_promotion_candidate_count"] = readiness.get("candidate_count")
        self.results["viewer_candidate_promotion_missing_requirements"] = ", ".join(
            readiness.get("missing_requirements", [])
        ) or "None"
        self.results["viewer_candidate_promotion_recommendation"] = readiness.get("recommendation")

    def update_reference_candidate_values_preview(self, reference_name):
        if not hasattr(self, "reference_candidate_values_label"):
            return

        if not reference_name:
            self.reference_candidate_values_label.setText(
                "No reference engine selected."
            )
            return

        if get_reference_engine_candidate_values is None:
            self.reference_candidate_values_label.setText(
                "Candidate-value helper is unavailable."
            )
            return

        candidates = get_reference_engine_candidate_values(reference_name)

        if not candidates:
            self.reference_candidate_values_label.setText(
                "No candidate values stored."
            )
            return

        lines = []

        for section_key, section in candidates.items():
            lines.append(str(section_key))
            lines.append("-" * len(str(section_key)))

            if isinstance(section, dict):
                if not section:
                    lines.append("No values.")
                else:
                    for key, value in section.items():
                        lines.append(f"{key}: {value}")
            else:
                lines.append(str(section))

            lines.append("")

        self.reference_candidate_values_label.setText("\n".join(lines))

    def update_reference_database_record_preview(self, reference_name):
        prefix = "viewer_reference_db_"

        fields_to_clear = [
            "fuel",
            "oxidizer",
            "mixture_ratio",
            "mass_flow_rate",
            "chamber_pressure",
            "characteristic_length",
            "ambient_pressure",
            "thrust_n",
            "throat_area_m2",
            "exit_area_m2",
            "throat_radius_m",
            "exit_radius_m",
            "nozzle_length_m",
            "channel_count",
            "channel_width_m",
            "channel_height_m",
            "wall_thickness_m",
            "coolant_velocity_m_s",
            "pressure_drop_pa",
            "coolant_temperature_rise_k",
            "source_title",
            "source_author",
            "source_year",
            "doi",
            "url",
            "notes",
        ]

        if not reference_name or get_reference_engine is None:
            for field in fields_to_clear:
                self.results[prefix + field] = "N/A"

            completeness = self.evaluate_reference_database_completeness(None)
            self.results["viewer_reference_db_input_completeness"] = completeness["input_text"]
            self.results["viewer_reference_db_geometry_completeness"] = completeness["geometry_text"]
            self.results["viewer_reference_db_comparison_completeness"] = completeness["comparison_text"]
            self.results["viewer_reference_db_source_completeness"] = completeness["source_text"]
            self.results["viewer_reference_db_overall_completeness"] = completeness["overall_text"]
            self.results["viewer_reference_db_usefulness_status"] = completeness["usefulness"]
            self.results["viewer_reference_db_next_action"] = completeness["next_action"]
            return

        engine = get_reference_engine(reference_name)

        if not engine:
            for field in fields_to_clear:
                self.results[prefix + field] = "N/A"

            completeness = self.evaluate_reference_database_completeness(None)
            self.results["viewer_reference_db_input_completeness"] = completeness["input_text"]
            self.results["viewer_reference_db_geometry_completeness"] = completeness["geometry_text"]
            self.results["viewer_reference_db_comparison_completeness"] = completeness["comparison_text"]
            self.results["viewer_reference_db_source_completeness"] = completeness["source_text"]
            self.results["viewer_reference_db_overall_completeness"] = completeness["overall_text"]
            self.results["viewer_reference_db_usefulness_status"] = completeness["usefulness"]
            self.results["viewer_reference_db_next_action"] = completeness["next_action"]
            return

        overrides = engine.get("minimum_input_overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}

        reference_geometry = engine.get("reference_geometry", {})
        if not isinstance(reference_geometry, dict):
            reference_geometry = {}

        self.results[prefix + "fuel"] = overrides.get("fuel") or engine.get("fuel") or "N/A"
        self.results[prefix + "oxidizer"] = overrides.get("oxidizer") or engine.get("oxidizer") or "N/A"
        self.results[prefix + "mixture_ratio"] = overrides.get("mixture_ratio", "N/A")
        self.results[prefix + "mass_flow_rate"] = overrides.get("mass_flow_rate", "N/A")
        self.results[prefix + "chamber_pressure"] = overrides.get("chamber_pressure", "N/A")
        self.results[prefix + "characteristic_length"] = overrides.get("characteristic_length", "N/A")
        self.results[prefix + "ambient_pressure"] = overrides.get("ambient_pressure", "N/A")

        self.results[prefix + "thrust_n"] = engine.get("thrust_n", "N/A")

        self.results[prefix + "throat_area_m2"] = reference_geometry.get("throat_area_m2", "N/A")
        self.results[prefix + "exit_area_m2"] = reference_geometry.get("exit_area_m2", "N/A")
        self.results[prefix + "throat_radius_m"] = reference_geometry.get("throat_radius_m", "N/A")
        self.results[prefix + "exit_radius_m"] = reference_geometry.get("exit_radius_m", "N/A")
        self.results[prefix + "nozzle_length_m"] = reference_geometry.get("nozzle_length_m", "N/A")

        for field in [
            "channel_count",
            "channel_width_m",
            "channel_height_m",
            "wall_thickness_m",
            "coolant_velocity_m_s",
            "pressure_drop_pa",
            "coolant_temperature_rise_k",
            "source_title",
            "source_author",
            "source_year",
            "doi",
            "url",
            "notes",
        ]:
            self.results[prefix + field] = engine.get(field, "N/A")

        completeness = self.evaluate_reference_database_completeness(engine)

        self.results["viewer_reference_db_input_completeness"] = completeness["input_text"]
        self.results["viewer_reference_db_geometry_completeness"] = completeness["geometry_text"]
        self.results["viewer_reference_db_comparison_completeness"] = completeness["comparison_text"]
        self.results["viewer_reference_db_source_completeness"] = completeness["source_text"]
        self.results["viewer_reference_db_overall_completeness"] = completeness["overall_text"]
        self.results["viewer_reference_db_usefulness_status"] = completeness["usefulness"]
        self.results["viewer_reference_db_next_action"] = completeness["next_action"]

    def build_candidate_promotion_preview_text(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            return "No reference engine selected."

        if get_reference_engine_candidate_values is None:
            return "Candidate-value helper is unavailable."

        candidates = get_reference_engine_candidate_values(reference_name)

        if not candidates:
            return f"No candidate values found for {reference_name}."

        lines = []
        lines.append(f"Candidate Promotion Preview — {reference_name}")
        lines.append("=" * 64)
        lines.append("")
        lines.append("Important:")
        lines.append("- This is a preview only.")
        lines.append("- Do not promote values unless the source is public and recorded.")
        lines.append("- Candidate values do not produce validation PASS.")
        lines.append("")

        section_map = [
            ("minimum_input_overrides", "Minimum Input Overrides"),
            ("reference_geometry", "Reference Geometry"),
            ("comparison_values", "Regen Comparison Values"),
        ]

        for section_key, title in section_map:
            section = candidates.get(section_key, {})

            lines.append(title)
            lines.append("-" * 40)

            if not isinstance(section, dict) or not section:
                lines.append("No candidate values.")
                lines.append("")
                continue

            for field, value in section.items():
                lines.append(f"{field}: {value}")
                if section_key == "comparison_values":
                    target = f"REFERENCE_ENGINES['{reference_name}']['{field}']"
                else:
                    target = f"REFERENCE_ENGINES['{reference_name}']['{section_key}']['{field}']"

                lines.append(f"  promote target: {target}")
                lines.append(f"  required source_ledger: source_ledger['{section_key}']['{field}']")
                lines.append(f"  required value_origin: value_origin['{section_key}']['{field}']")
                lines.append("")

        notes = candidates.get("notes")
        if notes:
            lines.append("Candidate Notes")
            lines.append("-" * 40)
            lines.append(str(notes))
            lines.append("")

        return "\n".join(lines)

    def build_candidate_station_debug_export_text(self):
        """
        Full-engine regen geometry station export.

        Exports every available regen/nozzle station profile plus the evaluated
        manual/recommended/candidate geometry at each station.
        """
        canvas = self.canvas

        profile_keys = [
            "rao_nozzle_profile",
            "conical_nozzle_profile",
            "regen_axial_profile",
            "variable_channel_geometry_profile",
            "variable_geometry_thermal_profile",
            "velocity_limited_variable_geometry_profile",
            "coupled_split_strategy_profile",
            "explicit_coating_liner_profile",
        ]

        original_selected_length = self.results.get("regen_viewer_selected_length")
        original_selected_length_fallback = self.results.get("selected_length")

        profiles_export = {}

        try:
            for profile_key in profile_keys:
                profile = self.results.get(profile_key)

                # Fallback: active_station_profile() can expose a generated/fallback profile
                # even when the raw results dictionary does not directly contain the profile key.
                if (not isinstance(profile, list) or not profile) and profile_key == canvas.station_profile_key:
                    profile = canvas.active_station_profile()

                if not isinstance(profile, list) or not profile:
                    profiles_export[profile_key] = {
                        "station_count": 0,
                        "export_status": "NO_PROFILE_DATA_AVAILABLE",
                        "stations": [],
                    }
                    continue

                station_exports = []

                for index, station in enumerate(profile):
                    if not isinstance(station, dict):
                        continue

                    station_x = (
                        station.get("x")
                        if station.get("x") not in (None, "")
                        else station.get("station_x")
                    )

                    try:
                        station_x = float(station_x)
                    except Exception:
                        station_x = float(index)

                    self.results["regen_viewer_selected_length"] = station_x
                    self.results["selected_length"] = station_x
                    canvas.results = self.results

                    manual_geometry = canvas.get_geometry("manual")
                    automatic_geometry = canvas.get_geometry("automatic")

                    station_exports.append({
                        "station_index": index,
                        "station_x": station_x,
                        "raw_station_data": station,
                        "manual_geometry": manual_geometry,
                        "automatic_geometry": automatic_geometry,
                    })

                profiles_export[profile_key] = {
                    "station_count": len(station_exports),
                    "stations": station_exports,
                }

        finally:
            self.results["regen_viewer_selected_length"] = original_selected_length
            self.results["selected_length"] = original_selected_length_fallback
            canvas.results = self.results

        if not any(item.get("station_count", 0) > 0 for item in profiles_export.values()):
            generated_stations = []

            effective_length = self.get_effective_nozzle_length()

            for index in range(51):
                station_x = effective_length * index / 50.0

                self.results["regen_viewer_selected_length"] = station_x
                self.results["selected_length"] = station_x
                canvas.results = self.results

                generated_stations.append({
                    "station_index": index,
                    "station_x": station_x,
                    "raw_station_data": {
                        "generated_by_exporter": True,
                        "reason": "No real axial profile was available in results.",
                    },
                    "manual_geometry": canvas.get_geometry("manual"),
                    "automatic_geometry": canvas.get_geometry("automatic"),
                })

            profiles_export["viewer_generated_51_station_debug_profile"] = {
                "station_count": len(generated_stations),
                "export_status": "GENERATED_DEBUG_PROFILE_NO_REAL_PROFILE_AVAILABLE",
                "stations": generated_stations,
            }

        export_data = {
            "leaf_debug_export_type": "full_engine_regen_geometry_station_dump",
            "phase": "11A.11",
            "purpose": (
                "Full engine station-by-station regen geometry export for debugging "
                "manual/automatic geometry, topology, coatings, bond layers, "
                "liner data, channel count, radius, pitch, and station behaviour."
            ),
            "viewer_state": {
                "viewer_geometry_source": getattr(canvas, "geometry_source", None),
                "viewer_profile_key": getattr(canvas, "station_profile_key", None),
                "selected_length": original_selected_length,
                "selected_length_fallback": original_selected_length_fallback,
                "available_station_profiles": canvas.available_station_profiles(),
                "topology": canvas.evaluate_channel_topology_status(),
            },
            "global_geometry_inputs": {
                key: value
                for key, value in self.results.items()
                if any(token in str(key).lower() for token in [
                    "channel",
                    "rib",
                    "wall",
                    "coating",
                    "bond",
                    "liner",
                    "throat",
                    "exit",
                    "radius",
                    "area",
                    "nozzle",
                    "regen",
                    "geometry",
                    "coolant",
                ])
                   and not isinstance(value, list)
            },
            "profiles": profiles_export,
        }

        return json.dumps(export_data, indent=2, sort_keys=True, default=str)

    def copy_candidate_station_debug_export(self):
        text = self.build_candidate_station_debug_export_text()

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Full Regen Station Export Copied",
            (
                "Full engine regen station geometry export copied to clipboard.\n\n"
                "Paste it into ChatGPT for station-by-station geometry debugging."
            )
        )

    def copy_candidate_promotion_preview(self):
        text = self.build_candidate_promotion_preview_text()
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Candidate promotion preview copied to clipboard."
        )




    def copy_schema_repair_patch(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying a schema repair patch."
            )
            return

        if build_reference_schema_repair_patch is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Schema repair helper is unavailable."
            )
            return

        text = build_reference_schema_repair_patch(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Schema repair patch copied to clipboard."
        )

    def copy_reference_database_self_test(self):
        if build_reference_database_self_test_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference database self-test helper is unavailable."
            )
            return

        text = build_reference_database_self_test_report()
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference database self-test copied to clipboard."
        )

    def copy_candidate_readiness_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying candidate readiness."
            )
            return

        if build_candidate_promotion_readiness_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Candidate readiness report helper is unavailable."
            )
            return

        text = build_candidate_promotion_readiness_report(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Candidate readiness report copied to clipboard."
        )

    def copy_candidate_promotion_patch(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying a candidate promotion patch."
            )
            return

        if build_candidate_promotion_patch is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Candidate promotion patch helper is unavailable."
            )
            return

        text = build_candidate_promotion_patch(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Candidate promotion patch copied to clipboard."
        )

    def copy_candidate_apply_preview(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying candidate apply preview."
            )
            return

        if build_candidate_promotion_apply_preview is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Candidate apply preview helper is unavailable."
            )
            return

        text = build_candidate_promotion_apply_preview(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Candidate apply preview copied to clipboard."
        )

    def copy_candidate_delta_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying candidate delta."
            )
            return

        if build_candidate_promotion_completeness_delta_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Candidate delta report helper is unavailable."
            )
            return

        text = build_candidate_promotion_completeness_delta_report(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Candidate delta report copied to clipboard."
        )

    def copy_reference_rebuild_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying rebuild readiness."
            )
            return

        if build_reference_rebuild_readiness_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild report helper is unavailable."
            )
            return

        text = build_reference_rebuild_readiness_report(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference rebuild report copied to clipboard."
        )

    def copy_reference_rebuild_inputs(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying rebuild inputs."
            )
            return

        if build_reference_rebuild_input_export is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild input export helper is unavailable."
            )
            return

        text = build_reference_rebuild_input_export(reference_name)
        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference rebuild inputs copied to clipboard."
        )

    def copy_reference_rebuild_load_preview(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying rebuild input apply plan."
            )
            return

        if build_reference_rebuild_input_apply_plan is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild input apply-plan helper is unavailable."
            )
            return

        text = build_reference_rebuild_input_apply_plan(
            reference_name,
            self.results,
        )

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference rebuild input apply plan copied to clipboard."
        )

    def copy_reference_rebuild_session_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying rebuild session report."
            )
            return

        if build_reference_rebuild_session_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild session helper is unavailable."
            )
            return

        text = build_reference_rebuild_session_report(
            reference_name,
            self.results,
        )

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference rebuild session report copied to clipboard."
        )

    def copy_reference_rebuild_run_record_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying rebuild run record."
            )
            return

        if build_reference_rebuild_run_record_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild run-record helper is unavailable."
            )
            return

        text = build_reference_rebuild_run_record_report(
            reference_name,
            self.results,
        )

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference rebuild run record copied to clipboard."
        )

    def copy_reference_rebuild_result_export(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying rebuild result export."
            )
            return

        if build_reference_rebuild_result_export is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild result export helper is unavailable."
            )
            return

        text = build_reference_rebuild_result_export(
            reference_name,
            self.results,
        )

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Full reference rebuild result export copied to clipboard."
        )

    def copy_reference_geometry_comparison_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying geometry comparison."
            )
            return

        if build_reference_geometry_comparison_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference geometry comparison helper is unavailable."
            )
            return

        text = build_reference_geometry_comparison_report(
            reference_name,
            self.results,
        )

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference geometry comparison copied to clipboard."
        )

    def copy_reference_regen_geometry_comparison_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before copying regen geometry comparison."
            )
            return

        if build_reference_regen_geometry_comparison_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference regen geometry comparison helper is unavailable."
            )
            return

        text = build_reference_regen_geometry_comparison_report(
            reference_name,
            self.results,
        )

        QApplication.clipboard().setText(text)

        QMessageBox.information(
            self,
            "Copied",
            "Reference regen geometry comparison copied to clipboard."
        )

    def export_reference_regen_geometry_comparison_txt(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting regen geometry comparison."
            )
            return

        if build_reference_regen_geometry_comparison_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference regen geometry comparison helper is unavailable."
            )
            return

        text = build_reference_regen_geometry_comparison_report(
            reference_name,
            self.results,
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Regen Geometry Comparison",
            f"{reference_name}_regen_geometry_comparison.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(text)

        QMessageBox.information(
            self,
            "Export Complete",
            f"Reference regen geometry comparison exported:\n{filepath}"
        )

    def export_reference_geometry_comparison_txt(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting geometry comparison."
            )
            return

        if build_reference_geometry_comparison_report is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference geometry comparison helper is unavailable."
            )
            return

        text = build_reference_geometry_comparison_report(
            reference_name,
            self.results,
        )

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Geometry Comparison",
            f"{reference_name}_geometry_comparison.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(text)

        QMessageBox.information(
            self,
            "Export Complete",
            f"Reference geometry comparison exported:\n{filepath}"
        )

    def export_reference_rebuild_result_export_txt(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting rebuild result."
            )
            return

        if build_reference_rebuild_result_export is None:
            QMessageBox.warning(
                self,
                "Unavailable",
                "Reference rebuild result export helper is unavailable."
            )
            return

        text = build_reference_rebuild_result_export(
            reference_name,
            self.results,
        )

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Rebuild Result",
            f"{reference_name}_reference_rebuild_result_export.txt",
            "Text Files (*.txt)"
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

        QMessageBox.information(
            self,
            "Exported",
            f"Reference rebuild result exported to:\n{path}"
        )

    def build_reference_database_report_text(self, reference_name):
        if not reference_name or get_reference_engine is None:
            return "No reference engine selected."

        engine = get_reference_engine(reference_name)

        if not engine:
            return f"Reference engine '{reference_name}' was not found."

        completeness = self.evaluate_reference_database_completeness(engine)

        overrides = engine.get("minimum_input_overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}

        geometry = engine.get("reference_geometry", {})
        if not isinstance(geometry, dict):
            geometry = {}

        lines = []
        lines.append(f"Reference Database Completeness Report — {reference_name}")
        lines.append("=" * 64)
        lines.append("")
        lines.append("Auto-Derived Record Status")
        lines.append("-" * 40)
        lines.append(f"Derived source status: {self.results.get('viewer_reference_auto_source_status', 'N/A')}")
        lines.append(f"Derived quality band: {self.results.get('viewer_reference_auto_quality_band', 'N/A')}")
        lines.append(f"Derived quality score: {self.results.get('viewer_reference_auto_quality_score', 'N/A')}")
        lines.append(f"Derived ledger status: {self.results.get('viewer_reference_auto_ledger_status', 'N/A')}")
        lines.append(f"Derived ledger coverage: {self.results.get('viewer_reference_auto_ledger_coverage', 'N/A')}")
        lines.append("")
        lines.append("Status Consistency")
        lines.append("-" * 40)
        lines.append(f"Consistency: {self.results.get('viewer_reference_status_consistency', 'N/A')}")
        lines.append(f"Mismatch count: {self.results.get('viewer_reference_status_mismatch_count', 'N/A')}")
        lines.append(f"Mismatches: {self.results.get('viewer_reference_status_mismatches', 'N/A')}")
        lines.append(f"Recommendation: {self.results.get('viewer_reference_status_consistency_recommendation', 'N/A')}")
        lines.append(f"Raw source status: {self.results.get('viewer_reference_raw_source_status', 'N/A')}")
        lines.append(f"Raw quality band: {self.results.get('viewer_reference_raw_quality_band', 'N/A')}")
        lines.append(f"Raw quality score: {self.results.get('viewer_reference_raw_quality_score', 'N/A')}")
        lines.append("")
        lines.append("Data Quality")
        lines.append("-" * 40)
        lines.append(f"Quality band: {self.results.get('viewer_reference_data_quality_band', 'N/A')}")
        lines.append(f"Quality score: {self.results.get('viewer_reference_data_quality_score', 'N/A')}")
        lines.append(f"Quality status: {self.results.get('viewer_reference_data_quality_status', 'N/A')}")
        lines.append(f"Quality recommendation: {self.results.get('viewer_reference_data_quality_recommendation', 'N/A')}")
        lines.append("")
        lines.append("Completeness")
        lines.append("-" * 40)
        lines.append(f"Input fields: {completeness['input_text']}")
        lines.append(f"Geometry fields: {completeness['geometry_text']}")
        lines.append(f"Comparison fields: {completeness['comparison_text']}")
        lines.append(f"Source fields: {completeness['source_text']}")
        lines.append(f"Overall completeness: {completeness['overall_text']}")
        lines.append(f"Database usefulness: {completeness['usefulness']}")
        lines.append(f"Next action: {completeness['next_action']}")
        lines.append("")

        lines.append("Minimum Input Overrides")
        lines.append("-" * 40)
        for key in [
            "fuel",
            "oxidizer",
            "mixture_ratio",
            "mass_flow_rate",
            "chamber_pressure",
            "characteristic_length",
            "ambient_pressure",
        ]:
            lines.append(f"{key}: {overrides.get(key, 'N/A')}")
        lines.append("")

        lines.append("Reference Geometry")
        lines.append("-" * 40)
        for key in [
            "throat_area_m2",
            "exit_area_m2",
            "throat_radius_m",
            "exit_radius_m",
            "nozzle_length_m",
        ]:
            lines.append(f"{key}: {geometry.get(key, 'N/A')}")
        lines.append("")

        lines.append("Regen Comparison Values")
        lines.append("-" * 40)
        for key in [
            "channel_count",
            "channel_width_m",
            "channel_height_m",
            "wall_thickness_m",
            "coolant_velocity_m_s",
            "pressure_drop_pa",
            "coolant_temperature_rise_k",
        ]:
            lines.append(f"{key}: {engine.get(key, 'N/A')}")
        lines.append("")

        lines.append("Source Metadata")
        lines.append("-" * 40)
        for key in [
            "source_status",
            "source_title",
            "source_author",
            "source_year",
            "doi",
            "url",
            "notes",
        ]:
            lines.append(f"{key}: {engine.get(key, 'N/A')}")
        lines.append("")
        lines.append("Value Origin Coverage")
        lines.append("-" * 40)
        lines.append(f"Origin status: {self.results.get('viewer_reference_origin_status', 'N/A')}")
        lines.append(f"Filled values: {self.results.get('viewer_reference_origin_filled_count', 'N/A')}")
        lines.append(f"Tagged values: {self.results.get('viewer_reference_origin_tagged_count', 'N/A')}")
        lines.append(f"Missing origin tags: {self.results.get('viewer_reference_origin_missing_fields', 'N/A')}")
        lines.append(f"Blocked fields: {self.results.get('viewer_reference_origin_blocked_fields', 'N/A')}")
        lines.append(f"Recommendation: {self.results.get('viewer_reference_origin_recommendation', 'N/A')}")
        lines.append("")
        lines.append("Source Ledger Coverage")
        lines.append("-" * 40)
        lines.append(f"Ledger status: {self.results.get('viewer_reference_ledger_status', 'N/A')}")
        lines.append(f"Covered values: {self.results.get('viewer_reference_ledger_covered_count', 'N/A')}")
        lines.append(f"Filled values: {self.results.get('viewer_reference_ledger_filled_count', 'N/A')}")
        lines.append(f"Coverage percent: {self.results.get('viewer_reference_ledger_coverage_percent', 'N/A')}")
        lines.append(f"Missing notes: {self.results.get('viewer_reference_ledger_missing_notes', 'N/A')}")
        lines.append(f"Recommendation: {self.results.get('viewer_reference_ledger_recommendation', 'N/A')}")
        lines.append("")
        lines.append("Source Ledger")
        lines.append("-" * 40)

        ledger = engine.get("source_ledger", {})

        if isinstance(ledger, dict):
            for section_key in [
                "minimum_input_overrides",
                "reference_geometry",
                "comparison_values",
            ]:
                lines.append(section_key + ":")

                section = ledger.get(section_key, {})

                if isinstance(section, dict) and section:
                    for field, note in section.items():
                        lines.append(f"  {field}: {note}")
                else:
                    lines.append("  No value-level source notes yet.")

                lines.append("")
        else:
            lines.append("No source ledger available.")
            lines.append("")

        lines.append("Reference Value Entry Checklist")
        lines.append("-" * 40)

        if build_reference_value_entry_checklist is not None:
            rows = build_reference_value_entry_checklist(engine)

            for row in rows:
                if row.get("value") in (None, ""):
                    continue

                lines.append(
                    f"{row.get('section')}.{row.get('field')}: {row.get('status')}"
                )
                lines.append(f"  value: {row.get('value')}")
                lines.append(f"  origin: {row.get('origin')}")
                lines.append(f"  action: {row.get('action')}")
        else:
            lines.append("Value-entry checklist helper unavailable.")

        lines.append("")
        lines.append("Rules")
        lines.append("-" * 40)
        lines.append("Only fill values from public sourced data.")
        lines.append("Leave unknown values as None.")
        lines.append("Do not manually enter CEA-derived values.")
        lines.append("CEA-owned fields include chamber_temperature, Gamma, R, Prandtl, c*, Isp, and exhaust velocity.")
        lines.append("")

        return "\n".join(lines)

    def build_reference_fill_assistant_text(self, reference_name):
        if not reference_name or get_reference_engine is None:
            return "No reference engine selected."

        engine = get_reference_engine(reference_name)

        if not engine:
            return f"Reference engine '{reference_name}' was not found."

        display_name = engine.get("display_name", reference_name)

        lines = []
        lines.append(f"Direct Database Fill Guide — {display_name}")
        lines.append("=" * 64)
        lines.append("")
        lines.append("Edit this block directly inside:")
        lines.append("reference_engine_database.py")
        lines.append("")
        lines.append(f"Target:")
        lines.append(f'REFERENCE_ENGINES["{reference_name}"]')
        lines.append("")
        lines.append("Only replace None values when you have public sourced data.")
        lines.append("Do not enter CEA-derived values manually.")
        lines.append("")

        lines.append("Minimum Input Overrides")
        lines.append("-" * 40)
        lines.append('"minimum_input_overrides": {')
        for key in [
            "fuel",
            "oxidizer",
            "mixture_ratio",
            "mass_flow_rate",
            "chamber_pressure",
            "characteristic_length",
            "ambient_pressure",
        ]:
            current = engine.get("minimum_input_overrides", {}).get(key, None)
            lines.append(f'    "{key}": {repr(current)},  # source: TODO')
        lines.append("},")
        lines.append("")

        lines.append("Reference Geometry")
        lines.append("-" * 40)
        lines.append('"reference_geometry": {')
        for key in [
            "throat_area_m2",
            "exit_area_m2",
            "throat_radius_m",
            "exit_radius_m",
            "nozzle_length_m",
        ]:
            current = engine.get("reference_geometry", {}).get(key, None)
            lines.append(f'    "{key}": {repr(current)},  # source: TODO')
        lines.append("},")
        lines.append("")

        lines.append("Regen Comparison Values")
        lines.append("-" * 40)
        for key in [
            "channel_count",
            "channel_width_m",
            "channel_height_m",
            "wall_thickness_m",
            "coolant_velocity_m_s",
            "pressure_drop_pa",
            "coolant_temperature_rise_k",
        ]:
            lines.append(f'"{key}": {repr(engine.get(key, None))},  # source: TODO')

        lines.append("")
        lines.append("Source Metadata")
        lines.append("-" * 40)
        for key in [
            "source_title",
            "source_author",
            "source_year",
            "doi",
            "url",
            "notes",
        ]:
            lines.append(f'"{key}": {repr(engine.get(key, None))},')

        lines.append("")
        lines.append("After filling real data, set:")
        lines.append('"source_status": "SOURCED_PARTIAL",')
        lines.append("")
        lines.append("Only use SOURCED_VALIDATION_READY once:")
        lines.append("- comparison values are filled")
        lines.append("- source metadata is filled")
        lines.append("- values have been checked against the source")
        lines.append("")

        return "\n".join(lines)

    def export_reference_fill_assistant(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting the fill guide."
            )
            return

        guide_text = self.build_reference_fill_assistant_text(reference_name)

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Direct Database Fill Guide",
            f"{reference_name}_direct_database_fill_guide.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(guide_text)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Direct database fill guide exported:\n{filepath}"
            )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export direct database fill guide:\n{exc}"
            )

    def build_reference_ledger_audit_text(self, reference_name):
        if not reference_name or get_reference_engine is None:
            return "No reference engine selected."

        engine = get_reference_engine(reference_name)

        if not engine:
            return f"Reference engine '{reference_name}' was not found."

        ledger = engine.get("source_ledger", {})
        if not isinstance(ledger, dict):
            ledger = {}

        coverage_status = self.results.get("reference_source_ledger_status") or self.results.get("viewer_reference_ledger_status", "N/A")
        coverage_percent = self.results.get("reference_source_ledger_coverage_percent") or self.results.get("viewer_reference_ledger_coverage_percent", "N/A")
        missing_notes = self.results.get("reference_source_ledger_missing_notes") or self.results.get("viewer_reference_ledger_missing_notes", "N/A")
        recommendation = self.results.get("reference_source_ledger_recommendation") or self.results.get("viewer_reference_ledger_recommendation", "N/A")

        sections = [
            (
                "Minimum Input Overrides",
                "minimum_input_overrides",
                engine.get("minimum_input_overrides", {}),
                [
                    "fuel",
                    "oxidizer",
                    "mixture_ratio",
                    "mass_flow_rate",
                    "chamber_pressure",
                    "characteristic_length",
                    "ambient_pressure",
                ],
            ),
            (
                "Reference Geometry",
                "reference_geometry",
                engine.get("reference_geometry", {}),
                [
                    "throat_area_m2",
                    "exit_area_m2",
                    "throat_radius_m",
                    "exit_radius_m",
                    "nozzle_length_m",
                ],
            ),
            (
                "Regen Comparison Values",
                "comparison_values",
                engine,
                [
                    "channel_count",
                    "channel_width_m",
                    "channel_height_m",
                    "wall_thickness_m",
                    "coolant_velocity_m_s",
                    "pressure_drop_pa",
                    "coolant_temperature_rise_k",
                ],
            ),
        ]

        lines = []
        lines.append(f"Reference Source Ledger Audit — {reference_name}")
        lines.append("=" * 64)
        lines.append("")
        lines.append("Ledger Coverage Summary")
        lines.append("-" * 40)
        lines.append(f"Status: {coverage_status}")
        lines.append(f"Coverage percent: {coverage_percent}")
        lines.append(f"Missing notes: {missing_notes}")
        lines.append(f"Recommendation: {recommendation}")
        lines.append("")
        lines.append("Value-Level Audit")
        lines.append("-" * 40)

        for title, ledger_key, source_dict, fields in sections:
            if not isinstance(source_dict, dict):
                source_dict = {}

            ledger_section = ledger.get(ledger_key, {})
            if not isinstance(ledger_section, dict):
                ledger_section = {}

            lines.append("")
            lines.append(title)
            lines.append("-" * len(title))

            for field in fields:
                value = source_dict.get(field)

                if value in (None, ""):
                    lines.append(f"{field}: EMPTY")
                    continue

                note = ledger_section.get(field)

                if note in (None, ""):
                    lines.append(f"{field}: FILLED = {value} | LEDGER NOTE MISSING")
                else:
                    lines.append(f"{field}: FILLED = {value}")
                    lines.append(f"  ledger: {note}")

        lines.append("")
        lines.append("Rules")
        lines.append("-" * 40)
        lines.append("A filled reference value should have a source-ledger note.")
        lines.append("PASS should remain blocked if filled comparison/input values lack ledger notes.")
        lines.append("Leave unknown values as None rather than guessing.")

        return "\n".join(lines)

    def export_reference_ledger_audit(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting the source ledger audit."
            )
            return

        audit_text = self.build_reference_ledger_audit_text(reference_name)

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Source Ledger Audit",
            f"{reference_name}_source_ledger_audit.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(audit_text)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Reference source ledger audit exported:\n{filepath}"
            )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export source ledger audit:\n{exc}"
            )

    def export_reference_database_report(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting the database report."
            )
            return

        report_text = self.build_reference_database_report_text(reference_name)

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Database Completeness Report",
            f"{reference_name}_database_completeness_report.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(report_text)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Reference database report exported:\n{filepath}"
            )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export reference database report:\n{exc}"
            )

    def export_reference_input_summary(self):
        reference_name = self.results.get("reference_engine_name")

        if not reference_name:
            QMessageBox.warning(
                self,
                "No Reference Engine",
                "Select a reference engine before exporting the input preset summary."
            )
            return

        if build_reference_engine_input_summary is None:
            QMessageBox.warning(
                self,
                "Reference Database Missing",
                "Could not import build_reference_engine_input_summary."
            )
            return

        summary_text = build_reference_engine_input_summary(reference_name)

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Reference Engine Input Preset Summary",
            f"{reference_name}_input_preset_summary.txt",
            "Text File (*.txt)"
        )

        if not filepath:
            return

        if not filepath.lower().endswith(".txt"):
            filepath += ".txt"

        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(summary_text)

            QMessageBox.information(
                self,
                "Export Complete",
                f"Reference input preset summary exported:\n{filepath}"
            )
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export reference input preset summary:\n{exc}"
            )

    def build_export_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        export_group = QGroupBox("Export Current Regen Evidence")
        export_layout = QGridLayout(export_group)

        self.export_png_button = self.make_inspector_button(
            "Export Current View PNG",
            self.export_current_canvas_png,
        )

        self.export_summary_button = self.make_inspector_button(
            "Export Station Summary TXT",
            self.export_station_summary_txt,
        )

        self.export_pack_button = self.make_inspector_button(
            "Export Figure Pack",
            self.export_figure_pack,
        )

        self.copy_recommended_regen_geometry_button = self.make_inspector_button(
            "Copy Recommended Regen Geometry",
            self.copy_recommended_regen_geometry,
        )

        export_layout.addWidget(self.export_png_button, 0, 0)
        export_layout.addWidget(self.export_summary_button, 1, 0)
        export_layout.addWidget(self.export_pack_button, 2, 0)
        export_layout.addWidget(self.copy_recommended_regen_geometry_button, 3, 0)

        overlay_group = QGroupBox("Viewport Display")
        overlay_layout = QGridLayout(overlay_group)

        self.geometry_overlay_button = self.make_inspector_button(
            "Geometry",
            lambda: self.set_overlay_mode("geometry"),
        )

        self.gas_overlay_button = self.make_inspector_button(
            "Gas",
            lambda: self.set_overlay_mode("gas"),
        )

        self.thermal_overlay_button = self.make_inspector_button(
            "Thermal",
            lambda: self.set_overlay_mode("thermal"),
        )

        self.coolant_overlay_button = self.make_inspector_button(
            "Coolant",
            lambda: self.set_overlay_mode("coolant"),
        )

        self.validation_overlay_button = self.make_inspector_button(
            "Validation",
            lambda: self.set_overlay_mode("validation"),
        )

        overlay_layout.addWidget(self.geometry_overlay_button, 0, 0)
        overlay_layout.addWidget(self.gas_overlay_button, 1, 0)
        overlay_layout.addWidget(self.thermal_overlay_button, 2, 0)
        overlay_layout.addWidget(self.coolant_overlay_button, 3, 0)
        overlay_layout.addWidget(self.validation_overlay_button, 4, 0)

        panel_group = QGroupBox("Viewport Options")
        panel_layout = QVBoxLayout(panel_group)

        self.legend_checkbox = QCheckBox("Show Legend / Overlay Key")
        self.legend_checkbox.setChecked(True)

        self.dimensions_checkbox = QCheckBox("Show Dimensions")
        self.dimensions_checkbox.setChecked(True)

        panel_layout.addWidget(self.legend_checkbox)
        panel_layout.addWidget(self.dimensions_checkbox)

        self.legend_checkbox.toggled.connect(self.set_show_legend)
        self.dimensions_checkbox.toggled.connect(self.set_show_dimensions)

        layout.addWidget(export_group)
        layout.addWidget(overlay_group)
        layout.addWidget(panel_group)
        layout.addStretch()

        self.update_overlay_button_styles()

        return self.wrap_tab_in_scroll_area(tab)

    def copy_recommended_regen_geometry(self):
        lines = []

        lines.append("Recommended Regen Geometry")
        lines.append("=" * 56)
        lines.append("")
        lines.append(f"Status: {self.results.get('recommended_geometry_status')}")
        lines.append(f"Valid: {self.results.get('recommended_geometry_valid')}")
        lines.append("")
        lines.append("Manual input values to apply:")
        lines.append(f"number_of_coolant_channels = {self.results.get('recommended_channel_count')}")
        lines.append(f"coolant_channel_width = {self.results.get('recommended_channel_width')}")
        lines.append(f"coolant_channel_height = {self.results.get('recommended_channel_height')}")
        lines.append(f"rib_width = {self.results.get('recommended_rib_width')}")
        lines.append("")
        lines.append("Derived checks:")
        lines.append(f"recommended_channel_pitch = {self.results.get('recommended_channel_pitch')}")
        lines.append(f"recommended_effective_rib_width = {self.results.get('recommended_effective_rib_width')}")
        lines.append(f"recommended_channel_fit_ratio = {self.results.get('recommended_channel_fit_ratio')}")
        lines.append(
            f"recommended_circumferential_cooling_coverage = {self.results.get('recommended_circumferential_cooling_coverage')}")
        lines.append(f"recommended_coolant_velocity = {self.results.get('recommended_coolant_velocity')}")
        lines.append(f"recommended_reynolds_number = {self.results.get('recommended_reynolds_number')}")
        lines.append(f"recommended_tightest_gas_radius = {self.results.get('recommended_tightest_gas_radius')}")

        QApplication.clipboard().setText("\n".join(lines))

        QMessageBox.information(
            self,
            "Copied",
            "Recommended regen geometry copied to clipboard."
        )

    def refresh_values_panel(self):
        if not hasattr(self, "value_labels"):
            return

        effective_nozzle_length = self.get_effective_nozzle_length()

        if hasattr(self, "station_spinbox"):
            with QSignalBlocker(self.station_spinbox):
                self.station_spinbox.setMaximum(
                    max(effective_nozzle_length, 0.001)
                )

        geometry = self.canvas.get_geometry()
        self.results["viewer_geometry_source"] = self.canvas.geometry_source
        self.results["viewer_actual_geometry_source"] = geometry.get("source")
        source_maturity = (
            self.canvas.evaluate_source_maturity_score()
            if hasattr(self.canvas, "evaluate_source_maturity_score")
            else {
                "overall_score": "N/A",
                "status": "N/A",
            }
        )

        signoff = (
            self.canvas.evaluate_regen_signoff(geometry)
            if hasattr(self.canvas, "evaluate_regen_signoff")
            else {
                "status": "N/A",
                "passed_items": "N/A",
                "total_items": "N/A",
                "external_testing_ready": "N/A",
            }
        )

        viewer_values = {
            "viewer_view_mode": self.canvas.view_mode,
            "viewer_geometry_source": self.canvas.geometry_source,
            "viewer_overlay_mode": self.canvas.overlay_mode.upper(),
            "viewer_scale_mode": self.canvas.scale_mode,
            "viewer_station_profile": self.canvas.station_profile_key,
            "viewer_station_profile_explanation": (
                "Controls which axial profile/station dataset is sampled. "
                "Geometry changes only if the selected profile contains different radius, area, or channel values."
            ),
            "viewer_show_legend": self.canvas.show_legend,
            "viewer_show_dimensions": self.canvas.show_dimensions,
            "regen_viewer_selected_length": geometry.get("selected_length"),
            "viewer_nearest_station_x": self.canvas.station_value(["x"], geometry.get("selected_length")),
            "viewer_station_index": self.canvas.station_value(
                ["station_index", "source_station_index", "coolant_path_index"],
                "N/A"
            ),

            "viewer_gas_radius": geometry.get("gas_radius"),
            "viewer_wall_thickness": geometry.get("wall"),
            "viewer_coating_thickness": geometry.get("coating"),
            "viewer_channel_height": geometry.get("channel_height"),
            "viewer_channel_width": geometry.get("channel_width"),
            "viewer_requested_rib_width": geometry.get("requested_rib_width"),
            "viewer_effective_rib_width": geometry.get("effective_rib_width"),
            "viewer_channel_count": geometry.get("channel_count"),
            "viewer_requested_pitch": geometry.get("requested_pitch"),
            "viewer_available_pitch": geometry.get("available_pitch"),
            "viewer_channel_fit_ratio": geometry.get("channel_fit_ratio"),
            "viewer_channel_geometry_valid": geometry.get("channel_geometry_valid"),
            "viewer_cooling_coverage": geometry.get("cooling_coverage"),

            "viewer_station_mach": self.canvas.station_value(["mach"], "N/A"),
            "viewer_station_static_pressure": self.canvas.station_value(["static_pressure"], "N/A"),
            "viewer_station_static_temperature": self.canvas.station_value(["static_temperature"], "N/A"),
            "viewer_station_adiabatic_wall_temperature": self.canvas.station_value(["adiabatic_wall_temperature"],
                                                                                   "N/A"),
            "viewer_station_heat_flux": self.canvas.station_value(["regen_heat_flux", "heat_flux"], "N/A"),

            "viewer_station_coolant_temperature_in": self.canvas.station_value(["coolant_temperature_in"], "N/A"),
            "viewer_station_coolant_temperature_out": self.canvas.station_value(
                ["coolant_temperature_out", "coolant_temperature"], "N/A"),
            "viewer_station_coolant_velocity": self.canvas.station_value(
                ["coolant_velocity", "variable_coolant_velocity", "safe_variable_coolant_velocity"], "N/A"),
            "viewer_station_reynolds_number": self.canvas.station_value(
                ["coolant_reynolds_number", "variable_reynolds_number", "safe_variable_reynolds_number"], "N/A"),
            "viewer_station_pressure_drop_total": self.canvas.station_value(["total_pressure_drop_so_far"], "N/A"),

            "viewer_source_maturity_score": source_maturity.get("overall_score"),
            "viewer_source_maturity_status": source_maturity.get("status"),

            "viewer_signoff_status": signoff.get("status"),
            "viewer_signoff_checklist": f"{signoff.get('passed_items')} / {signoff.get('total_items')}",
            "viewer_external_testing_ready": signoff.get("external_testing_ready"),
            "viewer_reference_verdict": self.results.get(
                "reference_validation_verdict",
                "REFERENCE_NOT_SELECTED"
            ),
            "viewer_reference_action": self.results.get(
                "reference_validation_recommendation",
                "Select and validate a reference engine."
            ),
        }

        key_aliases = {
            "recommended_channel_count": [
                "recommended_channel_count",
                "recommended_number_of_coolant_channels",
            ],
            "recommended_channel_width": [
                "recommended_channel_width",
                "recommended_coolant_channel_width",
            ],
            "recommended_channel_height": [
                "recommended_channel_height",
                "recommended_coolant_channel_height",
            ],
            "recommended_reynolds_number": [
                "recommended_reynolds_number",
                "recommended_coolant_reynolds_number",
            ],
            "recommended_geometry_valid": [
                "recommended_geometry_valid",
                "recommended_channel_geometry_valid",
            ],
        }

        for key, label in self.value_labels.items():
            if key in viewer_values:
                value = viewer_values[key]
            elif key in key_aliases:
                value = "N/A"

                for alias in key_aliases[key]:
                    if self.results.get(alias) not in (None, ""):
                        value = self.results.get(alias)
                        break
            else:
                value = self.results.get(key, "N/A")

            if isinstance(value, float):
                value = f"{value:.6g}"

            label.setText(str(value))

        if hasattr(self, "update_reference_comparison_evidence_preview"):
            self.update_reference_comparison_evidence_preview()

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_data_action_checklist(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_source_ledger_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_ledger_coverage_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_data_quality_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_auto_status_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_status_consistency_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_source_target_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_value_origin_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_value_entry_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_candidate_values_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_schema_audit_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_candidate_promotion_readiness_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_candidate_promotion_delta_preview(reference_name)

        if hasattr(self, "reference_engine_selector"):
            reference_name = self.results.get("reference_engine_name")
            self.update_reference_rebuild_readiness_preview(reference_name)

        # RH2C-R1 — canonical consolidated viewer refresh

        # --------------------------------------------------------
        # Read-only manufacturability presentation.
        #
        # The pure builder returns presentation data without
        # changing canonical Regen engineering status.
        # --------------------------------------------------------
        try:
            from leaf_qt.regen_viewer_manufacturability_overlay_phase_16q5 import (
                build_manufacturability_overlay,
            )

            manufacturability = build_manufacturability_overlay(
                self.results,
                geometry,
            )

            self.results[
                "phase_16q5_manufacturability_overlay_status"
            ] = manufacturability.get(
                "status"
            )

            self.results[
                "phase_16q5_manufacturability_overlay_pass"
            ] = manufacturability.get(
                "passed"
            )

            self.results[
                "phase_16q5_manufacturability_overlay_label"
            ] = manufacturability.get(
                "label"
            )

            self.results[
                "phase_16q5_manufacturability_overlay_details"
            ] = manufacturability.get(
                "details"
            )

            label = getattr(
                self,
                "phase_16q5_manufacturability_label",
                None,
            )

            if (
                label is not None
                and
                hasattr(
                    label,
                    "setText",
                )
            ):
                label.setText(
                    str(
                        manufacturability.get(
                            "label",
                            "MANUFACTURABILITY: NOT CHECKED",
                        )
                    )
                )

        except Exception as exc:
            self.results[
                "phase_16q5_manufacturability_overlay_status"
            ] = (
                "ERROR_REGEN_VIEWER_"
                "MANUFACTURABILITY_PRESENTATION"
            )

            self.results[
                "phase_16q5_manufacturability_overlay_error"
            ] = str(exc)


        # --------------------------------------------------------
        # Recommended-geometry presentation.
        #
        # Existing recommendation data is displayed directly.
        # Displayed canvas geometry is not promoted back into the
        # recommendation/engineering result state.
        # --------------------------------------------------------
        try:
            from leaf_qt.regen_viewer_recommended_geometry_panel_phase_16q14 import (
                build_recommended_geometry_panel_text,
            )

            panel_text = build_recommended_geometry_panel_text(
                self.results
            )

            for attr in (
                "recommended_geometry_label",
                "recommended_geometry_text",
                "recommendation_details_label",
                "recommendation_text",
                "geometry_recommendation_label",
            ):
                widget = getattr(
                    self,
                    attr,
                    None,
                )

                if (
                    widget is not None
                    and
                    hasattr(
                        widget,
                        "setText",
                    )
                ):
                    widget.setText(
                        panel_text
                    )

                    self.results[
                        "phase_16q15_recommended_widget_updated"
                    ] = attr

                    break

        except Exception as exc:
            self.results[
                "phase_16q15_recommended_refresh_error"
            ] = str(exc)


        # --------------------------------------------------------
        # Authoritative station payload and fallback.
        # --------------------------------------------------------
        try:
            attach_station_row_fallback(
                self.results,
                station_count=51,
            )

            selected_x = self.safe_float(
                geometry.get(
                    "selected_length"
                ),
                self.safe_float(
                    self.results.get(
                        "regen_viewer_selected_length"
                    ),
                    0.0,
                ),
            )

            attach_authoritative_station_payload(
                self.results,
                selected_x,
            )

        except Exception as exc:
            self.results[
                "phase_16q17_station_fallback_status"
            ] = (
                "ERROR_REGEN_VIEWER_"
                "STATION_ROW_FALLBACK_PHASE_16Q17"
            )

            self.results[
                "phase_16q17_station_fallback_error"
            ] = str(exc)


        # --------------------------------------------------------
        # Station-tab presentation.
        # --------------------------------------------------------
        try:
            attach_station_tab_payload(
                self.results
            )

            station_text = build_station_tab_text(
                self.results
            )

            station_widget_found = False

            for attr in (
                "station_data_label",
                "station_data_text",
                "station_details_label",
                "station_details_text",
                "station_tab_label",
                "station_tab_text",
            ):
                widget = getattr(
                    self,
                    attr,
                    None,
                )

                if (
                    widget is not None
                    and
                    hasattr(
                        widget,
                        "setText",
                    )
                ):
                    widget.setText(
                        station_text
                    )

                    self.results[
                        "phase_16q18_station_tab_widget_updated"
                    ] = attr

                    station_widget_found = True
                    break

            if not station_widget_found:
                self.results[
                    "phase_16q18_station_tab_widget_updated"
                ] = "NO_EXISTING_WIDGET_FOUND"

        except Exception as exc:
            self.results[
                "phase_16q18_station_tab_status"
            ] = (
                "ERROR_REGEN_VIEWER_"
                "STATION_TAB_POPULATION_PHASE_16Q18"
            )

            self.results[
                "phase_16q18_station_tab_error"
            ] = str(exc)


        # --------------------------------------------------------
        # Topology presentation.
        # --------------------------------------------------------
        try:
            attach_topology_panel_payload(
                self.results
            )

            topology_text = build_topology_panel_text(
                self.results
            )

            topology_widget_found = False

            for attr in (
                "topology_label",
                "topology_text",
                "topology_status_label",
                "profile_topology_label",
                "station_topology_label",
                "topology_details_text",
            ):
                widget = getattr(
                    self,
                    attr,
                    None,
                )

                if (
                    widget is not None
                    and
                    hasattr(
                        widget,
                        "setText",
                    )
                ):
                    widget.setText(
                        topology_text
                    )

                    self.results[
                        "phase_16q19_topology_widget_updated"
                    ] = attr

                    topology_widget_found = True
                    break

            if not topology_widget_found:
                self.results[
                    "phase_16q19_topology_widget_updated"
                ] = "NO_EXISTING_WIDGET_FOUND"

        except Exception as exc:
            self.results[
                "phase_16q19_topology_panel_status"
            ] = (
                "ERROR_REGEN_VIEWER_"
                "TOPOLOGY_PANEL_PHASE_16Q19"
            )

            self.results[
                "phase_16q19_topology_panel_error"
            ] = str(exc)


        # --------------------------------------------------------
        # Canonical automatic-geometry cache maintenance.
        # --------------------------------------------------------
        try:
            if (
                self.results.get(
                    "phase_16p1_automatic_geometry_workflow_applied"
                )
                is True
                or
                self.results.get(
                    "regen_ui_applied_geometry"
                )
                or
                self.results.get(
                    "regen_geometry_commit_staged_geometry"
                )
            ):
                store_automatic_geometry_cache(
                    self.results
                )

        except Exception as exc:
            self.results[
                "phase_16q25_auto_geometry_cache_status"
            ] = (
                "ERROR_REGEN_VIEWER_"
                "AUTOMATIC_GEOMETRY_CACHE_PHASE_16Q25"
            )

            self.results[
                "phase_16q25_auto_geometry_cache_error"
            ] = str(exc)


        # --------------------------------------------------------
        # Canonical full-engine side-profile overlay.
        # --------------------------------------------------------
        try:
            _canonical_side_profile_update_overlay(
                self
            )

        except Exception as exc:
            self.results[
                "canonical_side_profile_refresh_error"
            ] = str(exc)


        if hasattr(
            self,
            "configure_status_strip",
        ):
            self.configure_status_strip()

    def on_zoom_changed(self, value):
        self.zoom_label.setText(f"Zoom: {value}%")
        self.canvas.set_zoom_percent(value)

    def configure_status_strip(self):
        """Present only the active design mode's honest engineering state."""

        if not isinstance(
            getattr(
                self,
                "results",
                None,
            ),
            dict,
        ):
            self.results = {}

        mode = (
            self.current_regen_design_mode()
            if hasattr(
                self,
                "current_regen_design_mode",
            )
            else
            "manual"
        )

        status = str(
            self.results.get(
                "regen_overall_status"
            )
            or
            self.results.get(
                "overall_status"
            )
            or
            "UNKNOWN"
        ).upper()

        geometry = str(
            self.results.get(
                "regen_geometry_status"
            )
            or
            self.results.get(
                "geometry_status"
            )
            or
            "UNKNOWN"
        ).upper()

        thermal = str(
            self.results.get(
                "regen_thermal_status"
            )
            or
            self.results.get(
                "thermal_status"
            )
            or
            "UNKNOWN"
        ).upper()

        coolant = str(
            self.results.get(
                "regen_coolant_status"
            )
            or
            self.results.get(
                "coolant_status"
            )
            or
            "UNKNOWN"
        ).upper()

        material = str(
            self.results.get(
                "regen_material_status"
            )
            or
            self.results.get(
                "material_status"
            )
            or
            "UNKNOWN"
        ).upper()

        source_mode = str(
            self.results.get(
                "source_validation_mode"
            )
            or
            "N/A"
        ).upper()

        direct_status_values = (
            status,
            geometry,
            thermal,
            coolant,
            material,
        )

        direct_fail = any(
            _leaf_16u38_is_fail_like(
                value
            )
            for value in direct_status_values
        )

        direct_unproven = any(
            _leaf_16u38_status_severity(
                value
            )
            in
            {
                "WARN",
                "UNKNOWN",
            }
            for value in direct_status_values
        )

        source_unproven = (
            source_mode
            in
            {
                "",
                "N/A",
                "UNKNOWN",
                "PLACEHOLDER",
                "PLACEHOLDER_MODE",
                "PARTIAL",
                "PARTIAL_SOURCE",
                "PARTIAL_SOURCE_MODE",
            }
            or
            "PLACEHOLDER"
            in
            source_mode
            or
            "PARTIAL"
            in
            source_mode
        )

        generation_state = str(
            self.results.get(
                "regen_design_mode_generation_state"
            )
            or
            (
                "MANUAL"
                if mode == "manual"
                else
                "NOT_GENERATED"
            )
        ).upper()

        selected_material = str(
            self.results.get(
                "selected_material"
            )
            or
            "not specified"
        )

        if (
            mode
            ==
            "automatic_selected_material"
        ):
            mode_label = (
                "Automatic — Selected Material"
                f" ({selected_material})"
            )

        elif (
            mode
            ==
            "automatic_geometry_materials"
        ):
            mode_label = (
                "Automatic — Geometry + Materials"
            )

        else:
            mode_label = "Manual"

        ranked = (
            self.results.get(
                "regen_candidate_ranked_population"
            )
            or
            []
        )

        # ---------------------------------------------------------
        # MANUAL MODE
        #
        # Candidate-population qualification is deliberately excluded.
        # It belongs to Automatic design strategies, not Manual identity.
        # ---------------------------------------------------------

        if mode == "manual":
            if direct_fail:
                assessment = "FAIL"

            elif (
                direct_unproven
                or
                source_unproven
            ):
                assessment = "UNPROVEN"

            elif all(
                _leaf_16u38_is_pass_like(
                    value
                )
                for value in direct_status_values
            ):
                assessment = "PASS"

            else:
                assessment = "UNPROVEN"

            detail = (
                f"Overall {status}"
            )

        # ---------------------------------------------------------
        # AUTOMATIC MODE
        # ---------------------------------------------------------

        elif generation_state == "NOT_GENERATED":
            assessment = "UNPROVEN"

            detail = (
                "NOT GENERATED — press Generate"
            )

        elif generation_state == "RUNNING":
            assessment = "UNPROVEN"

            detail = (
                "GENERATING…"
            )

        elif generation_state == "NO_FEASIBLE_DESIGN":
            assessment = "FAIL"

            detail = (
                "No feasible qualified design"
            )

        elif generation_state == "ERROR":
            assessment = "FAIL"

            detail = (
                "Generation error"
            )

        elif generation_state == "GENERATED":
            try:
                qualification = (
                    self.canonical_regen_failure_presentation()
                )

            except Exception:
                qualification = {}

            failed_constraints = list(
                qualification.get(
                    "failed_constraints"
                )
                or
                []
            )

            unproven_constraints = list(
                qualification.get(
                    "unproven_constraints"
                )
                or
                []
            )

            feasibility = str(
                qualification.get(
                    "feasibility_status"
                )
                or
                "UNKNOWN"
            ).upper()

            automatic_fail = bool(
                failed_constraints
                or
                direct_fail
                or
                _leaf_16u38_is_fail_like(
                    feasibility
                )
            )

            automatic_unproven = bool(
                unproven_constraints
                or
                direct_unproven
                or
                source_unproven
                or
                _leaf_16u38_status_severity(
                    feasibility
                )
                in
                {
                    "WARN",
                    "UNKNOWN",
                }
            )

            if (
                ranked
                and
                not automatic_fail
                and
                not automatic_unproven
            ):
                assessment = "PASS"

                rank_one = (
                    ranked[0]
                    if isinstance(
                        ranked[0],
                        dict,
                    )
                    else
                    {}
                )

                rank_material = (
                    rank_one.get(
                        "candidate_material_name"
                    )
                    or
                    self.results.get(
                        "regen_geometry_material_display_material"
                    )
                )

                detail = (
                    "Generated qualified design"
                )

                if rank_material:
                    detail += (
                        f" | Rank 1 • {rank_material}"
                    )

            elif automatic_fail:
                assessment = "FAIL"

                detail = (
                    "Generated geometry failed qualification"
                )

            else:
                assessment = "UNPROVEN"

                detail = (
                    "Generated geometry qualification incomplete"
                )

        else:
            assessment = "UNPROVEN"
            detail = generation_state

        if assessment == "PASS":
            colour = "#204d2a"
            border = "#63b977"

        elif assessment == "FAIL":
            colour = "#5c1f1f"
            border = "#d46a6a"

        else:
            colour = "#5c4516"
            border = "#d6a23a"

        message = (
            f"MODE: {mode_label} | "
            f"{assessment} | "
            f"{detail} | "
            f"G:{geometry} "
            f"T:{thermal} "
            f"C:{coolant} "
            f"M:{material} | "
            f"Source:{source_mode}"
        )

        self.results[
            "regen_viewer_mode_assessment"
        ] = assessment

        self.results[
            "regen_viewer_mode_assessment_message"
        ] = message

        self.results[
            "regen_viewer_mode_generation_state"
        ] = generation_state

        if (
            mode != "manual"
            and
            generation_state
            in
            {
                "NO_FEASIBLE_DESIGN",
                "ERROR",
            }
        ):
            guidance_lines = (
                self.canonical_regen_failure_lines()
            )

            self.results[
                "regen_viewer_canonical_failure_guidance_lines"
            ] = list(
                guidance_lines
            )

            self.results[
                "regen_viewer_canonical_failure_guidance_present"
            ] = bool(
                guidance_lines
            )

        else:
            self.results[
                "regen_viewer_canonical_failure_guidance_lines"
            ] = []

            self.results[
                "regen_viewer_canonical_failure_guidance_present"
            ] = False

        self.status_strip.setText(
            message
        )

        self.status_strip.setStyleSheet(
            f"""
            QLabel {{
                background-color: {colour};
                border: 1px solid {border};
                border-radius: 4px;
                padding-left: 8px;
                padding-right: 8px;
                font-weight: 600;
            }}
            """
        )


# ---------------------------------------------------------------------------
# POST-16F REGEN VIEWER ACCEPTANCE FIX
# Geometry mode availability truth layer.
#
# Purpose:
# - Manual remains available.
# - Recommended is disabled unless real recommended geometry values exist.
# - Candidate is disabled unless a real candidate payload exists.
# - The viewer must not silently make recommended/candidate look like manual.
# ---------------------------------------------------------------------------



















# ---------------------------------------------------------------------------
# POST-16F REGEN VIEWER ACCEPTANCE FIX 2
# Hide/disable accept-reject geometry controls unless a real candidate decision
# is pending.
# ---------------------------------------------------------------------------







pass


# ---------------------------------------------------------------------------
# POST-16F.2 REGEN WORKFLOW STATUS PANEL
#
# Purpose:
# - Explain the actual regen workflow state to the user.
# - Show why Manual / Recommended / Candidate / Automatic are blocked.
# - Does not change solver physics.
# - Does not generate candidates.
# - Does not accept/reject geometry.
# ---------------------------------------------------------------------------
















pass
pass
pass
pass


# ---------------------------------------------------------------------------
# POST-16G CANDIDATE POPULATION INSPECTOR BUTTON
#
# ---------------------------------------------------------------------------










pass
pass
pass


# ---------------------------------------------------------------------------
# PHASE 16J CANDIDATE RANKING INSPECTOR BUTTON
#
# ---------------------------------------------------------------------------










pass
pass
pass


# ---------------------------------------------------------------------------
# PHASE 16P.15 — VIEWER PHYSICAL GEOMETRY VALIDATION SYNCHRONISATION
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.16 — AUTOMATIC GEOMETRY RUNTIME RE-ENTRY / STALE PAYLOAD PURGE
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.17 — COMPACT STATION GEOMETRY DUMP
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.18 — VIEWER GEOMETRY DEBUG EXPORT / COPY REPORT
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.19 — AUTOMATIC GEOMETRY RUNTIME PROOF BANNER
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.20 — REGEN VIEWER FINAL RUNTIME SIGNOFF GATE
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.21 — RUNTIME SIGNOFF REPORT EXPORT
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.22 — GUI RUNTIME SIGNOFF CHECKLIST
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16P.23 — FINAL REGEN VIEWER COMPLETION LOCK
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.2 — VIEWER FIT-METRIC RECONCILIATION REPAIR
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.5 — VIEWER MANUFACTURABILITY OVERLAY / WARNING DISPLAY
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.9 — REALISM-AWARE VIEWER RUNTIME REPORT
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.13 — REALISM + RECOMMENDATION GUI INTEGRATION SUMMARY
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.14 — RECOMMENDED GEOMETRY PANEL POPULATION REPAIR
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.15 — VIEWER DATA SYNCHRONISATION AUDIT
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.16 — AUTHORITATIVE STATION DATA PIPELINE
# ---------------------------------------------------------------------------
from leaf_qt.regen_viewer_authoritative_station_pipeline_phase_16q16 import (
    attach_authoritative_station_payload,
)

# ---------------------------------------------------------------------------
# PHASE 16Q.17 — STATION ROW GENERATION FALLBACK
# ---------------------------------------------------------------------------
from leaf_qt.regen_viewer_station_row_fallback_phase_16q17 import (
    attach_station_row_fallback,
)

# ---------------------------------------------------------------------------
# PHASE 16Q.18 — STATION TAB GUI POPULATION REPAIR
# ---------------------------------------------------------------------------
from leaf_qt.regen_viewer_station_tab_population_phase_16q18 import (
    attach_station_tab_payload,
    build_station_tab_text,
)

# ---------------------------------------------------------------------------
# PHASE 16Q.19 — TOPOLOGY PANEL GUI POPULATION REPAIR
# ---------------------------------------------------------------------------
from leaf_qt.regen_viewer_topology_panel_phase_16q19 import (
    attach_topology_panel_payload,
    build_topology_panel_text,
)

# ---------------------------------------------------------------------------
# PHASE 16Q.21 — REGEN VIEWER PANEL CLEANUP + ACTIVE GEOMETRY HIGHLIGHT
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.22 — GEOMETRY SOURCE TOGGLE HIGHLIGHT REPAIR
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.23 — EXCLUSIVE GEOMETRY TOGGLE STYLE OWNER
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.24 — REAL BUTTON DISCOVERY + FORCED TOGGLE STYLING
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.25 — AUTOMATIC GEOMETRY CACHE / INSTANT TOGGLE OWNER
# ---------------------------------------------------------------------------
from leaf_qt.regen_viewer_automatic_geometry_cache_phase_16q25 import (
    store_automatic_geometry_cache,
)

# ---------------------------------------------------------------------------
# PHASE 16Q.26 — GEOMETRY TOGGLE CACHE RUNTIME AUDIT
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.27 — FINAL VIEWER TOGGLE UX CLEANUP
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# PHASE 16Q.29 — COPY FINAL GUI ACCEPTANCE REPORT BUTTON
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CANONICAL FULL-ENGINE SIDE-PROFILE INTEGRATION
# ---------------------------------------------------------------------------
def _canonical_side_profile_points(raw_profile, source_key):
    if not isinstance(raw_profile, list):
        return []

    points = []

    for station in raw_profile:
        if not isinstance(station, dict):
            return []

        try:
            x = float(station['x'])
            radius = float(station['radius'])

        except (KeyError, TypeError, ValueError):
            return []

        if not math.isfinite(x) or not math.isfinite(radius) or radius <= 0:
            return []

        points.append({
            'x': x,
            'gas_radius': radius,
            'source': source_key,
            'section': station.get('section'),
        })

    if any(
        b['x'] < a['x']
        for a, b in zip(
            points,
            points[1:],
        )
    ):
        return []

    return points

def _interpolate_canonical_side_profile_radius(profile, x):
    if not profile:
        return None

    if x <= profile[0]['x']:
        return profile[0]['gas_radius']

    if x >= profile[-1]['x']:
        return profile[-1]['gas_radius']

    for a, b in zip(
        profile,
        profile[1:],
    ):
        if a['x'] <= x <= b['x']:
            if b['x'] == a['x']:
                return a['gas_radius']

            fraction = (
                (x - a['x'])
                / (b['x'] - a['x'])
            )

            return (
                a['gas_radius']
                + fraction
                * (
                    b['gas_radius']
                    - a['gas_radius']
                )
            )

    return None

def extract_canonical_full_engine_profile(results):
    if not isinstance(results, dict):
        results = {}

    active_model = str(
        results.get(
            'nozzle_geometry_model'
        )
        or ''
    ).upper()

    nozzle_source = (
        'conical_nozzle_profile'
        if active_model == 'CONICAL'
        else 'rao_nozzle_profile'
    )

    chamber_profile = (
        _canonical_side_profile_points(
            results.get(
                'chamber_profile'
            ),
            'chamber_profile',
        )
    )

    nozzle_profile = (
        _canonical_side_profile_points(
            results.get(
                nozzle_source
            ),
            nozzle_source,
        )
    )

    def unavailable(reason):
        return {
            'status':
                'WARN_REGEN_VIEWER_'
                'CANONICAL_FULL_ENGINE_'
                'PROFILE_UNAVAILABLE',

            'passed':
                False,

            'available':
                False,

            'authoritative':
                False,

            'exact_canonical':
                False,

            'full_engine':
                False,

            'profile':
                [],

            'profile_station_count':
                0,

            'chamber_profile_station_count':
                len(
                    chamber_profile
                ),

            'nozzle_profile_station_count':
                len(
                    nozzle_profile
                ),

            'source':
                f'chamber_profile+{nozzle_source}',

            'nozzle_source':
                nozzle_source,

            'throat_continuity':
                False,

            'reason':
                reason,
        }

    if len(chamber_profile) < 3:
        return unavailable(
            'Canonical chamber profile unavailable.'
        )

    if len(nozzle_profile) < 2:
        return unavailable(
            'Canonical nozzle profile unavailable.'
        )

    chamber_throat = chamber_profile[-1]
    nozzle_throat = nozzle_profile[0]

    if not (
        math.isclose(
            chamber_throat['x'],
            nozzle_throat['x'],
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        and
        math.isclose(
            chamber_throat['gas_radius'],
            nozzle_throat['gas_radius'],
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    ):
        return unavailable(
            'Canonical chamber and nozzle profiles '
            'do not meet at the throat.'
        )

    profile = (
        chamber_profile
        + nozzle_profile[1:]
    )

    x_min = profile[0]['x']
    x_max = profile[-1]['x']

    selected_x = 0.0

    for key in (
        'regen_viewer_selected_length',
        'selected_length',
        'selected_station_x',
        'viewer_selected_station_x',
    ):
        try:
            value = results.get(
                key
            )

            if value not in (
                None,
                '',
                'N/A',
                'None',
            ):
                selected_x = float(
                    value
                )

                break

        except (
            TypeError,
            ValueError,
        ):
            continue

    selected_x = max(
        x_min,
        min(
            x_max,
            selected_x,
        ),
    )

    marker_radius = (
        _interpolate_canonical_side_profile_radius(
            profile,
            selected_x,
        )
    )

    return {
        'status':
            'PASS_REGEN_VIEWER_'
            'CANONICAL_FULL_ENGINE_'
            'SIDE_PROFILE',

        'passed':
            True,

        'available':
            True,

        'authoritative':
            True,

        'exact_canonical':
            True,

        'full_engine':
            True,

        'profile':
            profile,

        'profile_station_count':
            len(
                profile
            ),

        'chamber_profile_station_count':
            len(
                chamber_profile
            ),

        'nozzle_profile_station_count':
            len(
                nozzle_profile
            ),

        'selected_x':
            selected_x,

        'x_min':
            x_min,

        'x_max':
            x_max,

        'r_max':
            max(
                item[
                    'gas_radius'
                ]
                for item
                in profile
            ),

        'marker_radius':
            marker_radius,

        'source':
            f'chamber_profile+{nozzle_source}',

        'nozzle_source':
            nozzle_source,

        'throat_continuity':
            True,

        'reason':
            (
                'Canonical chamber and nozzle profiles '
                'joined directly at the throat.'
            ),
    }

class RegenCanvasCanonicalSideProfile(QWidget):

    def __init__(
        self,
        results=None,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.results = (
            results
            if isinstance(
                results,
                dict,
            )
            else {}
        )

        self.setFixedSize(
            230,
            78,
        )

        self.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            True,
        )

    def set_results(
        self,
        results,
    ):
        if isinstance(
            results,
            dict,
        ):
            self.results = results

        self.update()

    def paintEvent(
        self,
        event,
    ):
        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        w = self.width()
        h = self.height()

        painter.fillRect(
            0,
            0,
            w,
            h,
            QColor(
                10,
                12,
                16,
                210,
            ),
        )

        payload = (
            extract_canonical_full_engine_profile(
                self.results
            )
        )

        profile = payload.get(
            'profile',
            [],
        )

        margin = 10
        label_height = 18
        bottom_margin = 8

        if (
            payload.get(
                'available'
            )
            and len(profile) >= 2
        ):
            model_x_min = float(
                payload[
                    'x_min'
                ]
            )

            model_x_max = float(
                payload[
                    'x_max'
                ]
            )

            r_max = float(
                payload[
                    'r_max'
                ]
            )

            x_span = max(
                model_x_max
                - model_x_min,
                1e-12,
            )

            available_width = max(
                1.0,
                float(
                    w
                    - 2 * margin
                ),
            )

            available_half_height = max(
                1.0,
                (
                    float(
                        h
                        - label_height
                        - bottom_margin
                    )
                    / 2.0
                )
                - 3.0,
            )

            scale = min(
                available_width
                / x_span,

                available_half_height
                / r_max,
            )

            rendered_width = (
                x_span
                * scale
            )

            model_left = (
                float(
                    margin
                )
                + (
                    available_width
                    - rendered_width
                )
                / 2.0
            )

            centre_y = (
                float(
                    label_height
                )
                + available_half_height
                + 3.0
            )

            def sx(x):
                return int(
                    round(
                        model_left
                        + (
                            float(x)
                            - model_x_min
                        )
                        * scale
                    )
                )

            def sy_top(radius):
                return int(
                    round(
                        centre_y
                        - float(
                            radius
                        )
                        * scale
                    )
                )

            def sy_bot(radius):
                return int(
                    round(
                        centre_y
                        + float(
                            radius
                        )
                        * scale
                    )
                )

            painter.setPen(
                QPen(
                    QColor(
                        95,
                        105,
                        120,
                    ),
                    1,
                    Qt.DashLine,
                )
            )

            painter.drawLine(
                sx(
                    model_x_min
                ),
                int(
                    round(
                        centre_y
                    )
                ),
                sx(
                    model_x_max
                ),
                int(
                    round(
                        centre_y
                    )
                ),
            )

            painter.setPen(
                QPen(
                    QColor(
                        235,
                        235,
                        235,
                    ),
                    2,
                )
            )

            for a, b in zip(
                profile,
                profile[1:],
            ):
                painter.drawLine(
                    sx(
                        a['x']
                    ),
                    sy_top(
                        a[
                            'gas_radius'
                        ]
                    ),
                    sx(
                        b['x']
                    ),
                    sy_top(
                        b[
                            'gas_radius'
                        ]
                    ),
                )

                painter.drawLine(
                    sx(
                        a['x']
                    ),
                    sy_bot(
                        a[
                            'gas_radius'
                        ]
                    ),
                    sx(
                        b['x']
                    ),
                    sy_bot(
                        b[
                            'gas_radius'
                        ]
                    ),
                )

            injector_face = (
                profile[0]
            )

            painter.drawLine(
                sx(
                    injector_face[
                        'x'
                    ]
                ),
                sy_top(
                    injector_face[
                        'gas_radius'
                    ]
                ),
                sx(
                    injector_face[
                        'x'
                    ]
                ),
                sy_bot(
                    injector_face[
                        'gas_radius'
                    ]
                ),
            )

            marker_x = sx(
                payload.get(
                    'selected_x',
                    0.0,
                )
            )

            painter.setPen(
                QPen(
                    QColor(
                        47,
                        128,
                        237,
                    ),
                    2,
                )
            )

            painter.drawLine(
                marker_x,
                label_height,
                marker_x,
                h
                - bottom_margin,
            )

            label = (
                'CANONICAL FULL ENGINE | CONICAL'
                if payload.get(
                    'nozzle_source'
                )
                == 'conical_nozzle_profile'
                else
                'CANONICAL FULL ENGINE | RAO'
            )

        else:
            painter.setPen(
                QPen(
                    QColor(
                        235,
                        235,
                        235,
                    ),
                    1,
                )
            )

            painter.drawText(
                8,
                h // 2,
                (
                    'Canonical full-engine '
                    'profile unavailable'
                ),
            )

            label = (
                'NO SCHEMATIC'
            )

        painter.setPen(
            QPen(
                QColor(
                    235,
                    235,
                    235,
                ),
                1,
            )
        )

        painter.drawText(
            8,
            13,
            label,
        )

        painter.end()

def _canonical_side_profile_find_canvas(
    self,
):
    for attr in (
        'canvas',
        'cross_section_canvas',
        'regen_canvas',
    ):
        widget = getattr(
            self,
            attr,
            None,
        )

        if widget is not None:
            return widget

    return None

def _canonical_side_profile_update_overlay(
    self,
):
    try:
        payload = (
            extract_canonical_full_engine_profile(
                self.results
            )
        )

        self.results[
            'canonical_full_engine_side_profile_status'
        ] = payload[
            'status'
        ]

        self.results[
            'canonical_full_engine_side_profile_pass'
        ] = payload[
            'passed'
        ]

        self.results[
            'canonical_full_engine_side_profile_available'
        ] = payload[
            'available'
        ]

        canvas = (
            _canonical_side_profile_find_canvas(
                self
            )
        )

        if canvas is None:
            self.results[
                'canonical_side_profile_attached'
            ] = False

            self.results[
                'canonical_side_profile_reason'
            ] = (
                'NO_CANVAS_FOUND'
            )

            return

        overlay = getattr(
            self,
            'canonical_side_profile',
            None,
        )

        if overlay is None:
            overlay = (
                RegenCanvasCanonicalSideProfile(
                    self.results,
                    canvas,
                )
            )

            self.canonical_side_profile = (
                overlay
            )

        overlay.setParent(
            canvas
        )

        overlay.move(
            max(
                8,
                canvas.width()
                - overlay.width()
                - 14,
            ),
            14,
        )

        overlay.raise_()
        overlay.show()

        overlay.set_results(
            self.results
        )

        self.results[
            'canonical_side_profile_attached'
        ] = True

        self.results.pop(
            'canonical_side_profile_reason',
            None,
        )

    except Exception as exc:
        self.results[
            'canonical_full_engine_side_profile_status'
        ] = (
            'ERROR_REGEN_VIEWER_'
            'CANONICAL_FULL_ENGINE_SIDE_PROFILE'
        )

        self.results[
            'canonical_full_engine_side_profile_error'
        ] = str(
            exc
        )

# ---------------------------------------------------------------------------
# PHASE 16T.3W.5 — REGEN CROSS SECTION VIEWER STATUS ADAPTER
# ---------------------------------------------------------------------------
# Additive viewer-level reporting adapter only.
# Does not alter rendering, Qt layout, callbacks, geometry logic, solver logic,
# existing viewer status strings, or GUI workflow behaviour.












