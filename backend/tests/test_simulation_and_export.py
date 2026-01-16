from __future__ import annotations

import json
from typing import Tuple

import pytest

from app.adapters.exporter_qiskit import QiskitExportAdapter
from app.adapters.repository_sqlite import SQLiteCircuitRepository
from app.adapters.simulator_qiskit import QiskitSimulationAdapter
from app.domain.models import BlochVector, Circuit, Gate, Snapshot
from app.domain.noise import NoiseConfig
from app.domain.services import SnapshotService
from app.domain.ports import CircuitRepositoryPort, SimulationPort


def _build_simple_circuit() -> Circuit:
    circuit = Circuit(qubit_count=1)
    circuit.append(Gate(name="H", targets=(0,)))
    circuit.append(Gate(name="RZ", targets=(0,), parameters=(3.14159 / 2,)))
    return circuit


@pytest.mark.asyncio
async def test_noise_reduces_radius_and_purity() -> None:
    circuit = _build_simple_circuit()
    simulator = QiskitSimulationAdapter()

    clean = await simulator.simulate(circuit)
    noisy = await simulator.simulate(
        circuit,
        noise=NoiseConfig(depolarizing=0.2, phase_damping=0.1),
    )

    clean_radius = clean[-1].bloch_radius
    noisy_radius = noisy[-1].bloch_radius
    clean_purity = clean[-1].purity
    noisy_purity = noisy[-1].purity

    assert clean_radius is not None and noisy_radius is not None
    assert clean_purity is not None and noisy_purity is not None
    assert noisy_radius < clean_radius
    assert noisy_purity < clean_purity


@pytest.mark.asyncio
async def test_exporter_produces_qasm_and_snapshot_json() -> None:
    circuit = _build_simple_circuit()
    simulator = QiskitSimulationAdapter()
    exporter = QiskitExportAdapter()

    snapshots = await simulator.simulate(circuit)
    qasm = await exporter.export_qasm(circuit)
    snapshot_json = await exporter.export_json(snapshots)

    assert "OPENQASM 3" in qasm

    payload = json.loads(snapshot_json)
    assert isinstance(payload, list)
    assert payload[-1]["step"] == snapshots[-1].step
    assert "bloch" in payload[-1]


@pytest.mark.asyncio
async def test_focus_qubit_changes_reduced_state() -> None:
    circuit = Circuit(qubit_count=2)
    circuit.append(Gate(name="H", targets=(0,)))
    circuit.append(Gate(name="CX", targets=(1,), controls=(0,)))

    simulator = QiskitSimulationAdapter()
    snapshots_focus0 = await simulator.simulate(circuit, focus_qubit=0)
    snapshots_focus1 = await simulator.simulate(circuit, focus_qubit=1)

    final0 = snapshots_focus0[-1]
    final1 = snapshots_focus1[-1]

    assert final0.focus_qubit == 0
    assert final1.focus_qubit == 1
    assert final0.purity is not None and final1.purity is not None
    assert pytest.approx(final0.purity, rel=1e-6) == final1.purity
    assert snapshots_focus0[1].metadata.get("gate") == "H"
    assert snapshots_focus0[2].metadata.get("gate") == "CX"


@pytest.mark.asyncio
async def test_repository_persists_focus(tmp_path) -> None:
    repo = SQLiteCircuitRepository(f"sqlite:///{tmp_path / 'circuits.db'}")
    await repo.connect()

    circuit = _build_simple_circuit()
    simulator = QiskitSimulationAdapter()
    snapshots = await simulator.simulate(circuit, focus_qubit=0)

    circuit_id = await repo.save(circuit, snapshots, name="focus", focus_qubit=0)
    _, loaded_snapshots, name, focus = await repo.load(circuit_id)

    assert name == "focus"
    assert focus == 0
    assert loaded_snapshots[-1].focus_qubit == 0

    await repo.disconnect()


class _StubRepository(CircuitRepositoryPort):
    async def save(self, circuit, snapshots, *, name=None, focus_qubit=None):  # type: ignore[override]
        return "stub"

    async def load(self, circuit_id):  # type: ignore[override]
        raise NotImplementedError

    async def list(self):  # type: ignore[override]
        return []


@pytest.mark.asyncio
async def test_measurement_returns_samples_and_stats() -> None:
    circuit = _build_simple_circuit()
    simulator = QiskitSimulationAdapter()
    service = SnapshotService(simulator=simulator, repository=_StubRepository())

    result = await service.measure(circuit, basis="Z", shots=64)

    assert result.samples
    assert len(result.samples) == 64
    assert -1.0 <= result.mean <= 1.0
    assert result.standard_deviation >= 0.0
    assert result.longest_run >= 1
    assert result.switches >= 0
    assert result.longest_symbol in {"plus", "minus"}


def _fake_snapshots() -> Tuple[Snapshot, ...]:
    return (
        Snapshot(
            step=0,
            statevector=tuple(),
            density_matrix=None,
            bloch=BlochVector(0.0, 0.0, 1.0),
            probabilities=(1.0, 0.0),
            metadata={"gate": "INIT"},
        ),
        Snapshot(
            step=1,
            statevector=tuple(),
            density_matrix=None,
            bloch=BlochVector(0.0, 0.0, 1.0),
            probabilities=(1.0, 0.0),
            metadata={"gate": "H"},
        ),
    )


class _CountingSimulator(SimulationPort):
    def __init__(self) -> None:
        self.calls: list[tuple[int | None, tuple[float, float, float] | None]] = []
        self.snapshots = _fake_snapshots()

    async def simulate(self, circuit, noise=None, focus_qubit=None):  # type: ignore[override]
        self.calls.append((focus_qubit, None if noise is None else (
            float(noise.depolarizing or 0.0),
            float(noise.amplitude_damping or 0.0),
            float(noise.phase_damping or 0.0),
        )))
        return self.snapshots

    async def simulate_partial(self, circuit, *, start_step, noise=None, focus_qubit=None):  # type: ignore[override]
        return self.snapshots[start_step:]


@pytest.mark.asyncio
async def test_snapshot_cache_reuses_results() -> None:
    circuit = _build_simple_circuit()
    simulator = _CountingSimulator()
    service = SnapshotService(simulator=simulator, repository=_StubRepository())

    await service.generate(circuit, focus_qubit=0)
    assert len(simulator.calls) == 1

    await service.generate(circuit, focus_qubit=0)
    assert len(simulator.calls) == 1  # reused cache

    await service.generate(circuit, focus_qubit=1)
    assert len(simulator.calls) == 2  # new focus -> new sim

    await service.measure(circuit, basis="Z", shots=8, focus_qubit=1)
    assert len(simulator.calls) == 2  # measure uses cached snapshot for focus 1
