from __future__ import annotations

import math

from qiskit import QuantumCircuit
from utils.gate_utils import (
    parse_gate_sequence,
    parse_gate_token,
    build_circuit,
    statevector_after,
    state_to_bloch,
    prepare_initial_state,
)


def almost(a: float, b: float, eps: float = 1e-6) -> bool:
    return abs(a - b) < eps


def test_parse_variants_and_casing():
    gate, ang = parse_gate_token("Rx(pi/2)")
    assert gate == "RX" and almost(ang, math.pi / 2)
    seq = parse_gate_sequence("h, rz(π/2),  x , Ry(-90deg), s, sdg, t, tdg")
    names = [g for g, _ in seq]
    assert names == ["H", "RZ", "X", "RY", "S", "SDG", "T", "TDG"]
    assert almost(seq[1][1], math.pi / 2)
    assert almost(seq[3][1], -math.pi / 2)


def test_hadamard_equator_and_rx_flip():
    qc = QuantumCircuit(1); qc.h(0)
    x, y, z = state_to_bloch(statevector_after(qc))
    assert almost(z, 0.0) and (x > 0.999 or x < -0.999)

    qc = QuantumCircuit(1); qc.rx(math.pi, 0)
    x, y, z = state_to_bloch(statevector_after(qc))
    assert z < -0.999


def test_presets_plus_and_i():
    qc = prepare_initial_state("|+>")
    x, y, z = state_to_bloch(statevector_after(qc))
    assert almost(z, 0.0) and x > 0.999

    qc = prepare_initial_state("|i>")
    x, y, z = state_to_bloch(statevector_after(qc))
    assert almost(z, 0.0) and y > 0.999
