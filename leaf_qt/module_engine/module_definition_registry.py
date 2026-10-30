from __future__ import annotations

from dataclasses import dataclass

from leaf_qt.module_engine.module_definition import ModuleDefinition


@dataclass
class ModuleDefinitionRegistry:
    definitions: dict[str, ModuleDefinition]

    @classmethod
    def from_definitions(
        cls,
        definitions: list[ModuleDefinition],
    ) -> "ModuleDefinitionRegistry":
        registry: dict[str, ModuleDefinition] = {}

        for definition in definitions:
            if definition.module_id in registry:
                raise ValueError(f"Duplicate module_id: {definition.module_id}")
            registry[definition.module_id] = definition

        return cls(definitions=registry)

    def get(self, module_id: str) -> ModuleDefinition:
        return self.definitions[module_id]

    def ids(self) -> list[str]:
        return sorted(self.definitions)

    def validate_all(self) -> dict[str, dict]:
        return {
            module_id: definition.validate()
            for module_id, definition in sorted(self.definitions.items())
        }
