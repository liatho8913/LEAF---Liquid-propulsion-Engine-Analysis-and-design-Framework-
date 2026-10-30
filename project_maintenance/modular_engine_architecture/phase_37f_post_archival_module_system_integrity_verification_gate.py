from __future__ import annotations

import py_compile
from pathlib import Path

from phase_37f_post_archival_module_system_integrity_verification import (
    PostArchivalModuleSystemIntegrityVerifier,
    write_report,
    ROOT,
)


def main() -> None:
    current_file = Path(__file__).resolve()
    source_file = current_file.with_name(
        "phase_37f_post_archival_module_system_integrity_verification.py"
    )

    py_compile.compile(str(source_file), doraise=True)
    py_compile.compile(str(current_file), doraise=True)

    report = PostArchivalModuleSystemIntegrityVerifier().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"missing_module_dependency_count={report.missing_module_dependency_count}")
    print(f"inactive_module_dependency_count={report.inactive_module_dependency_count}")
    print(f"cascade_row_count={report.cascade_row_count}")
    print(f"archived_count={report.archived_count}")
    print(f"retained_count={report.retained_count}")
    print(f"rollback_available_count={report.rollback_available_count}")
    print(f"compile_failure_count={report.compile_failure_count}")
    print(f"module_discovery_preserved={report.module_discovery_preserved}")
    print(f"cascade_reporting_preserved={report.cascade_reporting_preserved}")
    print(f"rollback_paths_preserved={report.rollback_paths_preserved}")
    print(f"permanent_deletion_detected={report.permanent_deletion_detected}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
