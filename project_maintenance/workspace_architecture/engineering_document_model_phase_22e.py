from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.design_session_manager_phase_22d import (
    USER_DESIGN_ROOT,
)

SCHEMA = "LEAF_ENGINEERING_DOCUMENT_MODEL_PHASE_22E_V1"

USER_PROJECT_ROOT = "LEAF_Projects"
USER_REPORT_ROOT = "LEAF_Reports"
USER_EXPORT_ROOT = "LEAF_Exports"


@dataclass(frozen=True)
class EngineeringDocumentType:
    document_type: str
    label: str
    canonical_root: str
    default_extension: str
    owner_layer: str
    user_visible: bool
    internal_storage: bool
    qt_owns_document_logic: bool
    filesystem_mutation_requires_user_action: bool


def build_engineering_document_model(project_root: str | Path = ".") -> dict[str, Any]:
    document_types = [
        EngineeringDocumentType(
            "design",
            "Design",
            USER_DESIGN_ROOT,
            ".leaf_design.json",
            "design_session_manager",
            True,
            False,
            False,
            True,
        ),
        EngineeringDocumentType(
            "project",
            "Project",
            USER_PROJECT_ROOT,
            ".leaf_project.json",
            "workspace_project_owner",
            True,
            False,
            False,
            True,
        ),
        EngineeringDocumentType(
            "report",
            "Report",
            USER_REPORT_ROOT,
            ".leaf_report.json",
            "report_owner",
            True,
            False,
            False,
            True,
        ),
        EngineeringDocumentType(
            "export",
            "Export",
            USER_EXPORT_ROOT,
            ".leaf_export",
            "export_owner",
            True,
            False,
            False,
            True,
        ),
    ]

    return {
        "schema": SCHEMA,
        "phase": "22E",
        "feature": "ENGINEERING_DOCUMENT_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "document_rule": "User-facing engineering documents live in clear canonical roots. Internal artifacts may index or reference them but must not become authoritative user storage.",
        "document_types": [asdict(doc) for doc in document_types],
        "canonical_roots": {
            doc.document_type: doc.canonical_root for doc in document_types
        },
        "summary": {
            "document_type_count": len(document_types),
            "user_visible_document_types": sum(1 for doc in document_types if doc.user_visible),
            "internal_storage_document_types": sum(1 for doc in document_types if doc.internal_storage),
            "qt_owns_document_logic_count": sum(1 for doc in document_types if doc.qt_owns_document_logic),
            "filesystem_mutation_requires_user_action_count": sum(
                1 for doc in document_types if doc.filesystem_mutation_requires_user_action
            ),
            "design_root": USER_DESIGN_ROOT,
            "project_root": USER_PROJECT_ROOT,
            "report_root": USER_REPORT_ROOT,
            "export_root": USER_EXPORT_ROOT,
            "developer_user_architecture_separated": True,
            "ready_for_22f_report_export_routing": True,
        },
        "safety_boundaries": {
            "qt_owns_document_logic": False,
            "internal_artifacts_are_authoritative_user_storage": False,
            "automatic_sorting_activation": False,
            "automatic_filesystem_mutation": False,
            "solver_execution": False,
        },
    }


def write_engineering_document_model(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_22e"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_engineering_document_model(root)

    json_path = out_dir / "engineering_document_model_phase_22e.json"
    txt_path = out_dir / "engineering_document_model_phase_22e.txt"

    json_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 22E ENGINEERING DOCUMENT MODEL",
        "=========================================",
        f"schema={model['schema']}",
        f"phase={model['phase']}",
        f"feature={model['feature']}",
        f"document_type_count={model['summary']['document_type_count']}",
        f"user_visible_document_types={model['summary']['user_visible_document_types']}",
        f"internal_storage_document_types={model['summary']['internal_storage_document_types']}",
        f"qt_owns_document_logic_count={model['summary']['qt_owns_document_logic_count']}",
        f"developer_user_architecture_separated={model['summary']['developer_user_architecture_separated']}",
        f"ready_for_22f_report_export_routing={model['summary']['ready_for_22f_report_export_routing']}",
        "",
        "Canonical Roots:",
        *[
            f"{key}={value}"
            for key, value in model["canonical_roots"].items()
        ],
        "",
        "Document Types:",
        *[
            f"{doc['document_type']} -> {doc['canonical_root']} -> {doc['default_extension']}"
            for doc in model["document_types"]
        ],
    ]), encoding="utf-8")

    return {
        "model": model,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_engineering_document_model(Path.cwd())
    print("PASS_PHASE_22E_ENGINEERING_DOCUMENT_MODEL_WRITTEN")
    print(f"schema={result['model']['schema']}")
    print(f"document_type_count={result['model']['summary']['document_type_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
