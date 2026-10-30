from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)

from output_panel import OutputPanel
from leaf_qt.module_engine.module_runtime_manifest import (
    ACTIVE,
    USER_DEACTIVATED,
)


class WindowLaunchController:
    """
    Owns secondary windows, report viewers, and tab-launch actions.

    Important:
    - Full-result windows use ResultAccessController.current_results().
    - Main Outputs uses ResultAccessController.current_main_outputs().
    - Report text dialogs use QTextEdit so long reports remain readable.
    """

    def __init__(
            self,
            parent,
            result_access_controller,
            report_export_controller,
            get_results_callback,
            get_inputs_callback,
            get_startup_health_callback,
            get_sections_callback,
            get_symbols_callback,
            get_units_callback,
            input_tabs,
            right_tabs,
            cea_panel,
            foundation_status_panel=None,
            report_viewer_window_class=None,
            foundation_test_runner_window_class=None,
            startup_health_window_class=None,
            graph_explorer_window_class=None,
            station_table_window_class=None,
            regen_cross_section_viewer_class=None,
            build_report_viewer_bundle=None,
            regen_solver_regeneration_callback=None,
            module_runtime_integrator=None,
            engineering_reference_window_class=None,
    ):
        self.parent = parent
        self.result_access_controller = result_access_controller

        self.report_export_controller = report_export_controller
        # Kept for compatibility with older call sites/tools.
        self.get_results = get_results_callback

        self.get_inputs = get_inputs_callback
        self.get_startup_health = get_startup_health_callback
        self.get_sections = get_sections_callback
        self.get_symbols = get_symbols_callback
        self.get_units = get_units_callback

        self.input_tabs = input_tabs
        self.right_tabs = right_tabs
        self.cea_panel = cea_panel
        self.foundation_status_panel = foundation_status_panel

        self.ReportViewerWindow = report_viewer_window_class
        self.EngineeringReferenceWindow = engineering_reference_window_class
        self.FoundationTestRunnerWindow = foundation_test_runner_window_class
        self.StartupHealthWindow = startup_health_window_class
        self.GraphExplorerWindow = graph_explorer_window_class
        self.StationTableWindow = station_table_window_class
        self.RegenCrossSectionViewer = regen_cross_section_viewer_class

        self.build_report_viewer_bundle = build_report_viewer_bundle
        self.regen_solver_regeneration_callback = regen_solver_regeneration_callback
        self.module_runtime_integrator = module_runtime_integrator

    def require_results(self, message="Run a calculation first."):
        return self.result_access_controller.require_results(
            parent=self.parent,
            message=message,
        )

    def require_main_outputs(self):
        return self.result_access_controller.require_main_outputs(
            parent=self.parent,
        )

    def show_text_report_dialog(self, title, report_text):
        if not report_text:
            report_text = "No report text available. Run a calculation first."

        dialog = QDialog(self.parent)
        dialog.setWindowTitle(title)
        dialog.resize(1000, 750)

        layout = QVBoxLayout(dialog)

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setPlainText(str(report_text))

        layout.addWidget(text_box)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec()

    def show_report_viewer(self):
        if self.ReportViewerWindow is None:
            QMessageBox.warning(
                self.parent,
                "Report Viewer Unavailable",
                "The Report Viewer module could not be loaded.",
            )
            return

        if self.build_report_viewer_bundle is None:
            QMessageBox.warning(
                self.parent,
                "Report Builder Unavailable",
                "The report bundle builder could not be loaded.",
            )
            return

        results = self.require_results(
            "Run a calculation before opening the Report Viewer."
        )

        if results is None:
            return

        reports = self.build_report_viewer_bundle(results)

        window = self.ReportViewerWindow(
            self.parent,
            title="LEAF Report Viewer",
            reports=reports,
            export_controller=self.report_export_controller,
        )
        window.exec()

    def show_startup_health_window(self):
        if self.StartupHealthWindow is None:
            QMessageBox.warning(
                self.parent,
                "Startup Health Window Unavailable",
                "The Startup Health window module could not be loaded.",
            )
            return

        window = self.StartupHealthWindow(
            self.parent,
            health_report=self.get_startup_health(),
        )
        window.exec()


    def show_engineering_reference(self):
        if self.EngineeringReferenceWindow is None:
            QMessageBox.warning(
                self.parent,
                "Engineering Reference Unavailable",
                "The Engineering Reference window could not be loaded.",
            )
            return

        window = self.EngineeringReferenceWindow(
            self.parent
        )

        window.exec()

    def show_foundation_test_runner(self):
        if self.FoundationTestRunnerWindow is None:
            QMessageBox.warning(
                self.parent,
                "Foundation Test Runner Unavailable",
                "The Foundation Test Runner module could not be loaded.",
            )
            return

        results = self.require_results(
            "Run a calculation before opening the Foundation Test Runner."
        )

        if results is None:
            return

        window = self.FoundationTestRunnerWindow(self.parent, results)
        window.exec()

    def show_graph_explorer(self):
        if self.GraphExplorerWindow is None:
            QMessageBox.warning(
                self.parent,
                "Graph Explorer Unavailable",
                "The Graph Explorer module could not be loaded.",
            )
            return

        inputs = self.get_inputs()
        results = self.result_access_controller.current_results()

        if not isinstance(
            inputs,
            dict,
        ):
            inputs = {}

        else:
            inputs = dict(
                inputs
            )

        if isinstance(
            results,
            dict,
        ):
            inputs.update(
                results
            )

        regen_transfer = getattr(
            self,
            "_regen_graph_transfer_state",
            {},
        )

        if isinstance(
            regen_transfer,
            dict,
        ):
            for key, value in (
                regen_transfer.items()
            ):

                if isinstance(
                    value,
                    dict,
                ):
                    value = dict(
                        value
                    )

                elif isinstance(
                    value,
                    list,
                ):
                    value = list(
                        value
                    )

                inputs[
                    key
                ] = value

        available_input_keys = []

        input_owner = getattr(
            self.parent,
            "input_assembly_controller",
            None,
        )

        available_callback = getattr(
            input_owner,
            "get_available_graph_input_keys",
            None,
        )

        if callable(
            available_callback
        ):
            try:
                available_input_keys = list(
                    available_callback()
                    or
                    []
                )

            except Exception:
                available_input_keys = []

        design_history = []

        history_owner = getattr(
            self.parent,
            "design_history_controller",
            None,
        )

        history_callback = getattr(
            history_owner,
            "get_history",
            None,
        )

        if callable(
            history_callback
        ):
            try:
                design_history = list(
                    history_callback()
                    or
                    []
                )

            except Exception:
                design_history = []

        inputs[
            "__leaf_graph_available_input_keys__"
        ] = available_input_keys

        inputs[
            "__leaf_graph_design_history__"
        ] = design_history

        window = self.GraphExplorerWindow(
            self.parent,
            inputs,
        )

        window.exec()

    def show_station_table(self):
        if self.StationTableWindow is None:
            QMessageBox.warning(
                self.parent,
                "Station Table Unavailable",
                "The Station Table module could not be loaded.",
            )
            return

        results = self.require_results(
            "Run a calculation before opening the Station Table."
        )

        if results is None:
            return

        window = self.StationTableWindow(self.parent, results)
        window.exec()

    def show_regen_cross_section_viewer(self):
        if self.RegenCrossSectionViewer is None:
            QMessageBox.warning(
                self.parent,
                "Regen Viewer Unavailable",
                "The Regen Cross-Section Viewer module could not be loaded.",
            )
            return

        results = self.require_results(
            "Calculate the engine before opening the regen cross-section viewer."
        )

        if results is None:
            return

        viewer = self.RegenCrossSectionViewer(
            results,
            self.parent,
            regeneration_callback=self.regen_solver_regeneration_callback,
        )

        viewer.exec()

        # Viewer -> Graph Explorer is a presentation/analysis transfer
        # boundary. Keep this session state local to the existing window
        # launch owner rather than inventing a persistence system.
        transfer = {}

        viewer_results = getattr(
            viewer,
            "results",
            {},
        )

        if isinstance(
            viewer_results,
            dict,
        ):
            transfer_keys = (
                "regen_viewer_manual_geometry_snapshot",
                "regen_manual_geometry",
                "manual_regen_geometry",

                "regen_current_geometry",
                "regen_ui_applied_geometry",
                "regen_viewer_accepted_geometry",

                "regen_candidate_ranked_population",
                "regen_candidate_evaluated_population",
                "regen_candidate_populations_by_strategy",

                "regen_design_mode",
                "regen_design_mode_label",
                "regen_design_mode_strategy",
                "regen_candidate_design_mode",

                "regen_geometry_source_active",
                "regen_viewer_actual_geometry_source",
            )

            for key in transfer_keys:

                if key not in viewer_results:
                    continue

                value = viewer_results.get(
                    key
                )

                if isinstance(
                    value,
                    dict,
                ):
                    value = dict(
                        value
                    )

                elif isinstance(
                    value,
                    list,
                ):
                    value = list(
                        value
                    )

                transfer[
                    key
                ] = value

        # Canonicalise the real Viewer Regen station profile for the Graph
        # Explorer axial mode. Do not fabricate one from unrelated nozzle data.
        canvas = getattr(
            viewer,
            "canvas",
            None,
        )

        canvas_results = getattr(
            canvas,
            "results",
            {},
        )

        profile = None
        profile_source_key = None

        # Prefer the already-canonical profile.  When the solver's real
        # solved Regen station data is exposed under the existing recommended
        # profile key, canonicalise it here for Graph Explorer rather than
        # requiring the graph consumer to understand multiple solver keys.
        for source_key in (
            "regen_axial_profile",
            "recommended_regen_axial_profile",
        ):
            for mapping in (
                viewer_results,
                canvas_results,
            ):
                if not isinstance(
                    mapping,
                    dict,
                ):
                    continue

                candidate = mapping.get(
                    source_key
                )

                if (
                    isinstance(
                        candidate,
                        list,
                    )
                    and
                    candidate
                ):
                    profile = list(
                        candidate
                    )

                    profile_source_key = (
                        source_key
                    )

                    break

            if profile is not None:
                break

        if (
            profile is None
            and
            canvas is not None
        ):
            available_callback = getattr(
                canvas,
                "available_station_profiles",
                None,
            )

            if callable(
                available_callback
            ):
                try:
                    available = (
                        available_callback()
                        or
                        {}
                    )

                except Exception:
                    available = {}

                if isinstance(
                    available,
                    dict,
                ):
                    for profile_key in available:

                        if (
                            "regen"
                            not in
                            str(
                                profile_key
                            ).lower()
                        ):
                            continue

                        candidate = None

                        for mapping in (
                            viewer_results,
                            canvas_results,
                        ):
                            if not isinstance(
                                mapping,
                                dict,
                            ):
                                continue

                            value = mapping.get(
                                profile_key
                            )

                            if (
                                isinstance(
                                    value,
                                    list,
                                )
                                and
                                value
                            ):
                                candidate = value
                                break

                        if candidate is None:
                            continue

                        profile = list(
                            candidate
                        )

                        profile_source_key = str(
                            profile_key
                        )

                        break

        if (
            profile is None
            and
            canvas is not None
        ):
            active_key = str(
                getattr(
                    canvas,
                    "station_profile_key",
                    "",
                )
                or
                ""
            )

            active_callback = getattr(
                canvas,
                "active_station_profile",
                None,
            )

            if (
                "regen"
                in
                active_key.lower()
                and
                callable(
                    active_callback
                )
            ):
                try:
                    candidate = (
                        active_callback()
                    )

                except Exception:
                    candidate = None

                if (
                    isinstance(
                        candidate,
                        list,
                    )
                    and
                    candidate
                ):
                    profile = list(
                        candidate
                    )

                    profile_source_key = (
                        active_key
                    )

        if profile:
            transfer[
                "regen_axial_profile"
            ] = profile

            transfer[
                "regen_axial_profile_source_key"
            ] = (
                profile_source_key
            )

        self._regen_graph_transfer_state = (
            transfer
        )

    @staticmethod
    def _module_control_text(
        values,
        names=None,
    ):
        names = names or {}

        rendered = [
            str(
                names.get(
                    value,
                    value,
                )
            )
            for value in (
                values
                or []
            )
        ]

        return (
            ", ".join(
                rendered
            )
            if rendered
            else "None"
        )


    @staticmethod
    def _module_control_action(
        row,
    ):
        status = row.get(
            "activation_status"
        )

        if status == ACTIVE:
            return (
                "Deactivate",
                False,
                True,
            )

        if (
            status
            == USER_DEACTIVATED
            and
            row.get(
                "can_user_activate"
            )
        ):
            return (
                "Activate",
                True,
                True,
            )

        return (
            "Unavailable",
            None,
            False,
        )


    def _apply_module_control_change(
        self,
        *,
        table,
        module_id,
        module_name,
        enabled,
        cascade_names,
    ):
        if (
            not enabled
            and cascade_names
        ):
            cascade_text = "\n".join(
                f"• {name}"
                for name
                in cascade_names
            )

            answer = QMessageBox.question(
                self.parent,
                "Confirm Module Deactivation",
                (
                    f"Deactivating {module_name} "
                    "will also make these dependent "
                    "modules unavailable:"
                    f"\n\n{cascade_text}"
                    "\n\nContinue?"
                ),
                (
                    QMessageBox.StandardButton.Yes
                    |
                    QMessageBox.StandardButton.No
                ),
                QMessageBox.StandardButton.No,
            )

            if (
                answer
                !=
                QMessageBox.StandardButton.Yes
            ):
                return False

        result = (
            self.module_runtime_integrator
            .set_module_enabled(
                module_id,
                enabled,
            )
        )

        if (
            result.get(
                "status"
            )
            != "PASS"
        ):
            QMessageBox.warning(
                self.parent,
                "Module State Change Failed",
                str(
                    result.get(
                        "reason",
                        "The module state could not "
                        "be changed.",
                    )
                ),
            )

            return False

        self._populate_module_control_table(
            table
        )

        if (
            self.parent is not None
            and
            hasattr(
                self.parent,
                "statusBar",
            )
        ):
            status_bar = (
                self.parent.statusBar()
            )

            if status_bar is not None:
                status_bar.showMessage(
                    "Module state updated: "
                    f"{module_name}"
                )

        return True


    def _populate_module_control_table(
        self,
        table,
    ):
        rows = list(
            self.module_runtime_integrator
            .availability_surface()
            .get(
                "status_table",
                [],
            )
        )

        names = {
            row.get(
                "module_id"
            ):
                (
                    row.get(
                        "module_name"
                    )
                    or
                    row.get(
                        "module_id"
                    )
                )
            for row in rows
        }

        table.setRowCount(
            len(rows)
        )

        for row_index, row in enumerate(
            rows
        ):
            module_id = str(
                row.get(
                    "module_id",
                    "",
                )
            )

            module_name = str(
                row.get(
                    "module_name",
                    module_id,
                )
            )

            cascade_names = tuple(
                names.get(
                    module,
                    module,
                )
                for module
                in (
                    row.get(
                        "cascade_consequences",
                        [],
                    )
                    or []
                )
            )

            values = (
                module_name,
                str(
                    row.get(
                        "activation_status",
                        "",
                    )
                ),
                (
                    "On"
                    if row.get(
                        "enabled"
                    )
                    else "Off"
                ),
                str(
                    row.get(
                        "runtime_status",
                        "",
                    )
                ),
                self._module_control_text(
                    row.get(
                        "requires_modules"
                    ),
                    names,
                ),
                self._module_control_text(
                    row.get(
                        "required_by_modules"
                    ),
                    names,
                ),
                self._module_control_text(
                    cascade_names
                ),
                str(
                    row.get(
                        "activation_reason",
                        "",
                    )
                    or ""
                ),
            )

            for column, value in enumerate(
                values
            ):
                item = QTableWidgetItem(
                    value
                )

                item.setToolTip(
                    value
                )

                table.setItem(
                    row_index,
                    column,
                    item,
                )

            (
                label,
                desired_enabled,
                action_enabled,
            ) = (
                self._module_control_action(
                    row
                )
            )

            button = QPushButton(
                label
            )

            button.setEnabled(
                action_enabled
            )

            if desired_enabled is not None:
                button.clicked.connect(
                    lambda checked=False,
                    *,
                    selected_table=table,
                    selected_module_id=module_id,
                    selected_module_name=module_name,
                    selected_enabled=desired_enabled,
                    selected_cascade=cascade_names:
                        self._apply_module_control_change(
                            table=selected_table,
                            module_id=selected_module_id,
                            module_name=selected_module_name,
                            enabled=selected_enabled,
                            cascade_names=selected_cascade,
                        )
                )

            table.setCellWidget(
                row_index,
                8,
                button,
            )

        table.resizeColumnsToContents()


    def show_module_control(
        self,
    ):
        """
        Render canonical ModuleRuntimeIntegrator state.

        This method owns dialog composition only.
        """
        if (
            self.module_runtime_integrator
            is None
        ):
            QMessageBox.warning(
                self.parent,
                "Module Control Unavailable",
                "The canonical Module Runtime Integrator "
                "is not available.",
            )

            return None

        dialog = QDialog(
            self.parent
        )

        dialog.setWindowTitle(
            "LEAF Module Control"
        )

        dialog.resize(
            1250,
            560,
        )

        layout = QVBoxLayout(
            dialog
        )

        description = QLabel(
            "Module state is supplied directly by the "
            "LEAF Module Runtime Integrator. "
            "Dependency-deactivated modules cannot be "
            "manually activated until their required "
            "modules become available."
        )

        description.setWordWrap(
            True
        )

        layout.addWidget(
            description
        )

        table = QTableWidget()

        table.setColumnCount(
            9
        )

        table.setHorizontalHeaderLabels(
            [
                "Module",
                "Status",
                "Enabled",
                "Runtime",
                "Requires",
                "Required By",
                "Cascade if Disabled",
                "Reason",
                "Action",
            ]
        )

        layout.addWidget(
            table
        )

        self._populate_module_control_table(
            table
        )

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            dialog.close
        )

        layout.addWidget(
            close_button
        )

        dialog.exec()

        return dialog




    def show_main_outputs_window(self):
        results = self.require_main_outputs()

        if results is None:
            return

        dialog = QDialog(self.parent)
        dialog.setWindowTitle("LEAF Main Outputs")
        dialog.resize(900, 700)

        layout = QVBoxLayout(dialog)

        output_panel = OutputPanel(
            self.get_sections(),
            self.get_symbols(),
            self.get_units(),
        )

        output_panel.update_outputs(results)

        layout.addWidget(output_panel)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec()

    def show_foundation_status_tab(self):
        if self.foundation_status_panel is None:
            QMessageBox.warning(
                self.parent,
                "Foundation Status Unavailable",
                "The Foundation Status panel could not be loaded.",
            )
            return

        self.right_tabs.setCurrentWidget(self.foundation_status_panel)

    def show_warnings_tab(self):
        if self.right_tabs is None:
            QMessageBox.warning(
                self.parent,
                "Warnings Unavailable",
                "The warnings panel is not available.",
            )
            return

        for index in range(self.right_tabs.count()):
            if self.right_tabs.tabText(index) == "Warnings":
                self.right_tabs.setCurrentIndex(index)
                return

        QMessageBox.warning(
            self.parent,
            "Warnings Unavailable",
            "The warnings tab could not be found.",
        )

    def show_raw_cea_output(self):
        self.input_tabs.setCurrentWidget(self.cea_panel)