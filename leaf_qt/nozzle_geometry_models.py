import math


def safe_float(value, default=None):
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def rao_angle_estimate(expansion_ratio, length_fraction=0.8):
    """
    Approximate Rao-style bell nozzle start/end angles.

    This is not a full digitised Rao chart.
    It is a conservative engineering approximation suitable for LEAF's first
    bell-nozzle geometry model.

    Returns:
        theta_start_deg
        theta_exit_deg
    """

    expansion_ratio = safe_float(expansion_ratio, 10.0)
    length_fraction = safe_float(length_fraction, 0.8)

    if expansion_ratio is None or expansion_ratio <= 1.0:
        expansion_ratio = 10.0

    if length_fraction is None:
        length_fraction = 0.8

    length_fraction = max(0.6, min(1.0, length_fraction))

    # Conservative Rao-like estimates.
    # Higher expansion nozzles usually have lower exit angle.
    if expansion_ratio < 10.0:
        theta_start = 30.0
        theta_exit = 12.0
    elif expansion_ratio < 25.0:
        theta_start = 28.0
        theta_exit = 9.0
    elif expansion_ratio < 50.0:
        theta_start = 26.0
        theta_exit = 7.0
    elif expansion_ratio < 100.0:
        theta_start = 24.0
        theta_exit = 5.5
    else:
        theta_start = 22.0
        theta_exit = 4.5

    # Shorter bells need slightly more aggressive turning.
    if length_fraction < 0.8:
        theta_start += 2.0
        theta_exit += 1.0
    elif length_fraction > 0.9:
        theta_start -= 1.0
        theta_exit -= 0.5

    return theta_start, theta_exit


def conical_nozzle_length(throat_radius, exit_radius, half_angle_deg=15.0):
    throat_radius = safe_float(throat_radius)
    exit_radius = safe_float(exit_radius)

    if throat_radius is None or exit_radius is None:
        return None

    if exit_radius <= throat_radius:
        return None

    angle = math.radians(half_angle_deg)

    if abs(math.tan(angle)) < 1.0e-12:
        return None

    return (exit_radius - throat_radius) / math.tan(angle)


def hermite_radius(x, length, r0, r1, slope0, slope1):
    """
    Cubic Hermite interpolation for bell-nozzle radius.

    Enforces:
    - throat radius
    - exit radius
    - throat/start wall angle
    - exit wall angle
    """

    if length <= 0:
        return r0

    t = max(0.0, min(1.0, x / length))

    h00 = 2.0 * t**3 - 3.0 * t**2 + 1.0
    h10 = t**3 - 2.0 * t**2 + t
    h01 = -2.0 * t**3 + 3.0 * t**2
    h11 = t**3 - t**2

    return (
        h00 * r0
        + h10 * length * slope0
        + h01 * r1
        + h11 * length * slope1
    )


def build_rao_bell_nozzle_profile(
    throat_radius,
    exit_radius,
    nozzle_length=None,
    expansion_ratio=None,
    length_fraction=0.8,
    station_count=80,
):
    """
    Builds a Rao-style bell nozzle approximation.

    This is intended to replace simple linear/conical radius interpolation
    inside LEAF.

    Returns a dict containing:
    - profile stations
    - geometry summary
    - model status
    """

    throat_radius = safe_float(throat_radius)
    exit_radius = safe_float(exit_radius)
    nozzle_length = safe_float(nozzle_length)
    expansion_ratio = safe_float(expansion_ratio)
    length_fraction = safe_float(length_fraction, 0.8)

    station_count = int(station_count or 80)
    station_count = max(8, min(400, station_count))

    if throat_radius is None or throat_radius <= 0:
        return {
            "status": "RAO_GEOMETRY_BLOCKED",
            "reason": "Invalid throat radius.",
            "profile": [],
        }

    if exit_radius is None or exit_radius <= throat_radius:
        return {
            "status": "RAO_GEOMETRY_BLOCKED",
            "reason": "Invalid exit radius.",
            "profile": [],
        }

    if expansion_ratio is None:
        expansion_ratio = (exit_radius / throat_radius) ** 2.0

    if nozzle_length is None or nozzle_length <= 0:
        full_conical_length = conical_nozzle_length(
            throat_radius,
            exit_radius,
            half_angle_deg=15.0,
        )

        if full_conical_length is None:
            return {
                "status": "RAO_GEOMETRY_BLOCKED",
                "reason": "Could not calculate reference conical length.",
                "profile": [],
            }

        nozzle_length = full_conical_length * length_fraction

    theta_start_deg, theta_exit_deg = rao_angle_estimate(
        expansion_ratio,
        length_fraction,
    )

    slope_start = math.tan(math.radians(theta_start_deg))
    slope_exit = math.tan(math.radians(theta_exit_deg))

    profile = []

    previous_radius = None
    monotonic = True

    for index in range(station_count):
        fraction = index / (station_count - 1)
        x = fraction * nozzle_length

        radius = hermite_radius(
            x=x,
            length=nozzle_length,
            r0=throat_radius,
            r1=exit_radius,
            slope0=slope_start,
            slope1=slope_exit,
        )

        radius = max(throat_radius, radius)
        area = math.pi * radius**2.0
        local_expansion_ratio = area / (math.pi * throat_radius**2.0)

        if previous_radius is not None and radius < previous_radius:
            monotonic = False

        previous_radius = radius

        profile.append({
            "station_index": index,
            "x": x,
            "fraction": fraction,
            "radius": radius,
            "area": area,
            "local_expansion_ratio": local_expansion_ratio,
            "nozzle_model": "RAO_BELL_APPROXIMATION",
        })

    status = "RAO_GEOMETRY_READY" if monotonic else "RAO_GEOMETRY_WARN_NON_MONOTONIC"

    return {
        "status": status,
        "reason": "Rao-style bell approximation generated.",
        "profile": profile,
        "summary": {
            "nozzle_model": "RAO_BELL_APPROXIMATION",
            "throat_radius": throat_radius,
            "exit_radius": exit_radius,
            "nozzle_length": nozzle_length,
            "expansion_ratio": expansion_ratio,
            "length_fraction": length_fraction,
            "theta_start_deg": theta_start_deg,
            "theta_exit_deg": theta_exit_deg,
            "station_count": station_count,
            "monotonic_radius": monotonic,
        },
    }