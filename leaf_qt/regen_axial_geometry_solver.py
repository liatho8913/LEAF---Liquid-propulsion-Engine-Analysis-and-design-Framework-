from dataclasses import dataclass, asdict
import math

try:
    from leaf_qt.regen_geometry_solver import solve_regen_geometry
except Exception:
    from regen_geometry_solver import solve_regen_geometry


@dataclass
class RegenAxialStation:
    station_id: str
    station_name: str
    axial_position: float
    local_radius: float
    local_wall_radius: float | None = None
    local_heat_flux: float | None = None
    coolant_mass_flow_rate: float | None = None
    coolant_density: float | None = None
    coolant_dynamic_viscosity: float | None = None
    target_reynolds_number: float = 10000.0
    minimum_rib_width: float = 0.0005
    minimum_channel_width: float = 0.0005
    maximum_channel_height: float | None = None
    channel_aspect_ratio: float = 2.0
    minimum_channel_count: int = 4
    maximum_channel_count: int = 300
    maximum_coolant_velocity: float | None = None
    minimum_hydraulic_diameter: float | None = None
    pressure_drop_limit: float | None = None
    axial_segment_length: float | None = None
    minimum_cooling_coverage: float | None = None


def _safe_float(value, default=None):
    try:
        if value is None:
            return default
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return default
        return value
    except Exception:
        return default


def _safe_int(value, default):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _normalise_station_spec(spec, index, defaults):
    if spec is None:
        spec = {}

    station_id = str(spec.get("station_id", f"station_{index:03d}"))
    station_name = str(spec.get("station_name", spec.get("name", station_id)))

    axial_position = _safe_float(
        spec.get("axial_position", spec.get("x", spec.get("position"))),
        default=None,
    )
    local_radius = _safe_float(
        spec.get("local_radius", spec.get("radius", spec.get("channel_mid_radius"))),
        default=None,
    )

    if axial_position is None:
        axial_position = float(index)

    return RegenAxialStation(
        station_id=station_id,
        station_name=station_name,
        axial_position=axial_position,
        local_radius=local_radius,
        local_wall_radius=_safe_float(spec.get("local_wall_radius"), None),
        local_heat_flux=_safe_float(spec.get("local_heat_flux"), None),
        coolant_mass_flow_rate=_safe_float(
            spec.get("coolant_mass_flow_rate"), defaults.get("coolant_mass_flow_rate")
        ),
        coolant_density=_safe_float(
            spec.get("coolant_density"), defaults.get("coolant_density")
        ),
        coolant_dynamic_viscosity=_safe_float(
            spec.get("coolant_dynamic_viscosity"), defaults.get("coolant_dynamic_viscosity")
        ),
        target_reynolds_number=_safe_float(
            spec.get("target_reynolds_number"), defaults.get("target_reynolds_number", 10000.0)
        ),
        minimum_rib_width=_safe_float(
            spec.get("minimum_rib_width"), defaults.get("minimum_rib_width", 0.0005)
        ),
        minimum_channel_width=_safe_float(
            spec.get("minimum_channel_width"), defaults.get("minimum_channel_width", 0.0005)
        ),
        maximum_channel_height=_safe_float(
            spec.get("maximum_channel_height"), defaults.get("maximum_channel_height")
        ),
        channel_aspect_ratio=_safe_float(
            spec.get("channel_aspect_ratio"), defaults.get("channel_aspect_ratio", 2.0)
        ),
        minimum_channel_count=_safe_int(
            spec.get("minimum_channel_count"), defaults.get("minimum_channel_count", 4)
        ),
        maximum_channel_count=_safe_int(
            spec.get("maximum_channel_count"), defaults.get("maximum_channel_count", 300)
        ),
        maximum_coolant_velocity=_safe_float(
            spec.get("maximum_coolant_velocity"), defaults.get("maximum_coolant_velocity")
        ),
        minimum_hydraulic_diameter=_safe_float(
            spec.get("minimum_hydraulic_diameter"), defaults.get("minimum_hydraulic_diameter")
        ),
        pressure_drop_limit=_safe_float(
            spec.get("pressure_drop_limit"), defaults.get("pressure_drop_limit")
        ),
        axial_segment_length=_safe_float(
            spec.get("axial_segment_length"), defaults.get("axial_segment_length")
        ),
        minimum_cooling_coverage=_safe_float(
            spec.get("minimum_cooling_coverage"), defaults.get("minimum_cooling_coverage")
        ),
    )


def _build_default_station_specs(chamber_radius, throat_radius, exit_radius, engine_length):
    chamber_radius = _safe_float(chamber_radius, None)
    throat_radius = _safe_float(throat_radius, None)
    exit_radius = _safe_float(exit_radius, None)
    engine_length = _safe_float(engine_length, None)

    if chamber_radius is None or throat_radius is None or exit_radius is None:
        return []

    if engine_length is None or engine_length <= 0:
        engine_length = 1.0

    return [
        {"station_id": "injector_end", "station_name": "Injector End", "axial_position": 0.00 * engine_length, "local_radius": chamber_radius},
        {"station_id": "combustion_chamber", "station_name": "Combustion Chamber", "axial_position": 0.20 * engine_length, "local_radius": chamber_radius},
        {"station_id": "contraction", "station_name": "Contraction", "axial_position": 0.40 * engine_length, "local_radius": 0.5 * (chamber_radius + throat_radius)},
        {"station_id": "throat", "station_name": "Throat", "axial_position": 0.50 * engine_length, "local_radius": throat_radius},
        {"station_id": "early_nozzle", "station_name": "Early Nozzle", "axial_position": 0.65 * engine_length, "local_radius": 0.5 * (throat_radius + exit_radius)},
        {"station_id": "mid_nozzle", "station_name": "Mid Nozzle", "axial_position": 0.80 * engine_length, "local_radius": 0.75 * exit_radius + 0.25 * throat_radius},
        {"station_id": "exit_nozzle", "station_name": "Exit Nozzle", "axial_position": 1.00 * engine_length, "local_radius": exit_radius},
    ]


def build_regen_axial_station_profile(station_specs=None, **defaults):
    if station_specs is None:
        station_specs = _build_default_station_specs(
            chamber_radius=defaults.get("chamber_radius"),
            throat_radius=defaults.get("throat_radius"),
            exit_radius=defaults.get("exit_radius"),
            engine_length=defaults.get("engine_length"),
        )

    stations = [
        _normalise_station_spec(spec, index, defaults)
        for index, spec in enumerate(station_specs or [])
    ]

    stations.sort(key=lambda station: station.axial_position)

    station_dicts = [asdict(station) for station in stations]

    missing_radius_count = sum(
        1 for station in stations if station.local_radius is None or station.local_radius <= 0
    )

    profile_pass = len(stations) > 0 and missing_radius_count == 0

    return {
        "axial_station_profile_status": "PASS_REGEN_AXIAL_STATION_PROFILE" if profile_pass else "FAIL_REGEN_AXIAL_STATION_PROFILE",
        "axial_station_profile_pass": profile_pass,
        "station_count": len(stations),
        "missing_radius_count": missing_radius_count,
        "stations": station_dicts,
    }


def _solve_station_geometry(station):
    return solve_regen_geometry(
        channel_mid_radius=station.get("local_radius"),
        coolant_mass_flow_rate=station.get("coolant_mass_flow_rate"),
        coolant_density=station.get("coolant_density"),
        coolant_dynamic_viscosity=station.get("coolant_dynamic_viscosity"),
        target_reynolds_number=station.get("target_reynolds_number", 10000.0),
        minimum_rib_width=station.get("minimum_rib_width", 0.0005),
        minimum_channel_width=station.get("minimum_channel_width", 0.0005),
        maximum_channel_height=station.get("maximum_channel_height"),
        channel_aspect_ratio=station.get("channel_aspect_ratio", 2.0),
        minimum_channel_count=station.get("minimum_channel_count", 4),
        maximum_channel_count=station.get("maximum_channel_count", 300),
        maximum_coolant_velocity=station.get("maximum_coolant_velocity"),
        minimum_hydraulic_diameter=station.get("minimum_hydraulic_diameter"),
        pressure_drop_limit=station.get("pressure_drop_limit"),
        nozzle_length=station.get("axial_segment_length"),
        minimum_cooling_coverage=station.get("minimum_cooling_coverage"),
    )


def solve_regen_axial_geometry(station_specs=None, **defaults):
    profile = build_regen_axial_station_profile(station_specs=station_specs, **defaults)
    station_results = []

    for station in profile.get("stations", []):
        station_result = _solve_station_geometry(station)
        best_candidate = station_result.get("best_candidate")
        mapped_results = station_result.get("mapped_results", {})

        station_results.append(
            {
                "station_id": station.get("station_id"),
                "station_name": station.get("station_name"),
                "axial_position": station.get("axial_position"),
                "local_radius": station.get("local_radius"),
                "station_solver_status": station_result.get("solver_status"),
                "station_solver_pass": station_result.get("solver_pass"),
                "best_candidate": best_candidate,
                "mapped_results": mapped_results,
                "dominant_failure": mapped_results.get("recommended_regen_geometry_dominant_failure"),
            }
        )

    pass_count = sum(1 for result in station_results if result.get("station_solver_pass"))
    fail_count = len(station_results) - pass_count

    solver_pass = profile.get("axial_station_profile_pass") and len(station_results) > 0 and fail_count == 0

    return {
        "axial_geometry_solver_status": "PASS_REGEN_AXIAL_GEOMETRY_SOLVER" if solver_pass else "FAIL_REGEN_AXIAL_GEOMETRY_SOLVER",
        "axial_geometry_solver_pass": solver_pass,
        "axial_station_profile": profile,
        "station_results": station_results,
        "station_count": len(station_results),
        "station_pass_count": pass_count,
        "station_fail_count": fail_count,
    }


def flatten_regen_axial_geometry_result(result, prefix="recommended"):
    profile = result.get("axial_station_profile", {})
    station_results = result.get("station_results", [])

    flat = {
        f"{prefix}_regen_axial_geometry_solver_status": result.get("axial_geometry_solver_status"),
        f"{prefix}_regen_axial_geometry_solver_pass": 1.0 if result.get("axial_geometry_solver_pass") else 0.0,
        f"{prefix}_regen_axial_station_profile_status": profile.get("axial_station_profile_status"),
        f"{prefix}_regen_axial_station_profile_pass": 1.0 if profile.get("axial_station_profile_pass") else 0.0,
        f"{prefix}_regen_axial_station_count": float(result.get("station_count", 0)),
        f"{prefix}_regen_axial_station_pass_count": float(result.get("station_pass_count", 0)),
        f"{prefix}_regen_axial_station_fail_count": float(result.get("station_fail_count", 0)),
        f"{prefix}_regen_axial_missing_radius_count": float(profile.get("missing_radius_count", 0)),
    }

    for index, station_result in enumerate(station_results):
        station_prefix = f"{prefix}_regen_axial_station_{index + 1}"
        candidate = station_result.get("best_candidate") or {}

        flat.update(
            {
                f"{station_prefix}_id": station_result.get("station_id"),
                f"{station_prefix}_name": station_result.get("station_name"),
                f"{station_prefix}_axial_position": station_result.get("axial_position"),
                f"{station_prefix}_local_radius": station_result.get("local_radius"),
                f"{station_prefix}_solver_status": station_result.get("station_solver_status"),
                f"{station_prefix}_solver_pass": 1.0 if station_result.get("station_solver_pass") else 0.0,
                f"{station_prefix}_channel_count": float(candidate.get("channel_count", 0) or 0),
                f"{station_prefix}_channel_width": candidate.get("channel_width"),
                f"{station_prefix}_channel_height": candidate.get("channel_height"),
                f"{station_prefix}_rib_width": candidate.get("rib_width"),
                f"{station_prefix}_hydraulic_diameter": candidate.get("hydraulic_diameter"),
                f"{station_prefix}_coolant_velocity": candidate.get("coolant_velocity"),
                f"{station_prefix}_reynolds_number": candidate.get("reynolds_number"),
                f"{station_prefix}_estimated_pressure_drop": candidate.get("estimated_pressure_drop"),
                f"{station_prefix}_coverage": candidate.get("circumferential_coverage"),
                f"{station_prefix}_dominant_failure": station_result.get("dominant_failure"),
            }
        )

    return flat


def solve_regen_axial_geometry_to_engine_results(**kwargs):
    result = solve_regen_axial_geometry(**kwargs)
    return flatten_regen_axial_geometry_result(result)