"""
LEAF Demonstrator Release Completion Gate.

Canonical project-level owner for deciding whether the current LEAF
demonstrator has satisfied its authorised release-completion scope.

This owner is governance/maintenance infrastructure only.

It does not:
- execute engineering solvers;
- alter engineering state;
- modify production source;
- qualify engineering candidates;
- add engineering modules;
- package the application;
- mutate canonical governance documents.

The gate consumes existing evidence and reports remaining release blockers.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import ast
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

CONSTITUTION = ROOT / "LEAF_DESIGN_CONSTITUTION.md"
ROADMAP = ROOT / "LEAF_MASTER_ROADMAP.md"
HANDOVER = ROOT / "LEAF_CURRENT_PROGRAMME_HANDOVER.md"

NORMAL_APP_ACCEPTANCE = (
    Path.home()
    / "Downloads"
    / "LEAF_DEMONSTRATOR_RELEASE_NORMAL_APP_ACCEPTANCE.json"
)

PACKAGE_ACCEPTANCE = (
    Path.home()
    / "Downloads"
    / "LEAF_DEMONSTRATOR_RELEASE_PACKAGE_ACCEPTANCE.json"
)

REPORT_PATH = (
    Path.home()
    / "Downloads"
    / "LEAF_DEMONSTRATOR_RELEASE_COMPLETION_GATE.json"
)

CANONICAL_IDENTITY = (
    "Liquid Propulsion Engine Analysis and Design Framework"
)

EXPECTED_MODULE_SCOPE = {
    "combustion_chamber",
    "nozzle",
    "regen",
}


@dataclass(frozen=True)
class GateCheck:
    check_id: str
    passed: bool
    evidence: Any
    blocker: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "evidence": self.evidence,
            "blocker": self.blocker,
        }


def production_files() -> list[Path]:
    return sorted(
        LEAF_QT.rglob("*.py")
    )


def production_fingerprint() -> str:
    h = sha256()

    for path in production_files():
        relative = (
            path.relative_to(ROOT)
            .as_posix()
        )

        h.update(
            relative.encode()
        )
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")

    return h.hexdigest()


def production_parse_failures() -> list[dict[str, str]]:
    failures = []

    for path in production_files():
        try:
            ast.parse(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except Exception as exc:
            failures.append({
                "file":
                    path.relative_to(ROOT)
                    .as_posix(),

                "error":
                    repr(exc),
            })

    return failures


def read_text(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def section_text(
    text: str,
    heading_fragment: str,
) -> str:
    lines = text.splitlines()

    start = None
    level = None

    for index, line in enumerate(lines):
        stripped = line.strip()

        if (
            stripped.startswith("#")
            and
            heading_fragment.lower()
            in stripped.lower()
        ):
            start = index
            level = (
                len(stripped)
                -
                len(stripped.lstrip("#"))
            )
            break

    if start is None:
        return ""

    collected = []

    for line in lines[start:]:
        stripped = line.strip()

        if (
            collected
            and
            stripped.startswith("#")
        ):
            candidate_level = (
                len(stripped)
                -
                len(stripped.lstrip("#"))
            )

            if candidate_level <= level:
                break

        collected.append(line)

    return "\n".join(
        collected
    )


def authoritative_handover_hash(
    handover_text: str,
) -> tuple[str | None, list[str]]:
    baseline_section = section_text(
        handover_text,
        "Authoritative production baseline",
    )

    hashes = re.findall(
        r"\b[a-fA-F0-9]{64}\b",
        baseline_section,
    )

    unique_hashes = sorted(
        set(
            value.lower()
            for value in hashes
        )
    )

    if len(unique_hashes) != 1:
        return None, unique_hashes

    return unique_hashes[0], unique_hashes


def load_acceptance(
    path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "EVIDENCE_FILE_MISSING"

    try:
        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        return None, (
            "EVIDENCE_FILE_INVALID_JSON:"
            f"{exc}"
        )

    if not isinstance(
        payload,
        dict,
    ):
        return None, "EVIDENCE_PAYLOAD_NOT_OBJECT"

    return payload, None


def acceptance_passed(
    payload: dict[str, Any] | None,
    completion_key: str,
) -> tuple[bool, dict[str, Any]]:
    if not isinstance(
        payload,
        dict,
    ):
        return False, {}

    checks = payload.get(
        "checks",
        {},
    )

    checks_valid = bool(
        isinstance(
            checks,
            dict,
        )
        and
        checks
        and
        all(
            value is True
            for value in checks.values()
        )
    )

    completion = (
        payload.get(
            completion_key
        )
        is True
    )

    source_preserved = (
        payload.get(
            "source_preserved"
        )
        is True
    )

    return (
        bool(
            completion
            and
            checks_valid
            and
            source_preserved
        ),
        {
            "completion":
                completion,

            "checks_present":
                (
                    len(checks)
                    if isinstance(
                        checks,
                        dict,
                    )
                    else 0
                ),

            "all_checks_pass":
                checks_valid,

            "source_preserved":
                source_preserved,
        },
    )


def main() -> int:
    constitution = read_text(
        CONSTITUTION
    )

    roadmap = read_text(
        ROADMAP
    )

    handover = read_text(
        HANDOVER
    )

    live_hash = (
        production_fingerprint()
    )

    parse_failures = (
        production_parse_failures()
    )

    handover_hash, handover_hashes = (
        authoritative_handover_hash(
            handover
        )
    )

    normal_app, normal_app_error = (
        load_acceptance(
            NORMAL_APP_ACCEPTANCE
        )
    )

    package, package_error = (
        load_acceptance(
            PACKAGE_ACCEPTANCE
        )
    )

    normal_app_passed, normal_app_summary = (
        acceptance_passed(
            normal_app,
            "release_normal_app_acceptance_complete",
        )
    )

    package_passed, package_summary = (
        acceptance_passed(
            package,
            "release_package_acceptance_complete",
        )
    )

    roadmap_scope = section_text(
        roadmap,
        "Existing engineering-module scope",
    )

    handover_scope = section_text(
        handover,
        "Existing Module Engine scope",
    )

    module_presence = {
        module: bool(
            (
                f"`{module}`"
                in roadmap_scope
            )
            and
            (
                f"`{module}`"
                in handover_scope
            )
        )
        for module in sorted(
            EXPECTED_MODULE_SCOPE
        )
    }

    checks = [
        GateCheck(
            "CANONICAL_GOVERNANCE_DOCUMENTS_PRESENT",
            all(
                path.exists()
                for path in (
                    CONSTITUTION,
                    ROADMAP,
                    HANDOVER,
                )
            ),
            {
                path.name:
                    path.exists()
                for path in (
                    CONSTITUTION,
                    ROADMAP,
                    HANDOVER,
                )
            },
            "CANONICAL_GOVERNANCE_DOCUMENT_MISSING",
        ),

        GateCheck(
            "CANONICAL_PROJECT_IDENTITY",
            all(
                CANONICAL_IDENTITY
                in text
                for text in (
                    constitution,
                    roadmap,
                    handover,
                )
            ),
            CANONICAL_IDENTITY,
            "CANONICAL_PROJECT_IDENTITY_NOT_ALIGNED",
        ),

        GateCheck(
            "PRODUCTION_PARSE_CLEAN",
            not parse_failures,
            {
                "production_python_files":
                    len(
                        production_files()
                    ),

                "parse_failure_count":
                    len(
                        parse_failures
                    ),
            },
            "PRODUCTION_PARSE_FAILURE",
        ),

        GateCheck(
            "ROADMAP_RELEASE_COMPLETION_AUTHORISED",
            (
                "LEAF Demonstrator Release Completion"
                in roadmap
                and
                "LEAF Demonstrator Release Completion"
                in handover
            ),
            {
                "roadmap":
                    (
                        "LEAF Demonstrator Release Completion"
                        in roadmap
                    ),

                "handover":
                    (
                        "LEAF Demonstrator Release Completion"
                        in handover
                    ),
            },
            "RELEASE_COMPLETION_NOT_AUTHORISED",
        ),

        GateCheck(
            "EXISTING_ENGINEERING_MODULE_SCOPE_PRESERVED",
            all(
                module_presence.values()
            ),
            module_presence,
            "EXISTING_MODULE_SCOPE_NOT_PRESERVED",
        ),

        GateCheck(
            "NO_SPECULATIVE_MODULE_DIRECTION",
            (
                "No additional engineering module is authorised"
                in roadmap
                and
                (
                    "Do not infer, create or schedule speculative modules"
                    in handover
                    or
                    "Do not add speculative modules"
                    in handover
                )
            ),
            {
                "roadmap_scope_lock":
                    (
                        "No additional engineering module is authorised"
                        in roadmap
                    ),

                "handover_scope_lock":
                    (
                        "Do not infer, create or schedule speculative modules"
                        in handover
                        or
                        "Do not add speculative modules"
                        in handover
                    ),
            },
            "SPECULATIVE_MODULE_SCOPE_NOT_LOCKED",
        ),

        GateCheck(
            "REGEN_FROZEN_FOR_DEMONSTRATOR",
            (
                "Regen is frozen"
                in roadmap
                and
                "COMPLETE AND FROZEN"
                in handover
            ),
            {
                "roadmap_regen_frozen":
                    (
                        "Regen is frozen"
                        in roadmap
                    ),

                "handover_complete_and_frozen":
                    (
                        "COMPLETE AND FROZEN"
                        in handover
                    ),
            },
            "REGEN_FREEZE_NOT_CANONICAL",
        ),

        GateCheck(
            "HANDOVER_AUTHORITATIVE_BASELINE_RESOLVED",
            handover_hash is not None,
            {
                "resolved_hash":
                    handover_hash,

                "hashes_found":
                    handover_hashes,
            },
            "HANDOVER_AUTHORITATIVE_BASELINE_AMBIGUOUS_OR_MISSING",
        ),

        GateCheck(
            "HANDOVER_AUTHORITATIVE_BASELINE_CURRENT",
            bool(
                handover_hash
                and
                handover_hash
                ==
                live_hash
            ),
            {
                "handover_hash":
                    handover_hash,

                "live_hash":
                    live_hash,
            },
            "HANDOVER_PRODUCTION_BASELINE_STALE",
        ),

        GateCheck(
            "CANONICAL_RELEASE_CLOSEOUT_RECORDED",
            (
                "LEAF Demonstrator Release Completion — COMPLETE AND FROZEN"
                in roadmap
                and
                "LEAF Demonstrator Release Completion — COMPLETE AND FROZEN"
                in handover
            ),
            {
                "roadmap_closeout":
                    (
                        "LEAF Demonstrator Release Completion — COMPLETE AND FROZEN"
                        in roadmap
                    ),

                "handover_closeout":
                    (
                        "LEAF Demonstrator Release Completion — COMPLETE AND FROZEN"
                        in handover
                    ),
            },
            "CANONICAL_RELEASE_CLOSEOUT_NOT_RECORDED",
        ),

        GateCheck(
            "PROJECT_WIDE_NORMAL_APP_ACCEPTANCE",
            normal_app_passed,
            {
                "path":
                    str(
                        NORMAL_APP_ACCEPTANCE
                    ),

                "load_error":
                    normal_app_error,

                **normal_app_summary,
            },
            "NORMAL_APP_RELEASE_ACCEPTANCE_MISSING_OR_FAILED",
        ),

        GateCheck(
            "RELEASE_PACKAGE_ACCEPTANCE",
            package_passed,
            {
                "path":
                    str(
                        PACKAGE_ACCEPTANCE
                    ),

                "load_error":
                    package_error,

                **package_summary,
            },
            "RELEASE_PACKAGE_ACCEPTANCE_MISSING_OR_FAILED",
        ),
    ]

    blockers = [
        check.blocker
        for check in checks
        if (
            not check.passed
            and
            check.blocker
        )
    ]

    complete = (
        not blockers
    )

    payload = {
        "schema":
            "LEAF_DEMONSTRATOR_RELEASE_COMPLETION_GATE_V1",

        "project":
            CANONICAL_IDENTITY,

        "production_source_sha256":
            live_hash,

        "production_python_files":
            len(
                production_files()
            ),

        "check_count":
            len(
                checks
            ),

        "passed_check_count":
            sum(
                check.passed
                for check in checks
            ),

        "failed_check_count":
            sum(
                not check.passed
                for check in checks
            ),

        "checks":
            {
                check.check_id:
                    check.as_dict()
                for check in checks
            },

        "blockers":
            blockers,

        "release_completion_ready":
            complete,

        "production_mutation_performed":
            False,

        "solver_executed":
            False,

        "engineering_behaviour_changed":
            False,
    }

    REPORT_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 78)
    print(
        "LEAF DEMONSTRATOR RELEASE COMPLETION GATE"
    )
    print("=" * 78)

    print(
        "production_source_sha256="
        f"{live_hash}"
    )

    print(
        "production_python_files="
        f"{len(production_files())}"
    )

    print()

    for check in checks:
        print(
            f"{check.check_id}="
            f"{check.passed}"
        )

        if not check.passed:
            print(
                "  blocker="
                f"{check.blocker}"
            )

            print(
                "  evidence="
                f"{check.evidence}"
            )

    print()
    print(
        f"passed_check_count="
        f"{payload['passed_check_count']}"
    )

    print(
        f"failed_check_count="
        f"{payload['failed_check_count']}"
    )

    print(
        f"blockers="
        f"{blockers}"
    )

    print(
        "release_completion_ready="
        f"{complete}"
    )

    print(
        f"report="
        f"{REPORT_PATH}"
    )

    print(
        "production_mutation_performed=False"
    )

    print(
        "solver_executed=False"
    )

    print(
        "engineering_behaviour_changed=False"
    )

    if complete:
        print()
        print(
            "PASS_LEAF_DEMONSTRATOR_RELEASE_COMPLETION_GATE"
        )

        print(
            "next="
            "DEMONSTRATOR_RELEASE_FROZEN_NO_ACTIVE_ENGINEERING_PROGRAMME"
        )

        return 0

    print()
    print(
        "LEAF_DEMONSTRATOR_RELEASE_COMPLETION_BLOCKED"
    )

    print(
        "next="
        "RESOLVE_ONLY_REPORTED_RELEASE_BLOCKERS"
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
