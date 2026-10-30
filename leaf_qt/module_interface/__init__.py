"""
LEAF Modular Engineering Interface Platform.

Programme 28 defines the reusable interface every engineering module should
expose before it is integrated into workflow, runtime, storage, reports, and Qt.
"""

from .interface_model import (
    EngineeringModuleCapability,
    EngineeringModuleDependency,
    EngineeringModuleInterface,
    EngineeringModuleInterfaceStatus,
    EngineeringModuleSurface,
    build_engineering_module_interface,
)

__all__ = [
    "EngineeringModuleCapability",
    "EngineeringModuleDependency",
    "EngineeringModuleInterface",
    "EngineeringModuleInterfaceStatus",
    "EngineeringModuleSurface",
    "EngineeringModuleRegistry",
    "EngineeringModuleDependencyGraph",
    "EngineeringModuleDependencyGraphReport",
    "EngineeringModuleAdapterCapability",
    "EngineeringModuleAdapterContract",
    "EngineeringModuleAdapterProtocol",
    "EngineeringModuleAdapterResult",
    "EngineeringModuleAdapterStatus",
    "build_engineering_module_adapter_contract",
    "EngineeringModuleValidationContract",
    "EngineeringModuleValidationFinding",
    "EngineeringModuleValidationMode",
    "EngineeringModuleValidationResult",
    "EngineeringModuleValidationSeverity",
    "EngineeringModuleValidationVerdict",
    "EngineeringModuleReportContract",
    "EngineeringModuleReportPackage",
    "EngineeringModuleReportSection",
    "EngineeringModuleWorkflowContract",
    "EngineeringModuleWorkflowStepDefinition",
    "build_engineering_module_workflow_contract",
    "EngineeringModuleRuntimeAction",
    "EngineeringModuleRuntimeContract",
    "EngineeringModuleRuntimeRequest",
    "EngineeringModuleRuntimeRequestStatus",
    "EngineeringModuleRuntimeResult",
    "CANONICAL_STORAGE_FOLDERS",
    "EngineeringModuleStorageAction",
    "EngineeringModuleStorageContract",
    "EngineeringModuleStorageDomain",
    "EngineeringModuleStorageRequest",
    "EngineeringModuleStorageRequestStatus",
    "EngineeringModuleStorageResult",
    "EngineeringModuleNotificationContract",
    "EngineeringModuleNotificationEvent",
    "EngineeringModuleNotificationLevel",
    "EngineeringModuleNotificationResult",
    "EngineeringModuleNotificationStatus",
    "EngineeringModuleNotificationTopic",
    "EngineeringModuleIntegrationReadinessGate",
    "EngineeringModuleIntegrationReadinessResult",
    "EngineeringModuleIntegrationVerdict",
    "build_engineering_module_integration_readiness_gate",
    "build_engineering_module_notification_contract",
    "build_engineering_module_storage_contract",
    "build_engineering_module_runtime_contract",
    "default_engineering_module_workflow_steps",
    "build_engineering_module_report_contract",
    "build_engineering_module_validation_contract",
    "default_adapter_capability_map",
    "build_engineering_module_dependency_graph",
    "build_engineering_module_registry",
    "build_engineering_module_interface",
]

from .module_registry import (
    EngineeringModuleRegistry,
    build_engineering_module_registry,
)

from .dependency_graph import (
    EngineeringModuleDependencyGraph,
    EngineeringModuleDependencyGraphReport,
    build_engineering_module_dependency_graph,
)

from .adapter_contract import (
    EngineeringModuleAdapterCapability,
    EngineeringModuleAdapterContract,
    EngineeringModuleAdapterProtocol,
    EngineeringModuleAdapterResult,
    EngineeringModuleAdapterStatus,
    build_engineering_module_adapter_contract,
    default_adapter_capability_map,
)

from .validation_contract import (
    EngineeringModuleValidationContract,
    EngineeringModuleValidationFinding,
    EngineeringModuleValidationMode,
    EngineeringModuleValidationResult,
    EngineeringModuleValidationSeverity,
    EngineeringModuleValidationVerdict,
    build_engineering_module_validation_contract,
)

from .report_contract import (
    EngineeringModuleReportContract,
    EngineeringModuleReportPackage,
    EngineeringModuleReportSection,
    build_engineering_module_report_contract,
)

from .workflow_contract import (
    EngineeringModuleWorkflowContract,
    EngineeringModuleWorkflowStepDefinition,
    build_engineering_module_workflow_contract,
    default_engineering_module_workflow_steps,
)

from .runtime_contract import (
    EngineeringModuleRuntimeAction,
    EngineeringModuleRuntimeContract,
    EngineeringModuleRuntimeRequest,
    EngineeringModuleRuntimeRequestStatus,
    EngineeringModuleRuntimeResult,
    build_engineering_module_runtime_contract,
)

from .storage_contract import (
    CANONICAL_STORAGE_FOLDERS,
    EngineeringModuleStorageAction,
    EngineeringModuleStorageContract,
    EngineeringModuleStorageDomain,
    EngineeringModuleStorageRequest,
    EngineeringModuleStorageRequestStatus,
    EngineeringModuleStorageResult,
    build_engineering_module_storage_contract,
)

from .notification_contract import (
    EngineeringModuleNotificationContract,
    EngineeringModuleNotificationEvent,
    EngineeringModuleNotificationLevel,
    EngineeringModuleNotificationResult,
    EngineeringModuleNotificationStatus,
    EngineeringModuleNotificationTopic,
    build_engineering_module_notification_contract,
)

from .integration_readiness_gate import (
    EngineeringModuleIntegrationReadinessGate,
    EngineeringModuleIntegrationReadinessResult,
    EngineeringModuleIntegrationVerdict,
    build_engineering_module_integration_readiness_gate,
)
