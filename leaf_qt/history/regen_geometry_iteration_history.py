from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class RegenGeometryIterationRecord:
    iteration_index: int
    channel_count: int | None
    channel_width: float | None
    channel_height: float | None
    effective_rib_width: float | None
    fit_ratio: float | None
    coolant_velocity: float | None
    reynolds_number: float | None
    estimated_pressure_drop: float | None
    circumferential_coverage: float | None
    score: float | None
    constraint_status: str
    failures: list[str]
    warnings: list[str]
    decision: str


class RegenGeometryIterationHistory:
    def __init__(self, max_records: int = 250):
        self.max_records = max_records
        self.records: list[RegenGeometryIterationRecord] = []
        self.total_candidates_seen = 0
        self.total_passed_constraints = 0
        self.total_failed_constraints = 0

    def record_candidate(self, candidate: dict[str, Any], constraint_result: dict[str, Any]):
        self.total_candidates_seen += 1

        passed = bool(constraint_result.get("geometry_constraints_pass"))
        if passed:
            self.total_passed_constraints += 1
            decision = "ACCEPTED_BY_CONSTRAINT_OWNER"
        else:
            self.total_failed_constraints += 1
            decision = "REJECTED_BY_CONSTRAINT_OWNER"

        if len(self.records) >= self.max_records:
            return

        self.records.append(
            RegenGeometryIterationRecord(
                iteration_index=self.total_candidates_seen,
                channel_count=candidate.get("channel_count"),
                channel_width=candidate.get("channel_width"),
                channel_height=candidate.get("channel_height"),
                effective_rib_width=candidate.get("effective_rib_width"),
                fit_ratio=candidate.get("fit_ratio"),
                coolant_velocity=candidate.get("coolant_velocity"),
                reynolds_number=candidate.get("reynolds_number"),
                estimated_pressure_drop=candidate.get("estimated_pressure_drop"),
                circumferential_coverage=candidate.get("circumferential_coverage"),
                score=candidate.get("score"),
                constraint_status=constraint_result.get("constraint_status", "UNKNOWN"),
                failures=list(constraint_result.get("failures", [])),
                warnings=list(constraint_result.get("warnings", [])),
                decision=decision,
            )
        )

    def build_summary(self, selected_candidate: dict[str, Any] | None = None):
        if selected_candidate:
            selected_reason = (
                "Selected highest-scoring candidate that passed the regen geometry constraint owner."
            )
        else:
            selected_reason = (
                "No candidate passed the regen geometry constraint owner."
            )

        failure_counts: dict[str, int] = {}
        warning_counts: dict[str, int] = {}

        for record in self.records:
            for failure in record.failures:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
            for warning in record.warnings:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1

        return {
            "iteration_history_status": "PASS",
            "total_candidates_seen": float(self.total_candidates_seen),
            "total_passed_constraints": float(self.total_passed_constraints),
            "total_failed_constraints": float(self.total_failed_constraints),
            "stored_iteration_records": float(len(self.records)),
            "selected_candidate_reason": selected_reason,
            "most_common_failures": failure_counts,
            "most_common_warnings": warning_counts,
            "records": [asdict(record) for record in self.records],
        }


def flatten_iteration_history_summary(summary: dict[str, Any], prefix: str = "recommended"):
    failures = summary.get("most_common_failures", {})
    warnings = summary.get("most_common_warnings", {})

    failure_text = "; ".join(
        f"{key}: {value}" for key, value in sorted(failures.items())
    )

    warning_text = "; ".join(
        f"{key}: {value}" for key, value in sorted(warnings.items())
    )

    return {
        f"{prefix}_geometry_iteration_history_status": summary.get("iteration_history_status"),
        f"{prefix}_geometry_total_candidates_seen": summary.get("total_candidates_seen", 0.0),
        f"{prefix}_geometry_total_passed_constraints": summary.get("total_passed_constraints", 0.0),
        f"{prefix}_geometry_total_failed_constraints": summary.get("total_failed_constraints", 0.0),
        f"{prefix}_geometry_stored_iteration_records": summary.get("stored_iteration_records", 0.0),
        f"{prefix}_geometry_selected_candidate_reason": summary.get("selected_candidate_reason", ""),
        f"{prefix}_geometry_most_common_failures": failure_text,
        f"{prefix}_geometry_most_common_warnings": warning_text,
    }