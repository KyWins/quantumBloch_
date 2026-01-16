from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace
from qiskit.quantum_info.operators.channel import Kraus

from app.domain.models import BlochVector, Circuit, Gate, Snapshot
from app.domain.noise import NoiseConfig
from app.domain.ports import SimulationPort
from .qiskit_common import apply_gate_to_circuit


class QiskitSimulationAdapter(SimulationPort):
    """Qiskit-backed statevector simulator producing per-step snapshots."""

    async def simulate(
        self,
        circuit: Circuit,
        noise: NoiseConfig | None = None,
        *,
        focus_qubit: int | None = None,
    ) -> Sequence[Snapshot]:
        return self._simulate_all(circuit, noise=noise, focus_qubit=focus_qubit)

    async def simulate_partial(
        self,
        circuit: Circuit,
        *,
        start_step: int,
        noise: NoiseConfig | None = None,
        focus_qubit: int | None = None,
    ) -> Sequence[Snapshot]:
        # For now we recompute from scratch and slice from start_step onward.
        snapshots = self._simulate_all(circuit, noise=noise, focus_qubit=focus_qubit)
        return snapshots[start_step:]

    # ------------------------------------------------------------------
    # Internal helpers

    def _simulate_all(
        self,
        circuit: Circuit,
        noise: NoiseConfig | None = None,
        focus_qubit: int | None = None,
    ) -> List[Snapshot]:
        num_qubits = circuit.qubit_count
        snapshots: List[Snapshot] = []

        density = DensityMatrix.from_label("0" * num_qubits)
        state: Optional[Statevector] = Statevector.from_label("0" * num_qubits)
        focus = 0 if focus_qubit is None else int(focus_qubit)
        if focus < 0 or focus >= num_qubits:
            focus = 0

        if circuit.global_phase:
            phase = float(circuit.global_phase)
            if state is not None:
                state = state * np.exp(1j * phase)
            # Global phase does not impact density matrix (remains unchanged).

        snapshots.append(
            self._build_snapshot(
                step=0,
                density=density,
                state=state,
                focus_qubit=focus,
                metadata={"gate": "INIT"},
            )
        )

        for idx, gate in enumerate(circuit.gates, start=1):
            single_gate = QuantumCircuit(num_qubits)
            apply_gate_to_circuit(single_gate, gate)
            density = density.evolve(single_gate)
            if state is not None:
                state = state.evolve(single_gate)

            if noise and noise.enabled:
                density = self._apply_noise(density, noise)
                state = None

            snapshots.append(
                self._build_snapshot(
                    step=idx,
                    density=density,
                    state=state,
                    focus_qubit=focus,
                    metadata={
                        "gate": gate.name,
                        "targets": ",".join(str(t) for t in gate.targets),
                        "controls": ",".join(str(c) for c in gate.controls) if gate.controls else "",
                    },
                )
            )

        return snapshots

    def _apply_noise(self, density: DensityMatrix, noise: NoiseConfig) -> DensityMatrix:
        num_qubits = density.num_qubits
        updated = density
        depol = float(noise.depolarizing or 0.0)
        amp = float(noise.amplitude_damping or 0.0)
        phase = float(noise.phase_damping or 0.0)

        for qubit in range(num_qubits):
            if depol > 0.0:
                updated = updated.evolve(self._depolarizing_channel(depol), qargs=[qubit])
            if amp > 0.0:
                updated = updated.evolve(self._amplitude_channel(amp), qargs=[qubit])
            if phase > 0.0:
                updated = updated.evolve(self._phase_channel(phase), qargs=[qubit])
        return updated

    @staticmethod
    def _depolarizing_channel(p: float) -> Kraus:
        p = float(min(max(p, 0.0), 1.0))
        alpha = np.sqrt(max(0.0, 1.0 - 3.0 * p / 4.0))
        beta = np.sqrt(p / 4.0)
        identity = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=complex)
        pauli_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
        pauli_y = np.array([[0.0, -1j], [1j, 0.0]], dtype=complex)
        pauli_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
        return Kraus([alpha * identity, beta * pauli_x, beta * pauli_y, beta * pauli_z])

    @staticmethod
    def _amplitude_channel(gamma: float) -> Kraus:
        gamma = float(min(max(gamma, 0.0), 1.0))
        keep = np.sqrt(max(0.0, 1.0 - gamma))
        k0 = np.array([[1.0, 0.0], [0.0, keep]], dtype=complex)
        k1 = np.array([[0.0, np.sqrt(gamma)], [0.0, 0.0]], dtype=complex)
        return Kraus([k0, k1])

    @staticmethod
    def _phase_channel(lam: float) -> Kraus:
        lam = float(min(max(lam, 0.0), 1.0))
        keep = np.sqrt(max(0.0, 1.0 - lam))
        k0 = keep * np.eye(2, dtype=complex)
        k1 = np.sqrt(lam) * np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
        k2 = np.sqrt(lam) * np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
        return Kraus([k0, k1, k2])

    def _build_snapshot(
        self,
        *,
        step: int,
        density: DensityMatrix,
        state: Optional[Statevector],
        focus_qubit: int,
        metadata: Optional[dict[str, str]] = None,
    ) -> Snapshot:
        focus = max(0, min(focus_qubit, density.num_qubits - 1))
        if density.num_qubits == 1:
            reduced = density
        else:
            trace_qargs = [idx for idx in range(density.num_qubits) if idx != focus]
            reduced = partial_trace(density, trace_qargs)
            if not isinstance(reduced, DensityMatrix):
                reduced = DensityMatrix(reduced)
        rho = reduced.data
        bloch = BlochVector(
            x=float(2 * np.real(rho[0, 1])),
            y=float(2 * np.imag(rho[1, 0])),
            z=float(np.real(rho[0, 0] - rho[1, 1])),
        )
        probabilities = (
            float(np.real(rho[0, 0])),
            float(np.real(rho[1, 1])),
        )
        radius = float(np.sqrt(bloch.x**2 + bloch.y**2 + bloch.z**2))
        purity = float(np.real(np.trace(rho @ rho)))
        statevector = tuple(state.data.tolist()) if state is not None else None
        density_matrix = tuple(density.data.flatten().tolist())

        return Snapshot(
            step=step,
            statevector=statevector,
            density_matrix=density_matrix,
            bloch=bloch,
            probabilities=probabilities,
            global_phase=None,
            purity=purity,
            bloch_radius=radius,
            focus_qubit=focus,
            metadata=metadata or {},
        )
