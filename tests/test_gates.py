from __future__ import annotations

import math

import pytest
from qiskit import QuantumCircuit

from utils.gate_utils import (
    GateParseError,
    apply_gates,
    bloch_coordinates,
    build_circuit,
    cartesian_to_spherical,
    parse_gate_sequence,
    parse_gate_token,
    simulate_sequence,
    state_to_bloch,
    statevector_after,
)


def test_parse_gate_token_rotation():
    name, angle = parse_gate_token("Rx(pi/2)")
    assert name == "RX"
    assert math.isclose(angle, math.pi / 2, rel_tol=1e-7)


def test_parse_gate_sequence_variants_and_errors():
    seq = " h , rx(π/2), RZ(90deg) ,   y "
    gates = parse_gate_sequence(seq)
    assert [g for g, _ in gates] == ["H", "RX", "RZ", "Y"]
    assert math.isclose(gates[1][1], math.pi / 2, rel_tol=1e-7)
    assert math.isclose(gates[2][1], math.pi / 2, rel_tol=1e-7)

    with pytest.raises(GateParseError) as exc:
        parse_gate_sequence("H, foo")
    assert exc.value.index == 1
    assert exc.value.token.lower() == "foo"


def test_phase_gate_support():
    gates = parse_gate_sequence("H, P(pi/2)")
    assert gates[1][0] == "P"
    qc = QuantumCircuit(1)
    build_circuit(gates, base=qc)
    sv = statevector_after(qc)
    x, y, z = state_to_bloch(sv)
    assert abs(z) < 1e-7
    assert y > 0.9


def test_simulate_sequence_snapshots():
    result = simulate_sequence("|0>", "H, Rz(pi/2)")
    assert len(result.gates) == 2
    assert len(result.coordinates) == 3  # initial + two steps
    assert len(result.states) == 3
    # Initial |0>
    assert result.coordinates[0][2] > 0.999
    # After H -> equator
    assert abs(result.coordinates[1][2]) < 1e-7
    # Final point still on equator
    assert abs(result.coordinates[2][2]) < 1e-7


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


def test_state_metrics():
    qc = QuantumCircuit(1)
    qc.h(0)
    sv = statevector_after(qc)
    x, y, z = state_to_bloch(sv)
    theta, phi = cartesian_to_spherical(x, y, z)
    assert abs(z) < 1e-7
    assert 0.0 <= theta <= math.pi
    assert -math.pi <= phi <= math.pi
