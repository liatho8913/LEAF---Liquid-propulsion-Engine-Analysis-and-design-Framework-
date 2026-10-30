"""
LEAF Phase 16N.9
Before/After Geometry Comparison Owner

Builds an auditable before/after comparison between previous geometry
and applied recommendation geometry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GeometryComparisonChange:
    key: str
    before: Any
    after: Any
    delta: float | None = None
    relative_delta: float | None = None


@dataclass
class BeforeAfterComparisonResult:
    available: bool
    status: str
    changes: list[GeometryComparisonChange] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class RegenBeforeAfterComparisonOwnerPhase16N9:
    def compare(self, results: dict[str, Any]) -> BeforeAfterComparisonResult:
        if not isinstance(results, dict):
            return BeforeAfterComparisonResult(
                available=False,
                status="FAIL_BEFORE_AFTER_COMPARISON_INVALID_RESULTS_PHASE_16N9",
                reasons=["Results payload is not a dictionary."],
            )

        before = (
            results.get("phase_16n6_rollback_geometry")
            or results.get("regen_manual_geometry")
            or results.get("regen_geometry_baseline")
            or {}
        )

        after = (
            results.get("regen_ui_applied_geometry")
            or results.get("phase_16n7_applied_geometry")
            or results.get("regen_current_geometry")
            or {}
        )

        reasons: list[str] = []

        if not isinstance(before, dict) or not before:
            reasons.append("Before/manual geometry payload is missing.")

        if not isinstance(after, dict) or not after:
            reasons.append("After/applied geometry payload is missing.")

        if reasons:
            return BeforeAfterComparisonResult(
                available=False,
                status="FAIL_BEFORE_AFTER_COMPARISON_BLOCKED_PHASE_16N9",
                reasons=reasons,
            )

        keys = sorted(set(before.keys()) | set(after.keys()))
        changes: list[GeometryComparisonChange] = []

        for key in keys:
            before_value = before.get(key)
            after_value = after.get(key)

            delta = None
            relative_delta = None

            try:
                b = float(before_value)
                a = float(after_value)
                delta = a - b
                if b != 0.0:
                    relative_delta = delta / b
            except Exception:
                pass

            changes.append(
                GeometryComparisonChange(
                    key=key,
                    before=before_value,
                    after=after_value,
                    delta=delta,
                    relative_delta=relative_delta,
                )
            )

        return BeforeAfterComparisonResult(
            available=True,
            status="PASS_BEFORE_AFTER_COMPARISON_AVAILABLE_PHASE_16N9",
            changes=changes,
            reasons=[],
        )

    def as_text(self, result: BeforeAfterComparisonResult) -> str:
        lines = [
            "REGEN BEFORE / AFTER GEOMETRY COMPARISON",
            "========================================",
            "",
            f"Status: {result.status}",
            f"Available: {result.available}",
            "",
        ]

        if result.reasons:
            lines.append("Reasons:")
            for reason in result.reasons:
                lines.append(f"- {reason}")
            return "\n".join(lines)

        lines.extend([
            "CHANGES",
            "-------",
        ])

        for change in result.changes:
            if change.delta is None:
                lines.append(
                    f"{change.key}: before={change.before} after={change.after}"
                )
            else:
                rel = (
                    "N/A"
                    if change.relative_delta is None
                    else f"{change.relative_delta:.6g}"
                )
                lines.append(
                    f"{change.key}: before={change.before} "
                    f"after={change.after} delta={change.delta:.6g} "
                    f"relative_delta={rel}"
                )

        return "\n".join(lines)


def attach_before_after_comparison_phase_16n9(results: dict[str, Any]) -> dict[str, Any]:
    owner = RegenBeforeAfterComparisonOwnerPhase16N9()
    result = owner.compare(results)

    if not isinstance(results, dict):
        results = {}

    results["phase_16n9_before_after_comparison_status"] = result.status
    results["phase_16n9_before_after_comparison_available"] = result.available
    results["phase_16n9_before_after_comparison_report"] = owner.as_text(result)
    results["phase_16n9_before_after_comparison_reasons"] = list(result.reasons)
    results["phase_16n9_before_after_change_count"] = len(result.changes)

    results["phase_16n9_before_after_changes"] = [
        {
            "key": change.key,
            "before": change.before,
            "after": change.after,
            "delta": change.delta,
            "relative_delta": change.relative_delta,
        }
        for change in result.changes
    ]

    return results
