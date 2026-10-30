from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class PostQuarantineFileVerification:
    source: str
    destination: str
    source_absent: bool
    destination_present: bool
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "destination": self.destination,
            "source_absent": self.source_absent,
            "destination_present": self.destination_present,
            "status": self.status,
        }


@dataclass(frozen=True)
class PostQuarantineVerificationResult:
    status: str
    source_application: str
    files_verified: int
    source_absent_count: int
    destination_present_count: int
    failed_count: int
    mutation_performed_by_verifier: bool
    files: list[PostQuarantineFileVerification]
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source_application": self.source_application,
            "files_verified": self.files_verified,
            "source_absent_count": self.source_absent_count,
            "destination_present_count": self.destination_present_count,
            "failed_count": self.failed_count,
            "mutation_performed_by_verifier": self.mutation_performed_by_verifier,
            "files": [item.to_dict() for item in self.files],
            "next_action": self.next_action,
        }


class PostQuarantineVerifier:
    """
    Read-only verifier for controlled legacy quarantine.

    It verifies only moves recorded by 31J.5.

    It does not move files.
    It does not delete files.
    It does not edit imports.
    """

    def __init__(self, root: Path, application_json: Path):
        self.root = Path(root)
        self.application_json = Path(application_json)

    def load_moves(self) -> list[dict[str, Any]]:
        payload = json.loads(self.application_json.read_text(encoding="utf-8"))
        return payload.get("application", {}).get("moves", [])

    def verify_move(self, move: dict[str, Any]) -> PostQuarantineFileVerification:
        source = move["source"]
        destination = move["destination"]

        src = self.root / source
        dst = self.root / destination

        source_absent = not src.exists()
        destination_present = dst.exists() and dst.is_file()

        return PostQuarantineFileVerification(
            source=source,
            destination=destination,
            source_absent=source_absent,
            destination_present=destination_present,
            status="PASS" if source_absent and destination_present else "FAIL",
        )

    def verify(self) -> PostQuarantineVerificationResult:
        moves = [
            move for move in self.load_moves()
            if move.get("status") == "PASS"
        ]

        verifications = [self.verify_move(move) for move in moves]
        failed = [item for item in verifications if item.status != "PASS"]

        return PostQuarantineVerificationResult(
            status="PASS" if verifications and not failed else "FAIL",
            source_application=str(self.application_json.relative_to(self.root)),
            files_verified=len(verifications),
            source_absent_count=len([item for item in verifications if item.source_absent]),
            destination_present_count=len([item for item in verifications if item.destination_present]),
            failed_count=len(failed),
            mutation_performed_by_verifier=False,
            files=verifications,
            next_action="Repository simplification audit.",
        )
