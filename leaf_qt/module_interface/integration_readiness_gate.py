"""
Programme 28K: Engineering Module Integration Readiness Gate.

Checks whether an engineering module is ready across all Programme 28 contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Any, Dict, List, Tuple

from .adapter_contract import EngineeringModuleAdapterContract
from .interface_model import EngineeringModuleInterface
from .notification_contract import EngineeringModuleNotificationContract
from .report_contract import EngineeringModuleReportPackage
from .runtime_contract import EngineeringModuleRuntimeContract
from .storage_contract import EngineeringModuleStorageContract
from .validation_contract import EngineeringModuleValidationResult
from .workflow_contract import EngineeringModuleWorkflowContract


class EngineeringModuleIntegrationVerdict(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class EngineeringModuleIntegrationReadinessResult:
    schema: str
    module_id: str
    verdict: EngineeringModuleIntegrationVerdict
    ready: bool
    blockers: Tuple[str, ...]
    checks: Dict[str, bool]
    mutation_performed: bool = False
    solver_executed: bool = False
    runtime_mutation_performed: bool = False
    storage_mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "module_id": self.module_id,
            "verdict": self.verdict.value,
            "ready": self.ready,
            "blockers": list(self.blockers),
            "checks": dict(self.checks),
            "mutation_performed": self.mutation_performed,
            "solver_executed": self.solver_executed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "storage_mutation_performed": self.storage_mutation_performed,
        }


@dataclass(frozen=True)
class EngineeringModuleIntegrationReadinessGate:
    interface: EngineeringModuleInterface
    adapter_contract: EngineeringModuleAdapterContract
    validation_result: EngineeringModuleValidationResult
    report_package: EngineeringModuleReportPackage
    workflow_contract: EngineeringModuleWorkflowContract
    runtime_contract: EngineeringModuleRuntimeContract
    storage_contract: EngineeringModuleStorageContract
    notification_contract: EngineeringModuleNotificationContract
    dependency_missing_requirements: Tuple[str, ...] = dataclass_field(default_factory=tuple)

    def evaluate(self) -> EngineeringModuleIntegrationReadinessResult:
        blockers: List[str] = []
        checks: Dict[str, bool] = {}

        interface_ok = not self.interface.validate()
        checks["interface_valid"] = interface_ok
        if not interface_ok:
            blockers.append("Engineering module interface validation failed.")

        dependency_ok = not self.dependency_missing_requirements
        checks["dependencies_satisfied"] = dependency_ok
        if not dependency_ok:
            blockers.append(
                "Missing required dependency capabilities: "
                + ", ".join(self.dependency_missing_requirements)
            )

        adapter_ok = not self.adapter_contract.validate_adapter()
        checks["adapter_contract_valid"] = adapter_ok
        if not adapter_ok:
            blockers.append("Engineering module adapter contract validation failed.")

        validation_ok = self.validation_result.passed()
        checks["validation_passed"] = validation_ok
        if not validation_ok:
            blockers.append(
                f"Engineering module validation did not pass: {self.validation_result.verdict().value}"
            )

        report_ok = not self.report_package.validate()
        checks["report_package_valid"] = report_ok
        if not report_ok:
            blockers.append("Engineering module report package validation failed.")

        workflow_ok = not self.workflow_contract.validate_contract()
        checks["workflow_contract_valid"] = workflow_ok
        if not workflow_ok:
            blockers.append("Engineering module workflow contract validation failed.")

        runtime_ok = not self.runtime_contract.validate_contract()
        checks["runtime_contract_valid"] = runtime_ok
        if not runtime_ok:
            blockers.append("Engineering module runtime contract validation failed.")

        storage_ok = not self.storage_contract.validate_contract()
        checks["storage_contract_valid"] = storage_ok
        if not storage_ok:
            blockers.append("Engineering module storage contract validation failed.")

        notification_ok = not self.notification_contract.validate_contract()
        checks["notification_contract_valid"] = notification_ok
        if not notification_ok:
            blockers.append("Engineering module notification contract validation failed.")

        safety_flags_ok = (
            not self.report_package.mutation_performed
            and not self.report_package.solver_executed
            and not self.report_package.runtime_mutation_performed
            and not self.report_package.storage_mutation_performed
        )
        checks["non_mutating_contracts"] = safety_flags_ok
        if not safety_flags_ok:
            blockers.append("One or more module contracts reported unsafe mutation/execution.")

        ready = not blockers

        return EngineeringModuleIntegrationReadinessResult(
            schema="LEAF_ENGINEERING_MODULE_INTEGRATION_READINESS_GATE_PHASE_28K_V1",
            module_id=self.interface.module_id,
            verdict=EngineeringModuleIntegrationVerdict.READY
            if ready
            else EngineeringModuleIntegrationVerdict.BLOCKED,
            ready=ready,
            blockers=tuple(blockers),
            checks=checks,
            mutation_performed=False,
            solver_executed=False,
            runtime_mutation_performed=False,
            storage_mutation_performed=False,
        )

    def report(self) -> Dict[str, Any]:
        result = self.evaluate()
        return {
            "schema": "LEAF_ENGINEERING_MODULE_INTEGRATION_READINESS_REPORT_PHASE_28K_V1",
            "result": result.as_dict(),
            "interface": self.interface.report(),
            "adapter": self.adapter_contract.report(),
            "validation": self.validation_result.as_dict(),
            "report_package": self.report_package.as_dict(),
            "workflow": self.workflow_contract.report(
                current_step_id="run_module_solver",
            ),
            "runtime_contract_validation_failures": list(self.runtime_contract.validate_contract()),
            "storage_contract_validation_failures": list(self.storage_contract.validate_contract()),
            "notification_contract_validation_failures": list(
                self.notification_contract.validate_contract()
            ),
        }


def build_engineering_module_integration_readiness_gate(
    interface: EngineeringModuleInterface,
    adapter_contract: EngineeringModuleAdapterContract,
    validation_result: EngineeringModuleValidationResult,
    report_package: EngineeringModuleReportPackage,
    workflow_contract: EngineeringModuleWorkflowContract,
    runtime_contract: EngineeringModuleRuntimeContract,
    storage_contract: EngineeringModuleStorageContract,
    notification_contract: EngineeringModuleNotificationContract,
    dependency_missing_requirements: Tuple[str, ...] = tuple(),
) -> EngineeringModuleIntegrationReadinessGate:
    return EngineeringModuleIntegrationReadinessGate(
        interface=interface,
        adapter_contract=adapter_contract,
        validation_result=validation_result,
        report_package=report_package,
        workflow_contract=workflow_contract,
        runtime_contract=runtime_contract,
        storage_contract=storage_contract,
        notification_contract=notification_contract,
        dependency_missing_requirements=tuple(dependency_missing_requirements),
    )
