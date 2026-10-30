"""
POST-16G — Candidate Population Inspector

Purpose:
- Let the user see generated regen candidates.
- Show candidate ID, generation, parent, status, geometry, and metadata.
- Does not rank, solve, mutate, accept, reject, or commit candidates.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QPushButton,
    QSplitter,
    QWidget,
)
from PySide6.QtCore import Qt


def get_candidate_population(results):
    if not isinstance(results, dict):
        return []

    candidates = results.get("regen_candidate_population")
    if isinstance(candidates, list):
        return candidates

    candidates = results.get("regen_candidate_population_candidates")
    if isinstance(candidates, list):
        return candidates

    candidates = results.get("regen_optimisation_candidate_generator_candidates")
    if isinstance(candidates, list):
        return candidates

    candidates = results.get("regen_candidate_generator_candidates")
    if isinstance(candidates, list):
        return candidates

    return []


def build_candidate_summary(candidate):
    if not isinstance(candidate, dict):
        return {}

    geometry = candidate.get("candidate_geometry")
    if not isinstance(geometry, dict):
        geometry = candidate.get("geometry")
    if not isinstance(geometry, dict):
        geometry = {}

    return {
        "candidate_id": candidate.get("candidate_id", "UNKNOWN"),
        "generation": candidate.get("candidate_generation", "N/A"),
        "parent": candidate.get("candidate_parent", "N/A"),
        "status": candidate.get("candidate_status", "UNKNOWN"),
        "channels": geometry.get("number_of_coolant_channels", "N/A"),
        "width": geometry.get("coolant_channel_width", "N/A"),
        "height": geometry.get("coolant_channel_height", "N/A"),
        "rib": geometry.get("rib_width", "N/A"),
        "wall": geometry.get("hot_gas_wall_thickness", "N/A"),
        "coolant_fraction": geometry.get("coolant_flow_fraction", "N/A"),
    }


def format_candidate_details(candidate):
    if not isinstance(candidate, dict):
        return "No candidate selected."

    geometry = candidate.get("candidate_geometry")
    if not isinstance(geometry, dict):
        geometry = candidate.get("geometry")
    if not isinstance(geometry, dict):
        geometry = {}

    metadata = candidate.get("candidate_metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    lines = [
        "CANDIDATE DETAILS",
        "=================",
        "",
        f"Candidate ID: {candidate.get('candidate_id', 'UNKNOWN')}",
        f"Generation: {candidate.get('candidate_generation', 'N/A')}",
        f"Parent: {candidate.get('candidate_parent', 'N/A')}",
        f"Status: {candidate.get('candidate_status', 'UNKNOWN')}",
        "",
        "GEOMETRY",
        "--------",
    ]

    if geometry:
        for key in sorted(geometry):
            lines.append(f"{key}: {geometry.get(key)}")
    else:
        lines.append("No geometry payload found.")

    lines.extend([
        "",
        "METADATA",
        "--------",
    ])

    if metadata:
        for key in sorted(metadata):
            lines.append(f"{key}: {metadata.get(key)}")
    else:
        lines.append("No metadata payload found.")

    lines.extend([
        "",
        "SAFETY MEANING",
        "--------------",
        "This inspector is read-only.",
        "It does not solve candidates.",
        "It does not rank candidates.",
        "It does not apply geometry.",
        "It does not modify live design inputs.",
    ])

    return "\n".join(lines)


class RegenCandidatePopulationInspector(QDialog):
    def __init__(self, results=None, parent=None):
        super().__init__(parent)

        self.results = results if isinstance(results, dict) else {}
        self.candidates = get_candidate_population(self.results)

        self.setWindowTitle("Regen Candidate Population Inspector")
        self.resize(1100, 700)

        self.build_ui()
        self.populate_table()
        self.update_summary()

    def build_ui(self):
        root = QVBoxLayout(self)

        title = QLabel("Regen Candidate Population Inspector")
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
            "ID",
            "Generation",
            "Parent",
            "Status",
            "Channels",
            "Width",
            "Height",
            "Rib",
            "Wall",
            "Coolant Fraction",
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
        splitter.setSizes([650, 450])

        buttons = QHBoxLayout()
        root.addLayout(buttons)

        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        buttons.addWidget(refresh)

        copy = QPushButton("Copy Selected Candidate")
        copy.clicked.connect(self.copy_selected_candidate)
        buttons.addWidget(copy)

        close = QPushButton("Close")
        close.clicked.connect(self.close)
        buttons.addWidget(close)

    def update_summary(self):
        population_count = len(self.candidates)

        master_gate_status = self.results.get(
            "regen_candidate_population_master_gate_status",
            self.results.get("regen_population_master_gate_status", "UNKNOWN"),
        )

        ranking_allowed = self.results.get(
            "regen_candidate_ranking_architecture_allowed",
            self.results.get("phase_11b_4_candidate_ranking_architecture_allowed", False),
        )

        self.summary_label.setText(
            f"Population count: {population_count} | "
            f"Population master gate: {master_gate_status} | "
            f"Ranking architecture allowed: {ranking_allowed} | "
            "Read-only inspector"
        )

        self.results["regen_candidate_population_inspector_opened"] = True
        self.results["regen_candidate_population_inspector_candidate_count"] = population_count
        self.results["regen_candidate_population_inspector_status"] = (
            "PASS_REGEN_CANDIDATE_POPULATION_INSPECTOR_POST16G"
            if population_count > 0 else
            "WARN_REGEN_CANDIDATE_POPULATION_INSPECTOR_NO_CANDIDATES_POST16G"
        )

    def populate_table(self):
        self.table.setRowCount(len(self.candidates))

        for row, candidate in enumerate(self.candidates):
            summary = build_candidate_summary(candidate)
            values = [
                summary["candidate_id"],
                summary["generation"],
                summary["parent"],
                summary["status"],
                summary["channels"],
                summary["width"],
                summary["height"],
                summary["rib"],
                summary["wall"],
                summary["coolant_fraction"],
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
                "No candidate population is available yet.\n\n"
                "Run regen solve / candidate generation first."
            )

    def refresh(self):
        self.candidates = get_candidate_population(self.results)
        self.populate_table()
        self.update_summary()

    def selected_candidate(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.candidates):
            return None
        return self.candidates[row]

    def on_selection_changed(self):
        candidate = self.selected_candidate()
        self.details.setPlainText(format_candidate_details(candidate))

    def copy_selected_candidate(self):
        candidate = self.selected_candidate()
        text = format_candidate_details(candidate)

        try:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
        except Exception:
            pass


def show_regen_candidate_population_inspector(results=None, parent=None):
    dialog = RegenCandidatePopulationInspector(results=results, parent=parent)
    dialog.exec()
    return dialog
