from __future__ import annotations

from typing import List, Tuple, Optional, NamedTuple

import math
import re
import ast
import operator as op
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


SUPPORTED_GATES = {"I", "X", "Y", "Z", "H", "S", "SDG", "T", "TDG", "SX", "SXDG", "P", "RX", "RY", "RZ"}
ANGLE_GATES = {"RX", "RY", "RZ", "P"}
_GATE_ALIASES = {"ID": "I"}


class GateParseError(ValueError):
    """Raised when a gate token cannot be parsed."""

    def __init__(self, token: str, index: Optional[int], message: str):
        self.token = token
        self.index = index
        super().__init__(message)

    def __str__(self) -> str:
        position = f" (token #{self.index + 1})" if self.index is not None else ""
        return f"{super().__str__()} [offending token: '{self.token}']{position}"


ParsedGate = Tuple[str, Optional[float]]
Coordinate = Tuple[float, float, float]
StateTuple = Tuple[complex, complex]


class SimulationResult(NamedTuple):
    gates: Tuple[ParsedGate, ...]
    coordinates: Tuple[Coordinate, ...]
    states: Tuple[StateTuple, ...]

# Safe arithmetic evaluator for basic expressions --------------------------------
_ALLOWED_BINOPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv}
_ALLOWED_UNARYOPS = {ast.UAdd: op.pos, ast.USub: op.neg}


def _safe_eval_arith(expr: str) -> float:
    node = ast.parse(expr, mode="eval")

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Num):  # Python <3.8 compatibility
            return float(n.n)
        if isinstance(n, ast.Constant):  # Python 3.8+
            if isinstance(n.value, (int, float)):
                return float(n.value)
            raise ValueError("Invalid constant in angle expression")
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_UNARYOPS:
            return _ALLOWED_UNARYOPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_BINOPS:
            left = _eval(n.left)
            right = _eval(n.right)
            return _ALLOWED_BINOPS[type(n.op)](left, right)
        if isinstance(n, ast.Tuple):
            raise ValueError("Tuples not allowed in angle expression")
        raise ValueError("Unsupported syntax in angle expression")

    return float(_eval(node))


# Enhanced angle parsing -------------------------------------------------------
_PI_ALIASES = {"pi": math.pi, "π": math.pi}
def _parse_angle_to_radians(expr: str) -> float:
    """Parse expressions like 'pi', 'π/2', '2*pi/3', '1.234', '90deg', '-45deg' using a safe arithmetic evaluator."""
    s = expr.strip()
    for name, value in _PI_ALIASES.items():
        s = re.sub(fr"(?i){name}", f"({value})", s)
    s = s.replace(" ", "")
    if s.lower().endswith("deg"):
        core = s[:-3]
        try:
            degrees = float(core)
        except ValueError as exc:
            raise ValueError(f"Invalid degree angle: {expr}") from exc
        return math.radians(degrees)
    try:
        return _safe_eval_arith(s)
    except Exception as exc:
        raise ValueError(f"Invalid angle expression: {expr}") from exc


# New parser that accepts a free-form sequence string -------------------------

def parse_gate_sequence(seq: str) -> List[ParsedGate]:
    """Parse a comma-separated sequence into normalized (UPPERCASE gate, angle) tuples."""
    tokens = [t.strip() for t in seq.split(",")]
    result: List[ParsedGate] = []
    for idx, token in enumerate(tokens):
        if not token:
            continue
        result.append(parse_gate_token(token, index=idx))
    return result


def parse_gate_token(token: str, *, index: Optional[int] = None) -> ParsedGate:
    """Parse a single gate token like 'H', 'X', 'Rx(pi/2)', 'Rz(1.5708)' -> (UPPERCASE gate, angle_or_None)."""
    token = token.strip()
    if not token:
        raise GateParseError(token, index, "Empty gate token")

    angle: Optional[float] = None
    if "(" in token:
        if not token.endswith(")"):
            raise GateParseError(token, index, "Gate arguments must be enclosed in parentheses")
        gate, arg = token.split("(", 1)
        gate = gate.strip().upper()
        arg = arg[:-1].strip()
        if not arg:
            raise GateParseError(token, index, f"Gate {gate or token} requires an angle expression")
        try:
            angle = _parse_angle_to_radians(arg)
        except ValueError as exc:
            raise GateParseError(token, index, str(exc)) from exc
    else:
        gate = token.upper()

    gate = _GATE_ALIASES.get(gate, gate)

    if gate not in SUPPORTED_GATES:
        supported = ", ".join(sorted(SUPPORTED_GATES))
        raise GateParseError(token, index, f"Unsupported gate '{gate}'. Supported gates: {supported}")

    if gate in ANGLE_GATES:
        if angle is None:
            raise GateParseError(token, index, f"Gate {gate} requires an angle, e.g., {gate}(pi/2)")
        angle = float(angle)
    elif angle is not None:
        raise GateParseError(token, index, f"Gate {gate} does not take an angle")

    return gate, angle


def build_circuit(gates: List[ParsedGate], base: QuantumCircuit | None = None) -> QuantumCircuit:
    """Build a single-qubit circuit from parsed gate tuples.

    If base is provided, append to it in-place and return it; otherwise create a new circuit.
    """
    qc = base if base is not None else QuantumCircuit(1)
    for name, angle in gates:
        if name == "I":
            qc.i(0)
        elif name == "H":
            qc.h(0)
        elif name == "X":
            qc.x(0)
        elif name == "Y":
            qc.y(0)
        elif name == "Z":
            qc.z(0)
        elif name == "S":
            qc.s(0)
        elif name == "SDG":
            qc.sdg(0)
        elif name == "T":
            qc.t(0)
        elif name == "TDG":
            qc.tdg(0)
        elif name == "SX":
            qc.sx(0)
        elif name == "SXDG":
            qc.sxdg(0)
        elif name == "P":
            qc.p(float(angle), 0)  # type: ignore[arg-type]
        elif name == "RX":
            qc.rx(float(angle), 0)  # type: ignore[arg-type]
        elif name == "RY":
            qc.ry(float(angle), 0)  # type: ignore[arg-type]
        elif name == "RZ":
            qc.rz(float(angle), 0)  # type: ignore[arg-type]
        else:
            raise ValueError(f"Unsupported gate: {name}")
    return qc


def prepare_initial_state(key: str) -> QuantumCircuit:
    """Return a circuit that prepares a chosen initial state on |0>.

    key in {"|0>", "|+>", "|i>"}
    |0>: default computational basis state
    |+>: H|0>
    |i>: S H |0> (global phase ignored)
    """
    qc = QuantumCircuit(1)
    if key == "|+>":
        qc.h(0)
    elif key == "|i>":
        qc.h(0)
        qc.s(0)
    return qc


# Backwards compatible helpers -------------------------------------------------

def apply_gates(circuit: QuantumCircuit, gates: List[str]) -> QuantumCircuit:
    """Apply a list of gate tokens to a single-qubit circuit in-place and return it."""
    if circuit.num_qubits != 1:
        raise ValueError("apply_gates expects a single-qubit circuit")
    for idx, token in enumerate(gates):
        name, angle = parse_gate_token(token, index=idx)
        if name == "I":
            circuit.i(0)
        elif name == "SX":
            circuit.sx(0)
        elif name == "SXDG":
            circuit.sxdg(0)
        elif name == "P":
            circuit.p(angle, 0)  # type: ignore[arg-type]
        elif name == "X":
            circuit.x(0)
        elif name == "Y":
            circuit.y(0)
        elif name == "Z":
            circuit.z(0)
        elif name == "H":
            circuit.h(0)
        elif name == "RX":
            circuit.rx(angle, 0)  # type: ignore[arg-type]
        elif name == "RY":
            circuit.ry(angle, 0)  # type: ignore[arg-type]
        elif name == "RZ":
            circuit.rz(angle, 0)  # type: ignore[arg-type]
        elif name == "S":
            circuit.s(0)
        elif name == "SDG":
            circuit.sdg(0)
        elif name == "T":
            circuit.t(0)
        elif name == "TDG":
            circuit.tdg(0)
        else:
            raise ValueError(f"Unsupported gate encountered: {name}")
    return circuit


def statevector_after(circuit: QuantumCircuit) -> Statevector:
    """Return the final statevector for a single-qubit circuit, no simulator backend."""
    if circuit.num_qubits != 1:
        raise ValueError("statevector_after expects a single-qubit circuit")
    return Statevector.from_label("0").evolve(circuit)


def bloch_coordinates(state: Statevector) -> Tuple[float, float, float]:
    """Compute Bloch vector coordinates (x, y, z) from a single-qubit statevector.

    Delegates to state_to_bloch for numerical stability and consistency.
    """
    if state.num_qubits != 1:
        raise ValueError("bloch_coordinates expects a single-qubit statevector")
    return state_to_bloch(state)


def sequence_to_bloch_path(gates: List[str]) -> List[Tuple[float, float, float]]:
    """Return Bloch coordinates after each prefix of the sequence, starting from |0>."""
    circ = prepare_initial_state("|0>")
    path: List[Tuple[float, float, float]] = []
    for idx, gate in enumerate(gates):
        name, angle = parse_gate_token(gate, index=idx)
        build_circuit([(name, angle)], base=circ)
        sv = statevector_after(circ)
        path.append(bloch_coordinates(sv))
    return path


# Numerically stable state->Bloch and metrics ---------------------------------

def state_to_bloch(state: np.ndarray | Statevector) -> Tuple[float, float, float]:
    """Convert a statevector (array or Statevector) into (x, y, z) Bloch coords.

    Uses Pauli expectations; clamps tiny numerical drift to [-1, 1].
    """
    if isinstance(state, Statevector):
        sv = state
    else:
        arr = np.asarray(state, dtype=complex)
        if arr.ndim != 1 or arr.size != 2:
            raise ValueError("state_to_bloch expects a size-2 statevector")
        # Normalize defensively
        norm = np.linalg.norm(arr)
        if norm == 0:
            raise ValueError("Zero statevector")
        sv = Statevector(arr / norm)
    rho = np.outer(sv.data, sv.data.conjugate())
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    x = float(np.real(np.trace(rho @ sx)))
    y = float(np.real(np.trace(rho @ sy)))
    z = float(np.real(np.trace(rho @ sz)))
    def clamp(u: float) -> float:
        return max(-1.0, min(1.0, u))
    return clamp(x), clamp(y), clamp(z)


def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float]:
    """Return (theta, phi) for the 3D unit vector.

    theta: polar angle from +Z in [0, pi]; phi: azimuth from +X in (-pi, pi].
    """
    r = max(1e-12, math.sqrt(x * x + y * y + z * z))
    theta = math.acos(max(-1.0, min(1.0, z / r)))
    phi = math.atan2(y, x)
    return theta, phi


def _statevector_to_tuple(state: Statevector) -> StateTuple:
    data = tuple(complex(val) for val in state.data.flatten())
    if len(data) != 2:
        raise ValueError("Only single-qubit states are supported")
    return data  # type: ignore[return-value]


def simulate_sequence(initial: str, seq_text: str) -> SimulationResult:
    """Simulate a gate sequence, returning coordinates and statevectors after each step.

    The first snapshot corresponds to the prepared initial state. Subsequent snapshots apply each gate in order.
    """
    gates = tuple(parse_gate_sequence(seq_text) if seq_text.strip() else [])
    circuit = prepare_initial_state(initial)

    snapshots: List[Coordinate] = []
    states: List[StateTuple] = []

    sv = statevector_after(circuit)
    snapshots.append(state_to_bloch(sv))
    states.append(_statevector_to_tuple(sv))

    for name, angle in gates:
        build_circuit([(name, angle)], base=circuit)
        sv = statevector_after(circuit)
        snapshots.append(state_to_bloch(sv))
        states.append(_statevector_to_tuple(sv))

    return SimulationResult(gates=gates, coordinates=tuple(snapshots), states=tuple(states))
