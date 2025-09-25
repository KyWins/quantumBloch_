from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit

from utils.gate_utils import (
    parse_gate_token,
    apply_gates,
    statevector_after,
    bloch_coordinates,
    parse_gate_sequence,
    build_circuit,
    state_to_bloch,
    cartesian_to_spherical,
)


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


def test_parse_gate_sequence_variants():
    seq = " h , rx(π/2), RZ(90deg) ,   y "
    gates = parse_gate_sequence(seq)
    assert [g for g, _ in gates] == ["H", "RX", "RZ", "Y"]
    assert math.isclose(gates[1][1], math.pi / 2, rel_tol=1e-7)
    assert math.isclose(gates[2][1], math.pi / 2, rel_tol=1e-7)


def test_state_metrics():
    qc = QuantumCircuit(1)
    qc.h(0)
    sv = statevector_after(qc)
    x, y, z = state_to_bloch(sv)
    theta, phi = cartesian_to_spherical(x, y, z)
    assert abs(z) < 1e-7
    assert 0.0 <= theta <= math.pi
    assert -math.pi <= phi <= math.pi
