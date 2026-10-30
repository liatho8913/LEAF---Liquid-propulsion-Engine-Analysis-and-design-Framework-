from dataclasses import dataclass, asdict
import math

try:
    from leaf_qt.regen_geometry_constraint_owner import (
        evaluate_regen_geometry_constraints,
        flatten_constraint_result,
    )
    from leaf_qt.history.regen_geometry_iteration_history import (
        RegenGeometryIterationHistory,
        flatten_iteration_history_summary,
    )
except Exception:
    from regen_geometry_constraint_owner import (
        evaluate_regen_geometry_constraints,
        flatten_constraint_result,
    )
    from regen_geometry_iteration_history import (
        RegenGeometryIterationHistory,
        flatten_iteration_history_summary,
    )

@dataclass
class RegenGeometryCandidate:
    channel_count: int
    channel_width: float
    channel_height: float
    rib_width: float
    pitch: float
    effective_rib_width: float
    fit_ratio: float
    single_channel_area: float
    total_flow_area: float
    wetted_perimeter: float
    hydraulic_diameter: float
    coolant_velocity: float
    reynolds_number: float
    estimated_pressure_drop: float | None
    circumferential_coverage: float
    total_wetted_perimeter: float
    score: float
    status: str


def _friction_factor(reynolds: float | None) -> float | None:
    if reynolds is None or reynolds <= 0:
        return None
    if reynolds < 2300:
        return 64.0 / reynolds
    return 0.3164 / (reynolds ** 0.25)


def _pressure_drop(friction_factor, length, hydraulic_diameter, density, velocity):
    if (
        friction_factor is None
        or length is None
        or hydraulic_diameter is None
        or density is None
        or velocity is None
        or length <= 0
        or hydraulic_diameter <= 0
        or density <= 0
    ):
        return None

    return friction_factor * (length / hydraulic_diameter) * 0.5 * density * velocity ** 2


def generate_regen_geometry_candidates(
    channel_mid_radius,
    coolant_mass_flow_rate,
    coolant_density,
    coolant_dynamic_viscosity,
    target_reynolds_number=10000.0,
    minimum_rib_width=0.0005,
    minimum_channel_width=0.0005,
    maximum_channel_height=None,
    channel_aspect_ratio=2.0,
    minimum_channel_count=4,
    maximum_channel_count=300,
    maximum_coolant_velocity=None,
    minimum_hydraulic_diameter=None,
    pressure_drop_limit=None,
    nozzle_length=None,
    minimum_cooling_coverage=None,
):
    if (
        channel_mid_radius is None
        or coolant_mass_flow_rate is None
        or coolant_density is None
        or coolant_dynamic_viscosity is None
        or channel_mid_radius <= 0
        or coolant_mass_flow_rate <= 0
        or coolant_density <= 0
        or coolant_dynamic_viscosity <= 0
    ):
        return {
            "status": "MISSING_INPUT_DATA",
            "best_candidate": None,
            "candidates_checked": 0,
            "valid_fit_candidates": 0,
            "rejected_fit_candidates": 0,
            "rejected_velocity_candidates": 0,
            "rejected_hydraulic_diameter_candidates": 0,
            "rejected_pressure_drop_candidates": 0,
            "rejected_cooling_coverage_candidates": 0,
        }

    if any(
        value is not None
        and not math.isfinite(value)
        for value in (
            channel_mid_radius,
            coolant_mass_flow_rate,
            coolant_density,
            coolant_dynamic_viscosity,
            target_reynolds_number,
            minimum_rib_width,
            minimum_channel_width,
            maximum_channel_height,
            channel_aspect_ratio,
            minimum_channel_count,
            maximum_channel_count,
            maximum_coolant_velocity,
            minimum_hydraulic_diameter,
            pressure_drop_limit,
            nozzle_length,
            minimum_cooling_coverage,
        )
    ):
        return {
            "status": "MISSING_INPUT_DATA",
            "best_candidate": None,
            "candidates_checked": 0,
            "valid_fit_candidates": 0,
            "rejected_fit_candidates": 0,
            "rejected_velocity_candidates": 0,
            "rejected_hydraulic_diameter_candidates": 0,
            "rejected_pressure_drop_candidates": 0,
            "rejected_cooling_coverage_candidates": 0,
        }

    maximum_channel_height = maximum_channel_height or minimum_channel_width * 4.0
    circumference = 2.0 * math.pi * channel_mid_radius

    best_candidate = None
    best_score = None
    iteration_history = RegenGeometryIterationHistory(max_records=250)

    candidates_checked = 0
    valid_fit_candidates = 0
    rejected_fit_candidates = 0
    rejected_velocity = 0
    rejected_hydraulic_diameter = 0
    rejected_pressure_drop = 0
    rejected_cooling_coverage = 0

    width_steps = 32
    height_steps = 24

    for channel_count in range(int(minimum_channel_count), int(maximum_channel_count) + 1):
        pitch = circumference / channel_count
        max_channel_width = pitch - minimum_rib_width

        if max_channel_width < minimum_channel_width:
            rejected_fit_candidates += 1
            continue

        for width_index in range(width_steps):
            width_fraction = width_index / max(1, width_steps - 1)

            channel_width = minimum_channel_width + width_fraction * (
                max_channel_width - minimum_channel_width
            )

            effective_rib_width = pitch - channel_width
            required_pitch = channel_width + minimum_rib_width
            fit_ratio = pitch / required_pitch if required_pitch > 0 else None

            if effective_rib_width < minimum_rib_width:
                rejected_fit_candidates += 1
                continue

            max_height_for_width = min(
                maximum_channel_height,
                max(channel_width * channel_aspect_ratio, minimum_channel_width),
            )

            for height_index in range(height_steps):
                candidates_checked += 1

                height_fraction = height_index / max(1, height_steps - 1)
                channel_height = minimum_channel_width + height_fraction * (
                    max_height_for_width - minimum_channel_width
                )

                single_area = channel_width * channel_height
                total_area = single_area * channel_count
                wetted_perimeter = 2.0 * (channel_width + channel_height)

                if single_area <= 0 or total_area <= 0 or wetted_perimeter <= 0:
                    rejected_fit_candidates += 1
                    continue

                hydraulic_diameter = 4.0 * single_area / wetted_perimeter

                if (
                    minimum_hydraulic_diameter is not None
                    and hydraulic_diameter < minimum_hydraulic_diameter
                ):
                    rejected_hydraulic_diameter += 1
                    continue

                coolant_velocity = coolant_mass_flow_rate / (coolant_density * total_area)

                if (
                    maximum_coolant_velocity is not None
                    and coolant_velocity > maximum_coolant_velocity
                ):
                    rejected_velocity += 1
                    continue

                reynolds = (
                    coolant_density
                    * coolant_velocity
                    * hydraulic_diameter
                    / coolant_dynamic_viscosity
                )

                friction_factor = _friction_factor(reynolds)

                pressure_drop = _pressure_drop(
                    friction_factor,
                    nozzle_length,
                    hydraulic_diameter,
                    coolant_density,
                    coolant_velocity,
                )

                if (
                    pressure_drop_limit is not None
                    and pressure_drop is not None
                    and pressure_drop > pressure_drop_limit
                ):
                    rejected_pressure_drop += 1
                    continue

                coverage = (channel_width * channel_count) / circumference

                if (
                    minimum_cooling_coverage is not None
                    and coverage < minimum_cooling_coverage
                ):
                    rejected_cooling_coverage += 1
                    continue

                total_wetted_perimeter = wetted_perimeter * channel_count

                reynolds_score = min(reynolds / target_reynolds_number, 1.5)

                velocity_score = 1.0
                if maximum_coolant_velocity:
                    velocity_score = 1.0 - min(coolant_velocity / maximum_coolant_velocity, 1.0)

                pressure_score = 1.0
                if pressure_drop_limit and pressure_drop is not None:
                    pressure_score = 1.0 - min(pressure_drop / pressure_drop_limit, 1.0)

                manufacturability_score = min(
                    effective_rib_width / max(minimum_rib_width, 1e-9), 3.0
                ) / 3.0

                coverage_score = min(coverage, 1.0)
                channel_count_score = min(channel_count / 40.0, 1.0)

                score = (
                    4.0 * reynolds_score
                    + 2.0 * velocity_score
                    + 2.0 * pressure_score
                    + 2.5 * coverage_score
                    + 1.0 * channel_count_score
                    + 1.0 * manufacturability_score
                )

                status = "PASS" if reynolds >= target_reynolds_number else "BEST_AVAILABLE_BELOW_TARGET"

                candidate = RegenGeometryCandidate(
                    channel_count=channel_count,
                    channel_width=channel_width,
                    channel_height=channel_height,
                    rib_width=effective_rib_width,
                    pitch=pitch,
                    effective_rib_width=effective_rib_width,
                    fit_ratio=fit_ratio,
                    single_channel_area=single_area,
                    total_flow_area=total_area,
                    wetted_perimeter=wetted_perimeter,
                    hydraulic_diameter=hydraulic_diameter,
                    coolant_velocity=coolant_velocity,
                    reynolds_number=reynolds,
                    estimated_pressure_drop=pressure_drop,
                    circumferential_coverage=coverage,
                    total_wetted_perimeter=total_wetted_perimeter,
                    score=score,
                    status=status,
                )

                candidate_dict = asdict(candidate)

                constraint_result = evaluate_regen_geometry_constraints(
                    candidate_dict,
                    minimum_rib_width=minimum_rib_width,
                    minimum_channel_width=minimum_channel_width,
                    minimum_channel_height=minimum_channel_width,
                    minimum_hydraulic_diameter=minimum_hydraulic_diameter,
                    maximum_coolant_velocity=maximum_coolant_velocity,
                    pressure_drop_limit=pressure_drop_limit,
                    minimum_cooling_coverage=minimum_cooling_coverage,
                )

                iteration_history.record_candidate(candidate_dict, constraint_result)

                if not constraint_result["geometry_constraints_pass"]:
                    rejected_fit_candidates += 1
                    continue

                valid_fit_candidates += 1

                if best_candidate is None or score > best_score:
                    best_candidate = candidate
                    best_score = score

    selected_candidate_dict = asdict(best_candidate) if best_candidate else None
    history_summary = iteration_history.build_summary(
        selected_candidate=selected_candidate_dict
    )

    return {
        "status": "PASS" if best_candidate is not None else "NO_VALID_GEOMETRY_FOUND",
        "best_candidate": selected_candidate_dict,
        "iteration_history": history_summary,
        "candidates_checked": candidates_checked,
        "valid_fit_candidates": valid_fit_candidates,
        "rejected_fit_candidates": rejected_fit_candidates,
        "rejected_velocity_candidates": rejected_velocity,
        "rejected_hydraulic_diameter_candidates": rejected_hydraulic_diameter,
        "rejected_pressure_drop_candidates": rejected_pressure_drop,
        "rejected_cooling_coverage_candidates": rejected_cooling_coverage,
    }


def map_candidate_report_to_engine_results(report, target_reynolds_number=10000.0):
    candidate = report.get("best_candidate")

    mapped_target_reynolds_number = (
        None
        if (
            isinstance(target_reynolds_number, (int, float))
            and not isinstance(target_reynolds_number, bool)
            and not math.isfinite(float(target_reynolds_number))
        )
        else target_reynolds_number
    )

    if not candidate:
        return {
            "recommended_geometry_status": report.get("status", "NO_VALID_GEOMETRY_FOUND"),
            "recommended_target_reynolds_number": mapped_target_reynolds_number,
            "recommended_geometry_candidates_checked": float(report.get("candidates_checked", 0)),
            "recommended_valid_fit_candidates": float(report.get("valid_fit_candidates", 0)),
            "recommended_rejected_fit_candidates": float(report.get("rejected_fit_candidates", 0)),
            "recommended_rejected_velocity_candidates": float(report.get("rejected_velocity_candidates", 0)),
            "recommended_rejected_hydraulic_diameter_candidates": float(report.get("rejected_hydraulic_diameter_candidates", 0)),
            "recommended_rejected_pressure_drop_candidates": float(report.get("rejected_pressure_drop_candidates", 0)),
            "recommended_rejected_cooling_coverage_candidates": float(report.get("rejected_cooling_coverage_candidates", 0)),
        }

    constraint_result = evaluate_regen_geometry_constraints(candidate)
    constraint_flat = flatten_constraint_result(constraint_result)

    history_summary = report.get("iteration_history", {})
    history_flat = flatten_iteration_history_summary(history_summary)

    mapped = {
        "recommended_channel_count": float(candidate["channel_count"]),
        "recommended_number_of_coolant_channels": float(candidate["channel_count"]),
        "recommended_channel_width": candidate["channel_width"],
        "recommended_coolant_channel_width": candidate["channel_width"],
        "recommended_channel_height": candidate["channel_height"],
        "recommended_coolant_channel_height": candidate["channel_height"],
        "recommended_rib_width": candidate["rib_width"],
        "recommended_channel_pitch": candidate["pitch"],
        "recommended_effective_rib_width": candidate["effective_rib_width"],
        "recommended_channel_fit_ratio": candidate["fit_ratio"],
        "recommended_channel_geometry_valid": 1.0,
        "recommended_geometry_valid": 1.0,
        "recommended_single_channel_flow_area": candidate["single_channel_area"],
        "recommended_total_coolant_flow_area": candidate["total_flow_area"],
        "recommended_coolant_wetted_perimeter": candidate["wetted_perimeter"],
        "recommended_coolant_hydraulic_diameter": candidate["hydraulic_diameter"],
        "recommended_hydraulic_diameter": candidate["hydraulic_diameter"],
        "recommended_coolant_velocity": candidate["coolant_velocity"],
        "recommended_coolant_reynolds_number": candidate["reynolds_number"],
        "recommended_reynolds_number": candidate["reynolds_number"],
        "recommended_estimated_pressure_drop": candidate["estimated_pressure_drop"],
        "recommended_circumferential_cooling_coverage": candidate["circumferential_coverage"],
        "recommended_cooling_coverage": candidate["circumferential_coverage"],
        "recommended_total_cooling_wetted_perimeter": candidate["total_wetted_perimeter"],
        "recommended_target_reynolds_number": mapped_target_reynolds_number,
        "recommended_geometry_score": candidate["score"],
        "recommended_geometry_status": candidate["status"],
        "recommended_geometry_candidates_checked": float(report.get("candidates_checked", 0)),
        "recommended_valid_fit_candidates": float(report.get("valid_fit_candidates", 0)),
        "recommended_rejected_fit_candidates": float(report.get("rejected_fit_candidates", 0)),
        "recommended_rejected_velocity_candidates": float(report.get("rejected_velocity_candidates", 0)),
        "recommended_rejected_hydraulic_diameter_candidates": float(report.get("rejected_hydraulic_diameter_candidates", 0)),
        "recommended_rejected_pressure_drop_candidates": float(report.get("rejected_pressure_drop_candidates", 0)),
        "recommended_rejected_cooling_coverage_candidates": float(report.get("rejected_cooling_coverage_candidates", 0)),
    }

    mapped.update(constraint_flat)
    mapped.update(history_flat)
    return mapped
