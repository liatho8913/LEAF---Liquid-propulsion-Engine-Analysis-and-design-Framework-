class CalculationAuditEngine:
    def __init__(self):
        pass

    def safe_float(self, value):
        try:
            if value is None:
                return None
            return float(value)
        except Exception:
            return None

    def status_row(self, section, variable, status, reason, recommendation=""):
        return {
            "section": section,
            "variable": variable,
            "status": status,
            "reason": reason,
            "recommendation": recommendation,
        }

    def audit(self, solved):
        rows = []

        rows.extend(self.audit_core_engine(solved))
        rows.extend(self.audit_cea(solved))
        rows.extend(self.audit_geometry(solved))
        rows.extend(self.audit_performance(solved))
        rows.extend(self.audit_regen(solved))

        return rows

    def audit_core_engine(self, solved):
        rows = []

        for key in [
            "mass_flow_rate",
            "mixture_ratio",
            "chamber_pressure",
            "chamber_temperature",
            "Gamma",
            "R",
        ]:
            value = self.safe_float(solved.get(key))

            if value is None:
                rows.append(self.status_row("Core", key, "MISSING", "No value was returned."))
            elif value <= 0 and key != "Gamma":
                rows.append(self.status_row("Core", key, "FAIL", "Value is zero or negative."))
            elif key == "Gamma" and value <= 1.0:
                rows.append(self.status_row("Core", key, "FAIL", "Gamma must be greater than 1."))
            else:
                rows.append(self.status_row("Core", key, "PASS", "Value is present and physically positive."))

        return rows

    def audit_cea(self, solved):
        rows = []

        authoritative_mode = solved.get("cea_authoritative_mode")
        authoritative_used = solved.get("cea_authoritative_used")

        if authoritative_mode is True and authoritative_used is not True:
            rows.append(self.status_row(
                "CEA",
                "cea_authoritative_used",
                "WARNING",
                "CEA authoritative mode is enabled, but CEA values were not used.",
                "Check CEA execution, selected propellants, and fallback logic."
            ))
        else:
            rows.append(self.status_row(
                "CEA",
                "cea_authoritative_used",
                "PASS",
                "CEA status is acceptable."
            ))

        for key in [
            "cea_chamber_temperature",
            "cea_selected_gamma",
            "cea_selected_molecular_weight",
            "cea_selected_cp",
            "cea_selected_viscosity",
            "cea_selected_conductivity",
        ]:
            value = self.safe_float(solved.get(key))

            if value is None:
                rows.append(self.status_row("CEA", key, "MISSING", "CEA value is missing."))
            elif value <= 0:
                rows.append(self.status_row("CEA", key, "FAIL", "CEA value is zero or negative."))
            else:
                rows.append(self.status_row("CEA", key, "PASS", "CEA value is present."))

        return rows

    def audit_geometry(self, solved):
        rows = []

        throat_radius = self.safe_float(solved.get("throat_radius"))
        exit_radius = self.safe_float(solved.get("exit_radius"))
        throat_area = self.safe_float(solved.get("throat_area"))
        exit_area = self.safe_float(solved.get("exit_area"))
        expansion_ratio = self.safe_float(solved.get("expansion_ratio"))

        checks = [
            ("throat_radius", throat_radius),
            ("exit_radius", exit_radius),
            ("throat_area", throat_area),
            ("exit_area", exit_area),
            ("expansion_ratio", expansion_ratio),
        ]

        for key, value in checks:
            if value is None:
                rows.append(self.status_row("Geometry", key, "MISSING", "Geometry value is missing."))
            elif value <= 0:
                rows.append(self.status_row("Geometry", key, "FAIL", "Geometry value is zero or negative."))
            else:
                rows.append(self.status_row("Geometry", key, "PASS", "Geometry value is positive."))

        if throat_radius is not None and exit_radius is not None:
            if exit_radius <= throat_radius:
                rows.append(self.status_row(
                    "Geometry",
                    "exit_radius",
                    "FAIL",
                    "Exit radius is not larger than throat radius.",
                    "Check expansion ratio and exit area."
                ))

        if throat_area is not None and exit_area is not None and expansion_ratio is not None:
            expected = exit_area / throat_area if throat_area > 0 else None

            if expected is not None:
                error = abs(expected - expansion_ratio)

                if error > 1e-3:
                    rows.append(self.status_row(
                        "Geometry",
                        "expansion_ratio",
                        "WARNING",
                        f"Expansion ratio does not exactly match Ae/At. Difference: {error:.6g}",
                        "Check geometry calculation order."
                    ))

        return rows

    def audit_performance(self, solved):
        rows = []

        mdot = self.safe_float(solved.get("mass_flow_rate"))
        thrust = self.safe_float(solved.get("thrust"))
        isp = self.safe_float(solved.get("specific_impulse"))
        g0 = 9.80665

        for key in [
            "thrust",
            "specific_impulse",
            "exhaust_velocity",
            "characteristic_velocity",
            "thrust_coefficient",
            "corrected_thrust",
            "volumetric_corrected_thrust",
        ]:
            value = self.safe_float(solved.get(key))

            if value is None:
                rows.append(self.status_row("Performance", key, "MISSING", "Performance value is missing."))
            elif value <= 0:
                rows.append(self.status_row("Performance", key, "FAIL", "Performance value is zero or negative."))
            else:
                rows.append(self.status_row("Performance", key, "PASS", "Performance value is positive."))

        if thrust is not None and isp is not None and mdot is not None and mdot > 0:
            expected_isp = thrust / (mdot * g0)
            error_percent = abs(expected_isp - isp) / max(abs(isp), 1e-9) * 100.0

            if error_percent > 0.5:
                rows.append(self.status_row(
                    "Performance",
                    "specific_impulse",
                    "WARNING",
                    f"Isp does not match F/(ṁg0). Error: {error_percent:.3g}%.",
                    "Check thrust, mass flow, or g0 convention."
                ))

        return rows

    def audit_regen(self, solved):
        rows = []

        for key in [
            "regen_overall_status",
            "regen_geometry_status",
            "regen_thermal_status",
            "regen_coolant_status",
            "regen_material_status",
        ]:
            value = solved.get(key)

            if value is None:
                rows.append(self.status_row("Regen", key, "MISSING", "Regen validation status is missing."))
            elif str(value).upper() == "PASS":
                rows.append(self.status_row("Regen", key, "PASS", "Regen check passed."))
            else:
                rows.append(self.status_row("Regen", key, "FAIL", f"Regen check returned {value}."))

        hot_wall = self.safe_float(solved.get("hot_gas_side_wall_temperature"))
        material_max = self.safe_float(solved.get("material_max_wall_temperature"))

        if hot_wall is not None and material_max is not None:
            if hot_wall > material_max:
                rows.append(self.status_row(
                    "Regen",
                    "hot_gas_side_wall_temperature",
                    "FAIL",
                    f"Hot wall temperature {hot_wall:.6g} K exceeds material limit {material_max:.6g} K.",
                    "Improve coolant flow, channel geometry, wall material, or reduce heat flux."
                ))

        channel_valid = self.safe_float(solved.get("channel_geometry_valid"))

        if channel_valid == 0:
            rows.append(self.status_row(
                "Regen",
                "channel_geometry_valid",
                "FAIL",
                "Channel geometry does not physically fit.",
                "Reduce channel count/width/rib width, or increase local radius."
            ))

        reynolds = self.safe_float(solved.get("coolant_reynolds_number"))

        if reynolds is not None:
            if reynolds < 2300:
                rows.append(self.status_row(
                    "Regen",
                    "coolant_reynolds_number",
                    "FAIL",
                    f"Coolant Reynolds number {reynolds:.6g} is laminar.",
                    "Increase coolant velocity, reduce hydraulic diameter, or adjust channel count."
                ))
            elif reynolds < 10000:
                rows.append(self.status_row(
                    "Regen",
                    "coolant_reynolds_number",
                    "WARNING",
                    f"Coolant Reynolds number {reynolds:.6g} is transitional.",
                    "Turbulent cooling is usually preferred for regen channels."
                ))

        return rows