def build_recommendation_explanation(results):
    results = results if isinstance(results, dict) else {}

    causes = results.get("failure_root_cause_items") or []
    recommendations = []

    def add(category, recommendation, why, expected_effect, caution=""):
        recommendations.append({
            "category": category,
            "recommendation": recommendation,
            "why": why,
            "expected_effect": expected_effect,
            "caution": caution,
        })

    categories = {
        cause.get("category")
        for cause in causes
        if isinstance(cause, dict)
    }

    if "GEOMETRY_FIT" in categories:
        add(
            "GEOMETRY_FIT",
            "Revise coolant channel count, width, rib width, or allow variable geometry.",
            "One or more stations cannot fit the requested channel architecture.",
            "Improves circumferential fit and prevents collapsed rib width.",
            "Do not force a geometry pass if effective rib width falls below the requested safe rib width.",
        )

    if "COOLANT_REYNOLDS" in categories:
        add(
            "COOLANT_REYNOLDS",
            "Increase coolant Reynolds number by revising channel area, velocity, or coolant properties.",
            "Low Reynolds number weakens coolant-side heat transfer.",
            "Improves coolant heat-transfer coefficient and lowers wall temperature.",
            "Higher velocity may increase pressure drop.",
        )

    if "COOLANT_VELOCITY" in categories:
        add(
            "COOLANT_VELOCITY",
            "Increase total coolant flow area or revise channel count to reduce velocity.",
            "The design may require excessive coolant velocity to achieve thermal performance.",
            "Reduces erosion/pressure-drop risk and improves feasibility.",
            "Reducing velocity too far may reduce Reynolds number.",
        )

    if "THERMAL_MATERIAL_LIMIT" in categories:
        add(
            "THERMAL_MATERIAL_LIMIT",
            "Improve material capability, reduce heat load, improve coolant-side heat transfer, or add validated coating/film cooling.",
            "Hot-wall temperature exceeds the current material capability.",
            "Increases thermal margin and may convert a thermal fail into a pass.",
            "Placeholder coating or film data must not create a validated pass.",
        )

    if "PRESSURE_DROP" in categories:
        add(
            "PRESSURE_DROP",
            "Rebalance channel hydraulic diameter, velocity, length, and pressure budget.",
            "The cooling solution may require more pressure drop than allowed.",
            "Improves pump/feed-system compatibility.",
            "Lower pressure drop can reduce heat-transfer performance.",
        )

    if "MISSING_DATA" in categories:
        add(
            "MISSING_DATA",
            "Complete sourced material, coating, coolant, and temperature-dependent property data.",
            "LEAF cannot produce a trusted validation pass without sufficient source data.",
            "Moves the design from source-blocked to validation-ready.",
            "Do not treat placeholder data as pass-capable.",
        )

    if "BEST_AVAILABLE_NOT_VALIDATED" in categories:
        add(
            "BEST_AVAILABLE_NOT_VALIDATED",
            "Treat the selected design as best available, not validated.",
            "The best candidate still failed one or more gates.",
            "Prevents false confidence and keeps the audit trail honest.",
            "Only benchmarking and further validation can promote this to a trusted pass.",
        )

    if not recommendations:
        add(
            "NO_CLEAR_RECOMMENDATION",
            "Improve structured validation outputs before making design changes.",
            "No recognised root-cause category was available.",
            "Makes future reports more explainable.",
            "This indicates an architecture/reporting gap, not necessarily a physical pass.",
        )

    text = build_recommendation_text(recommendations)

    return {
        "recommendation_explanation_status": "RECORDED",
        "recommendation_explanation_count": len(recommendations),
        "recommendation_explanation_items": recommendations,
        "recommendation_explanation_text": text,
    }


def build_recommendation_text(recommendations):
    lines = []
    lines.append("LEAF RECOMMENDATION EXPLANATION")
    lines.append("===============================")
    lines.append("")

    for index, item in enumerate(recommendations, start=1):
        lines.append(f"Recommendation {index}: {item.get('recommendation')}")
        lines.append(f"Category: {item.get('category')}")
        lines.append("")
        lines.append("Why:")
        lines.append(f"- {item.get('why')}")
        lines.append("")
        lines.append("Expected effect:")
        lines.append(f"- {item.get('expected_effect')}")
        lines.append("")
        lines.append("Caution:")
        lines.append(f"- {item.get('caution') or 'None recorded.'}")
        lines.append("")
        lines.append("-" * 50)
        lines.append("")

    return "\n".join(lines)


def attach_recommendation_explanation(results):
    if results is None:
        return results

    explanation = build_recommendation_explanation(results)

    for key, value in explanation.items():
        results[key] = value

    return results