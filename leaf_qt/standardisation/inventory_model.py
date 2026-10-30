"""
Programme 27A: Standardisation Inventory Model.

Reusable inventory model for project-wide standardisation.

This is platform infrastructure. It does not modify files. It records what
needs standardisation before later phases validate or repair anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Tuple


class StandardisationArea(str, Enum):
    SCHEMA = "SCHEMA"
    NAMING = "NAMING"
    VALIDATION = "VALIDATION"
    REPORT = "REPORT"
    OWNERSHIP = "OWNERSHIP"
    COMPLETION_GATE = "COMPLETION_GATE"
    FOLDER_STRUCTURE = "FOLDER_STRUCTURE"
    MODULE_INTERFACE = "MODULE_INTERFACE"
    DEPENDENCY = "DEPENDENCY"


@dataclass(frozen=True)
class StandardisationInventoryItem:
    item_id: str
    area: StandardisationArea
    title: str
    description: str
    owner: str = "standardisation_platform"
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.item_id.strip():
            failures.append("item_id is empty")

        if not isinstance(self.area, StandardisationArea):
            failures.append(f"area invalid for {self.item_id!r}: {self.area!r}")

        if not self.title.strip():
            failures.append(f"title is empty for {self.item_id!r}")

        if not self.owner.strip():
            failures.append(f"owner is empty for {self.item_id!r}")

        return failures


@dataclass(frozen=True)
class StandardisationInventoryModel:
    inventory_id: str
    title: str
    items: Tuple[StandardisationInventoryItem, ...]
    version: str = "1.0.0"

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.inventory_id.strip():
            failures.append("inventory_id is empty")

        if not self.title.strip():
            failures.append("title is empty")

        seen = set()
        for item in self.items:
            failures.extend(item.validate())
            if item.item_id in seen:
                failures.append(f"duplicate item_id: {item.item_id}")
            seen.add(item.item_id)

        return failures

    def area_counts(self) -> Dict[str, int]:
        counts = {area.value: 0 for area in StandardisationArea}
        for item in self.items:
            counts[item.area.value] += 1
        return counts

    def report(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_STANDARDISATION_INVENTORY_MODEL_PHASE_27A_V1",
            "inventory_id": self.inventory_id,
            "title": self.title,
            "version": self.version,
            "item_count": len(self.items),
            "area_counts": self.area_counts(),
            "validation_failures": self.validate(),
            "items": [
                {
                    "item_id": item.item_id,
                    "area": item.area.value,
                    "title": item.title,
                    "owner": item.owner,
                    "required": item.required,
                    "metadata_keys": sorted(item.metadata.keys()),
                }
                for item in self.items
            ],
        }


def build_standardisation_inventory_model(
    inventory_id: str = "leaf_project_wide_standardisation_inventory",
) -> StandardisationInventoryModel:
    items = (
        StandardisationInventoryItem(
            item_id="schema_standardisation",
            area=StandardisationArea.SCHEMA,
            title="Schema Standardisation",
            description="Inventory schema names, versions, and report payload formats.",
        ),
        StandardisationInventoryItem(
            item_id="naming_standardisation",
            area=StandardisationArea.NAMING,
            title="Naming Standardisation",
            description="Inventory naming conventions for modules, gates, reports, and owners.",
        ),
        StandardisationInventoryItem(
            item_id="validation_standardisation",
            area=StandardisationArea.VALIDATION,
            title="Validation Standardisation",
            description="Inventory validation behaviour and failure reporting conventions.",
        ),
        StandardisationInventoryItem(
            item_id="report_standardisation",
            area=StandardisationArea.REPORT,
            title="Report Standardisation",
            description="Inventory report ownership and output locations.",
        ),
        StandardisationInventoryItem(
            item_id="ownership_standardisation",
            area=StandardisationArea.OWNERSHIP,
            title="Ownership Standardisation",
            description="Inventory owner boundaries across platform and engineering modules.",
        ),
        StandardisationInventoryItem(
            item_id="completion_gate_standardisation",
            area=StandardisationArea.COMPLETION_GATE,
            title="Completion Gate Standardisation",
            description="Inventory pass/fail gate conventions and completion notices.",
        ),
        StandardisationInventoryItem(
            item_id="folder_structure_standardisation",
            area=StandardisationArea.FOLDER_STRUCTURE,
            title="Folder Structure Standardisation",
            description="Inventory canonical folders and non-authoritative legacy locations.",
        ),
        StandardisationInventoryItem(
            item_id="module_interface_standardisation",
            area=StandardisationArea.MODULE_INTERFACE,
            title="Module Interface Standardisation",
            description="Inventory required module interfaces for future engineering systems.",
        ),
        StandardisationInventoryItem(
            item_id="dependency_standardisation",
            area=StandardisationArea.DEPENDENCY,
            title="Dependency Standardisation",
            description="Inventory provides/requires/optional dependency declarations.",
        ),
    )

    return StandardisationInventoryModel(
        inventory_id=inventory_id,
        title="LEAF Project-Wide Standardisation Inventory",
        items=items,
    )
