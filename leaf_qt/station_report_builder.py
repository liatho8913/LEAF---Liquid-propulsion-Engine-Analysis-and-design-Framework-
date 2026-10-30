STATION_VISIBILITY_THERMAL = "THERMAL_REPORT"
STATION_VISIBILITY_VALIDATION = "VALIDATION_REPORT"
STATION_VISIBILITY_DIAGNOSTIC = "DIAGNOSTIC_REPORT"
STATION_VISIBILITY_INTERNAL = "INTERNAL_ONLY"
STATION_VISIBILITY_EXPORT = "CSV_EXPORT"


STATION_COLUMN_REGISTRY = {
    "station_index": {
        "label": "Station Index",
        "visibility": STATION_VISIBILITY_EXPORT,
    },
    "station_label": {
        "label": "Station",
        "visibility": STATION_VISIBILITY_EXPORT,
    },
    "x": {
        "label": "x [m]",
        "visibility": STATION_VISIBILITY_EXPORT,
    },
    "radius": {
        "label": "Radius [m]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "cross_sectional_area": {
        "label": "Area [m²]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "mach_number": {
        "label": "Mach",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "static_temperature": {
        "label": "Static Temp [K]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "static_pressure": {
        "label": "Static Pressure [Pa]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "regen_heat_flux": {
        "label": "Heat Flux [W/m²]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "hot_gas_side_wall_temperature": {
        "label": "Hot Wall Temp [K]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "coolant_side_wall_temperature_calculated": {
        "label": "Coolant Wall Temp [K]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "coolant_temperature": {
        "label": "Coolant Temp [K]",
        "visibility": STATION_VISIBILITY_THERMAL,
    },
    "coolant_reynolds_number": {
        "label": "Reynolds",
        "visibility": STATION_VISIBILITY_VALIDATION,
    },
    "coolant_velocity": {
        "label": "Coolant Velocity [m/s]",
        "visibility": STATION_VISIBILITY_VALIDATION,
    },
    "coolant_pressure_drop": {
        "label": "Pressure Drop [Pa]",
        "visibility": STATION_VISIBILITY_VALIDATION,
    },
    "material_temperature_margin": {
        "label": "Material Margin [K]",
        "visibility": STATION_VISIBILITY_VALIDATION,
    },
    "channel_geometry_valid": {
        "label": "Geometry Valid",
        "visibility": STATION_VISIBILITY_VALIDATION,
    },
    "failure_reason": {
        "label": "Failure Reason",
        "visibility": STATION_VISIBILITY_DIAGNOSTIC,
    },
    "diagnostic_note": {
        "label": "Diagnostic Note",
        "visibility": STATION_VISIBILITY_DIAGNOSTIC,
    },
}


def get_station_rows(results):
    results = results if isinstance(results, dict) else {}

    rows = (
        results.get("regen_station_rows")
        or results.get("station_rows")
        or results.get("axial_station_rows")
        or results.get("regen_axial_station_rows")
        or []
    )

    if isinstance(rows, list):
        return rows

    return []


def get_station_columns_for_visibility(rows, visibility):
    columns = []

    always_include = [
        "station_index",
        "station_label",
        "x",
    ]

    for key in always_include:
        if any(isinstance(row, dict) and key in row for row in rows):
            columns.append(key)

    for key, meta in STATION_COLUMN_REGISTRY.items():
        if key in columns:
            continue

        if meta.get("visibility") != visibility:
            continue

        if any(isinstance(row, dict) and key in row for row in rows):
            columns.append(key)

    return columns


def get_station_columns_for_csv(rows):
    columns = []

    for key in STATION_COLUMN_REGISTRY:
        if any(isinstance(row, dict) and key in row for row in rows):
            columns.append(key)

    if not columns and rows and isinstance(rows[0], dict):
        columns = list(rows[0].keys())

    return columns


def build_station_table_text(results, visibility=STATION_VISIBILITY_THERMAL, max_rows=None):
    rows = get_station_rows(results)

    lines = []
    lines.append("LEAF STATION-BY-STATION AXIAL TABLE")
    lines.append("===================================")
    lines.append(f"Visibility: {visibility}")
    lines.append("")

    if not rows:
        lines.append("No station-by-station rows found in results.")
        lines.append("")
        lines.append("Expected one of these result keys:")
        lines.append("- regen_station_rows")
        lines.append("- station_rows")
        lines.append("- axial_station_rows")
        lines.append("- regen_axial_station_rows")
        return "\n".join(lines)

    if max_rows is not None:
        rows = rows[:max_rows]

    columns = get_station_columns_for_visibility(rows, visibility)

    if not columns:
        lines.append("Station rows exist, but no columns matched this visibility category.")
        return "\n".join(lines)

    header_labels = [
        STATION_COLUMN_REGISTRY.get(key, {}).get("label", key)
        for key in columns
    ]

    header = " | ".join(header_labels)
    lines.append(header)
    lines.append("-" * len(header))

    for row in rows:
        if not isinstance(row, dict):
            continue

        values = [
            _format_cell(row.get(key))
            for key in columns
        ]

        lines.append(" | ".join(values))

    return "\n".join(lines)


def build_station_validation_table_text(results, max_rows=None):
    return build_station_table_text(
        results,
        visibility=STATION_VISIBILITY_VALIDATION,
        max_rows=max_rows,
    )


def build_station_diagnostic_table_text(results, max_rows=None):
    return build_station_table_text(
        results,
        visibility=STATION_VISIBILITY_DIAGNOSTIC,
        max_rows=max_rows,
    )


def build_station_table_csv_text(results):
    rows = get_station_rows(results)

    if not rows:
        return ""

    columns = get_station_columns_for_csv(rows)

    if not columns:
        return ""

    header_labels = [
        STATION_COLUMN_REGISTRY.get(key, {}).get("label", key)
        for key in columns
    ]

    lines = []
    lines.append(",".join(_csv_escape(label) for label in header_labels))

    for row in rows:
        if not isinstance(row, dict):
            continue

        values = [
            _csv_escape(row.get(key))
            for key in columns
        ]

        lines.append(",".join(values))

    return "\n".join(lines)


def _format_cell(value):
    if value in (None, "", "N/A", "None"):
        return "N/A"

    if isinstance(value, float):
        return f"{value:.6g}"

    return str(value)


def _csv_escape(value):
    text = _format_cell(value)

    if "," in text or "\n" in text or '"' in text:
        text = text.replace('"', '""')
        return f'"{text}"'

    return text

def get_station_column_registry():
    return dict(STATION_COLUMN_REGISTRY)


def get_station_columns_for_named_view(rows, view_name):
    view_name = str(view_name or "").upper()

    if view_name == "THERMAL":
        return get_station_columns_for_visibility(
            rows,
            STATION_VISIBILITY_THERMAL,
        )

    if view_name == "VALIDATION":
        return get_station_columns_for_visibility(
            rows,
            STATION_VISIBILITY_VALIDATION,
        )

    if view_name == "DIAGNOSTICS":
        return get_station_columns_for_visibility(
            rows,
            STATION_VISIBILITY_DIAGNOSTIC,
        )

    if view_name in ("FULL", "CSV", "EXPORT"):
        return get_station_columns_for_csv(rows)

    return get_station_columns_for_csv(rows)


def get_station_column_label(key):
    return STATION_COLUMN_REGISTRY.get(key, {}).get("label", key)


def build_station_view_rows(results, view_name):
    rows = get_station_rows(results)
    columns = get_station_columns_for_named_view(rows, view_name)

    return rows, columns