COMPARISON_PAIRS = [
    (
        "Coolant channel count",
        "number_of_coolant_channels",
        "recommended_channel_count",
        "best_full_engine_regen_channel_count",
    ),
    (
        "Coolant channel width",
        "coolant_channel_width",
        "recommended_channel_width",
        "best_full_engine_regen_channel_width",
    ),
    (
        "Coolant channel height",
        "coolant_channel_height",
        "recommended_channel_height",
        "best_full_engine_regen_channel_height",
    ),
    (
        "Rib width",
        "rib_width",
        "recommended_rib_width",
        "best_full_engine_regen_rib_width",
    ),
    (
        "Effective rib width",
        "effective_rib_width",
        "recommended_effective_rib_width",
        "best_full_engine_regen_effective_rib_width",
    ),
    (
        "Channel fit ratio",
        "channel_fit_ratio",
        "recommended_channel_fit_ratio",
        "best_full_engine_regen_channel_fit_ratio",
    ),
    (
        "Coolant velocity",
        "coolant_velocity",
        "recommended_coolant_velocity",
        "best_full_engine_regen_max_velocity",
    ),
    (
        "Coolant Reynolds number",
        "coolant_reynolds_number",
        "recommended_reynolds_number",
        "best_full_engine_regen_min_reynolds",
    ),
    (
        "Hot wall temperature",
        "hot_gas_side_wall_temperature",
        "material_aware_combined_predicted_hot_wall_temperature",
        "best_full_engine_regen_max_hot_wall_temperature",
    ),
    (
        "Thermal margin",
        "material_temperature_margin",
        "material_aware_combined_thermal_margin",
        "best_full_engine_regen_thermal_margin",
    ),
]


def _fmt(value):
    if value in (None, "", "N/A", "None"):
        return "N/A"

    if isinstance(value, float):
        return f"{value:.6g}"

    return str(value)


def _num(value):
    try:
        if value in (None, "", "N/A", "None"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _delta(before, after):
    before_n = _num(before)
    after_n = _num(after)

    if before_n is None or after_n is None:
        return "N/A"

    change = after_n - before_n

    if before_n != 0:
        percent = 100.0 * change / abs(before_n)
        return f"{change:.6g} ({percent:.3g}%)"

    return f"{change:.6g}"


def build_before_after_comparison(results):
    results = results if isinstance(results, dict) else {}

    rows = []

    for label, manual_key, recommended_key, best_key in COMPARISON_PAIRS:
        manual = results.get(manual_key)
        recommended = results.get(recommended_key)
        best = results.get(best_key)

        if manual in (None, "", "N/A", "None") and recommended in (None, "", "N/A", "None") and best in (None, "", "N/A", "None"):
            continue

        rows.append({
            "label": label,
            "manual_key": manual_key,
            "recommended_key": recommended_key,
            "best_key": best_key,
            "manual": manual,
            "recommended": recommended,
            "best": best,
            "manual_to_recommended_delta": _delta(manual, recommended),
            "recommended_to_best_delta": _delta(recommended, best),
            "manual_to_best_delta": _delta(manual, best),
        })

    text = build_before_after_text(rows, results)

    return {
        "before_after_comparison_status": "RECORDED" if rows else "EMPTY",
        "before_after_comparison_count": len(rows),
        "before_after_comparison_rows": rows,
        "before_after_comparison_text": text,
    }


def build_before_after_text(rows, results):
    lines = []
    lines.append("LEAF BEFORE / AFTER COMPARISON")
    lines.append("==============================")
    lines.append("")

    if not rows:
        lines.append("No before/after comparison data available.")
        return "\n".join(lines)

    lines.append("Design status summary:")
    lines.append(f"- Manual geometry valid: {_fmt(results.get('channel_geometry_valid'))}")
    lines.append(f"- Recommended geometry status: {_fmt(results.get('recommended_geometry_status'))}")
    lines.append(f"- Full-engine regen status: {_fmt(results.get('full_engine_regen_geometry_status'))}")
    lines.append(f"- Best full-engine regen status: {_fmt(results.get('best_full_engine_regen_status'))}")
    lines.append("")

    for row in rows:
        lines.append(row["label"])
        lines.append("-" * len(row["label"]))
        lines.append(f"Manual [{row['manual_key']}]: {_fmt(row['manual'])}")
        lines.append(f"Recommended [{row['recommended_key']}]: {_fmt(row['recommended'])}")
        lines.append(f"Best available [{row['best_key']}]: {_fmt(row['best'])}")
        lines.append(f"Manual → Recommended change: {row['manual_to_recommended_delta']}")
        lines.append(f"Recommended → Best change: {row['recommended_to_best_delta']}")
        lines.append(f"Manual → Best change: {row['manual_to_best_delta']}")
        lines.append("")

    return "\n".join(lines)


def attach_before_after_comparison(results):
    if results is None:
        return results

    comparison = build_before_after_comparison(results)

    for key, value in comparison.items():
        results[key] = value

    return results