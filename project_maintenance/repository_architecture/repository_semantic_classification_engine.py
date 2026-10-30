from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_knowledge_database import (
    build_repository_knowledge_database,
)

SCHEMA = "LEAF_REPOSITORY_SEMANTIC_CLASSIFICATION_ENGINE_V1"


SEMANTIC_SIGNALS = {
    "iterative_solver": {
        "keywords": ["brentq", "root_scalar", "newton", "solve", "iterate", "converge", "residual"],
        "subsystem_hint": "solver",
        "role_hint": "solver",
    },
    "validation_gate": {
        "keywords": ["passed", "failures", "blocked", "gate", "validate", "validation", "raise systemexit"],
        "subsystem_hint": "validation",
        "role_hint": "validator",
    },
    "report_artifact": {
        "keywords": ["write_text", "json.dumps", "report", "certificate", "summary", "artifact"],
        "subsystem_hint": "reports",
        "role_hint": "reporter",
    },
    "qt_interface": {
        "keywords": ["qwidget", "qmainwindow", "qdialog", "qlabel", "qtablewidget", "pyside6", "qt"],
        "subsystem_hint": "ui",
        "role_hint": "viewer",
    },
    "repository_intelligence": {
        "keywords": ["repository", "architecture", "metadata", "knowledge", "dependency", "ownership", "sorter"],
        "subsystem_hint": "repository_architecture",
        "role_hint": "controller",
    },
    "regen_thermal": {
        "keywords": ["regen", "coolant", "channel", "heat flux", "wall temperature", "bartz", "pressure drop"],
        "subsystem_hint": "regen",
        "role_hint": "solver",
    },
    "materials_data": {
        "keywords": ["material", "conductivity", "density", "yield", "alloy", "interpolation"],
        "subsystem_hint": "materials",
        "role_hint": "database",
    },
    "coating_data": {
        "keywords": ["coating", "liner", "barrier", "bondcoat", "emissivity"],
        "subsystem_hint": "coatings",
        "role_hint": "database",
    },
    "history_narrative": {
        "keywords": ["history", "iteration", "narrative", "timeline", "attempt", "decision"],
        "subsystem_hint": "history",
        "role_hint": "controller",
    },
    "optimisation": {
        "keywords": ["candidate", "ranking", "optimisation", "optimization", "mutation", "selection"],
        "subsystem_hint": "optimisation",
        "role_hint": "controller",
    },
}


def _read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    return path.read_text(encoding="utf-8", errors="replace")


def _ast_shape(text: str) -> dict[str, int]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {
            "function_count": 0,
            "class_count": 0,
            "branch_count": 0,
            "loop_count": 0,
            "call_count": 0,
            "assignment_count": 0,
        }

    return {
        "function_count": sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree)),
        "class_count": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree)),
        "branch_count": sum(isinstance(n, (ast.If, ast.Match, ast.Try)) for n in ast.walk(tree)),
        "loop_count": sum(isinstance(n, (ast.For, ast.While, ast.AsyncFor)) for n in ast.walk(tree)),
        "call_count": sum(isinstance(n, ast.Call) for n in ast.walk(tree)),
        "assignment_count": sum(isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)) for n in ast.walk(tree)),
    }


def score_semantic_signals(text: str, path: str) -> dict[str, dict[str, Any]]:
    lowered = f"{path}\n{text[:12000]}".lower()
    scores: dict[str, dict[str, Any]] = {}

    for signal_name, signal in SEMANTIC_SIGNALS.items():
        matches = [kw for kw in signal["keywords"] if kw in lowered]
        score = len(matches)
        scores[signal_name] = {
            "score": score,
            "matches": matches,
            "subsystem_hint": signal["subsystem_hint"],
            "role_hint": signal["role_hint"],
        }

    return scores


def choose_semantic_classification(
    existing_meta: dict[str, Any],
    signals: dict[str, dict[str, Any]],
    shape: dict[str, int],
) -> dict[str, Any]:
    best_signal_name = "unknown"
    best_signal = {"score": 0, "subsystem_hint": existing_meta.get("subsystem"), "role_hint": existing_meta.get("role")}

    for name, signal in signals.items():
        if signal["score"] > best_signal["score"]:
            best_signal_name = name
            best_signal = signal

    existing_subsystem = existing_meta.get("subsystem") or "unclassified"
    existing_role = existing_meta.get("role") or "module"

    semantic_subsystem = existing_subsystem
    semantic_role = existing_role
    classification_reason = "existing_metadata_retained"

    if best_signal["score"] >= 2:
        semantic_subsystem = best_signal["subsystem_hint"]
        semantic_role = best_signal["role_hint"]
        classification_reason = f"semantic_signal:{best_signal_name}"

    if shape["class_count"] >= 1 and semantic_role == "module":
        semantic_role = "controller"
        classification_reason += "|class_structure_detected"

    if shape["function_count"] >= 3 and semantic_role == "module":
        semantic_role = "controller"
        classification_reason += "|function_cluster_detected"

    confidence = int(existing_meta.get("confidence", 0)) + int(best_signal["score"]) + min(shape["function_count"], 5)

    return {
        "semantic_subsystem": semantic_subsystem,
        "semantic_role": semantic_role,
        "semantic_owner": semantic_subsystem if semantic_subsystem != "unclassified" else semantic_role,
        "semantic_confidence": confidence,
        "dominant_signal": best_signal_name,
        "classification_reason": classification_reason,
    }


def build_semantic_classification(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root).resolve()
    database = build_repository_knowledge_database(root_path)

    semantic_files: dict[str, dict[str, Any]] = {}

    changed_subsystem_count = 0
    changed_role_count = 0
    enriched_count = 0

    for path, meta in database["files"].items():
        text = _read_text(root_path, path)
        shape = _ast_shape(text) if Path(path).suffix == ".py" else {
            "function_count": 0,
            "class_count": 0,
            "branch_count": 0,
            "loop_count": 0,
            "call_count": 0,
            "assignment_count": 0,
        }

        signals = score_semantic_signals(text, path)
        semantic = choose_semantic_classification(meta, signals, shape)

        if semantic["semantic_subsystem"] != meta.get("subsystem"):
            changed_subsystem_count += 1
        if semantic["semantic_role"] != meta.get("role"):
            changed_role_count += 1
        if semantic["dominant_signal"] != "unknown":
            enriched_count += 1

        semantic_files[path] = {
            "path": path,
            "original_layer": meta.get("layer"),
            "original_subsystem": meta.get("subsystem"),
            "original_role": meta.get("role"),
            "semantic_subsystem": semantic["semantic_subsystem"],
            "semantic_role": semantic["semantic_role"],
            "semantic_owner": semantic["semantic_owner"],
            "semantic_confidence": semantic["semantic_confidence"],
            "dominant_signal": semantic["dominant_signal"],
            "classification_reason": semantic["classification_reason"],
            "ast_shape": shape,
            "signal_scores": signals,
        }

    return {
        "schema": SCHEMA,
        "database_schema": database["schema"],
        "metadata_schema": database["metadata_schema"],
        "summary": {
            "file_count": len(semantic_files),
            "semantic_enriched_files": enriched_count,
            "changed_subsystem_count": changed_subsystem_count,
            "changed_role_count": changed_role_count,
            "signal_count": len(SEMANTIC_SIGNALS),
        },
        "files": semantic_files,
    }


def write_semantic_classification(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/repository_semantic_classification_v1.json",
) -> dict[str, Any]:
    result = build_semantic_classification(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = write_semantic_classification(".")
    summary = result["summary"]

    print("LEAF_REPOSITORY_SEMANTIC_CLASSIFICATION_ENGINE")
    print(f"schema={result['schema']}")
    print(f"file_count={summary['file_count']}")
    print(f"semantic_enriched_files={summary['semantic_enriched_files']}")
    print(f"changed_subsystem_count={summary['changed_subsystem_count']}")
    print(f"changed_role_count={summary['changed_role_count']}")
    print(f"signal_count={summary['signal_count']}")
