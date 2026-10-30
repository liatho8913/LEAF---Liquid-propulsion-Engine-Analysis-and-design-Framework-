"""
LEAF Regen Scalability Framework
================================

Compatibility wrapper for Stage V.1.

The actual Stage V.1 pass/fail logic now belongs to:

regen_scalability_constraint_owner.py

This file remains so older pipeline calls do not break.
"""

from regen_scalability_constraint_owner import (
    attach_regen_scalability_constraint_owner,
    evaluate_regen_scalability_constraints,
)


def attach_regen_scalability_framework(results):
    return attach_regen_scalability_constraint_owner(results)


def audit_regen_scalability(results):
    return evaluate_regen_scalability_constraints(results)