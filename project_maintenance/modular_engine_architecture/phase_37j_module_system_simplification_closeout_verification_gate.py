from __future__ import annotations

import py_compile
from pathlib import Path

from phase_37j_module_system_simplification_closeout_verification import (
    ModuleSystemSimplificationCloseoutVerifier,
    write_report,
    ROOT,
)


def main() -> None:
    current_file = Path(__file__).resolve()
    source_file = current_file.with_name(
        "phase_37j_module_system_simplification_closeout_verification.py"
    )

    py_compile.compile(str(source_file), doraise=True)
    py_compile.compile(str(current_file), doraise=True)

    report = ModuleSystemSimplificationCloseoutVerifier().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"cascade_row_count={report.cascade_row_count}")
    print(f"duplicate_candidate_count={report.duplicate_candidate_count}")
    print(f"planned_retirement_count={report.planned_retirement_count}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"retained_reference_count={report.retained_reference_count}")
    print(f"import_replacement_required_count={report.import_replacement_required_count}")
    print(f"manual_review_required_count={report.manual_review_required_count}")
    print(f"compile_failure_count={report.compile_failure_count}")
    print(f"module_discovery_preserved={report.module_discovery_preserved}")
    print(f"cascade_visibility_preserved={report.cascade_visibility_preserved}")
    print(f"repository_simplification_verified={report.repository_simplification_verified}")
    print(f"deletion_performed={report.deletion_performed}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
