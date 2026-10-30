# LEAF CURRENT PROGRAMME HANDOVER

<!-- RDSI_FINAL_CURRENT_STATE -->

## CURRENT AUTHORITATIVE EXECUTION STATE

**Programme:** REGEN DESIGN-SPACE INTELLIGENCE  
**Programme state:** COMPLETE / CLOSED  
**RDSI Feature 1:** COMPLETE  
**RDSI Feature 2:** COMPLETE  
**RDSI Feature 3:** COMPLETE

**Authoritative production source SHA-256:**  
`c0f5355f3dc2221825d36141126d3d4810a1537eaa15100f1f55454e8370588b`

The RDSI programme has completed normal-application runtime acceptance.

Do not create another RDSI implementation or audit phase unless a real
production defect is demonstrated.

### Final accepted capability

LEAF Graph Explorer Regen Analysis now provides:

- currently available numeric LEAF inputs as controlled X variables;
- no unavailable registry-only X variables;
- categorical fuel/oxidizer chemistry context rather than continuous numeric
  sweep axes;
- selectable current Manual Regen geometry;
- selectable real evaluated Automatic/Generated Regen geometries;
- ranked generated designs when qualification produces them;
- Accepted geometry only after genuine acceptance/application;
- fixed selected Regen geometry during a controlled X sweep;
- real solver regeneration for every controlled X point;
- canonical chemistry-aware Mixture Ratio sweep values;
- explicit current selected Regen design marker;
- solver-owned failure state and material/engineering limits;
- no independent Graph Explorer feasibility or qualification physics.

### Final runtime proof

Final controlled-sweep acceptance demonstrated:

- real evaluated Generated Candidate selected;
- 50 requested Mixture Ratio points;
- 50 controlled solver calls;
- 50 unique Mixture Ratio values;
- actual values exactly matched canonical sweep values;
- selected generated Regen geometry fixed for every sweep point;
- one separate current-design marker solve;
- marker X matched the selected baseline;
- marker visible as `Current Selected Regen Design`;
- automatic displayed range matched **1.2 to 3.8**;
- accepted test case produced PASS 0 / FAIL 50 / WARN 0 / UNPROVEN 0;
- 50 hard-infeasible failure regions were presented;
- production source remained unchanged during final acceptance.

The final marker bookkeeping concern was disposed as a **test-harness timing
defect**, not a LEAF production defect. Production already returns and persists
the marker result correctly.

### Architecture / safety state

- Existing Engineering Physics remains authoritative.
- Existing Regen module ownership remains authoritative.
- Existing Module Engine remains authoritative.
- Existing LEAF operating-system owners remain authoritative.
- Graph Explorer remains analysis/presentation only.
- No new solver was added.
- No new persistence owner was added.
- No engineering equations were changed by final RDSI integration.
- No engineering thresholds were changed.
- No qualification logic was weakened.
- Failed generated candidates are selectable for analysis but are not promoted
  to feasible or accepted state.

### Existing module scope

Current demonstrated modules remain:

- `combustion_chamber`
- `nozzle`
- `regen`

Do not invent or document non-existent current modules merely to extend the
roadmap.

### Next authorised action

**POST-RDSI MASTER ROADMAP REVIEW**

Review the Master Roadmap from this completed baseline and deliberately select
the next demonstrator programme.

Until that review is complete:

- do not reopen RDSI;
- do not add new engineering modules by assumption;
- preserve the completed demonstrator foundation;
- continue to prefer existing owners over new systems;
- retain replacement-not-accumulation and single-source-of-truth rules.

---

<!-- POST_RDSI_STABLE_BASELINE -->

## STABLE BASELINE AFTER RDSI

**Active engineering programme:** NONE

**Current state:** completed demonstrator development baseline.

**Production source SHA-256:**  
`c0f5355f3dc2221825d36141126d3d4810a1537eaa15100f1f55454e8370588b`

**Current demonstrated modules:**

- `combustion_chamber`
- `nozzle`
- `regen`

The Design Intelligence Expansion programme is complete.

The Regen Design-Space Intelligence programme is complete.

There is no outstanding RDSI implementation, acceptance, bookkeeping, or
documentation action.

No speculative module or engineering feature is authorised as an automatic
successor.

### Next authorised decision

Select a new programme only when one of the following exists:

- an explicit new engineering requirement;
- a demonstrated production defect;
- a repository-health problem requiring correction;
- a security/platform requirement;
- a deliberately chosen distribution/release target;
- another deliberately authorised improvement to an existing LEAF capability.

Any next programme must first be checked against the LEAF Design Constitution,
the existing-owner model, the current module scope, and replacement-not-
accumulation requirements.

Until then:

**LEAF remains at the stable completed post-RDSI demonstrator baseline.**

<!-- PREINJECTOR_RECONCILIATION_CURRENT_STATE_2026_09_23_START -->

---

# Current Programme State Amendment — 23 September 2026

## Current programme

**MASTER ROADMAP / REQUIREMENTS RECONCILIATION**

The earlier post-RDSI current-state section is retained as historical state,
but it is no longer the current execution checkpoint.

The active pre-injector gate sequence is now governed by the explicit
Pre-Injector Gate Ordering Amendment in `LEAF_MASTER_ROADMAP.md`.

## Completed immediately preceding programme

**FULL THREE-DESIGN RUNTIME REGRESSION — COMPLETE**

Final gate:

`PASS_PREINJECTOR_FULL_THREE_DESIGN_RUNTIME_REGRESSION_R7_COMPLETION_GATE`

The runtime-regression evidence chain established:

- canonical regression operating-point baseline locked;
- six-run normal production runtime certified;
- runtime order `A/B/C/B/A/C`;
- repeated-design input identity exact;
- true engineering result repeatability exact;
- A/B/C engineering states remain distinct;
- apparent R5 state-leak HOLD traced only to incomplete volatile-metadata
  vocabulary;
- physical engineering state leak not confirmed;
- production Python source remained immutable.

## Current reconciliation state

Completed:

- MR1 — Governance & Evidence Discovery: **PASS**
- MR2 — Requirement Ledger Status Reconciliation: **HOLD**
- MR2-H1 — Governance Drift & Stage-1 Authority Diagnosis: **PASS**

MR2-H1 established:

- the original MR2 Stage-1 evidence binding was semantically invalid;
- Stage 1 remains historically complete but strict completion authority is not
  yet rebound;
- the local governance documents had drifted from the permanent ten-stage
  pre-injector ordering;
- all five unresolved requirements remain preserved.

Current authorised phase:

**MR2-H2 — CANONICAL GOVERNANCE AMENDMENT RECOVERY**

After successful governance recovery, the next phase is:

**MR2-R1 — CORRECTED REQUIREMENT LEDGER STATUS RECONCILIATION**

## Current unresolved reconciliation ledger

The following items remain unresolved and must be evidence-traced before the
remaining authorised pre-injector programme set can be released:

1. Stage 7 — REMAINING AUTHORISED PRE-INJECTOR PROGRAMMES
2. `WINDOWS_LINUX_LIVE_SECURITY_CERTIFICATION`
3. `D1048_EXTERNAL_PRIMARY_SOURCE`
4. `D2832_REPEAT_EXTRACTION_VALIDATION`
5. `REV_VALIDATION_PROGRAMME`

Stage 1 additionally requires strict completion-authority rebinding before its
historical-complete status can be converted into evidence-bound completion.

## Injector hard stop

The hard stop remains active:

- `injector_research_complete=False`
- `injector_architecture_authorised=False`
- `injector_solver_implementation_authorised=False`
- `injector_UI_implementation_authorised=False`

No injector architecture, solver, or UI implementation is authorised.

<!-- PREINJECTOR_RECONCILIATION_CURRENT_STATE_2026_09_23_END -->

<!-- PREINJECTOR_MAXIMUM_FIDELITY_CURRENT_STATE_2026_09_30_START -->

# Current Programme State Amendment — 30 September 2026

## Active engineering programme

**PRE-INJECTOR MAXIMUM-FIDELITY QUALIFICATION**

## Reason for programme

Stage-8 Full System Testing and Stage-9 Continuity & Uniformity certification
remain valid for their certified scopes.

They are not interpreted as proof that every engineering model, property source,
geometry approximation and correlation has reached maximum practical real-world
fidelity.

The existing three engineering modules are therefore being requalified before
any injector work proceeds.

## Existing module scope

Current modules only:

- `combustion_chamber`
- `nozzle`
- `regen`

## Injector state

- `injector_research_complete=False`
- `injector_research_authorised=False`
- `injector_architecture_authorised=False`
- `injector_solver_implementation_authorised=False`
- `injector_UI_implementation_authorised=False`
- `injector_production_mutation_authorised=False`
- `injector_hard_stop_remains_active=True`

Stage-10 injector evidence produced before this amendment is historical only.

No injector research, architecture, solver, module, UI or production mutation
is currently authorised.

## Current continuation point

**PFQ-1 — CURRENT ENGINEERING FIDELITY GAP INVENTORY**

PFQ-1 shall inventory current engineering limitations including:

- placeholder and partial-source engineering data;
- unsourced constants and property tables;
- approximate or fallback geometry;
- empirical correlations and their validity domains;
- incomplete canonical geometry ownership;
- unresolved external-validation requirements;
- numerical convergence and sensitivity gaps;
- known cross-platform qualification limitations;
- current module-specific limitations;
- current coupled-system limitations.

PFQ-1 is diagnostic/read-only.

Do not correct production merely because PFQ-1 discovers a limitation.
Classify each finding before authorising repair.

<!-- PREINJECTOR_MAXIMUM_FIDELITY_CURRENT_STATE_2026_09_30_END -->

<!-- PFQ_FULL_INPUT_ENGINE_TESTING_CURRENT_REQUIREMENT_START -->

# Mandatory Full-Input Engine Testing Requirement

The active PRE-INJECTOR MAXIMUM-FIDELITY QUALIFICATION now includes:

**PFQ-FIET — Full-Input Engine Testing & Scale Continuity Qualification**

PFQ-FIET is mandatory before the final maximum-fidelity master gate.

Minimum nominal runtime matrix:

- small atmospheric;
- small vacuum;
- medium atmospheric;
- medium vacuum;
- large atmospheric;
- large vacuum.

Each case must begin from a complete explicit engine input definition and
exercise the full applicable current LEAF calculation path.

Every applicable current module must receive complete, traceable input data and
must expose its canonical outputs.

Automatic geometry generation, module data transfer, complete result capture,
cross-scale continuity, atmospheric/vacuum behaviour, failure classification,
repeatability and state isolation must all be qualified.

PFQ-FIET does not invalidate previously verified subsystem evidence.

Existing evidence shall be reused according to the durable PFQ prior-verification
reuse policy.

Only new end-to-end requirements or deltas are qualified.

No PFQ-FIET engine execution is authorised until the current fidelity programme
reaches the appropriate runtime-testing phase.

Injector hard stop remains active.

<!-- PFQ_FULL_INPUT_ENGINE_TESTING_CURRENT_REQUIREMENT_END -->
