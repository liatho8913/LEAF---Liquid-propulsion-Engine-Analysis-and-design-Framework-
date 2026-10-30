REQUIRED_RECOMMENDATION_FIELDS = (
    "recommendation",
    "reason",
    "evidence",
    "tradeoff",
    "expected_outcome",
    "risk",
    "confidence",
    "next_action",
    "severity",
    "source",
)


class RecommendationExplanationOwner:
    """
    Owns recommendation explanation generation.

    Stage T.4:
    - builds recommendations
    - validates evidence completeness
    - removes unsupported recommendations
    - deduplicates recommendations
    - ranks recommendations
    - exposes primary recommendation
    """

    CONFIDENCE_SCORE = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    SEVERITY_SCORE = {
        "CRITICAL": 5,
        "ERROR": 4,
        "FAIL": 4,
        "BLOCKED": 3,
        "WARNING": 3,
        "INFO": 1,
        "UNKNOWN": 1,
    }

    def attach(self, results):
        results = results if isinstance(results, dict) else {}

        raw_recommendations = self._build_recommendations(results)
        validated, rejected = self._validate_recommendations(raw_recommendations)
        deduplicated = self._deduplicate(validated)
        prioritised = self._prioritise(deduplicated)

        primary = prioritised[0] if prioritised else None

        results["recommendation_owner_items"] = prioritised
        results["recommendation_owner_rejected_items"] = rejected
        results["recommendation_owner_count"] = len(prioritised)
        results["recommendation_owner_rejected_count"] = len(rejected)
        results["recommendation_owner_status"] = (
            "RECOMMENDATIONS_AVAILABLE" if prioritised else "NO_VALID_RECOMMENDATIONS"
        )
        results["recommendation_owner_evidence_status"] = (
            "EVIDENCE_COMPLETE" if not rejected else "EVIDENCE_REJECTIONS_PRESENT"
        )
        results["recommendation_owner_text"] = self.build_report(prioritised, rejected)

        results["recommendation_owner_primary_recommendation"] = (
            primary.get("recommendation") if primary else "No primary recommendation available."
        )
        results["recommendation_owner_primary_reason"] = (
            primary.get("reason") if primary else "No valid recommendation evidence was generated."
        )
        results["recommendation_owner_primary_priority_score"] = (
            primary.get("priority_score") if primary else 0
        )
        results["recommendation_owner_primary_source"] = (
            primary.get("source") if primary else "NONE"
        )

        return results

    def build_report(self, recommendations=None, rejected=None):
        recommendations = recommendations if isinstance(recommendations, list) else []
        rejected = rejected if isinstance(rejected, list) else []

        lines = [
            "LEAF RECOMMENDATION EVIDENCE REPORT",
            "===================================",
            "",
            f"Valid recommendations: {len(recommendations)}",
            f"Rejected recommendations: {len(rejected)}",
            "",
        ]

        if not recommendations:
            lines.append("No valid recommendations were generated from available evidence.")
            lines.append("")

        for item in recommendations:
            lines.append(f"{item.get('priority_rank', '?')}. {item.get('recommendation')}")
            lines.append(f"   Priority score: {item.get('priority_score')}")
            lines.append(f"   Evidence status: {item.get('evidence_status')}")
            lines.append(f"   Source owner: {item.get('source')}")
            lines.append(f"   Severity: {item.get('severity')}")
            lines.append(f"   Reason: {item.get('reason')}")
            lines.append(f"   Evidence: {item.get('evidence')}")
            lines.append(f"   Tradeoff: {item.get('tradeoff')}")
            lines.append(f"   Expected outcome: {item.get('expected_outcome')}")
            lines.append(f"   Risk: {item.get('risk')}")
            lines.append(f"   Confidence: {item.get('confidence')}")
            lines.append(f"   Next action: {item.get('next_action')}")
            lines.append("")

        if rejected:
            lines.append("Rejected Recommendations")
            lines.append("------------------------")

            for item in rejected:
                lines.append(f"- {item.get('recommendation', 'Unknown recommendation')}")
                lines.append(f"  Rejection reason: {item.get('rejection_reason')}")
                lines.append("")

        return "\n".join(lines)

    def _build_recommendations(self, results):
        recommendations = []

        self._add_from_root_cause(results, recommendations)
        self._add_from_optimisation(results, recommendations)
        self._add_from_warnings(results, recommendations)
        self._add_from_regen_status(results, recommendations)
        self._add_from_audit_status(results, recommendations)

        return recommendations

    def _make_item(
        self,
        recommendation,
        reason,
        evidence,
        tradeoff,
        expected_outcome,
        risk,
        confidence,
        next_action,
        severity="WARNING",
        validation_impact=1,
        ownership_importance=1,
        source="GENERAL",
    ):
        return {
            "recommendation": recommendation,
            "reason": reason,
            "evidence": evidence,
            "tradeoff": tradeoff,
            "expected_outcome": expected_outcome,
            "risk": risk,
            "confidence": confidence,
            "next_action": next_action,
            "severity": severity,
            "validation_impact": validation_impact,
            "ownership_importance": ownership_importance,
            "source": source,
        }

    def _validate_recommendations(self, recommendations):
        valid = []
        rejected = []

        for item in recommendations:
            missing = []

            for field in REQUIRED_RECOMMENDATION_FIELDS:
                value = item.get(field)

                if value is None:
                    missing.append(field)
                    continue

                if isinstance(value, str) and not value.strip():
                    missing.append(field)

            if missing:
                rejected_item = dict(item)
                rejected_item["evidence_status"] = "REJECTED"
                rejected_item["rejection_reason"] = (
                    "Missing required field(s): " + ", ".join(missing)
                )
                rejected.append(rejected_item)
                continue

            checked = dict(item)
            checked["evidence_status"] = "SUPPORTED"
            valid.append(checked)

        return valid, rejected

    def _deduplicate(self, recommendations):
        seen = {}

        for item in recommendations:
            key = str(item.get("recommendation", "")).strip().lower()
            existing = seen.get(key)

            if existing is None:
                seen[key] = item
                continue

            if self._raw_priority_score(item) > self._raw_priority_score(existing):
                seen[key] = item

        return list(seen.values())

    def _prioritise(self, recommendations):
        ranked = sorted(
            recommendations,
            key=self._raw_priority_score,
            reverse=True,
        )

        for index, item in enumerate(ranked, start=1):
            item["priority_rank"] = index
            item["priority_score"] = self._raw_priority_score(item)

        return ranked

    def _raw_priority_score(self, item):
        severity = self.SEVERITY_SCORE.get(str(item.get("severity", "")).upper(), 1)
        confidence = self.CONFIDENCE_SCORE.get(str(item.get("confidence", "")).upper(), 1)
        validation = int(item.get("validation_impact") or 0)
        ownership = int(item.get("ownership_importance") or 0)

        return severity * 10 + confidence * 5 + validation * 4 + ownership * 3

    def _add_from_root_cause(self, results, recommendations):
        if results.get("failure_root_cause_owner_status") != "FAILURES_DETECTED":
            return

        severity = str(
            results.get("failure_root_cause_owner_highest_severity") or "CRITICAL"
        ).upper()

        recommendations.append(
            self._make_item(
                recommendation="Resolve the highest-severity root cause before continuing optimisation.",
                reason=results.get(
                    "failure_root_cause_owner_primary_cause",
                    "A root-cause owner failure was detected.",
                ),
                evidence=results.get(
                    "failure_root_cause_owner_text",
                    "Root-cause evidence is available in the root-cause owner report.",
                ),
                tradeoff="This may slow feature progress, but prevents building optimisation logic on invalid foundations.",
                expected_outcome="The design state becomes easier to validate and future recommendations become more trustworthy.",
                risk="Ignoring root causes may allow invalid designs to appear optimised.",
                confidence=self._confidence_from_severity(severity),
                next_action="Open the Root Cause Ownership Report and complete the first high-priority corrective action.",
                severity=severity,
                validation_impact=5,
                ownership_importance=5,
                source="ROOT_CAUSE_OWNER",
            )
        )

    def _add_from_optimisation(self, results, recommendations):
        if not results.get("optimisation_regression_detected"):
            return

        recommendations.append(
            self._make_item(
                recommendation="Return to the best-ranked optimisation candidate or undo the regressing change.",
                reason="The latest iteration regressed against optimisation evidence.",
                evidence=results.get(
                    "optimisation_regression_gate_reason",
                    "Optimisation regression was detected.",
                ),
                tradeoff="Returning to an earlier candidate may discard recent changes, but preserves validated progress.",
                expected_outcome="The design returns to a stronger optimisation baseline.",
                risk="Continuing from a regressed candidate may compound design problems.",
                confidence="HIGH",
                next_action="Open Optimisation Ownership Report and compare latest candidate against best candidate.",
                severity="FAIL",
                validation_impact=4,
                ownership_importance=4,
                source="OPTIMISATION_OWNER",
            )
        )

    def _add_from_warnings(self, results, recommendations):
        warnings = results.get("warnings")

        if not isinstance(warnings, list) or not warnings:
            return

        recommendations.append(
            self._make_item(
                recommendation="Resolve active warnings before treating the design as final.",
                reason=f"{len(warnings)} warning(s) are active.",
                evidence="; ".join(str(item) for item in warnings[:3]),
                tradeoff="Some warnings may be conservative, but unresolved warnings reduce confidence.",
                expected_outcome="Cleaner validation state and better report confidence.",
                risk="Warnings may represent hidden geometry, thermal, material, or source-quality problems.",
                confidence="MEDIUM",
                next_action="Open the Warnings panel and address warnings in priority order.",
                severity="WARNING",
                validation_impact=3,
                ownership_importance=2,
                source="WARNINGS",
            )
        )

    def _add_from_regen_status(self, results, recommendations):
        status = str(results.get("regen_validation_status") or "").upper()

        if "FAIL" not in status and status not in {"INVALID", "ERROR", "BLOCKED"}:
            return

        recommendations.append(
            self._make_item(
                recommendation="Prioritise regenerative cooling validation before expanding engine features.",
                reason="Regen validation is failing or blocked.",
                evidence=f"regen_validation_status = {results.get('regen_validation_status')}",
                tradeoff="This delays new feature work, but protects LEAF from scaling an invalid thermal foundation.",
                expected_outcome="Thermal, geometry, coolant, and material assumptions become auditable.",
                risk="Invalid regen logic can invalidate engine-level design conclusions.",
                confidence="HIGH",
                next_action="Review regen validation report, station diagnostics, material limits, and geometry fit checks.",
                severity="FAIL",
                validation_impact=5,
                ownership_importance=5,
                source="REGEN_VALIDATION",
            )
        )

    def _add_from_audit_status(self, results, recommendations):
        audit_sources = (
            ("output_ownership_audit_status", "output ownership"),
            ("output_visibility_architecture_status", "output visibility architecture"),
            ("foundation_result_key_audit_status", "foundation result key"),
            ("foundation_attachment_pipeline_status", "foundation attachment pipeline"),
        )

        for key, label in audit_sources:
            status = str(results.get(key) or "").upper()

            if "FAIL" not in status and status not in {"INVALID", "ERROR", "BLOCKED"}:
                continue

            recommendations.append(
                self._make_item(
                    recommendation=f"Repair the {label} failure before adding new systems.",
                    reason=f"{key} is failing.",
                    evidence=f"{key} = {results.get(key)}",
                    tradeoff="Architecture repair takes priority over new physics features.",
                    expected_outcome="Reports, result keys, and ownership routing remain trustworthy.",
                    risk="Bad ownership routing can hide failures or pollute main outputs.",
                    confidence="HIGH",
                    next_action="Open the relevant foundation audit report and fix the first failing row.",
                    severity="FAIL",
                    validation_impact=5,
                    ownership_importance=5,
                    source="FOUNDATION_AUDIT",
                )
            )

    def _confidence_from_severity(self, severity):
        severity = str(severity or "").upper()

        if severity in {"CRITICAL", "ERROR", "FAIL"}:
            return "HIGH"

        if severity == "WARNING":
            return "MEDIUM"

        return "LOW"