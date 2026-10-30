"""
Programme 27F: Standardisation Repair Plan Owner.

Creates non-mutating repair plans from classified standardisation findings.

Design rules:
- Plan only.
- No mutation.
- No deletion.
- No archival.
- No automatic repair.
- Manual approval required for any future repair action.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Iterable, List, Tuple

from .compliance_classifier import (
    ClassifiedStandardisationFinding,
    StandardisationComplianceClassificationReport,
    StandardisationRepairPriority,
)


class StandardisationRepairActionType(str, Enum):
    STANDARDISE_GATE_REPORTING = "STANDARDISE_GATE_REPORTING"
    ADD_SCHEMA_FIELD = "ADD_SCHEMA_FIELD"
    REVIEW_LEGACY_NOISE = "REVIEW_LEGACY_NOISE"
    REVIEW_PLATFORM_STRUCTURE = "REVIEW_PLATFORM_STRUCTURE"
    REVIEW_CANONICAL_STORAGE = "REVIEW_CANONICAL_STORAGE"
    REVIEW_INTERFACE_DEPENDENCY = "REVIEW_INTERFACE_DEPENDENCY"
    REVIEW_UNCLASSIFIED = "REVIEW_UNCLASSIFIED"


@dataclass(frozen=True)
class StandardisationRepairPlanItem:
    plan_item_id: str
    action_type: StandardisationRepairActionType
    priority: StandardisationRepairPriority
    category: str
    rule_id: str
    path: str
    reason: str
    proposed_action: str
    manual_approval_required: bool = True
    mutation_allowed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "plan_item_id": self.plan_item_id,
            "action_type": self.action_type.value,
            "priority": self.priority.value,
            "category": self.category,
            "rule_id": self.rule_id,
            "path": self.path,
            "reason": self.reason,
            "proposed_action": self.proposed_action,
            "manual_approval_required": self.manual_approval_required,
            "mutation_allowed": self.mutation_allowed,
        }


@dataclass(frozen=True)
class StandardisationRepairPlan:
    schema: str
    plan_id: str
    source_total_findings: int
    planned_items: Tuple[StandardisationRepairPlanItem, ...]
    mutation_performed: bool = False
    automatic_repair_enabled: bool = False

    def priority_counts(self) -> Dict[str, int]:
        counts = {priority.value: 0 for priority in StandardisationRepairPriority}
        for item in self.planned_items:
            counts[item.priority.value] += 1
        return counts

    def action_counts(self) -> Dict[str, int]:
        counts = {action.value: 0 for action in StandardisationRepairActionType}
        for item in self.planned_items:
            counts[item.action_type.value] += 1
        return counts

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "plan_id": self.plan_id,
            "source_total_findings": self.source_total_findings,
            "planned_item_count": len(self.planned_items),
            "priority_counts": self.priority_counts(),
            "action_counts": self.action_counts(),
            "mutation_performed": self.mutation_performed,
            "automatic_repair_enabled": self.automatic_repair_enabled,
            "manual_approval_required": True,
            "planned_items": [item.as_dict() for item in self.planned_items[:250]],
            "planned_items_truncated": len(self.planned_items) > 250,
        }


class StandardisationRepairPlanOwner:
    """
    Owns non-mutating repair plans.

    The plan intentionally groups repeated findings by rule/path/action so
    later phases can reduce noise instead of producing thousands of duplicated
    manual tasks.
    """

    def __init__(
        self,
        classification_report: StandardisationComplianceClassificationReport,
    ) -> None:
        self.classification_report = classification_report

    def build_plan(self) -> StandardisationRepairPlan:
        planned_items = self._build_grouped_items()

        return StandardisationRepairPlan(
            schema="LEAF_STANDARDISATION_REPAIR_PLAN_OWNER_PHASE_27F_V1",
            plan_id="standardisation_repair_plan_owner",
            source_total_findings=self.classification_report.total_findings,
            planned_items=tuple(planned_items),
            mutation_performed=False,
            automatic_repair_enabled=False,
        )

    def _build_grouped_items(self) -> List[StandardisationRepairPlanItem]:
        grouped: Dict[Tuple[str, str, str, str], List[ClassifiedStandardisationFinding]] = {}

        for finding in self.classification_report.classified_findings:
            key = (
                finding.category.value,
                finding.repair_priority.value,
                finding.finding.rule_id,
                finding.finding.path,
            )
            grouped.setdefault(key, []).append(finding)

        items: List[StandardisationRepairPlanItem] = []

        for index, ((category, priority, rule_id, path), findings) in enumerate(grouped.items(), start=1):
            representative = findings[0]
            action_type = self._action_type_for(category, rule_id)
            proposed_action = self._proposed_action_for(action_type, rule_id, path, len(findings))

            items.append(
                StandardisationRepairPlanItem(
                    plan_item_id=f"standardisation_repair_{index:05d}",
                    action_type=action_type,
                    priority=StandardisationRepairPriority(priority),
                    category=category,
                    rule_id=rule_id,
                    path=path,
                    reason=representative.rationale,
                    proposed_action=proposed_action,
                    manual_approval_required=True,
                    mutation_allowed=False,
                )
            )

        priority_rank = {
            StandardisationRepairPriority.BLOCKING: 0,
            StandardisationRepairPriority.HIGH: 1,
            StandardisationRepairPriority.MEDIUM: 2,
            StandardisationRepairPriority.LOW: 3,
            StandardisationRepairPriority.NONE: 4,
        }

        return sorted(
            items,
            key=lambda item: (
                priority_rank[item.priority],
                item.action_type.value,
                item.path,
                item.rule_id,
            ),
        )

    def _action_type_for(
        self,
        category: str,
        rule_id: str,
    ) -> StandardisationRepairActionType:
        if rule_id == "completion_gates_emit_completion_notice":
            return StandardisationRepairActionType.STANDARDISE_GATE_REPORTING

        if rule_id == "schema_has_named_version":
            return StandardisationRepairActionType.ADD_SCHEMA_FIELD

        if category == "LEGACY_EXPECTED_NOISE":
            return StandardisationRepairActionType.REVIEW_LEGACY_NOISE

        if category == "PLATFORM_STRUCTURAL_ISSUE":
            return StandardisationRepairActionType.REVIEW_PLATFORM_STRUCTURE

        if category == "CANONICAL_STORAGE_ISSUE":
            return StandardisationRepairActionType.REVIEW_CANONICAL_STORAGE

        if category == "INTERFACE_DEPENDENCY_ISSUE":
            return StandardisationRepairActionType.REVIEW_INTERFACE_DEPENDENCY

        return StandardisationRepairActionType.REVIEW_UNCLASSIFIED

    def _proposed_action_for(
        self,
        action_type: StandardisationRepairActionType,
        rule_id: str,
        path: str,
        grouped_count: int,
    ) -> str:
        prefix = f"{grouped_count} finding(s) grouped for {path}. "

        if action_type == StandardisationRepairActionType.STANDARDISE_GATE_REPORTING:
            return (
                prefix
                + "Review gate/report output and later standardise completion_notice, report path, JSON path, and next_phase fields."
            )

        if action_type == StandardisationRepairActionType.ADD_SCHEMA_FIELD:
            return (
                prefix
                + "Review JSON/report payload and later add or route a stable schema field through the relevant report owner."
            )

        if action_type == StandardisationRepairActionType.REVIEW_LEGACY_NOISE:
            return (
                prefix
                + "Confirm whether this path is legacy/import-only/deprecated before excluding, archiving, or repairing manually."
            )

        if action_type == StandardisationRepairActionType.REVIEW_PLATFORM_STRUCTURE:
            return (
                prefix
                + "Review platform ownership boundaries before any manual repair is proposed."
            )

        if action_type == StandardisationRepairActionType.REVIEW_CANONICAL_STORAGE:
            return (
                prefix
                + "Review canonical storage expectations before creating or redirecting folders."
            )

        if action_type == StandardisationRepairActionType.REVIEW_INTERFACE_DEPENDENCY:
            return (
                prefix
                + "Review module interface/dependency declarations before future integration work."
            )

        return prefix + f"Review finding for rule {rule_id} before deciding whether repair is needed."

    def report(self) -> Dict[str, Any]:
        plan = self.build_plan()
        data = plan.as_dict()

        priority_counter = Counter(item.priority.value for item in plan.planned_items)
        action_counter = Counter(item.action_type.value for item in plan.planned_items)

        data["top_priorities"] = [
            {"priority": key, "count": value}
            for key, value in priority_counter.most_common()
        ]
        data["top_actions"] = [
            {"action_type": key, "count": value}
            for key, value in action_counter.most_common()
        ]

        return data


def build_standardisation_repair_plan_owner(
    classification_report: StandardisationComplianceClassificationReport,
) -> StandardisationRepairPlanOwner:
    return StandardisationRepairPlanOwner(classification_report)
