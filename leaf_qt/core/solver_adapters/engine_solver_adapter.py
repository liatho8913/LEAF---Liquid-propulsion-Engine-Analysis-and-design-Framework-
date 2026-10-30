from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from core.contracts.base_contracts import SolverContract


@dataclass
class EngineSolverReadOnlyAdapter(SolverContract):
    """
    Read-only SolverContract adapter for LEAF's existing engine solver.

    This adapter intentionally does not modify engine_solver.py.
    It wraps a supplied callable so the legacy solver can be accessed through
    the new stable SolverContract interface.
    """

    solver_callable: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    subsystem_name: str = "ENGINE_SOLVER"
    adapter_version: str = "1.0"
    evidence: dict[str, Any] = field(default_factory=dict)

    def contract_metadata(self) -> Mapping[str, Any]:
        return {
            "subsystem": self.subsystem_name,
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
            "adapter_version": self.adapter_version,
            "mode": "READ_ONLY_ADAPTER",
            "mutates_legacy_solver": False,
        }

    def solve(self, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        result = self.solver_callable(dict(inputs))

        if not isinstance(result, Mapping):
            raise TypeError(
                "EngineSolverReadOnlyAdapter expected solver result to be a Mapping."
            )

        self.evidence["last_input_keys"] = sorted(str(key) for key in inputs.keys())
        self.evidence["last_output_keys"] = sorted(str(key) for key in result.keys())

        return dict(result)


def make_engine_solver_read_only_adapter(
    solver_callable: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> EngineSolverReadOnlyAdapter:
    return EngineSolverReadOnlyAdapter(solver_callable=solver_callable)
