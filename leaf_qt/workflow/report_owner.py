"""
Programme 26I: Workflow Report Owner.

Single owned reporting layer for LEAF workflow infrastructure.

Design rules:
- Own workflow reporting format.
- Reuse existing workflow components.
- Do not mutate workflow, runtime, or storage.
- Do not duplicate graph/progress/readiness/recommendation logic.
- Keep Qt presentation separate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from .execution_context import WorkflowExecutionContext
from .graph import build_workflow_dependency_graph
from .progress_tracker import build_workflow_progress_tracker
from .readiness_gate import build_workflow_readiness_gate
from .recommendation_engine import build_workflow_recommendation_engine
from .runtime_bridge import (
    WorkflowRuntimeBridgeAction,
    WorkflowRuntimeBridgeRequest,
    build_workflow_runtime_bridge,
)


@dataclass(frozen=True)
class WorkflowReportPackage:
    schema: str
    workflow_id: str
    report_type: str
    summary: Dict[str, Any]
    sections: Dict[str, Any]
    metadata: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "workflow_id": self.workflow_id,
            "report_type": self.report_type,
            "summary": dict(self.summary),
            "sections": dict(self.sections),
            "metadata": dict(self.metadata),
        }


class WorkflowReportOwner:
    """
    Authoritative report owner for workflow platform outputs.

    Future UI/report routing/storage attachment layers should consume this
    package instead of each workflow component inventing separate report shapes.
    """

    def __init__(self, context: WorkflowExecutionContext) -> None:
        self.context = context

    def build_report(
        self,
        include_runtime_bridge: bool = True,
        bridge_action: WorkflowRuntimeBridgeAction = WorkflowRuntimeBridgeAction.NO_OP,
        bridge_payload: Optional[Mapping[str, Any]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> WorkflowReportPackage:
        workflow = self.context.workflow
        graph = build_workflow_dependency_graph(workflow)
        progress = build_workflow_progress_tracker(workflow)
        readiness = build_workflow_readiness_gate(self.context)
        recommendation = build_workflow_recommendation_engine(self.context)

        model_report = workflow.report()
        graph_report = graph.report().as_dict()
        progress_report = progress.report()
        readiness_report = readiness.report()
        recommendation_report = recommendation.report()

        sections: Dict[str, Any] = {
            "model": model_report,
            "graph": graph_report,
            "progress": progress_report,
            "readiness": readiness_report,
            "recommendation": recommendation_report,
            "context": self.context.report(),
        }

        if include_runtime_bridge:
            bridge = build_workflow_runtime_bridge(self.context)
            request: WorkflowRuntimeBridgeRequest = bridge.build_request(
                bridge_action,
                payload=dict(bridge_payload or {}),
            )
            sections["runtime_bridge"] = bridge.report(request)

        summary = self._summary(sections)

        return WorkflowReportPackage(
            schema="LEAF_WORKFLOW_REPORT_OWNER_PHASE_26I_V1",
            workflow_id=workflow.workflow_id,
            report_type="workflow_platform_report",
            summary=summary,
            sections=sections,
            metadata={
                "owner": "workflow_report_owner",
                "phase": "26I",
                "programme": "26",
                "qt_owned": False,
                "runtime_mutation_performed": False,
                **dict(metadata or {}),
            },
        )

    def _summary(self, sections: Mapping[str, Any]) -> Dict[str, Any]:
        progress_snapshot = sections["progress"]["snapshot"]
        readiness_result = sections["readiness"]["result"]
        recommendation = sections["recommendation"]["recommendation"]

        runtime_section = sections.get("runtime_bridge", {})
        runtime_result = runtime_section.get("result", {})

        return {
            "workflow_id": self.context.workflow.workflow_id,
            "workflow_title": self.context.workflow.title,
            "workflow_state": progress_snapshot["workflow_state"],
            "current_step_id": self.context.current_step_id,
            "current_step_title": sections["context"]["current_step_title"],
            "active_module": self.context.active_module,
            "percent_complete": progress_snapshot["percent_complete"],
            "ready_steps": progress_snapshot["ready_steps"],
            "blocked_steps": progress_snapshot["blocked_steps"],
            "remaining_steps": progress_snapshot["remaining_steps"],
            "readiness_verdict": readiness_result["verdict"],
            "can_proceed": readiness_result["can_proceed"],
            "recommendation_kind": recommendation["kind"],
            "recommended_step_id": recommendation["recommended_step_id"],
            "runtime_bridge_status": runtime_result.get("status"),
            "runtime_bridge_accepted": runtime_result.get("accepted"),
            "mutation_performed": runtime_result.get("emitted_event", {}).get(
                "mutation_performed",
                False,
            ),
        }


def build_workflow_report_owner(context: WorkflowExecutionContext) -> WorkflowReportOwner:
    return WorkflowReportOwner(context)
