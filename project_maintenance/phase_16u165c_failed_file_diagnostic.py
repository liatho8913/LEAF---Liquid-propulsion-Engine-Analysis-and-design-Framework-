from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

IN_165 = ROOT / "project_maintenance" / "phase_16u165_safe_transactional_presentation_debt_cleanup_wave1.json"
IN_165B = ROOT / "project_maintenance" / "phase_16u165b_failed_subset_repair.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u165c_failed_file_diagnostic.txt"


def main() -> None:
    wave = json.loads(IN_165.read_text(encoding="utf-8"))
    repair = json.loads(IN_165B.read_text(encoding="utf-8"))

    lines = [
        "LEAF PHASE 16U.165C",
        "FAILED FILE DIAGNOSTIC EXTRACTION",
        "=" * 42,
        "",
        "16U.165 COMPILE FAILURES",
        "-" * 27,
    ]

    for item in wave.get("compile_failures", []):
        rel_path = item["path"]
        path = ROOT / rel_path

        lines.append(f"path={rel_path}")
        lines.append(f"error={item.get('error')}")
        lines.append(f"rolled_back={item.get('rolled_back')}")
        lines.append("")

        if path.exists():
            source = path.read_text(encoding="utf-8", errors="replace").splitlines()
            interesting = []

            for idx, line in enumerate(source, start=1):
                if ".startswith(" in line or ".endswith(" in line or "status_severity(" in line:
                    interesting.append(idx)

            lines.append("MATCHING LINES")
            lines.append("-" * 14)

            for idx in interesting[:50]:
                start = max(1, idx - 3)
                end = min(len(source), idx + 3)

                lines.append("")
                lines.append(f"--- context around line {idx} ---")
                for line_no in range(start, end + 1):
                    marker = ">>" if line_no == idx else "  "
                    lines.append(f"{marker} {line_no:5d}: {source[line_no - 1]}")
        else:
            lines.append("File does not exist.")

        lines.append("")

    lines.extend([
        "",
        "16U.165B UNREPAIRED",
        "-" * 22,
    ])

    for item in repair.get("unrepaired", []):
        lines.append(json.dumps(item, indent=2))

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    print("PASS_PHASE_16U165C_FAILED_FILE_DIAGNOSTIC")
    print(f"text_report={OUT_TXT}")


if __name__ == "__main__":
    main()
