class OptimisationProofOwner:
    """
    Owns optimisation proof generation.

    Purpose:
    Explain why the current design is better, worse, or unchanged compared
    with previous persistent design-history iterations.
    """

    def build_proof(self, history):
        history = history if isinstance(history, list) else []

        lines = []
        lines.append("LEAF OPTIMISATION PROOF")
        lines.append("=======================")
        lines.append("")

        if len(history) < 2:
            lines.append("At least two design iterations are required for optimisation proof.")
            return "\n".join(lines)

        previous = history[-2]
        current = history[-1]

        previous_summary = self._safe_dict(previous.get("summary"))
        current_summary = self._safe_dict(current.get("summary"))

        lines.append(f"Compared iteration {previous.get('iteration_number')} to iteration {current.get('iteration_number')}.")
        lines.append("")

        proof_items = []

        proof_items.extend(
            self._compare_count(
                "Warnings",
                previous_summary.get("warning_count"),
                current_summary.get("warning_count"),
                lower_is_better=True,
            )
        )

        proof_items.extend(
            self._compare_count(
                "Critical diagnostics",
                previous_summary.get("critical_diagnostic_count"),
                current_summary.get("critical_diagnostic_count"),
                lower_is_better=True,
            )
        )

        proof_items.extend(
            self._compare_status(
                "Validation status",
                previous_summary.get("validation_status"),
                current_summary.get("validation_status"),
            )
        )

        proof_items.extend(
            self._compare_status(
                "Regen validation status",
                previous_summary.get("regen_validation_status"),
                current_summary.get("regen_validation_status"),
            )
        )

        proof_items.extend(
            self._compare_status(
                "Benchmark status",
                previous_summary.get("benchmark_status"),
                current_summary.get("benchmark_status"),
            )
        )

        if not proof_items:
            lines.append("No optimisation-relevant difference was detected.")
        else:
            for item in proof_items:
                lines.append(f"- {item}")

        lines.append("")
        lines.append("Proof conclusion:")
        lines.append(f"- {self._build_conclusion(previous_summary, current_summary)}")

        return "\n".join(lines)

    def _compare_count(self, label, old, new, lower_is_better=True):
        old_value = self._safe_int(old)
        new_value = self._safe_int(new)

        if old_value == new_value:
            return [f"{label} unchanged: {old_value}."]

        improved = new_value < old_value if lower_is_better else new_value > old_value

        if improved:
            return [f"{label} improved: {old_value} -> {new_value}."]

        return [f"{label} worsened: {old_value} -> {new_value}."]

    def _compare_status(self, label, old, new):
        if old == new:
            return [f"{label} unchanged: {new}."]

        if self._is_fail(old) and self._is_pass(new):
            return [f"{label} improved: {old} -> {new}."]

        if self._is_pass(old) and self._is_fail(new):
            return [f"{label} regressed: {old} -> {new}."]

        return [f"{label} changed: {old} -> {new}."]

    def _build_conclusion(self, previous_summary, current_summary):
        score = 0

        score += self._score_count_change(
            previous_summary.get("warning_count"),
            current_summary.get("warning_count"),
        )

        score += self._score_count_change(
            previous_summary.get("critical_diagnostic_count"),
            current_summary.get("critical_diagnostic_count"),
        )

        score += self._score_status_change(
            previous_summary.get("validation_status"),
            current_summary.get("validation_status"),
        )

        score += self._score_status_change(
            previous_summary.get("regen_validation_status"),
            current_summary.get("regen_validation_status"),
        )

        if score > 0:
            return "The latest iteration is better supported by the available validation evidence."

        if score < 0:
            return "The latest iteration appears worse than the previous iteration and should be treated as a regression."

        return "The latest iteration is not proven better than the previous iteration from available evidence."

    def build_candidate_ranking(self, history):
        history = history if isinstance(history, list) else []

        lines = []
        lines.append("LEAF OPTIMISATION CANDIDATE RANKING")
        lines.append("===================================")
        lines.append("")

        if not history:
            lines.append("No design iterations are available for ranking.")
            return "\n".join(lines)

        scored = []

        for record in history:
            scored.append(
                {
                    "iteration": record.get("iteration_number", "N/A"),
                    "score": self._score_record(record),
                    "summary": self._safe_dict(record.get("summary")),
                }
            )

        scored.sort(key=lambda item: item["score"], reverse=True)

        best = scored[0]
        worst = scored[-1]

        for item in scored:
            lines.append(
                f"Iteration {item['iteration']}: score {item['score']}"
            )

        lines.append("")
        lines.append("Ranking conclusion:")
        lines.append(f"- Best candidate: Iteration {best['iteration']} with score {best['score']}.")
        lines.append(f"- Worst candidate: Iteration {worst['iteration']} with score {worst['score']}.")

        actual_latest = history[-1].get("iteration_number", "N/A")

        if best["iteration"] == actual_latest:
            lines.append("- The latest iteration is currently the best-ranked candidate.")
        else:
            lines.append(
                f"- The latest iteration is NOT the best-ranked candidate. "
                f"Best candidate remains iteration {best['iteration']}."
            )

        return "\n".join(lines)

    def _score_record(self, record):
        breakdown = self._score_record_breakdown(record)
        return breakdown["total_score"]

    def _score_count_change(self, old, new):
        old_value = self._safe_int(old)
        new_value = self._safe_int(new)

        if new_value < old_value:
            return 1

        if new_value > old_value:
            return -1

        return 0

    def _score_status_change(self, old, new):
        if self._is_fail(old) and self._is_pass(new):
            return 2

        if self._is_pass(old) and self._is_fail(new):
            return -2

        return 0

    def _is_pass(self, value):
        text = str(value or "").strip().upper()
        return text in {"PASS", "PASSED", "OK", "VALID", "RECORDED", "COMPLETE"}

    def _is_fail(self, value):
        text = str(value or "").strip().upper()
        return text in {"FAIL", "FAILED", "INVALID", "ERROR", "BLOCKED"}

    def _safe_dict(self, value):
        return value if isinstance(value, dict) else {}

    def _safe_int(self, value):
        try:
            return int(value)
        except Exception:
            return 0

    def _score_record_breakdown(self, record):
        summary = self._safe_dict(record.get("summary"))

        rows = []
        total = 0

        warning_count = self._safe_int(summary.get("warning_count"))
        warning_score = -warning_count
        rows.append(("Warnings", warning_count, warning_score))
        total += warning_score

        critical_count = self._safe_int(summary.get("critical_diagnostic_count"))
        critical_score = -2 * critical_count
        rows.append(("Critical diagnostics", critical_count, critical_score))
        total += critical_score

        validation_status = summary.get("validation_status")
        validation_score = self._score_status(validation_status, pass_score=5, fail_score=-5)
        rows.append(("Validation status", validation_status, validation_score))
        total += validation_score

        regen_status = summary.get("regen_validation_status")
        regen_score = self._score_status(regen_status, pass_score=5, fail_score=-5)
        rows.append(("Regen validation status", regen_status, regen_score))
        total += regen_score

        benchmark_status = summary.get("benchmark_status")
        benchmark_score = self._score_status(benchmark_status, pass_score=3, fail_score=-3)
        rows.append(("Benchmark status", benchmark_status, benchmark_score))
        total += benchmark_score

        return {
            "total_score": total,
            "rows": rows,
        }

    def _score_status(self, value, pass_score, fail_score):
        if self._is_pass(value):
            return pass_score

        if self._is_fail(value):
            return fail_score

        return 0

    def build_score_evidence_table(self, history):
        history = history if isinstance(history, list) else []

        lines = []
        lines.append("LEAF OPTIMISATION SCORE EVIDENCE TABLE")
        lines.append("======================================")
        lines.append("")

        if not history:
            lines.append("No design iterations are available for score evidence.")
            return "\n".join(lines)

        for record in history:
            iteration_number = record.get("iteration_number", "N/A")
            breakdown = self._score_record_breakdown(record)

            lines.append(f"Iteration {iteration_number}")
            lines.append("-" * 30)

            for label, value, score in breakdown["rows"]:
                lines.append(f"{label}: {value} -> score {score}")

            lines.append(f"Total score: {breakdown['total_score']}")
            lines.append("")

        return "\n".join(lines)

    def build_best_candidate_summary(self, history):
        history = history if isinstance(history, list) else []

        if not history:
            return {
                "optimisation_best_candidate_iteration": None,
                "optimisation_best_candidate_score": None,
                "optimisation_latest_iteration": None,
                "optimisation_latest_score": None,
                "optimisation_latest_is_best": False,
                "optimisation_best_candidate_reason": "No design history is available.",
            }

        scored = []

        for record in history:
            scored.append(
                {
                    "iteration": record.get("iteration_number", "N/A"),
                    "score": self._score_record(record),
                }
            )

        scored.sort(key=lambda item: item["score"], reverse=True)

        best = scored[0]
        latest_record = history[-1]
        latest_iteration = latest_record.get("iteration_number", "N/A")
        latest_score = self._score_record(latest_record)

        latest_is_best = best["iteration"] == latest_iteration

        if latest_is_best:
            reason = (
                f"The latest iteration is the best-ranked candidate "
                f"with score {latest_score}."
            )
        else:
            reason = (
                f"The best-ranked candidate is iteration {best['iteration']} "
                f"with score {best['score']}. "
                f"The latest iteration is iteration {latest_iteration} "
                f"with score {latest_score}."
            )

        return {
            "optimisation_best_candidate_iteration": best["iteration"],
            "optimisation_best_candidate_score": best["score"],
            "optimisation_latest_iteration": latest_iteration,
            "optimisation_latest_score": latest_score,
            "optimisation_latest_is_best": latest_is_best,
            "optimisation_best_candidate_reason": reason,
        }

    def build_regression_gate(self, history):
        history = history if isinstance(history, list) else []

        if len(history) < 2:
            return {
                "optimisation_regression_gate_status": "INSUFFICIENT_HISTORY",
                "optimisation_regression_gate_reason": (
                    "At least two iterations are required to detect optimisation regression."
                ),
                "optimisation_regression_detected": False,
            }

        previous = history[-2]
        current = history[-1]

        previous_score = self._score_record(previous)
        current_score = self._score_record(current)

        previous_summary = self._safe_dict(previous.get("summary"))
        current_summary = self._safe_dict(current.get("summary"))

        reasons = []

        if current_score < previous_score:
            reasons.append(
                f"Latest score regressed: {previous_score} -> {current_score}."
            )

        for label, key in (
            ("Validation", "validation_status"),
            ("Regen validation", "regen_validation_status"),
            ("Benchmark", "benchmark_status"),
        ):
            old = previous_summary.get(key)
            new = current_summary.get(key)

            if self._is_pass(old) and self._is_fail(new):
                reasons.append(
                    f"{label} regressed from {old} to {new}."
                )

        best_summary = self.build_best_candidate_summary(history)

        if not best_summary.get("optimisation_latest_is_best"):
            reasons.append(
                best_summary.get(
                    "optimisation_best_candidate_reason",
                    "Latest iteration is not the best-ranked candidate.",
                )
            )

        regression_detected = bool(reasons)

        if regression_detected:
            status = "REGRESSION_DETECTED"
            reason = "\n".join(f"- {item}" for item in reasons)
        else:
            status = "NO_REGRESSION_DETECTED"
            reason = "No optimisation regression detected against the previous iteration."

        return {
            "optimisation_regression_gate_status": status,
            "optimisation_regression_gate_reason": reason,
            "optimisation_regression_detected": regression_detected,
        }

    def build_optimisation_ownership_report(self, history):
        sections = [
            self.build_proof(history),
            self.build_candidate_ranking(history),
            self.build_score_evidence_table(history),
        ]

        best_candidate = self.build_best_candidate_summary(history)
        regression_gate = self.build_regression_gate(history)

        lines = []
        lines.append("LEAF OPTIMISATION OWNERSHIP REPORT")
        lines.append("==================================")
        lines.append("")
        lines.append("Best Candidate Summary:")
        lines.append(f"- Best iteration: {best_candidate.get('optimisation_best_candidate_iteration')}")
        lines.append(f"- Best score: {best_candidate.get('optimisation_best_candidate_score')}")
        lines.append(f"- Latest iteration: {best_candidate.get('optimisation_latest_iteration')}")
        lines.append(f"- Latest score: {best_candidate.get('optimisation_latest_score')}")
        lines.append(f"- Latest is best: {best_candidate.get('optimisation_latest_is_best')}")
        lines.append(f"- Reason: {best_candidate.get('optimisation_best_candidate_reason')}")
        lines.append("")
        lines.append("Regression Gate:")
        lines.append(f"- Status: {regression_gate.get('optimisation_regression_gate_status')}")
        lines.append(regression_gate.get("optimisation_regression_gate_reason"))
        lines.append("")

        return "\n\n".join([*sections, "\n".join(lines)])