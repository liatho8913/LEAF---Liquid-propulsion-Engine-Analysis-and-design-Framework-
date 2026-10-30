from pathlib import Path
import json
import tempfile

from engineering_evidence_package_generator import (
    ARCHIVE_ONLY,
    EXCLUDE,
    PASS,
    REFERENCE_OK,
    SNAPSHOT_OK,
    WARN,
    classify_evidence_policy,
    evaluate_completion_gate,
    generate_engineering_evidence_package,
    update_engineering_package_registry,
    audit_engineering_package_registry,
    evaluate_legacy_evidence_ledger_replacement_gate,
    write_legacy_replacement_gate_report,
    audit_evidence_package_public_contract,
    write_evidence_package_public_contract_report,
    EVIDENCE_PACKAGE_PUBLIC_CONTRACT,
    evaluate_evidence_package_contract_regression_gate,
    write_evidence_package_contract_regression_report,
    generate_engineering_evidence_package_closeout_certificate,
    write_engineering_evidence_package_closeout_certificate,
    refresh_evidence_package_contract_baseline,
    write_evidence_package_contract_baseline_refresh_report,
)


def test_phase_16v3_engineering_evidence_package_completion_gate_pass():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        artifacts = root / "artifacts"
        artifacts.mkdir()

        (artifacts / "repository_architecture_index.json").write_text('{"status": "PASS"}', encoding="utf-8")
        (artifacts / "engine_solver_contract_stack_closeout_certificate.json").write_text('{"status": "PASS"}', encoding="utf-8")
        (artifacts / "engine_solver_decomposition_dry_run_gate.json").write_text('{"status": "PASS"}', encoding="utf-8")
        (artifacts / "engineering_narrative.txt").write_text("Narrative", encoding="utf-8")

        package = generate_engineering_evidence_package(
            milestone_id="phase_16v3_test",
            root=root,
            milestone_terms=["repository", "engine_solver", "engineering"],
            extra_paths=[
                "artifacts/repository_architecture_index.json",
                "artifacts/engine_solver_contract_stack_closeout_certificate.json",
                "artifacts/engine_solver_decomposition_dry_run_gate.json",
                "artifacts/engineering_narrative.txt",
            ],
            output_root=root / "project_evidence" / "engineering_packages",
        )

        assert package.package_status == PASS
        assert package.completion_gate.gate_status == PASS
        assert not package.completion_gate.missing_roles

        output = Path(package.output_directory)
        assert (output / "package_metadata.json").exists()
        assert (output / "engineering_narrative.txt").exists()
        assert (output / "asset_manifest.txt").exists()
        assert (output / "excluded_assets.txt").exists()
        assert (output / "completion_gate.json").exists()

        metadata = json.loads((output / "package_metadata.json").read_text(encoding="utf-8"))
        assert metadata["metadata"]["phase"] == "16V.3"
        assert metadata["metadata"]["completion_gate_status"] == PASS
        assert metadata["completion_gate"]["gate_status"] == PASS


def test_phase_16v3_completion_gate_warns_when_required_roles_missing():
    assets = []
    gate = evaluate_completion_gate(
        assets=assets,
        excluded_assets=[],
        missing_expected_assets=[],
        required_roles={"architecture_report"},
    )
    assert gate.gate_status != PASS
    assert "architecture_report" in gate.missing_roles

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        artifacts = root / "artifacts"
        artifacts.mkdir()
        (artifacts / "only_data.json").write_text("{}", encoding="utf-8")

        package = generate_engineering_evidence_package(
            milestone_id="phase_16v3_warn_test",
            root=root,
            milestone_terms=["only_data"],
            extra_paths=["artifacts/only_data.json"],
            output_root=root / "project_evidence" / "engineering_packages",
            required_roles={"architecture_report"},
        )

        assert package.package_status == WARN
        assert "architecture_report" in package.completion_gate.missing_roles


def test_phase_16v3_policy_classifier_direct_cases():
    assert classify_evidence_policy(Path("leaf_qt/example.py"), 200)[0] == SNAPSHOT_OK
    assert classify_evidence_policy(Path("artifacts/large.json"), 3_000_000)[0] == REFERENCE_OK
    assert classify_evidence_policy(Path("leaf_qt/__pycache__/x.pyc"), 100)[0] == EXCLUDE
    assert classify_evidence_policy(Path("_external_repository_quarantine/old.py"), 100)[0] == ARCHIVE_ONLY
    assert classify_evidence_policy(Path("leaf_qt/engine_solver.py.phase_16u8_backup"), 100)[0] == ARCHIVE_ONLY

def test_phase_16v3b_repository_architecture_index_classifies_as_manifest_role():
    from engineering_evidence_package_generator import _classify_asset

    assert _classify_asset(Path("artifacts/repository_architecture_index.json")) == "repository_index_or_manifest"
    assert _classify_asset(Path("artifacts/repository_organisation_manifest.json")) == "repository_index_or_manifest"

def test_phase_16v4_engineering_package_registry_updates_authoritative_index():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        artifacts = root / "artifacts"
        artifacts.mkdir()

        (artifacts / "repository_architecture_index.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_contract_stack_closeout_certificate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_decomposition_dry_run_gate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engineering_narrative.txt").write_text("Narrative", encoding="utf-8")

        output_root = root / "project_evidence" / "engineering_packages"

        package = generate_engineering_evidence_package(
            milestone_id="phase_16v4_registry_test",
            root=root,
            milestone_terms=["repository", "engine_solver", "engineering"],
            extra_paths=[
                "artifacts/repository_architecture_index.json",
                "artifacts/engine_solver_contract_stack_closeout_certificate.json",
                "artifacts/engine_solver_decomposition_dry_run_gate.json",
                "artifacts/engineering_narrative.txt",
            ],
            output_root=output_root,
        )

        registry_path = output_root / "engineering_package_registry.json"
        assert registry_path.exists()

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        assert registry["registry_schema"] == "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1"
        assert registry["package_count"] == 1
        assert "phase_16v4_registry_test" in registry["packages"]

        entry = registry["packages"]["phase_16v4_registry_test"]
        assert entry["package_status"] == PASS
        assert entry["completion_gate_status"] == PASS
        assert entry["asset_count"] == len(package.assets)
        assert entry["metadata_path"].endswith("package_metadata.json")

        registry_path_2 = update_engineering_package_registry(package, output_root=output_root)
        assert registry_path_2 == registry_path

def test_phase_16v5_registry_completion_audit_passes_complete_registry():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        artifacts = root / "artifacts"
        artifacts.mkdir()

        (artifacts / "repository_architecture_index.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_contract_stack_closeout_certificate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_decomposition_dry_run_gate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engineering_narrative.txt").write_text("Narrative", encoding="utf-8")

        output_root = root / "project_evidence" / "engineering_packages"

        generate_engineering_evidence_package(
            milestone_id="phase_16v5_registry_audit_test",
            root=root,
            milestone_terms=["repository", "engine_solver", "engineering"],
            extra_paths=[
                "artifacts/repository_architecture_index.json",
                "artifacts/engine_solver_contract_stack_closeout_certificate.json",
                "artifacts/engine_solver_decomposition_dry_run_gate.json",
                "artifacts/engineering_narrative.txt",
            ],
            output_root=output_root,
        )

        audit = audit_engineering_package_registry(output_root=output_root)
        assert audit.audit_status == PASS
        assert audit.package_count == 1
        assert audit.passed_packages == 1
        assert audit.failed_packages == 0
        assert audit.findings


def test_phase_16v5_registry_completion_audit_fails_missing_package_file():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        output_root = root / "project_evidence" / "engineering_packages"
        output_root.mkdir(parents=True)

        registry = {
            "registry_schema": "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1",
            "package_count": 1,
            "packages": {
                "broken_package": {
                    "milestone_id": "broken_package",
                    "package_status": PASS,
                    "completion_gate_status": PASS,
                    "output_directory": str(output_root / "broken_package"),
                    "metadata_path": str(output_root / "broken_package" / "package_metadata.json"),
                    "completion_gate_path": str(output_root / "broken_package" / "completion_gate.json"),
                    "narrative_path": str(output_root / "broken_package" / "engineering_narrative.txt"),
                    "asset_manifest_path": str(output_root / "broken_package" / "asset_manifest.txt"),
                }
            },
        }

        (output_root / "engineering_package_registry.json").write_text(
            json.dumps(registry, indent=2),
            encoding="utf-8",
        )

        audit = audit_engineering_package_registry(output_root=output_root)
        assert audit.audit_status == FAIL
        assert audit.failed_packages == 1
        assert any("broken_package" in finding for finding in audit.findings)

def test_phase_16v6_legacy_evidence_ledger_replacement_gate_passes_when_registry_is_healthy():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        artifacts = root / "artifacts"
        artifacts.mkdir()

        (artifacts / "legacy_evidence_ledger.json").write_text("{}", encoding="utf-8")
        (artifacts / "repository_architecture_index.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_contract_stack_closeout_certificate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_decomposition_dry_run_gate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engineering_narrative.txt").write_text("Narrative", encoding="utf-8")

        output_root = root / "project_evidence" / "engineering_packages"

        generate_engineering_evidence_package(
            milestone_id="phase_16v6_replacement_gate_test",
            root=root,
            milestone_terms=["repository", "engine_solver", "engineering", "legacy"],
            extra_paths=[
                "artifacts/legacy_evidence_ledger.json",
                "artifacts/repository_architecture_index.json",
                "artifacts/engine_solver_contract_stack_closeout_certificate.json",
                "artifacts/engine_solver_decomposition_dry_run_gate.json",
                "artifacts/engineering_narrative.txt",
            ],
            output_root=output_root,
        )

        old_cwd = Path.cwd()
        try:
            import os
            os.chdir(root)
            gate = evaluate_legacy_evidence_ledger_replacement_gate(output_root=output_root)
            report = write_legacy_replacement_gate_report(gate, output_root=output_root)
        finally:
            os.chdir(old_cwd)

        assert gate.gate_status == PASS
        assert gate.replacement_decision == "READY_TO_REPLACE_LEGACY_LEDGER_PROTOTYPE"
        assert gate.legacy_ledger_detected is True
        assert gate.registry_audit_status == PASS
        assert report.exists()

        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["gate_status"] == PASS
        assert data["replacement_decision"] == "READY_TO_REPLACE_LEGACY_LEDGER_PROTOTYPE"


def test_phase_16v6_legacy_replacement_gate_warns_without_registry():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        output_root = root / "project_evidence" / "engineering_packages"
        output_root.mkdir(parents=True)

        gate = evaluate_legacy_evidence_ledger_replacement_gate(output_root=output_root)

        assert gate.gate_status == WARN
        assert gate.replacement_decision == "KEEP_LEGACY_LEDGER_UNTIL_PACKAGE_SYSTEM_IS_HEALTHY"
        assert gate.registry_audit_status == FAIL

def test_phase_16v7_evidence_package_public_contract_audit_passes():
    audit = audit_evidence_package_public_contract()

    assert audit.audit_status == PASS
    assert audit.contract_id == "LEAF_ENGINEERING_EVIDENCE_PACKAGE_CONTRACT_V1"
    assert not audit.missing_functions
    assert "generate_engineering_evidence_package" in audit.checked_functions
    assert "audit_engineering_package_registry" in audit.checked_functions
    assert "write_evidence_package_public_contract_report" in audit.checked_functions
    assert sorted(audit.checked_status_values) == sorted([PASS, WARN, FAIL])
    assert sorted(audit.checked_policy_values) == sorted([REFERENCE_OK, SNAPSHOT_OK, ARCHIVE_ONLY, EXCLUDE])
    assert "package_metadata.json" in audit.checked_required_files
    assert audit.registry_schema == "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1"


def test_phase_16v7_evidence_package_public_contract_report_writes():
    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp) / "project_evidence" / "engineering_packages"
        audit = audit_evidence_package_public_contract()
        report = write_evidence_package_public_contract_report(audit, output_root=output_root)

        assert report.exists()
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["audit_status"] == PASS
        assert data["contract_id"] == EVIDENCE_PACKAGE_PUBLIC_CONTRACT["contract_id"]
        assert data["registry_schema"] == "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1"

def test_phase_16v8_contract_regression_gate_creates_and_matches_baseline():
    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp) / "project_evidence" / "engineering_packages"

        first = evaluate_evidence_package_contract_regression_gate(output_root=output_root)
        assert first.gate_status == PASS
        assert first.baseline_created is True
        assert first.drift_detected is False
        assert Path(first.baseline_path).exists()

        second = evaluate_evidence_package_contract_regression_gate(output_root=output_root)
        assert second.gate_status == PASS
        assert second.baseline_created is False
        assert second.drift_detected is False
        assert not second.changed_keys

        report = write_evidence_package_contract_regression_report(second, output_root=output_root)
        assert report.exists()

        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["gate_status"] == PASS
        assert data["drift_detected"] is False


def test_phase_16v8_contract_regression_gate_detects_drift():
    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp) / "project_evidence" / "engineering_packages"
        output_root.mkdir(parents=True)

        baseline = dict(EVIDENCE_PACKAGE_PUBLIC_CONTRACT)
        baseline["registry_schema"] = "OLD_SCHEMA"
        baseline["stable_public_functions"] = []

        baseline_path = output_root / "evidence_package_public_contract_baseline.json"
        baseline_path.write_text(json.dumps(baseline, indent=2), encoding="utf-8")

        gate = evaluate_evidence_package_contract_regression_gate(output_root=output_root)

        assert gate.gate_status == FAIL
        assert gate.drift_detected is True
        assert "registry_schema" in gate.changed_keys or "stable_public_functions" in gate.changed_keys

def test_phase_16v9_engineering_evidence_package_closeout_certificate_passes():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        artifacts = root / "artifacts"
        artifacts.mkdir()

        (artifacts / "legacy_evidence_ledger.json").write_text("{}", encoding="utf-8")
        (artifacts / "repository_architecture_index.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_contract_stack_closeout_certificate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engine_solver_decomposition_dry_run_gate.json").write_text("{}", encoding="utf-8")
        (artifacts / "engineering_narrative.txt").write_text("Narrative", encoding="utf-8")

        output_root = root / "project_evidence" / "engineering_packages"

        generate_engineering_evidence_package(
            milestone_id="phase_16v9_closeout_test",
            root=root,
            milestone_terms=["repository", "engine_solver", "engineering", "legacy"],
            extra_paths=[
                "artifacts/legacy_evidence_ledger.json",
                "artifacts/repository_architecture_index.json",
                "artifacts/engine_solver_contract_stack_closeout_certificate.json",
                "artifacts/engine_solver_decomposition_dry_run_gate.json",
                "artifacts/engineering_narrative.txt",
            ],
            output_root=output_root,
        )

        old_cwd = Path.cwd()
        try:
            import os
            os.chdir(root)
            certificate = generate_engineering_evidence_package_closeout_certificate(output_root=output_root)
            report = write_engineering_evidence_package_closeout_certificate(
                certificate,
                output_root=output_root,
            )
        finally:
            os.chdir(old_cwd)

        assert certificate.certificate_status == PASS
        assert certificate.certificate_decision == "ENGINEERING_EVIDENCE_PACKAGE_SYSTEM_COMPLETE"
        assert certificate.registry_audit_status == PASS
        assert certificate.legacy_replacement_status == PASS
        assert certificate.public_contract_status == PASS
        assert certificate.contract_regression_status == PASS
        assert report.exists()

        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["phase"] == "16V.9"
        assert data["certificate_status"] == PASS
        assert data["certificate_decision"] == "ENGINEERING_EVIDENCE_PACKAGE_SYSTEM_COMPLETE"

def test_phase_16v9b_contract_baseline_refresh_gate_resolves_drift():
    with tempfile.TemporaryDirectory() as tmp:
        output_root = Path(tmp) / "project_evidence" / "engineering_packages"
        output_root.mkdir(parents=True)

        old_baseline = dict(EVIDENCE_PACKAGE_PUBLIC_CONTRACT)
        old_baseline["registry_schema"] = "OLDER_SCHEMA"
        old_baseline["stable_public_functions"] = []

        baseline_path = output_root / "evidence_package_public_contract_baseline.json"
        baseline_path.write_text(json.dumps(old_baseline, indent=2), encoding="utf-8")

        before = evaluate_evidence_package_contract_regression_gate(output_root=output_root)
        assert before.gate_status == FAIL
        assert before.drift_detected is True

        refresh = refresh_evidence_package_contract_baseline(output_root=output_root)
        assert refresh.gate_status == PASS
        assert refresh.refresh_applied is True
        assert refresh.previous_drift_detected is True
        assert refresh.contract_audit_status == PASS

        after = evaluate_evidence_package_contract_regression_gate(output_root=output_root)
        assert after.gate_status == PASS
        assert after.drift_detected is False

        report = write_evidence_package_contract_baseline_refresh_report(refresh, output_root=output_root)
        assert report.exists()

        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["gate_status"] == PASS
        assert data["refresh_applied"] is True

