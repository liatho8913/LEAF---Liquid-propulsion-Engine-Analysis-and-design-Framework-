"""
Canonical LEAF engineering-module validation contract.

This module owns the shared validation infrastructure used by engineering
modules.

It defines:
- validation modes
- validation severities
- validation verdicts
- structured validation findings
- reusable validation results
- reusable validation contracts
- placeholder-data PASS prevention

It does not own:
- engineering-specific validation rules
- engineering physics
- repository-architecture validation
- Qt/UI behaviour
- report transport
- runtime or storage mutation

Engineering modules provide their domain-specific findings and requirements
through this shared contract rather than creating new validation frameworks.

Historical domain validators may remain during migration, but new engineering
modules must use this contract as the canonical validation infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from .interface_model import EngineeringModuleInterface


class EngineeringModuleValidationMode(str, Enum):
    PLACEHOLDER_MODE = "PLACEHOLDER_MODE"
    PARTIAL_SOURCE_MODE = "PARTIAL_SOURCE_MODE"
    SOURCED_VALIDATION_MODE = "SOURCED_VALIDATION_MODE"


class EngineeringModuleValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKING = "BLOCKING"


class EngineeringModuleValidationVerdict(str, Enum):
    PASS_ = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class EngineeringModuleValidationFinding:
    finding_id: str
    severity: EngineeringModuleValidationSeverity
    message: str
    source: str = "module_validation"
    field: str | None = None
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.finding_id.strip():
            failures.append("finding_id is empty")

        if not isinstance(self.severity, EngineeringModuleValidationSeverity):
            failures.append(f"invalid severity for finding {self.finding_id!r}: {self.severity!r}")

        if not self.message.strip():
            failures.append(f"message is empty for finding {self.finding_id!r}")

        if not self.source.strip():
            failures.append(f"source is empty for finding {self.finding_id!r}")

        return failures

    def as_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "field": self.field,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class EngineeringModuleValidationResult:
    module_id: str
    validation_mode: EngineeringModuleValidationMode
    findings: Tuple[EngineeringModuleValidationFinding, ...] = dataclass_field(default_factory=tuple)
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.module_id.strip():
            failures.append("module_id is empty")

        if not isinstance(self.validation_mode, EngineeringModuleValidationMode):
            failures.append(f"invalid validation_mode: {self.validation_mode!r}")

        for finding in self.findings:
            failures.extend(finding.validate())

        return failures

    def severity_counts(self) -> Dict[str, int]:
        counts = {severity.value: 0 for severity in EngineeringModuleValidationSeverity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts

    def verdict(self) -> EngineeringModuleValidationVerdict:
        counts = self.severity_counts()

        if self.validation_mode == EngineeringModuleValidationMode.PLACEHOLDER_MODE:
            return EngineeringModuleValidationVerdict.BLOCKED

        if counts["BLOCKING"] > 0:
            return EngineeringModuleValidationVerdict.BLOCKED

        if counts["ERROR"] > 0:
            return EngineeringModuleValidationVerdict.FAIL

        if counts["WARNING"] > 0:
            return EngineeringModuleValidationVerdict.WARNING

        return EngineeringModuleValidationVerdict.PASS_

    def passed(self) -> bool:
        return self.verdict() == EngineeringModuleValidationVerdict.PASS_

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_ENGINEERING_MODULE_VALIDATION_RESULT_PHASE_28E_V1",
            "module_id": self.module_id,
            "validation_mode": self.validation_mode.value,
            "verdict": self.verdict().value,
            "passed": self.passed(),
            "finding_count": len(self.findings),
            "severity_counts": self.severity_counts(),
            "validation_failures": self.validate(),
            "findings": [finding.as_dict() for finding in self.findings],
            "metadata_keys": sorted(self.metadata.keys()),
        }


@dataclass(frozen=True)
class EngineeringModuleValidationContract:
    interface: EngineeringModuleInterface
    validation_mode: EngineeringModuleValidationMode
    required_fields: Tuple[str, ...] = dataclass_field(default_factory=tuple)
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate_contract(self) -> List[str]:
        failures: List[str] = []
        failures.extend(self.interface.validate())

        if not isinstance(self.validation_mode, EngineeringModuleValidationMode):
            failures.append(f"invalid validation_mode: {self.validation_mode!r}")

        if not self.required_fields:
            failures.append("validation contract has no required fields")

        return failures

    def evaluate(
        self,
        provided_fields: Iterable[str],
        external_findings: Iterable[EngineeringModuleValidationFinding] | None = None,
    ) -> EngineeringModuleValidationResult:
        provided = set(provided_fields)
        findings: List[EngineeringModuleValidationFinding] = []

        for failure in self.validate_contract():
            findings.append(
                EngineeringModuleValidationFinding(
                    finding_id=f"contract_failure_{len(findings)+1}",
                    severity=EngineeringModuleValidationSeverity.BLOCKING,
                    message=failure,
                    source="validation_contract",
                )
            )

        for field_name in self.required_fields:
            if field_name not in provided:
                findings.append(
                    EngineeringModuleValidationFinding(
                        finding_id=f"missing_required_field_{field_name}",
                        severity=EngineeringModuleValidationSeverity.ERROR,
                        message=f"Required validation field is missing: {field_name}",
                        source="validation_contract",
                        field=field_name,
                    )
                )

        findings.extend(tuple(external_findings or ()))

        if self.validation_mode == EngineeringModuleValidationMode.PLACEHOLDER_MODE:
            findings.append(
                EngineeringModuleValidationFinding(
                    finding_id="placeholder_mode_blocks_pass",
                    severity=EngineeringModuleValidationSeverity.BLOCKING,
                    message="PLACEHOLDER_MODE cannot produce PASS.",
                    source="validation_contract",
                )
            )

        return EngineeringModuleValidationResult(
            module_id=self.interface.module_id,
            validation_mode=self.validation_mode,
            findings=tuple(findings),
            metadata={
                "required_fields": list(self.required_fields),
                **dict(self.metadata),
            },
        )

    def report(
        self,
        provided_fields: Iterable[str],
        external_findings: Iterable[EngineeringModuleValidationFinding] | None = None,
    ) -> Dict[str, Any]:
        result = self.evaluate(
            provided_fields=provided_fields,
            external_findings=external_findings,
        )
        return {
            "schema": "LEAF_ENGINEERING_MODULE_VALIDATION_CONTRACT_PHASE_28E_V1",
            "module_id": self.interface.module_id,
            "interface": self.interface.report(),
            "required_fields": list(self.required_fields),
            "validation_mode": self.validation_mode.value,
            "result": result.as_dict(),
            "mutation_performed": False,
            "solver_executed": False,
            "runtime_mutation_performed": False,
            "storage_mutation_performed": False,
        }


def build_engineering_module_validation_contract(
    interface: EngineeringModuleInterface,
    validation_mode: EngineeringModuleValidationMode,
    required_fields: Iterable[str],
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleValidationContract:
    return EngineeringModuleValidationContract(
        interface=interface,
        validation_mode=validation_mode,
        required_fields=tuple(required_fields),
        metadata=dict(metadata or {}),
    )
