from __future__ import annotations

import py_compile
from pathlib import Path

from phase_37g_retained_duplicate_module_system_reference_resolution_plan import (
    RetainedDuplicateModuleSystemReferenceResolver,
    write_report,
    ROOT,
)


def main() -> None:
    current_file = Path(__file__).resolve()
    source_file = current_file.with_name(
        "phase_37g_retained_duplicate_module_system_reference_resolution_plan.py"
    )

    py_compile.compile(str(source_file), doraise=True)
    py_compile.compile(str(current_file), doraise=True)

    report = RetainedDuplicateModuleSystemReferenceResolver().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"total_reference_count={report.total_reference_count}")
    print(f"deletion_performed={report.deletion_performed}")
    print(f"files_modified={report.files_modified}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
