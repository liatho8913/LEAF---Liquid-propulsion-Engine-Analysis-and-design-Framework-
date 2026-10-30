# LEAF MASTER ROADMAP

## Project identity

**LEAF — Liquid Propulsion Engine Analysis and Design Framework**

This document is the canonical long-term strategic roadmap for LEAF.

It records major completed foundations, current strategic state and the next
authorised direction.

Detailed execution state belongs in `LEAF_CURRENT_PROGRAMME_HANDOVER.md`.


# 1. Strategic objective

LEAF is a modular liquid-propulsion engine engineering analysis and design
framework.

The demonstrator strategy is:

- establish trustworthy engineering physics;
- establish scalable ownership and infrastructure;
- establish a true modular engineering system;
- demonstrate those foundations through existing engineering modules;
- freeze completed foundations rather than endlessly expand scope.


# 2. Permanent development direction

LEAF development follows:

**Engineering Physics → Engineering Modules → Module Engine → LEAF Operating System → Repository Architecture**

The project prioritises:

- foundations before features;
- modularity;
- one canonical owner;
- one canonical mechanism;
- replacement rather than accumulation;
- repository simplification;
- engineering-safe validation;
- demonstrator readiness.


# 3. Existing engineering-module scope

The existing Module Engine module scope is:

- `combustion_chamber`
- `nozzle`
- `regen`

No additional engineering module is authorised merely to fill the roadmap.

Future modules require an explicit engineering requirement and deliberate
roadmap amendment.


# 4. Major completed foundation history

## Core engineering and Qt demonstrator foundations — COMPLETE

Established and validated:

- liquid-engine solver integration;
- nozzle geometry and flowfield;
- performance analysis;
- regenerative-cooling analysis;
- station data/reporting;
- Graph Explorer;
- Station Table;
- technical Cross-Section Viewer;
- Qt-only application architecture.


## Workspace, runtime, storage and workflow foundations — COMPLETE

Major programmes established canonical ownership for:

- workspace architecture;
- engineering documents;
- runtime sessions;
- state/event infrastructure;
- undo/redo;
- report routing;
- notifications;
- storage roots and lifecycle;
- workflow registry and readiness;
- runtime workflow integration.


## Engineering module architecture — COMPLETE

The Modular Engine established:

- module definitions;
- module loading;
- module registry;
- contracts;
- verification;
- runtime integration;
- dependency visibility;
- controlled migration from legacy mechanisms.

Existing modules:

- combustion chamber;
- nozzle;
- regen.


## Repository simplification and architectural consolidation — COMPLETE

Major cleanup programmes reduced competing mechanisms, retired legacy
surfaces, consolidated canonical ownership and improved repository
intelligence.

Repository health remains a permanent metric rather than a one-off cleanup
exercise.


## Security foundation — COMPLETE FOR CURRENT DEMONSTRATOR SCOPE

Security work established canonical ownership for:

- security audit events;
- project authorisation;
- project-key custody;
- recovery;
- activation;
- migration security;
- ownership lifecycle;
- principal recovery.

Platform-specific certification remains a release concern only when required
by the target distribution environment.


# 5. Regen Hardening Programme — COMPLETE AND FROZEN

Regen Hardening RH1 through RH10 is complete.

Major outcomes include:

- Regen architecture audit;
- Viewer consolidation;
- automatic-geometry end-to-end repair;
- legacy retirement;
- thermal prerequisite/status consistency;
- state/cache/re-entry validation;
- demonstrator UI cleanup;
- targeted legacy-retirement necessity audit;
- two-session normal-application acceptance;
- Regen Hardening Master Gate.


## Frozen engineering-safe demonstrator result

Canonical accepted demonstration state:

- candidate population: `12`
- evaluated candidates: `12`
- qualified candidates: `0`
- ranked candidates: `0`
- selected candidate: `None`
- application allowed: `False`
- commit ready: `False`
- Viewer geometry source: `manual`
- feasibility status: `REGEN_ONLY_NOT_FEASIBLE`
- wall thermal conductivity: `344.0 W/m·K`
- recommended maximum hot-wall temperature:
  `1530.4909636629407 K`
- recommended absorbed heat:
  `7573.364323944452 W`

This is a successful engineering-safe rejection.

The software demonstrator is ready even though the current baseline geometry
is not Regen-feasible.


## Regen freeze policy

Regen is frozen.

There is no authorised RH11.

Reopen Regen only for:

- a demonstrated defect;
- an explicit new engineering requirement;
- a deliberate architectural amendment.


# 6. Canonical LEAF identity correction — COMPLETE

The obsolete project expansion was replaced in active owners.

Canonical identity:

**LEAF — Liquid Propulsion Engine Analysis and Design Framework**

The normal application title has been runtime-accepted.

Historical evidence containing superseded names remains historical evidence
when it has no active production ownership.


# 7. Current programme

## LEAF Demonstrator Release Completion — COMPLETE AND FROZEN

The authorised LEAF Demonstrator Release Completion is complete.

Accepted production baseline:

`f5dbd366c8b05fdd29d971fba713ca36fa3823c05102b95892ea9029235b12fb`

Production Python files:

`536`

Release acceptance evidence:

- project-wide normal-application acceptance: **PASS**;
- clean demonstrator release-package acceptance: **PASS**;
- canonical Demonstrator Release Completion Gate: **PASS**;
- release blockers: **0**.

Accepted release package:

`LEAF_Demonstrator_v0.5.2-dev.zip`

The released engineering-module scope remains exactly:

- `combustion_chamber`
- `nozzle`
- `regen`

No speculative engineering module was introduced for release completion.

The demonstrator is frozen at this accepted baseline. Existing subsystem
freeze and reopen policies remain in force.


# 8. Current authorised direction

<!-- POST_RDSI_CANONICAL_DIRECTION_STATE -->

## Stable post-RDSI demonstrator baseline

**Active engineering programme:** NONE

**Demonstrator state:** STABLE / COMPLETED CURRENT BASELINE

The previously authorised Design Intelligence Expansion and subsequent
Regen Design-Space Intelligence programme are complete.

LEAF therefore has no automatically implied next engineering programme.

The current demonstrated engineering-module scope remains exactly:

- `combustion_chamber`
- `nozzle`
- `regen`

No additional engineering module is authorised merely to continue development.

A future engineering programme requires:

1. an explicit engineering or product requirement;
2. confirmation that the requirement is not already owned by an existing
   LEAF system;
3. deliberate Master Roadmap authorisation;
4. constitutional ownership review before production mutation.

Until such a requirement exists:

- preserve the completed demonstrator foundation;
- do not reopen RDSI without a real defect or deliberate feature amendment;
- do not create speculative engineering modules;
- prefer maintenance only when a real defect, repository-health issue,
  security requirement, release target, or explicitly authorised improvement
  exists;
- keep the frozen demonstrator release unchanged unless a new release is
  deliberately authorised.

**Next decision point:** explicit engineering requirement or deliberately
authorised product/release target.

# 9. Future development rule

After demonstrator release, new engineering capability begins only from an
explicit engineering requirement.

The Module Engine and foundational architecture must make future modules
progressively easier to integrate without project-wide rewrites.

The Master Roadmap must be amended deliberately when strategic direction
changes.

<!-- LEAF_DESIGN_INTELLIGENCE_EXPANSION_CLOSEOUT_START -->

# Design Intelligence Expansion — COMPLETE

**Completion date:** 2026-08-27

**Programme status:** COMPLETE

**Completion gate:**
`PASS_DESIGN_INTELLIGENCE_EXPANSION_COMPLETION_GATE`

## Programme objective

Extend the completed LEAF demonstrator with a tightly bounded set of
design-intelligence capabilities while preserving the LEAF Design
Constitution, canonical engineering ownership, modularity, truthful
qualification, repository health, and the frozen demonstrator release.

## Completed features

### 1. Full Automatic Design — Geometry + Materials

**Status:** COMPLETE

LEAF can perform a genuine combined geometry/material search using the
existing canonical candidate pipeline:

Candidate Population
→ Candidate Application
→ Candidate Resolve
→ Real Solver Execution
→ Candidate Qualification
→ Qualified Population
→ Ranking

The feature does not treat evaluated or failing candidates as feasible
designs and does not weaken qualification criteria to manufacture PASS.

The full search population is:

- manufacturable geometries: 12
- eligible materials: 14
- combined candidates: 168

A canonical Qt background execution owner prevents the 168-candidate
search from blocking the GUI.

### 2. Mode-Aware Design Status + Honest Geometry Display

**Status:** COMPLETE

Regen design modes are:

- Manual
- Automatic — Selected Material
- Automatic — Geometry + Materials

Automatic modes no longer display Manual geometry as an automatic
fallback.

Canonical automatic presentation states are:

- NOT_GENERATED
- RUNNING
- GENERATED
- NO_FEASIBLE_DESIGN
- ERROR

Manual and Automatic status identities are isolated. A failed automatic
search cannot overwrite the preserved Manual engineering-status state.

### 3. Canonical Failure Guidance

**Status:** COMPLETE

Automatic failure presentation now provides:

- WHAT FAILED
- WHY
- WHAT MIGHT FIX IT

The viewer consumes existing canonical qualification, validation,
explanation, feasibility, and recommendation evidence.

The viewer does not fabricate limits, recommendations, engineering
criteria, or corrective actions.

### 4. Ambient Pressure Presets + Custom Pressure

**Status:** COMPLETE

The existing canonical `ambient_pressure` MANUAL design-choice input was
extended with:

- Vacuum
- Earth Sea Level
- Mars Surface Reference
- Venus Surface Reference
- Mercury Surface Reference
- Custom

Canonical internal pressure representation remains SI pascals.

Reference values:

- Vacuum: 0 Pa
- Earth Sea Level: 101325 Pa
- Mars Surface Reference: 636 Pa
- Venus Surface Reference: 9200000 Pa
- Mercury Surface Reference: 0 Pa engineering reference model

The existing LEAF pressure-unit preference controls display/input
conversion. No independent pressure-unit selector was introduced.

## Final programme acceptance

Normal-application acceptance is complete for Features 1–4.

Production Python files:

`537`

Accepted production source SHA-256:

`0cf7f4feefd438539be6864b3d45e9f30a1aaf364bad767d740cfdb0fe796305`

Frozen demonstrator package:

`/Users/liamthorpe/Downloads/LEAF_Demonstrator_v0.5.2-dev.zip`

Frozen demonstrator SHA-256:

`0b9255524e3e8d617ed2bba785d9ca81ed28212748d622a0b0ff03bf93de156a`

Frozen demonstrator release changed:

`False`

Production parse failures:

`0`

## Constitutional result

The programme preserved:

- Engineering Physics → Engineering Modules → Module Engine →
  LEAF Operating System → Repository Architecture
- Single Source of Truth
- exactly one canonical owner per concept
- One Way
- replacement rather than accumulation
- GUI does not own engineering physics
- infrastructure does not own engineering physics
- foundations before features
- modular/removable engineering modules
- truthful validation and qualification
- no speculative modules
- no false PASS

## Strategic state after completion

**No new development programme is activated by this closeout.**

LEAF returns to a deliberate stable development state.

Any further development must begin with a deliberate amendment to the
LEAF Master Roadmap and must conform to the LEAF Design Constitution.

<!-- LEAF_DESIGN_INTELLIGENCE_EXPANSION_CLOSEOUT_END -->

<!-- LEAF_REGEN_DESIGN_SPACE_INTELLIGENCE_START -->

# REGEN DESIGN-SPACE INTELLIGENCE

<!-- RDSI_FINAL_COMPLETION_CLOSEOUT -->

## RDSI FINAL COMPLETION CLOSEOUT — COMPLETE

**Programme:** Regen Design-Space Intelligence  
**Status:** COMPLETE  
**Final validated production source SHA-256:** `c0f5355f3dc2221825d36141126d3d4810a1537eaa15100f1f55454e8370588b`

RDSI is closed as a completed LEAF demonstrator capability. It must not be
reopened or extended merely for additional audit phases. Re-entry requires a
real production defect or a deliberately authorised future feature.

### Feature completion

1. **Feature 1 — Full thrust-chamber Regen domain**
   - COMPLETE.
   - Existing Regen physics and full thrust-chamber domain remain the
     engineering authority.
   - No replacement solver or parallel Regen physics owner was introduced.

2. **Feature 2 — Persistent Regen candidate evidence**
   - COMPLETE.
   - Existing project/design engineering state remains the persistence owner.
   - No new global cache or competing persistence mechanism was introduced.

3. **Feature 3 — Graph Explorer Regen Analysis**
   - COMPLETE.
   - Normal-application runtime acceptance completed.

### Final Graph Explorer Regen Analysis behaviour

The existing Graph Explorer now supports a controlled Regen design-space
analysis workflow in which:

- X variables come only from currently available numeric LEAF input controls;
- registry-only or unavailable values are not exposed as editable sweep axes;
- `selected_length` and `selected_station_length` are not exposed as current
  X variables when they are not editable controls;
- fuel and oxidizer remain categorical chemistry context rather than numeric
  X variables;
- Manual Regen geometry is materialised from the existing Regen Viewer and is
  selectable;
- all unique actually evaluated Automatic/Generated Regen geometries are
  selectable for analysis;
- qualified/ranked generated geometries remain distinguishable from evaluated
  but non-qualified candidates;
- a generated geometry being selectable does **not** promote it to feasible,
  ranked, recommended, accepted, or applied state;
- Accepted geometry exists in the selector only after genuine LEAF
  acceptance/application;
- Graph Explorer does not generate Regen geometries and does not own Regen
  persistence;
- the selected Regen geometry becomes the fixed baseline for a controlled
  sweep;
- the selected X input alone is varied through the graph state while dependent
  calculated values are regenerated through the existing calculation bridge;
- chemistry-dependent Mixture Ratio sweep bounds reuse the canonical sweep
  owner;
- the current selected Regen design is plotted explicitly as
  **Current Selected Regen Design**;
- solver-owned PASS / FAIL / WARN / UNPROVEN state and solver-owned engineering
  limits remain authoritative;
- Graph Explorer does not create qualification physics or engineering
  thresholds.

### Final runtime acceptance evidence

The final controlled Mixture Ratio acceptance used a real evaluated generated
Regen candidate as the fixed baseline:

- requested controlled-sweep points: **50**;
- actual controlled-sweep solver calls: **50**;
- separate current-design marker solver calls: **1**;
- unique controlled X values: **50**;
- actual sweep values matched the canonical sweep owner;
- Mixture Ratio range: **1.2 to 3.8** for the validated chemistry;
- selected generated Regen geometry remained fixed for every controlled sweep
  point;
- selected generated Regen geometry remained fixed for the current-design
  marker solve;
- current-design marker X matched the selected baseline;
- current-design marker was visible in the graph legend;
- all 50 tested samples were genuine solver-owned FAIL results in the accepted
  test case;
- 50 hard-infeasible failure hatches were shown;
- no PASS was manufactured and no threshold was weakened.

The one apparent final marker-result failure was proven to be a test-harness
timing defect: the marker method returns the result dictionary and the caller
persists that returned dictionary after the wrapped method returns. No
production correction was required.

### Architectural closeout

RDSI preserved the LEAF constitutional ownership hierarchy:

**Engineering Physics → Engineering Modules → Module Engine → LEAF Operating
System → Repository Architecture**

RDSI introduced:

- no new engineering solver;
- no competing Regen qualification owner;
- no new persistence owner;
- no new module architecture;
- no engineering-equation changes;
- no engineering-threshold changes;
- no qualification-logic weakening.

**RDSI programme state:** COMPLETE.

**Next authorised action:** perform the post-RDSI Master Roadmap review and
select the next demonstrator programme deliberately. Do not create a new RDSI
phase merely because RDSI has closed.


**Programme ID:** `REGEN_DESIGN_SPACE_INTELLIGENCE`

**Status:** ACTIVE

**Activated:** 2026-08-27

## Purpose

Extend LEAF's existing regenerative-cooling architecture into a
persistent design-space engineering capability.

The programme builds on the already completed:

- Regen candidate generation;
- candidate resolve and real solver execution;
- canonical qualification;
- Automatic — Selected Material;
- Automatic — Geometry + Materials;
- canonical failure guidance;
- Graph Explorer;
- project/design storage architecture.

No competing candidate, solver, qualification, storage, ranking,
graphing, or engineering-physics architecture is authorised.

---

## Feature 1 — Full Thrust-Chamber Regen Domain

**Status:** ACTIVE

### Objective

Replace the remaining throat-origin/nozzle-centric Regen domain
assumption with one canonical full thrust-chamber hot-wall domain.

Target physical domain:

`injector/chamber head → chamber → convergent → throat → divergent nozzle`

Preferred coordinate convention where compatible:

- chamber upstream of throat: `x < 0`
- throat: `x = 0`
- nozzle downstream of throat: `x > 0`

The programme must reuse or cleanly extend the existing canonical
geometry/axial owners.

A second parallel coordinate or contour system is prohibited.

### Cooling coverage

The complete thrust-chamber contour is the available thermal domain.

This does NOT mean every engine must regeneratively cool the entire
domain.

Cooling coverage must eventually distinguish, where supported:

- regenerative;
- film;
- dump;
- radiation;
- other;
- unmodelled.

No nozzle extension may be falsely classified as regen-cooled merely
because it belongs to the contour.

### Coolant direction

Axial geometric direction and coolant-flow direction are separate
engineering concepts.

Coolant marching direction must be explicit rather than inferred from
increasing axial coordinate.

### Immediate stage

`RDSI_1A_FULL_THRUST_CHAMBER_REGEN_DOMAIN_OWNER_AUDIT`

This stage is READ ONLY.

Before production mutation it must identify:

- chamber contour owner;
- chamber cylindrical-section owner;
- convergent contour owner;
- throat datum owner;
- nozzle contour owner;
- Regen axial-profile owner;
- gas/thermal axial station owner;
- coolant marching owner;
- cooling coverage owner;
- current profile start/end coordinates;
- whether chamber geometry already exists but is disconnected from
  Regen;
- the smallest existing-owner correction required.

---

## Feature 2 — Persistent Regen Candidate Records

**Status:** COMPLETE

Evaluated Regen candidates shall become persistent engineering evidence
associated with the saved LEAF design.

The minimum persistent record should preserve, where available:

- run/candidate/design identity;
- generation mode;
- candidate variables actually changed;
- fixed design requirements;
- selected material;
- key thermal/hydraulic/geometric results;
- PASS / FAIL / UNPROVEN;
- canonical failed constraints;
- qualification margins;
- blockers/source-validation state;
- required axial-profile evidence or reference.

Do not persist hundreds of redundant full solver dictionaries when a
compact canonical analysis record is sufficient.

Candidate persistence must use existing project/design storage
ownership wherever possible.

---

## Feature 3 — Graph Explorer: Regen Analysis — COMPLETE

**Status:** COMPLETE

Extend the existing Graph Explorer.

Do not create another plotting window.

Required capability:

- Regen Analysis mode;
- candidate dataset/mode selector;
- selectable numerical X candidate/input variable;
- selectable numerical Y Regen result metric;
- PASS / FAIL / UNPROVEN points;
- selected canonical constraint analysis;
- canonical threshold/limit overlays where evidence exists.

### Failure-region presentation

Canonically supported infeasible regions may be shown using strongly
visible red diagonal hatching.

However:

**Sparse multivariable candidate scatter MUST NOT automatically be turned
into a continuous infeasible region.**

A failed point proves that evaluated candidate failed.

It does not prove that all unevaluated combinations at the same X value
fail.

Graph Explorer must distinguish:

### Candidate Scatter Evidence

Observed candidate points only.

No unsupported continuous feasibility interpolation.

### Controlled Parameter Sweep Evidence

One selected X variable is deliberately varied while the remaining
controlled design state is held fixed.

The real solver and canonical qualification pipeline are executed.

Only this type of evidence, or another equally authoritative canonical
boundary, may establish explicit feasible/infeasible intervals.

Graph Explorer remains an analysis/presentation owner.

It never owns qualification physics.

---

## Feature 4 — Normal-Application Acceptance + Completion Gate

**Status:** COMPLETE

Completion requires:

- full-domain normal-app acceptance;
- candidate persistence acceptance;
- save/reload persistence proof;
- Graph Explorer Regen Analysis acceptance;
- PASS / FAIL / UNPROVEN correctness;
- failure-region evidence correctness;
- source/repository integrity;
- final programme completion gate.

---

## Locked execution order

1. `FULL_THRUST_CHAMBER_REGEN_DOMAIN`
2. `PERSISTENT_REGEN_CANDIDATE_RECORDS`
3. `GRAPH_EXPLORER_REGEN_ANALYSIS`
4. `NORMAL_APP_ACCEPTANCE_AND_COMPLETION_GATE`

Feature 2 must not begin before Feature 1 closes.

Feature 3 must not begin before candidate persistence has one canonical
owner.

---

## Constitutional constraints

Permanent hierarchy:

**Engineering Physics → Engineering Modules → Module Engine →
LEAF Operating System → Repository Architecture**

Permanent rules remain:

- Single Source of Truth;
- exactly one owner;
- One Way;
- foundations before features;
- replacement rather than accumulation;
- scalability over hardcoding;
- GUI never owns engineering physics;
- infrastructure never owns engineering physics;
- no duplicate candidate pipeline;
- no duplicate validator;
- no duplicate ranker;
- no duplicate graph window;
- no speculative engineering modules;
- no weakened thresholds;
- no false PASS;
- no unsupported feasibility interpolation;
- normal application is authoritative.

---

## Starting baseline

Production Python files:

`537`

Production source SHA-256:

c0f5355f3dc2221825d36141126d3d4810a1537eaa15100f1f55454e8370588b

Frozen demonstrator SHA-256:

`0b9255524e3e8d617ed2bba785d9ca81ed28212748d622a0b0ff03bf93de156a`

Frozen demonstrator remains unchanged.

---

## Next

`RDSI_1A_FULL_THRUST_CHAMBER_REGEN_DOMAIN_OWNER_AUDIT`

<!-- LEAF_REGEN_DESIGN_SPACE_INTELLIGENCE_END -->

<!-- PREINJECTOR_CANONICAL_GATE_ORDERING_AMENDMENT_2026_09_23_START -->

---

# Canonical Pre-Injector Gate Ordering Amendment — 23 September 2026

## Amendment status

**ACTIVE — CUMULATIVE ROADMAP REQUIREMENT**

This amendment restores the permanent pre-injector programme ordering that was
authorised after the earlier demonstrator/RDSI roadmap state.

It does not delete or rewrite historical roadmap sections. Earlier statements
describing the post-RDSI state remain historical evidence of the state that
existed when they were written.

Where an earlier section states that there is no active engineering programme,
or that the next action is merely to select a post-RDSI programme, this
amendment supersedes that statement **only as current programme-state
authority**.

This amendment does not supersede the LEAF Design Constitution.

## Permanent pre-injector ordering

The canonical ordered gate sequence is:

1. **FULL PRE-INJECTOR ENGINEERING QUALIFICATION**
2. **THREE-DESIGN SCALABILITY**
3. **GEOMETRY CONSISTENCY**
4. **2D REGEN VIEWER GEOMETRY FIDELITY**
5. **FULL THREE-DESIGN RUNTIME REGRESSION**
6. **MASTER ROADMAP / REQUIREMENTS RECONCILIATION**
7. **REMAINING AUTHORISED PRE-INJECTOR PROGRAMMES**
8. **FULL SYSTEM TESTING**
9. **LEAF SYSTEM CONTINUITY & UNIFORMITY MASTER GATE**
10. **INJECTOR HARD STOP**

This order is cumulative and must not be silently reordered, compressed,
discarded, or bypassed.

A later roadmap amendment may supersede a requirement only when that
supersession is explicit, deliberate, recorded, and authorised.

## Current gate state

At this amendment checkpoint:

- Stage 1 — FULL PRE-INJECTOR ENGINEERING QUALIFICATION:
  **HISTORICALLY COMPLETE — STRICT COMPLETION AUTHORITY REBIND PENDING**
- Stage 2 — THREE-DESIGN SCALABILITY:
  **COMPLETE**
- Stage 3 — GEOMETRY CONSISTENCY:
  **COMPLETE**
- Stage 4 — 2D REGEN VIEWER GEOMETRY FIDELITY:
  **COMPLETE**
- Stage 5 — FULL THREE-DESIGN RUNTIME REGRESSION:
  **COMPLETE — R7 CERTIFIED**
- Stage 6 — MASTER ROADMAP / REQUIREMENTS RECONCILIATION:
  **CURRENT**
- Stage 7 — REMAINING AUTHORISED PRE-INJECTOR PROGRAMMES:
  **BLOCKED PENDING RECONCILIATION CLOSEOUT**
- Stage 8 — FULL SYSTEM TESTING:
  **PENDING**
- Stage 9 — LEAF SYSTEM CONTINUITY & UNIFORMITY MASTER GATE:
  **PENDING**
- Stage 10 — INJECTOR HARD STOP:
  **ACTIVE**

The Stage-1 historical completion state is preserved, but it must not be
upgraded to evidence-bound completion until a genuine Stage-1 parent/master
completion authority has been recovered and verified.

## Injector hard stop

The current injector boundary is explicit:

- `injector_research_complete=False`
- `injector_architecture_authorised=False`
- `injector_solver_implementation_authorised=False`
- `injector_UI_implementation_authorised=False`

Injector architecture, solver implementation, and injector UI implementation
must not begin until the preceding authorised pre-injector work, Full System
Testing, and the LEAF System Continuity & Uniformity Master Gate are complete,
and injector research has been explicitly declared complete and implementation
explicitly authorised.

Injector research may continue independently.

## Requirements-preservation rule

The following inherited obligations remain active reconciliation items and must
not disappear merely because newer work exists:

- `WINDOWS_LINUX_LIVE_SECURITY_CERTIFICATION`
- `D1048_EXTERNAL_PRIMARY_SOURCE`
- `D2832_REPEAT_EXTRACTION_VALIDATION`
- `REV_VALIDATION_PROGRAMME`

Their current status must be resolved through evidence. Absence of a local
reference is not evidence of completion or cancellation.

<!-- PREINJECTOR_CANONICAL_GATE_ORDERING_AMENDMENT_2026_09_23_END -->

<!-- PREINJECTOR_MAXIMUM_FIDELITY_RELOCK_2026_09_30_START -->

# Pre-Injector Maximum-Fidelity Qualification Amendment — 30 September 2026

## Authority

This amendment records an explicit current engineering directive.

The earlier Stage-9 Continuity & Uniformity Master Gate remains valid historical
evidence for the scope it certified. Its injector-programme-entry release does
not constitute proof that the existing engineering physics has achieved maximum
practical real-world fidelity.

The subsequent Stage-10 injector research-entry artifacts remain historical
evidence only. They do not authorise current injector research or implementation.

## Current active programme

**PRE-INJECTOR MAXIMUM-FIDELITY QUALIFICATION**

Existing engineering modules remain:

- `combustion_chamber`
- `nozzle`
- `regen`

No new engineering module is authorised during this programme unless an
independent current engineering requirement proves one necessary.

## Engineering objective

Before injector work resumes, the existing LEAF system shall be qualified to
the highest practical engineering fidelity supported by authoritative evidence.

Completion requires, at minimum:

1. all authoritative engineering equations and correlations have identified
   provenance and applicability limits;
2. engineering constants and material/fluid/property data used for acceptance
   are sourced rather than placeholder-derived;
3. PLACEHOLDER or PARTIAL_SOURCE evidence may not support a final engineering
   PASS where sourced validation is required;
4. canonical chamber, nozzle and regenerative-cooling geometry ownership is
   complete for every authoritative result path;
5. hidden empirical, geometric or numerical approximations are either removed,
   replaced by authoritative models, or explicitly bounded and justified;
6. solver results are benchmarked against appropriate analytical, experimental
   or authoritative external reference cases;
7. numerical convergence, sensitivity and repeatability are demonstrated;
8. uncertainty and model limitations are explicit rather than silently ignored;
9. scalar, axial, GUI, reporting and persistence paths preserve the same
   authoritative engineering state;
10. no known current production defect affecting engineering accuracy remains;
11. existing module activation/deactivation and ownership boundaries remain
   valid after engineering corrections;
12. project-wide failure handling remains fail-closed;
13. production source and validation evidence remain auditable and reproducible.

This qualification is stronger than the prior demonstrator acceptance standard.

## Injector hard stop — REIMPOSED

Current locked state:

- `injector_research_complete=False`
- `injector_research_authorised=False`
- `injector_architecture_authorised=False`
- `injector_solver_implementation_authorised=False`
- `injector_UI_implementation_authorised=False`
- `injector_production_mutation_authorised=False`
- `injector_hard_stop_remains_active=True`

No injector research programme, architecture, module, solver, UI, or production
implementation may proceed while this hard stop is active.

Existing Stage-10 injector artifacts are retained as historical evidence and
must not be interpreted as current authorisation.

## Qualification ordering

The active programme shall proceed:

1. **PFQ-1 — CURRENT ENGINEERING FIDELITY GAP INVENTORY**
2. **PFQ-2 — SOURCE / PROPERTY / CORRELATION AUTHORITY QUALIFICATION**
3. **PFQ-3 — COMBUSTION-CHAMBER ENGINEERING PHYSICS QUALIFICATION**
4. **PFQ-4 — NOZZLE ENGINEERING PHYSICS QUALIFICATION**
5. **PFQ-5 — REGENERATIVE-COOLING ENGINEERING PHYSICS QUALIFICATION**
6. **PFQ-6 — COUPLED ENGINE / CROSS-MODULE PHYSICS QUALIFICATION**
7. **PFQ-7 — NUMERICAL CONVERGENCE / SENSITIVITY / UNCERTAINTY**
8. **PFQ-8 — EXTERNAL / EXPERIMENTAL BENCHMARK VALIDATION**
9. **PFQ-9 — GUI / REPORT / PERSISTENCE ENGINEERING-STATE FIDELITY**
10. **PFQ-10 — CROSS-PLATFORM / FAILURE / REPEATABILITY QUALIFICATION**
11. **PFQ-11 — MAXIMUM-FIDELITY MASTER GATE**
12. **INJECTOR HARD-STOP REVIEW**

The injector hard stop may only be reconsidered after PFQ-11 passes and after a
separate explicit user authorisation.

<!-- PREINJECTOR_MAXIMUM_FIDELITY_RELOCK_2026_09_30_END -->

<!-- PFQ_FULL_INPUT_ENGINE_TESTING_REQUIREMENT_START -->

# PFQ-FIET — Full-Input Engine Testing & Scale Continuity Qualification

PFQ-FIET is a mandatory programme within the active
PRE-INJECTOR MAXIMUM-FIDELITY QUALIFICATION.

PFQ-FIET must complete before the final maximum-fidelity master gate may
reconsider the injector hard stop.

This programme is NOT a blanket repetition of previously verified subsystem
tests.

Previous qualified evidence remains reusable according to:

`PFQ2A_R1_PRIOR_VERIFICATION_REUSE_DELTA_ADJUDICATION`

PFQ-FIET adds new integrated full-engine evidence only where that exact
end-to-end requirement has not already been demonstrated.

## Objective

Demonstrate that complete realistic engine input definitions can traverse the
entire current LEAF engineering system without missing data, stale state,
uncontrolled fallback behaviour, incorrect geometry generation, silent module
disconnects, or incorrect pass/fail classification.

Every qualified test engine shall begin from a complete input definition and
shall be evaluated through every applicable current engineering module and
canonical result path.

## Mandatory nominal engine matrix

At minimum six complete nominal engines are required:

1. SMALL CLASS — atmospheric;
2. SMALL CLASS — vacuum;
3. MEDIUM CLASS — atmospheric;
4. MEDIUM CLASS — vacuum;
5. LARGE CLASS — atmospheric;
6. LARGE CLASS — vacuum.

### Small class

Engineering intent:

- student liquid propulsion;
- sounding-rocket liquid propulsion;
- university competition-scale propulsion;
- Race 2 Space-type engineering scale where applicable.

### Medium class

Engineering intent:

- operational launch-engine scale;
- broadly Merlin/Raptor-order thrust class;
- sufficiently large to exercise high mass-flow, pressure, geometry and thermal
  behaviour.

### Large class

Engineering intent:

- thrust greater than the medium-class reference;
- multi-meganewton-class behaviour where supported by the qualified LEAF domain;
- intended to expose scaling failures that would not appear in small or medium
  cases.

Exact numerical input decks shall NOT be invented merely to satisfy these
labels.

PFQ-FIET-1 shall deliberately define the six engine input decks only after
source/property/correlation authority has been qualified sufficiently for the
relevant parameters.

## Complete-input requirement

Each nominal engine shall explicitly provide every required user-facing and
engineering input necessary for the current LEAF calculation chain.

The execution record shall identify:

- every supplied input;
- input unit;
- canonical internal key;
- owning subsystem;
- input source or design basis where relevant;
- whether any default was invoked;
- whether any fallback was invoked.

A hidden default or fallback must not silently replace a required engine input.

## Automatic geometry qualification

For every nominal engine, LEAF shall verify the complete applicable automatic
geometry-generation chain.

This includes, where owned by the current qualified system:

- combustion-chamber geometry;
- chamber length/radius;
- chamber convergence;
- throat geometry;
- throat curvature/blending;
- nozzle type selection;
- conical nozzle generation;
- Rao/bell nozzle generation;
- expansion geometry;
- station geometry;
- axial engine geometry;
- regenerative-cooling channel geometry;
- wall/rib/channel relationships;
- coolant-path geometry;
- any current canonical geometry consumed by downstream modules.

Generated geometry shall be checked against the input requirements, continuity
requirements, governing equations and expected parameter ranges.

## Atmospheric / vacuum qualification

Atmospheric and vacuum variants must be treated as genuine engineering cases,
not merely presentation labels.

Qualification shall inspect the effects of environment/configuration on:

- nozzle design;
- expansion ratio;
- exit state;
- pressure relationships;
- thrust;
- thrust coefficient;
- specific impulse;
- effective exhaust velocity;
- nozzle geometry;
- any applicable altitude/environment-dependent result.

## Full-module data continuity

For every engine execution, a machine-readable module-transfer ledger shall be
created.

For each active engineering module the ledger shall identify:

- module name;
- input keys required;
- input keys received;
- source owner for every received value;
- values received;
- units;
- output keys generated;
- downstream consumers;
- missing inputs;
- unused required inputs;
- overwritten values;
- aliases/conversions;
- stale-state evidence;
- pass/fail status.

Current module scope remains:

- `combustion_chamber`
- `nozzle`
- `regen`

No injector module is permitted.

## Complete output capture

Each nominal engine shall produce a complete terminal/artifact result package
sufficient for detailed engineering interpretation.

This shall include, where applicable:

- combustion state;
- thermodynamic properties;
- CEA-derived state;
- mass flows;
- mixture ratio;
- chamber state;
- throat state;
- nozzle geometry;
- flowfield;
- Mach distribution;
- pressure distribution;
- temperature distribution;
- density distribution;
- performance;
- thrust;
- Isp;
- c-star;
- thrust coefficient;
- exhaust velocity;
- station table;
- wall geometry;
- regen geometry;
- gas-side heat transfer;
- coolant-side heat transfer;
- heat flux;
- hot-wall temperature;
- cold-wall temperature;
- coolant temperature;
- coolant pressure;
- coolant velocity;
- Reynolds number;
- hydraulic diameter;
- pressure drop;
- material state;
- material validation;
- coating/bond-coat state where applicable;
- feasibility state;
- warnings;
- blockers;
- validation status;
- module status;
- source-quality status.

The test shall capture the complete canonical result dictionary or equivalent
authoritative result structure, not merely a manually selected summary.

## Scaling continuity qualification

The six-engine matrix shall be compared across scale.

LEAF shall demonstrate that small → medium → large transitions do not cause:

- discontinuous geometry behaviour without physical cause;
- stale or inherited values;
- unit conversion errors;
- module disconnection;
- invalid array/station scaling;
- numerical instability;
- inappropriate fixed-value assumptions;
- hidden size-specific limits;
- unexplained result discontinuities.

Expected physical trends shall be defined before the final comparison and shall
be checked quantitatively where possible.

## Failure qualification

PFQ-FIET shall also contain intentionally invalid complete-input cases.

Failure cases shall be defined with expected failure ownership before execution.

Required classes include, where applicable:

- missing mandatory input;
- invalid unit/value;
- negative physical quantity;
- zero physical quantity where forbidden;
- incompatible pressure relationship;
- invalid mixture ratio;
- impossible throat/nozzle geometry;
- invalid expansion geometry;
- invalid regen geometry;
- impossible channel/rib relationship;
- invalid coolant conditions;
- unsupported material state;
- property table range violation;
- invalid source-quality state;
- non-convergent engineering state;
- impossible or non-physical engine combination.

For every failure case:

`expected_failure_owner == observed_failure_owner`

must be demonstrated where an explicit owner exists.

A failure case must not silently produce an engineering PASS.

## Pass qualification

For every valid nominal engine:

- expected PASS conditions shall be established before execution;
- all required gates must pass;
- no prohibited fallback may be active;
- required outputs must exist;
- required data transfers must be complete;
- result values must remain physically and numerically coherent.

PFQ-FIET must explicitly prove:

`passes_pass_when_they_should=True`

and:

`failures_fail_when_they_should=True`

within the defined qualified domains.

## State-isolation / repeatability

The six-engine suite shall test sequential execution.

The test order shall be deliberately varied.

A previous engine's:

- inputs;
- geometry;
- material state;
- coolant state;
- flowfield;
- failure state;
- result arrays;
- validation state;

must not contaminate the next engine.

Repeated execution of an identical complete input shall reproduce the same
engineering result within the explicitly defined numerical tolerance.

## PFQ-FIET phases

1. `PFQ-FIET-1 — FULL INPUT CONTRACT & SIX-ENGINE MATRIX DEFINITION`
2. `PFQ-FIET-2 — SMALL-CLASS ATMOSPHERIC / VACUUM QUALIFICATION`
3. `PFQ-FIET-3 — MEDIUM-CLASS ATMOSPHERIC / VACUUM QUALIFICATION`
4. `PFQ-FIET-4 — LARGE-CLASS ATMOSPHERIC / VACUUM QUALIFICATION`
5. `PFQ-FIET-5 — CROSS-SCALE CONTINUITY & PHYSICAL TREND QUALIFICATION`
6. `PFQ-FIET-6 — MODULE DATA-TRANSFER COMPLETENESS QUALIFICATION`
7. `PFQ-FIET-7 — AUTOMATIC GEOMETRY GENERATION QUALIFICATION`
8. `PFQ-FIET-8 — EXPECTED FAILURE / INVALID-INPUT QUALIFICATION`
9. `PFQ-FIET-9 — REPEATABILITY & CROSS-ENGINE STATE-ISOLATION QUALIFICATION`
10. `PFQ-FIET-10 — FULL-INPUT ENGINE TESTING MASTER GATE`

## Master-gate rule

PFQ-FIET-10 may PASS only if all nominal and required failure cases satisfy
their predefined acceptance contracts.

PFQ-FIET completion is a mandatory prerequisite for the final
maximum-fidelity master gate.

Injector hard-stop release is prohibited merely because PFQ-FIET completes.
All other maximum-fidelity requirements must also pass, followed by explicit
user authorisation.

<!-- PFQ_FULL_INPUT_ENGINE_TESTING_REQUIREMENT_END -->
