from leaf_qt.status_presentation import status_severity

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:


    class LegacyCompatibilityProducer:
        """
        Phase 16U shared presentation compatibility fallback.

        This local fallback is only used when leaf_qt.status_presentation
        cannot be imported. Normal production execution should use the shared
        status_presentation implementation.
        """

        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity == "FAIL":
                return "FAIL"
            if severity == "WARN":
                return "WARN"
            if severity == "PASS":
                return "PASS"
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

    def status_severity(value):
        text = str(value or "").upper()
        if _leaf_16u71_is_fail_like(text) or _leaf_16u71_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u71_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u71_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u71_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u71_is_fail_like(text) or _leaf_16u71_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u71_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u71_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u71_is_fail_like(value):
    return _leaf_16u71_status_severity(value) == "FAIL"


def _leaf_16u71_is_warn_like(value):
    return _leaf_16u71_status_severity(value) == "WARN"


def _leaf_16u71_is_pass_like(value):
    return _leaf_16u71_status_severity(value) == "PASS"


class FailureRootCauseOwner:
    """
    Owns generic failure root-cause generation.
    """

    def build_root_cause_report(self, results, diagnostics_report=None, audit_rows=None):
        results = results if isinstance(results, dict) else {}
        diagnostics_report = diagnostics_report if isinstance(diagnostics_report, dict) else {}
        audit_rows = audit_rows if isinstance(audit_rows, list) else []

        failures = self._collect_failures(results, diagnostics_report, audit_rows)

        lines = []
        lines.append("LEAF FAILURE ROOT CAUSE REPORT")
        lines.append("==============================")
        lines.append("")

        if not failures:
            lines.append("No failure state detected from available result keys.")
            return "\n".join(lines)

        lines.append("Detected Failure Chain:")
        lines.append("")

        for index, failure in enumerate(failures, start=1):
            lines.append(f"{index}. {failure['title']}")
            lines.append(f"   Severity: {failure['severity']}")
            lines.append(f"   Evidence: {failure['evidence']}")
            lines.append(f"   Likely cause: {failure['cause']}")
            lines.append(f"   Next action: {failure['action']}")
            lines.append("")

        lines.append("Root Cause Summary:")
        lines.append(f"- Primary root cause: {failures[0]['cause']}")
        lines.append(f"- Highest severity: {self._highest_severity(failures)}")

        return "\n".join(lines)

    def attach(self, results, diagnostics_report=None, audit_rows=None):
        results = results if isinstance(results, dict) else {}
        diagnostics_report = diagnostics_report if isinstance(diagnostics_report, dict) else {}
        audit_rows = audit_rows if isinstance(audit_rows, list) else []

        failures = self._collect_failures(results, diagnostics_report, audit_rows)

        results["failure_root_cause_owner_text"] = self.build_root_cause_report(
            results,
            diagnostics_report,
            audit_rows,
        )

        results["corrective_action_priority_text"] = self.build_corrective_action_report(
            results,
            diagnostics_report,
            audit_rows,
        )

        results["root_cause_ownership_report_text"] = (
            self.build_root_cause_ownership_report(
                results,
                diagnostics_report,
                audit_rows,
            )
        )

        results["failure_root_cause_owner_count"] = len(failures)
        results["failure_root_cause_owner_status"] = (
            "FAILURES_DETECTED" if failures else "NO_FAILURES_DETECTED"
        )

        results["corrective_action_priority_count"] = len(failures)
        results["corrective_action_priority_status"] = (
            "ACTIONS_AVAILABLE" if failures else "NO_ACTIONS_REQUIRED"
        )

        results["root_cause_ownership_report_status"] = "RECORDED"

        if failures:
            results["failure_root_cause_owner_primary_cause"] = failures[0]["cause"]
            results["failure_root_cause_owner_highest_severity"] = self._highest_severity(failures)
        else:
            results["failure_root_cause_owner_primary_cause"] = None
            results["failure_root_cause_owner_highest_severity"] = None

        return results

    def _collect_failures(self, results, diagnostics_report, audit_rows):
        failures = []

        self._collect_status_failures(failures, results)
        self._collect_warning_failures(failures, results)
        self._collect_diagnostic_failures(failures, diagnostics_report)
        self._collect_audit_failures(failures, audit_rows)
        self._collect_optimisation_regression(failures, results)

        if failures:
            self._collect_validation_reason_failures(failures, results)

        return self._sort_failures(failures)

    def _collect_status_failures(self, failures, results):
        status_map = [
            (
                "validation_status",
                "Overall validation failed",
                "One or more required validation gates did not pass.",
                "Review validation report and correct the first failing gate.",
            ),
            (
                "regen_validation_status",
                "Regenerative cooling validation failed",
                "The regen system did not satisfy thermal, hydraulic, material, or geometry constraints.",
                "Review regen geometry, coolant state, wall temperature, Reynolds number, and material limits.",
            ),
            (
                "foundation_attachment_pipeline_status",
                "Foundation attachment pipeline failed",
                "One or more optional foundation/report layers failed during attachment.",
                "Review foundation attachment audit rows and repair failed attachment layers.",
            ),
            (
                "output_ownership_audit_status",
                "Output ownership audit failed",
                "A result key may be routed to the wrong output/report visibility layer.",
                "Review output ownership audit and update variable_registry ownership categories.",
            ),
            (
                "foundation_result_key_audit_status",
                "Foundation result key audit failed",
                "A result key may be unregistered or assigned incorrect ownership.",
                "Register the key in variable_registry or correct its visibility ownership.",
            ),
        ]

        for key, title, cause, action in status_map:
            value = results.get(key)

            if self._is_fail(value):
                failures.append(
                    {
                        "title": title,
                        "severity": self._severity_from_key(key),
                        "evidence": f"{key} = {value}",
                        "cause": cause,
                        "action": action,
                    }
                )

    def _collect_warning_failures(self, failures, results):
        warnings = results.get("warnings")

        if not isinstance(warnings, list) or not warnings:
            return

        preview = "; ".join(str(item) for item in warnings[:3])

        failures.append(
            {
                "title": "Warnings present",
                "severity": "WARNING",
                "evidence": f"{len(warnings)} warning(s): {preview}",
                "cause": "The design produced warning-level issues that reduce confidence.",
                "action": "Review warning panel and resolve warnings before treating the design as final.",
            }
        )

    def _collect_diagnostic_failures(self, failures, diagnostics_report):
        items = diagnostics_report.get("items")

        if not isinstance(items, list):
            items = diagnostics_report.get("diagnostics")

        if not isinstance(items, list):
            return

        for item in items:
            if not isinstance(item, dict):
                continue

            severity = str(item.get("severity", "")).upper()
            message = item.get("message") or item.get("text") or item.get("description")
            key = item.get("key") or item.get("variable") or item.get("name")

            if severity not in {"CRITICAL", "ERROR", "FAIL", "WARNING"}:
                continue

            failures.append(
                {
                    "title": f"Diagnostic issue: {key or 'unnamed'}",
                    "severity": "CRITICAL" if severity in {"CRITICAL", "ERROR", "FAIL"} else "WARNING",
                    "evidence": message or "Diagnostic issue recorded.",
                    "cause": "A diagnostic rule identified a design or calculation issue.",
                    "action": "Open Diagnostics and resolve the listed diagnostic condition.",
                }
            )

    def _collect_audit_failures(self, failures, audit_rows):
        for row in audit_rows:
            if not isinstance(row, dict):
                continue

            status = str(row.get("status", "")).upper()

            if status in {"PASS", "PASSED", "OK", "SKIPPED"}:
                continue

            if not status:
                continue

            failures.append(
                {
                    "title": f"Audit issue: {row.get('layer') or row.get('check') or 'unknown'}",
                    "severity": "WARNING",
                    "evidence": row.get("message") or f"Audit status: {status}",
                    "cause": "A foundation audit or attachment layer reported an issue.",
                    "action": "Review the relevant audit report and repair the failed layer.",
                }
            )

    def _collect_validation_reason_failures(self, failures, results):
        reason_keys = [
            "validation_reason",
            "regen_validation_reason",
            "recommended_geometry_reason",
            "best_full_engine_regen_reason",
            "full_engine_regen_reason",
            "channel_geometry_reason",
            "material_validation_reason",
            "coating_validation_reason",
        ]

        for key in reason_keys:
            value = results.get(key)

            if value:
                failures.append(
                    {
                        "title": f"Validation reason: {key}",
                        "severity": "INFO",
                        "evidence": str(value),
                        "cause": "A validation subsystem supplied explanatory evidence.",
                        "action": "Use this reason to guide the next design correction.",
                    }
                )

    def _collect_optimisation_regression(self, failures, results):
        if not results.get("optimisation_regression_detected"):
            return

        failures.append(
            {
                "title": "Optimisation regression detected",
                "severity": "WARNING",
                "evidence": results.get(
                    "optimisation_regression_gate_reason",
                    "The latest design regressed against optimisation evidence.",
                ),
                "cause": "The latest iteration is worse than an earlier candidate or regressed from a pass state.",
                "action": "Return to the best-ranked candidate or revise the latest changes.",
            }
        )

    def _is_fail(self, value):
        text = str(value or "").strip().upper()
        return (
            text in {"FAIL", "FAILED", "INVALID", "ERROR", "BLOCKED"}
            or status_severity(text) == "FAIL"
            or status_severity(text) == "FAIL"
            or _leaf_16u71_is_fail_like(text)
        )

    def _severity_from_key(self, key):
        if key in {
            "validation_status",
            "regen_validation_status",
            "foundation_attachment_pipeline_status",
        }:
            return "CRITICAL"

        return "WARNING"

    def _sort_failures(self, failures):
        rank = {
            "CRITICAL": 0,
            "WARNING": 1,
            "INFO": 2,
        }

        return sorted(
            failures,
            key=lambda failure: rank.get(failure.get("severity"), 99),
        )

    def _highest_severity(self, failures):
        if any(failure.get("severity") == "CRITICAL" for failure in failures):
            return "CRITICAL"

        if any(failure.get("severity") == "WARNING" for failure in failures):
            return "WARNING"

        return "INFO"

    def build_corrective_action_report(self, results, diagnostics_report=None, audit_rows=None):
        results = results if isinstance(results, dict) else {}
        diagnostics_report = diagnostics_report if isinstance(diagnostics_report, dict) else {}
        audit_rows = audit_rows if isinstance(audit_rows, list) else []

        failures = self._collect_failures(results, diagnostics_report, audit_rows)

        lines = []
        lines.append("LEAF CORRECTIVE ACTION PRIORITY REPORT")
        lines.append("======================================")
        lines.append("")

        if not failures:
            lines.append("No corrective actions required from available failure evidence.")
            return "\n".join(lines)

        self._append_prioritised_actions(lines, failures)

        return "\n".join(lines)

    def build_root_cause_ownership_report(self, results, diagnostics_report=None, audit_rows=None):
        results = results if isinstance(results, dict) else {}
        diagnostics_report = diagnostics_report if isinstance(diagnostics_report, dict) else {}
        audit_rows = audit_rows if isinstance(audit_rows, list) else []

        failures = self._collect_failures(results, diagnostics_report, audit_rows)

        lines = []
        lines.append("LEAF ROOT CAUSE OWNERSHIP REPORT")
        lines.append("================================")
        lines.append("")

        lines.append("Ownership:")
        lines.append("- FailureRootCauseOwner owns generic root-cause reporting.")
        lines.append("- Regen-specific root-cause systems may provide supporting evidence.")
        lines.append("- Reports should consume this ownership report as the controlled source.")
        lines.append("")

        if not failures:
            lines.append("Status: NO_FAILURES_DETECTED")
            lines.append("")
            lines.append("No root-cause action is required from available evidence.")
            return "\n".join(lines)

        lines.append("Status: FAILURES_DETECTED")
        lines.append(f"Failure count: {len(failures)}")
        lines.append(f"Highest severity: {self._highest_severity(failures)}")
        lines.append(f"Primary cause: {failures[0].get('cause')}")
        lines.append("")

        lines.append(self.build_root_cause_report(results, diagnostics_report, audit_rows))
        lines.append("")
        lines.append(self.build_corrective_action_report(results, diagnostics_report, audit_rows))

        return "\n".join(lines)

    def _append_prioritised_actions(self, lines, failures):
        lines.append("Prioritised Corrective Actions:")
        lines.append("")

        ranked = self._rank_corrective_actions(failures)

        for index, item in enumerate(ranked, start=1):
            lines.append(f"{index}. {item['action']}")
            lines.append(f"   Priority: {item['priority']}")
            lines.append(f"   Reason: {item['reason']}")
            lines.append(f"   Linked failure: {item['title']}")
            lines.append("")

    def _rank_corrective_actions(self, failures):
        ranked = []

        for failure in failures:
            ranked.append(
                {
                    "title": failure.get("title", "Unknown failure"),
                    "action": failure.get("action", "Review this failure."),
                    "priority": self._priority_from_failure(failure),
                    "reason": self._priority_reason(failure),
                    "rank": self._priority_rank(failure),
                }
            )

        ranked.sort(key=lambda item: item["rank"])

        return ranked

    def _priority_from_failure(self, failure):
        severity = failure.get("severity")

        if severity == "CRITICAL":
            return "HIGH"

        if severity == "WARNING":
            return "MEDIUM"

        return "LOW"

    def _priority_rank(self, failure):
        severity = failure.get("severity")
        title = str(failure.get("title", "")).lower()

        if severity == "CRITICAL":
            base = 0
        elif severity == "WARNING":
            base = 10
        else:
            base = 20

        if "validation" in title:
            base -= 2

        if "regen" in title:
            base -= 1

        if "pipeline" in title:
            base += 2

        return base

    def _priority_reason(self, failure):
        severity = failure.get("severity", "UNKNOWN")
        evidence = failure.get("evidence", "No evidence recorded.")

        if severity == "CRITICAL":
            return f"Critical failure blocks design confidence. Evidence: {evidence}"

        if severity == "WARNING":
            return f"Warning-level issue may reduce design confidence. Evidence: {evidence}"

        return f"Informational evidence supports later refinement. Evidence: {evidence}"
