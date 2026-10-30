class DiagnosticsEngine:
    def __init__(self):
        self.engine_scale = "unknown"

    def safe_float(self, value):
        try:
            if value is None:
                return None
            return float(value)
        except Exception:
            return None

    def add_issue(self, issues, severity, title, detail, suggestion=""):
        issues.append({
            "severity": severity,
            "title": title,
            "detail": detail,
            "suggestion": suggestion,
        })

    def classify_engine_scale(self, solved):
        thrust = self.safe_float(solved.get("thrust"))
        mass_flow = self.safe_float(solved.get("mass_flow_rate"))
        throat_area = self.safe_float(solved.get("throat_area"))

        if thrust is not None:
            if thrust < 1_000:
                return "small"
            if thrust < 50_000:
                return "laboratory"
            if thrust < 500_000:
                return "medium"
            if thrust < 2_500_000:
                return "large"
            return "booster"

        if mass_flow is not None:
            if mass_flow < 0.5:
                return "small"
            if mass_flow < 20:
                return "laboratory"
            if mass_flow < 200:
                return "medium"
            if mass_flow < 1000:
                return "large"
            return "booster"

        if throat_area is not None:
            if throat_area < 1e-4:
                return "small"
            if throat_area < 5e-3:
                return "laboratory"
            if throat_area < 5e-2:
                return "medium"
            if throat_area < 0.2:
                return "large"
            return "booster"

        return "unknown"

    def get_scale_limits(self):
        limits = {
            "small": {
                "coolant_pressure_drop_warning": 1.0e5,
                "heat_flux_warning": 15.0e6,
                "coolant_velocity_warning": 30.0,
            },
            "laboratory": {
                "coolant_pressure_drop_warning": 5.0e5,
                "heat_flux_warning": 30.0e6,
                "coolant_velocity_warning": 60.0,
            },
            "medium": {
                "coolant_pressure_drop_warning": 2.0e6,
                "heat_flux_warning": 60.0e6,
                "coolant_velocity_warning": 100.0,
            },
            "large": {
                "coolant_pressure_drop_warning": 5.0e6,
                "heat_flux_warning": 100.0e6,
                "coolant_velocity_warning": 150.0,
            },
            "booster": {
                "coolant_pressure_drop_warning": 1.5e7,
                "heat_flux_warning": 150.0e6,
                "coolant_velocity_warning": 200.0,
            },
            "unknown": {
                "coolant_pressure_drop_warning": 1.0e6,
                "heat_flux_warning": 50.0e6,
                "coolant_velocity_warning": 100.0,
            },
        }

        return limits.get(self.engine_scale, limits["unknown"])

    def sort_issues(self, issues):
        order = {
            "critical": 0,
            "warning": 1,
            "info": 2,
        }

        return sorted(
            issues,
            key=lambda issue: order.get(issue.get("severity", "info"), 99)
        )

    def count_by_severity(self, issues):
        counts = {
            "critical": 0,
            "warning": 0,
            "info": 0,
        }

        for issue in issues:
            severity = issue.get("severity", "info")
            counts[severity] = counts.get(severity, 0) + 1

        return counts

    def evaluate(self, solved):
        issues = []

        self.engine_scale = self.classify_engine_scale(solved)
        regen_validation = self.build_regen_validation(solved)

        if isinstance(solved, dict):
            solved.update(regen_validation)
        self.add_issue(
            issues,
            "info",
            "Engine scale classification",
            f"Diagnostics classified this design as: {self.engine_scale}.",
            "Scale is estimated from thrust, mass flow rate, or throat area."
        )

        self.check_cea_status(solved, issues)
        self.check_propellant_volume_logic(solved, issues)
        self.check_performance(solved, issues)
        self.check_heat_flux(solved, issues)
        self.check_wall_temperatures(solved, issues)
        self.check_wall_thickness(solved, issues)
        self.check_channel_geometry(solved, issues)
        self.check_coolant_flow(solved, issues)
        self.check_regen_validation_summary(solved, issues)
        issues = self.sort_issues(issues)

        return {
            "engine_scale": self.engine_scale,
            "counts": self.count_by_severity(issues),
            "issues": issues,
        }

    def check_cea_status(self, solved, issues):
        cea_authoritative_mode = solved.get("cea_authoritative_mode")
        cea_authoritative_used = solved.get("cea_authoritative_used")

        gamma = self.safe_float(solved.get("Gamma"))
        chamber_temperature = self.safe_float(solved.get("chamber_temperature"))

        if cea_authoritative_mode and not cea_authoritative_used:
            self.add_issue(
                issues,
                "warning",
                "CEA authoritative mode not used",
                "CEA authoritative mode appears enabled, but CEA was not used.",
                "Check whether CEA ran successfully or whether LEAF used fallback values."
            )

        if gamma is not None and not 1.05 <= gamma <= 1.45:
            self.add_issue(
                issues,
                "warning",
                "Gamma outside expected range",
                f"Gamma is {gamma:.4g}.",
                "Check gas model, CEA output, or fallback thermodynamic constants."
            )

        if chamber_temperature is not None and not 1500 <= chamber_temperature <= 4500:
            self.add_issue(
                issues,
                "warning",
                "Chamber temperature outside expected range",
                f"Chamber temperature is {chamber_temperature:.4g} K.",
                "Check propellant selection, CEA output, or manual chamber temperature."
            )

    def check_propellant_volume_logic(self, solved, issues):
        oxidizer = str(solved.get("oxidizer") or solved.get("selected_oxidizer") or "")
        fuel_density = self.safe_float(solved.get("fuel_density"))
        oxidizer_density = self.safe_float(solved.get("oxidizer_density"))
        volume_flow = self.safe_float(solved.get("total_propellant_volume_flow_rate"))
        mass_flow = self.safe_float(solved.get("mass_flow_rate"))

        if oxidizer in {"O2", "GOX"} or "GOX" in oxidizer.upper():
            self.add_issue(
                issues,
                "info",
                "Gaseous oxygen selected",
                "The selected oxidizer appears to be gaseous oxygen. Volume-flow metrics will be much larger than LOX cases.",
                "Use O2(L) / LOX for liquid-storage volume comparisons."
            )

        if oxidizer in {"O2(L)", "LOX"}:
            self.add_issue(
                issues,
                "info",
                "Liquid oxygen selected",
                "The selected oxidizer appears to be liquid oxygen. Volume-flow metrics use liquid storage density.",
                ""
            )

        if fuel_density is not None and fuel_density <= 5:
            self.add_issue(
                issues,
                "info",
                "Low fuel density",
                f"Fuel density is {fuel_density:.4g} kg/m³.",
                "This suggests gaseous fuel storage and weak volumetric performance."
            )

        if oxidizer_density is not None and oxidizer_density <= 5:
            self.add_issue(
                issues,
                "info",
                "Low oxidizer density",
                f"Oxidizer density is {oxidizer_density:.4g} kg/m³.",
                "This suggests gaseous oxidizer storage and high volume flow."
            )

        if volume_flow is not None and mass_flow is not None and mass_flow > 0 and volume_flow > 0:
            implied_bulk_density = mass_flow / volume_flow

            if implied_bulk_density < 10:
                self.add_issue(
                    issues,
                    "info",
                    "Very low bulk propellant density",
                    f"Implied bulk propellant density is {implied_bulk_density:.4g} kg/m³.",
                    "Expected for gaseous propellant cases; unusual for compact liquid systems."
                )

    def check_performance(self, solved, issues):
        thrust = self.safe_float(solved.get("thrust"))
        corrected_thrust = self.safe_float(solved.get("corrected_thrust"))
        isp = self.safe_float(solved.get("specific_impulse"))
        cf = self.safe_float(solved.get("thrust_coefficient"))

        if thrust is not None and thrust <= 0:
            self.add_issue(
                issues,
                "critical",
                "Non-positive thrust",
                f"Thrust is {thrust:.4g} N.",
                "Check chamber pressure, throat area, nozzle expansion, and pressure thrust."
            )

        if corrected_thrust is not None and corrected_thrust <= 0:
            self.add_issue(
                issues,
                "critical",
                "Non-positive corrected thrust",
                f"Corrected thrust is {corrected_thrust:.4g} N.",
                "Check correction factors and performance model."
            )

        if isp is not None and not 50 <= isp <= 550:
            self.add_issue(
                issues,
                "warning",
                "Specific impulse outside expected range",
                f"Specific impulse is {isp:.4g} s.",
                "Check propellant selection, nozzle expansion, chamber pressure, or units."
            )

        if cf is not None and not 0.5 <= cf <= 2.5:
            self.add_issue(
                issues,
                "warning",
                "Thrust coefficient outside expected range",
                f"Thrust coefficient is {cf:.4g}.",
                "Check nozzle expansion and pressure-thrust calculation."
            )

    def build_regen_validation(self, solved):
        requested_width = self.safe_float(solved.get("coolant_channel_width"))
        requested_rib = self.safe_float(solved.get("rib_width"))
        requested_pitch = self.safe_float(solved.get("channel_pitch"))

        available_pitch = self.safe_float(solved.get("circumferential_channel_pitch"))
        effective_rib = self.safe_float(solved.get("effective_rib_width"))

        hot_wall = self.safe_float(solved.get("hot_gas_side_wall_temperature"))
        material_max = self.safe_float(solved.get("material_max_wall_temperature"))
        reynolds = self.safe_float(solved.get("coolant_reynolds_number"))
        pressure_drop = self.safe_float(solved.get("coolant_pressure_drop"))

        geometry_ok = True
        thermal_ok = True
        coolant_ok = True
        material_ok = True

        reasons = []

        if requested_pitch is None and requested_width is not None and requested_rib is not None:
            requested_pitch = requested_width + requested_rib

        if requested_pitch is not None and available_pitch is not None:
            if requested_pitch > available_pitch:
                geometry_ok = False
                reasons.append(
                    f"Requested channel pitch {requested_pitch:.6g} m exceeds available circumferential pitch {available_pitch:.6g} m."
                )

        if requested_rib is not None and effective_rib is not None:
            if effective_rib < requested_rib:
                geometry_ok = False
                reasons.append(
                    f"Effective rib width {effective_rib:.6g} m is below requested rib width {requested_rib:.6g} m."
                )

        if effective_rib is not None and effective_rib <= 0:
            geometry_ok = False
            reasons.append("Effective rib width is zero or negative, meaning channels overlap.")

        if hot_wall is not None and material_max is not None:
            if hot_wall > material_max:
                thermal_ok = False
                material_ok = False
                reasons.append(
                    f"Hot-gas-side wall temperature {hot_wall:.6g} K exceeds material limit {material_max:.6g} K."
                )

        if reynolds is not None and reynolds < 2300:
            coolant_ok = False
            reasons.append(
                f"Coolant Reynolds number {reynolds:.6g} is laminar."
            )

        if pressure_drop is not None and pressure_drop < 0:
            coolant_ok = False
            reasons.append(
                f"Coolant pressure drop {pressure_drop:.6g} Pa is nonphysical."
            )

        overall_ok = geometry_ok and thermal_ok and coolant_ok and material_ok
        # Override legacy solver validity so downstream UI does not display
        # physically invalid geometry as valid.
        if isinstance(solved, dict):
            solved["channel_geometry_valid"] = 1.0 if geometry_ok else 0.0

        return {
            "regen_geometry_status": "PASS" if geometry_ok else "FAIL",
            "regen_thermal_status": "PASS" if thermal_ok else "FAIL",
            "regen_coolant_status": "PASS" if coolant_ok else "FAIL",
            "regen_material_status": "PASS" if material_ok else "FAIL",
            "regen_overall_status": "PASS" if overall_ok else "FAIL",

            "geometry_fit_pass": 1.0 if geometry_ok else 0.0,
            "wall_temperature_pass": 1.0 if thermal_ok else 0.0,
            "coolant_reynolds_pass": 1.0 if coolant_ok else 0.0,
            "material_temperature_pass": 1.0 if material_ok else 0.0,
            "regen_design_pass": 1.0 if overall_ok else 0.0,

            "regen_validation_reasons": reasons,
        }

    def check_regen_validation_summary(self, solved, issues):
        overall = solved.get("regen_overall_status")
        reasons = solved.get("regen_validation_reasons", [])

        if overall == "FAIL":
            self.add_issue(
                issues,
                "critical",
                "Regenerative cooling validation failed",
                "The regen system should not be treated as a validated design.",
                "Review geometry fit, coolant Reynolds number, wall temperature, and material margin."
            )

        for reason in reasons:
            self.add_issue(
                issues,
                "warning",
                "Regen validation reason",
                reason,
                "Correct this before treating the regen geometry as valid."
            )

    def check_heat_flux(self, solved, issues):
        limits = self.get_scale_limits()

        hot_gas_heat_flux = self.safe_float(solved.get("hot_gas_heat_flux"))
        regen_heat_flux = self.safe_float(solved.get("regen_heat_flux"))

        limit = limits["heat_flux_warning"]

        if hot_gas_heat_flux is not None and hot_gas_heat_flux > limit:
            self.add_issue(
                issues,
                "warning",
                "High hot-gas heat flux",
                f"Hot-gas heat flux is {hot_gas_heat_flux:.4g} W/m² for a {self.engine_scale} engine.",
                "Check Bartz inputs, throat geometry, gas properties, and wall cooling assumptions."
            )

        if regen_heat_flux is not None and regen_heat_flux > limit:
            self.add_issue(
                issues,
                "warning",
                "High regenerative heat flux",
                f"Regenerative heat flux is {regen_heat_flux:.4g} W/m² for a {self.engine_scale} engine.",
                "Check coolant flow, wall resistance, and heat-transfer coefficients."
            )

    def check_wall_temperatures(self, solved, issues):
        hot_wall = self.safe_float(solved.get("hot_gas_side_wall_temperature"))
        material_max = self.safe_float(solved.get("material_max_wall_temperature"))
        margin = self.safe_float(solved.get("material_temperature_margin"))

        if hot_wall is not None and material_max is not None and hot_wall > material_max:
            self.add_issue(
                issues,
                "critical",
                "Hot wall temperature exceeds material limit",
                f"Hot-gas-side wall temperature is {hot_wall:.4g} K, above material limit {material_max:.4g} K.",
                "Increase cooling, change material, increase conductivity, reduce heat flux, or revise channel geometry."
            )

        if margin is not None and margin < 0:
            self.add_issue(
                issues,
                "critical",
                "Negative material temperature margin",
                f"Material temperature margin is {margin:.4g} K.",
                "Thermal design is outside the selected material limit."
            )

    def check_wall_thickness(self, solved, issues):
        hot_wall_thickness = self.safe_float(solved.get("hot_gas_wall_thickness"))
        pressure_required = self.safe_float(solved.get("pressure_required_wall_thickness"))
        conduction_required = self.safe_float(solved.get("conduction_required_wall_thickness"))

        if hot_wall_thickness is None:
            return

        if pressure_required is not None and hot_wall_thickness < pressure_required:
            self.add_issue(
                issues,
                "critical",
                "Wall thinner than pressure requirement",
                f"Hot-gas wall thickness is {hot_wall_thickness:.4g} m, below pressure-required thickness {pressure_required:.4g} m.",
                "Enable wall auto-sizing or increase minimum wall thickness."
            )

        if conduction_required is not None and hot_wall_thickness < conduction_required:
            self.add_issue(
                issues,
                "warning",
                "Wall thinner than conduction estimate",
                f"Hot-gas wall thickness is {hot_wall_thickness:.4g} m, below conduction estimate {conduction_required:.4g} m.",
                "This may indicate the simplified conduction requirement is conservative or that cooling needs revision."
            )

    def check_channel_geometry(self, solved, issues):
        fit_ratio = self.safe_float(solved.get("channel_fit_ratio"))
        valid = solved.get("channel_geometry_valid")
        effective_rib_width = self.safe_float(solved.get("effective_rib_width"))

        requested_width = self.safe_float(solved.get("coolant_channel_width"))
        requested_rib = self.safe_float(solved.get("rib_width"))
        requested_pitch = self.safe_float(solved.get("channel_pitch"))
        available_pitch = self.safe_float(solved.get("circumferential_channel_pitch"))

        if requested_pitch is None and requested_width is not None and requested_rib is not None:
            requested_pitch = requested_width + requested_rib

        if requested_pitch is not None and available_pitch is not None:
            if requested_pitch > available_pitch:
                self.add_issue(
                    issues,
                    "critical",
                    "Requested coolant channel pitch does not fit",
                    f"Requested pitch is {requested_pitch:.4g} m, but available circumferential pitch is only {available_pitch:.4g} m.",
                    "Reduce channel width, reduce rib width, reduce channel count, or increase local radius."
                )

        if fit_ratio is not None:
            if fit_ratio < 1.0:
                self.add_issue(
                    issues,
                    "critical",
                    "Coolant channels exceed available circumference",
                    f"Channel fit ratio is {fit_ratio:.4g}. Values below 1.0 mean the requested pitch does not fit.",
                    "The geometry should not be marked valid unless auto-resizing is explicitly enabled."
                )
            elif fit_ratio < 1.1:
                self.add_issue(
                    issues,
                    "warning",
                    "Coolant channels have little circumferential margin",
                    f"Channel fit ratio is {fit_ratio:.4g}.",
                    "Check manufacturability and rib width margin."
                )

        if str(valid).lower() in {"false", "0"}:
            self.add_issue(
                issues,
                "critical",
                "Invalid channel geometry",
                "Channel geometry validity flag is false.",
                "Check channel count, width, rib width, and local radius."
            )

        if effective_rib_width is not None and effective_rib_width <= 0:
            self.add_issue(
                issues,
                "critical",
                "Non-positive effective rib width",
                f"Effective rib width is {effective_rib_width:.4g} m.",
                "Coolant channels overlap; reduce channel count or width."
            )

        if requested_rib is not None and effective_rib_width is not None:
            if effective_rib_width < requested_rib:
                self.add_issue(
                    issues,
                    "warning",
                    "Effective rib width below requested rib width",
                    f"Requested rib width is {requested_rib:.4g} m, but effective rib width is {effective_rib_width:.4g} m.",
                    "The displayed geometry is being squeezed compared with the requested design."
                )

    def check_coolant_flow(self, solved, issues):
        limits = self.get_scale_limits()

        reynolds = self.safe_float(solved.get("coolant_reynolds_number"))
        pressure_drop = self.safe_float(solved.get("coolant_pressure_drop"))
        coolant_velocity = self.safe_float(solved.get("coolant_velocity"))

        if reynolds is not None:
            if reynolds < 2300:
                self.add_issue(
                    issues,
                    "warning",
                    "Coolant flow may be laminar",
                    f"Coolant Reynolds number is {reynolds:.4g}.",
                    "Laminar coolant flow usually gives weaker heat transfer. Consider higher velocity, smaller hydraulic diameter, or more coolant mass flow."
                )
            elif reynolds < 4000:
                self.add_issue(
                    issues,
                    "info",
                    "Coolant flow is transitional",
                    f"Coolant Reynolds number is {reynolds:.4g}.",
                    "Heat-transfer correlations may be less reliable in the transitional regime."
                )

        if pressure_drop is not None:
            if pressure_drop < 0:
                self.add_issue(
                    issues,
                    "critical",
                    "Negative coolant pressure drop",
                    f"Coolant pressure drop is {pressure_drop:.4g} Pa.",
                    "Check friction factor and channel length calculations."
                )
            elif pressure_drop > limits["coolant_pressure_drop_warning"]:
                self.add_issue(
                    issues,
                    "warning",
                    "High coolant pressure drop",
                    f"Coolant pressure drop is {pressure_drop:.4g} Pa for a {self.engine_scale} engine.",
                    "Check pump requirements, coolant channel dimensions, and channel length."
                )

        if coolant_velocity is not None and coolant_velocity > limits["coolant_velocity_warning"]:
            self.add_issue(
                issues,
                "warning",
                "High coolant velocity",
                f"Coolant velocity is {coolant_velocity:.4g} m/s for a {self.engine_scale} engine.",
                "Check pressure drop, erosion risk, and pump requirements."
            )