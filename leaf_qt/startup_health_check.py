import importlib


OPTIONAL_SYSTEMS = [
    {
        "name": "Foundation Attachment Pipeline",
        "module": "foundation_attachment_pipeline",
        "required": True,
    },
    {
        "name": "Report Ownership",
        "module": "report_ownership",
        "required": True,
    },
    {
        "name": "Report Viewer",
        "module": "report_viewer_window",
        "required": False,
    },
    {
        "name": "Report Formatting",
        "module": "report_formatting",
        "required": False,
    },
    {
        "name": "Station Report Builder",
        "module": "station_report_builder",
        "required": False,
    },
    {
        "name": "Foundation Regression Tests",
        "module": "foundation_regression_tests",
        "required": False,
    },
    {
        "name": "Benchmark Database",
        "module": "benchmark_case_database",
        "required": False,
    },
    {
        "name": "Benchmark Evaluator",
        "module": "benchmark_evaluator",
        "required": False,
    },
    {
        "name": "Benchmark Panel",
        "module": "benchmark_panel",
        "required": False,
    },
    {
        "name": "Engine Reproduction Validation",
        "module": "engine_reproduction_validation",
        "required": False,
    },
    {
        "name": "NASA CEA Runner",
        "module": "cea_integration.cea_runner",
        "required": False,
    },
    {
        "name": "Material Database",
        "module": "material_database",
        "required": False,
    },
    {
        "name": "Coolant Database",
        "module": "coolant_database",
        "required": False,
    },
    {
        "name": "Fluid Property Database",
        "module": "fluid_property_database",
        "required": False,
    },
]


def run_startup_health_check():
    rows = []

    for system in OPTIONAL_SYSTEMS:
        name = system["name"]
        module_name = system["module"]
        required = bool(system.get("required", False))

        try:
            importlib.import_module(module_name)

            rows.append({
                "name": name,
                "module": module_name,
                "required": required,
                "status": "AVAILABLE",
                "error": "",
            })

        except Exception as error:
            rows.append({
                "name": name,
                "module": module_name,
                "required": required,
                "status": "FAILED_IMPORT" if required else "MISSING_OPTIONAL",
                "error": str(error),
            })

    required_failures = [
        row for row in rows
        if row["required"] and row["status"] != "AVAILABLE"
    ]

    optional_failures = [
        row for row in rows
        if not row["required"] and row["status"] != "AVAILABLE"
    ]

    if required_failures:
        overall_status = "CRITICAL_FOUNDATION_MISSING"
    elif optional_failures:
        overall_status = "AVAILABLE_WITH_OPTIONAL_WARNINGS"
    else:
        overall_status = "PASS"

    return {
        "startup_health_status": overall_status,
        "startup_health_required_failure_count": len(required_failures),
        "startup_health_optional_warning_count": len(optional_failures),
        "startup_health_rows": rows,
        "startup_health_text": build_startup_health_text(
            overall_status,
            rows,
        ),
    }


def build_startup_health_text(overall_status, rows):
    lines = []
    lines.append("LEAF STARTUP HEALTH CHECK")
    lines.append("=========================")
    lines.append("")
    lines.append(f"Overall status: {overall_status}")
    lines.append("")

    for row in rows:
        required_text = "required" if row["required"] else "optional"

        lines.append(f"{row['name']}")
        lines.append(f"- Module: {row['module']}")
        lines.append(f"- Type: {required_text}")
        lines.append(f"- Status: {row['status']}")

        if row.get("error"):
            lines.append(f"- Error: {row['error']}")

        lines.append("")

    return "\n".join(lines)