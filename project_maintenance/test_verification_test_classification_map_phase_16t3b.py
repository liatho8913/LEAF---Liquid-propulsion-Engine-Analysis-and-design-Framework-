from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.verification_test_classification_map_phase_16t3b import (
    PASS_STATUS,
    WARN_STATUS,
    classify_test_domain,
    build_verification_test_classification_map,
    build_verification_test_classification_report,
    write_verification_test_classification_map,
)


def main() -> int:
    assert classify_test_domain(Path("leaf_qt/test_regen_geometry_solver.py"))[0] == "engineering_geometry"
    assert classify_test_domain(Path("leaf_qt/test_material_validation_owner.py"))[0] == "engineering_materials"
    assert classify_test_domain(Path("leaf_qt/test_coating_validation_owner.py"))[0] == "engineering_coatings"
    assert classify_test_domain(Path("leaf_qt/test_regen_candidate_ranker.py"))[0] == "engineering_optimisation"
    assert classify_test_domain(Path("leaf_qt/test_real_engine_benchmark_master_gate.py"))[0] == "benchmarks_real_engines"

    mapping = build_verification_test_classification_map()

    assert mapping["status"] in {PASS_STATUS, WARN_STATUS}
    assert mapping["passed"] is True
    assert mapping["test_count"] >= 1
    assert "counts" in mapping
    assert "actions" in mapping

    report = build_verification_test_classification_report()

    assert "VERIFICATION TEST CLASSIFICATION MAP" in report
    assert "DOMAIN COUNTS" in report
    assert "SAFETY RULE" in report

    plan_path, report_path = write_verification_test_classification_map()

    assert plan_path.exists()
    assert report_path.exists()
    assert plan_path.parent.name == "allowlists"
    assert report_path.parent.name == "reports"

    print("PASS_VERIFICATION_TEST_CLASSIFICATION_MAP_PHASE_16T3B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
