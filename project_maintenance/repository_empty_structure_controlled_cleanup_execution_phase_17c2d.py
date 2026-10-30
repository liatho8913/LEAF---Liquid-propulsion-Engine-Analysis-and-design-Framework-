from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


ROOT = Path(__file__).resolve().parents[1]

IN_MANIFEST = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c2c" / "repository_empty_structure_cleanup_approval_manifest_phase_17c2c.json"

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c2d"
OUT_TXT = OUT_DIR / "repository_empty_structure_controlled_cleanup_execution_phase_17c2d.txt"
OUT_JSON = OUT_DIR / "repository_empty_structure_controlled_cleanup_execution_phase_17c2d.json"
ROLLBACK_DIR = OUT_DIR / "rollback_snapshot"


def safe_resolve(relative_path: str) -> Path:
    target = (ROOT / relative_path).resolve()
    root = ROOT.resolve()

    if not str(target).startswith(str(root)):
        raise ValueError(f"Unsafe path outside repository root: {relative_path}")

    return target


def load_manifest() -> Dict[str, Any]:
    if not IN_MANIFEST.exists():
        raise FileNotFoundError(
            f"Missing approval manifest: {IN_MANIFEST.relative_to(ROOT)}"
        )

    return json.loads(IN_MANIFEST.read_text(encoding="utf-8"))


def is_empty_directory(path: Path) -> bool:
    return path.is_dir() and not any(path.iterdir())


def is_zero_byte_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size == 0


def snapshot_before_delete(path: Path, rel: str) -> str | None:
    if not path.exists():
        return None

    snapshot_path = ROLLBACK_DIR / rel
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    if path.is_file():
        shutil.copy2(path, snapshot_path)
        return str(snapshot_path.relative_to(ROOT))

    if path.is_dir():
        snapshot_path.mkdir(parents=True, exist_ok=True)
        return str(snapshot_path.relative_to(ROOT))

    return None


def execute_cleanup(manifest: Dict[str, Any]) -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ROLLBACK_DIR.mkdir(parents=True, exist_ok=True)

    approved = []
    skipped_unapproved = []
    skipped_missing = []
    skipped_safety = []
    deleted = []

    for item in manifest.get("delete_candidates", []):
        rel = item.get("path", "")
        kind = item.get("kind", "")
        approved_for_deletion = item.get("approved_for_deletion") is True

        if not approved_for_deletion:
            skipped_unapproved.append(
                {
                    "path": rel,
                    "kind": kind,
                    "reason": "not approved for deletion",
                }
            )
            continue

        approved.append(item)

        target = safe_resolve(rel)

        if not target.exists():
            skipped_missing.append(
                {
                    "path": rel,
                    "kind": kind,
                    "reason": "path no longer exists",
                }
            )
            continue

        if kind == "empty_directory" and not is_empty_directory(target):
            skipped_safety.append(
                {
                    "path": rel,
                    "kind": kind,
                    "reason": "directory is no longer empty",
                }
            )
            continue

        if kind == "zero_byte_file" and not is_zero_byte_file(target):
            skipped_safety.append(
                {
                    "path": rel,
                    "kind": kind,
                    "reason": "file is no longer zero-byte",
                }
            )
            continue

        rollback_snapshot = snapshot_before_delete(target, rel)

        if kind == "empty_directory":
            target.rmdir()
        elif kind == "zero_byte_file":
            target.unlink()
        else:
            skipped_safety.append(
                {
                    "path": rel,
                    "kind": kind,
                    "reason": "unknown cleanup kind",
                }
            )
            continue

        deleted.append(
            {
                "path": rel,
                "kind": kind,
                "rollback_snapshot": rollback_snapshot,
            }
        )

    result = {
        "phase": "17C.2D",
        "name": "Repository Empty Structure Controlled Cleanup Execution",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_manifest": str(IN_MANIFEST.relative_to(ROOT)),
        "policy": {
            "requires_approval_manifest": True,
            "only_deletes_approved_items": True,
            "deletes_unapproved_items": False,
            "validates_empty_directory_before_delete": True,
            "validates_zero_byte_file_before_delete": True,
            "creates_rollback_snapshot": True,
        },
        "counts": {
            "manifest_candidates": len(manifest.get("delete_candidates", [])),
            "approved_candidates": len(approved),
            "deleted": len(deleted),
            "skipped_unapproved": len(skipped_unapproved),
            "skipped_missing": len(skipped_missing),
            "skipped_safety": len(skipped_safety),
        },
        "deleted": deleted,
        "skipped_unapproved": skipped_unapproved,
        "skipped_missing": skipped_missing,
        "skipped_safety": skipped_safety,
        "rollback_dir": str(ROLLBACK_DIR.relative_to(ROOT)),
        "passed": (
            len(skipped_safety) == 0
            and len(skipped_missing) == 0
            and len(deleted) == len(approved)
        ),
    }

    return result


def write_report(result: Dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.2D",
        "REPOSITORY EMPTY STRUCTURE CONTROLLED CLEANUP EXECUTION",
        "=" * 62,
        "",
        f"input_manifest={result['input_manifest']}",
        f"rollback_dir={result['rollback_dir']}",
        "",
        "POLICY",
        "------",
    ]

    for key, value in result["policy"].items():
        lines.append(f"{key}={value}")

    lines += [
        "",
        "COUNTS",
        "------",
    ]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += [
        "",
        "DELETED",
        "-------",
    ]

    if result["deleted"]:
        for item in result["deleted"]:
            lines.append(
                f"{item['kind']} :: {item['path']} :: rollback={item['rollback_snapshot']}"
            )
    else:
        lines.append("none")

    lines += [
        "",
        "SKIPPED UNAPPROVED",
        "------------------",
    ]

    for item in result["skipped_unapproved"]:
        lines.append(f"{item['kind']} :: {item['path']} :: {item['reason']}")

    lines += [
        "",
        "SKIPPED SAFETY",
        "--------------",
    ]

    if result["skipped_safety"]:
        for item in result["skipped_safety"]:
            lines.append(f"{item['kind']} :: {item['path']} :: {item['reason']}")
    else:
        lines.append("none")

    lines += [
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C2D_EMPTY_STRUCTURE_CONTROLLED_CLEANUP_EXECUTION" if result["passed"] else "FAIL_PHASE_17C2D_EMPTY_STRUCTURE_CONTROLLED_CLEANUP_EXECUTION",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        "next_phase=17C.2E_REPOSITORY_EMPTY_STRUCTURE_CLOSEOUT_CERTIFICATE",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    manifest = load_manifest()
    result = execute_cleanup(manifest)
    write_report(result)

    print("PASS_PHASE_17C2D_EMPTY_STRUCTURE_CONTROLLED_CLEANUP_EXECUTION" if result["passed"] else "FAIL_PHASE_17C2D_EMPTY_STRUCTURE_CONTROLLED_CLEANUP_EXECUTION")
    print(f"manifest_candidates={result['counts']['manifest_candidates']}")
    print(f"approved_candidates={result['counts']['approved_candidates']}")
    print(f"deleted={result['counts']['deleted']}")
    print(f"skipped_unapproved={result['counts']['skipped_unapproved']}")
    print(f"skipped_missing={result['counts']['skipped_missing']}")
    print(f"skipped_safety={result['counts']['skipped_safety']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
