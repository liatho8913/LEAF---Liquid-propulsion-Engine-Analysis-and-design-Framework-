from leaf_qt.status_presentation import status_severity


HISTORY_VALIDATION_EVIDENCE_KEYS = (
    "validation_reason",
    "regen_validation_reason",
    "recommended_geometry_reason",
    "best_full_engine_regen_reason",
    "full_engine_regen_reason",
    "channel_geometry_reason",
    "material_validation_reason",
    "coating_validation_reason",
)

HISTORY_DIRECT_RESULT_KEYS = (
    "warnings",
)

HISTORY_RESULT_KEYS = (
    *HISTORY_DIRECT_RESULT_KEYS,
    *HISTORY_VALIDATION_EVIDENCE_KEYS,
)


def build_history_result_snapshot(results):
    """
    Preserve only result evidence consumed by the canonical
    design-history narrative owner.

    Complete current solver results remain owned by last_results.
    """
    results = (
        results
        if isinstance(results, dict)
        else {}
    )

    return {
        key: results[key]
        for key in HISTORY_RESULT_KEYS
        if key in results
    }


class DesignHistoryNarrativeBuilder:
    """
    Builds a persistent design-iteration narrative from DesignHistoryController.history.

    Ownership rule:
    - DesignHistoryController owns recorded iteration history.
    - This builder converts that history into a readable engineering narrative.
    - It does not own calculation logic.
    """

    PASS_WORDS = {"PASS", "PASSED", "OK", "VALID", "RECORDED", "COMPLETE"}
    FAIL_WORDS = {"FAIL", "FAILED", "INVALID", "ERROR", "BLOCKED"}

    def build(self, history):
        history = history if isinstance(history, list) else []

        lines = []
        lines.append("LEAF PERSISTENT DESIGN ITERATION NARRATIVE")
        lines.append("==========================================")
        lines.append("")

        if not history:
            lines.append("No design iterations have been recorded yet.")
            return "\n".join(lines)

        previous = None

        for record in history:
            self._append_iteration(lines, previous, record)
            previous = record

        return "\n".join(lines)

    def _append_iteration(self, lines, previous, record):
        iteration_number = record.get("iteration_number", "N/A")
        timestamp = record.get("timestamp", "N/A")
        summary = self._safe_dict(record.get("summary"))

        lines.append(f"Iteration {iteration_number}")
        lines.append("-" * 40)
        lines.append(f"Timestamp: {timestamp}")
        lines.append(f"Validation status: {summary.get('validation_status', 'UNKNOWN')}")
        lines.append(f"Regen status: {summary.get('regen_validation_status', 'UNKNOWN')}")
        lines.append(f"Benchmark status: {summary.get('benchmark_status', 'UNKNOWN')}")
        lines.append(f"Warnings: {summary.get('warning_count', 0)}")
        lines.append(f"Critical diagnostics: {summary.get('critical_diagnostic_count', 0)}")
        lines.append("")

        if previous is None:
            lines.append("Baseline:")
            lines.append("- This is the first recorded design iteration.")
            lines.append("")
            self._append_current_failure_state(lines, summary)
            lines.append("")
            return

        previous_summary = self._safe_dict(previous.get("summary"))

        self._append_changes(lines, previous, record)
        lines.append("")
        self._append_status_transitions(lines, previous_summary, summary)
        lines.append("")
        self._append_failure_reasoning(lines, previous_summary, summary)
        lines.append("")
        self._append_evidence(lines, record)
        lines.append("")

    def _append_changes(self, lines, previous, current):
        previous_inputs = self._safe_dict(previous.get("inputs"))
        current_inputs = self._safe_dict(current.get("inputs"))

        changed = []

        for key in sorted(set(previous_inputs.keys()) | set(current_inputs.keys())):
            old = previous_inputs.get(key)
            new = current_inputs.get(key)

            if old != new:
                changed.append(f"{key}: {old} -> {new}")

        lines.append("Changes since previous iteration:")

        if not changed:
            lines.append("- No input changes detected.")
        else:
            for item in changed:
                lines.append(f"- {item}")

    def _append_status_transitions(self, lines, previous_summary, current_summary):
        checks = [
            ("Validation", "validation_status"),
            ("Regen validation", "regen_validation_status"),
            ("Benchmark", "benchmark_status"),
            ("Pipeline", "foundation_attachment_pipeline_status"),
            ("Output ownership audit", "output_ownership_audit_status"),
            ("Result key audit", "foundation_result_key_audit_status"),
        ]

        transitions = []

        for label, key in checks:
            old = previous_summary.get(key)
            new = current_summary.get(key)

            if old != new:
                transitions.append(
                    self._describe_status_transition(label, old, new)
                )

        lines.append("Status transitions:")

        if not transitions:
            lines.append("- No major status transitions detected.")
        else:
            for item in transitions:
                lines.append(f"- {item}")

    def _append_failure_reasoning(self, lines, previous_summary, current_summary):
        lines.append("Failure / improvement reasoning:")

        reasoning = []

        previous_warnings = self._safe_int(previous_summary.get("warning_count"))
        current_warnings = self._safe_int(current_summary.get("warning_count"))

        previous_critical = self._safe_int(previous_summary.get("critical_diagnostic_count"))
        current_critical = self._safe_int(current_summary.get("critical_diagnostic_count"))

        if current_warnings < previous_warnings:
            reasoning.append(
                f"Warning count improved: {previous_warnings} -> {current_warnings}."
            )
        elif current_warnings > previous_warnings:
            reasoning.append(
                f"Warning count worsened: {previous_warnings} -> {current_warnings}."
            )

        if current_critical < previous_critical:
            reasoning.append(
                f"Critical diagnostics improved: {previous_critical} -> {current_critical}."
            )
        elif current_critical > previous_critical:
            reasoning.append(
                f"Critical diagnostics worsened: {previous_critical} -> {current_critical}."
            )

        for label, key in (
            ("Validation", "validation_status"),
            ("Regen validation", "regen_validation_status"),
            ("Benchmark", "benchmark_status"),
        ):
            old = previous_summary.get(key)
            new = current_summary.get(key)

            if self._is_fail(old) and self._is_pass(new):
                reasoning.append(
                    f"{label} moved from failure to pass. The latest design should be treated as an improvement candidate."
                )

            elif self._is_pass(old) and self._is_fail(new):
                reasoning.append(
                    f"{label} moved from pass to failure. The latest design introduced a regression."
                )

            elif self._is_fail(new):
                reasoning.append(
                    f"{label} is still failing. Further correction is required before this can be considered validated."
                )

        if not reasoning:
            reasoning.append(
                "No clear failure/improvement transition was detected from available summary fields."
            )

        for item in reasoning:
            lines.append(f"- {item}")

    def _append_current_failure_state(self, lines, summary):
        lines.append("Initial failure state:")

        items = []

        for label, key in (
            ("Validation", "validation_status"),
            ("Regen validation", "regen_validation_status"),
            ("Benchmark", "benchmark_status"),
        ):
            value = summary.get(key)

            if self._is_fail(value):
                items.append(f"{label} starts in a failing state: {value}.")

        warning_count = self._safe_int(summary.get("warning_count"))
        critical_count = self._safe_int(summary.get("critical_diagnostic_count"))

        if warning_count:
            items.append(f"Initial warning count: {warning_count}.")

        if critical_count:
            items.append(f"Initial critical diagnostic count: {critical_count}.")

        if not items:
            items.append("No initial failure state detected from available summary fields.")

        for item in items:
            lines.append(f"- {item}")


    def _append_evidence(self, lines, record):
        lines.append("Evidence:")

        evidence = []

        results = self._safe_dict(record.get("results"))
        diagnostics_report = self._safe_dict(record.get("diagnostics_report"))
        audit_rows = record.get("audit_rows", [])

        evidence.extend(self._extract_warning_evidence(results))
        evidence.extend(self._extract_diagnostic_evidence(diagnostics_report))
        evidence.extend(self._extract_audit_evidence(audit_rows))
        evidence.extend(self._extract_validation_evidence(results))

        if not evidence:
            lines.append("- No detailed evidence was recorded for this iteration.")
            return

        for item in evidence[:12]:
            lines.append(f"- {item}")

        if len(evidence) > 12:
            lines.append(f"- Additional evidence entries omitted: {len(evidence) - 12}")

    def _extract_warning_evidence(self, results):
        warnings = results.get("warnings")

        if not isinstance(warnings, list):
            return []

        evidence = []

        for warning in warnings:
            if warning:
                evidence.append(f"Warning: {warning}")

        return evidence

    def _extract_diagnostic_evidence(self, diagnostics_report):
        evidence = []

        items = diagnostics_report.get("items")

        if not isinstance(items, list):
            items = diagnostics_report.get("diagnostics")

        if not isinstance(items, list):
            return evidence

        for item in items:
            if isinstance(item, dict):
                severity = item.get("severity", "UNKNOWN")
                message = item.get("message") or item.get("text") or item.get("description")
                key = item.get("key") or item.get("variable") or item.get("name")

                if message:
                    if key:
                        evidence.append(f"Diagnostic [{severity}] {key}: {message}")
                    else:
                        evidence.append(f"Diagnostic [{severity}]: {message}")
            elif item:
                evidence.append(f"Diagnostic: {item}")

        return evidence

    def _extract_audit_evidence(self, audit_rows):
        if not isinstance(audit_rows, list):
            return []

        evidence = []

        for row in audit_rows:
            if not isinstance(row, dict):
                continue

            status = row.get("status")
            message = row.get("message")
            layer = row.get("layer") or row.get("name") or row.get("check")

            if status and status not in ("PASS", "PASSED", "OK"):
                if layer and message:
                    evidence.append(f"Audit [{status}] {layer}: {message}")
                elif layer:
                    evidence.append(f"Audit [{status}] {layer}")
                elif message:
                    evidence.append(f"Audit [{status}]: {message}")

        return evidence

    def _extract_validation_evidence(self, results):
        evidence = []

        possible_keys = HISTORY_VALIDATION_EVIDENCE_KEYS

        for key in possible_keys:
            value = results.get(key)

            if value:
                evidence.append(f"{key}: {value}")

        return evidence

    def _describe_status_transition(self, label, old, new):
        if self._is_fail(old) and self._is_pass(new):
            return f"{label}: {old} -> {new} improvement"

        if self._is_pass(old) and self._is_fail(new):
            return f"{label}: {old} -> {new} regression"

        return f"{label}: {old} -> {new}"

    def _is_pass(self, value):
        text = str(value or "").strip().upper()
        return text in self.PASS_WORDS or status_severity(text) == "PASS"

    def _is_fail(self, value):
        text = str(value or "").strip().upper()
        return text in self.FAIL_WORDS or status_severity(text) == "FAIL"

    def _safe_dict(self, value):
        return value if isinstance(value, dict) else {}

    def _safe_int(self, value):
        try:
            return int(value)
        except Exception:
            return 0