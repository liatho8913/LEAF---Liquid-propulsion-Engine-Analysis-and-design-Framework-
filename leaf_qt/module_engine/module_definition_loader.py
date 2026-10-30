from __future__ import annotations

import json
from pathlib import Path

from leaf_qt.module_engine.module_definition import ModuleDefinition


class ModuleDefinitionLoader:
    def __init__(self, definition_dir: Path):
        self.definition_dir = Path(definition_dir)

    def load_file(self, path: Path) -> ModuleDefinition:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return ModuleDefinition.from_dict(data)

    def discover(self) -> list[ModuleDefinition]:
        definitions: list[ModuleDefinition] = []

        if not self.definition_dir.exists():
            return definitions

        for path in sorted(self.definition_dir.glob("*.json")):
            definitions.append(self.load_file(path))

        return definitions

    def definition_path(
        self,
        module_id: str,
    ) -> Path:
        """
        Resolve a module's definition file by its declared
        module_id rather than by filename convention.

        Module identity belongs to the definition metadata;
        filenames are storage details.
        """
        matches = [
            path
            for path
            in sorted(
                self.definition_dir.glob(
                    "*.json"
                )
            )
            if (
                self.load_file(
                    path
                ).module_id
                == module_id
            )
        ]

        if not matches:
            raise KeyError(
                f"Unknown module: {module_id}"
            )

        if len(matches) > 1:
            raise ValueError(
                f"Duplicate module_id: {module_id}"
            )

        return matches[0]
