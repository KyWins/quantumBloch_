from __future__ import annotations

import json
from typing import Sequence

from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps as qasm3_dumps

from app.domain.models import Circuit, Snapshot
from app.domain.ports import ExportPort
from .qiskit_common import apply_gate_to_circuit


class QiskitExportAdapter(ExportPort):
    """Export adapter producing OpenQASM 3 and JSON snapshot payloads."""

    async def export_qasm(self, circuit: Circuit) -> str:
        qc = self._build_circuit(circuit)
        return qasm3_dumps(qc)

    async def export_json(self, snapshots: Sequence[Snapshot]) -> str:
        data = []
        for snap in snapshots:
            entry: dict[str, object] = {
                "step": snap.step,
                "probabilities": snap.probabilities,
                "purity": snap.purity,
                "radius": snap.bloch_radius,
                "global_phase": snap.global_phase,
                "focus_qubit": snap.focus_qubit,
                "metadata": snap.metadata,
            }
            if snap.bloch:
                entry["bloch"] = {"x": snap.bloch.x, "y": snap.bloch.y, "z": snap.bloch.z}
            if snap.statevector is not None:
                entry["statevector"] = [
                    {"re": float(complex(val).real), "im": float(complex(val).imag)}
                    for val in snap.statevector
                ]
            if snap.density_matrix is not None:
                entry["density_matrix"] = [
                    {"re": float(complex(val).real), "im": float(complex(val).imag)}
                    for val in snap.density_matrix
                ]
            data.append(entry)
        return json.dumps(data, indent=2)

    def _build_circuit(self, circuit: Circuit) -> QuantumCircuit:
        qc = QuantumCircuit(circuit.qubit_count)
        if circuit.global_phase:
            qc.global_phase = circuit.global_phase  # type: ignore[assignment]

        for gate in circuit.gates:
            apply_gate_to_circuit(qc, gate)
        return qc
