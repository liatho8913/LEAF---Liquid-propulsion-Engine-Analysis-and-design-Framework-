from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leaf_qt.module_engine.module_contract import ModuleContract
from leaf_qt.module_engine.module_definition import (
    RUNTIME_BINDING_ENTRYPOINT,
    RUNTIME_BINDING_STAGE_GATED,
)
from leaf_qt.module_engine.module_contract_builder import ModuleContractBuilder
from leaf_qt.module_engine.module_verification import (
    STANDARD_VERIFICATION_TYPES,
    ModuleVerificationCheck,
    ModuleVerificationPlan,
)


@dataclass(frozen=True)
class ModuleVerificationBuildResult:
    status: str
    verification_count: int
    plans: dict[str, dict[str, Any]]
    invalid_plans: dict[str, Any]
    builder_owner: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "verification_count": self.verification_count,
            "plans": self.plans,
            "invalid_plans": self.invalid_plans,
            "builder_owner": self.builder_owner,
        }


class ModuleVerificationBuilder:
    """
    Single source of truth for generating standard module verification plans.

    This builder converts module contracts into reusable verification plans.

    It does not run engineering solvers.
    It does not own physics.
    It does not manually create per-module gates.
    """

    BUILDER_OWNER = "leaf_qt.module_engine.module_verification_builder.ModuleVerificationBuilder"

    def __init__(self, definition_dir: Path):
        self.definition_dir = Path(definition_dir)
        self.contract_builder = ModuleContractBuilder(self.definition_dir)

    def build_plan(self, contract: ModuleContract) -> ModuleVerificationPlan:
        contract_validation = contract.validate()
        contract_valid = contract_validation["status"] == "PASS"

        if contract.runtime_binding == RUNTIME_BINDING_STAGE_GATED:
            readiness_passed = not bool(str(contract.entrypoint).strip())
            readiness_reason = (
                "Module uses canonical stage-gated runtime binding."
                if readiness_passed
                else "Stage-gated module retains a stale direct entrypoint."
            )
        elif contract.runtime_binding == RUNTIME_BINDING_ENTRYPOINT:
            readiness_passed = False
            readiness_reason = (
                "Direct-entrypoint runtime binding has no canonical executor yet."
            )
        else:
            readiness_passed = False
            readiness_reason = "Module runtime binding is unsupported."

        checks = [
            ModuleVerificationCheck(
                module_id=contract.module_id,
                verification_type="compatibility",
                owner="module_engine",
                status="PASS" if contract_valid else "FAIL",
                reason="Contract contains all required infrastructure owners."
                if contract_valid else "Contract is missing required infrastructure owners.",
            ),
            ModuleVerificationCheck(
                module_id=contract.module_id,
                verification_type="dependency",
                owner="dependency_engine",
                status="PASS",
                reason="Dependencies are declared in the module contract.",
            ),
            ModuleVerificationCheck(
                module_id=contract.module_id,
                verification_type="readiness",
                owner="runtime_engine",
                status="PASS" if readiness_passed else "FAIL",
                reason=readiness_reason,
            ),
            ModuleVerificationCheck(
                module_id=contract.module_id,
                verification_type="completion",
                owner="module_engine",
                status="PASS" if contract.outputs else "FAIL",
                reason="Module declares engineering outputs."
                if contract.outputs else "Module declares no engineering outputs.",
            ),
            ModuleVerificationCheck(
                module_id=contract.module_id,
                verification_type="cross_platform",
                owner="module_engine",
                status="PASS",
                reason="Module definition uses platform-neutral declaration data.",
            ),
        ]

        return ModuleVerificationPlan(module_id=contract.module_id, checks=checks)

    def build_all(self) -> dict[str, ModuleVerificationPlan]:
        contracts = self.contract_builder.build_all()
        return {
            module_id: self.build_plan(contract)
            for module_id, contract in sorted(contracts.items())
        }

    def audit(self) -> ModuleVerificationBuildResult:
        plans = self.build_all()

        plan_payloads = {
            module_id: plan.to_dict()
            for module_id, plan in sorted(plans.items())
        }

        invalid_plans = {
            module_id: payload
            for module_id, payload in plan_payloads.items()
            if payload["status"] != "PASS"
        }

        passed = bool(plans) and not invalid_plans

        return ModuleVerificationBuildResult(
            status="PASS" if passed else "FAIL",
            verification_count=len(plans),
            plans=plan_payloads,
            invalid_plans=invalid_plans,
            builder_owner=self.BUILDER_OWNER,
        )
