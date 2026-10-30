from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from leaf_qt.structured_status_access import canonical_status, is_fail, is_pass, is_warn


@dataclass(frozen=True)
class StatusPresentation:
    raw_status: str
    canonical_status: str
    display_text: str
    severity: str
    colour_role: str
    icon: str
    badge: str
    is_positive: bool
    is_negative: bool
    is_attention: bool
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PASS_LIKE = {
    "PASS",
    "PASSED",
    "VALID",
    "TRUE",
    "READY",
    "COMPLETE",
    "COMPLETED",
    "OK",
}

WARN_LIKE = {
    "WARN",
    "WARNING",
    "REVIEW",
    "REVIEW_REQUIRED",
    "PARTIAL",
    "MARGINAL",
    "PLAUSIBLE",
    "CHECK",
    "UNKNOWN",
}

FAIL_LIKE = {
    "FAIL",
    "FAILED",
    "INVALID",
    "BLOCKED",
    "ERROR",
    "NOT_RUN",
    "NONE",
    "MISSING",
}


def normalise_status_text(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, bool):
        return "PASS" if value else "FAIL"
    return str(value).strip().upper() or "UNKNOWN"


def status_severity(status: object) -> str:
    """Return the presentation severity for an exact LEAF status code.

    This is intentionally broader than the original PASS/WARN/FAIL-only helper.

    It preserves exact status-code ownership while allowing presentation code to
    ask only for the display severity. Exact codes such as
    PASS_REGEN_CONVERGENCE_MASTER_GATE_CONVERGED must remain exact-code logic
    when state-machine decisions depend on them.

    Returned severities:
        PASS
        WARN
        FAIL
        BLOCKED
        ERROR
        UNKNOWN
    """
    text = str(status or "").strip().upper()

    if not text:
        return "UNKNOWN"

    if text.startswith("PASS"):
        return "PASS"

    if text.startswith("WARN") or text.startswith("WARNING"):
        return "WARN"

    if text.startswith("FAIL") or text.startswith("FAILED"):
        return "FAIL"

    if text.startswith("BLOCKED"):
        return "BLOCKED"

    if text.startswith("ERROR") or text.startswith("EXCEPTION"):
        return "ERROR"

    return "UNKNOWN"
def status_colour_role(value: Any) -> str:
    severity = status_severity(value)
    return {
        "PASS": "success",
        "WARN": "warning",
        "FAIL": "danger",
        "UNKNOWN": "neutral",
    }.get(severity, "neutral")


def status_icon(value: Any) -> str:
    severity = status_severity(value)
    return {
        "PASS": "✓",
        "WARN": "!",
        "FAIL": "✕",
        "UNKNOWN": "?",
    }.get(severity, "?")


def display_status(value: Any) -> str:
    text = normalise_status_text(value)
    severity = status_severity(text)

    if severity == "PASS":
        return "PASS"
    if severity == "WARN":
        return "REVIEW"
    if severity == "FAIL":
        return "FAIL"
    return text.replace("_", " ")


def status_badge(value: Any) -> str:
    severity = status_severity(value)
    icon = status_icon(value)
    label = display_status(value)
    return f"{icon} {label}"


def present_status(value: Any) -> StatusPresentation:
    raw = normalise_status_text(value)
    canonical = canonical_status(raw)
    severity = status_severity(raw)

    return StatusPresentation(
        raw_status=raw,
        canonical_status=canonical,
        display_text=display_status(raw),
        severity=severity,
        colour_role=status_colour_role(raw),
        icon=status_icon(raw),
        badge=status_badge(raw),
        is_positive=severity == "PASS",
        is_negative=severity == "FAIL",
        is_attention=severity in {"WARN", "UNKNOWN"},
        explanation=f"Status '{raw}' is presented as {severity}.",
    )


def present_finding(finding: Mapping[str, Any]) -> StatusPresentation:
    if "severity" in finding:
        return present_status(finding.get("severity"))
    if "status" in finding:
        return present_status(finding.get("status"))
    if "passed" in finding:
        return present_status(bool(finding.get("passed")))
    return present_status("UNKNOWN")


def report_state_filter_options() -> list[str]:
    return ["FAIL", "WARN", "PASS", "UNKNOWN", "NOT_AVAILABLE"]


def should_show_for_filter(value: Any, selected_filter: str) -> bool:
    selected = normalise_status_text(selected_filter)
    if selected in {"ALL", "*"}:
        return True
    if selected == "NOT_AVAILABLE":
        return normalise_status_text(value) in {"NOT_AVAILABLE", "NONE", "MISSING", "UNKNOWN"}
    return status_severity(value) == selected


class StructuredStatusRenderer:
    @staticmethod
    def present(value: Any) -> StatusPresentation:
        return present_status(value)

    @staticmethod
    def text(value: Any) -> str:
        return display_status(value)

    @staticmethod
    def badge(value: Any) -> str:
        return status_badge(value)

    @staticmethod
    def severity(value: Any) -> str:
        return status_severity(value)


class StatusVisualStyle:
    @staticmethod
    def colour_role(value: Any) -> str:
        return status_colour_role(value)

    @staticmethod
    def icon(value: Any) -> str:
        return status_icon(value)


class ReportStatusPresenter:
    @staticmethod
    def render_label(name: str, value: Any) -> str:
        return f"{name}: {status_badge(value)}"

    @staticmethod
    def render_check(check: Mapping[str, Any]) -> str:
        name = str(check.get("name", "Unnamed check"))
        if "status" in check:
            return ReportStatusPresenter.render_label(name, check.get("status"))
        if "passed" in check:
            return ReportStatusPresenter.render_label(name, bool(check.get("passed")))
        return ReportStatusPresenter.render_label(name, "UNKNOWN")


class ReportFilterModel:
    @staticmethod
    def options() -> list[str]:
        return report_state_filter_options()

    @staticmethod
    def accepts(value: Any, selected_filter: str) -> bool:
        return should_show_for_filter(value, selected_filter)


class LegacyCompatibilityProducer:
    @staticmethod
    def status_from_bool(passed: bool) -> str:
        return "PASS" if bool(passed) else "FAIL"

    @staticmethod
    def marker_from_bool(passed: bool) -> str:
        return "PASS" if bool(passed) else "FAIL"
