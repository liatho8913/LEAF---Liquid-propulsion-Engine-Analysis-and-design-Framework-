from core.contracts.base_contracts import (
    ContractResult,
    SolverContract,
    ValidationContract,
    ReportingContract,
    RegistryContract,
    OptimisationContract,
    UIPanelContract,
    describe_contract,
    validate_contract_metadata,
)


class DemoSolver(SolverContract):
    def contract_metadata(self):
        return {
            "subsystem": "DEMO_SOLVER",
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def solve(self, inputs):
        return {"value": inputs["x"] + 1}


class DemoValidation(ValidationContract):
    def contract_metadata(self):
        return {
            "subsystem": "DEMO_VALIDATION",
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def validate(self, payload):
        return ContractResult(
            status="PASS" if payload.get("ok") else "FAIL",
            subsystem="DEMO_VALIDATION",
            message="demo validation complete",
            evidence={"payload": dict(payload)},
        )


class DemoReport(ReportingContract):
    def contract_metadata(self):
        return {
            "subsystem": "DEMO_REPORT",
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def build_report(self, payload):
        return f"report={payload.get('value')}"


class DemoRegistry(RegistryContract):
    def __init__(self):
        self._items = {"a": 1}

    def contract_metadata(self):
        return {
            "subsystem": "DEMO_REGISTRY",
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def list_registered_keys(self):
        return sorted(self._items)

    def get_registered_item(self, key):
        return self._items[key]


class DemoOptimisation(OptimisationContract):
    def contract_metadata(self):
        return {
            "subsystem": "DEMO_OPTIMISATION",
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def optimise(self, inputs):
        return {"best": inputs.get("seed", 0)}


class DemoPanel(UIPanelContract):
    def __init__(self):
        self.payload = {}

    def contract_metadata(self):
        return {
            "subsystem": "DEMO_UI",
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def panel_title(self):
        return "Demo Panel"

    def refresh_from_payload(self, payload):
        self.payload = dict(payload)


class BrokenMetadata(SolverContract):
    def contract_metadata(self):
        return {
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
        }

    def solve(self, inputs):
        return {}


def test_solver_contract():
    solver = DemoSolver()
    assert solver.solve({"x": 2})["value"] == 3
    result = validate_contract_metadata(solver)
    assert result.passed is True
    assert result.subsystem == "DEMO_SOLVER"


def test_validation_contract():
    validator = DemoValidation()
    assert validator.validate({"ok": True}).passed is True
    assert validator.validate({"ok": False}).passed is False


def test_reporting_contract():
    report = DemoReport()
    assert report.build_report({"value": 7}) == "report=7"


def test_registry_contract():
    registry = DemoRegistry()
    assert registry.list_registered_keys() == ["a"]
    assert registry.get_registered_item("a") == 1


def test_optimisation_contract():
    optimiser = DemoOptimisation()
    assert optimiser.optimise({"seed": 42})["best"] == 42


def test_ui_panel_contract():
    panel = DemoPanel()
    panel.refresh_from_payload({"a": 1})
    assert panel.panel_title() == "Demo Panel"
    assert panel.payload == {"a": 1}


def test_describe_contract_adds_defaults():
    solver = DemoSolver()
    metadata = describe_contract(solver)
    assert metadata["contract_name"] == "SOLVER_CONTRACT"
    assert metadata["contract_version"] == "1.0"
    assert metadata["subsystem"] == "DEMO_SOLVER"


def test_contract_metadata_failure():
    broken = BrokenMetadata()
    result = validate_contract_metadata(broken)
    assert result.passed is False
    assert "subsystem" in result.evidence["missing"]


if __name__ == "__main__":
    test_solver_contract()
    test_validation_contract()
    test_reporting_contract()
    test_registry_contract()
    test_optimisation_contract()
    test_ui_panel_contract()
    test_describe_contract_adds_defaults()
    test_contract_metadata_failure()
    print("PASS_STABLE_CONTRACT_EXTRACTION_FRAMEWORK_TEST")
