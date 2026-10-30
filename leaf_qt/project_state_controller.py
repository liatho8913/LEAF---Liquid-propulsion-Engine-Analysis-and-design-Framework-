from pathlib import Path
from leaf_qt.storage.design_manifest import DESIGN_MANIFEST_FILENAME
from PySide6.QtWidgets import QInputDialog

from PySide6.QtWidgets import QFileDialog, QMessageBox



class ProjectStateController:
    PROJECT_SCHEMA_VERSION = "LEAF_PROJECT_STATE_V2"

    DEFAULT_GEOMETRY_INPUTS = {
        "nozzle_geometry_model": "RAO_BELL_APPROXIMATION",
        "conical_half_angle_deg": 15.0,
        "rao_length_fraction": 0.8,
    }

    DEFAULT_MATERIAL_INPUTS = {
        "selected_material": "GRCop-42",
        "hot_gas_liner": "GRCop-42",
        "outer_jacket": "Inconel 718",
        "rib_channel": "GRCop-42",
        "selected_coating_material": "None",
        "selected_bond_coat": "None",
    }

    DEFAULT_MANUAL_INPUTS = {
        "chamber_pressure": 6895000.0,
        "mass_flow_rate": 1.15,
        "characteristic_length": 1.27,
        "selected_length": 0.04,
        "minimum_wall_thickness": 0.001,
        "corrosion_allowance": 0.0002,
        "coolant_side_wall_temperature": 600.0,
        "coolant_channel_height": 0.002,
        "coolant_channel_width": 0.0015,
        "rib_width": 0.001,
        "outer_jacket_thickness": 0.002,
        "coating_thickness": 0.0,
        "number_of_coolant_channels": 80.0,
        "selected_station_length": 0.001,
        "coolant_flow_fraction": 1.0,
    }

    def __init__(
            self,
            parent,
            manual_input_panel,
            cea_panel,
            geometry_panel,
            materials_panel,
            output_panel,
            warning_panel,
            foundation_status_panel,
            label_to_var,
            get_last_results_callback,
            set_last_results_callback,
            get_benchmark_case_callback,
            set_benchmark_case_callback,
            get_startup_health_callback,
            set_status_callback,
            get_design_history_callback=None,
            set_design_history_callback=None,
            save_load_bridge=None,
            project_design_creation_owner=None,
            project_browser_model=None,
    ):
        self.parent = parent
        self.manual_input_panel = manual_input_panel
        self.cea_panel = cea_panel
        self.geometry_panel = geometry_panel
        self.materials_panel = materials_panel
        self.output_panel = output_panel
        self.warning_panel = warning_panel
        self.foundation_status_panel = foundation_status_panel
        self.label_to_var = label_to_var

        self.get_last_results = get_last_results_callback
        self.set_last_results = set_last_results_callback
        self.get_design_history = get_design_history_callback
        self.set_design_history = set_design_history_callback
        self.get_benchmark_case = get_benchmark_case_callback
        self.set_benchmark_case = set_benchmark_case_callback
        self.get_startup_health = get_startup_health_callback
        self.set_status = set_status_callback
        self.save_load_bridge = save_load_bridge
        self.project_design_creation_owner = project_design_creation_owner
        self.project_browser_model = project_browser_model

        self.security_context = getattr(
            save_load_bridge,
            "security_context",
            None,
        )

        creation_security_context = getattr(
            project_design_creation_owner,
            "security_context",
            None,
        )

        if (
            self.security_context is not None
            and
            creation_security_context is not None
            and
            self.security_context.principal_id
            !=
            creation_security_context.principal_id
        ):
            raise RuntimeError(
                "security_context_principal_mismatch"
            )

        self.current_project_manifest_path = None
        self.current_design_manifest_path = None

    def get_project_state(self):
        return {
            "schema_version": self.PROJECT_SCHEMA_VERSION,
            "calculator_inputs": self.manual_input_panel.get_inputs(),
            "cea_inputs": self.cea_panel.get_cea_inputs(),
            "cea_raw_output": self._get_cea_raw_output(),
            "geometry_inputs": self.geometry_panel.get_inputs(),
            "regen_materials": self.materials_panel.get_selected_materials(),
            "benchmark_case": self.get_benchmark_case(),
            "startup_health_snapshot": self.get_startup_health() or {},
            "startup_health_snapshot_note": (
                "This is a saved evidence snapshot only. "
                "Loading this project must not overwrite the live startup-health controller state."
            ),
            "design_history": (
                self.get_design_history()
                if callable(self.get_design_history)
                else []
            ),
            "last_results": self.get_last_results() or {},
        }

    def load_project_state(self, state):
        if not isinstance(state, dict):
            QMessageBox.warning(
                self.parent,
                "Invalid Project",
                "Project file is not a valid JSON object.",
            )
            return

        normalised = self._normalise_project_state(state)

        self.manual_input_panel.set_inputs(normalised["calculator_inputs"])
        self.cea_panel.set_inputs(normalised["cea_inputs"])
        self.cea_panel.set_raw_output(normalised.get("cea_raw_output", ""))

        if hasattr(self.geometry_panel, "set_inputs"):
            self.geometry_panel.set_inputs(normalised["geometry_inputs"])

        if hasattr(self.materials_panel, "set_inputs"):
            self.materials_panel.set_inputs(normalised["regen_materials"])

        if normalised.get("benchmark_case"):
            self.set_benchmark_case(normalised["benchmark_case"])

        restored_results = normalised["last_results"]

        if isinstance(restored_results, dict):
            restored_results["loaded_project_startup_health_snapshot"] = normalised.get(
                "startup_health_snapshot",
                {},
            )
            restored_results["loaded_project_startup_health_snapshot_preserved"] = True
            restored_results["live_startup_health_used_after_load"] = self.get_startup_health() or {}

        self.set_last_results(restored_results)

        if callable(self.set_design_history):
            self.set_design_history(normalised.get("design_history", []))

        self._refresh_outputs_after_state_change(restored_results)

        QMessageBox.information(
            self.parent,
            "Project Loaded",
            "Project loaded successfully.",
        )

        self.set_status("Project loaded")

    def open_project(self):
        if self.project_browser_model is None:
            QMessageBox.critical(
                self.parent,
                "Open Failed",
                "Canonical project browser is not available.",
            )
            return

        design_paths = (
            self.project_browser_model
            .design_manifest_paths()
        )

        if design_paths:
            start_directory = str(
                design_paths[0].parent
            )
        else:
            start_directory = str(
                self.project_browser_model
                .storage
                .canonical_path("designs")
            )

        path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Open LEAF Project / Design",
            start_directory,
            f"LEAF Design Manifest ({DESIGN_MANIFEST_FILENAME});;"
            "Legacy LEAF State (*.leaf.json *.json);;"
            "All Files (*)",
        )

        if not path:
            return

        selected_path = Path(
            path
        )

        # ------------------------------------------------------------------
        # Canonical design manifest.
        # ------------------------------------------------------------------

        if selected_path.name == DESIGN_MANIFEST_FILENAME:

            try:
                project_manifest_path = (
                    self.project_browser_model
                    .resolve_project_manifest_for_design(
                        selected_path
                    )
                )

                if project_manifest_path is None:
                    raise FileNotFoundError(
                        "owning_project_manifest_not_found"
                    )

                self.save_load_bridge.load_design(
                    project_manifest_path=
                        project_manifest_path,

                    design_manifest_path=
                        selected_path,

                    source=
                        "project_state_controller",
                )

                state = (
                    self.save_load_bridge
                    .load_design_engineering_state(
                        selected_path
                    )
                )

            except Exception as exc:
                QMessageBox.critical(
                    self.parent,
                    "Open Failed",
                    "Could not open canonical LEAF design:"
                    f"\n\n{exc}",
                )
                return

            self.current_project_manifest_path = str(
                project_manifest_path
            )

            self.current_design_manifest_path = str(
                selected_path
            )

            self.load_project_state(
                state
            )

            self.set_status(
                "Canonical LEAF design loaded"
            )

            return

        # ------------------------------------------------------------------
        # Legacy standalone state.
        #
        # Import is supported, but it does not become an active canonical
        # design. A subsequent Save therefore routes through Save As.
        # ------------------------------------------------------------------

        try:
            state = (
                self.save_load_bridge
                .load_engineering_state(
                    selected_path
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Open Failed",
                "Could not import legacy LEAF state:"
                f"\n\n{exc}",
            )
            return

        self.current_project_manifest_path = None
        self.current_design_manifest_path = None

        self.load_project_state(
            state
        )

        self.set_status(
            "Legacy LEAF state imported — "
            "use Save As to create a canonical project/design"
        )

    def save_project_as(self):
        if self.project_design_creation_owner is None:
            QMessageBox.critical(
                self.parent,
                "Save As Failed",
                "Canonical project/design creation owner is not available.",
            )
            return

        project_name, accepted = QInputDialog.getText(
            self.parent,
            "Save LEAF Project As",
            "Project name:",
        )

        if not accepted:
            return

        project_name = str(
            project_name
        ).strip()

        if not project_name:
            QMessageBox.warning(
                self.parent,
                "Save As",
                "Project name cannot be empty.",
            )
            return

        design_name, accepted = QInputDialog.getText(
            self.parent,
            "Save LEAF Project As",
            "Design name:",
        )

        if not accepted:
            return

        design_name = str(
            design_name
        ).strip()

        if not design_name:
            QMessageBox.warning(
                self.parent,
                "Save As",
                "Design name cannot be empty.",
            )
            return

        state = self.get_project_state()

        try:
            created = (
                self.project_design_creation_owner
                .create_project_with_design(
                    project_name=
                        project_name,

                    design_name=
                        design_name,

                    runtime_schema_version=
                        str(
                            state.get(
                                "schema_version",
                                "",
                            )
                        ),
                )
            )

            self.save_load_bridge.save_design(
                project_manifest_path=
                    created.project_manifest_path,

                design_manifest_path=
                    created.design_manifest_path,

                engineering_state=
                    state,

                source=
                    "project_state_controller",
            )

        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Save As Failed",
                "Could not create canonical LEAF project/design:"
                f"\n\n{exc}",
            )
            return

        self.current_project_manifest_path = str(
            created.project_manifest_path
        )

        self.current_design_manifest_path = str(
            created.design_manifest_path
        )

        QMessageBox.information(
            self.parent,
            "Saved",
            "Canonical LEAF project/design saved successfully.",
        )

        self.set_status(
            "Canonical LEAF project/design saved"
        )

    def save_project(self):
        if (
            not self.current_project_manifest_path
            or not self.current_design_manifest_path
        ):
            self.save_project_as()
            return

        state = self.get_project_state()

        try:
            self.save_load_bridge.save_design(
                project_manifest_path=
                    self.current_project_manifest_path,

                design_manifest_path=
                    self.current_design_manifest_path,

                engineering_state=
                    state,

                source=
                    "project_state_controller",
            )

        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Save Failed",
                "Could not save canonical LEAF design:"
                f"\n\n{exc}",
            )
            return

        QMessageBox.information(
            self.parent,
            "Saved",
            "Project/design saved successfully.",
        )

        self.set_status(
            "Canonical LEAF design saved"
        )

    def _require_storage_security_owner(
        self,
    ):

        owner = getattr(
            self,
            "_storage_validation_repair_owner",
            None,
        )


        if owner is not None:

            return owner


        storage = getattr(
            self.project_browser_model,
            "storage",
            None,
        )


        if storage is None:

            storage = getattr(
                self.project_design_creation_owner,
                "storage",
                None,
            )


        if storage is None:

            raise RuntimeError(
                "canonical_storage_owner_not_available_for_security"
            )


        from leaf_qt.storage.storage_validation_repair import (
            StorageValidationRepairOwner,
        )


        owner = (
            StorageValidationRepairOwner(
                storage.root
            )
        )


        self._storage_validation_repair_owner = (
            owner
        )


        return owner


    def prompt_trust_this_device(self):
        confirmed = QMessageBox.question(
            self.parent,
            "Trust This Device",
            "Trust this device for installation of recovered LEAF project keys?\n\n"
            "Trust is stored only in the approved native OS secret store.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmed != QMessageBox.Yes:
            return False
        try:
            changed = self.security_context.enroll_trusted_device()
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Device Trust Failed",
                f"LEAF could not trust this device:\n\n{exc}",
            )
            return None
        QMessageBox.information(
            self.parent,
            "Device Trusted" if changed else "Device Already Trusted",
            "This device may receive recovered LEAF project keys."
            if changed else
            "This device was already trusted for LEAF project recovery.",
        )
        self.set_status(
            "This device is trusted for LEAF project recovery"
        )
        return changed


    def prompt_export_principal_recovery(self):
        destination, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export LEAF Principal Recovery",
            str(Path.home() / "leaf-principal-recovery.leaf-principal-recovery.json"),
            "LEAF Principal Recovery (*.leaf-principal-recovery.json);;All Files (*)",
        )
        if not destination:
            return None
        try:
            path, recovery_code = self.security_context.export_recovery_record(destination)
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Principal Recovery Export Failed",
                f"LEAF could not export principal recovery material:\n\n{exc}",
            )
            return None
        message = QMessageBox(self.parent)
        message.setIcon(QMessageBox.Information)
        message.setWindowTitle("Principal Recovery Created")
        message.setText(
            "Store the recovery record and recovery code separately. "
            "Both are required to restore this LEAF principal."
        )
        message.setDetailedText(f"Recovery record:\n{path}\n\nRecovery code:\n{recovery_code}")
        message.exec()
        self.set_status("LEAF principal recovery material exported")
        return path, recovery_code


    def prompt_claim_current_legacy_project(self):
        path = self.current_project_manifest_path
        if not path:
            QMessageBox.warning(
                self.parent,
                "Claim Legacy Project",
                "Open a canonical legacy LEAF project before claiming ownership.",
            )
            return None

        try:
            result = self._require_storage_security_owner().claim_legacy_project(
                path,
                self.security_context,
            )
        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Legacy Project Claim Failed",
                f"LEAF could not claim the current legacy project:\n\n{exc}",
            )
            return None

        self.set_status(
            "Legacy LEAF project ownership claimed"
        )
        QMessageBox.information(
            self.parent,
            "Legacy Project Claimed",
            "The current legacy project is now bound to the current local LEAF principal.",
        )
        return result


    def prepare_current_project_encryption(
        self,
        recovery_export_path,
    ):

        if not self.current_project_manifest_path:

            raise RuntimeError(
                "no_current_canonical_project_to_encrypt"
            )


        return (
            self
            ._require_storage_security_owner()
            .prepare_legacy_encryption_activation(
                self.current_project_manifest_path,

                recovery_export_path,

                security_context=
                    self.security_context,
            )
        )


    def activate_current_project_encryption(
        self,
        recovery_export_path,
        confirmation_code,
        *,
        acknowledge_irrecoverable_loss=False,
    ):

        import json


        if not self.current_project_manifest_path:

            raise RuntimeError(
                "no_current_canonical_project_to_encrypt"
            )


        if not self.current_design_manifest_path:

            raise RuntimeError(
                "no_current_canonical_design_for_encryption_transition"
            )


        if self.save_load_bridge is None:

            raise RuntimeError(
                "save_load_runtime_bridge_not_available"
            )


        old_project_path = Path(
            self.current_project_manifest_path
        )


        old_design_path = Path(
            self.current_design_manifest_path
        )


        design_payload = json.loads(
            old_design_path.read_text(
                encoding="utf-8"
            )
        )


        design_id = str(
            design_payload.get(
                "design_id",
                "",
            )
        ).strip()


        if not design_id:

            raise ValueError(
                "current_design_id_missing_before_encryption"
            )


        result = (
            self
            ._require_storage_security_owner()
            .activate_legacy_project_encryption(
                old_project_path,

                recovery_export_path,

                confirmation_code,

                acknowledge_irrecoverable_loss=
                    acknowledge_irrecoverable_loss,

                security_context=
                    self.security_context,

                key_custody=
                    getattr(
                        self.save_load_bridge,
                        "key_custody",
                        None,
                    ),

                encrypted_container_owner=
                    getattr(
                        self.save_load_bridge,
                        "encrypted_container_owner",
                        None,
                    ),
            )
        )


        new_project_path = Path(
            result[
                "project_manifest_path"
            ]
        )


        new_design_path_value = (
            dict(
                result.get(
                    "design_manifest_paths",
                    {},
                )
            )
            .get(
                design_id
            )
        )


        self.current_project_manifest_path = (
            str(
                new_project_path
            )
        )


        if not new_design_path_value:

            self.current_design_manifest_path = (
                None
            )

            self.set_status(
                "LEAF project encrypted — reopen design"
            )

            return {
                **result,

                "current_design_id":
                    design_id,

                "runtime_sync":
                    {},

                "runtime_sync_error":
                    "migrated_current_design_path_not_returned",
            }


        new_design_path = Path(
            new_design_path_value
        )


        self.current_design_manifest_path = (
            str(
                new_design_path
            )
        )


        runtime_sync = {}
        runtime_sync_error = None


        try:

            runtime_sync[
                "project"
            ] = (
                self.save_load_bridge
                .synchronise_renamed_reference(
                    old_project_path,
                    new_project_path,
                    "project",

                    source=
                        "project_state_controller",
                )
            )


            runtime_sync[
                "design"
            ] = (
                self.save_load_bridge
                .synchronise_renamed_reference(
                    old_design_path,
                    new_design_path,
                    "design",

                    source=
                        "project_state_controller",
                )
            )


        except Exception as exc:

            runtime_sync_error = repr(
                exc
            )


        if runtime_sync_error is None:

            self.set_status(
                "Canonical LEAF project encrypted"
            )

        else:

            self.set_status(
                "LEAF project encrypted — "
                "runtime references require reopen"
            )


        return {
            **result,

            "current_design_id":
                design_id,

            "current_project_manifest_path":
                str(
                    new_project_path
                ),

            "current_design_manifest_path":
                str(
                    new_design_path
                ),

            "runtime_sync":
                runtime_sync,

            "runtime_sync_error":
                runtime_sync_error,
        }


    def prompt_encrypt_current_project(
        self,
    ):

        if not (
            self.current_project_manifest_path
            and
            self.current_design_manifest_path
        ):

            QMessageBox.warning(
                self.parent,
                "Encrypt Project",
                "Open or save a canonical LEAF project/design "
                "before enabling encryption.",
            )

            return None


        default_name = str(
            Path.home()
            /
            "LEAF_Project_Recovery.leaf-recovery.json"
        )


        recovery_path, _ = (
            QFileDialog.getSaveFileName(
                self.parent,
                "Save LEAF Recovery Material",
                default_name,
                "LEAF Recovery Material "
                "(*.leaf-recovery.json)",
            )
        )


        if not recovery_path:

            return None


        if not recovery_path.endswith(
            ".leaf-recovery.json"
        ):

            recovery_path += (
                ".leaf-recovery.json"
            )


        try:

            preparation = (
                self.prepare_current_project_encryption(
                    recovery_path
                )
            )


        except Exception as exc:

            QMessageBox.critical(
                self.parent,
                "Encryption Preparation Failed",
                "LEAF could not prepare project encryption:"
                f"\n\n{exc}",
            )

            return None


        confirmation_code = str(
            preparation[
                "confirmation_code"
            ]
        )


        entered_code, accepted = (
            QInputDialog.getText(
                self.parent,
                "Confirm Project Encryption",
                (
                    "LEAF has created external recovery "
                    "material.\n\n"
                    "Keep that file secure and separate from "
                    "the encrypted project. Losing all usable "
                    "recovery material and all valid "
                    "device-local key copies may make the "
                    "project unrecoverable.\n\n"
                    "Recovery file:\n"
                    f"{recovery_path}\n\n"
                    "Type this project-specific code exactly "
                    "to activate encryption:\n\n"
                    f"{confirmation_code}"
                ),
            )
        )


        if not accepted:

            QMessageBox.information(
                self.parent,
                "Encryption Not Activated",
                "The project was not modified. The unused "
                "recovery file remains at the selected "
                "location and may be deleted.",
            )

            return None


        try:

            result = (
                self.activate_current_project_encryption(
                    recovery_path,

                    str(
                        entered_code
                    ).strip(),

                    acknowledge_irrecoverable_loss=
                        True,
                )
            )


        except Exception as exc:

            QMessageBox.critical(
                self.parent,
                "Encryption Activation Failed",
                "LEAF did not complete project encryption:"
                f"\n\n{exc}",
            )

            return None


        QMessageBox.information(
            self.parent,
            "Project Encryption Enabled",
            (
                "The canonical LEAF project is now encrypted."
                "\n\nKeep the recovery material offline and "
                "separate from the encrypted project.\n\n"
                "Recovery file:\n"
                f"{recovery_path}"
            ),
        )


        return result


    def recover_project_access(
        self,
        project_manifest_path,
        recovery_export_path,
    ):

        return (
            self
            ._require_storage_security_owner()
            .recover_encrypted_project_access(
                project_manifest_path,
                recovery_export_path,

                security_context=
                    self.security_context,

                key_custody=
                    getattr(
                        self.save_load_bridge,
                        "key_custody",
                        None,
                    ),
            )
        )


    def prompt_recover_encrypted_project_access(
        self,
    ):

        if self.project_browser_model is None:

            QMessageBox.critical(
                self.parent,
                "Recovery Failed",
                "Canonical project browser is not available.",
            )

            return None


        projects_root = (
            self.project_browser_model
            .storage
            .canonical_path(
                "projects"
            )
        )


        project_path, _ = (
            QFileDialog.getOpenFileName(
                self.parent,
                "Select Encrypted LEAF Project",
                str(
                    projects_root
                ),
                (
                    "LEAF Project Manifest "
                    "(project.leaf_project.json);;"
                    "All Files (*)"
                ),
            )
        )


        if not project_path:

            return None


        recovery_path, _ = (
            QFileDialog.getOpenFileName(
                self.parent,
                "Select LEAF Recovery Material",
                str(
                    Path.home()
                ),
                (
                    "LEAF Recovery Material "
                    "(*.leaf-recovery.json);;"
                    "All Files (*)"
                ),
            )
        )


        if not recovery_path:

            return None


        try:

            result = (
                self.recover_project_access(
                    project_path,
                    recovery_path,
                )
            )


        except Exception as exc:

            QMessageBox.critical(
                self.parent,
                "Recovery Failed",
                "LEAF could not restore encrypted project "
                "access:"
                f"\n\n{exc}",
            )

            return None


        QMessageBox.information(
            self.parent,
            "Project Access Recovered",
            (
                "The project key has been restored to the "
                "approved device-local secure store.\n\n"
                "The project remains encrypted and can now "
                "be opened normally."
            ),
        )


        self.set_status(
            "Encrypted LEAF project access recovered"
        )


        return result

    def prompt_rename_current_project(
        self,
    ):
        """
        Request a new project name through the canonical
        Qt project/design lifecycle surface.
        """
        if not (
            self.current_project_manifest_path
        ):
            QMessageBox.warning(
                self.parent,
                "Rename Project",
                "Open or save a canonical LEAF project "
                "before renaming it.",
            )

            return None

        new_name, accepted = (
            QInputDialog.getText(
                self.parent,
                "Rename Project",
                "New project name:",
            )
        )

        if not accepted:
            return None

        new_name = str(
            new_name
        ).strip()

        if not new_name:
            QMessageBox.warning(
                self.parent,
                "Rename Project",
                "Project name cannot be empty.",
            )

            return None

        try:
            result = (
                self.rename_current_project(
                    new_name
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Rename Project Failed",
                "Could not rename the canonical "
                "LEAF project:"
                f"\n\n{exc}",
            )

            return None

        QMessageBox.information(
            self.parent,
            "Project Renamed",
            "Canonical LEAF project renamed "
            "successfully.",
        )

        return result

    def prompt_rename_current_design(
        self,
    ):
        """
        Request a new design name through the canonical
        Qt project/design lifecycle surface.
        """
        if not (
            self.current_design_manifest_path
        ):
            QMessageBox.warning(
                self.parent,
                "Rename Design",
                "Open or save a canonical LEAF design "
                "before renaming it.",
            )

            return None

        new_name, accepted = (
            QInputDialog.getText(
                self.parent,
                "Rename Design",
                "New design name:",
            )
        )

        if not accepted:
            return None

        new_name = str(
            new_name
        ).strip()

        if not new_name:
            QMessageBox.warning(
                self.parent,
                "Rename Design",
                "Design name cannot be empty.",
            )

            return None

        try:
            result = (
                self.rename_current_design(
                    new_name
                )
            )

        except Exception as exc:
            QMessageBox.critical(
                self.parent,
                "Rename Design Failed",
                "Could not rename the canonical "
                "LEAF design:"
                f"\n\n{exc}",
            )

            return None

        QMessageBox.information(
            self.parent,
            "Design Renamed",
            "Canonical LEAF design renamed "
            "successfully.",
        )

        return result

    def rename_current_project(
        self,
        new_name,
    ):
        """
        Rename the current canonical project as one
        persistence + runtime transaction.
        """
        if (
            self.project_design_creation_owner
            is None
        ):
            raise RuntimeError(
                "canonical_project_design_lifecycle_owner_not_available"
            )

        if self.save_load_bridge is None:
            raise RuntimeError(
                "save_load_runtime_bridge_not_available"
            )

        if not (
            self.current_project_manifest_path
        ):
            raise RuntimeError(
                "no_current_canonical_project_to_rename"
            )

        old_path = Path(
            self.current_project_manifest_path
        )

        runtime_sync_holder = {}

        def synchronise(
            persisted_path,
        ):
            runtime_sync_holder[
                "result"
            ] = (
                self.save_load_bridge
                .synchronise_renamed_reference(
                    old_path,
                    persisted_path,
                    "project",
                    source=
                        "project_state_controller",
                )
            )

        new_path = (
            self.project_design_creation_owner
            .rename_project(
                old_path,
                new_name,
                after_persist=
                    synchronise,
            )
        )

        # Same-name rename is a persistent no-op and
        # therefore does not execute after_persist.
        if (
            "result"
            not in runtime_sync_holder
        ):
            runtime_sync_holder[
                "result"
            ] = (
                self.save_load_bridge
                .synchronise_renamed_reference(
                    old_path,
                    new_path,
                    "project",
                    source=
                        "project_state_controller",
                )
            )

        self.current_project_manifest_path = (
            str(
                new_path
            )
        )

        self.set_status(
            "Canonical LEAF project renamed"
        )

        return {
            "entity_type":
                "project",

            "old_path":
                str(old_path),

            "new_path":
                str(new_path),

            "runtime_sync":
                runtime_sync_holder[
                    "result"
                ],
        }

    def rename_current_design(
        self,
        new_name,
    ):
        """
        Rename the current canonical design as one
        persistence + runtime transaction.
        """
        if (
            self.project_design_creation_owner
            is None
        ):
            raise RuntimeError(
                "canonical_project_design_lifecycle_owner_not_available"
            )

        if self.save_load_bridge is None:
            raise RuntimeError(
                "save_load_runtime_bridge_not_available"
            )

        if not (
            self.current_design_manifest_path
        ):
            raise RuntimeError(
                "no_current_canonical_design_to_rename"
            )

        old_path = Path(
            self.current_design_manifest_path
        )

        runtime_sync_holder = {}

        def synchronise(
            persisted_path,
        ):
            runtime_sync_holder[
                "result"
            ] = (
                self.save_load_bridge
                .synchronise_renamed_reference(
                    old_path,
                    persisted_path,
                    "design",
                    source=
                        "project_state_controller",
                )
            )

        new_path = (
            self.project_design_creation_owner
            .rename_design(
                old_path,
                new_name,
                after_persist=
                    synchronise,
            )
        )

        # Same-name rename is a persistent no-op.
        if (
            "result"
            not in runtime_sync_holder
        ):
            runtime_sync_holder[
                "result"
            ] = (
                self.save_load_bridge
                .synchronise_renamed_reference(
                    old_path,
                    new_path,
                    "design",
                    source=
                        "project_state_controller",
                )
            )

        self.current_design_manifest_path = (
            str(
                new_path
            )
        )

        self.set_status(
            "Canonical LEAF design renamed"
        )

        return {
            "entity_type":
                "design",

            "old_path":
                str(old_path),

            "new_path":
                str(new_path),

            "runtime_sync":
                runtime_sync_holder[
                    "result"
                ],
        }

    def new_project(self):
        self.manual_input_panel.clear_inputs()
        self.cea_panel.set_raw_output("")

        if hasattr(self.geometry_panel, "set_inputs"):
            self.geometry_panel.set_inputs(self.DEFAULT_GEOMETRY_INPUTS)

        if hasattr(self.materials_panel, "set_inputs"):
            self.materials_panel.set_inputs(self.DEFAULT_MATERIAL_INPUTS)

        if callable(self.set_design_history):
            self.set_design_history([])

        self.set_last_results({})
        self._refresh_outputs_after_state_change({})

        self.current_project_manifest_path = None
        self.current_design_manifest_path = None
        self.set_status("New project")

    def reset_defaults(self):
        self.clear_inputs()

        self.manual_input_panel.set_inputs(self.DEFAULT_MANUAL_INPUTS)

        if hasattr(self.geometry_panel, "set_inputs"):
            self.geometry_panel.set_inputs(self.DEFAULT_GEOMETRY_INPUTS)

        if hasattr(self.materials_panel, "set_inputs"):
            self.materials_panel.set_inputs(self.DEFAULT_MATERIAL_INPUTS)

        self.set_status("Defaults restored")

    def clear_inputs(self):
        self.manual_input_panel.clear_inputs()

        if callable(self.set_design_history):
            self.set_design_history([])

        self.set_last_results({})
        self._refresh_outputs_after_state_change({})
        self.set_status("Inputs cleared")

    def _normalise_project_state(self, state):
        if "calculator_inputs" in state:
            manual_inputs = state.get("calculator_inputs", {})
            cea_inputs = state.get("cea_inputs", {})
            material_inputs = state.get("regen_materials", {})
            geometry_inputs = state.get("geometry_inputs", {})
            benchmark_case = state.get("benchmark_case")
            last_results = state.get("last_results", {})
            design_history = state.get("design_history", [])
            startup_health_snapshot = state.get(
                "startup_health_snapshot",
                state.get("startup_health", {}),
            )
            cea_raw_output = state.get("cea_raw_output", "")

        elif "manual_inputs" in state:
            manual_inputs = state.get("manual_inputs", {})
            cea_inputs = state.get("cea_inputs", {})
            material_inputs = state.get("material_inputs", {})
            geometry_inputs = state.get("geometry_inputs", {})
            benchmark_case = state.get("benchmark_case")
            last_results = state.get("last_results", {})
            design_history = state.get("design_history", [])
            startup_health_snapshot = state.get(
                "startup_health_snapshot",
                state.get("startup_health", {}),
            )
            cea_raw_output = state.get("cea_raw_output", "")

        else:
            manual_inputs = state
            cea_inputs = {}
            material_inputs = {}
            geometry_inputs = {}
            benchmark_case = None
            last_results = {}
            design_history = []
            cea_raw_output = ""
            startup_health_snapshot = {}

        return {
            "calculator_inputs": self._normalise_manual_inputs(manual_inputs),
            "cea_inputs": cea_inputs if isinstance(cea_inputs, dict) else {},
            "regen_materials": material_inputs if isinstance(material_inputs, dict) else {},
            "geometry_inputs": geometry_inputs if isinstance(geometry_inputs, dict) else {},
            "benchmark_case": benchmark_case,
            "last_results": last_results if isinstance(last_results, dict) else {},
            "design_history": design_history if isinstance(design_history, list) else [],
            "cea_raw_output": cea_raw_output or "",
            "startup_health_snapshot": (
                startup_health_snapshot
                if isinstance(startup_health_snapshot, dict)
                else {}
            ),
        }

    def _normalise_manual_inputs(self, manual_inputs):
        if not isinstance(manual_inputs, dict):
            return {}

        valid_vars = set(self.label_to_var.values())
        loaded_values = {}

        for key, value in manual_inputs.items():
            if key in valid_vars:
                loaded_values[key] = value
            elif key in self.label_to_var:
                loaded_values[self.label_to_var[key]] = value

        return loaded_values

    def _refresh_outputs_after_state_change(self, results):
        results = results if isinstance(results, dict) else {}

        try:
            if results:
                self.output_panel.update_outputs(results)
            else:
                self.output_panel.clear_outputs()
        except Exception:
            pass

        try:
            self.warning_panel.clear_warnings()
        except Exception:
            pass

        if self.foundation_status_panel is not None:
            self.foundation_status_panel.update_status(
                results=results,
                startup_health_report=self.get_startup_health(),
            )

    def _get_cea_raw_output(self):
        try:
            return self.cea_panel.raw_output.toPlainText()
        except Exception:
            return ""