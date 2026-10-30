from __future__ import annotations

from typing import Any, Iterable, Mapping

from leaf_qt.structured_status_access import (
    aggregate_status,
    canonical_status,
    findings_highest_severity,
    highest_severity,
    interpret_status,
    is_fail,
    is_pass,
    is_warn,
    payload_status,
    should_block,
)


def solver_status(value: Any) -> str:
    return canonical_status(value)


def solver_pass(value: Any) -> bool:
    return is_pass(value)


def solver_warn(value: Any) -> bool:
    return is_warn(value)


def solver_fail(value: Any) -> bool:
    return is_fail(value)


def solver_blocks(value: Any) -> bool:
    return should_block(value)


def solver_payload_status(payload: Mapping[str, Any]) -> str:
    return payload_status(payload)


def solver_aggregate_status(values: Iterable[Any]) -> str:
    return aggregate_status(values)


def solver_highest_severity(values: Iterable[Any]) -> str:
    return highest_severity(values)


def solver_findings_highest_severity(findings: Iterable[Mapping[str, Any]]) -> str:
    return findings_highest_severity(findings)


def solver_status_record(value: Any, *, source: str = "solver") -> dict[str, Any]:
    interpreted = interpret_status(value, source=source)
    return {
        "raw": interpreted.raw,
        "canonical": interpreted.canonical,
        "severity": interpreted.severity,
        "passed": interpreted.passed,
        "warning": interpreted.warning,
        "failed": interpreted.failed,
        "blocked": interpreted.blocked,
        "source": interpreted.source,
    }
