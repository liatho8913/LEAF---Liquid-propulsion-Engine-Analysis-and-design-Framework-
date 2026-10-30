"""
PHASE 11B.2O
Automatic Geometry Objective Selector

Defines the active regen optimisation objective before automatic decision scoring.
"""


VALID_REGEN_OBJECTIVES = {
    "BALANCED": {
        "label": "Balanced",
        "description": "Balances geometry validity, thermal margin, pressure drop, and Reynolds performance.",
    },
    "THERMAL": {
        "label": "Thermal",
        "description": "Prioritises reducing wall temperature and improving thermal margin.",
    },
    "PRESSURE_DROP": {
        "label": "Pressure Drop",
        "description": "Prioritises keeping coolant pressure drop within limits.",
    },
    "REYNOLDS": {
        "label": "Reynolds",
        "description": "Prioritises turbulent or target coolant Reynolds behaviour.",
    },
    "MANUFACTURABILITY": {
        "label": "Manufacturability",
        "description": "Prioritises practical channel count, rib width, wall thickness, and geometry fit.",
    },
    "MINIMUM_MASS": {
        "label": "Minimum Mass",
        "description": "Prioritises lower wall/jacket/channel mass while respecting validation gates.",
    },
}


def attach_regen_automatic_geometry_objective_selector(results):
    if not isinstance(results, dict):
        return results

    selected = normalise_regen_objective(
        results.get("regen_optimisation_objective")
        or results.get("regen_selected_performance_metric")
        or results.get("regen_geometry_objective")
        or "BALANCED"
    )

    objective_data = VALID_REGEN_OBJECTIVES[selected]

    results.update({
        "regen_automatic_geometry_objective_selector_complete": True,
        "phase_11b_2o_regen_automatic_geometry_objective_selector_complete": True,
        "regen_automatic_geometry_objective": selected,
        "regen_optimisation_objective": selected,
        "regen_automatic_geometry_objective_label": objective_data["label"],
        "regen_automatic_geometry_objective_description": objective_data["description"],
        "regen_automatic_geometry_available_objectives": list(VALID_REGEN_OBJECTIVES.keys()),
        "regen_automatic_geometry_objective_status": (
            "PASS_REGEN_AUTOMATIC_GEOMETRY_OBJECTIVE_SELECTED"
        ),
        "regen_automatic_geometry_objective_report": build_objective_report(selected),

        # Safety locks.
        "regen_automatic_geometry_objective_solver_executed": False,
        "regen_automatic_geometry_objective_live_geometry_modified": False,
        "regen_automatic_geometry_objective_candidate_committed": False,
    })

    return results


def normalise_regen_objective(value):
    text = str(value or "BALANCED").strip().upper()
    text = text.replace(" ", "_").replace("-", "_")

    aliases = {
        "BALANCE": "BALANCED",
        "WALL_TEMP": "THERMAL",
        "WALL_TEMPERATURE": "THERMAL",
        "TEMPERATURE": "THERMAL",
        "DP": "PRESSURE_DROP",
        "PRESSURE": "PRESSURE_DROP",
        "RE": "REYNOLDS",
        "REYNOLDS_NUMBER": "REYNOLDS",
        "MANUFACTURING": "MANUFACTURABILITY",
        "MASS": "MINIMUM_MASS",
        "LOW_MASS": "MINIMUM_MASS",
    }

    text = aliases.get(text, text)

    if text not in VALID_REGEN_OBJECTIVES:
        return "BALANCED"

    return text


def build_objective_report(selected):
    data = VALID_REGEN_OBJECTIVES[selected]

    lines = [
        "LEAF PHASE 11B.2O AUTOMATIC GEOMETRY OBJECTIVE SELECTOR",
        "=======================================================",
        "",
        f"Selected objective: {selected}",
        f"Label: {data['label']}",
        f"Description: {data['description']}",
        "",
        "Available objectives:",
    ]

    for key, item in VALID_REGEN_OBJECTIVES.items():
        lines.append(f"- {key}: {item['description']}")

    lines.extend([
        "",
        "Safety State:",
        "- Solver executed: False",
        "- Live geometry modified: False",
        "- Candidate committed: False",
    ])

    return "\n".join(lines)