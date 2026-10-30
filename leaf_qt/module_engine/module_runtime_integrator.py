from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from leaf_qt.module_engine.module_contract_builder import ModuleContractBuilder
from leaf_qt.module_engine.module_definition_loader import ModuleDefinitionLoader
from leaf_qt.module_engine.module_runtime_manifest import (
    ACTIVE,
    BLOCKED,
    DEPENDENCY_DEACTIVATED,
    USER_DEACTIVATED,
    ModuleRuntimeManifest,
    ModuleRuntimeRecord,
)
from leaf_qt.module_engine.module_verification_builder import ModuleVerificationBuilder


@dataclass(frozen=True)
class ModuleRuntimeIntegrationResult:
    status: str
    manifest: dict[str, Any]
    integrator_owner: str
    manual_runtime_binding_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "manifest": self.manifest,
            "integrator_owner": self.integrator_owner,
            "manual_runtime_binding_required": self.manual_runtime_binding_required,
        }


class ModuleRuntimeIntegrator:
    INTEGRATOR_OWNER = "leaf_qt.module_engine.module_runtime_integrator.ModuleRuntimeIntegrator"

    def __init__(self, definition_dir: Path):
        self.definition_dir = Path(definition_dir)
        self.definition_loader = ModuleDefinitionLoader(self.definition_dir)
        self.contract_builder = ModuleContractBuilder(self.definition_dir)
        self.verification_builder = ModuleVerificationBuilder(self.definition_dir)

    def _definition_path(self, module_id: str) -> Path:
        return self.definition_loader.definition_path(
            module_id
        )

    def set_module_enabled(self, module_id: str, enabled: bool) -> dict[str, Any]:
        try:
            path = self._definition_path(
                module_id
            )
        except KeyError:
            return {
                "status": "FAIL",
                "reason": f"Unknown module: {module_id}",
            }

        before = self.build_manifest().records[module_id]
        if enabled and before.activation_status == DEPENDENCY_DEACTIVATED:
            return {
                "status": "BLOCKED",
                "module_id": module_id,
                "reason": before.activation_reason,
            }

        data = json.loads(path.read_text(encoding="utf-8"))
        data["enabled"] = bool(enabled)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        after = self.build_manifest().records[module_id]
        return {
            "status": "PASS",
            "module_id": module_id,
            "enabled": after.enabled,
            "activation_status": after.activation_status,
            "activation_reason": after.activation_reason,
        }

    def _activation_states(self, contracts: dict[str, Any]) -> dict[str, tuple[str, str]]:
        states = {
            module_id: (
                ACTIVE if getattr(contract, "enabled", True) else USER_DEACTIVATED,
                "Module enabled." if getattr(contract, "enabled", True) else "User disabled this module in its module definition.",
            )
            for module_id, contract in contracts.items()
        }

        changed = True
        while changed:
            changed = False
            for module_id, contract in contracts.items():
                if states[module_id][0] == USER_DEACTIVATED:
                    continue

                required = list(getattr(contract, "requires_modules", []) or [])
                missing = [item for item in required if item not in contracts]
                inactive = [item for item in required if item in states and states[item][0] != ACTIVE]

                if missing or inactive:
                    new_state = (
                        DEPENDENCY_DEACTIVATED,
                        f"Required modules unavailable or inactive. missing={missing}; inactive={inactive}",
                    )
                    if states[module_id] != new_state:
                        states[module_id] = new_state
                        changed = True

        return states

    def build_manifest(self) -> ModuleRuntimeManifest:
        contracts = self.contract_builder.build_all()
        verification = self.verification_builder.audit()
        activation = self._activation_states(contracts)
        records: dict[str, ModuleRuntimeRecord] = {}

        for module_id, contract in sorted(contracts.items()):
            plan = verification.plans.get(module_id, {})
            verification_status = plan.get("status", "FAIL")
            runtime_status = "READY" if verification_status == "PASS" else "BLOCKED"
            activation_status, activation_reason = activation[module_id]

            if runtime_status == "BLOCKED":
                activation_status = BLOCKED
                activation_reason = "Runtime verification failed."

            records[module_id] = ModuleRuntimeRecord(
                module_id=module_id,
                module_name=contract.module_name,
                domain=contract.domain,
                version=contract.version,
                entrypoint=contract.entrypoint,
                runtime_binding=contract.runtime_binding,
                engineering_owner=contract.engineering_owner,
                runtime_owner=contract.contract_owners.get("runtime", "runtime_engine"),
                verification_status=verification_status,
                runtime_status=runtime_status,
                outputs=list(contract.outputs),
                dependencies=list(contract.dependencies),
                enabled=getattr(contract, "enabled", True),
                requires_modules=list(getattr(contract, "requires_modules", []) or []),
                activation_status=activation_status,
                activation_reason=activation_reason,
            )

        return ModuleRuntimeManifest(records)


    def execution_policy(self) -> dict[str, bool]:
        """
        Canonical engineering execution projection.

        This does not own solver behaviour. It projects the existing
        activation/dependency state into the boolean policy consumed by
        calculation orchestration and engineering stage gates.
        """
        manifest = self.build_manifest()
        return {
            module_id: record.activation_status == ACTIVE
            for module_id, record in sorted(manifest.records.items())
        }


    def exposed_methods(self) -> dict[str, list[str]]:
        """
        Canonical LEAF method exposure surface.

        Only Active modules expose methods.
        UserDeactivated, DependencyDeactivated, and Blocked modules expose nothing.
        """
        manifest = self.build_manifest()
        return {
            module_id: record.active_outputs
            for module_id, record in sorted(manifest.records.items())
            if record.active_outputs
        }

    def _dependency_projection(
        self,
        manifest: ModuleRuntimeManifest,
    ) -> dict[str, dict[str, list[str]]]:
        """
        Derive reverse and transitive dependency visibility
        from the canonical requires_modules relationships.

        This is projection only. It owns no independent
        dependency state or activation state.
        """
        required_by = {
            module_id: []
            for module_id
            in manifest.records
        }

        for (
            dependent_id,
            record,
        ) in sorted(
            manifest.records.items()
        ):
            for provider_id in (
                record.requires_modules
                or []
            ):
                if (
                    provider_id
                    in required_by
                ):
                    required_by[
                        provider_id
                    ].append(
                        dependent_id
                    )

        for module_id in required_by:
            required_by[
                module_id
            ] = sorted(
                set(
                    required_by[
                        module_id
                    ]
                )
            )

        cascade = {}

        for module_id in sorted(
            manifest.records
        ):
            found = set()
            pending = list(
                required_by.get(
                    module_id,
                    []
                )
            )

            while pending:
                dependent_id = (
                    pending.pop()
                )

                if (
                    dependent_id
                    in found
                ):
                    continue

                found.add(
                    dependent_id
                )

                pending.extend(
                    required_by.get(
                        dependent_id,
                        []
                    )
                )

            # A malformed circular dependency must never
            # report the originating module as its own
            # cascade consequence.
            found.discard(
                module_id
            )

            cascade[
                module_id
            ] = sorted(
                found
            )

        return {
            "required_by_modules":
                required_by,

            "cascade_consequences":
                cascade,
        }

    def module_status_table(
        self,
    ) -> list[dict[str, Any]]:
        """
        Canonical runtime/UI status projection for every
        discovered module.

        Qt and other consumers should display this state
        rather than reconstructing module availability,
        dependency relationships, or activation reasons.
        """
        manifest = (
            self.build_manifest()
        )

        dependency_projection = (
            self._dependency_projection(
                manifest
            )
        )

        required_by = (
            dependency_projection[
                "required_by_modules"
            ]
        )

        cascade = (
            dependency_projection[
                "cascade_consequences"
            ]
        )

        return [
            {
                "module_id":
                    module_id,

                "module_name":
                    record.module_name,

                "activation_status":
                    record.activation_status,

                "runtime_status":
                    record.runtime_status,

                "runtime_binding":
                    record.runtime_binding,

                "enabled":
                    record.enabled,

                "can_user_activate":
                    record.can_user_activate,

                "activation_reason":
                    record.activation_reason,

                "active_outputs":
                    len(
                        record.active_outputs
                    ),

                "requires_modules":
                    list(
                        record.requires_modules
                        or []
                    ),

                "required_by_modules":
                    list(
                        required_by.get(
                            module_id,
                            []
                        )
                    ),

                "cascade_consequences":
                    list(
                        cascade.get(
                            module_id,
                            []
                        )
                    ),
            }
            for (
                module_id,
                record,
            ) in sorted(
                manifest.records.items()
            )
        ]


    def availability_surface(self) -> dict[str, Any]:
        """
        Canonical LEAF runtime/UI availability surface.

        This is the public projection LEAF should use when deciding which
        module capabilities are visible or callable.
        """
        manifest = self.build_manifest()
        exposed = self.exposed_methods()

        return {
            "owner": self.INTEGRATOR_OWNER,
            "module_count": len(manifest.records),
            "active_modules": manifest.active_ids(),
            "deactivated_modules": manifest.deactivated_ids(),
            "available_methods": exposed,
            "status_table": self.module_status_table(),
        }

    def audit(self) -> ModuleRuntimeIntegrationResult:
        manifest = self.build_manifest()
        return ModuleRuntimeIntegrationResult(
            status=manifest.status(),
            manifest=manifest.to_dict(),
            integrator_owner=self.INTEGRATOR_OWNER,
            manual_runtime_binding_required=False,
        )
