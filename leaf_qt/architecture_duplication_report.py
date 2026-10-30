from __future__ import annotations

from pathlib import Path

from core.architecture.duplication import (
    build_architecture_duplication_report,
    build_duplication_text_report,
)
from core.architecture.io import write_json_artifact, write_text_artifact


OUT_JSON = Path("artifacts/architecture_duplication_report.json")
OUT_TXT = Path("artifacts/architecture_duplication_report.txt")


if __name__ == "__main__":
    report = build_architecture_duplication_report(".")
    payload = report.to_dict()
    text = build_duplication_text_report(report)

    write_json_artifact(payload, OUT_JSON)
    write_text_artifact(text, OUT_TXT)

    print(text)
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")
    print("PASS_ARCHITECTURE_DUPLICATION_REPORT")
