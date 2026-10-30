from startup_health_check import run_startup_health_check


class StartupHealthController:
    """
    Owns LEAF startup-health state.

    This prevents main_window.py from directly storing and distributing
    startup-health reports through scattered lambdas.
    """

    def __init__(self):
        self.health_report = {}
        self.run_check()

    def run_check(self):
        self.health_report = run_startup_health_check()

        if not isinstance(self.health_report, dict):
            self.health_report = {
                "startup_health_status": "INVALID_HEALTH_REPORT",
                "startup_health_required_failure_count": 1,
                "startup_health_optional_warning_count": 0,
                "startup_health_rows": [],
                "startup_health_text": "Startup health check returned an invalid report.",
            }

        return self.health_report

    def get_report(self):
        return self.health_report or {}

    def get_status(self):
        return self.get_report().get("startup_health_status", "UNKNOWN")

    def get_required_failure_count(self):
        return self.get_report().get(
            "startup_health_required_failure_count",
            0,
        )

    def get_optional_warning_count(self):
        return self.get_report().get(
            "startup_health_optional_warning_count",
            0,
        )

    def get_text(self):
        return self.get_report().get(
            "startup_health_text",
            "No startup health report available.",
        )

    def attach_to_results(self, results):
        if not isinstance(results, dict):
            return results

        report = self.get_report()

        results["startup_health_status"] = report.get("startup_health_status")
        results["startup_health_text"] = report.get("startup_health_text")
        results["startup_health_required_failure_count"] = report.get(
            "startup_health_required_failure_count"
        )
        results["startup_health_optional_warning_count"] = report.get(
            "startup_health_optional_warning_count"
        )
        results["startup_health_attached_to_results"] = True

        return results