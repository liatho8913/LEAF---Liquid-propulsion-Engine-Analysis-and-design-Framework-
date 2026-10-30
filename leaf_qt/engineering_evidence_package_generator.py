from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_ROOT = Path("LEAF_Validation/engineering_packages")
DEFAULT_REGISTRY_NAME = "engineering_package_registry.json"

REFERENCE_OK = "REFERENCE_OK"
SNAPSHOT_OK = "SNAPSHOT_OK"
ARCHIVE_ONLY = "ARCHIVE_ONLY"
EXCLUDE = "EXCLUDE"

PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"


REQUIRED_COMPLETION_ROLES = {
    "architecture_report",
    "repository_index_or_manifest",
    "structured_evidence",
    "narrative_evidence",
}


EVIDENCE_PACKAGE_PUBLIC_CONTRACT = {
    "contract_id": "LEAF_ENGINEERING_EVIDENCE_PACKAGE_CONTRACT_V1",
    "phase_frozen": "16V.7",
    "stable_public_functions": [
        "generate_engineering_evidence_package",
        "discover_evidence_assets",
        "classify_evidence_policy",
        "evaluate_completion_gate",
        "update_engineering_package_registry",
        "audit_engineering_package_registry",
        "evaluate_legacy_evidence_ledger_replacement_gate",
        "write_legacy_replacement_gate_report",
        "audit_evidence_package_public_contract",
        "write_evidence_package_public_contract_report",
        "evaluate_evidence_package_contract_regression_gate",
        "write_evidence_package_contract_regression_report",
        "generate_engineering_evidence_package_closeout_certificate",
        "write_engineering_evidence_package_closeout_certificate",
        "refresh_evidence_package_contract_baseline",
        "write_evidence_package_contract_baseline_refresh_report",
    ],
    "stable_status_values": [PASS, WARN, FAIL],
    "stable_policy_values": [REFERENCE_OK, SNAPSHOT_OK, ARCHIVE_ONLY, EXCLUDE],
    "required_package_files": [
        "package_metadata.json",
        "engineering_narrative.txt",
        "asset_manifest.txt",
        "excluded_assets.txt",
        "completion_gate.json",
    ],
    "registry_schema": "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1",
    "default_output_root": str(DEFAULT_OUTPUT_ROOT),
}


@dataclass(frozen=True)
class EvidenceAsset:
    path: str
    role: str
    size_bytes: int
    sha256: str
    policy: str
    policy_reason: str
    snapshot_path: str | None = None


@dataclass(frozen=True)
class EvidenceCompletionGate:
    gate_status: str
    required_roles: list[str]
    present_roles: list[str]
    missing_roles: list[str]
    accepted_asset_count: int
    snapshot_count: int
    referenced_count: int
    archive_only_count: int
    excluded_count: int
    missing_expected_count: int
    reasons: list[str]


@dataclass(frozen=True)
class EngineeringPackageRegistryAudit:
    audit_status: str
    registry_path: str
    package_count: int
    passed_packages: int
    warned_packages: int
    failed_packages: int
    findings: list[str]


@dataclass(frozen=True)
class LegacyEvidenceLedgerReplacementGate:
    gate_status: str
    replacement_decision: str
    legacy_ledger_detected: bool
    registry_audit_status: str
    registry_package_count: int
    reasons: list[str]


@dataclass(frozen=True)
class EvidencePackagePublicContractAudit:
    audit_status: str
    contract_id: str
    checked_functions: list[str]
    missing_functions: list[str]
    checked_status_values: list[str]
    checked_policy_values: list[str]
    checked_required_files: list[str]
    registry_schema: str
    reasons: list[str]


@dataclass(frozen=True)
class EvidencePackageContractRegressionGate:
    gate_status: str
    baseline_path: str
    baseline_created: bool
    drift_detected: bool
    missing_keys: list[str]
    changed_keys: list[str]
    reasons: list[str]


@dataclass(frozen=True)
class EngineeringEvidencePackageCloseoutCertificate:
    certificate_status: str
    phase: str
    system: str
    generated_at_utc: str
    registry_audit_status: str
    legacy_replacement_status: str
    public_contract_status: str
    contract_regression_status: str
    package_count: int
    certificate_decision: str
    reasons: list[str]


@dataclass(frozen=True)
class EvidencePackageContractBaselineRefreshGate:
    gate_status: str
    baseline_path: str
    refresh_applied: bool
    previous_drift_detected: bool
    contract_audit_status: str
    reasons: list[str]


@dataclass(frozen=True)
class EngineeringEvidencePackage:
    milestone_id: str
    package_status: str
    generated_at_utc: str
    output_directory: str
    assets: list[EvidenceAsset]
    excluded_assets: list[str]
    missing_expected_assets: list[str]
    completion_gate: EvidenceCompletionGate
    narrative: str
    metadata: dict[str, Any]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_milestone_id(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value.strip())
    return cleaned or "UNNAMED_MILESTONE"


def _classify_asset(path: Path) -> str:
    name = path.name.lower()

    # Index/manifest must be detected before architecture because
    # repository_architecture_index.json contains both meanings.
    if "manifest" in name or "index" in name:
        return "repository_index_or_manifest"
    if "certificate" in name:
        return "completion_certificate"
    if "master_gate" in name or "gate" in name:
        return "gate_report"
    if "regression" in name:
        return "regression_report"
    if "validation" in name or "audit" in name:
        return "validation_or_audit_report"
    if "architecture" in name or "decomposition" in name or "contract" in name:
        return "architecture_report"
    if name.endswith(".py"):
        return "source_reference"
    if name.endswith(".json"):
        return "structured_evidence"
    if name.endswith(".txt") or name.endswith(".md"):
        return "narrative_evidence"

    return "supporting_evidence"


def classify_evidence_policy(path: Path, size_bytes: int) -> tuple[str, str]:
    parts = {part.lower() for part in path.parts}
    suffix = path.suffix.lower()
    name = path.name.lower()

    if any(part in parts for part in {".git", ".venv", "venv", "__pycache__"}):
        return EXCLUDE, "runtime_environment_or_cache"

    if any(part.startswith("dist") or part.startswith("build") for part in parts):
        return EXCLUDE, "packaged_build_artifact"

    if "_external_repository_quarantine" in parts:
        return ARCHIVE_ONLY, "repository_recovery_or_quarantine"

    if suffix in {".pyc", ".pyo", ".zip", ".dll", ".pyd", ".so", ".dylib", ".exe", ".dmg", ".mp4", ".mov", ".avi"}:
        return EXCLUDE, "binary_or_heavy_runtime_artifact"

    if ".phase_" in name or "backup" in name or suffix in {".bak", ".old"}:
        return ARCHIVE_ONLY, "historical_backup_or_migration_recovery"

    if size_bytes > 2_000_000:
        return REFERENCE_OK, "large_evidence_referenced_by_checksum"

    if suffix in {".py", ".json", ".txt", ".md", ".toml", ".yaml", ".yml"}:
        return SNAPSHOT_OK, "small_text_engineering_evidence"

    return REFERENCE_OK, "supporting_evidence_referenced_by_checksum"


def _copy_snapshot(root: Path, source: Path, output_dir: Path) -> str:
    rel = source.relative_to(root)
    destination = output_dir / "source_snapshot" / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination.relative_to(output_dir))


def discover_evidence_assets(
    root: str | Path = ".",
    milestone_terms: list[str] | None = None,
    extra_paths: list[str | Path] | None = None,
    output_dir: str | Path | None = None,
    enable_snapshots: bool = True,
) -> tuple[list[EvidenceAsset], list[str], list[str]]:
    root = Path(root)
    milestone_terms = [t.lower() for t in (milestone_terms or []) if t.strip()]
    extra_paths = extra_paths or []
    output_dir = Path(output_dir) if output_dir else None

    candidate_roots = [
        root / "artifacts",
        root / "project_evidence" / "generated_artifacts",
        root / "project_evidence" / "phase_artifacts",
        root / "leaf_qt",
        root / "project_maintenance",
    ]

    files: set[Path] = set()

    for base in candidate_roots:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if not path.is_file():
                continue

            rel_text = str(path.relative_to(root)).lower()
            if milestone_terms and not any(term in rel_text for term in milestone_terms):
                continue

            files.add(path)

    for raw in extra_paths:
        path = root / raw
        if path.exists() and path.is_file():
            files.add(path)

    assets: list[EvidenceAsset] = []
    excluded: list[str] = []
    missing: list[str] = []

    for path in sorted(files):
        try:
            stat = path.stat()
            policy, reason = classify_evidence_policy(path, stat.st_size)

            if policy == EXCLUDE:
                excluded.append(f"{path.relative_to(root)} | {reason}")
                continue

            snapshot_path = None
            if enable_snapshots and policy == SNAPSHOT_OK and output_dir is not None:
                snapshot_path = _copy_snapshot(root, path, output_dir)

            assets.append(
                EvidenceAsset(
                    path=str(path.relative_to(root)),
                    role=_classify_asset(path),
                    size_bytes=stat.st_size,
                    sha256=_sha256(path),
                    policy=policy,
                    policy_reason=reason,
                    snapshot_path=snapshot_path,
                )
            )
        except Exception as exc:
            missing.append(f"{path}: {exc}")

    return assets, excluded, missing


def evaluate_completion_gate(
    assets: list[EvidenceAsset],
    excluded_assets: list[str],
    missing_expected_assets: list[str],
    required_roles: set[str] | None = None,
) -> EvidenceCompletionGate:
    required = sorted(required_roles or REQUIRED_COMPLETION_ROLES)
    present = sorted({asset.role for asset in assets})
    missing_roles = [role for role in required if role not in present]

    snapshot_count = len([a for a in assets if a.policy == SNAPSHOT_OK])
    referenced_count = len([a for a in assets if a.policy == REFERENCE_OK])
    archive_only_count = len([a for a in assets if a.policy == ARCHIVE_ONLY])

    reasons: list[str] = []

    if not assets:
        reasons.append("No accepted evidence assets were discovered.")

    if missing_roles:
        reasons.append("Required evidence roles are missing: " + ", ".join(missing_roles))

    if missing_expected_assets:
        reasons.append("Some expected assets were unreadable or missing.")

    if not missing_roles and assets and not missing_expected_assets:
        status = PASS
        reasons.append("All required evidence roles are present and readable.")
    elif assets:
        status = WARN
    else:
        status = FAIL

    return EvidenceCompletionGate(
        gate_status=status,
        required_roles=required,
        present_roles=present,
        missing_roles=missing_roles,
        accepted_asset_count=len(assets),
        snapshot_count=snapshot_count,
        referenced_count=referenced_count,
        archive_only_count=archive_only_count,
        excluded_count=len(excluded_assets),
        missing_expected_count=len(missing_expected_assets),
        reasons=reasons,
    )


def _build_narrative(
    milestone_id: str,
    assets: list[EvidenceAsset],
    excluded: list[str],
    missing: list[str],
    gate: EvidenceCompletionGate,
) -> str:
    roles: dict[str, int] = {}
    policies: dict[str, int] = {}

    for asset in assets:
        roles[asset.role] = roles.get(asset.role, 0) + 1
        policies[asset.policy] = policies.get(asset.policy, 0) + 1

    lines = [
        f"ENGINEERING EVIDENCE PACKAGE — {milestone_id}",
        "=" * (32 + len(milestone_id)),
        "",
        "Purpose:",
        "This package records milestone-level engineering evidence without duplicating live runtime unnecessarily.",
        "",
        "Evidence policy:",
        "Live runtime, engineering evidence, and repository recovery remain separate.",
        "Small text evidence may be snapshotted.",
        "Large files are referenced by path and checksum.",
        "Recovery/quarantine files are archive-only.",
        "Runtime binaries, caches, packaged builds, and virtual environments are excluded.",
        "",
        "Completion gate:",
        f"- status: {gate.gate_status}",
        f"- required roles: {', '.join(gate.required_roles)}",
        f"- missing roles: {', '.join(gate.missing_roles) if gate.missing_roles else 'none'}",
        "",
        "Gate reasons:",
    ]

    lines.extend(f"- {reason}" for reason in gate.reasons)

    lines.extend(["", "Asset summary:"])

    for role, count in sorted(roles.items()):
        lines.append(f"- {role}: {count}")

    lines.append("")
    lines.append("Policy summary:")

    for policy, count in sorted(policies.items()):
        lines.append(f"- {policy}: {count}")

    lines.extend(
        [
            "",
            f"Total accepted assets: {len(assets)}",
            f"Excluded assets: {len(excluded)}",
            f"Missing or unreadable expected assets: {len(missing)}",
            "",
            "Status:",
            gate.gate_status,
        ]
    )

    return "\n".join(lines)




def update_engineering_package_registry(
    package: EngineeringEvidencePackage,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    registry_path = output_root / DEFAULT_REGISTRY_NAME

    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            registry = {}
    else:
        registry = {}

    packages = registry.get("packages", {})
    packages[package.milestone_id] = {
        "milestone_id": package.milestone_id,
        "package_status": package.package_status,
        "generated_at_utc": package.generated_at_utc,
        "output_directory": package.output_directory,
        "asset_count": len(package.assets),
        "excluded_count": len(package.excluded_assets),
        "missing_expected_count": len(package.missing_expected_assets),
        "snapshot_count": len([a for a in package.assets if a.snapshot_path]),
        "completion_gate_status": package.completion_gate.gate_status,
        "missing_roles": package.completion_gate.missing_roles,
        "metadata_path": str(Path(package.output_directory) / "package_metadata.json"),
        "completion_gate_path": str(Path(package.output_directory) / "completion_gate.json"),
        "narrative_path": str(Path(package.output_directory) / "engineering_narrative.txt"),
        "asset_manifest_path": str(Path(package.output_directory) / "asset_manifest.txt"),
    }

    registry = {
        "registry_schema": "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "package_count": len(packages),
        "packages": dict(sorted(packages.items())),
    }

    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    return registry_path




def audit_engineering_package_registry(
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> EngineeringPackageRegistryAudit:
    output_root = Path(output_root)
    registry_path = output_root / DEFAULT_REGISTRY_NAME
    findings: list[str] = []

    if not registry_path.exists():
        return EngineeringPackageRegistryAudit(
            audit_status=FAIL,
            registry_path=str(registry_path),
            package_count=0,
            passed_packages=0,
            warned_packages=0,
            failed_packages=1,
            findings=["Registry file does not exist."],
        )

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return EngineeringPackageRegistryAudit(
            audit_status=FAIL,
            registry_path=str(registry_path),
            package_count=0,
            passed_packages=0,
            warned_packages=0,
            failed_packages=1,
            findings=[f"Registry file could not be parsed: {exc}"],
        )

    if registry.get("registry_schema") != "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1":
        findings.append("Registry schema is missing or unsupported.")

    packages = registry.get("packages", {})
    if not isinstance(packages, dict) or not packages:
        findings.append("Registry contains no packages.")
        return EngineeringPackageRegistryAudit(
            audit_status=FAIL,
            registry_path=str(registry_path),
            package_count=0,
            passed_packages=0,
            warned_packages=0,
            failed_packages=1,
            findings=findings,
        )

    passed = 0
    warned = 0
    failed = 0

    required_entry_fields = {
        "milestone_id",
        "package_status",
        "output_directory",
        "metadata_path",
        "completion_gate_path",
        "narrative_path",
        "asset_manifest_path",
        "completion_gate_status",
    }

    for milestone_id, entry in sorted(packages.items()):
        if not isinstance(entry, dict):
            failed += 1
            findings.append(f"{milestone_id}: registry entry is not an object.")
            continue

        missing_fields = sorted(required_entry_fields - set(entry))
        if missing_fields:
            failed += 1
            findings.append(f"{milestone_id}: missing registry fields: {', '.join(missing_fields)}")
            continue

        entry_status = entry.get("package_status")
        gate_status = entry.get("completion_gate_status")

        package_findings: list[str] = []

        for field in [
            "output_directory",
            "metadata_path",
            "completion_gate_path",
            "narrative_path",
            "asset_manifest_path",
        ]:
            target = Path(entry.get(field, ""))
            if not target.exists():
                package_findings.append(f"missing {field}: {target}")

        metadata_path = Path(entry.get("metadata_path", ""))
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                if metadata.get("milestone_id") != milestone_id:
                    package_findings.append("metadata milestone_id does not match registry key")
                if metadata.get("package_status") != entry_status:
                    package_findings.append("metadata package_status does not match registry entry")
            except Exception as exc:
                package_findings.append(f"metadata parse failure: {exc}")

        gate_path = Path(entry.get("completion_gate_path", ""))
        if gate_path.exists():
            try:
                gate = json.loads(gate_path.read_text(encoding="utf-8"))
                if gate.get("gate_status") != gate_status:
                    package_findings.append("completion gate status does not match registry entry")
                if gate.get("gate_status") != PASS:
                    package_findings.append("completion gate is not PASS")
            except Exception as exc:
                package_findings.append(f"completion gate parse failure: {exc}")

        if package_findings:
            failed += 1
            findings.append(f"{milestone_id}: " + "; ".join(package_findings))
        elif entry_status == PASS and gate_status == PASS:
            passed += 1
        else:
            warned += 1
            findings.append(f"{milestone_id}: package_status={entry_status}, completion_gate_status={gate_status}")

    if failed:
        status = FAIL
    elif warned:
        status = WARN
    else:
        status = PASS

    return EngineeringPackageRegistryAudit(
        audit_status=status,
        registry_path=str(registry_path),
        package_count=len(packages),
        passed_packages=passed,
        warned_packages=warned,
        failed_packages=failed,
        findings=findings or ["All registered packages are complete and internally consistent."],
    )




def evaluate_legacy_evidence_ledger_replacement_gate(
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    legacy_paths: list[str | Path] | None = None,
) -> LegacyEvidenceLedgerReplacementGate:
    legacy_paths = legacy_paths or [
        "artifacts/legacy_evidence_ledger.json",
        "project_evidence/generated_artifacts/artifacts/legacy_evidence_ledger.json",
    ]

    detected_paths = [Path(path) for path in legacy_paths if Path(path).exists()]
    legacy_detected = bool(detected_paths)

    audit = audit_engineering_package_registry(output_root=output_root)

    reasons: list[str] = []

    if legacy_detected:
        reasons.append(
            "Legacy evidence ledger prototype detected and should now be treated as historical evidence."
        )
    else:
        reasons.append(
            "Legacy evidence ledger prototype was not detected; replacement can still proceed if registry is healthy."
        )

    if audit.audit_status == PASS:
        reasons.append("Engineering evidence package registry audit is PASS.")
    else:
        reasons.append(f"Engineering evidence package registry audit is {audit.audit_status}.")

    if audit.package_count > 0:
        reasons.append("At least one milestone evidence package is registered.")
    else:
        reasons.append("No milestone evidence packages are registered.")

    if audit.audit_status == PASS and audit.package_count > 0:
        status = PASS
        decision = "READY_TO_REPLACE_LEGACY_LEDGER_PROTOTYPE"
        reasons.append(
            "The milestone-based evidence package system is ready to replace the file-oriented legacy ledger prototype."
        )
    else:
        status = WARN
        decision = "KEEP_LEGACY_LEDGER_UNTIL_PACKAGE_SYSTEM_IS_HEALTHY"
        reasons.append(
            "Legacy ledger should remain available until the package registry passes audit."
        )

    return LegacyEvidenceLedgerReplacementGate(
        gate_status=status,
        replacement_decision=decision,
        legacy_ledger_detected=legacy_detected,
        registry_audit_status=audit.audit_status,
        registry_package_count=audit.package_count,
        reasons=reasons,
    )


def write_legacy_replacement_gate_report(
    gate: LegacyEvidenceLedgerReplacementGate,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / "legacy_evidence_ledger_replacement_gate.json"
    path.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")
    return path




def audit_evidence_package_public_contract() -> EvidencePackagePublicContractAudit:
    contract = EVIDENCE_PACKAGE_PUBLIC_CONTRACT
    missing_functions = [
        name for name in contract["stable_public_functions"]
        if name not in globals() or not callable(globals().get(name))
    ]

    reasons: list[str] = []

    if missing_functions:
        reasons.append("Missing stable public functions: " + ", ".join(missing_functions))

    status_values = contract["stable_status_values"]
    if sorted(status_values) != sorted([PASS, WARN, FAIL]):
        reasons.append("Stable status values do not match PASS/WARN/FAIL.")

    policy_values = contract["stable_policy_values"]
    if sorted(policy_values) != sorted([REFERENCE_OK, SNAPSHOT_OK, ARCHIVE_ONLY, EXCLUDE]):
        reasons.append("Stable policy values do not match evidence policy constants.")

    required_files = contract["required_package_files"]
    required_file_set = {
        "package_metadata.json",
        "engineering_narrative.txt",
        "asset_manifest.txt",
        "excluded_assets.txt",
        "completion_gate.json",
    }
    if set(required_files) != required_file_set:
        reasons.append("Required package file contract has drifted.")

    if contract.get("registry_schema") != "LEAF_ENGINEERING_EVIDENCE_PACKAGE_REGISTRY_V1":
        reasons.append("Registry schema contract has drifted.")

    if not reasons:
        reasons.append("Evidence package public contract is frozen and internally consistent.")
        status = PASS
    else:
        status = FAIL

    return EvidencePackagePublicContractAudit(
        audit_status=status,
        contract_id=contract["contract_id"],
        checked_functions=list(contract["stable_public_functions"]),
        missing_functions=missing_functions,
        checked_status_values=list(status_values),
        checked_policy_values=list(policy_values),
        checked_required_files=list(required_files),
        registry_schema=contract["registry_schema"],
        reasons=reasons,
    )


def write_evidence_package_public_contract_report(
    audit: EvidencePackagePublicContractAudit,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / "evidence_package_public_contract.json"
    path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")
    return path




def _normalised_public_contract_snapshot() -> dict[str, Any]:
    contract = dict(EVIDENCE_PACKAGE_PUBLIC_CONTRACT)
    contract["stable_public_functions"] = sorted(contract["stable_public_functions"])
    contract["stable_status_values"] = sorted(contract["stable_status_values"])
    contract["stable_policy_values"] = sorted(contract["stable_policy_values"])
    contract["required_package_files"] = sorted(contract["required_package_files"])
    return contract


def evaluate_evidence_package_contract_regression_gate(
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    baseline_name: str = "evidence_package_public_contract_baseline.json",
    create_if_missing: bool = True,
) -> EvidencePackageContractRegressionGate:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    baseline_path = output_root / baseline_name

    current = _normalised_public_contract_snapshot()

    if not baseline_path.exists():
        if create_if_missing:
            baseline_path.write_text(json.dumps(current, indent=2, sort_keys=True), encoding="utf-8")
            return EvidencePackageContractRegressionGate(
                gate_status=PASS,
                baseline_path=str(baseline_path),
                baseline_created=True,
                drift_detected=False,
                missing_keys=[],
                changed_keys=[],
                reasons=["Contract baseline created from current frozen public contract."],
            )

        return EvidencePackageContractRegressionGate(
            gate_status=FAIL,
            baseline_path=str(baseline_path),
            baseline_created=False,
            drift_detected=True,
            missing_keys=[],
            changed_keys=[],
            reasons=["Contract baseline does not exist and create_if_missing=False."],
        )

    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return EvidencePackageContractRegressionGate(
            gate_status=FAIL,
            baseline_path=str(baseline_path),
            baseline_created=False,
            drift_detected=True,
            missing_keys=[],
            changed_keys=[],
            reasons=[f"Contract baseline could not be parsed: {exc}"],
        )

    missing_keys = sorted(set(baseline) - set(current))
    changed_keys = sorted(
        key for key in baseline.keys() & current.keys()
        if baseline.get(key) != current.get(key)
    )

    reasons: list[str] = []

    if missing_keys:
        reasons.append("Current contract is missing baseline keys: " + ", ".join(missing_keys))

    if changed_keys:
        reasons.append("Contract drift detected in keys: " + ", ".join(changed_keys))

    drift = bool(missing_keys or changed_keys)

    if drift:
        status = FAIL
    else:
        status = PASS
        reasons.append("Current public contract matches frozen baseline.")

    return EvidencePackageContractRegressionGate(
        gate_status=status,
        baseline_path=str(baseline_path),
        baseline_created=False,
        drift_detected=drift,
        missing_keys=missing_keys,
        changed_keys=changed_keys,
        reasons=reasons,
    )


def write_evidence_package_contract_regression_report(
    gate: EvidencePackageContractRegressionGate,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / "evidence_package_contract_regression_gate.json"
    path.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")
    return path




def generate_engineering_evidence_package_closeout_certificate(
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> EngineeringEvidencePackageCloseoutCertificate:
    registry_audit = audit_engineering_package_registry(output_root=output_root)
    legacy_gate = evaluate_legacy_evidence_ledger_replacement_gate(output_root=output_root)
    contract_audit = audit_evidence_package_public_contract()
    regression_gate = evaluate_evidence_package_contract_regression_gate(output_root=output_root)

    checks = {
        "registry_audit": registry_audit.audit_status,
        "legacy_replacement": legacy_gate.gate_status,
        "public_contract": contract_audit.audit_status,
        "contract_regression": regression_gate.gate_status,
    }

    reasons: list[str] = []

    for name, status in checks.items():
        reasons.append(f"{name}={status}")

    if all(status == PASS for status in checks.values()):
        status = PASS
        decision = "ENGINEERING_EVIDENCE_PACKAGE_SYSTEM_COMPLETE"
        reasons.append(
            "Engineering Evidence Package Generator is complete and ready to supersede the legacy evidence ledger prototype."
        )
    else:
        status = WARN
        decision = "ENGINEERING_EVIDENCE_PACKAGE_SYSTEM_REQUIRES_REVIEW"
        reasons.append(
            "One or more closeout gates did not return PASS."
        )

    return EngineeringEvidencePackageCloseoutCertificate(
        certificate_status=status,
        phase="16V.9",
        system="Engineering Evidence Package Generator",
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        registry_audit_status=registry_audit.audit_status,
        legacy_replacement_status=legacy_gate.gate_status,
        public_contract_status=contract_audit.audit_status,
        contract_regression_status=regression_gate.gate_status,
        package_count=registry_audit.package_count,
        certificate_decision=decision,
        reasons=reasons,
    )


def write_engineering_evidence_package_closeout_certificate(
    certificate: EngineeringEvidencePackageCloseoutCertificate,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / "engineering_evidence_package_closeout_certificate.json"
    path.write_text(json.dumps(asdict(certificate), indent=2, sort_keys=True), encoding="utf-8")
    return path




def refresh_evidence_package_contract_baseline(
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    baseline_name: str = "evidence_package_public_contract_baseline.json",
    require_contract_audit_pass: bool = True,
) -> EvidencePackageContractBaselineRefreshGate:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    baseline_path = output_root / baseline_name

    contract_audit = audit_evidence_package_public_contract()
    previous_gate = evaluate_evidence_package_contract_regression_gate(
        output_root=output_root,
        baseline_name=baseline_name,
        create_if_missing=True,
    )

    reasons: list[str] = []

    if require_contract_audit_pass and contract_audit.audit_status != PASS:
        reasons.append(
            f"Contract audit is {contract_audit.audit_status}; baseline refresh refused."
        )
        return EvidencePackageContractBaselineRefreshGate(
            gate_status=FAIL,
            baseline_path=str(baseline_path),
            refresh_applied=False,
            previous_drift_detected=previous_gate.drift_detected,
            contract_audit_status=contract_audit.audit_status,
            reasons=reasons,
        )

    current = _normalised_public_contract_snapshot()
    baseline_path.write_text(json.dumps(current, indent=2, sort_keys=True), encoding="utf-8")

    final_gate = evaluate_evidence_package_contract_regression_gate(
        output_root=output_root,
        baseline_name=baseline_name,
        create_if_missing=False,
    )

    if final_gate.gate_status == PASS:
        status = PASS
        reasons.append("Contract baseline refreshed to the current approved public contract.")
        if previous_gate.drift_detected:
            reasons.append("Previous drift was intentional and has now been resolved.")
        else:
            reasons.append("No previous drift was present; baseline was reaffirmed.")
    else:
        status = FAIL
        reasons.append("Baseline refresh was attempted but regression gate still failed.")

    return EvidencePackageContractBaselineRefreshGate(
        gate_status=status,
        baseline_path=str(baseline_path),
        refresh_applied=status == PASS,
        previous_drift_detected=previous_gate.drift_detected,
        contract_audit_status=contract_audit.audit_status,
        reasons=reasons,
    )


def write_evidence_package_contract_baseline_refresh_report(
    gate: EvidencePackageContractBaselineRefreshGate,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
) -> Path:
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / "evidence_package_contract_baseline_refresh_gate.json"
    path.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")
    return path


def generate_engineering_evidence_package(
    milestone_id: str,
    root: str | Path = ".",
    milestone_terms: list[str] | None = None,
    extra_paths: list[str | Path] | None = None,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    enable_snapshots: bool = True,
    required_roles: set[str] | None = None,
    update_registry: bool = True,
) -> EngineeringEvidencePackage:
    root = Path(root)
    safe_id = _safe_milestone_id(milestone_id)
    output_dir = Path(output_root) / safe_id
    output_dir.mkdir(parents=True, exist_ok=True)

    assets, excluded, missing = discover_evidence_assets(
        root=root,
        milestone_terms=milestone_terms,
        extra_paths=extra_paths,
        output_dir=output_dir,
        enable_snapshots=enable_snapshots,
    )

    gate = evaluate_completion_gate(
        assets=assets,
        excluded_assets=excluded,
        missing_expected_assets=missing,
        required_roles=required_roles,
    )

    narrative = _build_narrative(safe_id, assets, excluded, missing, gate)

    package = EngineeringEvidencePackage(
        milestone_id=safe_id,
        package_status=gate.gate_status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        output_directory=str(output_dir),
        assets=assets,
        excluded_assets=excluded,
        missing_expected_assets=missing,
        completion_gate=gate,
        narrative=narrative,
        metadata={
            "phase": "16V.9B",
            "system": "Engineering Evidence Package Generator",
            "policy": "milestone_based_evidence_contract_baseline_refresh_gate",
            "runtime_copy_policy": "small_text_snapshot_large_file_reference",
            "replacement_target": "legacy_evidence_ledger_prototype",
            "asset_count": len(assets),
            "excluded_count": len(excluded),
            "snapshot_count": len([a for a in assets if a.snapshot_path]),
            "completion_gate_status": gate.gate_status,
        },
    )

    (output_dir / "package_metadata.json").write_text(
        json.dumps(
            {
                **asdict(package),
                "assets": [asdict(asset) for asset in assets],
                "completion_gate": asdict(gate),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    (output_dir / "engineering_narrative.txt").write_text(narrative, encoding="utf-8")

    (output_dir / "asset_manifest.txt").write_text(
        "\n".join(
            f"{asset.policy} | {asset.role} | {asset.size_bytes} bytes | "
            f"{asset.sha256} | snapshot={asset.snapshot_path or '-'} | {asset.path}"
            for asset in assets
        )
        + "\n",
        encoding="utf-8",
    )

    (output_dir / "excluded_assets.txt").write_text(
        "\n".join(excluded) + ("\n" if excluded else ""),
        encoding="utf-8",
    )

    (output_dir / "completion_gate.json").write_text(
        json.dumps(asdict(gate), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    if update_registry:
        update_engineering_package_registry(package, output_root=output_root)

    return package


def main() -> int:
    package = generate_engineering_evidence_package(
        milestone_id="phase_16v9b_contract_baseline_refresh_gate",
        milestone_terms=[
            "legacy_evidence",
            "repository_architecture",
            "contract",
            "decomposition",
            "sustainability",
            "16v",
        ],
        extra_paths=[
            "artifacts/legacy_evidence_ledger.json",
            "artifacts/repository_architecture_index.json",
            "artifacts/repository_organisation_manifest.json",
            "project_evidence/generated_artifacts/artifacts/repository_architecture_index.json",
            "project_evidence/generated_artifacts/artifacts/repository_organisation_manifest.json",
            "artifacts/engine_solver_contract_stack_closeout_certificate.json",
            "artifacts/engine_solver_decomposition_dry_run_gate.json",
            "leaf_qt/engineering_evidence_package_generator.py",
        ],
    )

    print(f"status={package.package_status}")
    print(f"milestone_id={package.milestone_id}")
    print(f"asset_count={len(package.assets)}")
    print(f"excluded_count={len(package.excluded_assets)}")
    print(f"snapshot_count={len([a for a in package.assets if a.snapshot_path])}")
    print(f"completion_gate={package.completion_gate.gate_status}")
    print(f"missing_roles={package.completion_gate.missing_roles}")
    print(f"output_directory={package.output_directory}")

    audit = audit_engineering_package_registry()
    print(f"registry_audit={audit.audit_status}")
    print(f"registry_package_count={audit.package_count}")
    print(f"registry_failed_packages={audit.failed_packages}")

    replacement_gate = evaluate_legacy_evidence_ledger_replacement_gate()
    replacement_report = write_legacy_replacement_gate_report(replacement_gate)
    print(f"legacy_replacement_gate={replacement_gate.gate_status}")
    print(f"legacy_replacement_decision={replacement_gate.replacement_decision}")
    print(f"legacy_replacement_report={replacement_report}")

    contract_audit = audit_evidence_package_public_contract()
    contract_report = write_evidence_package_public_contract_report(contract_audit)
    print(f"public_contract_audit={contract_audit.audit_status}")
    print(f"public_contract_id={contract_audit.contract_id}")
    print(f"public_contract_report={contract_report}")

    regression_gate = evaluate_evidence_package_contract_regression_gate()
    regression_report = write_evidence_package_contract_regression_report(regression_gate)
    print(f"contract_regression_gate_before_refresh={regression_gate.gate_status}")
    print(f"contract_drift_detected_before_refresh={regression_gate.drift_detected}")
    print(f"contract_regression_report={regression_report}")

    refresh_gate = refresh_evidence_package_contract_baseline()
    refresh_report = write_evidence_package_contract_baseline_refresh_report(refresh_gate)
    print(f"baseline_refresh_gate={refresh_gate.gate_status}")
    print(f"baseline_refresh_applied={refresh_gate.refresh_applied}")
    print(f"baseline_refresh_report={refresh_report}")

    regression_gate_after = evaluate_evidence_package_contract_regression_gate()
    write_evidence_package_contract_regression_report(regression_gate_after)
    print(f"contract_regression_gate_after_refresh={regression_gate_after.gate_status}")
    print(f"contract_drift_detected_after_refresh={regression_gate_after.drift_detected}")

    closeout = generate_engineering_evidence_package_closeout_certificate()
    closeout_report = write_engineering_evidence_package_closeout_certificate(closeout)
    print(f"closeout_certificate={closeout.certificate_status}")
    print(f"closeout_decision={closeout.certificate_decision}")
    print(f"closeout_report={closeout_report}")
    print("PASS_PHASE_16V9B_CONTRACT_BASELINE_REFRESH_GATE")

    return 0 if package.package_status in {PASS, WARN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
