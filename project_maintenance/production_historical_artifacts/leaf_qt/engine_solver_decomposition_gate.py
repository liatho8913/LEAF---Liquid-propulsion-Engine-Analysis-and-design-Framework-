from __future__ import annotations

import ast
import json
import py_compile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

PUBLIC_SOLVER_CONTRACT = "solve_engine"

DEFAULT_SOURCE = Path("leaf_qt/engine_solver.py")
DEFAULT_OUTPUT_JSON = Path("artifacts/phase_16w1_engine_solver_first_extraction_gate.json")
DEFAULT_OUTPUT_TXT = Path("artifacts/phase_16w1_engine_solver_first_extraction_gate.txt")
DEFAULT_DRY_RUN_ROOT = Path("artifacts/phase_16w2_engine_solver_first_extraction_dry_run")
DEFAULT_DRY_RUN_JSON = Path("artifacts/phase_16w2_engine_solver_first_extraction_dry_run.json")
DEFAULT_DRY_RUN_TXT = Path("artifacts/phase_16w2_engine_solver_first_extraction_dry_run.txt")
DEFAULT_EXTRACTED_HELPERS = Path("leaf_qt/engine_solver_extracted_helpers.py")
DEFAULT_APPLY_JSON = Path("artifacts/phase_16w3_engine_solver_first_extraction_apply_gate.json")
DEFAULT_APPLY_TXT = Path("artifacts/phase_16w3_engine_solver_first_extraction_apply_gate.txt")
DEFAULT_REGRESSION_JSON = Path("artifacts/phase_16w4_engine_solver_post_extraction_regression_gate.json")
DEFAULT_REGRESSION_TXT = Path("artifacts/phase_16w4_engine_solver_post_extraction_regression_gate.txt")
DEFAULT_EXTRACTION_REGISTRY = Path("artifacts/engine_solver_extraction_registry.json")
DEFAULT_REGISTRY_JSON = Path("artifacts/phase_16w5_engine_solver_extraction_registry.json")
DEFAULT_REGISTRY_TXT = Path("artifacts/phase_16w5_engine_solver_extraction_registry.txt")
DEFAULT_REGISTRY_AUDIT_JSON = Path("artifacts/phase_16w6_engine_solver_extraction_registry_audit.json")
DEFAULT_REGISTRY_AUDIT_TXT = Path("artifacts/phase_16w6_engine_solver_extraction_registry_audit.txt")
DEFAULT_EXTRACTION_CLOSEOUT_JSON = Path("artifacts/phase_16w7_engine_solver_extraction_closeout_certificate.json")
DEFAULT_EXTRACTION_CLOSEOUT_TXT = Path("artifacts/phase_16w7_engine_solver_extraction_closeout_certificate.txt")
DEFAULT_SECOND_CANDIDATE_JSON = Path("artifacts/phase_16w8_engine_solver_second_extraction_candidate_gate.json")
DEFAULT_SECOND_CANDIDATE_TXT = Path("artifacts/phase_16w8_engine_solver_second_extraction_candidate_gate.txt")
DEFAULT_SECOND_DRY_RUN_ROOT = Path("artifacts/phase_16w9_engine_solver_second_extraction_dry_run")
DEFAULT_SECOND_DRY_RUN_JSON = Path("artifacts/phase_16w9_engine_solver_second_extraction_dry_run.json")
DEFAULT_SECOND_DRY_RUN_TXT = Path("artifacts/phase_16w9_engine_solver_second_extraction_dry_run.txt")
DEFAULT_SECOND_APPLY_JSON = Path("artifacts/phase_16w10_engine_solver_second_extraction_apply_gate.json")
DEFAULT_SECOND_APPLY_TXT = Path("artifacts/phase_16w10_engine_solver_second_extraction_apply_gate.txt")
DEFAULT_SECOND_REGISTRY_JSON = Path("artifacts/phase_16w11_engine_solver_second_extraction_regression_registry_gate.json")
DEFAULT_SECOND_REGISTRY_TXT = Path("artifacts/phase_16w11_engine_solver_second_extraction_regression_registry_gate.txt")
DEFAULT_SECOND_CLOSEOUT_JSON = Path("artifacts/phase_16w12_engine_solver_second_extraction_closeout_certificate.json")
DEFAULT_SECOND_CLOSEOUT_TXT = Path("artifacts/phase_16w12_engine_solver_second_extraction_closeout_certificate.txt")


LOW_RISK_NAME_TERMS = {
    "regen",
    "report",
    "nozzle",
    "geometry",
    "performance",
    "validation",
    "material",
    "coolant",
    "thermal",
    "station",
    "area",
    "mach",
    "flow",
}

HIGH_RISK_NAME_TERMS = {
    "solve_engine",
    "main",
    "window",
    "ui",
    "thread",
    "qt",
    "callback",
}


@dataclass(frozen=True)
class ExtractionCandidate:
    name: str
    kind: str
    lineno: int
    end_lineno: int
    line_count: int
    risk: str
    reason: str


@dataclass(frozen=True)
class EngineSolverFirstExtractionDryRun:
    phase: str
    dry_run_status: str
    generated_at_utc: str
    source_path: str
    candidate_name: str | None
    candidate_kind: str | None
    candidate_line_count: int | None
    dry_run_root: str
    simulated_module_path: str | None
    simulated_engine_solver_path: str | None
    original_compile_passed: bool
    simulated_module_compile_passed: bool
    simulated_engine_solver_compile_passed: bool
    public_contract_present_after_simulation: bool
    live_source_modified: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverFirstExtractionApplyGate:
    phase: str
    apply_status: str
    generated_at_utc: str
    source_path: str
    target_module_path: str
    candidate_name: str | None
    candidate_line_count: int | None
    dry_run_status: str
    backup_path: str | None
    source_compile_passed_after_apply: bool
    target_compile_passed_after_apply: bool
    public_contract_present_after_apply: bool
    extraction_applied: bool
    rollback_required: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverPostExtractionRegressionGate:
    phase: str
    regression_status: str
    generated_at_utc: str
    source_path: str
    helper_module_path: str
    extracted_helper_name: str
    source_compile_passed: bool
    helper_compile_passed: bool
    public_contract_present: bool
    helper_import_present: bool
    helper_definition_removed_from_source: bool
    helper_definition_present_in_module: bool
    helper_probe_passed: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverExtractionRegistryGate:
    phase: str
    registry_status: str
    generated_at_utc: str
    registry_path: str
    registered_extraction_count: int
    latest_extraction: str | None
    public_contract: str
    public_contract_preserved: bool
    helper_module_path: str
    helper_module_exists: bool
    source_path: str
    source_exists: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverExtractionCloseoutCertificate:
    phase: str
    certificate_status: str
    generated_at_utc: str
    public_contract: str
    public_contract_preserved: bool
    registered_extraction_count: int
    latest_extraction: str | None
    source_compile_passed: bool
    helper_compile_passed: bool
    registry_audit_status: str
    certificate_decision: str
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverSecondExtractionCandidateGate:
    phase: str
    gate_status: str
    generated_at_utc: str
    first_closeout_status: str
    registered_extraction_count: int
    already_extracted_helpers: list[str]
    selected_candidate: ExtractionCandidate | None
    candidate_count: int
    low_risk_candidate_count: int
    public_contract_present: bool
    public_contract_move_allowed: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverSecondExtractionDryRun:
    phase: str
    dry_run_status: str
    generated_at_utc: str
    source_path: str
    candidate_name: str | None
    candidate_kind: str | None
    candidate_line_count: int | None
    dry_run_root: str
    simulated_helper_module_path: str | None
    simulated_engine_solver_path: str | None
    second_candidate_gate_status: str
    simulated_helper_compile_passed: bool
    simulated_engine_solver_compile_passed: bool
    public_contract_present_after_simulation: bool
    previous_extractions_preserved: bool
    live_source_modified: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverSecondExtractionApplyGate:
    phase: str
    apply_status: str
    generated_at_utc: str
    source_path: str
    helper_module_path: str
    candidate_name: str | None
    candidate_line_count: int | None
    second_dry_run_status: str
    backup_path: str | None
    source_compile_passed_after_apply: bool
    helper_compile_passed_after_apply: bool
    public_contract_present_after_apply: bool
    previous_extractions_preserved: bool
    extraction_applied: bool
    rollback_required: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverSecondExtractionRegressionRegistryGate:
    phase: str
    gate_status: str
    generated_at_utc: str
    extracted_helper_name: str
    regression_status: str
    registry_update_status: str
    registry_audit_status: str
    registered_extraction_count: int
    public_contract_preserved: bool
    source_compile_passed: bool
    helper_compile_passed: bool
    helper_probe_passed: bool
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverSecondExtractionCloseoutCertificate:
    phase: str
    certificate_status: str
    generated_at_utc: str
    public_contract: str
    public_contract_preserved: bool
    registered_extraction_count: int
    registered_helpers: list[str]
    source_compile_passed: bool
    helper_compile_passed: bool
    second_registry_gate_status: str
    certificate_decision: str
    reasons: list[str]
    next_phase: str


@dataclass(frozen=True)
class EngineSolverFirstExtractionGate:
    phase: str
    gate_status: str
    generated_at_utc: str
    source_path: str
    public_contract: str
    source_exists: bool
    compile_passed: bool
    public_contract_present: bool
    public_contract_lineno: int | None
    public_contract_move_allowed: bool
    candidate_count: int
    low_risk_candidate_count: int
    selected_first_extraction: ExtractionCandidate | None
    candidates: list[ExtractionCandidate]
    reasons: list[str]
    next_phase: str


def _node_line_count(node: ast.AST) -> int:
    lineno = getattr(node, "lineno", 0) or 0
    end_lineno = getattr(node, "end_lineno", lineno) or lineno
    return max(1, end_lineno - lineno + 1)


def _risk_for_name(name: str, line_count: int) -> tuple[str, str]:
    lower = name.lower()

    if lower == PUBLIC_SOLVER_CONTRACT:
        return "BOUNDARY_LOCKED", "Public solver contract must not be moved in the first extraction."

    if any(term in lower for term in HIGH_RISK_NAME_TERMS):
        return "HIGH", "Name indicates public boundary, GUI, callback, or runtime orchestration coupling."

    if line_count > 350:
        return "HIGH", "Candidate is too large for first extraction and needs manual review."

    if line_count > 180:
        return "MEDIUM", "Candidate is moderately large and should not be first extraction."

    if any(term in lower for term in LOW_RISK_NAME_TERMS):
        return "LOW", "Name suggests reusable internal engineering domain suitable for controlled extraction."

    if lower.startswith("_") and line_count <= 120:
        return "LOW", "Private helper with limited size."

    return "MEDIUM", "No strong low-risk signal; keep for later review."


def analyse_engine_solver_decomposition_readiness(
    source_path: str | Path = DEFAULT_SOURCE,
) -> EngineSolverFirstExtractionGate:
    source = Path(source_path)
    reasons: list[str] = []

    source_exists = source.exists()
    compile_passed = False
    public_contract_present = False
    public_contract_lineno: int | None = None
    candidates: list[ExtractionCandidate] = []

    if not source_exists:
        return EngineSolverFirstExtractionGate(
            phase="16W.1",
            gate_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            public_contract=PUBLIC_SOLVER_CONTRACT,
            source_exists=False,
            compile_passed=False,
            public_contract_present=False,
            public_contract_lineno=None,
            public_contract_move_allowed=False,
            candidate_count=0,
            low_risk_candidate_count=0,
            selected_first_extraction=None,
            candidates=[],
            reasons=[f"Source file not found: {source}"],
            next_phase="BLOCKED_UNTIL_ENGINE_SOLVER_SOURCE_EXISTS",
        )

    try:
        py_compile.compile(str(source), doraise=True)
        compile_passed = True
        reasons.append("engine_solver.py compiles successfully.")
    except Exception as exc:
        reasons.append(f"engine_solver.py compile failed: {exc}")

    try:
        tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        return EngineSolverFirstExtractionGate(
            phase="16W.1",
            gate_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            public_contract=PUBLIC_SOLVER_CONTRACT,
            source_exists=True,
            compile_passed=compile_passed,
            public_contract_present=False,
            public_contract_lineno=None,
            public_contract_move_allowed=False,
            candidate_count=0,
            low_risk_candidate_count=0,
            selected_first_extraction=None,
            candidates=[],
            reasons=reasons + [f"AST parse failed: {exc}"],
            next_phase="BLOCKED_UNTIL_ENGINE_SOLVER_AST_PARSE_PASSES",
        )

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            line_count = _node_line_count(node)

            if name == PUBLIC_SOLVER_CONTRACT and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                public_contract_present = True
                public_contract_lineno = getattr(node, "lineno", None)

            risk, reason = _risk_for_name(name, line_count)

            candidates.append(
                ExtractionCandidate(
                    name=name,
                    kind=type(node).__name__,
                    lineno=getattr(node, "lineno", 0) or 0,
                    end_lineno=getattr(node, "end_lineno", getattr(node, "lineno", 0)) or 0,
                    line_count=line_count,
                    risk=risk,
                    reason=reason,
                )
            )

    low_risk = [
        c for c in candidates
        if c.risk == "LOW" and c.name != PUBLIC_SOLVER_CONTRACT
    ]

    selected = sorted(low_risk, key=lambda c: (c.line_count, c.lineno))[0] if low_risk else None

    if public_contract_present:
        reasons.append(f"Public contract {PUBLIC_SOLVER_CONTRACT} is present and locked.")
    else:
        reasons.append(f"Public contract {PUBLIC_SOLVER_CONTRACT} was not found.")

    if selected:
        reasons.append(
            f"Selected first extraction candidate: {selected.name} "
            f"({selected.line_count} lines, line {selected.lineno})."
        )
    else:
        reasons.append("No low-risk first extraction candidate was identified.")

    if compile_passed and public_contract_present and selected:
        status = PASS
        next_phase = "16W.2_ENGINE_SOLVER_FIRST_EXTRACTION_DRY_RUN"
    elif compile_passed and public_contract_present:
        status = WARN
        next_phase = "16W.1B_EXTRACTION_CANDIDATE_CLASSIFICATION_REPAIR"
    else:
        status = FAIL
        next_phase = "BLOCKED_UNTIL_PUBLIC_CONTRACT_AND_COMPILE_PASS"

    return EngineSolverFirstExtractionGate(
        phase="16W.1",
        gate_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source_path=str(source),
        public_contract=PUBLIC_SOLVER_CONTRACT,
        source_exists=source_exists,
        compile_passed=compile_passed,
        public_contract_present=public_contract_present,
        public_contract_lineno=public_contract_lineno,
        public_contract_move_allowed=False,
        candidate_count=len(candidates),
        low_risk_candidate_count=len(low_risk),
        selected_first_extraction=selected,
        candidates=candidates,
        reasons=reasons,
        next_phase=next_phase,
    )




def _find_top_level_node_by_name(tree: ast.Module, name: str) -> ast.AST | None:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return node
    return None


def _replace_line_range_with_import(
    source_text: str,
    node: ast.AST,
    import_line: str,
) -> str:
    lines = source_text.splitlines()
    start = (getattr(node, "lineno", 1) or 1) - 1
    end = getattr(node, "end_lineno", getattr(node, "lineno", 1)) or 1

    before = lines[:start]
    after = lines[end:]

    insertion = [
        import_line,
        "",
        f"# Phase 16W.2 dry-run placeholder: extracted {getattr(node, 'name', 'UNKNOWN')} above.",
    ]

    return "\n".join(before + insertion + after) + "\n"


def simulate_engine_solver_first_extraction_dry_run(
    source_path: str | Path = DEFAULT_SOURCE,
    dry_run_root: str | Path = DEFAULT_DRY_RUN_ROOT,
) -> EngineSolverFirstExtractionDryRun:
    source = Path(source_path)
    dry_root = Path(dry_run_root)
    dry_root.mkdir(parents=True, exist_ok=True)

    gate = analyse_engine_solver_decomposition_readiness(source)
    reasons: list[str] = list(gate.reasons)

    if gate.gate_status != PASS or gate.selected_first_extraction is None:
        reasons.append("Dry run refused because first extraction gate is not PASS.")
        return EngineSolverFirstExtractionDryRun(
            phase="16W.2",
            dry_run_status=WARN if gate.gate_status == WARN else FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            candidate_name=None,
            candidate_kind=None,
            candidate_line_count=None,
            dry_run_root=str(dry_root),
            simulated_module_path=None,
            simulated_engine_solver_path=None,
            original_compile_passed=gate.compile_passed,
            simulated_module_compile_passed=False,
            simulated_engine_solver_compile_passed=False,
            public_contract_present_after_simulation=False,
            live_source_modified=False,
            reasons=reasons,
            next_phase="BLOCKED_UNTIL_16W1_GATE_PASS",
        )

    candidate = gate.selected_first_extraction

    original_text = source.read_text(encoding="utf-8", errors="replace")
    original_hash_before = source.read_bytes()

    tree = ast.parse(original_text)
    node = _find_top_level_node_by_name(tree, candidate.name)

    if node is None:
        reasons.append(f"Selected candidate {candidate.name} could not be found in AST.")
        return EngineSolverFirstExtractionDryRun(
            phase="16W.2",
            dry_run_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            candidate_name=candidate.name,
            candidate_kind=candidate.kind,
            candidate_line_count=candidate.line_count,
            dry_run_root=str(dry_root),
            simulated_module_path=None,
            simulated_engine_solver_path=None,
            original_compile_passed=gate.compile_passed,
            simulated_module_compile_passed=False,
            simulated_engine_solver_compile_passed=False,
            public_contract_present_after_simulation=False,
            live_source_modified=False,
            reasons=reasons,
            next_phase="BLOCKED_SELECTED_CANDIDATE_NOT_FOUND",
        )

    segment = ast.get_source_segment(original_text, node)
    if segment:
        segment = segment.replace("\\n", "\n")

    if not segment:
        reasons.append(f"Source segment for {candidate.name} could not be extracted.")
        return EngineSolverFirstExtractionDryRun(
            phase="16W.2",
            dry_run_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            candidate_name=candidate.name,
            candidate_kind=candidate.kind,
            candidate_line_count=candidate.line_count,
            dry_run_root=str(dry_root),
            simulated_module_path=None,
            simulated_engine_solver_path=None,
            original_compile_passed=gate.compile_passed,
            simulated_module_compile_passed=False,
            simulated_engine_solver_compile_passed=False,
            public_contract_present_after_simulation=False,
            live_source_modified=False,
            reasons=reasons,
            next_phase="BLOCKED_SOURCE_SEGMENT_EXTRACTION_FAILED",
        )

    module_name = "engine_solver_extracted_helpers_phase_16w2"
    simulated_module = dry_root / f"{module_name}.py"
    simulated_solver = dry_root / "engine_solver_simulated.py"

    simulated_module.write_text(
        "from __future__ import annotations\n\n"
        "# Phase 16W.2 dry-run extraction module.\n"
        "# This file is generated evidence only and is not runtime-authoritative.\n\n"
        + segment
        + "\n",
        encoding="utf-8",
    )

    simulated_solver_text = _replace_line_range_with_import(
        original_text,
        node,
        f"from {module_name} import {candidate.name}",
    )
    simulated_solver.write_text(simulated_solver_text, encoding="utf-8")

    module_compile = False
    solver_compile = False
    public_contract_after = False

    try:
        py_compile.compile(str(simulated_module), doraise=True)
        module_compile = True
        reasons.append("Simulated extracted helper module compiles.")
    except Exception as exc:
        reasons.append(f"Simulated extracted helper module compile failed: {exc}")

    try:
        py_compile.compile(str(simulated_solver), doraise=True)
        solver_compile = True
        reasons.append("Simulated engine_solver after extraction compiles.")
    except Exception as exc:
        reasons.append(f"Simulated engine_solver after extraction compile failed: {exc}")

    try:
        simulated_tree = ast.parse(simulated_solver.read_text(encoding="utf-8", errors="replace"))
        public_contract_after = _find_top_level_node_by_name(simulated_tree, PUBLIC_SOLVER_CONTRACT) is not None
    except Exception:
        public_contract_after = False

    live_source_modified = source.read_bytes() != original_hash_before

    if public_contract_after:
        reasons.append("Public solve_engine contract remains present after simulation.")
    else:
        reasons.append("Public solve_engine contract missing after simulation.")

    if not live_source_modified:
        reasons.append("Live engine_solver.py was not modified by dry run.")
    else:
        reasons.append("Live engine_solver.py was unexpectedly modified.")

    if module_compile and solver_compile and public_contract_after and not live_source_modified:
        status = PASS
        next_phase = "16W.3_ENGINE_SOLVER_FIRST_EXTRACTION_APPLY_GATE"
    else:
        status = FAIL
        next_phase = "BLOCKED_UNTIL_DRY_RUN_COMPILES_AND_CONTRACT_SURVIVES"

    return EngineSolverFirstExtractionDryRun(
        phase="16W.2",
        dry_run_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source_path=str(source),
        candidate_name=candidate.name,
        candidate_kind=candidate.kind,
        candidate_line_count=candidate.line_count,
        dry_run_root=str(dry_root),
        simulated_module_path=str(simulated_module),
        simulated_engine_solver_path=str(simulated_solver),
        original_compile_passed=gate.compile_passed,
        simulated_module_compile_passed=module_compile,
        simulated_engine_solver_compile_passed=solver_compile,
        public_contract_present_after_simulation=public_contract_after,
        live_source_modified=live_source_modified,
        reasons=reasons,
        next_phase=next_phase,
    )




def _ensure_import_not_duplicate(source_text: str, import_line: str) -> str:
    if import_line in source_text:
        return source_text

    lines = source_text.splitlines()
    insert_at = 0

    if lines and lines[0].startswith("#!"):
        insert_at = 1

    while insert_at < len(lines) and (
        lines[insert_at].strip() == ""
        or lines[insert_at].startswith("#")
        or lines[insert_at].startswith("from __future__")
    ):
        insert_at += 1

    lines.insert(insert_at, import_line)
    return "\n".join(lines) + "\n"


def apply_engine_solver_first_extraction(
    source_path: str | Path = DEFAULT_SOURCE,
    target_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    backup_suffix: str = ".phase_16w3_first_extraction_backup",
) -> EngineSolverFirstExtractionApplyGate:
    source = Path(source_path)
    target = Path(target_module_path)
    reasons: list[str] = []

    dry_run = simulate_engine_solver_first_extraction_dry_run(source)

    if dry_run.dry_run_status != PASS or not dry_run.candidate_name:
        reasons.append("Apply refused because 16W.2 dry run did not PASS.")
        return EngineSolverFirstExtractionApplyGate(
            phase="16W.3",
            apply_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            target_module_path=str(target),
            candidate_name=dry_run.candidate_name,
            candidate_line_count=dry_run.candidate_line_count,
            dry_run_status=dry_run.dry_run_status,
            backup_path=None,
            source_compile_passed_after_apply=False,
            target_compile_passed_after_apply=False,
            public_contract_present_after_apply=False,
            extraction_applied=False,
            rollback_required=False,
            reasons=reasons + dry_run.reasons,
            next_phase="BLOCKED_UNTIL_16W2_DRY_RUN_PASS",
        )

    original_text = source.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(original_text)
    node = _find_top_level_node_by_name(tree, dry_run.candidate_name)

    if node is None:
        reasons.append(f"Candidate {dry_run.candidate_name} was not found in live source.")
        return EngineSolverFirstExtractionApplyGate(
            phase="16W.3",
            apply_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            target_module_path=str(target),
            candidate_name=dry_run.candidate_name,
            candidate_line_count=dry_run.candidate_line_count,
            dry_run_status=dry_run.dry_run_status,
            backup_path=None,
            source_compile_passed_after_apply=False,
            target_compile_passed_after_apply=False,
            public_contract_present_after_apply=False,
            extraction_applied=False,
            rollback_required=False,
            reasons=reasons,
            next_phase="BLOCKED_SELECTED_CANDIDATE_NOT_FOUND_IN_LIVE_SOURCE",
        )

    segment = ast.get_source_segment(original_text, node)
    if segment:
        segment = segment.replace("\\n", "\n")

    if not segment:
        reasons.append(f"Source segment for {dry_run.candidate_name} could not be extracted.")
        return EngineSolverFirstExtractionApplyGate(
            phase="16W.3",
            apply_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            target_module_path=str(target),
            candidate_name=dry_run.candidate_name,
            candidate_line_count=dry_run.candidate_line_count,
            dry_run_status=dry_run.dry_run_status,
            backup_path=None,
            source_compile_passed_after_apply=False,
            target_compile_passed_after_apply=False,
            public_contract_present_after_apply=False,
            extraction_applied=False,
            rollback_required=False,
            reasons=reasons,
            next_phase="BLOCKED_SOURCE_SEGMENT_EXTRACTION_FAILED",
        )

    backup = source.with_name(source.name + backup_suffix)
    backup.write_text(original_text, encoding="utf-8")
    reasons.append(f"Rollback backup written: {backup}")

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        target_text = target.read_text(encoding="utf-8", errors="replace")
    else:
        target_text = (
            "from __future__ import annotations\n\n"
            '"""Reusable helpers extracted from engine_solver.py.\n\n'
            "This module is runtime-authoritative only for helpers explicitly imported by engine_solver.py.\n"
            "The public solver boundary remains solve_engine().\n"
            '"""\n\n'
        )

    if f"def {dry_run.candidate_name}(" not in target_text:
        target_text = target_text.rstrip() + "\n\n\n" + segment.strip() + "\n"
        reasons.append(f"Candidate appended to helper module: {target}")
    else:
        reasons.append(f"Candidate already present in helper module: {target}")

    target.write_text(target_text, encoding="utf-8")

    import_line = f"from engine_solver_extracted_helpers import {dry_run.candidate_name}"
    transformed = _replace_line_range_with_import(
        original_text,
        node,
        f"# Phase 16W.3 extraction: {dry_run.candidate_name} moved to engine_solver_extracted_helpers.py",
    )

    transformed = _ensure_import_not_duplicate(transformed, import_line)
    source.write_text(transformed, encoding="utf-8")

    source_compile = False
    target_compile = False
    public_contract_after = False
    rollback_required = False

    try:
        py_compile.compile(str(target), doraise=True)
        target_compile = True
        reasons.append("Extracted helper module compiles after apply.")
    except Exception as exc:
        reasons.append(f"Extracted helper module compile failed after apply: {exc}")

    try:
        py_compile.compile(str(source), doraise=True)
        source_compile = True
        reasons.append("engine_solver.py compiles after apply.")
    except Exception as exc:
        reasons.append(f"engine_solver.py compile failed after apply: {exc}")

    try:
        post_tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
        public_contract_after = _find_top_level_node_by_name(post_tree, PUBLIC_SOLVER_CONTRACT) is not None
    except Exception:
        public_contract_after = False

    if public_contract_after:
        reasons.append("Public solve_engine contract remains present after apply.")
    else:
        reasons.append("Public solve_engine contract missing after apply.")

    if source_compile and target_compile and public_contract_after:
        status = PASS
        next_phase = "16W.4_ENGINE_SOLVER_POST_EXTRACTION_REGRESSION_GATE"
        extraction_applied = True
    else:
        status = FAIL
        next_phase = "ROLLBACK_REQUIRED_BEFORE_CONTINUING"
        extraction_applied = False
        rollback_required = True
        source.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
        reasons.append("Apply failed safety checks; live engine_solver.py rolled back from backup.")

    return EngineSolverFirstExtractionApplyGate(
        phase="16W.3",
        apply_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source_path=str(source),
        target_module_path=str(target),
        candidate_name=dry_run.candidate_name,
        candidate_line_count=dry_run.candidate_line_count,
        dry_run_status=dry_run.dry_run_status,
        backup_path=str(backup),
        source_compile_passed_after_apply=source_compile,
        target_compile_passed_after_apply=target_compile,
        public_contract_present_after_apply=public_contract_after,
        extraction_applied=extraction_applied,
        rollback_required=rollback_required,
        reasons=reasons,
        next_phase=next_phase,
    )




def evaluate_engine_solver_post_extraction_regression(
    source_path: str | Path = DEFAULT_SOURCE,
    helper_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    helper_name: str = "calculate_selected_station_length_default",
) -> EngineSolverPostExtractionRegressionGate:
    source = Path(source_path)
    helper = Path(helper_module_path)
    reasons: list[str] = []

    source_compile = False
    helper_compile = False
    public_contract_present = False
    helper_import_present = False
    helper_removed_from_source = False
    helper_present_in_module = False
    helper_probe_passed = False

    if not source.exists():
        reasons.append(f"Source file missing: {source}")

    if not helper.exists():
        reasons.append(f"Helper module missing: {helper}")

    if source.exists():
        try:
            py_compile.compile(str(source), doraise=True)
            source_compile = True
            reasons.append("engine_solver.py compiles after extraction.")
        except Exception as exc:
            reasons.append(f"engine_solver.py compile failed after extraction: {exc}")

        source_text = source.read_text(encoding="utf-8", errors="replace")
        helper_import_present = f"from engine_solver_extracted_helpers import {helper_name}" in source_text
        helper_removed_from_source = f"def {helper_name}(" not in source_text

        try:
            tree = ast.parse(source_text)
            public_contract_present = _find_top_level_node_by_name(tree, PUBLIC_SOLVER_CONTRACT) is not None
        except Exception as exc:
            reasons.append(f"engine_solver.py AST parse failed during regression: {exc}")

    if helper.exists():
        try:
            py_compile.compile(str(helper), doraise=True)
            helper_compile = True
            reasons.append("engine_solver_extracted_helpers.py compiles.")
        except Exception as exc:
            reasons.append(f"engine_solver_extracted_helpers.py compile failed: {exc}")

        helper_text = helper.read_text(encoding="utf-8", errors="replace")
        helper_present_in_module = f"def {helper_name}(" in helper_text

    if public_contract_present:
        reasons.append("Public solve_engine contract remains present.")
    else:
        reasons.append("Public solve_engine contract is missing.")

    if helper_import_present:
        reasons.append("engine_solver.py imports the extracted helper.")
    else:
        reasons.append("engine_solver.py does not import the extracted helper.")

    if helper_removed_from_source:
        reasons.append("Extracted helper definition has been removed from engine_solver.py.")
    else:
        reasons.append("Extracted helper definition still exists in engine_solver.py.")

    if helper_present_in_module:
        reasons.append("Extracted helper definition exists in helper module.")
    else:
        reasons.append("Extracted helper definition missing from helper module.")

    try:
        import sys
        import importlib

        helper_parent = str(helper.parent.resolve())
        if helper_parent not in sys.path:
            sys.path.insert(0, helper_parent)

        module_name = helper.stem
        if module_name in sys.modules:
            del sys.modules[module_name]

        module = importlib.import_module(module_name)
        fn = getattr(module, helper_name)
        probe_value = fn(3.5)
        helper_probe_passed = probe_value == 3.5
        if helper_probe_passed:
            reasons.append("Extracted helper behavioural probe passed.")
        else:
            reasons.append(f"Extracted helper behavioural probe returned unexpected value: {probe_value!r}")
    except Exception as exc:
        reasons.append(f"Extracted helper behavioural probe failed: {exc}")

    checks = [
        source_compile,
        helper_compile,
        public_contract_present,
        helper_import_present,
        helper_removed_from_source,
        helper_present_in_module,
        helper_probe_passed,
    ]

    if all(checks):
        status = PASS
        next_phase = "16W.5_ENGINE_SOLVER_EXTRACTION_REGISTRY"
    else:
        status = FAIL
        next_phase = "BLOCKED_UNTIL_POST_EXTRACTION_REGRESSION_PASS"

    return EngineSolverPostExtractionRegressionGate(
        phase="16W.4",
        regression_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source_path=str(source),
        helper_module_path=str(helper),
        extracted_helper_name=helper_name,
        source_compile_passed=source_compile,
        helper_compile_passed=helper_compile,
        public_contract_present=public_contract_present,
        helper_import_present=helper_import_present,
        helper_definition_removed_from_source=helper_removed_from_source,
        helper_definition_present_in_module=helper_present_in_module,
        helper_probe_passed=helper_probe_passed,
        reasons=reasons,
        next_phase=next_phase,
    )




def update_engine_solver_extraction_registry(
    regression: EngineSolverPostExtractionRegressionGate,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
) -> EngineSolverExtractionRegistryGate:
    registry_path = Path(registry_path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            registry = {}
    else:
        registry = {}

    extractions = registry.get("extractions", {})
    helper_name = regression.extracted_helper_name

    reasons: list[str] = []

    if regression.regression_status != PASS:
        reasons.append("Registry update refused because post-extraction regression is not PASS.")
        status = FAIL
    else:
        extractions[helper_name] = {
            "helper_name": helper_name,
            "source_path": regression.source_path,
            "helper_module_path": regression.helper_module_path,
            "registered_at_utc": datetime.now(timezone.utc).isoformat(),
            "phase_registered": "16W.5",
            "source_compile_passed": regression.source_compile_passed,
            "helper_compile_passed": regression.helper_compile_passed,
            "public_contract_present": regression.public_contract_present,
            "helper_import_present": regression.helper_import_present,
            "helper_definition_removed_from_source": regression.helper_definition_removed_from_source,
            "helper_definition_present_in_module": regression.helper_definition_present_in_module,
            "helper_probe_passed": regression.helper_probe_passed,
            "status": regression.regression_status,
        }

        registry = {
            "registry_schema": "LEAF_ENGINE_SOLVER_EXTRACTION_REGISTRY_V1",
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "public_contract": PUBLIC_SOLVER_CONTRACT,
            "public_contract_move_allowed": False,
            "registered_extraction_count": len(extractions),
            "extractions": dict(sorted(extractions.items())),
        }

        registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
        reasons.append(f"Extraction registered: {helper_name}")
        status = PASS

    source = Path(regression.source_path)
    helper = Path(regression.helper_module_path)

    return EngineSolverExtractionRegistryGate(
        phase="16W.5",
        registry_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        registry_path=str(registry_path),
        registered_extraction_count=len(extractions),
        latest_extraction=helper_name if status == PASS else None,
        public_contract=PUBLIC_SOLVER_CONTRACT,
        public_contract_preserved=regression.public_contract_present,
        helper_module_path=str(helper),
        helper_module_exists=helper.exists(),
        source_path=str(source),
        source_exists=source.exists(),
        reasons=reasons,
        next_phase="16W.6_ENGINE_SOLVER_EXTRACTION_REGISTRY_AUDIT" if status == PASS else "BLOCKED_UNTIL_REGRESSION_PASS",
    )


def audit_engine_solver_extraction_registry(
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
) -> EngineSolverExtractionRegistryGate:
    registry_path = Path(registry_path)
    reasons: list[str] = []

    if not registry_path.exists():
        return EngineSolverExtractionRegistryGate(
            phase="16W.6",
            registry_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            registry_path=str(registry_path),
            registered_extraction_count=0,
            latest_extraction=None,
            public_contract=PUBLIC_SOLVER_CONTRACT,
            public_contract_preserved=False,
            helper_module_path=str(DEFAULT_EXTRACTED_HELPERS),
            helper_module_exists=DEFAULT_EXTRACTED_HELPERS.exists(),
            source_path=str(DEFAULT_SOURCE),
            source_exists=DEFAULT_SOURCE.exists(),
            reasons=["Extraction registry does not exist."],
            next_phase="BLOCKED_UNTIL_EXTRACTION_REGISTRY_EXISTS",
        )

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return EngineSolverExtractionRegistryGate(
            phase="16W.6",
            registry_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            registry_path=str(registry_path),
            registered_extraction_count=0,
            latest_extraction=None,
            public_contract=PUBLIC_SOLVER_CONTRACT,
            public_contract_preserved=False,
            helper_module_path=str(DEFAULT_EXTRACTED_HELPERS),
            helper_module_exists=DEFAULT_EXTRACTED_HELPERS.exists(),
            source_path=str(DEFAULT_SOURCE),
            source_exists=DEFAULT_SOURCE.exists(),
            reasons=[f"Extraction registry parse failed: {exc}"],
            next_phase="BLOCKED_UNTIL_EXTRACTION_REGISTRY_PARSE_PASS",
        )

    extractions = registry.get("extractions", {})
    public_contract_preserved = registry.get("public_contract") == PUBLIC_SOLVER_CONTRACT

    if registry.get("registry_schema") != "LEAF_ENGINE_SOLVER_EXTRACTION_REGISTRY_V1":
        reasons.append("Registry schema is missing or unsupported.")

    if not public_contract_preserved:
        reasons.append("Registry does not preserve solve_engine as public contract.")
    else:
        reasons.append("Registry preserves solve_engine as public contract.")

    if not extractions:
        reasons.append("No solver extractions are registered.")

    all_live_checks_pass = True
    latest = sorted(extractions.keys())[-1] if extractions else None

    for name, entry in sorted(extractions.items()):
        entry_reasons: list[str] = []

        source = Path(entry.get("source_path", DEFAULT_SOURCE))
        helper = Path(entry.get("helper_module_path", DEFAULT_EXTRACTED_HELPERS))

        if entry.get("status") != PASS:
            entry_reasons.append("registered status is not PASS")

        if not entry.get("public_contract_present"):
            entry_reasons.append("registered public contract flag is false")

        if not entry.get("helper_probe_passed"):
            entry_reasons.append("registered helper probe flag is false")

        if not source.exists():
            entry_reasons.append(f"source file missing: {source}")
        else:
            source_text = source.read_text(encoding="utf-8", errors="replace")
            if f"from engine_solver_extracted_helpers import {name}" not in source_text:
                entry_reasons.append("live source import is missing")
            if f"def {name}(" in source_text:
                entry_reasons.append("helper definition still exists in live source")
            try:
                tree = ast.parse(source_text)
                if _find_top_level_node_by_name(tree, PUBLIC_SOLVER_CONTRACT) is None:
                    entry_reasons.append("solve_engine missing from live source")
            except Exception as exc:
                entry_reasons.append(f"live source AST parse failed: {exc}")

        if not helper.exists():
            entry_reasons.append(f"helper module missing: {helper}")
        else:
            helper_text = helper.read_text(encoding="utf-8", errors="replace")
            if f"def {name}(" not in helper_text:
                entry_reasons.append("helper definition missing from helper module")

        try:
            py_compile.compile(str(source), doraise=True)
        except Exception as exc:
            entry_reasons.append(f"source compile failed: {exc}")

        try:
            py_compile.compile(str(helper), doraise=True)
        except Exception as exc:
            entry_reasons.append(f"helper compile failed: {exc}")

        if entry_reasons:
            all_live_checks_pass = False
            reasons.append(f"{name}: " + "; ".join(entry_reasons))
        else:
            reasons.append(f"{name}: live extraction audit passed.")

    helper_module = DEFAULT_EXTRACTED_HELPERS
    source_file = DEFAULT_SOURCE

    status = PASS if extractions and public_contract_preserved and all_live_checks_pass else FAIL

    return EngineSolverExtractionRegistryGate(
        phase="16W.6",
        registry_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        registry_path=str(registry_path),
        registered_extraction_count=len(extractions),
        latest_extraction=latest,
        public_contract=PUBLIC_SOLVER_CONTRACT,
        public_contract_preserved=public_contract_preserved,
        helper_module_path=str(helper_module),
        helper_module_exists=helper_module.exists(),
        source_path=str(source_file),
        source_exists=source_file.exists(),
        reasons=reasons,
        next_phase="16W.7_ENGINE_SOLVER_EXTRACTION_CLOSEOUT_CERTIFICATE" if status == PASS else "BLOCKED_UNTIL_EXTRACTION_REGISTRY_AUDIT_PASS",
    )




def generate_engine_solver_extraction_closeout_certificate(
    source_path: str | Path = DEFAULT_SOURCE,
    helper_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
) -> EngineSolverExtractionCloseoutCertificate:
    source = Path(source_path)
    helper = Path(helper_module_path)
    reasons: list[str] = []

    source_compile = False
    helper_compile = False

    try:
        py_compile.compile(str(source), doraise=True)
        source_compile = True
        reasons.append("engine_solver.py compiles.")
    except Exception as exc:
        reasons.append(f"engine_solver.py compile failed: {exc}")

    try:
        py_compile.compile(str(helper), doraise=True)
        helper_compile = True
        reasons.append("engine_solver_extracted_helpers.py compiles.")
    except Exception as exc:
        reasons.append(f"engine_solver_extracted_helpers.py compile failed: {exc}")

    registry_audit = audit_engine_solver_extraction_registry(registry_path=registry_path)

    if registry_audit.registry_status == PASS:
        reasons.append("Extraction registry audit is PASS.")
    else:
        reasons.append(f"Extraction registry audit is {registry_audit.registry_status}.")

    checks = [
        source_compile,
        helper_compile,
        registry_audit.registry_status == PASS,
        registry_audit.public_contract_preserved,
        registry_audit.registered_extraction_count >= 1,
    ]

    if all(checks):
        status = PASS
        decision = "FIRST_ENGINE_SOLVER_EXTRACTION_COMPLETE"
        next_phase = "16W.8_ENGINE_SOLVER_SECOND_EXTRACTION_CANDIDATE_GATE"
        reasons.append("First controlled engine solver extraction is complete.")
    else:
        status = FAIL
        decision = "FIRST_ENGINE_SOLVER_EXTRACTION_REQUIRES_REVIEW"
        next_phase = "BLOCKED_UNTIL_FIRST_EXTRACTION_CLOSEOUT_PASS"
        reasons.append("First controlled engine solver extraction is not ready for closeout.")

    return EngineSolverExtractionCloseoutCertificate(
        phase="16W.7",
        certificate_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        public_contract=PUBLIC_SOLVER_CONTRACT,
        public_contract_preserved=registry_audit.public_contract_preserved,
        registered_extraction_count=registry_audit.registered_extraction_count,
        latest_extraction=registry_audit.latest_extraction,
        source_compile_passed=source_compile,
        helper_compile_passed=helper_compile,
        registry_audit_status=registry_audit.registry_status,
        certificate_decision=decision,
        reasons=reasons,
        next_phase=next_phase,
    )




def evaluate_engine_solver_second_extraction_candidate_gate(
    source_path: str | Path = DEFAULT_SOURCE,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
) -> EngineSolverSecondExtractionCandidateGate:
    source = Path(source_path)
    registry_path = Path(registry_path)

    reasons: list[str] = []

    closeout = generate_engine_solver_extraction_closeout_certificate(
        source_path=source,
        helper_module_path=DEFAULT_EXTRACTED_HELPERS,
        registry_path=registry_path,
    )

    gate = analyse_engine_solver_decomposition_readiness(source)

    already_extracted: list[str] = []
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            already_extracted = sorted(registry.get("extractions", {}).keys())
        except Exception as exc:
            reasons.append(f"Could not read extraction registry: {exc}")

    if closeout.certificate_status != PASS:
        reasons.append("Second extraction candidate selection refused because first closeout is not PASS.")
        status = FAIL
        selected = None
        next_phase = "BLOCKED_UNTIL_FIRST_EXTRACTION_CLOSEOUT_PASS"
    else:
        eligible = [
            candidate for candidate in gate.candidates
            if candidate.risk == "LOW"
            and candidate.name != PUBLIC_SOLVER_CONTRACT
            and candidate.name not in already_extracted
        ]

        selected = sorted(eligible, key=lambda c: (c.line_count, c.lineno))[0] if eligible else None

        if selected:
            status = PASS
            reasons.append(
                f"Second extraction candidate selected: {selected.name} "
                f"({selected.line_count} lines, line {selected.lineno})."
            )
            next_phase = "16W.9_ENGINE_SOLVER_SECOND_EXTRACTION_DRY_RUN"
        else:
            status = WARN
            reasons.append("No eligible second extraction candidate found.")
            next_phase = "16W.8B_SECOND_EXTRACTION_CANDIDATE_CLASSIFICATION_REVIEW"

    reasons.extend(closeout.reasons)

    return EngineSolverSecondExtractionCandidateGate(
        phase="16W.8",
        gate_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        first_closeout_status=closeout.certificate_status,
        registered_extraction_count=closeout.registered_extraction_count,
        already_extracted_helpers=already_extracted,
        selected_candidate=selected,
        candidate_count=gate.candidate_count,
        low_risk_candidate_count=gate.low_risk_candidate_count,
        public_contract_present=gate.public_contract_present,
        public_contract_move_allowed=False,
        reasons=reasons,
        next_phase=next_phase,
    )




def simulate_engine_solver_second_extraction_dry_run(
    source_path: str | Path = DEFAULT_SOURCE,
    helper_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
    dry_run_root: str | Path = DEFAULT_SECOND_DRY_RUN_ROOT,
) -> EngineSolverSecondExtractionDryRun:
    source = Path(source_path)
    helper = Path(helper_module_path)
    registry_path = Path(registry_path)
    dry_root = Path(dry_run_root)
    dry_root.mkdir(parents=True, exist_ok=True)

    gate = evaluate_engine_solver_second_extraction_candidate_gate(
        source_path=source,
        registry_path=registry_path,
    )

    reasons: list[str] = list(gate.reasons)

    if gate.gate_status != PASS or gate.selected_candidate is None:
        reasons.append("Second extraction dry run refused because 16W.8 candidate gate is not PASS.")
        return EngineSolverSecondExtractionDryRun(
            phase="16W.9",
            dry_run_status=WARN if gate.gate_status == WARN else FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            candidate_name=None,
            candidate_kind=None,
            candidate_line_count=None,
            dry_run_root=str(dry_root),
            simulated_helper_module_path=None,
            simulated_engine_solver_path=None,
            second_candidate_gate_status=gate.gate_status,
            simulated_helper_compile_passed=False,
            simulated_engine_solver_compile_passed=False,
            public_contract_present_after_simulation=False,
            previous_extractions_preserved=False,
            live_source_modified=False,
            reasons=reasons,
            next_phase="BLOCKED_UNTIL_16W8_SECOND_CANDIDATE_GATE_PASS",
        )

    candidate = gate.selected_candidate
    original_source_bytes = source.read_bytes()
    original_text = source.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(original_text)
    node = _find_top_level_node_by_name(tree, candidate.name)

    if node is None:
        reasons.append(f"Selected second candidate {candidate.name} could not be found in AST.")
        return EngineSolverSecondExtractionDryRun(
            phase="16W.9",
            dry_run_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            candidate_name=candidate.name,
            candidate_kind=candidate.kind,
            candidate_line_count=candidate.line_count,
            dry_run_root=str(dry_root),
            simulated_helper_module_path=None,
            simulated_engine_solver_path=None,
            second_candidate_gate_status=gate.gate_status,
            simulated_helper_compile_passed=False,
            simulated_engine_solver_compile_passed=False,
            public_contract_present_after_simulation=False,
            previous_extractions_preserved=False,
            live_source_modified=False,
            reasons=reasons,
            next_phase="BLOCKED_SECOND_CANDIDATE_NOT_FOUND",
        )

    segment = ast.get_source_segment(original_text, node)
    if segment:
        segment = segment.replace("\\n", "\n")

    if not segment:
        reasons.append(f"Source segment for {candidate.name} could not be extracted.")
        return EngineSolverSecondExtractionDryRun(
            phase="16W.9",
            dry_run_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            candidate_name=candidate.name,
            candidate_kind=candidate.kind,
            candidate_line_count=candidate.line_count,
            dry_run_root=str(dry_root),
            simulated_helper_module_path=None,
            simulated_engine_solver_path=None,
            second_candidate_gate_status=gate.gate_status,
            simulated_helper_compile_passed=False,
            simulated_engine_solver_compile_passed=False,
            public_contract_present_after_simulation=False,
            previous_extractions_preserved=False,
            live_source_modified=False,
            reasons=reasons,
            next_phase="BLOCKED_SECOND_SOURCE_SEGMENT_EXTRACTION_FAILED",
        )

    simulated_helper = dry_root / "engine_solver_extracted_helpers_simulated.py"
    simulated_solver = dry_root / "engine_solver_simulated.py"

    helper_text = ""
    if helper.exists():
        helper_text = helper.read_text(encoding="utf-8", errors="replace")
    else:
        helper_text = (
            "from __future__ import annotations\n\n"
            '"""Simulated extracted helper module."""\n\n'
        )

    if f"def {candidate.name}(" not in helper_text:
        helper_text = helper_text.rstrip() + "\n\n\n" + segment.strip() + "\n"

    simulated_helper.write_text(helper_text, encoding="utf-8")

    replacement_comment = (
        f"# Phase 16W.9 dry-run extraction: {candidate.name} "
        "would move to engine_solver_extracted_helpers.py"
    )
    simulated_solver_text = _replace_line_range_with_import(original_text, node, replacement_comment)

    import_line = f"from engine_solver_extracted_helpers import {candidate.name}"
    simulated_solver_text = _ensure_import_not_duplicate(simulated_solver_text, import_line)
    simulated_solver.write_text(simulated_solver_text, encoding="utf-8")

    helper_compile = False
    solver_compile = False
    public_contract_after = False
    previous_preserved = True

    try:
        py_compile.compile(str(simulated_helper), doraise=True)
        helper_compile = True
        reasons.append("Simulated helper module with second extraction compiles.")
    except Exception as exc:
        reasons.append(f"Simulated helper module compile failed: {exc}")

    try:
        py_compile.compile(str(simulated_solver), doraise=True)
        solver_compile = True
        reasons.append("Simulated engine_solver.py with second extraction compiles.")
    except Exception as exc:
        reasons.append(f"Simulated engine_solver.py compile failed: {exc}")

    try:
        simulated_tree = ast.parse(simulated_solver.read_text(encoding="utf-8", errors="replace"))
        public_contract_after = _find_top_level_node_by_name(simulated_tree, PUBLIC_SOLVER_CONTRACT) is not None
    except Exception:
        public_contract_after = False

    for extracted in gate.already_extracted_helpers:
        if f"from engine_solver_extracted_helpers import {extracted}" not in simulated_solver_text:
            previous_preserved = False
            reasons.append(f"Previously extracted helper import missing after simulation: {extracted}")
        if f"def {extracted}(" not in helper_text:
            previous_preserved = False
            reasons.append(f"Previously extracted helper definition missing from simulated helper module: {extracted}")

    if public_contract_after:
        reasons.append("Public solve_engine contract remains present after second extraction simulation.")
    else:
        reasons.append("Public solve_engine contract missing after second extraction simulation.")

    if previous_preserved:
        reasons.append("Previously registered extractions remain preserved in simulation.")

    live_modified = source.read_bytes() != original_source_bytes

    if not live_modified:
        reasons.append("Live engine_solver.py was not modified by second dry run.")
    else:
        reasons.append("Live engine_solver.py was unexpectedly modified by second dry run.")

    if helper_compile and solver_compile and public_contract_after and previous_preserved and not live_modified:
        status = PASS
        next_phase = "16W.10_ENGINE_SOLVER_SECOND_EXTRACTION_APPLY_GATE"
    else:
        status = FAIL
        next_phase = "BLOCKED_UNTIL_SECOND_DRY_RUN_PASS"

    return EngineSolverSecondExtractionDryRun(
        phase="16W.9",
        dry_run_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source_path=str(source),
        candidate_name=candidate.name,
        candidate_kind=candidate.kind,
        candidate_line_count=candidate.line_count,
        dry_run_root=str(dry_root),
        simulated_helper_module_path=str(simulated_helper),
        simulated_engine_solver_path=str(simulated_solver),
        second_candidate_gate_status=gate.gate_status,
        simulated_helper_compile_passed=helper_compile,
        simulated_engine_solver_compile_passed=solver_compile,
        public_contract_present_after_simulation=public_contract_after,
        previous_extractions_preserved=previous_preserved,
        live_source_modified=live_modified,
        reasons=reasons,
        next_phase=next_phase,
    )




def apply_engine_solver_second_extraction(
    source_path: str | Path = DEFAULT_SOURCE,
    helper_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
    backup_suffix: str = ".phase_16w10_second_extraction_backup",
) -> EngineSolverSecondExtractionApplyGate:
    source = Path(source_path)
    helper = Path(helper_module_path)
    registry_path = Path(registry_path)

    dry_run = simulate_engine_solver_second_extraction_dry_run(
        source_path=source,
        helper_module_path=helper,
        registry_path=registry_path,
    )

    reasons: list[str] = list(dry_run.reasons)

    if dry_run.dry_run_status != PASS or not dry_run.candidate_name:
        reasons.append("Second extraction apply refused because 16W.9 dry run did not PASS.")
        return EngineSolverSecondExtractionApplyGate(
            phase="16W.10",
            apply_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            helper_module_path=str(helper),
            candidate_name=dry_run.candidate_name,
            candidate_line_count=dry_run.candidate_line_count,
            second_dry_run_status=dry_run.dry_run_status,
            backup_path=None,
            source_compile_passed_after_apply=False,
            helper_compile_passed_after_apply=False,
            public_contract_present_after_apply=False,
            previous_extractions_preserved=False,
            extraction_applied=False,
            rollback_required=False,
            reasons=reasons,
            next_phase="BLOCKED_UNTIL_16W9_DRY_RUN_PASS",
        )

    original_source = source.read_text(encoding="utf-8", errors="replace")
    original_helper = helper.read_text(encoding="utf-8", errors="replace") if helper.exists() else ""

    tree = ast.parse(original_source)
    node = _find_top_level_node_by_name(tree, dry_run.candidate_name)

    if node is None:
        reasons.append(f"Candidate {dry_run.candidate_name} was not found in live source.")
        return EngineSolverSecondExtractionApplyGate(
            phase="16W.10",
            apply_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            helper_module_path=str(helper),
            candidate_name=dry_run.candidate_name,
            candidate_line_count=dry_run.candidate_line_count,
            second_dry_run_status=dry_run.dry_run_status,
            backup_path=None,
            source_compile_passed_after_apply=False,
            helper_compile_passed_after_apply=False,
            public_contract_present_after_apply=False,
            previous_extractions_preserved=False,
            extraction_applied=False,
            rollback_required=False,
            reasons=reasons,
            next_phase="BLOCKED_SECOND_CANDIDATE_NOT_FOUND_IN_LIVE_SOURCE",
        )

    segment = ast.get_source_segment(original_source, node)
    if segment:
        segment = segment.replace("\\n", "\n")

    if segment:
        # Some legacy generated code may contain literal backslash-n tokens.
        # Sanitise extracted helper segments before moving them into the helper module.
        segment = segment.replace("\\n", "\n")

    if not segment:
        reasons.append(f"Source segment for {dry_run.candidate_name} could not be extracted.")
        return EngineSolverSecondExtractionApplyGate(
            phase="16W.10",
            apply_status=FAIL,
            generated_at_utc=datetime.now(timezone.utc).isoformat(),
            source_path=str(source),
            helper_module_path=str(helper),
            candidate_name=dry_run.candidate_name,
            candidate_line_count=dry_run.candidate_line_count,
            second_dry_run_status=dry_run.dry_run_status,
            backup_path=None,
            source_compile_passed_after_apply=False,
            helper_compile_passed_after_apply=False,
            public_contract_present_after_apply=False,
            previous_extractions_preserved=False,
            extraction_applied=False,
            rollback_required=False,
            reasons=reasons,
            next_phase="BLOCKED_SECOND_SOURCE_SEGMENT_EXTRACTION_FAILED",
        )

    backup = source.with_name(source.name + backup_suffix)
    backup.write_text(original_source, encoding="utf-8")
    reasons.append(f"Rollback backup written: {backup}")

    helper.parent.mkdir(parents=True, exist_ok=True)

    helper_text = original_helper
    if not helper_text:
        helper_text = (
            "from __future__ import annotations\n\n"
            '"""Reusable helpers extracted from engine_solver.py."""\n\n'
        )

    if f"def {dry_run.candidate_name}(" not in helper_text:
        helper_text = helper_text.rstrip() + "\n\n\n" + segment.strip() + "\\n"
        reasons.append(f"Second candidate appended to helper module: {helper}")
    else:
        reasons.append(f"Second candidate already present in helper module: {helper}")

    transformed = _replace_line_range_with_import(
        original_source,
        node,
        f"# Phase 16W.10 extraction: {dry_run.candidate_name} moved to engine_solver_extracted_helpers.py",
    )

    import_line = f"from engine_solver_extracted_helpers import {dry_run.candidate_name}"
    transformed = _ensure_import_not_duplicate(transformed, import_line)

    # Final safety normalisation before writing generated helper content.
    # Only normalise helper_text. Do NOT normalise the whole transformed
    # engine_solver.py because escaped newlines may legitimately exist inside strings.
    helper_text = helper_text.replace("\\n", "\n")

    helper.write_text(helper_text, encoding="utf-8")
    source.write_text(transformed, encoding="utf-8")

    source_compile = False
    helper_compile = False
    public_contract_after = False
    previous_preserved = True
    rollback_required = False

    try:
        py_compile.compile(str(helper), doraise=True)
        helper_compile = True
        reasons.append("Helper module compiles after second extraction.")
    except Exception as exc:
        reasons.append(f"Helper module compile failed after second extraction: {exc}")

    try:
        py_compile.compile(str(source), doraise=True)
        source_compile = True
        reasons.append("engine_solver.py compiles after second extraction.")
    except Exception as exc:
        reasons.append(f"engine_solver.py compile failed after second extraction: {exc}")

    try:
        post_tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
        public_contract_after = _find_top_level_node_by_name(post_tree, PUBLIC_SOLVER_CONTRACT) is not None
    except Exception:
        public_contract_after = False

    source_text = source.read_text(encoding="utf-8", errors="replace")
    helper_text_after = helper.read_text(encoding="utf-8", errors="replace")

    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            for extracted in registry.get("extractions", {}).keys():
                if f"from engine_solver_extracted_helpers import {extracted}" not in source_text:
                    previous_preserved = False
                    reasons.append(f"Previously extracted helper import missing after second apply: {extracted}")
                if f"def {extracted}(" not in helper_text_after:
                    previous_preserved = False
                    reasons.append(f"Previously extracted helper definition missing after second apply: {extracted}")
        except Exception as exc:
            previous_preserved = False
            reasons.append(f"Could not verify previous extractions from registry: {exc}")

    if public_contract_after:
        reasons.append("Public solve_engine contract remains present after second apply.")
    else:
        reasons.append("Public solve_engine contract missing after second apply.")

    if previous_preserved:
        reasons.append("Previous extractions remain preserved after second apply.")

    if source_compile and helper_compile and public_contract_after and previous_preserved:
        status = PASS
        extraction_applied = True
        next_phase = "16W.11_ENGINE_SOLVER_SECOND_EXTRACTION_REGRESSION_AND_REGISTRY_GATE"
    else:
        status = FAIL
        extraction_applied = False
        rollback_required = True
        source.write_text(original_source, encoding="utf-8")
        helper.write_text(original_helper, encoding="utf-8")
        reasons.append("Second apply failed safety checks; source and helper module rolled back.")
        next_phase = "ROLLBACK_REQUIRED_BEFORE_CONTINUING"

    return EngineSolverSecondExtractionApplyGate(
        phase="16W.10",
        apply_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        source_path=str(source),
        helper_module_path=str(helper),
        candidate_name=dry_run.candidate_name,
        candidate_line_count=dry_run.candidate_line_count,
        second_dry_run_status=dry_run.dry_run_status,
        backup_path=str(backup),
        source_compile_passed_after_apply=source_compile,
        helper_compile_passed_after_apply=helper_compile,
        public_contract_present_after_apply=public_contract_after,
        previous_extractions_preserved=previous_preserved,
        extraction_applied=extraction_applied,
        rollback_required=rollback_required,
        reasons=reasons,
        next_phase=next_phase,
    )




def evaluate_engine_solver_second_extraction_regression_registry_gate(
    source_path: str | Path = DEFAULT_SOURCE,
    helper_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
    helper_name: str = "calculate_coolant_flow_fraction_default",
) -> EngineSolverSecondExtractionRegressionRegistryGate:
    reasons: list[str] = []

    regression = evaluate_engine_solver_post_extraction_regression(
        source_path=source_path,
        helper_module_path=helper_module_path,
        helper_name=helper_name,
    )

    reasons.extend(regression.reasons)

    registry_update = update_engine_solver_extraction_registry(
        regression,
        registry_path=registry_path,
    )

    reasons.extend(registry_update.reasons)

    registry_audit = audit_engine_solver_extraction_registry(registry_path=registry_path)
    reasons.extend(registry_audit.reasons)

    checks = [
        regression.regression_status == PASS,
        registry_update.registry_status == PASS,
        registry_audit.registry_status == PASS,
        registry_audit.public_contract_preserved,
        registry_audit.registered_extraction_count >= 2,
    ]

    if all(checks):
        status = PASS
        next_phase = "16W.12_ENGINE_SOLVER_SECOND_EXTRACTION_CLOSEOUT_CERTIFICATE"
        reasons.append("Second extraction regression, registry update, and registry audit all passed.")
    else:
        status = FAIL
        next_phase = "BLOCKED_UNTIL_SECOND_EXTRACTION_REGRESSION_REGISTRY_PASS"
        reasons.append("Second extraction regression/registry gate failed.")

    return EngineSolverSecondExtractionRegressionRegistryGate(
        phase="16W.11",
        gate_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        extracted_helper_name=helper_name,
        regression_status=regression.regression_status,
        registry_update_status=registry_update.registry_status,
        registry_audit_status=registry_audit.registry_status,
        registered_extraction_count=registry_audit.registered_extraction_count,
        public_contract_preserved=registry_audit.public_contract_preserved,
        source_compile_passed=regression.source_compile_passed,
        helper_compile_passed=regression.helper_compile_passed,
        helper_probe_passed=regression.helper_probe_passed,
        reasons=reasons,
        next_phase=next_phase,
    )


def write_engine_solver_second_extraction_regression_registry_report(
    gate: EngineSolverSecondExtractionRegressionRegistryGate,
    output_json: str | Path = DEFAULT_SECOND_REGISTRY_JSON,
    output_txt: str | Path = DEFAULT_SECOND_REGISTRY_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.11",
        "ENGINE SOLVER SECOND EXTRACTION REGRESSION + REGISTRY GATE",
        "=" * 65,
        f"status={gate.gate_status}",
        f"helper={gate.extracted_helper_name}",
        f"regression_status={gate.regression_status}",
        f"registry_update_status={gate.registry_update_status}",
        f"registry_audit_status={gate.registry_audit_status}",
        f"registered_extraction_count={gate.registered_extraction_count}",
        f"public_contract_preserved={gate.public_contract_preserved}",
        f"source_compile_passed={gate.source_compile_passed}",
        f"helper_compile_passed={gate.helper_compile_passed}",
        f"helper_probe_passed={gate.helper_probe_passed}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in gate.reasons)

    output_txt.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_second_extraction_apply_report(
    gate: EngineSolverSecondExtractionApplyGate,
    output_json: str | Path = DEFAULT_SECOND_APPLY_JSON,
    output_txt: str | Path = DEFAULT_SECOND_APPLY_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.10",
        "ENGINE SOLVER SECOND EXTRACTION APPLY GATE",
        "=" * 49,
        f"status={gate.apply_status}",
        f"candidate={gate.candidate_name}",
        f"candidate_line_count={gate.candidate_line_count}",
        f"second_dry_run_status={gate.second_dry_run_status}",
        f"source={gate.source_path}",
        f"helper_module={gate.helper_module_path}",
        f"backup={gate.backup_path}",
        f"source_compile_passed_after_apply={gate.source_compile_passed_after_apply}",
        f"helper_compile_passed_after_apply={gate.helper_compile_passed_after_apply}",
        f"public_contract_present_after_apply={gate.public_contract_present_after_apply}",
        f"previous_extractions_preserved={gate.previous_extractions_preserved}",
        f"extraction_applied={gate.extraction_applied}",
        f"rollback_required={gate.rollback_required}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in gate.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_second_extraction_dry_run_report(
    dry_run: EngineSolverSecondExtractionDryRun,
    output_json: str | Path = DEFAULT_SECOND_DRY_RUN_JSON,
    output_txt: str | Path = DEFAULT_SECOND_DRY_RUN_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(dry_run), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.9",
        "ENGINE SOLVER SECOND EXTRACTION DRY RUN",
        "=" * 46,
        f"status={dry_run.dry_run_status}",
        f"candidate={dry_run.candidate_name}",
        f"candidate_kind={dry_run.candidate_kind}",
        f"candidate_line_count={dry_run.candidate_line_count}",
        f"second_candidate_gate_status={dry_run.second_candidate_gate_status}",
        f"simulated_helper_module={dry_run.simulated_helper_module_path}",
        f"simulated_engine_solver={dry_run.simulated_engine_solver_path}",
        f"simulated_helper_compile_passed={dry_run.simulated_helper_compile_passed}",
        f"simulated_engine_solver_compile_passed={dry_run.simulated_engine_solver_compile_passed}",
        f"public_contract_present_after_simulation={dry_run.public_contract_present_after_simulation}",
        f"previous_extractions_preserved={dry_run.previous_extractions_preserved}",
        f"live_source_modified={dry_run.live_source_modified}",
        f"next_phase={dry_run.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in dry_run.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_second_extraction_candidate_report(
    gate: EngineSolverSecondExtractionCandidateGate,
    output_json: str | Path = DEFAULT_SECOND_CANDIDATE_JSON,
    output_txt: str | Path = DEFAULT_SECOND_CANDIDATE_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.8",
        "ENGINE SOLVER SECOND EXTRACTION CANDIDATE GATE",
        "=" * 55,
        f"status={gate.gate_status}",
        f"first_closeout_status={gate.first_closeout_status}",
        f"registered_extraction_count={gate.registered_extraction_count}",
        f"already_extracted_helpers={gate.already_extracted_helpers}",
        f"selected_candidate={gate.selected_candidate.name if gate.selected_candidate else None}",
        f"candidate_count={gate.candidate_count}",
        f"low_risk_candidate_count={gate.low_risk_candidate_count}",
        f"public_contract_present={gate.public_contract_present}",
        f"public_contract_move_allowed={gate.public_contract_move_allowed}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in gate.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_extraction_closeout_certificate(
    certificate: EngineSolverExtractionCloseoutCertificate,
    output_json: str | Path = DEFAULT_EXTRACTION_CLOSEOUT_JSON,
    output_txt: str | Path = DEFAULT_EXTRACTION_CLOSEOUT_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(certificate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.7",
        "ENGINE SOLVER EXTRACTION CLOSEOUT CERTIFICATE",
        "=" * 52,
        f"status={certificate.certificate_status}",
        f"decision={certificate.certificate_decision}",
        f"public_contract={certificate.public_contract}",
        f"public_contract_preserved={certificate.public_contract_preserved}",
        f"registered_extraction_count={certificate.registered_extraction_count}",
        f"latest_extraction={certificate.latest_extraction}",
        f"source_compile_passed={certificate.source_compile_passed}",
        f"helper_compile_passed={certificate.helper_compile_passed}",
        f"registry_audit_status={certificate.registry_audit_status}",
        f"next_phase={certificate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in certificate.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_extraction_registry_report(
    gate: EngineSolverExtractionRegistryGate,
    output_json: str | Path = DEFAULT_REGISTRY_AUDIT_JSON,
    output_txt: str | Path = DEFAULT_REGISTRY_AUDIT_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.6",
        "ENGINE SOLVER EXTRACTION REGISTRY AUDIT",
        "=" * 39,
        f"status={gate.registry_status}",
        f"registry={gate.registry_path}",
        f"registered_extraction_count={gate.registered_extraction_count}",
        f"latest_extraction={gate.latest_extraction}",
        f"public_contract={gate.public_contract}",
        f"public_contract_preserved={gate.public_contract_preserved}",
        f"helper_module_exists={gate.helper_module_exists}",
        f"source_exists={gate.source_exists}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in gate.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_post_extraction_regression_report(
    gate: EngineSolverPostExtractionRegressionGate,
    output_json: str | Path = DEFAULT_REGRESSION_JSON,
    output_txt: str | Path = DEFAULT_REGRESSION_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.4",
        "ENGINE SOLVER POST-EXTRACTION REGRESSION GATE",
        "=" * 55,
        f"status={gate.regression_status}",
        f"source={gate.source_path}",
        f"helper_module={gate.helper_module_path}",
        f"extracted_helper={gate.extracted_helper_name}",
        f"source_compile_passed={gate.source_compile_passed}",
        f"helper_compile_passed={gate.helper_compile_passed}",
        f"public_contract_present={gate.public_contract_present}",
        f"helper_import_present={gate.helper_import_present}",
        f"helper_definition_removed_from_source={gate.helper_definition_removed_from_source}",
        f"helper_definition_present_in_module={gate.helper_definition_present_in_module}",
        f"helper_probe_passed={gate.helper_probe_passed}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in gate.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_first_extraction_apply_report(
    gate: EngineSolverFirstExtractionApplyGate,
    output_json: str | Path = DEFAULT_APPLY_JSON,
    output_txt: str | Path = DEFAULT_APPLY_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(gate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.3",
        "ENGINE SOLVER FIRST EXTRACTION APPLY GATE",
        "=" * 48,
        f"status={gate.apply_status}",
        f"source={gate.source_path}",
        f"target_module={gate.target_module_path}",
        f"candidate={gate.candidate_name}",
        f"candidate_line_count={gate.candidate_line_count}",
        f"dry_run_status={gate.dry_run_status}",
        f"backup={gate.backup_path}",
        f"source_compile_passed_after_apply={gate.source_compile_passed_after_apply}",
        f"target_compile_passed_after_apply={gate.target_compile_passed_after_apply}",
        f"public_contract_present_after_apply={gate.public_contract_present_after_apply}",
        f"extraction_applied={gate.extraction_applied}",
        f"rollback_required={gate.rollback_required}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in gate.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_first_extraction_dry_run_report(
    dry_run: EngineSolverFirstExtractionDryRun,
    output_json: str | Path = DEFAULT_DRY_RUN_JSON,
    output_txt: str | Path = DEFAULT_DRY_RUN_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(dry_run), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.2",
        "ENGINE SOLVER FIRST EXTRACTION DRY RUN",
        "=" * 45,
        f"status={dry_run.dry_run_status}",
        f"source={dry_run.source_path}",
        f"candidate={dry_run.candidate_name}",
        f"candidate_kind={dry_run.candidate_kind}",
        f"candidate_line_count={dry_run.candidate_line_count}",
        f"dry_run_root={dry_run.dry_run_root}",
        f"simulated_module={dry_run.simulated_module_path}",
        f"simulated_engine_solver={dry_run.simulated_engine_solver_path}",
        f"original_compile_passed={dry_run.original_compile_passed}",
        f"simulated_module_compile_passed={dry_run.simulated_module_compile_passed}",
        f"simulated_engine_solver_compile_passed={dry_run.simulated_engine_solver_compile_passed}",
        f"public_contract_present_after_simulation={dry_run.public_contract_present_after_simulation}",
        f"live_source_modified={dry_run.live_source_modified}",
        f"next_phase={dry_run.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in dry_run.reasons)

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_json, output_txt


def write_engine_solver_first_extraction_gate_report(
    gate: EngineSolverFirstExtractionGate,
    output_json: str | Path = DEFAULT_OUTPUT_JSON,
    output_txt: str | Path = DEFAULT_OUTPUT_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(gate)
    output_json.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.1",
        "ENGINE SOLVER CONTROLLED DECOMPOSITION FIRST EXTRACTION GATE",
        "=" * 68,
        f"status={gate.gate_status}",
        f"source={gate.source_path}",
        f"compile_passed={gate.compile_passed}",
        f"public_contract={gate.public_contract}",
        f"public_contract_present={gate.public_contract_present}",
        f"public_contract_lineno={gate.public_contract_lineno}",
        f"public_contract_move_allowed={gate.public_contract_move_allowed}",
        f"candidate_count={gate.candidate_count}",
        f"low_risk_candidate_count={gate.low_risk_candidate_count}",
        f"selected_first_extraction={gate.selected_first_extraction.name if gate.selected_first_extraction else None}",
        f"next_phase={gate.next_phase}",
        "",
        "Reasons:",
    ]

    lines.extend(f"- {reason}" for reason in gate.reasons)

    lines.append("")
    lines.append("Low-risk candidates:")
    for candidate in gate.candidates:
        if candidate.risk == "LOW":
            lines.append(
                f"- {candidate.name} | {candidate.kind} | lines={candidate.line_count} "
                f"| start={candidate.lineno} | reason={candidate.reason}"
            )

    output_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return output_json, output_txt




def generate_engine_solver_second_extraction_closeout_certificate(
    source_path: str | Path = DEFAULT_SOURCE,
    helper_module_path: str | Path = DEFAULT_EXTRACTED_HELPERS,
    registry_path: str | Path = DEFAULT_EXTRACTION_REGISTRY,
) -> EngineSolverSecondExtractionCloseoutCertificate:
    source = Path(source_path)
    helper = Path(helper_module_path)
    registry_path = Path(registry_path)

    reasons: list[str] = []
    source_compile = False
    helper_compile = False
    registered_helpers: list[str] = []

    try:
        py_compile.compile(str(source), doraise=True)
        source_compile = True
        reasons.append("engine_solver.py compiles.")
    except Exception as exc:
        reasons.append(f"engine_solver.py compile failed: {exc}")

    try:
        py_compile.compile(str(helper), doraise=True)
        helper_compile = True
        reasons.append("engine_solver_extracted_helpers.py compiles.")
    except Exception as exc:
        reasons.append(f"engine_solver_extracted_helpers.py compile failed: {exc}")

    second_gate = evaluate_engine_solver_second_extraction_regression_registry_gate(
        source_path=source,
        helper_module_path=helper,
        registry_path=registry_path,
    )
    reasons.extend(second_gate.reasons)

    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registered_helpers = sorted(registry.get("extractions", {}).keys())
        except Exception as exc:
            reasons.append(f"Could not read registered helpers: {exc}")

    required = {
        "calculate_selected_station_length_default",
        "calculate_coolant_flow_fraction_default",
    }
    missing_required = sorted(required - set(registered_helpers))

    if missing_required:
        reasons.append("Required extracted helpers missing from registry: " + ", ".join(missing_required))

    checks = [
        source_compile,
        helper_compile,
        second_gate.gate_status == PASS,
        second_gate.public_contract_preserved,
        second_gate.registered_extraction_count >= 2,
        not missing_required,
    ]

    if all(checks):
        status = PASS
        decision = "SECOND_ENGINE_SOLVER_EXTRACTION_COMPLETE"
        next_phase = "16X.1_REPOSITORY_CLEANUP_INVENTORY_GATE"
        reasons.append("Second controlled engine solver extraction is complete.")
    else:
        status = FAIL
        decision = "SECOND_ENGINE_SOLVER_EXTRACTION_REQUIRES_REVIEW"
        next_phase = "BLOCKED_UNTIL_SECOND_EXTRACTION_CLOSEOUT_PASS"
        reasons.append("Second controlled engine solver extraction is not ready for closeout.")

    return EngineSolverSecondExtractionCloseoutCertificate(
        phase="16W.12",
        certificate_status=status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        public_contract=PUBLIC_SOLVER_CONTRACT,
        public_contract_preserved=second_gate.public_contract_preserved,
        registered_extraction_count=second_gate.registered_extraction_count,
        registered_helpers=registered_helpers,
        source_compile_passed=source_compile,
        helper_compile_passed=helper_compile,
        second_registry_gate_status=second_gate.gate_status,
        certificate_decision=decision,
        reasons=reasons,
        next_phase=next_phase,
    )


def write_engine_solver_second_extraction_closeout_certificate(
    certificate: EngineSolverSecondExtractionCloseoutCertificate,
    output_json: str | Path = DEFAULT_SECOND_CLOSEOUT_JSON,
    output_txt: str | Path = DEFAULT_SECOND_CLOSEOUT_TXT,
) -> tuple[Path, Path]:
    output_json = Path(output_json)
    output_txt = Path(output_txt)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_txt.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(json.dumps(asdict(certificate), indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "LEAF PHASE 16W.12",
        "ENGINE SOLVER SECOND EXTRACTION CLOSEOUT CERTIFICATE",
        "=" * 59,
        f"status={certificate.certificate_status}",
        f"decision={certificate.certificate_decision}",
        f"public_contract={certificate.public_contract}",
        f"public_contract_preserved={certificate.public_contract_preserved}",
        f"registered_extraction_count={certificate.registered_extraction_count}",
        f"registered_helpers={certificate.registered_helpers}",
        f"source_compile_passed={certificate.source_compile_passed}",
        f"helper_compile_passed={certificate.helper_compile_passed}",
        f"second_registry_gate_status={certificate.second_registry_gate_status}",
        f"next_phase={certificate.next_phase}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in certificate.reasons)

    output_txt.write_text("\\n".join(lines) + "\\n", encoding="utf-8")
    return output_json, output_txt


def main() -> int:
    gate = analyse_engine_solver_decomposition_readiness()
    output_json, output_txt = write_engine_solver_first_extraction_gate_report(gate)

    print(f"status={gate.gate_status}")
    print(f"compile_passed={gate.compile_passed}")
    print(f"public_contract_present={gate.public_contract_present}")
    print(f"candidate_count={gate.candidate_count}")
    print(f"low_risk_candidate_count={gate.low_risk_candidate_count}")
    print(
        "selected_first_extraction="
        f"{gate.selected_first_extraction.name if gate.selected_first_extraction else None}"
    )
    print(f"json={output_json}")
    print(f"report={output_txt}")
    print(f"next_phase={gate.next_phase}")

    closeout = generate_engine_solver_second_extraction_closeout_certificate()
    closeout_json, closeout_txt = write_engine_solver_second_extraction_closeout_certificate(closeout)

    print(f"second_closeout_status={closeout.certificate_status}")
    print(f"second_closeout_decision={closeout.certificate_decision}")
    print(f"registered_extraction_count={closeout.registered_extraction_count}")
    print(f"registered_helpers={closeout.registered_helpers}")
    print(f"public_contract_preserved={closeout.public_contract_preserved}")
    print(f"second_closeout_json={closeout_json}")
    print(f"second_closeout_report={closeout_txt}")
    print(f"second_closeout_next_phase={closeout.next_phase}")
    print("PASS_PHASE_16W12_ENGINE_SOLVER_SECOND_EXTRACTION_CLOSEOUT_CERTIFICATE")

    return 0 if closeout.certificate_status in {PASS, WARN} else 1


if __name__ == "__main__":
    raise SystemExit(main())
