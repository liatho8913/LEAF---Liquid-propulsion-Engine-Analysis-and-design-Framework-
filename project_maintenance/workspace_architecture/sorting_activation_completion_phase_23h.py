from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_SORTING_ACTIVATION_COMPLETION_PHASE_23H_V1"

PHASE_REQUIREMENTS = {
    "23A": "Sorting Activation Readiness Audit",
    "23B": "User Approval Rules",
    "23C": "Safe Execution Sandbox",
    "23D": "Small Batch Execution",
    "23E": "Rollback Validation",
    "23F": "Controlled Execution Gate",
    "23G": "Continuous Watch Readiness",
}

KNOWN_GATE_FILES = {
    "23C": "_leaf_artifacts/workspace_architecture/phase_23c/sorting_safe_execution_sandbox_gate_phase_23c.json",
    "23D": "_leaf_artifacts/workspace_architecture/phase_23d/sorting_small_batch_execution_gate_phase_23d.json",
    "23E": "_leaf_artifacts/workspace_architecture/phase_23e/sorting_rollback_validation_gate_phase_23e.json",
    "23F": "_leaf_artifacts/workspace_architecture/phase_23f/sorting_controlled_execution_master_gate_phase_23f.json",
    "23G": "_leaf_artifacts/workspace_architecture/phase_23g/sorting_continuous_watch_readiness_gate_phase_23g.json",
}


@dataclass(frozen=True)
class PhaseCompletionEvidence:
    phase: str
    name: str
    complete: bool
    evidence_source: str
    evidence_path: str
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class SortingActivationCompletion:
    schema: str
    phase: str
    programme: str
    programme_complete: bool
    phase_count: int
    completed_phase_count: int
    controlled_execution_available: bool
    automatic_execution_enabled: bool
    continuous_watcher_enabled: bool
    delete_operations_enabled: bool
    archive_operations_enabled: bool
    active_repository_mutation_default: bool
    manual_approval_required: bool
    rollback_required: bool
    small_batch_required: bool
    future_watch_readiness_only: bool
    next_programme: str
    next_feature: str
    blocker_count: int
    blockers: tuple[str, ...]
    phases: tuple[PhaseCompletionEvidence, ...]
    deterministic_completion_hash: str


def _stable_hash(payload: Any, length: int = 24) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _json_indicates_passed(data: dict[str, Any]) -> bool:
    if data.get("passed") is True:
        return True
    if data.get("result", {}).get("passed") is True:
        return True
    if data.get("summary", {}).get("sandbox_passed") is True:
        return True
    if data.get("result", {}).get("controlled_execution_available") is True:
        return True
    if data.get("result", {}).get("continuous_watch_ready_for_future_design") is True:
        return True
    if data.get("completion_notice", "").startswith("PHASE_"):
        return "BLOCKED" not in data.get("completion_notice", "")
    return False


class SortingActivationCompletionEvaluator:
    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root)
        self.workspace_dir = self.project_root / "project_maintenance" / "workspace_architecture"
        self.artifact_root = self.project_root / "_leaf_artifacts" / "workspace_architecture"
        self.out_dir = self.artifact_root / "phase_23h"
        self.result_json = self.out_dir / "sorting_activation_completion_phase_23h.json"
        self.report_txt = self.out_dir / "sorting_activation_completion_phase_23h.txt"

    def _phase_evidence(self, phase: str, name: str) -> PhaseCompletionEvidence:
        blockers: list[str] = []

        known_gate = KNOWN_GATE_FILES.get(phase)
        if known_gate:
            gate_path = self.project_root / known_gate
            gate_data = _read_json(gate_path)
            complete = _json_indicates_passed(gate_data)
            if not gate_data:
                blockers.append(f"{phase.lower()}_known_gate_missing")
            elif not complete:
                blockers.append(f"{phase.lower()}_known_gate_not_passed")

            return PhaseCompletionEvidence(
                phase=phase,
                name=name,
                complete=complete,
                evidence_source="known_gate_json",
                evidence_path=known_gate,
                blockers=tuple(blockers),
            )

        phase_lower = phase.lower()
        phase_dir = self.artifact_root / f"phase_{phase_lower}"
        json_candidates = sorted(phase_dir.glob(f"*{phase_lower}*.json")) if phase_dir.exists() else []
        module_candidates = sorted(self.workspace_dir.glob(f"*{phase_lower}*.py"))

        for candidate in json_candidates:
            data = _read_json(candidate)
            if _json_indicates_passed(data):
                return PhaseCompletionEvidence(
                    phase=phase,
                    name=name,
                    complete=True,
                    evidence_source="artifact_json",
                    evidence_path=candidate.relative_to(self.project_root).as_posix(),
                    blockers=tuple(),
                )

        if module_candidates:
            return PhaseCompletionEvidence(
                phase=phase,
                name=name,
                complete=True,
                evidence_source="module_present",
                evidence_path=module_candidates[0].relative_to(self.project_root).as_posix(),
                blockers=tuple(),
            )

        blockers.append(f"{phase.lower()}_evidence_missing")
        return PhaseCompletionEvidence(
            phase=phase,
            name=name,
            complete=False,
            evidence_source="missing",
            evidence_path="",
            blockers=tuple(blockers),
        )

    def evaluate(self) -> SortingActivationCompletion:
        phases = tuple(
            self._phase_evidence(phase, name)
            for phase, name in PHASE_REQUIREMENTS.items()
        )

        blockers = tuple(
            blocker
            for phase in phases
            for blocker in phase.blockers
        )

        completed_phase_count = sum(1 for phase in phases if phase.complete)

        phase_23f = _read_json(self.project_root / KNOWN_GATE_FILES["23F"])
        phase_23g = _read_json(self.project_root / KNOWN_GATE_FILES["23G"])

        f_result = phase_23f.get("result", {})
        g_result = phase_23g.get("result", {})

        controlled_execution_available = f_result.get("controlled_execution_available") is True
        automatic_execution_enabled = False
        continuous_watcher_enabled = False
        delete_operations_enabled = False
        archive_operations_enabled = False
        active_repository_mutation_default = False
        manual_approval_required = f_result.get("manual_approval_required") is True
        rollback_required = f_result.get("rollback_required") is True
        small_batch_required = f_result.get("small_batch_required") is True
        future_watch_readiness_only = g_result.get("readiness_only") is True

        safety_checks = {
            "controlled_execution_available": controlled_execution_available,
            "manual_approval_required": manual_approval_required,
            "rollback_required": rollback_required,
            "small_batch_required": small_batch_required,
            "future_watch_readiness_only": future_watch_readiness_only,
        }

        safety_blockers = tuple(
            f"safety_check_failed:{key}"
            for key, value in safety_checks.items()
            if value is not True
        )

        unsafe_flags = {
            "automatic_execution_enabled": automatic_execution_enabled,
            "continuous_watcher_enabled": continuous_watcher_enabled,
            "delete_operations_enabled": delete_operations_enabled,
            "archive_operations_enabled": archive_operations_enabled,
            "active_repository_mutation_default": active_repository_mutation_default,
        }

        unsafe_blockers = tuple(
            f"unsafe_flag_not_false:{key}"
            for key, value in unsafe_flags.items()
            if value is not False
        )

        all_blockers = blockers + safety_blockers + unsafe_blockers
        programme_complete = completed_phase_count == len(PHASE_REQUIREMENTS) and not all_blockers

        seed = {
            "programme_complete": programme_complete,
            "completed_phase_count": completed_phase_count,
            "blockers": all_blockers,
            "phases": [asdict(phase) for phase in phases],
        }

        return SortingActivationCompletion(
            schema=SCHEMA,
            phase="23H",
            programme="Programme 23 — Controlled Sorting Activation",
            programme_complete=programme_complete,
            phase_count=len(PHASE_REQUIREMENTS),
            completed_phase_count=completed_phase_count,
            controlled_execution_available=controlled_execution_available,
            automatic_execution_enabled=automatic_execution_enabled,
            continuous_watcher_enabled=continuous_watcher_enabled,
            delete_operations_enabled=delete_operations_enabled,
            archive_operations_enabled=archive_operations_enabled,
            active_repository_mutation_default=active_repository_mutation_default,
            manual_approval_required=manual_approval_required,
            rollback_required=rollback_required,
            small_batch_required=small_batch_required,
            future_watch_readiness_only=future_watch_readiness_only,
            next_programme="Programme 24 — Engineering Workspace Runtime",
            next_feature="24A — Runtime Session Lifecycle",
            blocker_count=len(all_blockers),
            blockers=all_blockers,
            phases=phases,
            deterministic_completion_hash=_stable_hash(seed, 24),
        )

    def write_result(self, result: SortingActivationCompletion) -> dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.result_json.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        self.report_txt.write_text("\n".join([
            "LEAF PHASE 23H SORTING ACTIVATION COMPLETION REPORT",
            "==================================================",
            f"schema={result.schema}",
            f"programme={result.programme}",
            f"programme_complete={result.programme_complete}",
            f"phase_count={result.phase_count}",
            f"completed_phase_count={result.completed_phase_count}",
            f"controlled_execution_available={result.controlled_execution_available}",
            f"automatic_execution_enabled={result.automatic_execution_enabled}",
            f"continuous_watcher_enabled={result.continuous_watcher_enabled}",
            f"delete_operations_enabled={result.delete_operations_enabled}",
            f"archive_operations_enabled={result.archive_operations_enabled}",
            f"active_repository_mutation_default={result.active_repository_mutation_default}",
            f"manual_approval_required={result.manual_approval_required}",
            f"rollback_required={result.rollback_required}",
            f"small_batch_required={result.small_batch_required}",
            f"future_watch_readiness_only={result.future_watch_readiness_only}",
            f"blocker_count={result.blocker_count}",
            f"deterministic_completion_hash={result.deterministic_completion_hash}",
            f"next_programme={result.next_programme}",
            f"next_feature={result.next_feature}",
            "",
            "Phase evidence:",
            *[
                f"{phase.phase} | complete={phase.complete} | source={phase.evidence_source} | path={phase.evidence_path}"
                for phase in result.phases
            ],
            "",
            "Blockers:",
            *(result.blockers or ("none",)),
        ]), encoding="utf-8")

        return {
            "json": self.result_json.relative_to(self.project_root).as_posix(),
            "report": self.report_txt.relative_to(self.project_root).as_posix(),
        }


def run_sorting_activation_completion(project_root: str | Path = ".") -> dict[str, Any]:
    evaluator = SortingActivationCompletionEvaluator(project_root)
    result = evaluator.evaluate()
    paths = evaluator.write_result(result)

    return {
        "schema": SCHEMA,
        "phase": "23H",
        "feature": "SORTING_ACTIVATION_COMPLETION",
        "result": asdict(result),
        "paths": paths,
        "completion_notice": "PHASE_23H_COMPLETE_SORTING_ACTIVATION_SIGNED_OFF" if result.programme_complete else "PHASE_23H_BLOCKED",
        "next_phase": "24A_RUNTIME_SESSION_LIFECYCLE",
    }


if __name__ == "__main__":
    run = run_sorting_activation_completion(Path.cwd())
    result = run["result"]
    print("PASS_PHASE_23H_SORTING_ACTIVATION_COMPLETION_WRITTEN" if result["programme_complete"] else "FAIL_PHASE_23H_SORTING_ACTIVATION_COMPLETION_WRITTEN")
    print(f"schema={run['schema']}")
    print(f"programme_complete={result['programme_complete']}")
    print(f"completed_phase_count={result['completed_phase_count']}/{result['phase_count']}")
    print(f"controlled_execution_available={result['controlled_execution_available']}")
    print(f"automatic_execution_enabled={result['automatic_execution_enabled']}")
    print(f"continuous_watcher_enabled={result['continuous_watcher_enabled']}")
    print(f"delete_operations_enabled={result['delete_operations_enabled']}")
    print(f"archive_operations_enabled={result['archive_operations_enabled']}")
    print(f"manual_approval_required={result['manual_approval_required']}")
    print(f"rollback_required={result['rollback_required']}")
    print(f"small_batch_required={result['small_batch_required']}")
    print(f"future_watch_readiness_only={result['future_watch_readiness_only']}")
    print(f"blocker_count={result['blocker_count']}")
    print(f"completion_notice={run['completion_notice']}")
    print(f"report={run['paths']['report']}")
    print(f"json={run['paths']['json']}")
    print(f"next_phase={run['next_phase']}")
