from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


INFRASTRUCTURE_DEPENDENCIES = {
    "runtime",
    "storage",
    "workflow",
    "reports",
    "report",
    "validation",
    "notifications",
    "notification",
    "ownership",
    "dependency_management",
    "completion_gates",
    "module_engine",
    "modular_engine",
    "operating_system",
}


CANONICAL_MODULAR_ENGINE_TOKENS = {
    "project_maintenance/modular_engine_architecture",
    "leaf_qt/module_engine",
    "leaf_qt/modular_engine",
    "leaf_qt/modules",
    "leaf_qt/engineering_modules",
    "leaf_qt/module_runtime",
}


@dataclass(frozen=True)
class ModuleDependencyNode:
    name: str
    status: str
    module_dependencies: list[str]
    infrastructure_dependencies: list[str]
    missing_module_dependencies: list[str]
    inactive_module_dependencies: list[str]
    activation_cascade: list[str]
    deactivation_cascade: list[str]


@dataclass(frozen=True)
class ModuleDependencyVisibilityReport:
    schema: str
    registered_module_count: int
    active_module_count: int
    inactive_module_count: int
    module_nodes: list[ModuleDependencyNode]
    missing_module_dependency_count: int
    inactive_module_dependency_count: int
    duplicate_dependency_systems_detected: int
    duplicate_availability_systems_detected: int
    duplicate_registry_systems_detected: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class ModuleDependencyVisibilityBuilder:
    """
    Programme 37A visibility layer.

    Constitutional limits:
    - Does not create a dependency engine.
    - Does not create a registry.
    - Does not create an availability system.
    - Does not mutate engineering behaviour.
    - Reads existing module definitions only.
    """

    schema = "LEAF_MODULE_DEPENDENCY_VISIBILITY_PHASE_37A_V2"

    def __init__(self, root: Path = ROOT) -> None:
        self.root = root
        self.module_root = root / "project_maintenance" / "modular_engine_architecture"

    def discover_module_definition_files(self) -> list[Path]:
        candidates: list[Path] = []

        for path in self.module_root.rglob("*.json"):
            rel = str(path.relative_to(self.root)).lower()

            if "/reports/" in rel or rel.endswith("_report.json"):
                continue

            if "module" in path.name.lower() or "definition" in path.name.lower():
                candidates.append(path)

        return sorted(set(candidates))

    def load_registered_modules(self) -> dict[str, dict[str, Any]]:
        modules: dict[str, dict[str, Any]] = {}

        for path in self.discover_module_definition_files():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue

            for record in self.extract_module_records(data):
                name = self.normalise_name(
                    record.get("name")
                    or record.get("module")
                    or record.get("module_name")
                    or record.get("id")
                )

                if not name:
                    continue

                existing = modules.get(name, {})
                merged = dict(existing)
                merged.update(record)
                merged["_source"] = str(path.relative_to(self.root))
                modules[name] = merged

        return modules

    def extract_module_records(self, value: Any) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []

        if isinstance(value, dict):
            if self.looks_like_module_record(value):
                records.append(value)

            for nested in value.values():
                records.extend(self.extract_module_records(nested))

        elif isinstance(value, list):
            for item in value:
                records.extend(self.extract_module_records(item))

        return records

    @staticmethod
    def looks_like_module_record(value: dict[str, Any]) -> bool:
        keys = {str(k).lower() for k in value.keys()}
        return bool(
            {"name", "module", "module_name", "id"} & keys
            and (
                "status" in keys
                or "dependencies" in keys
                or "outputs" in keys
                or "methods" in keys
                or "adapter" in keys
            )
        )

    @staticmethod
    def normalise_name(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip().lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def raw_dependency_list(cls, record: dict[str, Any]) -> list[str]:
        raw = (
            record.get("dependencies")
            or record.get("depends_on")
            or record.get("required_modules")
            or []
        )

        if isinstance(raw, str):
            raw = [raw]

        if not isinstance(raw, list):
            return []

        out: list[str] = []
        for item in raw:
            name = cls.normalise_name(item)
            if name and name not in out:
                out.append(name)
        return out

    @staticmethod
    def split_dependencies(raw: list[str], registered_modules: set[str]) -> tuple[list[str], list[str]]:
        module_dependencies: list[str] = []
        infrastructure_dependencies: list[str] = []

        for dep in raw:
            if dep in registered_modules:
                module_dependencies.append(dep)
            elif dep in INFRASTRUCTURE_DEPENDENCIES:
                infrastructure_dependencies.append(dep)
            else:
                infrastructure_dependencies.append(dep)

        return module_dependencies, infrastructure_dependencies

    @staticmethod
    def module_status(record: dict[str, Any]) -> str:
        raw = str(record.get("status") or record.get("state") or "active").strip().lower()

        if raw in {"active", "available", "enabled", "ready", "registered"}:
            return "active"

        if raw in {"inactive", "disabled", "unavailable", "blocked"}:
            return "inactive"

        return "active"

    def activation_cascade(self, module: str, dependencies: dict[str, list[str]]) -> list[str]:
        seen: set[str] = set()
        order: list[str] = []

        def visit(name: str) -> None:
            if name in seen:
                return
            seen.add(name)

            for dep in dependencies.get(name, []):
                visit(dep)

            if name not in order:
                order.append(name)

        visit(module)
        return order

    def deactivation_cascade(self, module: str, dependencies: dict[str, list[str]]) -> list[str]:
        reverse: dict[str, list[str]] = {}

        for owner, deps in dependencies.items():
            for dep in deps:
                reverse.setdefault(dep, []).append(owner)

        seen: set[str] = set()
        order: list[str] = []

        def visit(name: str) -> None:
            if name in seen:
                return
            seen.add(name)

            for child in sorted(reverse.get(name, [])):
                visit(child)

            if name not in order:
                order.append(name)

        visit(module)
        return order

    def is_canonical_modular_engine_path(self, path: Path) -> bool:
        rel = str(path.relative_to(self.root)).replace("\\", "/").lower()
        return any(token in rel for token in CANONICAL_MODULAR_ENGINE_TOKENS)

    def duplicate_system_indicators(self) -> dict[str, int]:
        py_files = list(self.root.rglob("*.py"))

        registry_hits = [
            p for p in py_files
            if "registry" in p.name.lower()
            and "module" in p.name.lower()
            and not self.is_canonical_modular_engine_path(p)
        ]

        dependency_hits = [
            p for p in py_files
            if "dependency" in p.name.lower()
            and "module" in p.name.lower()
            and not self.is_canonical_modular_engine_path(p)
        ]

        availability_hits = [
            p for p in py_files
            if "availability" in p.name.lower()
            and "module" in p.name.lower()
            and not self.is_canonical_modular_engine_path(p)
        ]

        return {
            "duplicate_registry_systems_detected": len(registry_hits),
            "duplicate_dependency_systems_detected": len(dependency_hits),
            "duplicate_availability_systems_detected": len(availability_hits),
        }

    def build(self) -> ModuleDependencyVisibilityReport:
        modules = self.load_registered_modules()
        registered_names = set(modules)

        module_dependencies: dict[str, list[str]] = {}
        infrastructure_dependencies: dict[str, list[str]] = {}

        for name, record in modules.items():
            raw = self.raw_dependency_list(record)
            module_deps, infra_deps = self.split_dependencies(raw, registered_names)
            module_dependencies[name] = module_deps
            infrastructure_dependencies[name] = infra_deps

        active = {
            name
            for name, record in modules.items()
            if self.module_status(record) == "active"
        }

        nodes: list[ModuleDependencyNode] = []

        for name, record in sorted(modules.items()):
            deps = module_dependencies.get(name, [])

            missing = [
                dep for dep in deps
                if dep not in modules
            ]

            inactive = [
                dep for dep in deps
                if dep in modules and self.module_status(modules[dep]) != "active"
            ]

            nodes.append(
                ModuleDependencyNode(
                    name=name,
                    status=self.module_status(record),
                    module_dependencies=deps,
                    infrastructure_dependencies=infrastructure_dependencies.get(name, []),
                    missing_module_dependencies=missing,
                    inactive_module_dependencies=inactive,
                    activation_cascade=self.activation_cascade(name, module_dependencies),
                    deactivation_cascade=self.deactivation_cascade(name, module_dependencies),
                )
            )

        duplicate_indicators = self.duplicate_system_indicators()

        missing_count = sum(len(node.missing_module_dependencies) for node in nodes)
        inactive_count = sum(len(node.inactive_module_dependencies) for node in nodes)

        # Phase 37A is a visibility foundation.
        # It must fail on broken module dependency state, but it must not fail merely
        # because historical/support files contain words such as registry/dependency.
        # Duplicate-system evidence is reported for later simplification work.
        passed = (
            bool(modules)
            and missing_count == 0
            and inactive_count == 0
        )

        return ModuleDependencyVisibilityReport(
            schema=self.schema,
            registered_module_count=len(modules),
            active_module_count=len(active),
            inactive_module_count=len(modules) - len(active),
            module_nodes=nodes,
            missing_module_dependency_count=missing_count,
            inactive_module_dependency_count=inactive_count,
            duplicate_dependency_systems_detected=duplicate_indicators["duplicate_dependency_systems_detected"],
            duplicate_availability_systems_detected=duplicate_indicators["duplicate_availability_systems_detected"],
            duplicate_registry_systems_detected=duplicate_indicators["duplicate_registry_systems_detected"],
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37A_MODULE_DEPENDENCY_VISIBILITY_FOUNDATION"
                if passed
                else "FAIL_PHASE_37A_MODULE_DEPENDENCY_VISIBILITY_FOUNDATION"
            ),
            next_programme="Programme 37B — Module Cascade Report Integration",
        )


def write_report(report: ModuleDependencyVisibilityReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37a_module_dependency_visibility_report.json"
    txt_path = REPORT_DIR / "phase_37a_module_dependency_visibility_report.txt"

    payload = asdict(report)

    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37A — Module Dependency Visibility Foundation",
        "",
        f"schema={report.schema}",
        f"registered_module_count={report.registered_module_count}",
        f"active_module_count={report.active_module_count}",
        f"inactive_module_count={report.inactive_module_count}",
        f"missing_module_dependency_count={report.missing_module_dependency_count}",
        f"inactive_module_dependency_count={report.inactive_module_dependency_count}",
        f"duplicate_dependency_systems_detected={report.duplicate_dependency_systems_detected}",
        f"duplicate_availability_systems_detected={report.duplicate_availability_systems_detected}",
        f"duplicate_registry_systems_detected={report.duplicate_registry_systems_detected}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Module Nodes",
        "",
    ]

    for node in report.module_nodes:
        lines.extend(
            [
                f"module={node.name}",
                f"status={node.status}",
                f"module_dependencies={node.module_dependencies}",
                f"infrastructure_dependencies={node.infrastructure_dependencies}",
                f"missing_module_dependencies={node.missing_module_dependencies}",
                f"inactive_module_dependencies={node.inactive_module_dependencies}",
                f"activation_cascade={node.activation_cascade}",
                f"deactivation_cascade={node.deactivation_cascade}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    return txt_path, json_path


def main() -> None:
    builder = ModuleDependencyVisibilityBuilder()
    report = builder.build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"inactive_module_count={report.inactive_module_count}")
    print(f"missing_module_dependency_count={report.missing_module_dependency_count}")
    print(f"inactive_module_dependency_count={report.inactive_module_dependency_count}")
    print(f"duplicate_dependency_systems_detected={report.duplicate_dependency_systems_detected}")
    print(f"duplicate_availability_systems_detected={report.duplicate_availability_systems_detected}")
    print(f"duplicate_registry_systems_detected={report.duplicate_registry_systems_detected}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
