from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_knowledge_database import (
    build_repository_knowledge_database,
)

SCHEMA = "LEAF_REPOSITORY_DEPENDENCY_OWNERSHIP_GRAPH_V1"


CONSTITUTIONAL_ARCHITECTURE_OWNERS = {
    "repository_intelligence": {
        "state": "CONFIRMED",
        "domain": "project_maintenance/repository_architecture",
        "entrypoint": "project_maintenance/repository_architecture/repository_intelligence_api.py",
    },
    "module_detection": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/module_engine",
        "entrypoint": "leaf_qt/module_engine/module_discovery_engine.py",
    },
    "dependencies": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/module_engine",
        "entrypoint": "leaf_qt/module_engine/module_runtime_integrator.py",
        "scope": "engineering_module_dependencies",
    },
    "runtime": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/runtime",
        "entrypoint": "leaf_qt/runtime/session_lifecycle.py",
    },
    "storage": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/storage",
        "entrypoint": "leaf_qt/storage/canonical_storage.py",
    },
    "workflow": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/workflow",
        "entrypoint": "leaf_qt/workflow/registry.py",
    },
    "notifications": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/runtime",
        "entrypoint": "leaf_qt/runtime/notification_centre.py",
    },

    # These are deliberately NOT marked clean.
    # Repository evidence shows more than one architectural path.
    "reports": {
        "state": "CONFIRMED",
        "domain": "leaf_qt",
        "entrypoint": "leaf_qt/report_ownership.py",
        "scope": "report_content_and_composition",
        "reason": (
            "Report content and composition are owned by report_ownership.py. "
            "leaf_qt/runtime/report_router.py owns runtime message routing only "
            "and is therefore runtime transport, not a competing report owner."
        ),
    },
    "validation": {
        "state": "CONFIRMED",
        "domain": "leaf_qt/module_interface",
        "entrypoint": "leaf_qt/module_interface/validation_contract.py",
        "scope": "engineering_module_validation_infrastructure",
        "migration_state": "LEGACY_DOMAIN_VALIDATORS_REMAIN",
        "reason": (
            "The reusable EngineeringModuleValidationContract is the canonical "
            "owner of engineering-module validation infrastructure. "
            "Engineering-specific validators supply domain findings through "
            "this contract. Older pre-module validation implementations remain "
            "migration debt and are not competing constitutional owners."
        ),
    },
}


ARCHITECTURAL_RESPONSIBILITY_TOKENS = {
    "repository_intelligence": (
        "repository_intelligence",
        "repository_metadata",
        "repository_knowledge",
        "repository_architecture",
        "semantic_classification",
    ),
    "module_detection": (
        "module_discovery",
        "module_definition_loader",
        "module_definition_registry",
    ),
    "dependencies": (
        "dependency",
        "dependencies",
    ),
    "validation": (
        "validation",
        "validator",
    ),
    "reports": (
        "report_router",
        "report_owner",
        "report_engine",
    ),
    "runtime": (
        "runtime",
        "event_bus",
        "state_registry",
        "undo_redo",
    ),
    "storage": (
        "storage",
        "manifest",
        "project_store",
        "design_store",
    ),
    "workflow": (
        "workflow",
        "execution_context",
        "progress_tracker",
    ),
    "notifications": (
        "notification",
        "notifications",
    ),
}


INFRASTRUCTURE_DOMAINS = (
    "leaf_qt/runtime/",
    "leaf_qt/storage/",
    "leaf_qt/workflow/",
    "leaf_qt/module_engine/",
    "leaf_qt/module_interface/",
    "leaf_qt/core/architecture/",
    "leaf_qt/standardisation/",
    "project_maintenance/repository_architecture/",
)

CANONICAL_ROOT_INFRASTRUCTURE_FILES = {
    "leaf_qt/report_ownership.py",
}


def architectural_domain(path: str) -> str:
    """Return the stable architectural domain containing a file."""
    normalised = path.replace("\\", "/")

    for domain in INFRASTRUCTURE_DOMAINS:
        if normalised.startswith(domain):
            return domain.rstrip("/")

    if normalised in CANONICAL_ROOT_INFRASTRUCTURE_FILES:
        return str(Path(normalised).parent)

    if normalised.startswith("leaf_qt/"):
        return "leaf_qt/domain_code"

    if normalised.startswith("project_maintenance/"):
        return "project_maintenance/domain_code"

    return "repository/support"


def ownership_relationship(
    path: str,
    file_meta: dict[str, Any],
) -> str:
    """
    Distinguish ownership from contracts, adapters, consumers and maintenance.

    A file mentioning an architectural concept is not automatically an owner.
    """
    normalised = path.replace("\\", "/")
    lowered = normalised.lower()
    name = Path(lowered).name

    source_class = file_meta.get("source_class")

    if source_class == "test" or name.startswith("test_"):
        return "test"

    if source_class == "non_operational":
        return "historical"

    if source_class == "maintenance":
        if normalised.startswith(
            "project_maintenance/repository_architecture/"
        ):
            return "owner_candidate"
        return "maintenance"

    if (
        "_contract.py" in name
        or name.endswith("contract.py")
    ):
        return "contract"

    if any(
        token in name
        for token in (
            "_binding_",
            "_binding.py",
            "_adapter.py",
            "_bridge.py",
            "_integration_",
            "_registration_",
        )
    ):
        return "adapter"

    if normalised.startswith(INFRASTRUCTURE_DOMAINS):
        return "owner_candidate"

    if normalised in CANONICAL_ROOT_INFRASTRUCTURE_FILES:
        return "owner_candidate"

    return "consumer"


def infer_architectural_responsibilities(
    path: str,
    file_meta: dict[str, Any],
) -> list[str]:
    """Return infrastructure responsibilities evidenced by this file."""
    searchable = " ".join(
        [
            path,
            str(file_meta.get("subsystem", "")),
            str(file_meta.get("role", "")),
            " ".join(file_meta.get("classes", [])),
            " ".join(file_meta.get("functions", [])),
        ]
    ).lower()

    matches = [
        responsibility
        for responsibility, tokens
        in ARCHITECTURAL_RESPONSIBILITY_TOKENS.items()
        if any(token in searchable for token in tokens)
    ]

    return sorted(set(matches))


def infer_owner(file_meta: dict[str, Any]) -> str:
    subsystem = file_meta.get("subsystem") or "unclassified"
    role = file_meta.get("role") or "module"
    layer = file_meta.get("layer") or "unclassified"

    if subsystem != "unclassified":
        return subsystem

    if role in {"validator", "reporter", "registry", "solver", "viewer", "owner", "controller"}:
        return role

    return layer


def normalise_import_to_candidates(import_name: str) -> list[str]:
    cleaned = import_name.lstrip(".")
    if not cleaned:
        return []

    parts = cleaned.split(".")
    candidates = []

    for i in range(len(parts), 0, -1):
        candidates.append("/".join(parts[:i]) + ".py")
        candidates.append("/".join(parts[:i]) + "/__init__.py")

    return candidates


def resolve_import(import_name: str, known_paths: set[str]) -> str | None:
    for candidate in normalise_import_to_candidates(import_name):
        if candidate in known_paths:
            return candidate

        leaf_candidate = f"leaf_qt/{candidate}"
        if leaf_candidate in known_paths:
            return leaf_candidate

        maintenance_candidate = f"project_maintenance/{candidate}"
        if maintenance_candidate in known_paths:
            return maintenance_candidate

    return None


def build_dependency_ownership_graph(root: str | Path = ".") -> dict[str, Any]:
    database = build_repository_knowledge_database(root)
    files = database["files"]
    known_paths = set(files)

    file_nodes: dict[str, dict[str, Any]] = {}
    owner_nodes: dict[str, dict[str, Any]] = {}
    subsystem_nodes: dict[str, dict[str, Any]] = {}
    dependency_edges: list[dict[str, str]] = []
    unresolved_import_edges: list[dict[str, str]] = []

    for path, meta in files.items():
        owner = infer_owner(meta)
        subsystem = meta.get("subsystem") or "unclassified"

        file_nodes[path] = {
            "path": path,
            "layer": meta.get("layer"),
            "source_class": meta.get("source_class"),
            "subsystem": subsystem,
            "role": meta.get("role"),
            "status": meta.get("status"),
            "owner": owner,
            "architectural_domain": architectural_domain(path),
            "ownership_relationship": ownership_relationship(path, meta),
            "architectural_responsibilities": (
                infer_architectural_responsibilities(path, meta)
            ),
            "public_api_candidate": meta.get("public_api_candidate"),
        }

        owner_nodes.setdefault(owner, {"owner": owner, "files": []})
        owner_nodes[owner]["files"].append(path)

        subsystem_nodes.setdefault(subsystem, {"subsystem": subsystem, "files": [], "owners": []})
        subsystem_nodes[subsystem]["files"].append(path)
        subsystem_nodes[subsystem]["owners"].append(owner)

        for imported in meta.get("imports", []):
            resolved = resolve_import(imported, known_paths)

            if resolved:
                dependency_edges.append({
                    "from": path,
                    "to": resolved,
                    "import": imported,
                    "type": "resolved_import",
                })
            else:
                unresolved_import_edges.append({
                    "from": path,
                    "import": imported,
                    "type": "unresolved_or_external_import",
                })

    for node in owner_nodes.values():
        node["files"] = sorted(set(node["files"]))
        node["file_count"] = len(node["files"])

    for node in subsystem_nodes.values():
        node["files"] = sorted(set(node["files"]))
        node["owners"] = sorted(set(node["owners"]))
        node["file_count"] = len(node["files"])
        node["owner_count"] = len(node["owners"])

    subsystem_dependency_edges: set[tuple[str, str]] = set()
    owner_dependency_edges: set[tuple[str, str]] = set()

    incoming_dependency_counts: dict[str, int] = {
        path: 0 for path in file_nodes
    }

    for edge in dependency_edges:
        incoming_dependency_counts[edge["to"]] = (
            incoming_dependency_counts.get(edge["to"], 0) + 1
        )

        source = file_nodes[edge["from"]]
        target = file_nodes[edge["to"]]

        source_subsystem = source["subsystem"] or "unclassified"
        target_subsystem = target["subsystem"] or "unclassified"

        source_owner = source["owner"] or "unclassified"
        target_owner = target["owner"] or "unclassified"

        if source_subsystem != target_subsystem:
            subsystem_dependency_edges.add((source_subsystem, target_subsystem))

        if source_owner != target_owner:
            owner_dependency_edges.add((source_owner, target_owner))


    responsibility_nodes: dict[str, dict[str, Any]] = {}

    for responsibility in ARCHITECTURAL_RESPONSIBILITY_TOKENS:
        candidates = []

        for path, node in file_nodes.items():
            if responsibility not in node["architectural_responsibilities"]:
                continue

            relationship = node.get(
                "ownership_relationship",
                "consumer",
            )

            # Only infrastructure providers compete for constitutional
            # ownership. Contracts, adapters, consumers, tests and
            # historical files remain visible as evidence but are not owners.
            if relationship != "owner_candidate":
                continue

            score = 0

            if node.get("public_api_candidate"):
                score += 2

            score += min(
                incoming_dependency_counts.get(path, 0),
                10,
            )

            filename = Path(path).name.lower()

            if responsibility.replace("_", "") in filename.replace("_", ""):
                score += 3

            candidates.append(
                {
                    "path": path,
                    "owner": node.get("owner"),
                    "architectural_domain": node.get(
                        "architectural_domain"
                    ),
                    "ownership_relationship": node.get(
                        "ownership_relationship"
                    ),
                    "source_class": node.get("source_class"),
                    "role": node.get("role"),
                    "incoming_dependencies": (
                        incoming_dependency_counts.get(path, 0)
                    ),
                    "public_api_candidate": bool(
                        node.get("public_api_candidate")
                    ),
                    "ownership_score": score,
                }
            )

        domain_candidates: dict[str, list[dict[str, Any]]] = {}

        for candidate in candidates:
            domain = str(
                candidate.get(
                    "architectural_domain",
                    "unknown",
                )
            )

            domain_candidates.setdefault(
                domain,
                [],
            ).append(candidate)

        candidates.sort(
            key=lambda item: (
                -item["ownership_score"],
                -item["incoming_dependencies"],
                item["path"],
            )
        )

        top_score = (
            candidates[0]["ownership_score"]
            if candidates
            else None
        )

        top_candidates = [
            item
            for item in candidates
            if item["ownership_score"] == top_score
        ] if candidates else []

        responsibility_nodes[responsibility] = {
            "responsibility": responsibility,
            "candidate_count": len(candidates),
            "candidate_domain_count": len(domain_candidates),
            "candidate_domains": {
                domain: {
                    "file_count": len(items),
                    "highest_score": max(
                        (
                            item["ownership_score"]
                            for item in items
                        ),
                        default=0,
                    ),
                    "files": [
                        item["path"]
                        for item in items
                    ],
                }
                for domain, items
                in sorted(domain_candidates.items())
            },
            "top_score": top_score,
            "top_candidate_count": len(top_candidates),
            "top_candidates": top_candidates,
            "candidates": candidates,
            "ownership_state": (
                "UNRESOLVED"
                if not candidates
                else
                "AMBIGUOUS"
                if len(top_candidates) > 1
                else
                "CANDIDATE_IDENTIFIED"
            ),
        }

    # Heuristic candidates above are diagnostic evidence only.
    # Constitutional ownership is explicit and auditable.
    known_paths = set(file_nodes)

    for responsibility, declaration in (
        CONSTITUTIONAL_ARCHITECTURE_OWNERS.items()
    ):
        node = responsibility_nodes.setdefault(
            responsibility,
            {
                "responsibility": responsibility,
                "candidate_count": 0,
                "candidate_domain_count": 0,
                "candidate_domains": {},
                "top_score": None,
                "top_candidate_count": 0,
                "top_candidates": [],
                "candidates": [],
            },
        )

        declared_state = declaration["state"]
        entrypoint = declaration.get("entrypoint")

        entrypoint_exists = (
            bool(entrypoint)
            and (Path.cwd() / entrypoint).is_file()
        )

        entrypoint_in_intelligence_graph = (
            bool(entrypoint)
            and entrypoint in known_paths
        )

        if (
            declared_state == "CONFIRMED"
            and not entrypoint_exists
        ):
            declared_state = "DECLARED_OWNER_MISSING"

        node["heuristic_state"] = node.get(
            "ownership_state",
            "UNRESOLVED",
        )

        node["ownership_state"] = declared_state
        node["canonical_owner"] = declaration.get("domain")
        node["canonical_entrypoint"] = entrypoint
        node["canonical_entrypoint_exists"] = entrypoint_exists
        node["canonical_entrypoint_in_intelligence_graph"] = (
            entrypoint_in_intelligence_graph
        )
        node["declared_owners"] = declaration.get(
            "owners",
            [entrypoint] if entrypoint else [],
        )
        node["scope"] = declaration.get("scope")
        node["migration_state"] = declaration.get("migration_state")
        node["ownership_reason"] = declaration.get("reason")
        node["ownership_authority"] = "EXPLICIT_CONSTITUTIONAL_DECLARATION"

    ambiguous_responsibilities = sorted(
        responsibility
        for responsibility, node
        in responsibility_nodes.items()
        if node["ownership_state"] in {
            "AMBIGUOUS",
            "SPLIT_OWNERSHIP",
        }
    )

    unresolved_responsibilities = sorted(
        responsibility
        for responsibility, node
        in responsibility_nodes.items()
        if node["ownership_state"] in {
            "UNRESOLVED",
            "DECLARED_OWNER_MISSING",
        }
    )

    confirmed_responsibilities = sorted(
        responsibility
        for responsibility, node
        in responsibility_nodes.items()
        if node["ownership_state"] == "CONFIRMED"
    )

    constitutional_gaps = sorted(
        responsibility
        for responsibility, node
        in responsibility_nodes.items()
        if node["ownership_state"] != "CONFIRMED"
    )

    graph = {
        "schema": SCHEMA,
        "database_schema": database["schema"],
        "metadata_schema": database["metadata_schema"],
        "summary": {
            "file_nodes": len(file_nodes),
            "owner_nodes": len(owner_nodes),
            "subsystem_nodes": len(subsystem_nodes),
            "resolved_dependency_edges": len(dependency_edges),
            "unresolved_or_external_import_edges": len(unresolved_import_edges),
            "subsystem_dependency_edges": len(subsystem_dependency_edges),
            "owner_dependency_edges": len(owner_dependency_edges),
            "architectural_responsibilities": len(responsibility_nodes),
            "ambiguous_architectural_responsibilities": len(
                ambiguous_responsibilities
            ),
            "unresolved_architectural_responsibilities": len(
                unresolved_responsibilities
            ),
            "confirmed_architectural_responsibilities": len(
                confirmed_responsibilities
            ),
            "constitutional_ownership_gaps": len(
                constitutional_gaps
            ),
        },
        "files": file_nodes,
        "owners": dict(sorted(owner_nodes.items())),
        "subsystems": dict(sorted(subsystem_nodes.items())),
        "architectural_responsibilities": dict(
            sorted(responsibility_nodes.items())
        ),
        "ambiguous_architectural_responsibilities": (
            ambiguous_responsibilities
        ),
        "unresolved_architectural_responsibilities": (
            unresolved_responsibilities
        ),
        "confirmed_architectural_responsibilities": (
            confirmed_responsibilities
        ),
        "constitutional_ownership_gaps": constitutional_gaps,
        "dependency_edges": sorted(dependency_edges, key=lambda edge: (edge["from"], edge["to"], edge["import"])),
        "unresolved_or_external_import_edges": sorted(unresolved_import_edges, key=lambda edge: (edge["from"], edge["import"])),
        "subsystem_dependency_edges": [
            {"from": source, "to": target}
            for source, target in sorted(subsystem_dependency_edges)
        ],
        "owner_dependency_edges": [
            {"from": source, "to": target}
            for source, target in sorted(owner_dependency_edges)
        ],
    }

    return graph


def write_dependency_ownership_graph(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/repository_dependency_ownership_graph_v1.json",
) -> dict[str, Any]:
    graph = build_dependency_ownership_graph(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return graph


if __name__ == "__main__":
    graph = write_dependency_ownership_graph(".")
    summary = graph["summary"]

    print("LEAF_REPOSITORY_DEPENDENCY_OWNERSHIP_GRAPH")
    print(f"schema={graph['schema']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"unresolved_or_external_import_edges={summary['unresolved_or_external_import_edges']}")
    print(f"subsystem_dependency_edges={summary['subsystem_dependency_edges']}")
    print(f"owner_dependency_edges={summary['owner_dependency_edges']}")
