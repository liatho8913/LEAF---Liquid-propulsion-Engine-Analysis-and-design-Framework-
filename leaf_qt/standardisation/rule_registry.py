"""
Programme 27B: Standardisation Rule Registry.

Reusable rule registry for project-wide LEAF standardisation.

This does not mutate files. It defines standards that later phases can validate
against and report on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from .inventory_model import StandardisationArea


class StandardisationRuleSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class StandardisationRule:
    rule_id: str
    area: StandardisationArea
    title: str
    description: str
    severity: StandardisationRuleSeverity = StandardisationRuleSeverity.ERROR
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.rule_id.strip():
            failures.append("rule_id is empty")

        if not isinstance(self.area, StandardisationArea):
            failures.append(f"area invalid for {self.rule_id!r}: {self.area!r}")

        if not self.title.strip():
            failures.append(f"title is empty for {self.rule_id!r}")

        if not self.description.strip():
            failures.append(f"description is empty for {self.rule_id!r}")

        if not isinstance(self.severity, StandardisationRuleSeverity):
            failures.append(f"severity invalid for {self.rule_id!r}: {self.severity!r}")

        return failures


@dataclass
class StandardisationRuleRegistry:
    registry_id: str = "leaf_project_wide_standardisation_rule_registry"
    rules: Dict[str, StandardisationRule] = field(default_factory=dict)

    def register(self, rule: StandardisationRule, replace: bool = False) -> None:
        failures = rule.validate()
        if failures:
            raise ValueError("; ".join(failures))

        if rule.rule_id in self.rules and not replace:
            raise ValueError(f"standardisation rule already registered: {rule.rule_id}")

        self.rules[rule.rule_id] = rule

    def register_many(
        self,
        rules: Iterable[StandardisationRule],
        replace: bool = False,
    ) -> None:
        for rule in rules:
            self.register(rule, replace=replace)

    def has(self, rule_id: str) -> bool:
        return rule_id in self.rules

    def get(self, rule_id: str) -> StandardisationRule:
        try:
            return self.rules[rule_id]
        except KeyError as exc:
            raise KeyError(f"unknown standardisation rule: {rule_id}") from exc

    def all_rules(self) -> Tuple[StandardisationRule, ...]:
        return tuple(self.rules.values())

    def rules_for_area(self, area: StandardisationArea) -> Tuple[StandardisationRule, ...]:
        return tuple(rule for rule in self.all_rules() if rule.area == area)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.registry_id.strip():
            failures.append("registry_id is empty")

        for rule in self.all_rules():
            failures.extend(rule.validate())

        covered_areas = {rule.area for rule in self.all_rules()}
        missing_areas = [area.value for area in StandardisationArea if area not in covered_areas]

        if missing_areas:
            failures.append(f"standardisation rule coverage missing areas: {missing_areas}")

        return failures

    def area_counts(self) -> Dict[str, int]:
        counts = {area.value: 0 for area in StandardisationArea}
        for rule in self.all_rules():
            counts[rule.area.value] += 1
        return counts

    def severity_counts(self) -> Dict[str, int]:
        counts = {severity.value: 0 for severity in StandardisationRuleSeverity}
        for rule in self.all_rules():
            counts[rule.severity.value] += 1
        return counts

    def report(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_STANDARDISATION_RULE_REGISTRY_PHASE_27B_V1",
            "registry_id": self.registry_id,
            "rule_count": len(self.rules),
            "area_counts": self.area_counts(),
            "severity_counts": self.severity_counts(),
            "validation_failures": self.validate(),
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "area": rule.area.value,
                    "title": rule.title,
                    "severity": rule.severity.value,
                    "required": rule.required,
                    "metadata_keys": sorted(rule.metadata.keys()),
                }
                for rule in self.all_rules()
            ],
        }


def build_default_standardisation_rule_registry() -> StandardisationRuleRegistry:
    registry = StandardisationRuleRegistry()

    registry.register_many(
        [
            StandardisationRule(
                rule_id="schema_has_named_version",
                area=StandardisationArea.SCHEMA,
                title="Schemas must have explicit names and versions",
                description="Reports and payloads must expose stable schema identifiers.",
                severity=StandardisationRuleSeverity.BLOCKING,
            ),
            StandardisationRule(
                rule_id="naming_uses_programme_phase_pattern",
                area=StandardisationArea.NAMING,
                title="Names must preserve programme and phase traceability",
                description="Files, gates, and reports should make ownership and phase lineage clear.",
            ),
            StandardisationRule(
                rule_id="validation_returns_structured_failures",
                area=StandardisationArea.VALIDATION,
                title="Validation must return structured failures",
                description="Validation must not hide failures or rely only on printed output.",
                severity=StandardisationRuleSeverity.BLOCKING,
            ),
            StandardisationRule(
                rule_id="reports_have_single_owner",
                area=StandardisationArea.REPORT,
                title="Reports must have a single owner",
                description="Subsystem reports should be created through an owner rather than scattered emitters.",
            ),
            StandardisationRule(
                rule_id="ownership_boundaries_are_explicit",
                area=StandardisationArea.OWNERSHIP,
                title="Ownership boundaries must be explicit",
                description="Platform, workflow, runtime, storage, Qt, and engineering ownership must remain separated.",
                severity=StandardisationRuleSeverity.BLOCKING,
            ),
            StandardisationRule(
                rule_id="completion_gates_emit_completion_notice",
                area=StandardisationArea.COMPLETION_GATE,
                title="Completion gates must emit completion notices",
                description="Every gate must report pass/fail, report path, JSON path, completion notice, and next phase.",
                severity=StandardisationRuleSeverity.BLOCKING,
            ),
            StandardisationRule(
                rule_id="canonical_user_storage_folders_only",
                area=StandardisationArea.FOLDER_STRUCTURE,
                title="Canonical user storage folders must remain authoritative",
                description="LEAF_Projects, LEAF_Designs, LEAF_Reports, and LEAF_Exports are authoritative user-facing locations.",
            ),
            StandardisationRule(
                rule_id="modules_expose_standard_interfaces",
                area=StandardisationArea.MODULE_INTERFACE,
                title="Modules must expose standard interfaces",
                description="Engineering modules should expose model, solver, validation, report, runtime, workflow, storage, and notification interfaces.",
            ),
            StandardisationRule(
                rule_id="dependencies_declare_provides_requires_optional",
                area=StandardisationArea.DEPENDENCY,
                title="Dependencies must declare provides/requires/optional relationships",
                description="Modules should declare dependency contracts before integration.",
                severity=StandardisationRuleSeverity.BLOCKING,
            ),
        ]
    )

    return registry
