from pathlib import Path
import re

path = Path("leaf_qt/regen_cross_section_viewer.py")

if not path.exists():
    raise SystemExit("Missing leaf_qt/regen_cross_section_viewer.py")

text = path.read_text()

backup = path.with_suffix(".py.post16f_mode_availability_backup")
backup.write_text(text)

helper_block = r'''
    def geometry_source_available(self, source):
        """
        Post-16F viewer acceptance rule.

        The viewer must not silently display manual geometry when the user
        asks for recommended/candidate geometry that does not actually exist.
        """
        source = str(source or "manual").lower()

        if source == "manual":
            return True

        results = self.results if isinstance(getattr(self, "results", None), dict) else {}

        def first_float(keys, default=None):
            for key in keys:
                try:
                    value = results.get(key)
                    if value is None or value == "":
                        continue
                    return float(value)
                except Exception:
                    continue
            return default

        def first_int(keys, default=0):
            for key in keys:
                try:
                    value = results.get(key)
                    if value is None or value == "":
                        continue
                    return int(float(value))
                except Exception:
                    continue
            return default

        if source == "recommended":
            width = first_float([
                "recommended_channel_width",
                "recommended_coolant_channel_width",
                "phase_11a5_recommended_channel_width",
                "phase_11a4_recommended_channel_width",
                "phase_11a5_regen_geometry_apply_recommendation_owner_channel_width",
                "phase_11a4_regen_geometry_recommendation_engine_owner_channel_width",
            ])
            height = first_float([
                "recommended_channel_height",
                "recommended_coolant_channel_height",
                "phase_11a5_recommended_channel_height",
                "phase_11a4_recommended_channel_height",
                "phase_11a5_regen_geometry_apply_recommendation_owner_channel_height",
                "phase_11a4_regen_geometry_recommendation_engine_owner_channel_height",
            ])
            rib = first_float([
                "recommended_rib_width",
                "recommended_requested_rib_width",
                "phase_11a5_recommended_rib_width",
                "phase_11a4_recommended_rib_width",
                "phase_11a5_regen_geometry_apply_recommendation_owner_rib_width",
                "phase_11a4_regen_geometry_recommendation_engine_owner_rib_width",
            ])
            count = first_int([
                "recommended_channel_count",
                "recommended_number_of_coolant_channels",
                "phase_11a5_recommended_channel_count",
                "phase_11a4_recommended_channel_count",
                "phase_11a5_regen_geometry_apply_recommendation_owner_channel_count",
                "phase_11a4_regen_geometry_recommendation_engine_owner_channel_count",
            ])

            return (
                width is not None and width > 0.0
                and height is not None and height > 0.0
                and rib is not None and rib >= 0.0
                and count > 0
            )

        if source == "candidate":
            candidate = None

            canvas = getattr(self, "canvas", None)
            if canvas is not None and hasattr(canvas, "get_phase_11a_candidate_geometry"):
                try:
                    candidate = canvas.get_phase_11a_candidate_geometry()
                except Exception:
                    candidate = None

            if candidate is None and hasattr(self, "get_phase_11a_candidate_geometry"):
                try:
                    candidate = self.get_phase_11a_candidate_geometry()
                except Exception:
                    candidate = None

            if not isinstance(candidate, dict) or not candidate:
                candidate = results.get("recommended_geometry_candidate")

            if not isinstance(candidate, dict) or not candidate:
                candidate = results.get("regen_geometry_recommended_candidate")

            if not isinstance(candidate, dict) or not candidate:
                return False

            def dict_float(data, keys, default=None):
                for key in keys:
                    try:
                        value = data.get(key)
                        if value is None or value == "":
                            continue
                        return float(value)
                    except Exception:
                        continue
                return default

            def dict_int(data, keys, default=0):
                for key in keys:
                    try:
                        value = data.get(key)
                        if value is None or value == "":
                            continue
                        return int(float(value))
                    except Exception:
                        continue
                return default

            width = dict_float(candidate, [
                "channel_width",
                "coolant_channel_width",
                "recommended_channel_width",
                "recommended_coolant_channel_width",
            ])
            height = dict_float(candidate, [
                "channel_height",
                "coolant_channel_height",
                "recommended_channel_height",
                "recommended_coolant_channel_height",
            ])
            rib = dict_float(candidate, [
                "rib_width",
                "requested_rib_width",
                "recommended_rib_width",
                "recommended_requested_rib_width",
            ])
            count = dict_int(candidate, [
                "channel_count",
                "number_of_coolant_channels",
                "recommended_channel_count",
                "recommended_number_of_coolant_channels",
            ])

            return (
                width is not None and width > 0.0
                and height is not None and height > 0.0
                and rib is not None and rib >= 0.0
                and count > 0
            )

        if source == "comparison":
            return self.geometry_source_available("recommended")

        if source == "automatic":
            automatic = results.get("regen_autonomous_committed_geometry")
            if not isinstance(automatic, dict):
                automatic = results.get("regen_runtime_best_candidate")
            return isinstance(automatic, dict) and bool(automatic)

        return False

    def refresh_geometry_source_availability(self):
        """
        Disable viewer modes that do not have real data yet.

        This prevents the pre-solve viewer from making recommended geometry
        look identical to manual geometry.
        """
        button_map = {}

        for name, attr in (
            ("manual", "manual_button"),
            ("recommended", "recommended_button"),
            ("candidate", "candidate_button"),
            ("comparison", "comparison_button"),
            ("automatic", "automatic_button"),
        ):
            if hasattr(self, attr):
                button_map[name] = getattr(self, attr)

        for source, button in button_map.items():
            available = self.geometry_source_available(source)
            try:
                button.setEnabled(bool(available))
            except Exception:
                pass

            if source == "manual":
                tooltip = "Manual input geometry is always available."
            elif available:
                tooltip = f"{source.title()} geometry is available."
            else:
                tooltip = (
                    f"{source.title()} geometry is not available yet. "
                    "Run a solve / recommendation / candidate generation first."
                )

            try:
                button.setToolTip(tooltip)
            except Exception:
                pass

        if isinstance(getattr(self, "results", None), dict):
            self.results["regen_viewer_manual_geometry_available"] = self.geometry_source_available("manual")
            self.results["regen_viewer_recommended_geometry_available"] = self.geometry_source_available("recommended")
            self.results["regen_viewer_candidate_geometry_available"] = self.geometry_source_available("candidate")
            self.results["regen_viewer_comparison_geometry_available"] = self.geometry_source_available("comparison")
'''

if "def geometry_source_available(self, source):" not in text:
    marker = "    def set_geometry_source(self, source):"
    if marker not in text:
        raise SystemExit("Could not find set_geometry_source method.")
    text = text.replace(marker, helper_block + "\n" + marker)

pattern = re.compile(
    r"    def set_geometry_source\(self, source\):\n"
    r".*?"
    r"(?=\n    def refresh_geometry_source_button_styles\(self\):)",
    re.S,
)

new_set_geometry_source = r'''    def set_geometry_source(self, source):
        """
        Route geometry-source button requests into the canvas.

        Post-16F acceptance rule:
        recommended/candidate/comparison modes must only activate when their
        own geometry exists. Otherwise the viewer remains on manual and records
        why the requested mode was rejected.
        """
        allowed_sources = ("manual", "recommended", "candidate", "comparison", "automatic")

        if source not in allowed_sources:
            source = "manual"

        requested_source = source

        if not self.geometry_source_available(source):
            source = "manual"
            if isinstance(getattr(self, "results", None), dict):
                self.results["regen_viewer_geometry_source_rejected"] = requested_source
                self.results["regen_viewer_geometry_source_rejection_reason"] = (
                    f"{requested_source} geometry is not available yet."
                )

        self.refresh_geometry_source_availability()

        self.canvas.set_geometry_source(source)

        if source == "comparison":
            self.canvas.set_view_mode("full")

        geometry = self.canvas.get_geometry(source)

        self.results["regen_viewer_requested_geometry_source"] = requested_source
        self.results["regen_viewer_active_geometry_source"] = source
        self.results["regen_viewer_actual_geometry_source"] = geometry.get("source")
        self.results["regen_viewer_debug_channel_count"] = geometry.get("channel_count")
        self.results["regen_viewer_debug_channel_width"] = geometry.get("channel_width")
        self.results["regen_viewer_debug_channel_height"] = geometry.get("channel_height")
        self.results["regen_viewer_debug_gas_radius"] = geometry.get("gas_radius")

        self.refresh_geometry_source_button_styles()
        self.refresh_values_panel()

        self.canvas.update()
        self.canvas.repaint()
'''

text, n = pattern.subn(new_set_geometry_source, text)
if n != 1:
    raise SystemExit(f"Expected to replace one set_geometry_source method, replaced {n}.")

pattern = re.compile(
    r"    def refresh_geometry_source_button_styles\(self\):\n"
    r".*?"
    r"(?=\n    def build_body\(self\):)",
    re.S,
)

new_refresh = r'''    def refresh_geometry_source_button_styles(self):
        """
        Visual feedback only. Buttons remain push buttons, not toggle buttons.

        Unavailable geometry modes are disabled and visually muted so that
        recommended/candidate cannot appear identical to manual before a solve.
        """
        self.refresh_geometry_source_availability()

        active = self.canvas.geometry_source

        button_map = {}

        for source, attr in (
            ("manual", "manual_button"),
            ("recommended", "recommended_button"),
            ("candidate", "candidate_button"),
            ("comparison", "comparison_button"),
            ("automatic", "automatic_button"),
        ):
            if hasattr(self, attr):
                button_map[source] = getattr(self, attr)

        for source, button in button_map.items():
            available = self.geometry_source_available(source)

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
            elif not available:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2f2f2f;
                        color: #888888;
                        border: 1px solid #444444;
                        padding: 3px 8px;
                    }
                """)
            else:
                button.setStyleSheet("")
'''

text, n = pattern.subn(new_refresh, text)
if n != 1:
    raise SystemExit(f"Expected to replace one refresh_geometry_source_button_styles method, replaced {n}.")

path.write_text(text)

print("POST16F_REGEN_VIEWER_MODE_AVAILABILITY_PATCHED")
print(f"Backup written to: {backup}")
