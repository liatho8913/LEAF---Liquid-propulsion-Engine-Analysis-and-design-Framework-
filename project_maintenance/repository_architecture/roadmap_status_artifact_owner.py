from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class RoadmapStatusArtifactOwner:
    """Permanent owner for project-wide repository architecture roadmap status.

    This keeps roadmap state reusable instead of scattering status text across
    one-off phase scripts.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[2]
        self.out = self.root / "_leaf_artifacts" / "repository_architecture" / "roadmap_status"
        self.out.mkdir(parents=True, exist_ok=True)
        self.json_path = self.out / "repository_architecture_roadmap_status.json"
        self.txt_path = self.out / "repository_architecture_roadmap_status.txt"

    def build_status(
        self,
        *,
        current_major_feature: str,
        current_phase: str,
        previous_completed_feature: str,
        current_goal: str,
        completed: list[str],
        active_constraints: list[str],
        remaining_work: list[str],
        next_phase: str,
        safety_locks: dict[str, bool],
        metrics: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "schema": "LEAF_REPOSITORY_ARCHITECTURE_ROADMAP_STATUS_V1",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "current_major_feature": current_major_feature,
            "current_phase": current_phase,
            "previous_completed_feature": previous_completed_feature,
            "current_goal": current_goal,
            "completed": completed,
            "active_constraints": active_constraints,
            "remaining_work": remaining_work,
            "metrics": metrics or {},
            "safety_locks": {
                "move_allowed": bool(safety_locks.get("move_allowed", False)),
                "archive_allowed": bool(safety_locks.get("archive_allowed", False)),
                "delete_allowed": bool(safety_locks.get("delete_allowed", False)),
                "automatic_delete_allowed": bool(safety_locks.get("automatic_delete_allowed", False)),
                "deletion_started": bool(safety_locks.get("deletion_started", False)),
            },
            "next_phase": next_phase,
        }

    def write_status(self, status: dict[str, Any]) -> dict[str, str]:
        self.json_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

        lines = [
            "LEAF REPOSITORY ARCHITECTURE ROADMAP STATUS",
            "===========================================",
            f"timestamp={status['timestamp']}",
            f"current_major_feature={status['current_major_feature']}",
            f"current_phase={status['current_phase']}",
            f"previous_completed_feature={status['previous_completed_feature']}",
            f"current_goal={status['current_goal']}",
            "",
            "COMPLETED",
            *[f"- {item}" for item in status["completed"]],
            "",
            "ACTIVE_CONSTRAINTS",
            *[f"- {item}" for item in status["active_constraints"]],
            "",
            "REMAINING_WORK",
            *[f"- {item}" for item in status["remaining_work"]],
            "",
            "METRICS",
            *[f"- {key}={value}" for key, value in status.get("metrics", {}).items()],
            "",
            "SAFETY_LOCKS",
            *[f"- {key}={value}" for key, value in status["safety_locks"].items()],
            "",
            f"next_phase={status['next_phase']}",
        ]
        self.txt_path.write_text("\n".join(lines), encoding="utf-8")

        return {
            "json": self.json_path.relative_to(self.root).as_posix(),
            "report": self.txt_path.relative_to(self.root).as_posix(),
        }
