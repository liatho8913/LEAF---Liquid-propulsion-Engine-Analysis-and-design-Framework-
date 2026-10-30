

class MenuController:
    def __init__(
            self,
            main_window,
            report_export_controller,
            window_launch_controller,
            project_state_controller,
            calculation_controller,
            recommended_design_controller,
            input_assembly_controller,
            output_panel,
            get_last_results_callback,
    ):
        self.main_window = main_window
        self.report_export_controller = report_export_controller
        self.window_launch_controller = window_launch_controller
        self.project_state_controller = project_state_controller
        self.calculation_controller = calculation_controller
        self.recommended_design_controller = recommended_design_controller
        self.input_assembly_controller = input_assembly_controller
        self.output_panel = output_panel
        self.get_last_results = get_last_results_callback

    def create_menu_bar(self):
        menu_bar = self.main_window.menuBar()

        self._create_file_menu(menu_bar)
        self._create_calculate_menu(menu_bar)
        self._create_view_menu(menu_bar)
        self._create_tools_menu(menu_bar)

    def _create_file_menu(self, menu_bar):
        file_menu = menu_bar.addMenu("File")

        new_action = file_menu.addAction("New Project")
        new_action.triggered.connect(
            lambda: self.project_state_controller.new_project()
        )

        open_action = file_menu.addAction("Open Project")
        open_action.triggered.connect(
            lambda: self.project_state_controller.open_project()
        )

        save_action = file_menu.addAction("Save Project")
        save_action.triggered.connect(
            lambda: self.project_state_controller.save_project()
        )

        save_as_action = file_menu.addAction("Save Project As")
        save_as_action.triggered.connect(
            lambda: self.project_state_controller.save_project_as()
        )

        file_menu.addSeparator()

        rename_project_action = file_menu.addAction(
            "Rename Project..."
        )
        rename_project_action.triggered.connect(
            lambda: self.project_state_controller.prompt_rename_current_project()
        )

        rename_design_action = file_menu.addAction(
            "Rename Design..."
        )
        rename_design_action.triggered.connect(
            lambda: self.project_state_controller.prompt_rename_current_design()
        )

        file_menu.addSeparator()


        security_menu = file_menu.addMenu("Security")

        lock_leaf_action = security_menu.addAction(
            "Lock LEAF"
        )

        lock_leaf_action.triggered.connect(
            lambda:
                self.main_window
                ._request_manual_runtime_lock()
        )

        security_menu.addSeparator()

        export_principal_recovery_action = security_menu.addAction(
            "Export Principal Recovery..."
        )
        export_principal_recovery_action.triggered.connect(
            lambda: self.project_state_controller.prompt_export_principal_recovery()
        )

        trust_device_action = security_menu.addAction(
            "Trust This Device..."
        )
        trust_device_action.triggered.connect(
            lambda: self.project_state_controller.prompt_trust_this_device()
        )

        claim_legacy_project_action = security_menu.addAction(
            "Claim Current Legacy Project..."
        )
        claim_legacy_project_action.triggered.connect(
            lambda: self.project_state_controller.prompt_claim_current_legacy_project()
        )

        encrypt_project_action = security_menu.addAction(
            "Encrypt Current Project..."
        )

        encrypt_project_action.triggered.connect(
            lambda:
                self.project_state_controller
                .prompt_encrypt_current_project()
        )

        recover_project_action = security_menu.addAction(
            "Recover Encrypted Project Access..."
        )

        recover_project_action.triggered.connect(
            lambda:
                self.project_state_controller
                .prompt_recover_encrypted_project_access()
        )

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("Export")

        export_json_action = export_menu.addAction("Export Outputs JSON")
        export_json_action.triggered.connect(
            lambda: self.report_export_controller.export_outputs_json()
        )

        export_csv_action = export_menu.addAction("Export Outputs CSV")
        export_csv_action.triggered.connect(
            lambda: self.report_export_controller.export_outputs_csv()
        )

        export_report_action = export_menu.addAction("Export Main Output Report TXT")
        export_report_action.triggered.connect(
            lambda: self.report_export_controller.export_main_output_report_txt()
        )

        export_validation_action = export_menu.addAction("Export Validation Report TXT")
        export_validation_action.triggered.connect(
            lambda: self.report_export_controller.export_validation_report_txt()
        )

        export_diagnostics_action = export_menu.addAction("Export Diagnostics Report TXT")
        export_diagnostics_action.triggered.connect(
            lambda: self.report_export_controller.export_diagnostics_report_txt()
        )

        export_recommendation_action = export_menu.addAction(
            "Export Recommended Design Report TXT"
        )
        export_recommendation_action.triggered.connect(
            lambda: self.report_export_controller.export_recommendation_report_txt()
        )

        export_development_evidence_action = export_menu.addAction(
            "Export Development Evidence Report TXT"
        )
        export_development_evidence_action.triggered.connect(
            lambda: self.report_export_controller.export_development_evidence_report_txt()
        )

        export_development_evidence_html_action = export_menu.addAction(
            "Export Development Evidence Report HTML"
        )
        export_development_evidence_html_action.triggered.connect(
            lambda: self.report_export_controller.export_development_evidence_report_html()
        )

        export_report_bundle_html_action = export_menu.addAction(
            "Export Report Bundle HTML"
        )
        export_report_bundle_html_action.triggered.connect(
            lambda: self.report_export_controller.export_report_bundle_html()
        )

        export_output_ownership_audit_action = export_menu.addAction(
            "Export Output Ownership Audit TXT"
        )
        export_output_ownership_audit_action.triggered.connect(
            lambda: self.report_export_controller.export_output_ownership_audit_txt()
        )

        export_foundation_attachment_audit_action = export_menu.addAction(
            "Export Foundation Attachment Audit TXT"
        )
        export_foundation_attachment_audit_action.triggered.connect(
            lambda: self.report_export_controller.export_foundation_attachment_audit_txt()
        )

        export_result_key_audit_action = export_menu.addAction(
            "Export Foundation Result Key Audit TXT"
        )
        export_result_key_audit_action.triggered.connect(
            lambda: self.report_export_controller.export_result_key_audit_txt()
        )

        export_benchmark_report_action = export_menu.addAction(
            "Export Benchmark Comparison Report TXT"
        )
        export_benchmark_report_action.triggered.connect(
            lambda: self.report_export_controller.export_benchmark_report_txt()
        )

        export_engine_reproduction_report_action = export_menu.addAction(
            "Export Engine Reproduction Report TXT"
        )
        export_engine_reproduction_report_action.triggered.connect(
            lambda: self.report_export_controller.export_engine_reproduction_report_txt()
        )

        export_axial_action = export_menu.addAction("Export Axial / Report-Only TXT")
        export_axial_action.triggered.connect(
            lambda: self.report_export_controller.export_axial_report_txt()
        )

        export_bundle_action = export_menu.addAction("Export Foundation Bundle TXT")
        export_bundle_action.triggered.connect(
            lambda: self.report_export_controller.export_foundation_bundle_report_txt()
        )

        export_station_table_csv_action = export_menu.addAction(
            "Export Station Table CSV"
        )
        export_station_table_csv_action.triggered.connect(
            lambda: self.report_export_controller.export_station_table_csv()
        )

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.main_window.close)

    def _create_calculate_menu(self, menu_bar):
        calculate_menu = menu_bar.addMenu("Calculate")

        calculate_action = calculate_menu.addAction("Calculate")
        calculate_action.triggered.connect(
            lambda: self.main_window.calculate()
        )

        calculate_menu.addSeparator()

        apply_recommended_regen_calculate_action = calculate_menu.addAction(
            "Apply Recommended Regen Geometry"
        )
        apply_recommended_regen_calculate_action.triggered.connect(
            lambda: self.recommended_design_controller.apply_recommended_regen_geometry_to_inputs()
        )

        calculate_menu.addSeparator()

        clear_inputs_action = calculate_menu.addAction("Clear Inputs")
        clear_inputs_action.triggered.connect(
            lambda: self.project_state_controller.clear_inputs()
        )

        reset_defaults_action = calculate_menu.addAction("Reset Defaults")
        reset_defaults_action.triggered.connect(
            lambda: self.project_state_controller.reset_defaults()
        )

        calculate_menu.addSeparator()

        missing_report_action = calculate_menu.addAction("Missing Parameter Report")
        missing_report_action.triggered.connect(
            lambda: self.input_assembly_controller.show_missing_parameter_report(
                self.main_window
            )
        )

    def _create_view_menu(self, menu_bar):
        view_menu = menu_bar.addMenu("View")

        full_outputs_action = view_menu.addAction("Main Outputs")

        full_outputs_action.triggered.connect(
            lambda: self.window_launch_controller.show_main_outputs_window()
        )

        report_viewer_action = view_menu.addAction("Report Viewer")

        report_viewer_action.triggered.connect(
            lambda: self.window_launch_controller.show_report_viewer()
        )

        engineering_reference_action = view_menu.addAction("Engineering Reference")
        engineering_reference_action.triggered.connect(
            lambda: self.window_launch_controller.show_engineering_reference()
        )

        foundation_test_runner_view_action = view_menu.addAction(
            "Foundation Test Runner"
        )

        foundation_test_runner_view_action.triggered.connect(
            lambda: self.window_launch_controller.show_foundation_test_runner()
        )

        foundation_status_action = view_menu.addAction("Foundation Status")

        foundation_status_action.triggered.connect(
            lambda: self.window_launch_controller.show_foundation_status_tab()
        )

        warnings_action = view_menu.addAction("Warnings")

        warnings_action.triggered.connect(
            lambda: self.window_launch_controller.show_warnings_tab()
        )

        raw_cea_action = view_menu.addAction("Raw NASA CEA Output")

        raw_cea_action.triggered.connect(
            lambda: self.window_launch_controller.show_raw_cea_output()
        )

    def _create_tools_menu(self, menu_bar):
        tools_menu = menu_bar.addMenu("Tools")

        module_control_action = tools_menu.addAction("Module Control")
        module_control_action.triggered.connect(
            lambda: self.window_launch_controller.show_module_control()
        )

        tools_menu.addSeparator()

        report_viewer_tool_action = tools_menu.addAction("Report Viewer")
        report_viewer_tool_action.triggered.connect(
            lambda: self.window_launch_controller.show_report_viewer()
        )

        foundation_test_runner_action = tools_menu.addAction(
            "Foundation Test Runner"
        )
        foundation_test_runner_action.triggered.connect(
            lambda: self.window_launch_controller.show_foundation_test_runner()
        )

        startup_health_action = tools_menu.addAction("Startup Health Check")
        startup_health_action.triggered.connect(
            lambda: self.window_launch_controller.show_startup_health_window()
        )

        graph_explorer_action = tools_menu.addAction("Graph Explorer")
        graph_explorer_action.triggered.connect(
            lambda: self.window_launch_controller.show_graph_explorer()
        )

        station_table_action = tools_menu.addAction("Station Table")
        station_table_action.triggered.connect(
            lambda: self.window_launch_controller.show_station_table()
        )

        regen_cross_section_action = tools_menu.addAction(
            "Regen Cross-Section Viewer"
        )
        regen_cross_section_action.triggered.connect(
            lambda: self.window_launch_controller.show_regen_cross_section_viewer()
        )

        apply_recommended_regen_action = tools_menu.addAction(
            "Apply Recommended Regen Geometry"
        )
        apply_recommended_regen_action.triggered.connect(
            lambda: self.recommended_design_controller.apply_recommended_regen_geometry_to_inputs()
        )

        tools_menu.addSeparator()

        missing_report_tool_action = tools_menu.addAction("Missing Parameter Report")
        missing_report_tool_action.triggered.connect(
            lambda: self.input_assembly_controller.show_missing_parameter_report(
                self.main_window
            )
        )

        clear_output_action = tools_menu.addAction("Clear Output")
        clear_output_action.triggered.connect(self.clear_outputs)

    def clear_outputs(self):
        self.output_panel.clear_outputs()
        self.main_window.statusBar().showMessage("Outputs cleared")