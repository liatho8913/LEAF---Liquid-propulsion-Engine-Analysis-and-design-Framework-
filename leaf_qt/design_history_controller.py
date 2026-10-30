from datetime import datetime
import copy

from leaf_qt.history.design_history_narrative_builder import (
    DesignHistoryNarrativeBuilder,
    build_history_result_snapshot,
)
from optimisation_proof_owner import OptimisationProofOwner
from failure_root_cause_owner import FailureRootCauseOwner
from recommendation_explanation_owner import RecommendationExplanationOwner


class DesignHistoryController:
    """
    Owns persistent in-session design history.

    Each calculation becomes a recorded design iteration containing:
    - timestamp
    - inputs snapshot
    - outputs summary
    - validation status
    - warning count
    - benchmark status
    - root-cause/recommendation evidence
    """

    def __init__(self, get_inputs_callback):
        self.get_inputs = get_inputs_callback
        self.history = []
        self.narrative_builder = DesignHistoryNarrativeBuilder()
        self.optimisation_proof_owner = OptimisationProofOwner()
        self.failure_root_cause_owner = FailureRootCauseOwner()
        self.recommendation_explanation_owner = RecommendationExplanationOwner()

    def record_iteration(self, solved, diagnostics_report=None, audit_rows=None):
        solved = solved if isinstance(solved, dict) else {}
        diagnostics_report = diagnostics_report if isinstance(diagnostics_report, dict) else {}
        audit_rows = audit_rows if isinstance(audit_rows, list) else []

        inputs_snapshot = self._safe_copy(self.get_inputs())
        iteration_number = len(self.history) + 1

        record = {
            "iteration_number": iteration_number,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "inputs": inputs_snapshot,
            "summary": self._build_summary(solved, diagnostics_report, audit_rows),
            "results": self._safe_copy(build_history_result_snapshot(solved)),
            "diagnostics_report": self._safe_copy(diagnostics_report),
            "audit_rows": self._safe_copy(audit_rows),
        }

        self.history.append(record)

        solved["design_history_iteration_number"] = iteration_number
        solved["design_history_count"] = len(self.history)
        solved["design_history_latest_summary"] = record["summary"]
        solved["design_history_text"] = self.build_history_text()
        solved["design_history_narrative_text"] = self.narrative_builder.build(self.history)

        solved["optimisation_proof_text"] = self.optimisation_proof_owner.build_proof(self.history)
        solved["optimisation_candidate_ranking_text"] = (
            self.optimisation_proof_owner.build_candidate_ranking(self.history)
        )
        solved["optimisation_score_evidence_text"] = (
            self.optimisation_proof_owner.build_score_evidence_table(self.history)
        )

        best_candidate_summary = (
            self.optimisation_proof_owner.build_best_candidate_summary(self.history)
        )
        solved.update(best_candidate_summary)

        regression_gate = (
            self.optimisation_proof_owner.build_regression_gate(self.history)
        )
        solved.update(regression_gate)

        solved["optimisation_ownership_report_text"] = (
            self.optimisation_proof_owner.build_optimisation_ownership_report(self.history)
        )

        self.failure_root_cause_owner.attach(
            solved,
            diagnostics_report=diagnostics_report,
            audit_rows=audit_rows,
        )

        self.recommendation_explanation_owner.attach(solved)

        record["results"] = self._safe_copy(build_history_result_snapshot(solved))
        record["summary"] = self._build_summary(solved, diagnostics_report, audit_rows)

        return solved

    def get_history(self):
        return self.history

    def set_history(self, history):
        self.history = history if isinstance(history, list) else []

    def clear_history(self):
        self.history = []

    def build_history_text(self):
        lines = []
        lines.append("LEAF DESIGN HISTORY")
        lines.append("===================")
        lines.append("")
        lines.append(f"Recorded iterations: {len(self.history)}")
        lines.append("")

        if not self.history:
            lines.append("No design iterations have been recorded yet.")
            return "\n".join(lines)

        for record in self.history:
            summary = record.get("summary", {})

            lines.append(f"Iteration {record.get('iteration_number', 'N/A')}")
            lines.append("-" * 30)
            lines.append(f"Timestamp: {record.get('timestamp', 'N/A')}")
            lines.append(f"Validation status: {summary.get('validation_status', 'N/A')}")
            lines.append(f"Regen status: {summary.get('regen_validation_status', 'N/A')}")
            lines.append(f"Pipeline status: {summary.get('foundation_attachment_pipeline_status', 'N/A')}")
            lines.append(f"Benchmark status: {summary.get('benchmark_status', 'N/A')}")
            lines.append(f"Warnings: {summary.get('warning_count', 'N/A')}")
            lines.append(f"Critical diagnostics: {summary.get('critical_diagnostic_count', 'N/A')}")
            lines.append("")

        return "\n".join(lines)

    def _build_summary(self, solved, diagnostics_report, audit_rows):
        counts = diagnostics_report.get("counts", {})

        return {
            "validation_status": solved.get("validation_status"),
            "regen_validation_status": solved.get("regen_validation_status"),
            "foundation_attachment_pipeline_status": solved.get("foundation_attachment_pipeline_status"),
            "benchmark_status": solved.get("benchmark_status"),
            "engine_reproduction_status": solved.get("engine_reproduction_status"),
            "output_ownership_audit_status": solved.get("output_ownership_audit_status"),
            "foundation_result_key_audit_status": solved.get("foundation_result_key_audit_status"),
            "warning_count": self._count_warning_like_items(solved),
            "critical_diagnostic_count": counts.get("critical", 0),
            "diagnostic_warning_count": counts.get("warning", 0),
            "audit_row_count": len(audit_rows),
            "root_cause_available": bool(
                solved.get("failure_root_cause_owner_text")
                or solved.get("failure_root_cause_text")
            ),
            "recommendation_available": bool(
                solved.get("recommendation_owner_text")
                or solved.get("recommendation_explanation_text")
            ),
            "recommendation_evidence_status": solved.get(
                "recommendation_owner_evidence_status",
                "N/A",
            ),
            "recommendation_rejected_count": solved.get(
                "recommendation_owner_rejected_count",
                0,
            ),
            "primary_recommendation_source": solved.get(
                "recommendation_owner_primary_source",
                "NONE",
            ),
        }

    def _count_warning_like_items(self, solved):
        warnings = solved.get("warnings")

        if isinstance(warnings, list):
            return len(warnings)

        warning_count = solved.get("warning_count")

        if isinstance(warning_count, int):
            return warning_count

        return 0

    def _safe_copy(self, value):
        try:
            return copy.deepcopy(value)
        except Exception:
            return value