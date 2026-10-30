from regen_candidate_decision_gate_owner import (
    attach_regen_candidate_decision_gate_owner,
)


def test_decision_gate_rejects_negative_score():
    solved = attach_regen_candidate_decision_gate_owner({
        "regen_candidate_post_validation_complete": True,
        "regen_candidate_post_validation_score": -0.1,
        "regen_candidate_post_validation_status": "FAIL_REGEN_CANDIDATE_POST_RESOLVE_WORSE",
    })

    assert solved["phase_11b_1j_regen_candidate_decision_gate_complete"] is True
    assert solved["regen_candidate_decision"] == "REJECTED"
    assert solved["regen_candidate_decision_status"] == (
        "PASS_REGEN_CANDIDATE_DECISION_REJECTED"
    )


def test_decision_gate_marks_equivalent_as_acceptable():
    solved = attach_regen_candidate_decision_gate_owner({
        "regen_candidate_post_validation_complete": True,
        "regen_candidate_post_validation_score": 0.0,
        "regen_candidate_post_validation_status": "WARN_REGEN_CANDIDATE_POST_RESOLVE_EQUIVALENT",
    })

    assert solved["regen_candidate_decision"] == "ACCEPTABLE"


def test_decision_gate_marks_small_positive_as_promising():
    solved = attach_regen_candidate_decision_gate_owner({
        "regen_candidate_post_validation_complete": True,
        "regen_candidate_post_validation_score": 0.1,
        "regen_candidate_post_validation_status": "PASS_REGEN_CANDIDATE_POST_RESOLVE_IMPROVED",
    })

    assert solved["regen_candidate_decision"] == "PROMISING"


def test_decision_gate_marks_large_positive_as_best_so_far():
    solved = attach_regen_candidate_decision_gate_owner({
        "regen_candidate_post_validation_complete": True,
        "regen_candidate_post_validation_score": 0.5,
        "regen_candidate_post_validation_status": "PASS_REGEN_CANDIDATE_POST_RESOLVE_IMPROVED",
    })

    assert solved["regen_candidate_decision"] == "BEST_SO_FAR"


def test_decision_gate_blocks_without_post_validation():
    solved = attach_regen_candidate_decision_gate_owner({})

    assert solved["regen_candidate_decision"] == "BLOCKED"
    assert solved["regen_candidate_decision_status"] == (
        "FAIL_REGEN_CANDIDATE_DECISION_BLOCKED"
    )