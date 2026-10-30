"""
Programme 28F: Engineering Module Report Contract.

Defines reusable, owned report output for every LEAF engineering module.

Design rules:
- Report ownership only.
- No solver execution.
- No Qt ownership.
- No runtime mutation.
- No storage mutation.
- Reports must expose schema, summary, sections, validation, and safety flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, Iterable, Mapping, Tuple

from .interface_model import EngineeringModuleInterface
from .validation_contract import EngineeringModuleValidationResult


@dataclass(frozen=True)
class EngineeringModuleReportSection:
    section_id: str
    title: str
    payload: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.section_id.strip():
            failures.append("section_id is empty")

        if not self.title.strip():
            failures.append(f"title is empty for section {self.section_id!r}")

        return tuple(failures)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class EngineeringModuleReportPackage:
    schema: str
    module_id: str
    report_id: str
    title: str
    summary: Dict[str, Any]
    sections: Tuple[EngineeringModuleReportSection, ...]
    validation: Dict[str, Any]
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)
    mutation_performed: bool = False
    solver_executed: bool = False
    runtime_mutation_performed: bool = False
    storage_mutation_performed: bool = False

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.schema.strip():
            failures.append("schema is empty")

        if not self.module_id.strip():
            failures.append("module_id is empty")

        if not self.report_id.strip():
            failures.append("report_id is empty")

        if not self.title.strip():
            failures.append("title is empty")

        if "verdict" not in self.validation:
            failures.append("validation verdict missing from report package")

        seen = set()
        for section in self.sections:
            failures.extend(section.validate())
            if section.section_id in seen:
                failures.append(f"duplicate section_id: {section.section_id}")
            seen.add(section.section_id)

        if self.mutation_performed:
            failures.append("report package indicates mutation_performed=True")

        if self.solver_executed:
            failures.append("report package indicates solver_executed=True")

        if self.runtime_mutation_performed:
            failures.append("report package indicates runtime_mutation_performed=True")

        if self.storage_mutation_performed:
            failures.append("report package indicates storage_mutation_performed=True")

        return tuple(failures)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "module_id": self.module_id,
            "report_id": self.report_id,
            "title": self.title,
            "summary": dict(self.summary),
            "sections": [section.as_dict() for section in self.sections],
            "validation": dict(self.validation),
            "metadata": dict(self.metadata),
            "validation_failures": list(self.validate()),
            "mutation_performed": self.mutation_performed,
            "solver_executed": self.solver_executed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "storage_mutation_performed": self.storage_mutation_performed,
        }


@dataclass(frozen=True)
class EngineeringModuleReportContract:
    interface: EngineeringModuleInterface
    report_owner: str = "engineering_module_report_contract"
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate_contract(self) -> Tuple[str, ...]:
        failures = []
        failures.extend(self.interface.validate())

        if not self.report_owner.strip():
            failures.append("report_owner is empty")

        return tuple(failures)

    def build_report(
        self,
        report_id: str,
        title: str,
        validation_result: EngineeringModuleValidationResult,
        sections: Iterable[EngineeringModuleReportSection],
        summary: Mapping[str, Any] | None = None,
    ) -> EngineeringModuleReportPackage:
        section_tuple = tuple(sections)
        validation_payload = validation_result.as_dict()

        package_summary = {
            "module_id": self.interface.module_id,
            "module_title": self.interface.title,
            "module_status": self.interface.status.value,
            "report_owner": self.report_owner,
            "validation_verdict": validation_payload["verdict"],
            "validation_passed": validation_payload["passed"],
            "section_count": len(section_tuple),
            **dict(summary or {}),
        }

        return EngineeringModuleReportPackage(
            schema="LEAF_ENGINEERING_MODULE_REPORT_CONTRACT_PHASE_28F_V1",
            module_id=self.interface.module_id,
            report_id=report_id,
            title=title,
            summary=package_summary,
            sections=section_tuple,
            validation=validation_payload,
            metadata={
                "owner": self.report_owner,
                "phase": "28F",
                "programme": "28",
                **dict(self.metadata),
            },
            mutation_performed=False,
            solver_executed=False,
            runtime_mutation_performed=False,
            storage_mutation_performed=False,
        )

    def report(
        self,
        report_id: str,
        title: str,
        validation_result: EngineeringModuleValidationResult,
        sections: Iterable[EngineeringModuleReportSection],
        summary: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        package = self.build_report(
            report_id=report_id,
            title=title,
            validation_result=validation_result,
            sections=sections,
            summary=summary,
        )
        return {
            "schema": "LEAF_ENGINEERING_MODULE_REPORT_CONTRACT_REPORT_PHASE_28F_V1",
            "contract_validation_failures": list(self.validate_contract()),
            "package": package.as_dict(),
        }


def build_engineering_module_report_contract(
    interface: EngineeringModuleInterface,
    report_owner: str = "engineering_module_report_contract",
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleReportContract:
    return EngineeringModuleReportContract(
        interface=interface,
        report_owner=report_owner,
        metadata=dict(metadata or {}),
    )
