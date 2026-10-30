from __future__ import annotations

from leaf_qt.core.architecture.repository_metadata import iter_supported_files
import ast
import copy
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SCHEMA = "LEAF_DUPLICATE_FUNCTIONALITY_DETECTION_ENGINE_V1"

EXCLUDED_SCAN_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "_leaf_artifacts", "_leaf_archive", "_external_repository_quarantine",
    "_leaf_repository_cleanup_candidates", "project_evidence", "artifacts",
    "build", "dist",
}


@dataclass(frozen=True)
class FunctionSignature:
    path: str
    qualified_name: str
    start_line: int
    end_line: int
    line_count: int
    statement_count: int
    normalised_ast_sha256: str
    structural_sha256: str


class AstNormaliser(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        node.name = "FUNCTION"
        node.decorator_list = []
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        node.name = "ASYNC_FUNCTION"
        node.decorator_list = []
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        node.arg = "ARG"
        node.annotation = None
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        return ast.copy_location(ast.Name(id="NAME", ctx=node.ctx), node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        self.generic_visit(node)
        node.attr = "ATTR"
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        value = node.value
        if isinstance(value, str):
            replacement: object = "STR"
        elif isinstance(value, bool):
            replacement = "BOOL"
        elif isinstance(value, (int, float, complex)):
            replacement = "NUM"
        elif value is None:
            replacement = None
        else:
            replacement = "CONST"
        return ast.copy_location(ast.Constant(value=replacement), node)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def iter_active_python_files(root: Path) -> list[Path]:
    return [
        path
        for path in iter_supported_files(root)
        if path.suffix.lower() == ".py"
        and not any(
            part in EXCLUDED_SCAN_PARTS
            for part in path.relative_to(root).parts
        )
    ]


def line_count(node: ast.AST) -> int:
    start = int(getattr(node, "lineno", 0) or 0)
    end = int(getattr(node, "end_lineno", start) or start)
    return max(1, end - start + 1)


def statement_count(node: ast.AST) -> int:
    return sum(1 for child in ast.walk(node) if isinstance(child, ast.stmt))


def normalised_fingerprint(node: ast.AST) -> str:
    copied = copy.deepcopy(node)
    normalised = ast.fix_missing_locations(AstNormaliser().visit(copied))
    return sha(ast.dump(normalised, include_attributes=False))


def structural_fingerprint(node: ast.AST) -> str:
    return sha("|".join(type(child).__name__ for child in ast.walk(node)))


def extract_function_signatures(root: str | Path = ".", minimum_lines: int = 5) -> list[FunctionSignature]:
    root_path = Path(root).resolve()
    signatures: list[FunctionSignature] = []

    for path in iter_active_python_files(root_path):
        rel = path.relative_to(root_path).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=rel)
        except SyntaxError:
            continue

        class_stack: list[str] = []

        def visit(node: ast.AST) -> None:
            if isinstance(node, ast.ClassDef):
                class_stack.append(node.name)
                for child in node.body:
                    visit(child)
                class_stack.pop()
                return

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if line_count(node) >= minimum_lines:
                    qualified = ".".join([*class_stack, node.name]) if class_stack else node.name
                    signatures.append(
                        FunctionSignature(
                            path=rel,
                            qualified_name=qualified,
                            start_line=int(getattr(node, "lineno", 0) or 0),
                            end_line=int(getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0),
                            line_count=line_count(node),
                            statement_count=statement_count(node),
                            normalised_ast_sha256=normalised_fingerprint(node),
                            structural_sha256=structural_fingerprint(node),
                        )
                    )

                for child in node.body:
                    visit(child)
                return

            for child in ast.iter_child_nodes(node):
                visit(child)

        visit(tree)

    return signatures


def grouped(signatures: list[FunctionSignature], attr: str) -> dict[str, list[FunctionSignature]]:
    out: dict[str, list[FunctionSignature]] = defaultdict(list)
    for sig in signatures:
        out[getattr(sig, attr)].append(sig)
    return {key: value for key, value in out.items() if len(value) > 1}


def cross_file(items: list[FunctionSignature]) -> bool:
    return len({item.path for item in items}) > 1


def detect_duplicate_functionality(root: str | Path = ".", minimum_lines: int = 5) -> dict[str, Any]:
    root_path = Path(root).resolve()
    signatures = extract_function_signatures(root_path, minimum_lines=minimum_lines)

    high_confidence: list[dict[str, Any]] = []
    medium_confidence: list[dict[str, Any]] = []

    for evidence_hash, items in grouped(signatures, "normalised_ast_sha256").items():
        if not cross_file(items):
            continue
        high_confidence.append({
            "duplicate_type": "normalised_ast_duplicate",
            "confidence": "HIGH",
            "evidence_hash": evidence_hash,
            "function_count": len(items),
            "file_count": len({item.path for item in items}),
            "functions": [asdict(item) for item in sorted(items, key=lambda x: (x.path, x.start_line))],
            "recommendation": "Review for reusable shared helper or owner-level consolidation. Proof only; no deletion.",
        })

    high_hashes = {group["evidence_hash"] for group in high_confidence}

    for evidence_hash, items in grouped(signatures, "structural_sha256").items():
        if not cross_file(items):
            continue
        if any(item.normalised_ast_sha256 in high_hashes for item in items):
            continue
        if len(items) < 3:
            continue
        medium_confidence.append({
            "duplicate_type": "structural_similarity_cluster",
            "confidence": "MEDIUM",
            "evidence_hash": evidence_hash,
            "function_count": len(items),
            "file_count": len({item.path for item in items}),
            "functions": [asdict(item) for item in sorted(items, key=lambda x: (x.path, x.start_line))],
            "recommendation": "Manual review only. Similar structure is not removal proof.",
        })

    groups = high_confidence + medium_confidence

    return {
        "schema": SCHEMA,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "root": str(root_path),
        "mode": "PROOF_ONLY_NO_MOVE_NO_ARCHIVE_NO_DELETE",
        "summary": {
            "active_python_files_scanned": len(iter_active_python_files(root_path)),
            "function_signatures": len(signatures),
            "duplicate_group_count": len(groups),
            "high_confidence_group_count": len(high_confidence),
            "medium_confidence_group_count": len(medium_confidence),
            "affected_file_count": len({fn["path"] for group in groups for fn in group["functions"]}),
            "automatic_move_allowed": False,
            "automatic_archive_allowed": False,
            "automatic_delete_allowed": False,
        },
        "groups": groups,
        "safety_policy": {
            "move_allowed": False,
            "archive_allowed": False,
            "delete_allowed": False,
            "reason": "Phase 17C.10A is evidence generation only. Retirement requires later unused-file proof, archive-first retirement and delete eligibility gates.",
        },
    }


def write_duplicate_functionality_report(
    root: str | Path = ".",
    output_dir: str | Path = "_leaf_artifacts/repository_architecture/phase_17c10a",
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    out = root_path / output_dir
    out.mkdir(parents=True, exist_ok=True)

    result = detect_duplicate_functionality(root_path)
    json_path = out / "duplicate_functionality_detection_phase_17c10a.json"
    txt_path = out / "duplicate_functionality_detection_phase_17c10a.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.10A DUPLICATE FUNCTIONALITY DETECTION",
        "========================================================",
        f"schema={result['schema']}",
        f"mode={result['mode']}",
        f"active_python_files_scanned={result['summary']['active_python_files_scanned']}",
        f"function_signatures={result['summary']['function_signatures']}",
        f"duplicate_group_count={result['summary']['duplicate_group_count']}",
        f"high_confidence_group_count={result['summary']['high_confidence_group_count']}",
        f"medium_confidence_group_count={result['summary']['medium_confidence_group_count']}",
        f"affected_file_count={result['summary']['affected_file_count']}",
        f"automatic_move_allowed={result['summary']['automatic_move_allowed']}",
        f"automatic_archive_allowed={result['summary']['automatic_archive_allowed']}",
        f"automatic_delete_allowed={result['summary']['automatic_delete_allowed']}",
        "",
        "TOP_HIGH_CONFIDENCE_GROUPS",
    ]

    for index, group in enumerate(result["groups"][:25], start=1):
        files = sorted({fn["path"] for fn in group["functions"]})
        lines.append(f"{index}. confidence={group['confidence']} functions={group['function_count']} files={group['file_count']}")
        lines.extend(f"   - {file}" for file in files[:8])

    if not result["groups"]:
        lines.append("none")

    lines.extend([
        "",
        "completion_notice=PHASE_17C10A_COMPLETE_DUPLICATE_FUNCTIONALITY_DETECTION_ESTABLISHED",
        "next_phase=17C.10B_UNUSED_FILE_PROOF_ENGINE",
        f"json={json_path.relative_to(root_path)}",
    ])

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    result["artefacts"] = {
        "json": json_path.relative_to(root_path).as_posix(),
        "report": txt_path.relative_to(root_path).as_posix(),
    }
    return result


if __name__ == "__main__":
    payload = write_duplicate_functionality_report(".")
    summary = payload["summary"]
    print("PASS_DUPLICATE_FUNCTIONALITY_DETECTION_ENGINE")
    print(f"active_python_files_scanned={summary['active_python_files_scanned']}")
    print(f"function_signatures={summary['function_signatures']}")
    print(f"duplicate_group_count={summary['duplicate_group_count']}")
    print(f"high_confidence_group_count={summary['high_confidence_group_count']}")
    print(f"medium_confidence_group_count={summary['medium_confidence_group_count']}")
    print(f"affected_file_count={summary['affected_file_count']}")
    print(f"automatic_move_allowed={summary['automatic_move_allowed']}")
    print(f"automatic_archive_allowed={summary['automatic_archive_allowed']}")
    print(f"automatic_delete_allowed={summary['automatic_delete_allowed']}")
    print(f"report={payload['artefacts']['report']}")
    print(f"json={payload['artefacts']['json']}")
