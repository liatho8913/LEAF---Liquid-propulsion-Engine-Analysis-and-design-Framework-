# LEAF DESIGN CONSTITUTION

## 1. Identity

**LEAF — Liquid Propulsion Engine Analysis and Design Framework**

This document is the permanent architectural and development constitution
of LEAF.

It defines the rules by which LEAF is designed, changed, reviewed and
extended.

It is not a programme roadmap and it is not a current-state handover.

This document changes only through a deliberate architectural amendment.


## 2. Architectural hierarchy

The canonical architectural hierarchy is:

**Engineering Physics → Engineering Modules → Module Engine → LEAF Operating System → Repository Architecture**

Each layer exists to support the layer above it without taking ownership of
that layer's responsibilities.


## 3. Physics and infrastructure boundary

Engineering physics owns engineering behaviour.

Infrastructure owns execution, lifecycle, storage, workflow and presentation
mechanisms.

Physics must never own infrastructure.

Infrastructure and the GUI must never own engineering physics.

The GUI presents and controls engineering systems; it does not become their
source of truth.


## 4. Single Source of Truth

Every architectural concept must have one canonical source of truth.

A concept must not be represented by competing implementations, competing
registries, competing state owners or competing lifecycle paths.


## 5. Exactly one owner

Every responsibility must have exactly one canonical owner.

Before creating a new class, file, service, registry, controller, cache,
state manager or abstraction, LEAF development must first determine whether
an existing owner can be extended.

New ownership is justified only when no valid existing owner exists.


## 6. One Way

For every operation, LEAF should converge on one canonical mechanism.

Competing paths are temporary migration states, not permanent architecture.


## 7. Replacement, not accumulation

When a new architecture supersedes an old one:

1. migrate legitimate consumers;
2. verify the replacement;
3. remove or quarantine the superseded mechanism.

LEAF must not indefinitely retain old systems beside their replacements.


## 8. Foundations before features

Ownership, contracts, validation, lifecycle, repository health and
scalability are established before feature expansion.

Incomplete foundations are not bypassed to add new engineering features.


## 9. Modular engineering architecture

Engineering modules are removable and replaceable crates.

Each module must have:

- an explicit definition;
- explicit contracts;
- explicit dependencies;
- controlled activation;
- controlled deactivation;
- no hidden dependency on another module's internal implementation.

Removing or deactivating a module must not require rewriting unrelated
engineering systems.


## 10. Scalability over hardcoding

LEAF architecture must support future engineering growth without requiring
project-wide hardcoded changes.

Configuration, registries, ownership and dependency contracts should be used
where they genuinely improve scalability.

Abstraction for its own sake is prohibited.


## 11. Automation before repetition

Repeated mechanical work should be automated when automation reduces error
or architectural drift.

Automation must not obscure engineering ownership or validation.


## 12. Engineering integrity

Validation criteria, equations, thresholds and physical constraints must
never be weakened merely to manufacture a PASS.

An engineering-safe rejection is a successful software outcome when the
design genuinely violates engineering requirements.

Synthetic tests support acceptance but do not override the normal
application as the authoritative runtime proof.


## 13. Evidence-driven development

Production mutation follows evidence.

The preferred sequence is:

1. read-only audit;
2. runtime proof where required;
3. narrow diagnosis;
4. minimal existing-owner correction;
5. static verification;
6. normal-application acceptance;
7. completion gate.

Speculative repairs are prohibited.


## 14. Minimal change discipline

Before production mutation, development must establish:

1. the exact change;
2. why it exists and what problem it solves;
3. where it sits in the architecture;
4. whether an existing owner can be extended;
5. files added, modified and removed;
6. why the amount of code is justified;
7. how success is measured;
8. the next step.

One feature is completed before the next is begun.


## 15. Repository health

Repository health is a permanent success metric.

LEAF tracks and reduces:

- unnecessary source files;
- duplicated files;
- duplicated logic;
- duplicated ownership;
- dead code;
- obsolete compatibility mechanisms;
- unnecessary dependency depth;
- abandoned development artefacts in active architecture.

Source growth must be justified by capability or architectural value.


## 16. Historical evidence

Historical reports, certificates, quarantine material and programme artefacts
are evidence.

They do not become current architectural owners merely because they contain
similar terminology.

Historical evidence should not be rewritten to make old records appear
current.


## 17. Demonstrator discipline

LEAF may deliberately freeze a subsystem or release when its agreed
demonstrator scope is complete.

A completed subsystem is not reopened merely to continue programme numbering.

A frozen subsystem is reopened only for:

- a demonstrated defect;
- an explicit new engineering requirement;
- a deliberate architectural amendment.


## 18. Governance ownership

LEAF governance has exactly three canonical project-level documents:

1. **LEAF_DESIGN_CONSTITUTION.md**
   Permanent architectural philosophy and development law.

2. **LEAF_MASTER_ROADMAP.md**
   Long-term strategic direction and major programme state.

3. **LEAF_CURRENT_PROGRAMME_HANDOVER.md**
   Exact current execution state and continuation point.

Programme reports and historical handovers do not replace these owners.


## 19. Constitution precedence

When implementation guidance conflicts with this Constitution, the
Constitution takes precedence unless it is deliberately amended.

The Constitution must be read before architectural production changes are
proposed or written.
