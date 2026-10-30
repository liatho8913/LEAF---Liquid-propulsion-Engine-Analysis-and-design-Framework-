from __future__ import annotations

import py_compile
from pathlib import Path

from phase_37b_module_cascade_report_integration import (
    ModuleCascadeReportIntegrator,
    write_report,
    ROOT,
)


def main() -> None:
    current_file = Path(__file__).resolve()
    source_file = current_file.with_name("phase_37b_module_cascade_report_integration.py")

    py_compile.compile(str(source_file), doraise=True)
    py_compile.compile(str(current_file), doraise=True)

    report = ModuleCascadeReportIntegrator().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"missing_module_dependency_count={report.missing_module_dependency_count}")
    print(f"inactive_module_dependency_count={report.inactive_module_dependency_count}")
    print(f"new_dependency_engine_created={report.new_dependency_engine_created}")
    print(f"new_registry_created={report.new_registry_created}")
    print(f"new_report_engine_created={report.new_report_engine_created}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
