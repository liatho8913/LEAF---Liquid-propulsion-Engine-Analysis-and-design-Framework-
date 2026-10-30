from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import shutil
from datetime import datetime


REPLACEMENT_MAP = {
    "manual_regen_platform_binding": "modular_engine_generated_architecture",
    "manual_combustion_chamber_platform_binding": "modular_engine_generated_architecture",
    "manual module registration": "module_engine_discovery",
    "manual_module_registration": "module_engine_discovery",
    "manual runtime binding": "module_runtime_integrator",
    "manual_runtime_binding": "module_runtime_integrator",
    "manual contract": "module_contract_builder",
    "manual_contract": "module_contract_builder",
}


ACTIVE_SOURCE_PREFIXES = (
    "leaf_qt/",
)

EXCLUDED_PATH_MARKERS = (
    "LEAF_Reports/",
    "project_maintenance/",
    "_leaf_repository_cleanup_candidates/",
    ".venv/",
    "venv/",
    ".git/",
    "__pycache__/",
)

ALLOWED_SUFFIXES = (
    ".py",
    ".json",
)


@dataclass(frozen=True)
class TargetedReplacementCandidate:
    file: str
    replacement_count: int
    replacements: dict[str, str]
    classification: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "replacement_count": self.replacement_count,
            "replacements": self.replacements,
            "classification": self.classification,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class TargetedReplacementResult:
    status: str
    mode: str
    source_plan: str
    candidate_count: int
    total_replacements: int
    files_modified: int
    backups_created: int
    mutation_performed: bool
    candidates: list[TargetedReplacementCandidate]
    blocked_reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mode": self.mode,
            "source_plan": self.source_plan,
            "candidate_count": self.candidate_count,
            "total_replacements": self.total_replacements,
            "files_modified": self.files_modified,
            "backups_created": self.backups_created,
            "mutation_performed": self.mutation_performed,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "blocked_reason": self.blocked_reason,
        }


class TargetedReferenceReplacer:
    """
    Controlled targeted replacement engine.

    Dry-run is the default.

    Apply mode must be explicit.

    The engine only touches active source/config files.
    It excludes reports, maintenance history, virtual environments, caches, and quarantine.
    """

    def __init__(self, root: Path, planning_json: Path):
        self.root = Path(root)
        self.planning_json = Path(planning_json)

    def load_plan_samples(self) -> list[dict[str, Any]]:
        payload = json.loads(self.planning_json.read_text(encoding="utf-8"))
        samples = payload.get("plan", {}).get("samples", {})
        return samples.get("safe_to_replace_candidate", [])

    def is_active_source_file(self, file: str) -> bool:
        if not file.startswith(ACTIVE_SOURCE_PREFIXES):
            return False

        if any(marker in file for marker in EXCLUDED_PATH_MARKERS):
            return False

        if Path(file).suffix not in ALLOWED_SUFFIXES:
            return False

        return True

    def build_candidates(self) -> list[TargetedReplacementCandidate]:
        samples = self.load_plan_samples()
        candidates: list[TargetedReplacementCandidate] = []

        seen_files: set[str] = set()

        for item in samples:
            file = item.get("file", "")

            if file in seen_files:
                continue
            seen_files.add(file)

            if not self.is_active_source_file(file):
                continue

            path = self.root / file
            if not path.exists() or not path.is_file():
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            replacements: dict[str, str] = {}
            replacement_count = 0

            for old, new in REPLACEMENT_MAP.items():
                count = text.count(old)
                if count:
                    replacements[old] = new
                    replacement_count += count

            if replacement_count:
                candidates.append(
                    TargetedReplacementCandidate(
                        file=file,
                        replacement_count=replacement_count,
                        replacements=replacements,
                        classification="active_source_targeted_candidate",
                        reason="File is active source/config and contains explicit replaceable manual architecture phrase.",
                    )
                )

        return candidates

    def apply_candidate(self, candidate: TargetedReplacementCandidate) -> bool:
        path = self.root / candidate.file
        original = path.read_text(encoding="utf-8")
        updated = original

        for old, new in candidate.replacements.items():
            updated = updated.replace(old, new)

        if updated == original:
            return False

        backup = path.with_suffix(
            path.suffix + ".backup_before_modular_reference_replacement_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        shutil.copy2(path, backup)
        path.write_text(updated, encoding="utf-8")
        return True

    def run(self, apply: bool = False, max_files: int = 25) -> TargetedReplacementResult:
        candidates = self.build_candidates()

        if len(candidates) > max_files and apply:
            return TargetedReplacementResult(
                status="BLOCKED",
                mode="apply",
                source_plan=str(self.planning_json.relative_to(self.root)),
                candidate_count=len(candidates),
                total_replacements=sum(candidate.replacement_count for candidate in candidates),
                files_modified=0,
                backups_created=0,
                mutation_performed=False,
                candidates=candidates,
                blocked_reason=f"Apply blocked because candidate count {len(candidates)} exceeds max_files {max_files}.",
            )

        files_modified = 0
        backups_created = 0

        if apply:
            for candidate in candidates:
                changed = self.apply_candidate(candidate)
                if changed:
                    files_modified += 1
                    backups_created += 1

        mutation_performed = apply and files_modified > 0

        return TargetedReplacementResult(
            status="PASS",
            mode="apply" if apply else "dry_run",
            source_plan=str(self.planning_json.relative_to(self.root)),
            candidate_count=len(candidates),
            total_replacements=sum(candidate.replacement_count for candidate in candidates),
            files_modified=files_modified,
            backups_created=backups_created,
            mutation_performed=mutation_performed,
            candidates=candidates,
            blocked_reason=None,
        )
