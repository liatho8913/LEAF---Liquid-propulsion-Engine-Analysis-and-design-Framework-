from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

KEYS = [
    "optimisation_report_backend_payload",
    "optimisation_report_backend_report",
    "optimisation_report_backend_source_count",
    "optimisation_report_backend_summary",
    "optimisation_report_history",
    "optimisation_report_html_exported",
    "optimisation_report_metrics",
    "optimisation_report_pdf_exported",
    "optimisation_report_qt_window_created",
    "optimisation_report_section_count",
    "optimisation_report_sections",
    "phase_16_unified_regen_ecosystem_allowed",
]

PREFIXES = [
    "optimisation_report_backend_",
    "optimisation_report_",
    "phase_16_",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    names = KEYS + PREFIXES

    if "KNOWN_DEVELOPMENT_KEYS = {" in text:
        additions = "\n".join(f'    "{k}",' for k in names)
        if '"optimisation_report_backend_payload",' not in text:
            text = text.replace(
                "KNOWN_DEVELOPMENT_KEYS = {",
                "KNOWN_DEVELOPMENT_KEYS = {\n" + additions
            )

    if "EXPECTED_PREFIX_VISIBILITY = {" in text:
        additions = "\n".join(
            f'    "{k}": "DIAGNOSTIC_ONLY",'
            for k in names
        )
        if '"optimisation_report_backend_payload": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace(
                "EXPECTED_PREFIX_VISIBILITY = {",
                "EXPECTED_PREFIX_VISIBILITY = {\n" + additions
            )

    path.write_text(text)
    print(f"PATCHED {path}")

print("PHASE_15D_REMAINING_RESULT_KEYS_REGISTERED")
