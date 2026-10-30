from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from datetime import datetime
import json
import shutil


@dataclass(frozen=True)
class AppliedReplacementFile:
    file: str
    backup: str
    replacements_applied: int
    post_replacement_remaining: int
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "backup": self.backup,
            "replacements_applied": self.replacements_applied,
            "post_replacement_remaining": self.post_replacement_remaining,
            "status": self.status,
        }


@dataclass(frozen=True)
class ControlledReplacementApplicationResult:
    status: str
    source_dry_run: str
    eligible_files_seen: int
    files_modified: int
    backups_created: int
    total_replacements_applied: int
    mutation_performed: bool
    applied_files: list[AppliedReplacementFile]
    blocked_reason: str | None
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source_dry_run": self.source_dry_run,
            "eligible_files_seen": self.eligible_files_seen,
            "files_modified": self.files_modified,
            "backups_created": self.backups_created,
            "total_replacements_applied": self.total_replacements_applied,
            "mutation_performed": self.mutation_performed,
            "applied_files": [item.to_dict() for item in self.applied_files],
            "blocked_reason": self.blocked_reason,
            "next_action": self.next_action,
        }


class ControlledReplacementApplication:
    """
    Applies only reviewed replacements from the 31I.4 dry-run manifest.

    This is intentionally narrow:
    - eligible files only
    - backups before write
    - no report/history paths
    - no broad pattern mutation
    """

    def __init__(self, root: Path, dry_run_json: Path):
        self.root = Path(root)
        self.dry_run_json = Path(dry_run_json)

    def load_eligible_plans(self) -> list[dict[str, Any]]:
        payload = json.loads(self.dry_run_json.read_text(encoding="utf-8"))
        plans = payload.get("dry_run", {}).get("plans", [])
        return [plan for plan in plans if plan.get("eligible")]

    def apply(self, max_files: int = 10, max_replacements: int = 50) -> ControlledReplacementApplicationResult:
        eligible_plans = self.load_eligible_plans()
        total_planned = sum(int(plan.get("total_replacements", 0)) for plan in eligible_plans)

        if len(eligible_plans) > max_files:
            return ControlledReplacementApplicationResult(
                status="BLOCKED",
                source_dry_run=str(self.dry_run_json.relative_to(self.root)),
                eligible_files_seen=len(eligible_plans),
                files_modified=0,
                backups_created=0,
                total_replacements_applied=0,
                mutation_performed=False,
                applied_files=[],
                blocked_reason=f"Eligible file count {len(eligible_plans)} exceeds max_files {max_files}.",
                next_action="Reduce candidate set before application.",
            )

        if total_planned > max_replacements:
            return ControlledReplacementApplicationResult(
                status="BLOCKED",
                source_dry_run=str(self.dry_run_json.relative_to(self.root)),
                eligible_files_seen=len(eligible_plans),
                files_modified=0,
                backups_created=0,
                total_replacements_applied=0,
                mutation_performed=False,
                applied_files=[],
                blocked_reason=f"Planned replacement count {total_planned} exceeds max_replacements {max_replacements}.",
                next_action="Reduce replacement set before application.",
            )

        applied: list[AppliedReplacementFile] = []

        for plan in eligible_plans:
            rel_file = plan["file"]
            path = self.root / rel_file

            original = path.read_text(encoding="utf-8")
            updated = original
            applied_count = 0

            for replacement_label, count in plan.get("planned_replacements", {}).items():
                old, new = replacement_label.split(" -> ", 1)
                applied_count += updated.count(old)
                updated = updated.replace(old, new)

            if updated == original:
                applied.append(
                    AppliedReplacementFile(
                        file=rel_file,
                        backup="",
                        replacements_applied=0,
                        post_replacement_remaining=sum(
                            updated.count(label.split(" -> ", 1)[0])
                            for label in plan.get("planned_replacements", {})
                        ),
                        status="NO_CHANGE",
                    )
                )
                continue

            backup = path.with_suffix(
                path.suffix + ".backup_before_phase_31i5_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            shutil.copy2(path, backup)
            path.write_text(updated, encoding="utf-8")

            remaining = sum(
                updated.count(label.split(" -> ", 1)[0])
                for label in plan.get("planned_replacements", {})
            )

            applied.append(
                AppliedReplacementFile(
                    file=rel_file,
                    backup=str(backup.relative_to(self.root)),
                    replacements_applied=applied_count,
                    post_replacement_remaining=remaining,
                    status="PASS" if remaining == 0 else "FAIL",
                )
            )

        files_modified = len([item for item in applied if item.status in {"PASS", "FAIL"}])
        backups_created = len([item for item in applied if item.backup])
        total_applied = sum(item.replacements_applied for item in applied)
        failed = [item for item in applied if item.status == "FAIL"]

        return ControlledReplacementApplicationResult(
            status="PASS" if applied and not failed else "FAIL",
            source_dry_run=str(self.dry_run_json.relative_to(self.root)),
            eligible_files_seen=len(eligible_plans),
            files_modified=files_modified,
            backups_created=backups_created,
            total_replacements_applied=total_applied,
            mutation_performed=files_modified > 0,
            applied_files=applied,
            blocked_reason=None,
            next_action="Run repository reference audit again to measure reduction.",
        )
