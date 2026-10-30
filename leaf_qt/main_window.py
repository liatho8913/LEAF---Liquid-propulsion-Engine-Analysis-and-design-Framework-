from PySide6.QtCore import QEvent, QTimer, Qt
from graph_explorer_window import GraphExplorerWindow
from input_panel import ManualInputPanel
from variable_registry import (
    LABEL_TO_VAR,
    UNITS,
    UNIT_GROUPS,
    UNIT_PREFERENCES,
    SYMBOLS,
    get_output_sections,
)

from window_launch_controller import WindowLaunchController
from calculation_controller import CalculationController
from project_state_controller import ProjectStateController
from recommended_design_controller import RecommendedDesignController
from input_assembly_controller import InputAssemblyController
from menu_controller import MenuController
from report_export_controller import ReportExportController
from foundation_layer_controller import FoundationLayerController
from benchmark_selection_controller import BenchmarkSelectionController
from result_access_controller import ResultAccessController
from result_ui_update_controller import ResultUIUpdateController
from startup_health_controller import StartupHealthController
from design_history_controller import DesignHistoryController

SECTIONS = get_output_sections()


SECURITY_INACTIVITY_CHECK_INTERVAL_MS = 1000

SECURITY_ACTIVITY_EVENT_TYPES = frozenset({
    QEvent.Type.KeyPress,
    QEvent.Type.KeyRelease,
    QEvent.Type.MouseButtonPress,
    QEvent.Type.MouseButtonRelease,
    QEvent.Type.MouseMove,
    QEvent.Type.Wheel,
    QEvent.Type.TouchBegin,
    QEvent.Type.TouchUpdate,
    QEvent.Type.TouchEnd,
    QEvent.Type.TabletPress,
    QEvent.Type.TabletMove,
    QEvent.Type.TabletRelease,
})
from output_panel import OutputPanel
import sys
from pathlib import Path
from cea_panel import CEAPanel
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from leaf_qt.storage.save_load_bridge import SaveLoadRuntimeBridge
from leaf_qt.storage.creation_owner import ProjectDesignCreationOwner
from leaf_qt.storage.project_browser_model import ProjectBrowserModel
from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator
from leaf_qt.runtime import (
    runtime_session_lifecycle,
    runtime_state_registry,
    dirty_state_manager,
    runtime_report_router,
    runtime_notification_centre,
)

try:
    from cea_integration.cea_runner import run_cea_rocket_case
except Exception:
    run_cea_rocket_case = None
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QStatusBar,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QLineEdit,
)

from diagnostics_panel import DiagnosticsPanel
from materials_panel import MaterialsPanel
from geometry_panel import GeometryPanel
from warning_panel import WarningPanel
from diagnostics_engine import DiagnosticsEngine
from regen_cross_section_viewer import RegenCrossSectionViewer
from calculation_audit import CalculationAuditEngine
from audit_panel import AuditPanel
from station_table_window import StationTableWindow

try:
    from report_viewer_window import ReportViewerWindow
    from engineering_reference_window import EngineeringReferenceWindow
except Exception:
    ReportViewerWindow = None

try:
    from foundation_test_runner_window import FoundationTestRunnerWindow
except Exception:
    FoundationTestRunnerWindow = None

try:
    from startup_health_window import StartupHealthWindow
except Exception:
    StartupHealthWindow = None

try:
    from benchmark_panel import BenchmarkPanel
except Exception:
    BenchmarkPanel = None

try:
    from foundation_status_panel import FoundationStatusPanel
except Exception:
    FoundationStatusPanel = None

try:
    from regen_geometry_output_window import RegenGeometryOutputWindow
except Exception:
    RegenGeometryOutputWindow = None

from report_ownership import (
    get_main_output_results,
    build_user_facing_report_viewer_bundle,
)

from leaf_qt.platform_lifecycle import PlatformLifecycleOwner

class LeafMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LEAF - Liquid Propulsion Engine Analysis and Design Framework")
        self.resize(1400, 850)
        self.diagnostics_engine = DiagnosticsEngine()
        self.calculation_audit_engine = CalculationAuditEngine()
        self.startup_health_controller = StartupHealthController()

        self.setStatusBar(QStatusBar())

        self.create_main_layout()

        self.benchmark_selection_controller = BenchmarkSelectionController(
            benchmark_panel=self.benchmark_panel,
        )

        self.foundation_layer_controller = FoundationLayerController(
            get_benchmark_case_callback=self.benchmark_selection_controller.get_selected_case,
            get_startup_health_callback=self.startup_health_controller.get_report,
        )

        self.result_access_controller = ResultAccessController(
            get_results_callback=self.get_last_results,
            get_main_outputs_callback=self.get_main_output_results,
        )

        self.input_assembly_controller = InputAssemblyController(
            manual_input_panel=self.manual_input_panel,
            cea_panel=self.cea_panel,
            geometry_panel=self.geometry_panel,
            materials_panel=self.materials_panel,
            get_last_results_callback=self.get_last_results,
        )

        self.design_history_controller = DesignHistoryController(
            get_inputs_callback=self.input_assembly_controller.build_combined_inputs,
        )

        self.result_ui_update_controller = ResultUIUpdateController(
            output_panel=self.output_panel,
            diagnostics_panel=self.diagnostics_panel,
            warning_panel=self.warning_panel,
            audit_panel=self.audit_panel,
            foundation_status_panel=self.foundation_status_panel,
            design_history_controller=self.design_history_controller,
            get_startup_health_callback=self.startup_health_controller.get_report,
            set_last_results_callback=self.set_last_results,
            finalize_foundation_callback=(
                self.foundation_layer_controller.finalize_foundation_regression
            ),
        )

        self.report_export_controller = ReportExportController(
            parent=self,
            result_access_controller=self.result_access_controller,
        )

        self.module_runtime_integrator = ModuleRuntimeIntegrator(
            PROJECT_ROOT
            / "leaf_qt"
            / "module_engine"
            / "definitions"
        )

        self.window_launch_controller = WindowLaunchController(
            parent=self,
            result_access_controller=self.result_access_controller,
            report_export_controller=self.report_export_controller,
            get_results_callback=lambda: getattr(self, "last_results", None),
            get_inputs_callback=self.input_assembly_controller.build_combined_inputs,
            get_startup_health_callback=self.startup_health_controller.get_report,
            get_sections_callback=lambda: SECTIONS,
            get_symbols_callback=lambda: SYMBOLS,
            get_units_callback=lambda: UNITS,
            input_tabs=self.input_tabs,
            right_tabs=self.right_tabs,
            cea_panel=self.cea_panel,
            foundation_status_panel=self.foundation_status_panel,
            report_viewer_window_class=ReportViewerWindow,
            engineering_reference_window_class=EngineeringReferenceWindow,
            foundation_test_runner_window_class=FoundationTestRunnerWindow,
            startup_health_window_class=StartupHealthWindow,
            graph_explorer_window_class=GraphExplorerWindow,
            station_table_window_class=StationTableWindow,
            regen_cross_section_viewer_class=RegenCrossSectionViewer,
            build_report_viewer_bundle=build_user_facing_report_viewer_bundle,
            regen_solver_regeneration_callback=self.regenerate_solver_from_regen_viewer_phase_16p4,
            module_runtime_integrator=self.module_runtime_integrator,
        )

        self.save_load_runtime_bridge = SaveLoadRuntimeBridge(
            session_lifecycle=runtime_session_lifecycle,
            state_registry=runtime_state_registry,
            dirty_state_manager=dirty_state_manager,
            report_router=runtime_report_router,
            notification_centre=runtime_notification_centre,
        )

        self._install_security_inactivity_monitor()

        self.project_design_creation_owner = ProjectDesignCreationOwner(
            PROJECT_ROOT
        )

        self.project_browser_model = ProjectBrowserModel(
            PROJECT_ROOT
        )

        self.project_state_controller = ProjectStateController(
            parent=self,
            manual_input_panel=self.manual_input_panel,
            cea_panel=self.cea_panel,
            geometry_panel=self.geometry_panel,
            materials_panel=self.materials_panel,
            output_panel=self.output_panel,
            warning_panel=self.warning_panel,
            foundation_status_panel=self.foundation_status_panel,
            label_to_var=LABEL_TO_VAR,
            get_last_results_callback=self.get_last_results,
            set_last_results_callback=self.set_last_results,
            get_design_history_callback=self.design_history_controller.get_history,
            set_design_history_callback=self.design_history_controller.set_history,
            get_benchmark_case_callback=self.benchmark_selection_controller.get_selected_case,
            set_benchmark_case_callback=self.benchmark_selection_controller.set_selected_case,
            get_startup_health_callback=self.startup_health_controller.get_report,
            set_status_callback=lambda message: self.statusBar().showMessage(message),
            save_load_bridge=self.save_load_runtime_bridge,
            project_design_creation_owner=self.project_design_creation_owner,
            project_browser_model=self.project_browser_model,
        )

        self.recommended_design_controller = RecommendedDesignController(
            parent=self,
            manual_input_panel=self.manual_input_panel,
            materials_panel=self.materials_panel,
            get_results_callback=lambda: getattr(self, "last_results", None),
            set_status_callback=lambda message: self.statusBar().showMessage(message),
        )

        self.calculation_controller = CalculationController(
            parent=self,
            diagnostics_engine=self.diagnostics_engine,
            calculation_audit_engine=self.calculation_audit_engine,
            get_inputs_callback=self.input_assembly_controller.build_combined_inputs,
            get_cea_inputs_callback=self.cea_panel.get_cea_inputs,
            get_benchmark_case_callback=self.benchmark_selection_controller.get_selected_case,
            get_startup_health_callback=self.startup_health_controller.get_report,
            apply_selected_material_metadata_callback=(
                lambda results: self.recommended_design_controller.apply_selected_material_metadata_to_results(results)
            ),
            apply_foundation_layers_callback=self.foundation_layer_controller.apply_foundation_layers,
            update_ui_callback=self.result_ui_update_controller.update_after_calculation,
            set_cea_raw_output_callback=self.cea_panel.set_raw_output,
            set_status_callback=lambda message: self.statusBar().showMessage(message),
            run_cea_rocket_case=run_cea_rocket_case,
            module_runtime_integrator=self.module_runtime_integrator,
        )

        self.menu_controller = MenuController(
            main_window=self,
            report_export_controller=self.report_export_controller,
            window_launch_controller=self.window_launch_controller,
            project_state_controller=self.project_state_controller,
            calculation_controller=self.calculation_controller,
            recommended_design_controller=self.recommended_design_controller,
            input_assembly_controller=self.input_assembly_controller,
            output_panel=self.output_panel,
            get_last_results_callback=self.get_last_results,
        )

        self.menu_controller.create_menu_bar()

        if hasattr(self, "foundation_status_panel") and self.foundation_status_panel is not None:
            self.foundation_status_panel.update_status(
                results={},
                startup_health_report=self.startup_health_controller.get_report(),
            )

        self.materials_panel.apply_button.clicked.connect(
            lambda: self.recommended_design_controller.apply_liner_material_to_regen_inputs()
        )

        startup_status = self.startup_health_controller.get_status()

        self.statusBar().showMessage(f"Ready | Startup Health: {startup_status}")

        self._install_security_lock_presentation()
        self._sync_security_lock_presentation()

        self._platform_lifecycle_owner = (
            PlatformLifecycleOwner(
                parent=self
            )
        )

        self._platform_lifecycle_owner.restrictive_event.connect(
            self._handle_platform_restrictive_event
        )

        self._platform_lifecycle_owner.start()

    def _install_security_inactivity_monitor(
        self,
    ) -> bool:
        """
        Install application-wide activity forwarding and one
        periodic inactivity evaluation timer.

        Qt observes application activity only. Authentication
        configuration and security transitions remain owned by
        their canonical non-Qt owners.
        """
        if hasattr(
            self,
            "_security_inactivity_timer",
        ):
            return False

        application = (
            QApplication.instance()
        )

        if application is None:
            raise RuntimeError(
                "qt_application_required_for_"
                "security_inactivity_monitor"
            )

        application.installEventFilter(
            self
        )

        self._security_inactivity_timer = (
            QTimer(
                self
            )
        )

        self._security_inactivity_timer.setInterval(
            SECURITY_INACTIVITY_CHECK_INTERVAL_MS
        )

        self._security_inactivity_timer.timeout.connect(
            self._evaluate_security_inactivity
        )

        self._security_inactivity_timer.start()

        return True

    def eventFilter(
        self,
        watched,
        event,
    ):
        if (
            watched is self
            and
            event.type()
            ==
            QEvent.Type.Resize
            and
            hasattr(
                self,
                "_security_lock_overlay",
            )
        ):
            self._security_lock_overlay.setGeometry(
                self.rect()
            )

        if (
            event.type()
            in
            SECURITY_ACTIVITY_EVENT_TYPES
        ):
            try:
                runtime_session_lifecycle.record_security_activity()

            except RuntimeError as exc:
                if (
                    str(exc)
                    !=
                    "runtime_session_not_open"
                ):
                    raise

        return super().eventFilter(
            watched,
            event,
        )


    def _evaluate_security_inactivity(
        self,
    ) -> bool:
        self._sync_security_lock_presentation()

        security_context = (
            self.save_load_runtime_bridge
            .security_context
        )

        if not security_context.requires_explicit_unlock:
            return False

        try:
            expired = (
                runtime_session_lifecycle
                .security_inactivity_expired(
                    security_context
                    .inactivity_timeout_seconds
                )
            )

        except RuntimeError as exc:
            if (
                str(exc)
                ==
                "runtime_session_not_open"
            ):
                return False

            raise

        if not expired:
            return False

        return (
            self._request_restrictive_runtime_lock()
        )



    def _install_security_lock_presentation(
        self,
    ) -> bool:
        """
        Create one opaque in-window lock surface.

        Qt collects the credential transiently but does not
        verify it or mutate security state.
        """
        if hasattr(
            self,
            "_security_lock_overlay",
        ):
            return False

        overlay = QWidget(
            self
        )

        overlay.setObjectName(
            "leaf_security_lock_overlay"
        )

        overlay.setAutoFillBackground(
            True
        )

        overlay.setPalette(
            self.palette()
        )

        layout = QVBoxLayout(
            overlay
        )

        layout.addStretch(
            1
        )

        title = QLabel(
            "LEAF is locked",
            overlay,
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        message = QLabel(
            "Enter your local credential to continue.",
            overlay,
        )

        message.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        credential_input = QLineEdit(
            overlay
        )

        credential_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        credential_input.setPlaceholderText(
            "Credential"
        )

        credential_input.setMaximumWidth(
            360
        )

        unlock_button = QPushButton(
            "Unlock",
            overlay,
        )

        unlock_button.setMaximumWidth(
            180
        )

        error_label = QLabel(
            "",
            overlay,
        )

        error_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            message
        )

        layout.addWidget(
            credential_input,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        layout.addWidget(
            unlock_button,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        layout.addWidget(
            error_label
        )

        layout.addStretch(
            1
        )

        credential_input.returnPressed.connect(
            self._submit_security_unlock
        )

        unlock_button.clicked.connect(
            self._submit_security_unlock
        )

        overlay.hide()

        self._security_lock_overlay = (
            overlay
        )

        self._security_unlock_input = (
            credential_input
        )

        self._security_unlock_error = (
            error_label
        )

        self._security_hidden_top_level_widgets = []

        self._security_central_enabled_before_lock = (
            None
        )

        self._security_menu_enabled_before_lock = (
            None
        )

        return True

    def _sync_security_lock_presentation(
        self,
    ) -> bool:
        """
        Reflect the canonical runtime LOCKED / UNLOCKED state.

        No authentication decision is made here.
        """
        if not hasattr(
            self,
            "_security_lock_overlay",
        ):
            return False

        try:
            session = (
                runtime_session_lifecycle
                .require_session()
            )

        except RuntimeError as exc:
            if (
                str(exc)
                !=
                "runtime_session_not_open"
            ):
                raise

            locked = False

        else:
            locked = (
                session.is_security_locked
            )

        overlay = (
            self._security_lock_overlay
        )

        presentation_was_locked = (
            not overlay.isHidden()
        )

        central = (
            self.centralWidget()
        )

        menu = (
            self.menuBar()
        )

        if locked:
            if not presentation_was_locked:
                self._security_central_enabled_before_lock = (
                    central.isEnabled()
                    if central is not None
                    else None
                )

                self._security_menu_enabled_before_lock = (
                    menu.isEnabled()
                )

                if central is not None:
                    central.setEnabled(
                        False
                    )

                menu.setEnabled(
                    False
                )

            # Any previously visible top-level engineering windows
            # are hidden while locked. Repeated synchronisation also
            # catches a window that appears after the lock occurred.
            hidden = (
                self
                ._security_hidden_top_level_widgets
            )

            for widget in (
                QApplication.topLevelWidgets()
            ):
                if (
                    widget is self
                    or
                    not widget.isVisible()
                ):
                    continue

                if widget not in hidden:
                    hidden.append(
                        widget
                    )

                widget.hide()

            overlay.setGeometry(
                self.rect()
            )

            overlay.show()
            overlay.raise_()

            self._security_unlock_input.setFocus(
                Qt.FocusReason.OtherFocusReason
            )

            return True

        if presentation_was_locked:
            overlay.hide()

            if (
                central is not None
                and
                self._security_central_enabled_before_lock
                is not None
            ):
                central.setEnabled(
                    bool(
                        self
                        ._security_central_enabled_before_lock
                    )
                )

            if (
                self._security_menu_enabled_before_lock
                is not None
            ):
                menu.setEnabled(
                    bool(
                        self
                        ._security_menu_enabled_before_lock
                    )
                )

            hidden = list(
                self
                ._security_hidden_top_level_widgets
            )

            self._security_hidden_top_level_widgets.clear()

            for widget in hidden:
                try:
                    widget.show()

                except RuntimeError:
                    # The Qt object may have been destroyed while
                    # hidden; it must not block unlock restoration.
                    continue

            self._security_central_enabled_before_lock = (
                None
            )

            self._security_menu_enabled_before_lock = (
                None
            )

            self._security_unlock_input.clear()
            self._security_unlock_error.clear()

        return False

    def _submit_security_unlock(
        self,
    ) -> bool:
        """
        Forward one transient credential to the canonical
        authenticated runtime-unlock boundary.
        """
        security_context = (
            self.save_load_runtime_bridge
            .security_context
        )

        credential = (
            self._security_unlock_input
            .text()
        )

        self._security_unlock_input.clear()
        self._security_unlock_error.clear()

        try:
            try:
                changed = (
                    security_context
                    .unlock_runtime_session(
                        credential,
                        runtime_session_lifecycle,
                    )
                )

            finally:
                credential = None

        except (
            PermissionError,
            TypeError,
            ValueError,
        ):
            self._security_unlock_error.setText(
                "Unable to unlock LEAF."
            )

            self._sync_security_lock_presentation()

            self._security_unlock_input.setFocus(
                Qt.FocusReason.OtherFocusReason
            )

            return False

        try:
            session = (
                runtime_session_lifecycle
                .require_session()
            )

        except RuntimeError:
            self._sync_security_lock_presentation()
            raise

        if (
            not session.is_security_unlocked
        ):
            self._sync_security_lock_presentation()

            raise RuntimeError(
                "runtime_unlock_ui_state_verification_failed"
            )

        self._sync_security_lock_presentation()

        return bool(
            changed
            or
            session.is_security_unlocked
        )

    def _request_restrictive_runtime_lock(
        self,
    ) -> bool:
        """
        Request the canonical restrictive runtime transition and
        immediately reflect canonical state in the UI.
        """
        security_context = (
            self.save_load_runtime_bridge
            .security_context
        )

        if not security_context.requires_explicit_unlock:
            self._sync_security_lock_presentation()
            return False

        try:
            changed = (
                security_context
                .lock_runtime_session(
                    runtime_session_lifecycle
                )
            )

        finally:
            self._sync_security_lock_presentation()

        return bool(
            changed
        )

    def _request_manual_runtime_lock(
        self,
    ) -> bool:
        return (
            self._request_restrictive_runtime_lock()
        )

    def _handle_platform_restrictive_event(
        self,
        event_name: str,
    ) -> bool:
        del event_name

        return (
            self._request_restrictive_runtime_lock()
        )


    def closeEvent(
        self,
        event,
    ):
        lifecycle_owner = getattr(
            self,
            "_platform_lifecycle_owner",
            None,
        )

        if lifecycle_owner is not None:
            lifecycle_owner.stop()

        super().closeEvent(
            event
        )

    def get_main_output_results(self):
        return get_main_output_results(getattr(self, "last_results", None))

    def get_last_results(self):
        return getattr(self, "last_results", {})

    def _show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def set_last_results(self, results):
        self.last_results = results if isinstance(results, dict) else {}


    def regenerate_solver_from_regen_viewer_phase_16p4(self, geometry, viewer_results):
        """
        Phase 16P.4B
        Main-window callback used by the regen cross-section viewer.

        The viewer owns geometry preview/application state.
        The main window owns recalculation through CalculationController.
        """
        if not isinstance(viewer_results, dict):
            viewer_results = {}

        if not isinstance(geometry, dict):
            geometry = {}

        viewer_results["phase_16p4_main_window_regeneration_callback_called"] = True
        viewer_results["phase_16p4_main_window_regeneration_geometry"] = dict(geometry)

        try:
            # Inject applied regen geometry into the input assembly override first.
            # This is required because normal manual/geometry panel inputs are applied
            # after last_results and can otherwise overwrite automatic regen geometry.
            if hasattr(self, "input_assembly_controller"):
                applied_override = (
                    self.input_assembly_controller.set_regen_geometry_override_phase_16p4(
                        geometry
                    )
                )
                viewer_results["phase_16p4_input_override_geometry"] = dict(applied_override)
                viewer_results["phase_16p4_input_override_applied"] = bool(applied_override)

            # Preserve the applied regen geometry in the shared last_results payload
            # before requesting recalculation. This lets downstream reports/viewers see
            # what geometry triggered the regeneration request.
            current = self.get_last_results()
            if isinstance(current, dict):
                current["phase_16p4_regeneration_requested_geometry"] = dict(geometry)
                current["phase_16p4_regeneration_requested_from_viewer"] = True
                self.set_last_results(current)

            calculation_mode = "Manual"

            if hasattr(self, "cea_panel"):
                cea_inputs = self.cea_panel.get_cea_inputs()
                calculation_mode = str(
                    cea_inputs.get("calculation_mode") or "Manual"
                )

            if calculation_mode.upper() == "CEA":
                self.run_cea_and_calculate()
            else:
                self.calculate()

            latest = self.get_last_results()

            if not isinstance(latest, dict):
                raise RuntimeError(
                    "Viewer regeneration did not produce a result dictionary."
                )

            required_outputs = (
                "throat_area",
                "exit_area",
                "characteristic_velocity",
                "thrust",
                "specific_impulse",
            )

            missing_outputs = [
                key for key in required_outputs
                if latest.get(key) is None
            ]

            if missing_outputs:
                raise RuntimeError(
                    "Viewer regeneration calculation incomplete; missing outputs: "
                    + ", ".join(missing_outputs)
                )

            viewer_results.update(latest)

            viewer_results["phase_16p3_live_solver_regenerated"] = True
            viewer_results["phase_16p4_main_window_regeneration_status"] = (
                "PASS_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4"
            )
            viewer_results["phase_16p4_main_window_regeneration_message"] = (
                "Main window calculation path was requested after regen geometry application."
            )

            return {
                "phase_16p3_live_solver_regenerated": True,
                "phase_16p4_main_window_regeneration_status": (
                    "PASS_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4"
                ),
                "phase_16p4_main_window_regeneration_message": (
                    "Main window calculation path was requested after regen geometry application."
                ),
                "phase_16p4_regeneration_requested_geometry": dict(geometry),
            }

        except Exception as exc:
            viewer_results["phase_16p3_live_solver_regenerated"] = False
            viewer_results["phase_16p4_main_window_regeneration_status"] = (
                "FAIL_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4"
            )
            viewer_results["phase_16p4_main_window_regeneration_message"] = str(exc)

            return {
                "phase_16p3_live_solver_regenerated": False,
                "phase_16p4_main_window_regeneration_status": (
                    "FAIL_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4"
                ),
                "phase_16p4_main_window_regeneration_message": str(exc),
                "phase_16p4_regeneration_requested_geometry": dict(geometry),
            }



    def run_cea_and_calculate(self):
        return self.calculation_controller.run_cea_and_calculate()

    def calculate(self):
        return self.calculation_controller.calculate()

    def create_main_layout(self):
        splitter = QSplitter(Qt.Horizontal)

        self.input_tabs = QTabWidget()

        self.manual_input_panel = ManualInputPanel(
            LABEL_TO_VAR,
            UNITS,
            UNIT_GROUPS,
            UNIT_PREFERENCES
        )

        self.input_tabs.addTab(
            self.manual_input_panel,
            "Manual Inputs"
        )

        self.cea_panel = CEAPanel()

        self.input_tabs.addTab(
            self.cea_panel,
            "Propellants"
        )

        self.geometry_panel = GeometryPanel()

        self.input_tabs.addTab(
            self.geometry_panel,
            "Geometry"
        )

        self.materials_panel = MaterialsPanel()

        self.input_tabs.addTab(
            self.materials_panel,
            "Materials"
        )

        if BenchmarkPanel is not None:
            self.benchmark_panel = BenchmarkPanel()

        else:
            self.benchmark_panel = None

        self.right_tabs = QTabWidget()

        self.output_panel = OutputPanel(
            SECTIONS,
            SYMBOLS,
            UNITS
        )

        self.diagnostics_panel = DiagnosticsPanel()
        self.warning_panel = WarningPanel()
        self.audit_panel = AuditPanel()
        self.foundation_status_panel = None

        if FoundationStatusPanel is not None:
            self.foundation_status_panel = FoundationStatusPanel()

        self.right_tabs.addTab(self.output_panel, "Outputs")

        if self.foundation_status_panel is not None:
            self.right_tabs.addTab(self.foundation_status_panel, "Foundation Status")

        self.right_tabs.addTab(self.diagnostics_panel, "Diagnostics")
        self.right_tabs.addTab(self.warning_panel, "Warnings")
        self.right_tabs.addTab(self.audit_panel, "Calculation Audit")
        self.right_tabs.addTab(
            self.create_regen_geometry_diagnostics_tab(),
            "Regen Geometry"
        )
        self.left_panel = QWidget()

        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.addWidget(self.input_tabs, 1)

        self.calculate_button = QPushButton("CALCULATE")
        self.calculate_button.setObjectName("mainCalculateButton")
        self.calculate_button.setMinimumHeight(46)
        self.calculate_button.setToolTip(
            "Run the current LEAF calculation."
        )

        calculate_font = self.calculate_button.font()
        calculate_font.setBold(True)
        self.calculate_button.setFont(calculate_font)

        self.calculate_button.clicked.connect(self.calculate)

        left_layout.addWidget(
            self.calculate_button,
            0,
        )

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_tabs)
        splitter.setSizes([450, 950])

        self.setCentralWidget(splitter)

    def create_regen_geometry_diagnostics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        title = QLabel("Regen Geometry Diagnostics")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        description = QLabel(
            "View regen geometry validation, recommendations, candidate geometry, "
            "and before/after comparison data."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        self.regen_geometry_diagnostics_button = QPushButton(
            "Open Regen Geometry Diagnostics"
        )
        self.regen_geometry_diagnostics_button.clicked.connect(
            self.open_regen_geometry_output_window
        )
        layout.addWidget(self.regen_geometry_diagnostics_button)

        layout.addStretch(1)

        return tab

    def open_regen_geometry_output_window(self):
        if RegenGeometryOutputWindow is None:
            self._show_message(
                "Regen Geometry Diagnostics",
                "RegenGeometryOutputWindow could not be imported.",
            )
            return

        results = getattr(self, "last_results", None)

        if not isinstance(results, dict):
            results = getattr(self, "results", None)

        if not isinstance(results, dict):
            self._show_message(
                "Regen Geometry Diagnostics",
                "Run the solver first so regen geometry diagnostics are available.",
            )
            return

        self.regen_geometry_output_window = RegenGeometryOutputWindow(
            results=results,
            parent=self,
        )
        self.regen_geometry_output_window.show()
