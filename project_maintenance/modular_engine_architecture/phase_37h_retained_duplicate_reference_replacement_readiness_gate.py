from __future__ import annotations

import py_compile
from pathlib import Path

from phase_37h_retained_duplicate_reference_replacement_readiness import (
    RetainedDuplicateReferenceReplacementReadinessChecker,
    write_report,
    ROOT,
)


def main() -> None:
    current_file = Path(__file__).resolve()
    source_file = current_file.with_name(
        "phase_37h_retained_duplicate_reference_replacement_readiness.py"
    )

    py_compile.compile(str(source_file), doraise=True)
    py_compile.compile(str(current_file), doraise=True)

    report = RetainedDuplicateReferenceReplacementReadinessChecker().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"total_reference_count={report.total_reference_count}")
    print(f"auto_replace_allowed_count={report.auto_replace_allowed_count}")
    print(f"manual_review_required_count={report.manual_review_required_count}")
    print(f"text_only_reference_count={report.text_only_reference_count}")
    print(f"import_replacement_required_count={report.import_replacement_required_count}")
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
