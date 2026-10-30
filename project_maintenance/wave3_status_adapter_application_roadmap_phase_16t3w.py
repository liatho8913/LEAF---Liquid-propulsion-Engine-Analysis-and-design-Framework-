from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave3_status_adapter_candidate_selection_phase_16t3v import (
    select_wave3_candidates,
)


PASS_STATUS = "PASS_WAVE3_STATUS_ADAPTER_APPLICATION_ROADMAP_PHASE_16T3W"
FAIL_STATUS = "FAIL_WAVE3_STATUS_ADAPTER_APPLICATION_ROADMAP_PHASE_16T3W"


ARCHIVE_OR_UPLOAD_MARKERS = [
    "LEAF_UPLOAD/",
    "archive/",
    "backup/",
    "backups/",
    "_archive/",
]


def _is_active_source(path):
    normalised = path.replace("\\", "/")
    return not any(marker in normalised for marker in ARCHIVE_OR_UPLOAD_MARKERS)


def _dedupe_candidates(candidates):
    seen_names = set()
    active = []

    for item in candidates:
        path = item["path"]
        if not _is_active_source(path):
            continue

        basename = Path(path).name
        if basename in seen_names:
            continue

        seen_names.add(basename)
        active.append(item)

    return active


def _phase_for_index(index):
    return f"16T.3W.{index}"


def build_wave3_status_adapter_application_roadmap(limit=8):
    selection = select_wave3_candidates(limit=40)
    active_candidates = _dedupe_candidates(selection.get("all_candidates", []))

    selected = active_candidates[:limit]

    roadmap = []

    for index, item in enumerate(selected, start=1):
        roadmap.append(
            {
                "phase": _phase_for_index(index),
                "target": item["path"],
                "classification": item["classification"],
                "legacy_status_count": item["legacy_status_count"],
                "score": item["score"],
                "implementation_policy": [
                    "inspect public API before patching",
                    "apply additive wrapper or payload extension only",
                    "preserve legacy status strings",
                    "preserve public function names",
                    "preserve existing payload fields",
                    "add structured_findings",
                    "add global_status",
                    "add global_status_payload",
                    "add adapter_report",
                    "add focused regression test",
                    "run legacy regression if present",
                ],
                "risk": (
                    "HIGH" if item["classification"] in {"GENERAL_STATUS_EMITTER"} and item["legacy_status_count"] > 40
                    else "MEDIUM" if item["legacy_status_count"] > 15
                    else "LOW"
                ),
            }
        )

    passed = bool(roadmap)
    status = PASS_STATUS if passed else FAIL_STATUS

    report_lines = [
        "LEAF PHASE 16T.3W",
        "WAVE 3 STATUS ADAPTER APPLICATION ROADMAP",
        "=========================================",
        "",
        f"Status: {status}",
        f"Candidate selection status: {selection.get('status')}",
        f"Raw candidates discovered: {selection.get('candidate_count')}",
        f"Active candidates after archive/upload filtering: {len(active_candidates)}",
        f"Roadmap targets selected: {len(roadmap)}",
        "",
        "Archive / Upload Filtering:",
        "- LEAF_UPLOAD and archive/backup copies are excluded from production migration.",
        "- Active source files are preferred over duplicated uploaded snapshots.",
        "",
        "Roadmap:",
    ]

    for item in roadmap:
        report_lines.append(
            f"- {item['phase']} | {item['target']} | {item['classification']} | "
            f"risk={item['risk']} | legacy_statuses={item['legacy_status_count']}"
        )

    report_lines.extend(
        [
            "",
            "Implementation Rule:",
            "No Wave 3 production module should be patched until its public API has been inspected.",
            "",
            "Decision:",
            (
                "Wave 3 application roadmap is complete."
                if passed
                else "Wave 3 application roadmap could not select active targets."
            ),
        ]
    )

    return {
        "phase": "16T.3W",
        "passed": passed,
        "status": status,
        "selection": selection,
        "active_candidate_count": len(active_candidates),
        "roadmap_count": len(roadmap),
        "roadmap": roadmap,
        "report": "\n".join(report_lines),
        "wave3_status_adapter_application_roadmap_complete": passed,
        "phase_16t3w_wave3_status_adapter_application_roadmap_complete": passed,
    }


if __name__ == "__main__":
    result = build_wave3_status_adapter_application_roadmap()
    print(result["report"])
    if not result["passed"]:
        raise SystemExit(1)
