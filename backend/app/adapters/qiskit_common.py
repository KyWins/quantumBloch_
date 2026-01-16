from __future__ import annotations

from qiskit import QuantumCircuit

from app.domain.models import Gate


def apply_gate_to_circuit(qc: QuantumCircuit, gate: Gate) -> None:
    """Apply a domain Gate onto the provided QuantumCircuit."""

    name = gate.name.upper()
    targets = list(gate.targets)
    controls = list(gate.controls)
    params = list(gate.parameters)

    if name == "I":
        qc.id(targets)
    elif name == "X":
        qc.x(targets)
    elif name == "Y":
        qc.y(targets)
    elif name == "Z":
        qc.z(targets)
    elif name == "H":
        qc.h(targets)
    elif name == "S":
        qc.s(targets)
    elif name in {"SDG", "S†"}:
        qc.sdg(targets)
    elif name == "T":
        qc.t(targets)
    elif name in {"TDG", "T†"}:
        qc.tdg(targets)
    elif name == "SX":
        qc.sx(targets)
    elif name in {"SXDG", "SX†"}:
        qc.sxdg(targets)
    elif name == "P":
        angle = params[0] if params else 0.0
        for qubit in targets:
            qc.p(angle, qubit)
    elif name == "RX":
        angle = params[0]
        for qubit in targets:
            qc.rx(angle, qubit)
    elif name == "RY":
        angle = params[0]
        for qubit in targets:
            qc.ry(angle, qubit)
    elif name == "RZ":
        angle = params[0]
        for qubit in targets:
            qc.rz(angle, qubit)
    elif name in {"CX", "CNOT"}:
        if len(controls) != 1 or len(targets) != 1:
            raise ValueError("CX requires one control and one target")
        if set(controls) & set(targets):
            raise ValueError("Control and target must be distinct for CX")
        qc.cx(controls[0], targets[0])
    elif name == "CZ":
        if len(controls) != 1 or len(targets) != 1:
            raise ValueError("CZ requires one control and one target")
        if set(controls) & set(targets):
            raise ValueError("Control and target must be distinct for CZ")
        qc.cz(controls[0], targets[0])
    elif name == "RESET":
        for qubit in targets:
            qc.reset(qubit)
    elif name in {"DEPOLARIZING", "AMP_DAMP", "PHASE_DAMP"}:
        # Noise placeholders – actual noise handled separately via density evolution.
        return
    elif name in {"MEASURE_Z", "MEASURE_X", "MEASURE_Y"}:
        # Measurement annotations are metadata only; no-op in simulation circuit.
        return
    else:
        raise ValueError(f"Unsupported gate: {gate.name}")
