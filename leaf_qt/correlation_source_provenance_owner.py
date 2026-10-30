"""
LEAF correlation source/provenance owner.

Owns authoritative source identity and provenance metadata for
production correlation/model families.

This module DOES NOT own the physics equations themselves.

PFQ-2E established source authority.
PFQ-2F subsequently qualified semantic applicability,
validity-domain behaviour, and runtime use for the declared
production correlation families while retaining their documented
assumptions and known limitations.
"""

from __future__ import annotations

from copy import deepcopy


CORRELATION_SOURCE_RECORDS = {
    "area_mach_relation": {
        "family": "area_mach_relation",
        "authority_class": "AUTHORITATIVE_CORRELATION",
        "source_id": "NACA_REPORT_1135_COMPRESSIBLE_FLOW",
        "title": "Equations, Tables, and Charts for Compressible Flow",
        "organisation": "NACA / NASA archival authority",
        "citation": "NACA Report 1135; NASA NTRS document 19930091059",
        "source_quality": "PRIMARY_ARCHIVAL_TECHNICAL_REPORT",
        "corroborating_source": {
            "source_id": "NASA_GRC_ISENTROPIC_FLOW_EQUATIONS",
            "organisation": "NASA Glenn Research Center",
            "resource": "Isentropic Flow Equations",
            "source_quality": "NASA_TECHNICAL_REFERENCE",
        },
        "assumptions": [
            "quasi-one-dimensional flow",
            "steady flow",
            "isentropic flow",
            "perfect-gas form when constant gamma relation is used",
            "A* denotes sonic/choked reference area",
        ],
        "known_limitations": [
            "subsonic and supersonic branches require explicit selection",
            "shock-containing regions are not globally isentropic",
            "constant-gamma use requires calorically-perfect-gas applicability",
        ],
        "source_authority_resolved": True,
        "semantic_validity_qualified": True,
        "runtime_use_qualified": True,
        "production_eligible": True,
        "qualification_state": (
            "SOURCE_AUTHORITY_AND_PFQ2F_SEMANTIC_RUNTIME_QUALIFIED"
        ),
    },

    "isentropic_flow": {
        "family": "isentropic_flow",
        "authority_class": "AUTHORITATIVE_CORRELATION",
        "source_id": "NACA_REPORT_1135_COMPRESSIBLE_FLOW",
        "title": "Equations, Tables, and Charts for Compressible Flow",
        "organisation": "NACA / NASA archival authority",
        "citation": "NACA Report 1135; NASA NTRS document 19930091059",
        "source_quality": "PRIMARY_ARCHIVAL_TECHNICAL_REPORT",
        "corroborating_source": {
            "source_id": "NASA_GRC_ISENTROPIC_FLOW_EQUATIONS",
            "organisation": "NASA Glenn Research Center",
            "resource": "Isentropic Flow Equations",
            "source_quality": "NASA_TECHNICAL_REFERENCE",
        },
        "assumptions": [
            "adiabatic",
            "reversible",
            "constant entropy",
            "constant-gamma expressions require calorically perfect gas",
        ],
        "known_limitations": [
            "normal shocks invalidate isentropic continuity across the shock",
            "oblique shocks invalidate isentropic continuity across the shock",
            "irreversible discontinuities require separate treatment",
            "caloric imperfection requires qualified treatment",
        ],
        "source_authority_resolved": True,
        "semantic_validity_qualified": True,
        "runtime_use_qualified": True,
        "production_eligible": True,
        "qualification_state": (
            "SOURCE_AUTHORITY_AND_PFQ2F_SEMANTIC_RUNTIME_QUALIFIED"
        ),
    },

    "thin_wall_pressure_vessel": {
        "family": "thin_wall_pressure_vessel",
        "authority_class": "AUTHORITATIVE_ENGINEERING_MODEL",
        "source_id": "NASA_THIN_WALLED_CYLINDRICAL_PRESSURE_VESSEL",
        "title": "Thin-walled cylindrical pressure-vessel membrane formulation",
        "organisation": "NASA technical authority",
        "citation": (
            "NASA technical thin-wall pressure-vessel formulation; "
            "hoop stress sigma_theta = p*r/t and longitudinal stress "
            "sigma_L = p*r/(2*t)"
        ),
        "source_quality": "NASA_TECHNICAL_FORMULATION",
        "assumptions": [
            "thin cylindrical wall",
            "membrane-stress approximation",
            "internal differential pressure",
            "axisymmetric idealisation",
        ],
        "known_limitations": [
            "local bending not represented",
            "stress concentrations not represented",
            "thermal stress not represented",
            "buckling not represented",
            "joint and weld effects not represented",
            "material nonlinearities not represented",
            "basic equation does not supply structural design factors",
            "r/t thin-wall applicability must be qualified by PFQ-2F",
        ],
        "source_authority_resolved": True,
        "semantic_validity_qualified": True,
        "runtime_use_qualified": True,
        "production_eligible": True,
        "qualification_state": (
            "SOURCE_AUTHORITY_AND_PFQ2F_SEMANTIC_RUNTIME_QUALIFIED"
        ),
    },
}


def build_correlation_source_provenance_owner(results):
    """
    Build source/provenance metadata.

    Source authority is resolved for the three PFQ-2E families.
    PFQ-2F semantic and runtime qualification is complete for the
    declared production use represented by these records.
    """

    results = (
        results
        if isinstance(results, dict)
        else {}
    )

    records = deepcopy(
        CORRELATION_SOURCE_RECORDS
    )

    required_families = (
        "area_mach_relation",
        "isentropic_flow",
        "thin_wall_pressure_vessel",
    )

    blockers = []

    for family in required_families:
        record = records.get(
            family
        )

        if not isinstance(
            record,
            dict,
        ):
            blockers.append(
                f"MISSING_CORRELATION_SOURCE_RECORD:{family}"
            )
            continue

        if (
            record.get(
                "source_authority_resolved"
            )
            is not True
        ):
            blockers.append(
                f"SOURCE_AUTHORITY_UNRESOLVED:{family}"
            )

        if not record.get(
            "source_id"
        ):
            blockers.append(
                f"MISSING_SOURCE_ID:{family}"
            )

        if not record.get(
            "citation"
        ):
            blockers.append(
                f"MISSING_CITATION:{family}"
            )

    source_authority_complete = (
        len(blockers)
        == 0
    )

    semantic_validity_complete = all(
        record.get(
            "semantic_validity_qualified"
        )
        is True
        for record
        in records.values()
    )

    runtime_use_complete = all(
        record.get(
            "runtime_use_qualified"
        )
        is True
        for record
        in records.values()
    )

    production_eligibility_complete = all(
        record.get(
            "production_eligible"
        )
        is True
        for record
        in records.values()
    )

    complete = all(
        (
            source_authority_complete,
            semantic_validity_complete,
            runtime_use_complete,
            production_eligibility_complete,
        )
    )

    status = (
        "PASS_CORRELATION_SOURCE_PROVENANCE_OWNER"
        if complete
        else "FAIL_CORRELATION_SOURCE_PROVENANCE_OWNER"
    )

    return {
        "correlation_source_provenance_owner_status":
            status,

        "correlation_source_provenance_owner_complete":
            complete,

        "correlation_source_provenance_source_authority_complete":
            source_authority_complete,

        "correlation_source_provenance_semantic_validity_complete":
            semantic_validity_complete,

        "correlation_source_provenance_runtime_use_complete":
            runtime_use_complete,

        "correlation_source_provenance_PFQ2F_required":
            not (
                semantic_validity_complete
                and runtime_use_complete
            ),

        "correlation_source_provenance_family_count":
            len(records),

        "correlation_source_provenance_families":
            list(records),

        "correlation_source_provenance_records":
            records,

        "correlation_source_provenance_blockers":
            blockers,

        "correlation_source_provenance_qualification_state":
            (
                "SOURCE_AUTHORITY_AND_PFQ2F_SEMANTIC_RUNTIME_QUALIFIED"
                if source_authority_complete
                else "SOURCE_AUTHORITY_INCOMPLETE"
            ),
    }


def attach_correlation_source_provenance_owner(results):
    """
    Attach correlation source/provenance metadata to result state.
    """

    results = (
        results
        if isinstance(results, dict)
        else {}
    )

    provenance = (
        build_correlation_source_provenance_owner(
            results
        )
    )

    results.update(
        provenance
    )

    return results
