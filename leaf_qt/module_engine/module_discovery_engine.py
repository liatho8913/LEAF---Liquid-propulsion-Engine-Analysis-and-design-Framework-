from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leaf_qt.module_engine.module_definition import ModuleDefinition
from leaf_qt.module_engine.module_definition_loader import ModuleDefinitionLoader
from leaf_qt.module_engine.module_definition_registry import ModuleDefinitionRegistry


@dataclass(frozen=True)
class ModuleDiscoveryResult:
    definition_dir: str
    discovered_count: int
    discovered_modules: list[str]
    duplicate_modules: list[str]
    invalid_modules: dict[str, Any]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "definition_dir": self.definition_dir,
            "discovered_count": self.discovered_count,
            "discovered_modules": self.discovered_modules,
            "duplicate_modules": self.duplicate_modules,
            "invalid_modules": self.invalid_modules,
            "status": self.status,
        }


class ModuleDiscoveryEngine:
    """
    Single source of truth for discovering LEAF engineering modules.

    This engine owns module discovery only.

    It does not own engineering physics.
    It does not own module execution.
    It does not own validation behaviour.
    It does not own reports.

    It discovers declared module definitions and produces a registry.
    """

    def __init__(self, definition_dir: Path):
        self.definition_dir = Path(definition_dir)
        self.loader = ModuleDefinitionLoader(self.definition_dir)

    def discover_definitions(self) -> list[ModuleDefinition]:
        return self.loader.discover()

    def build_registry(self) -> ModuleDefinitionRegistry:
        definitions = self.discover_definitions()
        return ModuleDefinitionRegistry.from_definitions(definitions)

    def audit(self) -> ModuleDiscoveryResult:
        definitions = self.discover_definitions()

        seen: set[str] = set()
        duplicate_modules: list[str] = []
        invalid_modules: dict[str, Any] = {}

        for definition in definitions:
            if definition.module_id in seen:
                duplicate_modules.append(definition.module_id)
            seen.add(definition.module_id)

            validation = definition.validate()
            if validation["status"] != "PASS":
                invalid_modules[definition.module_id] = validation

        discovered_modules = sorted(seen)

        passed = bool(discovered_modules) and not duplicate_modules and not invalid_modules

        return ModuleDiscoveryResult(
            definition_dir=str(self.definition_dir),
            discovered_count=len(discovered_modules),
            discovered_modules=discovered_modules,
            duplicate_modules=sorted(duplicate_modules),
            invalid_modules=invalid_modules,
            status="PASS" if passed else "FAIL",
        )
