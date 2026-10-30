from __future__ import annotations

from core.architecture.models import ArchitectureReport


def build_standard_architecture_text_report(report: ArchitectureReport) -> str:
    data = report.to_dict()

    lines = [
        report.title,
        "=" * len(report.title),
        f"schema={report.schema}",
        f"passed={data['passed']}",
        f"safe_to_modify_files={report.safe_to_modify_files}",
        "",
        "SUMMARY",
        "-------",
    ]

    for key, value in report.summary.items():
        lines.append(f"{key}={value}")

    lines.extend(["", "FINDINGS", "--------"])

    if not report.findings:
        lines.append("No findings.")
    else:
        for finding in report.findings:
            path = f" | {finding.path}" if finding.path else ""
            lines.append(
                f"{finding.status} | {finding.code} | {finding.message}{path}"
            )

    return "\n".join(lines)
