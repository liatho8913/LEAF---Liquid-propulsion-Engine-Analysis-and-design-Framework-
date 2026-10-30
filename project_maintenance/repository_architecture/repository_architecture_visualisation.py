from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_intelligence_api import (
    RepositoryIntelligenceAPI,
)

SCHEMA = "LEAF_REPOSITORY_ARCHITECTURE_VISUALISATION_V1"


def _top_items(mapping: dict[str, Any], limit: int = 20) -> list[dict[str, Any]]:
    rows = []
    for name, payload in mapping.items():
        rows.append({
            "name": name,
            "file_count": int(payload.get("file_count", len(payload.get("files", [])))),
            "owner_count": int(payload.get("owner_count", len(payload.get("owners", [])))),
        })
    return sorted(rows, key=lambda row: (-row["file_count"], row["name"]))[:limit]


def build_architecture_visualisation(root: str | Path = ".") -> dict[str, Any]:
    api = RepositoryIntelligenceAPI(root)
    graph = api.graph()
    summary = api.summary()

    subsystem_rows = _top_items(graph["subsystems"])
    owner_rows = _top_items(graph["owners"])

    subsystem_edges = graph["subsystem_dependency_edges"]
    owner_edges = graph["owner_dependency_edges"]

    mermaid_lines = [
        "flowchart TD",
        "    ROOT[LEAF Repository Intelligence]",
    ]

    for row in subsystem_rows[:12]:
        node = row["name"].replace("-", "_").replace(" ", "_")
        label = f"{row['name']} ({row['file_count']} files)"
        mermaid_lines.append(f"    ROOT --> {node}[{label}]")

    markdown_lines = [
        "# LEAF Repository Architecture Map",
        "",
        "## Summary",
        "",
        f"- Supported files: {summary['supported_files']}",
        f"- Python files: {summary['python_files']}",
        f"- File nodes: {summary['file_nodes']}",
        f"- Owner nodes: {summary['owner_nodes']}",
        f"- Subsystem nodes: {summary['subsystem_nodes']}",
        f"- Resolved dependency edges: {summary['resolved_dependency_edges']}",
        f"- Architecture errors: {summary['architecture_errors']}",
        f"- Architecture warnings: {summary['architecture_warnings']}",
        f"- Semantic enriched files: {summary['semantic_enriched_files']}",
        "",
        "## Top Subsystems",
        "",
        "| Subsystem | Files | Owners |",
        "|---|---:|---:|",
    ]

    for row in subsystem_rows:
        markdown_lines.append(f"| {row['name']} | {row['file_count']} | {row['owner_count']} |")

    markdown_lines.extend([
        "",
        "## Top Owners",
        "",
        "| Owner | Files |",
        "|---|---:|",
    ])

    for row in owner_rows:
        markdown_lines.append(f"| {row['name']} | {row['file_count']} |")

    markdown_lines.extend([
        "",
        "## Mermaid Overview",
        "",
        "```mermaid",
        *mermaid_lines,
        "```",
        "",
    ])

    return {
        "schema": SCHEMA,
        "api_schema": summary["schema"],
        "summary": summary,
        "top_subsystems": subsystem_rows,
        "top_owners": owner_rows,
        "subsystem_dependency_edge_count": len(subsystem_edges),
        "owner_dependency_edge_count": len(owner_edges),
        "mermaid": "\n".join(mermaid_lines),
        "markdown": "\n".join(markdown_lines),
    }


def write_architecture_visualisation(
    root: str | Path = ".",
    output_dir: str | Path = "_leaf_artifacts/repository_architecture/architecture_visualisation",
) -> dict[str, Any]:
    result = build_architecture_visualisation(root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "repository_architecture_visualisation_v1.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )
    (out / "repository_architecture_map.md").write_text(
        result["markdown"],
        encoding="utf-8",
    )
    (out / "repository_architecture_map.mmd").write_text(
        result["mermaid"],
        encoding="utf-8",
    )

    return result


if __name__ == "__main__":
    result = write_architecture_visualisation(".")
    summary = result["summary"]

    print("LEAF_REPOSITORY_ARCHITECTURE_VISUALISATION")
    print(f"schema={result['schema']}")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"subsystems={summary['subsystem_nodes']}")
    print(f"owners={summary['owner_nodes']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"top_subsystems={len(result['top_subsystems'])}")
    print(f"top_owners={len(result['top_owners'])}")
