# LEAF — Liquid Propulsion Engine Analysis and Design Framework

## Demonstrator Release Candidate

LEAF (Liquid Propulsion Engine Analysis and Design Framework) is a modular liquid-rocket-engine engineering analysis environment written in Python and PySide6.

This demonstrator release presents the current validated LEAF foundation and the engineering modules that are implemented today. It is intended as a working engineering demonstrator rather than a claim of complete launch-vehicle or propulsion-system coverage.

---

## Current Demonstrator Scope

The current Modular Engine represents three engineering modules:

- Combustion Chamber
- Nozzle
- Regenerative Cooling

These modules use LEAF's common runtime, storage, validation, reporting, workflow and module infrastructure rather than independent application frameworks.

The current architectural ownership hierarchy is:

Engineering Physics
    ↓
Engineering Modules
    ↓
Module Engine
    ↓
LEAF Operating System
    ↓
Repository Architecture

Engineering physics does not own application infrastructure, and the user interface does not own engineering equations.

---

## Principal Capabilities

The current demonstrator includes:

- NASA CEA / RocketCEA thermochemical integration
- chamber-pressure, mixture-ratio and mass-flow input handling
- fuel and oxidizer mass-flow calculation
- conical and Rao-bell nozzle geometry
- area-Mach solution
- nozzle flowfield calculation
- thrust, characteristic velocity, thrust coefficient and specific impulse
- vacuum and sea-level performance outputs
- regenerative cooling analysis
- Bartz gas-side heat-transfer modelling
- coolant-side heat-transfer and hydraulic calculations
- wall-temperature and heat-flux calculations
- axial cooling-channel marching
- cooling-channel geometry validation
- engineering validation and diagnostic reporting
- Main Outputs
- Graph Explorer
- Station Table
- Regenerative Cooling Cross-Section Viewer
- report viewing
- canonical project/design save and reload

Graph Explorer evaluations use the real LEAF calculation path. A plotted X point represents a genuine calculation rather than an interpolated substitute.

---

## Validated Environment

The current demonstrator release has been validated on:

Platform:       macOS 15.6
Architecture:   arm64
Python:         CPython 3.12.13

Validated Python dependencies:

PySide6==6.11.1
numpy==2.4.6
scipy==1.17.1
matplotlib==3.10.9
rocketcea==1.2.3

These exact dependencies are recorded in:

requirements.txt

RocketCEA includes native compiled components. The validated macOS environment uses Homebrew GCC runtime support, including libgfortran.

Other operating systems and Python versions should not be treated as release-certified unless separately verified.

---

## Installation

From the LEAF repository root, create and activate a Python 3.12 virtual environment.

Example:

    python3.12 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

RocketCEA may require platform-specific native compiler/runtime support during installation.

---

## Launch

The canonical application launch command is:

    python3 -m leaf_qt.main

Run it from the LEAF repository root with the validated virtual environment active.

---

## Canonical Demonstration Case

The portable demonstrator project is:

LEAF_Projects/
└── LEAF_Demonstrator_1722/
    └── project.leaf_project.json

Its baseline design is:

LEAF_Designs/
└── LEAF_Demonstrator_Baseline_1722/
    ├── design.leaf_design.json
    └── engineering_state.json

The engineering state uses:

LEAF_PROJECT_STATE_V2

The canonical state contains eleven top-level fields covering:

- calculator inputs
- CEA inputs
- raw CEA output
- geometry inputs
- regenerative-cooling materials
- benchmark selection
- startup-health state
- design history
- current calculated results

The release case uses repository-relative references and contains no developer-machine absolute paths.

---

## Canonical 1722 Baseline

Representative accepted values include:

Chamber pressure                 10 MPa
Mixture ratio                    1.875
Mass flow rate                   1.15 kg/s

Thrust                           3195.311573 N
Specific impulse                 283.234638 s
Vacuum specific impulse          302.265826 s

Corrected thrust                 2879.197527 N
Corrected specific impulse       255.214070 s

Throat area                      0.0001976364224 m²
Exit area                        0.002118927583 m²
Expansion ratio                  10.72134153

Rib width                        0.001 m
Hot-gas heat flux                3577036.357 W/m²
Required wall thickness          0.0857718105 m

These values are demonstration-case reference values, not universal design targets.

---

## Demonstration Workflow

A basic demonstration sequence is:

1. Launch LEAF.
2. Open LEAF_D-case reference values, not universal design targets.

---

## Demonstration Workflow

A basic demonstration sequence is:

1. Launch LEAF.
2. Open LEAF_Demonstrator_Baseline_1722.
3. Inspect the restored engineering inputs.
4. Run NASA CEA.
5. Run the LEAF calculation.
6. Inspect Main Outputs.
7. Open the Regenerative Cooling Cross-Section Viewer.
8. Inspect the Station Table.
9. Use Graph Explorer.
10. Inspect engineering reports and validation output.
11. Save to a new project/design if modifications are required.
12. Close and reopen the saved design to verify persistent engineering state.

Do not overwrite the canonical baseline when experimenting with alternative values.

---

## Project and Design Model

LEAF separates a project from a design.

A project represents the larger engineering programme or engine family.

A design represents an individual engineering configuration within that project.

Conceptually:

Project
    ↓
one or more Designs
    ↓
engineering_state.json

User-facing canonical storage roots are:

LEAF_Projects/
LEAF_Designs/
LEAF_Reports/
LEAF_Exports/

---

## Module Architecture

Module discovery is owned by LEAF's Module Engine.

Current module definitions are stored under:

leaf_qt/module_engine/definitions/

The demonstrator contains exactly three current definitions:

combustion_chamber.module.json
nozzle.json
regen.module.json

Modules are designed as explicit, independently represented engineering units with declared contracts and dependencies.

The Module Engine owns discovery, contracts, verification and runtime representation. Individual modules should not create parallel module registries or activation systems.

---

## Design History

LEAF maintains persistent design-iteration history.

The release history architecture stores:

- iteration identity
- timestamp
- engineering input snapshot
- engineering summary
- required historical validation evidence
- diagnostics
- audit evidence

The complete current calculated result set is owned by the current engineering state rather than duplicated into every historical iteration.

The canonical demonstrator state was reduced from approximately 280 MiB to approximately 8.5 MiB by eliminating recursive and duplicate history ownership while preserving the accepted engineering result state.

---

## Engineering Validation

A software PASS and an engineering PASS are not the same thing.

LEAF may execute correctly while reporting that a particular engineering configuration fails a thermal, material, geometry or validation criterion.

Engineering gates are intentionally preserved rather than weakened to produce visually clean demonstrations.

---

## Known Demonstrator Limitations

Some material and coating routes remain explicitly incomplete or insufficiently sourced.

States such as:

PLACEHOLDER
PARTIAL_SOURCE
INSUFFICIENT_SOURCE_MODE
NO_ACTIVE_COATING_ROUTE
SUMMARY_ONLY

should be interpreted as engineering-data limitations rather than silently promoted to validated data.

Some legitimate regenerative-cooling/material configurations may therefore produce engineering FAIL results.

The current release does not claim validated implementation of:

- injector design
- turbopump design
- complete propellant-feed-system analysis
- combustion-instability prediction
- full structural finite-element analysis
- vehicle trajectory analysis

Those capabilities are outside this demonstrator release.

---

## Repository Boundary

Runtime release content is centred on:

leaf_qt/
cea_integration/
requirements.txt

along with the canonical demonstration project/design required for the release.

Development-maintenance, historical evidence, quarantine, archive and IDE/environment directories are not part of the clean distributable runtime surface.

Examples include:

project_maintenance/
project_evidence/
_leaf_legacy_reduction_archive/
_leaf_repository_cleanup_candidates/
_leaf_legacy_quarantine/
_leaf_archive/
_leaf_artifacts/
_external_repository_quarantine/
.idea/
.venv/

---

## Development Philosophy

LEAF follows several permanent architectural rules:

- foundations before features
- one canonical owner for each concept
- engineering physics remains separate from infrastructure
- modules remain explicit and replaceable
- reuse existing owners before introducing new systems
- replace superseded mechanisms rather than accumulating compatibility layers indefinitely
- automate repeated integration work
- treat repository health as an engineering concern

The intended direction is that adding future engineering modules requires progressively less application-wide integration work.

---

## Release Status

This repository is currently in demonstrator release preparation.

Programme 40 established the accepted live demonstrator.

Release-freeze work has subsequently:

- captured the validated environment
- established a portable canonical demonstration case
- verified clean launch/save/reload behaviour
- removed embedded development debris from the production namespace
- consolidated design-history ownership
- reduced the portable engineering state from approximately 280 MiB to approximately 8.5 MiB
- proved compact linear history growth through live save/reload calculations

Final clean release staging and package-integrity verification remain before the demonstrator release is considered frozen.
