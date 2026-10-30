from __future__ import annotations

from leaf_qt.core.architecture.repository_metadata import iter_supported_files
import ast
import py_compile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_dependency_ownership_graph import architectural_domain


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "_leaf_artifacts",
    "_leaf_archive",
    "_external_repository_quarantine",
    "build",
    "dist",
}


GENERIC_ARCHITECTURAL_DOMAINS = {
    "leaf_qt/domain_code",
    "project_maintenance/domain_code",
    "repository/support",
}


def _source_structure(path: str) -> str:
    parts = Path(path).parts

    if path.startswith("leaf_qt/"):
        return (
            "FLAT_RUNTIME"
            if len(parts) == 2
            else "NESTED_RUNTIME"
        )

    if path.startswith("project_maintenance/"):
        return (
            "FLAT_DEVELOPMENT"
            if len(parts) == 2
            else "NESTED_DEVELOPMENT"
        )

    if path.startswith("tests/"):
        return "TEST_STRUCTURE"

    if path.startswith("docs/"):
        return "DOCUMENTATION_STRUCTURE"

    return "REPOSITORY_SUPPORT"


def apply_canonical_organisation_policy(
    item: dict,
) -> dict:
    """
    Apply LEAF's evidence-led organisation policy.

    Semantic classification may describe a file and
    suggest where similar functionality often lives.

    It does not authorise repository movement.

    Until positive ownership evidence proves that a
    file belongs elsewhere, the current location remains
    the canonical destination.
    """
    result = dict(item)

    path = Path(
        str(result["path"])
    ).as_posix()

    semantic_destination = Path(
        str(
            result.get(
                "proposed_destination",
                path,
            )
        )
    ).as_posix()

    domain = architectural_domain(path)
    structure = _source_structure(path)

    explicit_domain = (
        domain
        not in GENERIC_ARCHITECTURAL_DOMAINS
    )

    result.update(
        {
            "semantic_proposed_destination":
                semantic_destination,
            "proposed_destination":
                path,
            "canonical_domain":
                domain
                if explicit_domain
                else None,
            "existing_structure":
                structure,
            "movement_authorised":
                False,
            "already_in_proposed_location":
                True,
        }
    )

    if semantic_destination == path:
        result.update(
            {
                "placement_authority":
                    "CURRENT_STRUCTURE",
                "organisation_action":
                    "ALIGNED",
                "placement_reason":
                    "Current path already matches "
                    "the semantic destination hint.",
                "placement_evidence": [
                    "current_path_matches_semantic_hint",
                ],
            }
        )

        return result

    if explicit_domain:
        result.update(
            {
                "placement_authority":
                    "ARCHITECTURAL_DOMAIN",
                "organisation_action":
                    "PROTECTED",
                "placement_reason":
                    "Explicit architectural ownership "
                    "outranks semantic destination hints.",
                "placement_evidence": [
                    f"architectural_domain:{domain}",
                    (
                        "semantic_hint:"
                        f"{semantic_destination}"
                    ),
                ],
            }
        )

        return result

    if structure in {
        "NESTED_RUNTIME",
        "NESTED_DEVELOPMENT",
    }:
        result.update(
            {
                "placement_authority":
                    "EXISTING_PACKAGE_STRUCTURE",
                "organisation_action":
                    "PROTECTED",
                "placement_reason":
                    "Existing package placement is "
                    "architectural evidence. No positive "
                    "ownership evidence authorises exit.",
                "placement_evidence": [
                    (
                        "existing_parent:"
                        f"{Path(path).parent.as_posix()}"
                    ),
                    (
                        "semantic_hint:"
                        f"{semantic_destination}"
                    ),
                ],
            }
        )

        return result

    if structure in {
        "TEST_STRUCTURE",
        "DOCUMENTATION_STRUCTURE",
        "REPOSITORY_SUPPORT",
    }:
        result.update(
            {
                "placement_authority":
                    "EXISTING_REPOSITORY_STRUCTURE",
                "organisation_action":
                    "PROTECTED",
                "placement_reason":
                    "Support, test, and documentation "
                    "structure is preserved unless a "
                    "dedicated policy proves relocation.",
                "placement_evidence": [
                    f"existing_structure:{structure}",
                    (
                        "semantic_hint:"
                        f"{semantic_destination}"
                    ),
                ],
            }
        )

        return result

    result.update(
        {
            "placement_authority":
                "SEMANTIC_HINT_ONLY",
            "organisation_action":
                "MANUAL_REVIEW_REQUIRED",
            "placement_reason":
                "The flat runtime/development file has "
                "a semantic destination hint but lacks "
                "positive ownership evidence authorising "
                "movement.",
            "placement_evidence": [
                (
                    "semantic_hint:"
                    f"{semantic_destination}"
                ),
                "positive_ownership_evidence_missing",
            ],
        }
    )

    return result


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


SUBSYSTEM_RULES = {
    "regen": ["regen", "coolant", "channel", "thermal", "heat_flux", "wall_temperature"],
    "materials": ["material", "alloy", "property", "conductivity", "density"],
    "coatings": ["coating", "liner", "barrier", "bondcoat"],
    "ui": ["window", "viewer", "widget", "dialog", "panel", "canvas", "qt"],
    "reports": ["report", "certificate", "summary", "export"],
    "validation": ["validation", "validate", "gate", "audit", "sanity"],
    "optimisation": ["optimisation", "optimization", "candidate", "ranking", "selection"],
    "history": ["history", "iteration", "timeline", "record"],
    "registry": ["registry", "register", "variable"],
    "solver": ["solver", "cea", "nozzle", "flow", "combustion", "performance"],
    "repository_architecture": ["repository", "architecture", "organiser", "organizer", "sorter", "classifier", "movement"],
}


ROLE_RULES = {
    "owner": ["owner"],
    "controller": ["controller"],
    "solver": ["solver", "calculate", "compute"],
    "viewer": ["viewer", "window", "canvas", "widget", "dialog"],
    "validator": ["validation", "validate", "gate", "audit", "sanity"],
    "reporter": ["report", "certificate", "summary"],
    "registry": ["registry", "register"],
    "test": ["test_"],
    "maintenance": ["phase_", "project_maintenance", "migration", "repair", "patch"],
}


@dataclass(frozen=True)
class RepositoryClassification:
    path: str
    filename: str
    suffix: str
    layer: str
    subsystem: str
    role: str
    confidence: int
    imports: list[str]
    subsystem_scores: dict[str, int]
    role_scores: dict[str, int]
    proposed_destination: str
    already_in_proposed_location: bool


@dataclass(frozen=True)
class SorterMove:
    move_id: str
    from_path: str
    to_path: str
    layer: str
    subsystem: str
    role: str
    confidence: int


def is_excluded(root: Path, path: Path) -> bool:
    return bool(set(path.relative_to(root).parts) & EXCLUDED_DIRS)


def active_files(root: Path) -> list[Path]:
    return [
        path
        for path in iter_supported_files(root)
        if path.suffix.lower() in SUPPORTED_SUFFIXES
        and not is_excluded(root, path)
    ]


def active_python_files(root: Path) -> list[Path]:
    return [path for path in active_files(root) if path.suffix == ".py"]


def compile_active_python(root: Path) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []
    for path in active_python_files(root):
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            failures.append({"path": str(path.relative_to(root)), "error": repr(exc)})
    return failures


def safe_read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def imports_for(path: Path) -> list[str]:
    if path.suffix != ".py":
        return []

    try:
        tree = ast.parse(safe_read(path))
    except SyntaxError:
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return sorted(set(imports))


def score_rules(text: str, rules: dict[str, list[str]]) -> dict[str, int]:
    lower = text.lower()
    scores: dict[str, int] = {}

    for name, needles in rules.items():
        scores[name] = sum(1 for needle in needles if needle.lower() in lower)

    return scores


def best_score(scores: dict[str, int], fallback: str) -> str:
    if not scores:
        return fallback

    best_name, best_value = max(scores.items(), key=lambda item: item[1])
    return best_name if best_value > 0 else fallback


def classify_layer(path: Path, rel: str) -> str:
    if rel.startswith("project_maintenance/"):
        return "development"
    if rel.startswith("leaf_qt/"):
        return "runtime"
    if path.name.startswith("test_") or "/tests/" in rel:
        return "test"
    if path.suffix.lower() in {".md", ".txt"}:
        return "documentation"
    return "unclassified"


def proposed_destination(path: Path, classification: dict[str, Any]) -> str:
    rel = classification["path"]
    subsystem = classification["subsystem"]
    role = classification["role"]

    if rel.startswith("leaf_qt/"):
        if subsystem == "ui":
            return f"leaf_qt/ui/{role}/{path.name}"
        if subsystem in {"regen", "materials", "coatings", "solver", "optimisation", "validation", "reports", "history", "registry"}:
            return f"leaf_qt/{subsystem}/{role}/{path.name}"
        return f"leaf_qt/unclassified/{path.name}"

    if rel.startswith("project_maintenance/"):
        if subsystem == "repository_architecture":
            return f"project_maintenance/repository_architecture/{role}/{path.name}"
        return f"project_maintenance/{subsystem}/{role}/{path.name}"

    if classification["layer"] == "documentation":
        return f"docs/{subsystem}/{path.name}"

    if classification["layer"] == "test":
        return f"tests/{subsystem}/{path.name}"

    return f"_external_repository_quarantine/unclassified/{path.name}"


def classify_file(root: Path, path: Path) -> RepositoryClassification:
    rel = str(path.relative_to(root))
    name_text = path.name.replace("_", " ").replace("-", " ")
    import_text = " ".join(imports_for(path))
    content_head = safe_read(path)[:4000] if path.suffix in {".py", ".md", ".txt"} else ""

    combined = " ".join([rel, name_text, import_text, content_head])

    subsystem_scores = score_rules(combined, SUBSYSTEM_RULES)
    role_scores = score_rules(combined, ROLE_RULES)

    layer = classify_layer(path, rel)
    subsystem = best_score(subsystem_scores, "unclassified")
    role = best_score(role_scores, "module")

    confidence = (
        max(subsystem_scores.values() or [0])
        + max(role_scores.values() or [0])
        + (1 if layer != "unclassified" else 0)
    )

    partial = {
        "path": rel,
        "layer": layer,
        "subsystem": subsystem,
        "role": role,
    }

    destination = proposed_destination(path, partial)

    return RepositoryClassification(
        path=rel,
        filename=path.name,
        suffix=path.suffix,
        layer=layer,
        subsystem=subsystem,
        role=role,
        confidence=confidence,
        imports=imports_for(path),
        subsystem_scores=subsystem_scores,
        role_scores=role_scores,
        proposed_destination=destination,
        already_in_proposed_location=(rel == destination),
    )


def _classify_repository_unconstrained(root: Path) -> list[dict[str, Any]]:
    return [asdict(classify_file(root, path)) for path in active_files(root)]


def classify_repository(root: str | Path = ".") -> list[dict]:
    """
    Classify the repository using one canonical placement policy.

    The pre-existing sorter remains responsible for classification evidence.
    Architectural-package precedence is applied exactly once here.
    """
    return [
        apply_canonical_organisation_policy(item)
        for item in _classify_repository_unconstrained(root)
    ]


def is_safe_movement_candidate(root: Path, item: dict[str, Any], min_confidence: int = 3) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    path = str(item.get("path", ""))
    proposed = str(item.get("proposed_destination", ""))
    confidence = int(item.get("confidence", 0))
    layer = item.get("layer")
    subsystem = item.get("subsystem")
    role = item.get("role")

    src = root / path
    dst = root / proposed

    if item.get("organisation_action") != "MOVE_CANDIDATE":
        reasons.append("movement_not_authorised_by_organisation_policy")
    if item.get("movement_authorised") is not True:
        reasons.append("positive_ownership_evidence_missing")

    if not path.endswith(".py"):
        reasons.append("not_python")
    if not src.exists():
        reasons.append("source_missing")
    if dst.exists():
        reasons.append("destination_exists")
    if item.get("already_in_proposed_location") is True:
        reasons.append("already_in_proposed_location")
    if confidence < min_confidence:
        reasons.append("confidence_below_threshold")
    if layer not in {"runtime", "development", "test"}:
        reasons.append("unsupported_layer")
    if subsystem == "unclassified":
        reasons.append("unclassified_subsystem")
    if role == "module":
        reasons.append("generic_role")
    if proposed.startswith("_external_repository_quarantine/"):
        reasons.append("quarantine_destination")
    if path.startswith("_leaf_artifacts/") or path.startswith("_leaf_archive/"):
        reasons.append("artifact_or_archive_source")
    if proposed.startswith("_leaf_artifacts/") or proposed.startswith("_leaf_archive/"):
        reasons.append("artifact_or_archive_destination")

    return len(reasons) == 0, reasons


def select_safe_moves(
    root: Path,
    classifications: list[dict[str, Any]],
    batch_size: int = 25,
    min_confidence: int = 3,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for item in classifications:
        if str(item.get("path", "")).endswith(".py") is False:
            continue
        if item.get("layer") not in {"runtime", "development", "test"}:
            continue
        if item.get("already_in_proposed_location") is True:
            continue

        safe, reasons = is_safe_movement_candidate(root, item, min_confidence=min_confidence)
        entry = {
            "path": item.get("path"),
            "proposed_destination": item.get("proposed_destination"),
            "layer": item.get("layer"),
            "subsystem": item.get("subsystem"),
            "role": item.get("role"),
            "confidence": item.get("confidence"),
            "imports": item.get("imports", []),
            "accepted": safe,
            "reasons": reasons,
        }

        if safe:
            accepted.append(entry)
        else:
            rejected.append(entry)

    accepted = sorted(
        accepted,
        key=lambda item: (
            item["layer"],
            item["subsystem"],
            item["role"],
            -int(item["confidence"]),
            item["path"],
        ),
    )

    selected = accepted[:batch_size]
    deferred = accepted[batch_size:]

    selected_moves = [
        {
            "move_id": f"sorter_engine_move_{index:04d}",
            "from": item["path"],
            "to": item["proposed_destination"],
            "layer": item["layer"],
            "subsystem": item["subsystem"],
            "role": item["role"],
            "confidence": item["confidence"],
        }
        for index, item in enumerate(selected, start=1)
    ]

    return selected_moves, deferred, rejected
