from dataclasses import dataclass, field


@dataclass
class DesignAttempt:
    attempt_id: int
    name: str
    status: str = "UNKNOWN"
    changed: list = field(default_factory=list)
    passed: list = field(default_factory=list)
    failed: list = field(default_factory=list)
    reasons: list = field(default_factory=list)
    improvements: list = field(default_factory=list)
    next_actions: list = field(default_factory=list)


@dataclass
class DesignIterationNarrative:
    title: str = "LEAF DESIGN ITERATION NARRATIVE"
    attempts: list = field(default_factory=list)

    def add_attempt(self, attempt):
        self.attempts.append(attempt)

    def has_attempts(self):
        return bool(self.attempts)

    def to_dict(self):
        return {
            "title": self.title,
            "attempts": [
                {
                    "attempt_id": attempt.attempt_id,
                    "name": attempt.name,
                    "status": attempt.status,
                    "changed": attempt.changed,
                    "passed": attempt.passed,
                    "failed": attempt.failed,
                    "reasons": attempt.reasons,
                    "improvements": attempt.improvements,
                    "next_actions": attempt.next_actions,
                }
                for attempt in self.attempts
            ],
        }

    def to_text(self):
        lines = []
        lines.append(self.title)
        lines.append("=" * len(self.title))
        lines.append("")

        if not self.attempts:
            lines.append("No design attempts recorded.")
            return "\n".join(lines)

        for attempt in self.attempts:
            lines.append(f"Attempt {attempt.attempt_id}: {attempt.name}")
            lines.append(f"Status: {attempt.status}")
            lines.append("")

            _append_list(lines, "What changed", attempt.changed)
            _append_list(lines, "What passed", attempt.passed)
            _append_list(lines, "What failed", attempt.failed)
            _append_list(lines, "Reasons", attempt.reasons)
            _append_list(lines, "What improved", attempt.improvements)
            _append_list(lines, "Next recommended actions", attempt.next_actions)

            lines.append("-" * 50)
            lines.append("")

        return "\n".join(lines)


def _append_list(lines, title, items):
    lines.append(title + ":")

    if not items:
        lines.append("- None recorded.")
    else:
        for item in items:
            lines.append(f"- {item}")

    lines.append("")


def _truthy_pass(value):
    return value in (True, 1, "1", "PASS", "pass", "Pass", "TRUE", "true")


def _status_from_pass(value):
    return "PASS" if _truthy_pass(value) else "FAIL"


def build_regen_design_iteration_narrative(results):
    results = results if isinstance(results, dict) else {}

    narrative = DesignIterationNarrative()

    # Attempt 1 — Manual geometry
    manual_status = results.get("channel_geometry_valid")
    manual_attempt = DesignAttempt(
        attempt_id=1,
        name="Manual Regen Geometry",
        status=_status_from_pass(manual_status),
    )

    manual_attempt.changed.append("Used user/manual coolant channel geometry inputs.")

    if _truthy_pass(manual_status):
        manual_attempt.passed.append("Manual channel geometry fits the available circumference.")
    else:
        manual_attempt.failed.append("Manual channel geometry does not fully pass the fit gate.")
        manual_attempt.reasons.append(
            "Manual channel count, width, rib width, or pitch may not fit the local circumference."
        )
        manual_attempt.next_actions.append(
            "Try recommended or variable regen geometry sizing."
        )

    narrative.add_attempt(manual_attempt)

    # Attempt 2 — Recommended geometry
    recommended_status = results.get("recommended_geometry_status")
    recommended_pass = results.get("recommended_geometry_valid")

    recommended_attempt = DesignAttempt(
        attempt_id=2,
        name="Recommended Regen Geometry",
        status=str(recommended_status or _status_from_pass(recommended_pass)),
    )

    recommended_attempt.changed.append("LEAF generated a recommended coolant channel geometry.")

    if str(recommended_status).upper() == "PASS" or _truthy_pass(recommended_pass):
        recommended_attempt.passed.append("Recommended geometry passes the geometry fit gate.")
        recommended_attempt.improvements.append("Geometry was automatically adjusted from manual inputs.")
    else:
        recommended_attempt.failed.append("Recommended geometry did not fully pass all required gates.")
        recommended_attempt.reasons.append(
            str(results.get("recommended_geometry_reason") or "No detailed recommended-geometry reason was recorded.")
        )
        recommended_attempt.next_actions.append(
            "Use full-engine regen validation and best-available selector."
        )

    narrative.add_attempt(recommended_attempt)

    # Attempt 3 — Full-engine regen validation
    full_status = results.get("full_engine_regen_geometry_status")
    full_pass = results.get("full_engine_regen_geometry_pass")

    full_attempt = DesignAttempt(
        attempt_id=3,
        name="Full-Engine Regen Validation",
        status=str(full_status or _status_from_pass(full_pass)),
    )

    full_attempt.changed.append("Checked regen behaviour across the full axial station set.")

    failed_fit = results.get("full_engine_regen_failed_fit_count")
    failed_re = results.get("full_engine_regen_failed_reynolds_count")
    failed_velocity = results.get("full_engine_regen_failed_velocity_count")
    failed_thermal = results.get("full_engine_regen_failed_thermal_count")

    if _truthy_pass(full_pass) or str(full_status).upper() == "PASS":
        full_attempt.passed.append("Full-engine regen geometry validation passes.")
    else:
        full_attempt.failed.append("Full-engine regen validation did not fully pass.")

        if failed_fit is not None:
            full_attempt.reasons.append(f"Failed fit station count: {failed_fit}.")
        if failed_re is not None:
            full_attempt.reasons.append(f"Failed Reynolds station count: {failed_re}.")
        if failed_velocity is not None:
            full_attempt.reasons.append(f"Failed velocity station count: {failed_velocity}.")
        if failed_thermal is not None:
            full_attempt.reasons.append(f"Failed thermal station count: {failed_thermal}.")

        full_attempt.next_actions.append(
            "Use best full-engine selector or revise material, channel sizing, coolant assumptions, or thermal limits."
        )

    narrative.add_attempt(full_attempt)

    # Attempt 4 — Best available selector
    best_status = results.get("best_full_engine_regen_status")
    best_pass = results.get("best_full_engine_regen_pass")

    best_attempt = DesignAttempt(
        attempt_id=4,
        name="Best Full-Engine Regen Candidate",
        status=str(best_status or _status_from_pass(best_pass)),
    )

    best_attempt.changed.append("LEAF selected the best available regen candidate from available options.")

    best_reason = results.get("best_full_engine_regen_reason")

    if _truthy_pass(best_pass) or str(best_status).upper() == "PASS":
        best_attempt.passed.append("Best available full-engine regen candidate passes.")
        best_attempt.improvements.append("A candidate was found that satisfies the available validation gates.")
    else:
        best_attempt.failed.append("Best available candidate still does not fully pass.")
        best_attempt.reasons.append(str(best_reason or "No best-candidate reason was recorded."))
        best_attempt.next_actions.append(
            "Treat this as an honest failure or fail-best-available condition, not a validated pass."
        )

    narrative.add_attempt(best_attempt)

    return narrative


def attach_regen_design_iteration_narrative(results):
    if results is None:
        return results

    narrative = build_regen_design_iteration_narrative(results)

    results["design_iteration_narrative"] = narrative.to_dict()
    results["design_iteration_narrative_text"] = narrative.to_text()
    results["design_iteration_attempt_count"] = len(narrative.attempts)
    results["design_iteration_narrative_status"] = (
        "RECORDED" if narrative.has_attempts() else "EMPTY"
    )

    return results