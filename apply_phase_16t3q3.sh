#!/usr/bin/env bash
set -u

echo "Checking Phase 16T.3Q.2 first..."
python -m pytest -q \
  project_maintenance/test_regen_candidate_population_master_gate_status_adapter_phase_16t3q2.py \
  project_maintenance/test_regen_geometry_master_gate_status_adapter_phase_16t3q1.py

if [ $? -ne 0 ]; then
  echo "16T.3Q.2 regression failed. Not applying 16T.3Q.3."
  exit 1
fi

echo "16T.3Q.2 verified. Ready to apply 16T.3Q.3."
