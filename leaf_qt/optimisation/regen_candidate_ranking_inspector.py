"""
PHASE 16J — Candidate Ranking Inspector

Purpose:
- Show ranked regen candidates.
- Explain score, rank, winner/loser status, and penalties.
- Read-only: does not mutate, solve, accept, reject, or commit geometry.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTextEdit, QPushButton, QSplitter, QWidget
)
from PySide6.QtCore import Qt

try:
    from regen_recommendation_payload_ui_owner_phase_16n3 import (
        RegenRecommendationPayloadUIOwnerPhase16N3,
    )
except Exception:
    RegenRecommendationPayloadUIOwnerPhase16N3 = None



def get_ranked_candidates(results):
    if not isinstance(results, dict):
        return []

    for key in (
        "regen_candidate_ranking_inspector_ranked_candidates",
        "regen_optimisation_recommendation_ranked_candidates",
        "regen_optimisation_selection_ranked_candidates",
        "regen_optimisation_scored_candidates",
        "regen_candidate_ranking_ranked_candidates",
        "ranked_candidates",
    ):
        value = results.get(key)
        if isinstance(value, list):
            return value

    return []


def _candidate_value(candidate, keys, default="N/A"):
    if not isinstance(candidate, dict):
        return default
    for key in keys:
        if key in candidate:
            return candidate.get(key)
    return default


def _candidate_geometry(candidate):
    if not isinstance(candidate, dict):
        return {}
    for key in ("candidate_geometry", "geometry", "regen_geometry"):
        value = candidate.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _candidate_scores(candidate):
    if not isinstance(candidate, dict):
        return {}
    for key in ("score_breakdown", "candidate_score_breakdown", "scores", "metrics"):
        value = candidate.get(key)
        if isinstance(value, dict):
            return value
    return {}



def build_recommendation_payload_details(results):
    if RegenRecommendationPayloadUIOwnerPhase16N3 is None:
        return [
            "",
            "RECOMMENDATION PAYLOAD",
            "----------------------",
            "Recommendation payload owner could not be imported.",
        ]

    owner = RegenRecommendationPayloadUIOwnerPhase16N3()
    payload = owner.build(results if isinstance(results, dict) else {})

    lines = [
        "",
        "RECOMMENDATION PAYLOAD",
        "----------------------",
        f"Status: {payload.status}",
        f"Available: {payload.available}",
        f"Ready For User Acceptance: {payload.ready_for_user_acceptance}",
        f"Candidate ID: {payload.candidate_id}",
        f"Rank: {payload.rank}",
        f"Score: {payload.score}",
        f"Decision: {payload.decision}",
        "",
        "Recommendation Reason:",
        f"- {payload.reason or 'No recommendation reason supplied.'}",
        "",
        "Recommendation Blockers:",
    ]

    if payload.blockers:
        for blocker in payload.blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend(["", "Staged Geometry For Acceptance:"])

    if payload.staged_geometry:
        for key in sorted(payload.staged_geometry):
            lines.append(f"{key}: {payload.staged_geometry.get(key)}")
    else:
        lines.append("No staged geometry payload found.")

    return lines


def build_ranking_summary(candidate, row_index):
    geometry = _candidate_geometry(candidate)

    return {
        "rank": _candidate_value(candidate, ["rank", "candidate_rank"], row_index + 1),
        "id": _candidate_value(candidate, ["candidate_id", "id", "name"], f"CANDIDATE_{row_index+1:03d}"),
        "score": _candidate_value(candidate, ["score", "candidate_score", "total_score"], "N/A"),
        "status": _candidate_value(candidate, ["candidate_status", "status"], "UNKNOWN"),
        "winner": _candidate_value(candidate, ["winner", "is_winner", "selected"], False),
        "channels": geometry.get("number_of_coolant_channels", "N/A"),
        "width": geometry.get("coolant_channel_width", "N/A"),
        "height": geometry.get("coolant_channel_height", "N/A"),
        "rib": geometry.get("rib_width", "N/A"),
        "wall": geometry.get("hot_gas_wall_thickness", "N/A"),
    }


def format_ranking_details(candidate, row_index=0, results=None):
    if not isinstance(candidate, dict):
        return "No ranked candidate selected."

    summary = build_ranking_summary(candidate, row_index)
    geometry = _candidate_geometry(candidate)
    scores = _candidate_scores(candidate)

    penalties = _candidate_value(candidate, ["penalties", "penalty_breakdown"], {})
    failures = _candidate_value(candidate, ["failures", "failure_reasons", "blocking_reasons"], [])
    explanation = _candidate_value(candidate, ["explanation", "ranking_explanation", "reason"], "")

    lines = [
        "CANDIDATE RANKING DETAILS",
        "=========================",
        "",
        f"Rank: {summary['rank']}",
        f"Candidate ID: {summary['id']}",
        f"Score: {summary['score']}",
        f"Status: {summary['status']}",
        f"Winner/Selected: {summary['winner']}",
        "",
        "SCORE BREAKDOWN",
        "---------------",
    ]

    if scores:
        for key in sorted(scores):
            lines.append(f"{key}: {scores.get(key)}")
    else:
        lines.append("No score breakdown payload found.")

    lines.extend(["", "PENALTIES", "---------"])
    if isinstance(penalties, dict) and penalties:
        for key in sorted(penalties):
            lines.append(f"{key}: {penalties.get(key)}")
    elif isinstance(penalties, list) and penalties:
        for item in penalties:
            lines.append(f"- {item}")
    else:
        lines.append("No penalty breakdown payload found.")

    lines.extend(["", "FAILURE / WARNING REASONS", "-------------------------"])
    if isinstance(failures, list) and failures:
        for item in failures:
            lines.append(f"- {item}")
    elif failures:
        lines.append(str(failures))
    else:
        lines.append("No failure reasons reported.")

    lines.extend(["", "GEOMETRY", "--------"])
    if geometry:
        for key in sorted(geometry):
            lines.append(f"{key}: {geometry.get(key)}")
    else:
        lines.append("No geometry payload found.")

    lines.extend(["", "EXPLANATION", "-----------"])
    lines.append(str(explanation) if explanation else "No ranking explanation payload found.")

    lines.extend(build_recommendation_payload_details(results))

    lines.extend([
        "",
        "SAFETY MEANING",
        "--------------",
        "This inspector is read-only.",
        "It displays recommendation readiness but does not apply it.",
        "It does not solve candidates.",
        "It does not mutate candidates.",
        "It does not accept/reject candidates.",
        "It does not commit geometry.",
    ])

    return "\n".join(lines)


class RegenCandidateRankingInspector(QDialog):
    def __init__(self, results=None, parent=None):
        super().__init__(parent)

        self.results = results if isinstance(results, dict) else {}
        self.candidates = get_ranked_candidates(self.results)

        self.setWindowTitle("Regen Candidate Ranking Inspector")
        self.resize(1200, 720)

        self.build_ui()
        self.populate_table()
        self.update_summary()

    def build_ui(self):
        root = QVBoxLayout(self)

        title = QLabel("Regen Candidate Ranking Inspector")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        root.addWidget(self.summary_label)

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Rank", "ID", "Score", "Status", "Winner",
            "Channels", "Width", "Height", "Rib", "Wall"
        ])
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.table)

        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        right_layout.addWidget(self.details)

        splitter.addWidget(right)
        splitter.setSizes([700, 500])

        buttons = QHBoxLayout()
        root.addLayout(buttons)

        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        buttons.addWidget(refresh)

        copy = QPushButton("Copy Selected Ranking")
        copy.clicked.connect(self.copy_selected_ranking)
        buttons.addWidget(copy)

        close = QPushButton("Close")
        close.clicked.connect(self.close)
        buttons.addWidget(close)

    def update_summary(self):
        count = len(self.candidates)

        ranking_status = self.results.get(
            "regen_candidate_ranking_master_gate_status",
            self.results.get("regen_optimisation_selection_ranking_engine_status", "UNKNOWN"),
        )

        recommendation_count = self.results.get(
            "regen_optimisation_recommendation_ranked_candidate_count",
            count,
        )

        self.summary_label.setText(
            f"Ranked candidates: {count} | "
            f"Recommendation ranked count: {recommendation_count} | "
            f"Ranking status: {ranking_status} | "
            "Read-only inspector"
        )

        self.results["regen_candidate_ranking_inspector_opened"] = True
        self.results["regen_candidate_ranking_inspector_candidate_count"] = count
        self.results["regen_candidate_ranking_inspector_status"] = (
            "PASS_REGEN_CANDIDATE_RANKING_INSPECTOR_PHASE_16J"
            if count > 0 else
            "WARN_REGEN_CANDIDATE_RANKING_INSPECTOR_NO_RANKED_CANDIDATES_PHASE_16J"
        )

    def populate_table(self):
        self.table.setRowCount(len(self.candidates))

        for row, candidate in enumerate(self.candidates):
            summary = build_ranking_summary(candidate, row)
            values = [
                summary["rank"],
                summary["id"],
                summary["score"],
                summary["status"],
                summary["winner"],
                summary["channels"],
                summary["width"],
                summary["height"],
                summary["rib"],
                summary["wall"],
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

        if self.candidates:
            self.table.selectRow(0)
        else:
            self.details.setPlainText(
                "No ranked candidates are available yet.\n\n"
                "Ranking inspector is installed, but ranking data has not been produced/exposed."
            )

    def refresh(self):
        self.candidates = get_ranked_candidates(self.results)
        self.populate_table()
        self.update_summary()

    def selected_candidate(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.candidates):
            return None
        return self.candidates[row]

    def on_selection_changed(self):
        self.details.setPlainText(
            format_ranking_details(self.selected_candidate(), self.table.currentRow(), self.results)
        )

    def copy_selected_ranking(self):
        try:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(
                format_ranking_details(self.selected_candidate(), self.table.currentRow(), self.results)
            )
        except Exception:
            pass


def show_regen_candidate_ranking_inspector(results=None, parent=None):
    dialog = RegenCandidateRankingInspector(results=results, parent=parent)
    dialog.exec()
    return dialog
