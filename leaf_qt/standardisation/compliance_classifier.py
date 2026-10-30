"""
Programme 27E: Standardisation Compliance Classifier.

Classifies standardisation findings into useful architectural categories.

Design rules:
- Classify only.
- No mutation.
- No deletion.
- No automatic repair.
- Distinguish real structural issues from expected legacy/reporting noise.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

from .scanner import (
    StandardisationFinding,
    StandardisationFindingLevel,
    StandardisationScanResult,
)


class StandardisationComplianceCategory(str, Enum):
    GATE_STANDARDISATION_ISSUE = "GATE_STANDARDISATION_ISSUE"
    SCHEMA_REPORT_FORMATTING_ISSUE = "SCHEMA_REPORT_FORMATTING_ISSUE"
    LEGACY_EXPECTED_NOISE = "LEGACY_EXPECTED_NOISE"
    PLATFORM_STRUCTURAL_ISSUE = "PLATFORM_STRUCTURAL_ISSUE"
    CANONICAL_STORAGE_ISSUE = "CANONICAL_STORAGE_ISSUE"
    INTERFACE_DEPENDENCY_ISSUE = "INTERFACE_DEPENDENCY_ISSUE"
    CANDIDATE_FOR_LATER_REPAIR = "CANDIDATE_FOR_LATER_REPAIR"
    UNCLASSIFIED = "UNCLASSIFIED"


class StandardisationRepairPriority(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKING = "BLOCKING"


@dataclass(frozen=True)
class ClassifiedStandardisationFinding:
    finding: StandardisationFinding
    category: StandardisationComplianceCategory
    repair_priority: StandardisationRepairPriority
    rationale: str
    mutation_allowed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        data = self.finding.as_dict()
        data.update(
            {
                "category": self.category.value,
                "repair_priority": self.repair_priority.value,
                "rationale": self.rationale,
                "mutation_allowed": self.mutation_allowed,
            }
        )
        return data


@dataclass(frozen=True)
class StandardisationComplianceClassificationReport:
    schema: str
    total_findings: int
    category_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    classified_findings: Tuple[ClassifiedStandardisationFinding, ...]
    mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "total_findings": self.total_findings,
            "category_counts": dict(self.category_counts),
            "priority_counts": dict(self.priority_counts),
            "mutation_performed": self.mutation_performed,
            "classified_findings": [
                finding.as_dict() for finding in self.classified_findings[:250]
            ],
            "classified_findings_truncated": len(self.classified_findings) > 250,
        }


class StandardisationComplianceClassifier:
    """
    Classifies findings from the standardisation scanner.

    This creates prioritisation intelligence without modifying the repository.
    """

    LEGACY_PATH_MARKERS = (
        "legacy",
        "archive",
        "deprecated",
        "_leaf_repository_cleanup_candidates",
        "old",
        "backup",
    )

    PLATFORM_PATH_MARKERS = (
        "leaf_qt/workflow",
        "leaf_qt/standardisation",
        "leaf_qt/runtime",
        "leaf_qt/storage",
        "leaf_qt/core",
    )

    def __init__(self, scan_result: StandardisationScanResult) -> None:
        self.scan_result = scan_result

    def classify(self) -> StandardisationComplianceClassificationReport:
        classified = tuple(self._classify_finding(finding) for finding in self.scan_result.findings)

        category_counts = {category.value: 0 for category in StandardisationComplianceCategory}
        priority_counts = {priority.value: 0 for priority in StandardisationRepairPriority}

        for item in classified:
            category_counts[item.category.value] += 1
            priority_counts[item.repair_priority.value] += 1

        return StandardisationComplianceClassificationReport(
            schema="LEAF_STANDARDISATION_COMPLIANCE_CLASSIFIER_PHASE_27E_V1",
            total_findings=len(classified),
            category_counts=category_counts,
            priority_counts=priority_counts,
            classified_findings=classified,
            mutation_performed=False,
        )

    def _classify_finding(
        self,
        finding: StandardisationFinding,
    ) -> ClassifiedStandardisationFinding:
        path_lower = finding.path.lower()
        rule_id = finding.rule_id

        if self._is_legacy_path(path_lower):
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.LEGACY_EXPECTED_NOISE,
                repair_priority=StandardisationRepairPriority.LOW,
                rationale="Finding appears in a legacy/archive/deprecated path and should be reviewed later, not repaired immediately.",
                mutation_allowed=False,
            )

        if rule_id == "completion_gates_emit_completion_notice":
            priority = (
                StandardisationRepairPriority.MEDIUM
                if finding.level == StandardisationFindingLevel.ERROR
                else StandardisationRepairPriority.LOW
            )
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.GATE_STANDARDISATION_ISSUE,
                repair_priority=priority,
                rationale="Finding relates to gate/report consistency rather than direct solver or runtime behaviour.",
                mutation_allowed=False,
            )

        if rule_id == "schema_has_named_version":
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.SCHEMA_REPORT_FORMATTING_ISSUE,
                repair_priority=StandardisationRepairPriority.LOW,
                rationale="Finding relates to report schema formatting and can be standardised through report owners later.",
                mutation_allowed=False,
            )

        if rule_id == "canonical_user_storage_folders_only":
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.CANONICAL_STORAGE_ISSUE,
                repair_priority=StandardisationRepairPriority.HIGH,
                rationale="Finding affects canonical user-facing project/design/report/export storage expectations.",
                mutation_allowed=False,
            )

        if rule_id in {
            "modules_expose_standard_interfaces",
            "dependencies_declare_provides_requires_optional",
        }:
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.INTERFACE_DEPENDENCY_ISSUE,
                repair_priority=StandardisationRepairPriority.HIGH,
                rationale="Finding affects future module plug-in behaviour and dependency clarity.",
                mutation_allowed=False,
            )

        if rule_id in {
            "ownership_boundaries_are_explicit",
            "validation_returns_structured_failures",
        } or any(marker in path_lower for marker in self.PLATFORM_PATH_MARKERS):
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.PLATFORM_STRUCTURAL_ISSUE,
                repair_priority=StandardisationRepairPriority.BLOCKING
                if finding.level == StandardisationFindingLevel.ERROR
                else StandardisationRepairPriority.HIGH,
                rationale="Finding affects platform ownership, validation, or core infrastructure boundaries.",
                mutation_allowed=False,
            )

        if finding.level == StandardisationFindingLevel.ERROR:
            return ClassifiedStandardisationFinding(
                finding=finding,
                category=StandardisationComplianceCategory.CANDIDATE_FOR_LATER_REPAIR,
                repair_priority=StandardisationRepairPriority.MEDIUM,
                rationale="Finding is an error but does not match a more specific classifier rule.",
                mutation_allowed=False,
            )

        return ClassifiedStandardisationFinding(
            finding=finding,
            category=StandardisationComplianceCategory.UNCLASSIFIED,
            repair_priority=StandardisationRepairPriority.LOW,
            rationale="Finding does not yet match a specific compliance category.",
            mutation_allowed=False,
        )

    def _is_legacy_path(self, path_lower: str) -> bool:
        return any(marker in path_lower for marker in self.LEGACY_PATH_MARKERS)

    def report(self) -> Dict[str, Any]:
        classification = self.classify()
        data = classification.as_dict()

        top_categories = Counter()
        top_priorities = Counter()

        for finding in classification.classified_findings:
            top_categories[finding.category.value] += 1
            top_priorities[finding.repair_priority.value] += 1

        data["top_categories"] = [
            {"category": key, "count": value}
            for key, value in top_categories.most_common()
        ]
        data["top_priorities"] = [
            {"priority": key, "count": value}
            for key, value in top_priorities.most_common()
        ]

        return data


def build_standardisation_compliance_classifier(
    scan_result: StandardisationScanResult,
) -> StandardisationComplianceClassifier:
    return StandardisationComplianceClassifier(scan_result)
