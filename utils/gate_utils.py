from __future__ import annotations

from typing import List, Tuple

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


SUPPORTED_GATES = {"I", "X", "Y", "Z", "H", "Rx", "Ry", "Rz"}


def parse_gate_token(token: str) -> Tuple[str, float | None]:
    """Parse a gate token like 'H', 'X', 'Rx(pi/2)', 'Rz(1.5708)'.

    Returns (gate_name, angle_radians_or_None).
    """
    token = token.strip()
    if "(" not in token:
        gate = token
        angle = None
    else:
        gate, arg = token.split("(", 1)
        arg = arg.rstrip(")").strip()
        angle = _parse_angle_to_radians(arg)
    gate = gate.strip()
    if gate not in SUPPORTED_GATES:
        raise ValueError(f"Unsupported gate: {gate}")
    if gate in {"Rx", "Ry", "Rz"} and angle is None:
        raise ValueError(f"Rotation gate {gate} requires an angle, e.g., {gate}(pi/2)")
    return gate, angle


def _parse_angle_to_radians(expr: str) -> float:
    """Parse expressions like 'pi', 'pi/2', '2*pi/3', '1.234'."""
    expr = expr.replace(" ", "")
    if "pi" in expr:
        expr = expr.replace("pi", str(np.pi))
        try:
            return float(eval(expr, {"__builtins__": {}}, {}))
        except Exception as exc:
            raise ValueError(f"Invalid angle expression: {expr}") from exc
    try:
        return float(expr)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric angle: {expr}") from exc


def apply_gates(circuit: QuantumCircuit, gates: List[str]) -> QuantumCircuit:
    """Apply a list of gate tokens to a single-qubit circuit in-place and return it."""
    if circuit.num_qubits != 1:
        raise ValueError("apply_gates expects a single-qubit circuit")
    for token in gates:
        name, angle = parse_gate_token(token)
        if name == "I":
            circuit.i(0)
        elif name == "X":
            circuit.x(0)
        elif name == "Y":
            circuit.y(0)
        elif name == "Z":
            circuit.z(0)
        elif name == "H":
            circuit.h(0)
        elif name == "Rx":
            circuit.rx(angle, 0)
        elif name == "Ry":
            circuit.ry(angle, 0)
        elif name == "Rz":
            circuit.rz(angle, 0)
        else:
            raise ValueError(f"Unsupported gate encountered: {name}")
    return circuit


def statevector_after(circuit: QuantumCircuit) -> Statevector:
    """Return the final statevector for a single-qubit circuit."""
    if circuit.num_qubits != 1:
        raise ValueError("statevector_after expects a single-qubit circuit")
    return Statevector.from_instruction(circuit)


def bloch_coordinates(state: Statevector) -> Tuple[float, float, float]:
    """Compute Bloch vector coordinates (x, y, z) from a single-qubit statevector."""
    if state.num_qubits != 1:
        raise ValueError("bloch_coordinates expects a single-qubit statevector")
    alpha, beta = state.data
    rho01 = alpha.conjugate() * beta
    x = 2.0 * rho01.real
    y = 2.0 * rho01.imag
    z = (abs(alpha) ** 2) - (abs(beta) ** 2)
    return float(x), float(y), float(z)


def sequence_to_bloch_path(gates: List[str]) -> List[Tuple[float, float, float]]:
    """Return Bloch coordinates after each prefix of the sequence, starting from |0>."""
    circ = QuantumCircuit(1)
    path: List[Tuple[float, float, float]] = []
    for idx in range(len(gates)):
        circ = apply_gates(QuantumCircuit(1), gates[:idx + 1])
        sv = statevector_after(circ)
        path.append(bloch_coordinates(sv))
    return path
