from __future__ import annotations

import ast
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


NON_OPERATIONAL_ROOTS = {
    "_leaf_artifacts",
    "_leaf_archive",
    "_external_repository_quarantine",
    "_leaf_legacy_quarantine",
    "_leaf_repository_cleanup_candidates",
}

TOOLING_EXCLUSIONS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}

EXCLUDED_DIRS = NON_OPERATIONAL_ROOTS | TOOLING_EXCLUSIONS


SUPPORTED_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".ui",
    ".qss",
}


@dataclass(frozen=True)
class RepositoryFileMetadata:
    path: str
    filename: str
    suffix: str
    layer: str
    subsystem: str
    role: str
    status: str
    source_class: str
    public_api_candidate: bool
    line_count: int
    size_bytes: int
    content_sha256: str
    imports: list[str]
    classes: list[str]
    functions: list[str]
    ast_parse_status: str
    ast_error: str | None
    confidence: int
    classification_source: str


def is_excluded(root: Path, path: Path) -> bool:
    rel = path.relative_to(root)
    return any(part in EXCLUDED_DIRS for part in rel.parts)


def iter_supported_files(root: str | Path) -> list[Path]:
    """
    Enumerate the current repository for canonical Repository Intelligence.

    Historical repository snapshots remain valid historical evidence, but
    they must not define the current architectural state.

    Directory pruning happens before traversal so virtual environments,
    archives, quarantine roots and generated build trees are never scanned
    unnecessarily.
    """
    root_path = Path(root).resolve()
    files: list[Path] = []

    for current_root, dirnames, filenames in os.walk(
        root_path,
        topdown=True,
    ):
        current = Path(current_root)

        # Prune excluded trees before os.walk descends into them.
        dirnames[:] = sorted(
            dirname
            for dirname in dirnames
            if dirname not in EXCLUDED_DIRS
        )

        for filename in filenames:
            path = current / filename

            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue

            if is_excluded(root_path, path):
                continue

            files.append(path)

    return sorted(files)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def classify_layer(relative_path: str, suffix: str) -> str:
    if relative_path.startswith("leaf_qt/"):
        return "runtime"
    if relative_path.startswith("project_maintenance/"):
        return "development"
    if relative_path.startswith("tests/") or "/tests/" in relative_path:
        return "test"
    if suffix in {".md", ".txt"}:
        return "documentation"
    return "unclassified"


def keyword_score(text: str, keywords: dict[str, list[str]]) -> dict[str, int]:
    lowered = text.lower()
    return {
        name: sum(1 for word in words if word.lower() in lowered)
        for name, words in keywords.items()
    }


SUBSYSTEM_KEYWORDS = {
    "regen": ["regen", "coolant", "channel", "thermal", "heat", "wall"],
    "materials": ["material", "alloy", "conductivity", "density", "strength"],
    "coatings": ["coating", "liner", "barrier", "bondcoat"],
    "solver": ["solver", "cea", "nozzle", "flow", "combustion", "performance"],
    "ui": ["window", "viewer", "widget", "dialog", "panel", "canvas", "qt"],
    "validation": ["validation", "validate", "gate", "audit", "sanity"],
    "reports": ["report", "certificate", "summary", "export"],
    "optimisation": ["optimisation", "optimization", "candidate", "ranking", "selection"],
    "history": ["history", "iteration", "timeline", "record"],
    "registry": ["registry", "register", "variable"],
    "repository_architecture": ["repository", "architecture", "sorter", "classifier", "metadata", "dependency"],
}


ROLE_KEYWORDS = {
    "test": ["test_"],
    "owner": ["owner"],
    "controller": ["controller"],
    "solver": ["solver", "calculate", "compute"],
    "viewer": ["viewer", "window", "canvas", "widget", "dialog"],
    "validator": ["validation", "validate", "gate", "audit", "sanity"],
    "reporter": ["report", "certificate", "summary"],
    "registry": ["registry", "register"],
    "database": ["database", "table", "catalogue", "catalog"],
    "maintenance": ["phase_", "project_maintenance", "migration", "repair", "patch"],
    "module": ["module"],
}


def best_score(scores: dict[str, int], fallback: str) -> str:
    if not scores:
        return fallback
    name, score = max(scores.items(), key=lambda item: item[1])
    return name if score > 0 else fallback


def parse_python(text: str, relative_path: str) -> tuple[list[str], list[str], list[str], str, str | None]:
    try:
        tree = ast.parse(text, filename=relative_path)
    except SyntaxError as exc:
        return [], [], [], "FAIL", f"{exc.__class__.__name__}: {exc}"

    imports: set[str] = set()
    classes: set[str] = set()
    functions: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(("." * node.level) + node.module)
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)

    return sorted(imports), sorted(classes), sorted(functions), "PASS", None


def classify_status(relative_path: str) -> str:
    lowered = relative_path.lower()
    if "deprecated" in lowered or "legacy" in lowered:
        return "deprecated"
    if "test_" in Path(relative_path).name.lower():
        return "test"
    if relative_path.startswith("project_maintenance/"):
        return "development"
    if relative_path.startswith("leaf_qt/"):
        return "production_candidate"
    return "unknown"


def classify_source_class(relative_path: str, suffix: str) -> str:
    """Classify architectural use independently of engineering subsystem."""
    path = relative_path.replace("\\", "/")
    lowered = path.lower()

    parts = Path(lowered).parts
    name = Path(lowered).name

    if any(part in NON_OPERATIONAL_ROOTS for part in parts):
        return "non_operational"

    if (
        lowered.startswith("tests/")
        or "/tests/" in lowered
        or name.startswith("test_")
    ):
        return "test"

    if lowered.startswith("leaf_qt/"):
        return "runtime"

    if lowered.startswith("project_maintenance/"):
        return "maintenance"

    if suffix in {".md", ".txt"}:
        return "documentation"

    return "support"


def build_file_metadata(root: str | Path, path: str | Path) -> RepositoryFileMetadata:
    root_path = Path(root).resolve()
    file_path = Path(path).resolve()
    relative_path = file_path.relative_to(root_path).as_posix()

    text = read_text(file_path)
    suffix = file_path.suffix.lower()
    line_count = text.count("\n") + (1 if text else 0)

    imports: list[str] = []
    classes: list[str] = []
    functions: list[str] = []
    ast_status = "NOT_PYTHON"
    ast_error = None

    if suffix == ".py":
        imports, classes, functions, ast_status, ast_error = parse_python(text, relative_path)

    combined = " ".join([
        relative_path,
        file_path.name.replace("_", " ").replace("-", " "),
        " ".join(imports),
        text[:4000],
    ])

    subsystem_scores = keyword_score(combined, SUBSYSTEM_KEYWORDS)
    role_scores = keyword_score(combined, ROLE_KEYWORDS)

    layer = classify_layer(relative_path, suffix)
    subsystem = best_score(subsystem_scores, "unclassified")
    role = best_score(role_scores, "module")

    confidence = (
        max(subsystem_scores.values() or [0])
        + max(role_scores.values() or [0])
        + (1 if layer != "unclassified" else 0)
        + (1 if ast_status in {"PASS", "NOT_PYTHON"} else 0)
    )

    public_api_candidate = bool(classes or functions) and not Path(relative_path).name.startswith("test_")

    return RepositoryFileMetadata(
        path=relative_path,
        filename=file_path.name,
        suffix=suffix,
        layer=layer,
        subsystem=subsystem,
        role=role,
        status=classify_status(relative_path),
        source_class=classify_source_class(relative_path, suffix),
        public_api_candidate=public_api_candidate,
        line_count=line_count,
        size_bytes=file_path.stat().st_size,
        content_sha256=sha256_text(text),
        imports=imports,
        classes=classes,
        functions=functions,
        ast_parse_status=ast_status,
        ast_error=ast_error,
        confidence=confidence,
        classification_source="repository_metadata_foundation_v1",
    )


def build_repository_metadata(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root).resolve()
    files = [build_file_metadata(root_path, path) for path in iter_supported_files(root_path)]

    layer_counts: dict[str, int] = {}
    subsystem_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    source_class_counts: dict[str, int] = {}

    for item in files:
        layer_counts[item.layer] = layer_counts.get(item.layer, 0) + 1
        subsystem_counts[item.subsystem] = subsystem_counts.get(item.subsystem, 0) + 1
        role_counts[item.role] = role_counts.get(item.role, 0) + 1
        status_counts[item.status] = status_counts.get(item.status, 0) + 1
        source_class_counts[item.source_class] = source_class_counts.get(item.source_class, 0) + 1

    ast_failures = [asdict(item) for item in files if item.ast_parse_status == "FAIL"]

    return {
        "schema": "LEAF_REPOSITORY_METADATA_V1",
        "root": str(root_path),
        "summary": {
            "supported_files": len(files),
            "python_files": sum(1 for item in files if item.suffix == ".py"),
            "public_api_candidates": sum(1 for item in files if item.public_api_candidate),
            "ast_parse_failures": len(ast_failures),
            "layer_counts": dict(sorted(layer_counts.items())),
            "subsystem_counts": dict(sorted(subsystem_counts.items())),
            "role_counts": dict(sorted(role_counts.items())),
            "status_counts": dict(sorted(status_counts.items())),
            "source_class_counts": dict(sorted(source_class_counts.items())),
            "excluded_non_operational_roots": sorted(NON_OPERATIONAL_ROOTS),
        },
        "files": [asdict(item) for item in files],
        "ast_parse_failures": ast_failures,
    }


def write_repository_metadata(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/repository_metadata_v1.json",
) -> dict[str, Any]:
    metadata = build_repository_metadata(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    result = write_repository_metadata(".")
    summary = result["summary"]

    print("LEAF_REPOSITORY_METADATA_FOUNDATION")
    print(f"schema={result['schema']}")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"public_api_candidates={summary['public_api_candidates']}")
    print(f"ast_parse_failures={summary['ast_parse_failures']}")

    if summary["ast_parse_failures"]:
        raise SystemExit(1)
