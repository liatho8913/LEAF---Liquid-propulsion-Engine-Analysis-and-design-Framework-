from pathlib import Path

path = Path("leaf_qt/regen_candidate_ranking_inspector.py")
text = path.read_text()

old = '''    for key in (
        "regen_optimisation_recommendation_ranked_candidates",
        "regen_optimisation_selection_ranked_candidates",
        "regen_optimisation_scored_candidates",
        "regen_candidate_ranking_ranked_candidates",
        "ranked_candidates",
    ):'''

new = '''    for key in (
        "regen_candidate_ranking_inspector_ranked_candidates",
        "regen_optimisation_recommendation_ranked_candidates",
        "regen_optimisation_selection_ranked_candidates",
        "regen_optimisation_scored_candidates",
        "regen_candidate_ranking_ranked_candidates",
        "ranked_candidates",
    ):'''

if old not in text:
    raise SystemExit("Could not find ranking source tuple to patch.")

text = text.replace(old, new)

path.write_text(text)
print("PHASE_16J1_RANKING_INSPECTOR_SOURCE_PRIORITY_PATCHED")
