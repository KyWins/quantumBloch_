from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit

from utils.gate_utils import parse_gate_token, apply_gates, statevector_after, bloch_coordinates


def test_parse_gate_token_rotation():
    name, angle = parse_gate_token("Rx(pi/2)")
    assert name == "Rx"
    assert math.isclose(angle, math.pi / 2, rel_tol=1e-7)


def test_apply_hadamard_results_on_equator():
    qc = apply_gates(QuantumCircuit(1), ["H"])
    sv = statevector_after(qc)
    x, y, z = bloch_coordinates(sv)
    assert abs(z) < 1e-7
    assert x > 0.9


def test_rz_phase_rotation_does_not_change_z():
    qc = apply_gates(QuantumCircuit(1), ["H", "Rz(pi/2)"])
    sv = statevector_after(qc)
    x, y, z = bloch_coordinates(sv)
    assert abs(z) < 1e-7
    r = math.hypot(x, y)
    assert 0.9 < r < 1.1
