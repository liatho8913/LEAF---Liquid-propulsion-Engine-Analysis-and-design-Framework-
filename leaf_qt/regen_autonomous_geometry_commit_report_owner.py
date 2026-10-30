"""
PHASE 11B.2K
Regen Autonomous Geometry Commit Report Owner
"""


def attach_regen_autonomous_geometry_commit_report_owner(results):
    if not isinstance(results, dict):
        return results

    report = results.get("regen_autonomous_geometry_commit_report")

    if not isinstance(report, str) or not report.strip():
        report = build_fallback_report(results)

    results.update({
        "regen_autonomous_geometry_commit_report_complete": True,
        "phase_11b_2k_regen_autonomous_geometry_commit_report_complete": True,
        "regen_autonomous_geometry_commit_report_status": (
            "PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_REPORT_BUILT"
        ),
        "regen_autonomous_geometry_commit_report": report,
    })

    return results


def build_fallback_report(results):
    review = results.get("regen_autonomous_geometry_commit_review", {})
    if not isinstance(review, dict):
        review = {}

    return "\n".join([
        "LEAF PHASE 11B.2K REGEN AUTONOMOUS GEOMETRY COMMIT REPORT",
        "==========================================================",
        "",
        f"Status: {results.get('regen_autonomous_geometry_commit_status')}",
        f"Ready: {results.get('regen_autonomous_geometry_commit_ready')}",
        f"Decision: {review.get('decision')}",
        f"Issues: {review.get('issues')}",
        f"Warnings: {review.get('warnings')}",
    ])