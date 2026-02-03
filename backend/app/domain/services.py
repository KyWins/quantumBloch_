from __future__ import annotations

import logging
from typing import Dict, Hashable, Optional, Sequence, Tuple

import numpy as np

from .models import BlochVector, Circuit, MeasurementResult, Snapshot
from .noise import NoiseConfig
from .ports import CircuitRepositoryPort, ExportPort, SimulationPort

logger = logging.getLogger(__name__)


class SnapshotService:
    """Coordinates simulations and persistence of circuit snapshots."""

    def __init__(
        self,
        simulator: SimulationPort,
        repository: CircuitRepositoryPort,
        exporter: ExportPort | None = None,
    ):
        self._simulator = simulator
        self._repository = repository
        self._exporter = exporter
        self._snapshot_cache: Dict[Hashable, Tuple[Snapshot, ...]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    async def generate(
        self,
        circuit: Circuit,
        *,
        noise: Optional[NoiseConfig] = None,
        focus_qubit: Optional[int] = None,
    ) -> Sequence[Snapshot]:
        return await self._fetch_snapshots(
            circuit,
            noise=noise,
            focus_qubit=focus_qubit,
            start_step=None,
        )

    async def regenerate_from(
        self,
        circuit: Circuit,
        start_step: int,
        *,
        noise: Optional[NoiseConfig] = None,
        focus_qubit: Optional[int] = None,
    ) -> Sequence[Snapshot]:
        return await self._fetch_snapshots(
            circuit,
            noise=noise,
            focus_qubit=focus_qubit,
            start_step=start_step,
        )

    async def save(
        self,
        circuit: Circuit,
        snapshots: Sequence[Snapshot],
        *,
        name: str | None = None,
        focus_qubit: Optional[int] = None,
    ) -> str:
        key = self._cache_key(circuit, None, focus_qubit)
        self._snapshot_cache[key] = tuple(snapshots)
        return await self._repository.save(
            circuit,
            snapshots,
            name=name,
            focus_qubit=focus_qubit,
        )
        # cache already updated by generate/regenerate

    async def load(
        self,
        circuit_id: str
    ) -> tuple[Circuit, Sequence[Snapshot], str | None, int | None]:
        return await self._repository.load(circuit_id)

    async def export(
        self,
        circuit: Circuit,
        *,
        noise: Optional[NoiseConfig] = None,
        focus_qubit: Optional[int] = None,
        share: bool = False,
        name: str | None = None,
    ) -> tuple[str, str, Optional[str], Sequence[Snapshot]]:
        if self._exporter is None:
            raise RuntimeError("Export functionality not configured")

        snapshots = await self.generate(circuit, noise=noise, focus_qubit=focus_qubit)
        qasm = await self._exporter.export_qasm(circuit)
        snapshot_json = await self._exporter.export_json(snapshots)
        share_id: Optional[str] = None

        if share:
            share_id = await self.save(
                circuit,
                snapshots,
                name=name,
                focus_qubit=focus_qubit,
            )

        return qasm, snapshot_json, share_id, snapshots

    async def measure(
        self,
        circuit: Circuit,
        basis: str,
        shots: int,
        *,
        noise: Optional[NoiseConfig] = None,
        focus_qubit: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> MeasurementResult:
        snapshots = await self._fetch_snapshots(
            circuit,
            noise=noise,
            focus_qubit=focus_qubit,
            start_step=None,
        )
        final = snapshots[-1]

        bloch = final.bloch or BlochVector(x=0.0, y=0.0, z=1.0)
        if isinstance(bloch, BlochVector):
            bloch_vec = (bloch.x, bloch.y, bloch.z)
        else:
            bloch_vec = bloch  # type: ignore[assignment]

        if noise and noise.enabled:
            bloch_vec = self._apply_noise(bloch_vec, noise)

        axis_map = {
            "Z": (0.0, 0.0, 1.0),
            "X": (1.0, 0.0, 0.0),
            "Y": (0.0, 1.0, 0.0),
        }
        axis = axis_map.get(basis.upper(), axis_map["Z"])
        dot = bloch_vec[0] * axis[0] + bloch_vec[1] * axis[1] + bloch_vec[2] * axis[2]
        dot = max(-1.0, min(1.0, dot))
        p_plus = (1.0 + dot) / 2.0
        p_minus = 1.0 - p_plus

        rng = np.random.default_rng(seed)
        sample_sequence = rng.choice(["plus", "minus"], size=shots, p=[p_plus, p_minus])
        counts = {
            "plus": int(np.count_nonzero(sample_sequence == "plus")),
            "minus": int(np.count_nonzero(sample_sequence == "minus")),
        }
        overlay = axis if counts["plus"] >= counts["minus"] else (-axis[0], -axis[1], -axis[2])

        numeric_samples = np.where(sample_sequence == "plus", 1.0, -1.0)
        mean = float(np.mean(numeric_samples))
        std_dev = float(np.std(numeric_samples))
        longest_run, longest_symbol, switches = self._analyze_runs(sample_sequence.tolist())

        return MeasurementResult(
            step=final.step,
            basis=basis.upper(),
            shots=shots,
            counts=counts,
            probabilities={"plus": p_plus, "minus": p_minus},
            overlay_vector=overlay,
            samples=tuple(str(value) for value in sample_sequence.tolist()),
            mean=mean,
            standard_deviation=std_dev,
            longest_run=longest_run,
            longest_symbol=longest_symbol,
            switches=switches,
        )

    def _apply_noise(
        self, bloch: tuple[float, float, float], noise: NoiseConfig
    ) -> tuple[float, float, float]:
        x, y, z = bloch
        # Depolarizing shrinks the Bloch radius uniformly.
        if noise.depolarizing:
            shrink = max(0.0, 1.0 - float(noise.depolarizing) * 2.0)
            x *= shrink
            y *= shrink
            z *= shrink

        # Phase damping primarily attenuates transverse components (x,y).
        if noise.phase_damping:
            phase = max(0.0, 1.0 - float(noise.phase_damping))
            x *= phase
            y *= phase

        # Amplitude damping biases toward |0⟩ (z -> 1).
        if noise.amplitude_damping:
            amp = float(noise.amplitude_damping)
            z = z * (1 - amp) + amp

        return (
            max(-1.0, min(1.0, x)),
            max(-1.0, min(1.0, y)),
            max(-1.0, min(1.0, z)),
        )

    def _analyze_runs(self, sequence: list[str]) -> tuple[int, str, int]:
        if not sequence:
            return 0, "", 0
        longest_len = 1
        longest_value = sequence[0]
        current_len = 1
        switches = 0
        for prev, current in zip(sequence, sequence[1:]):
            if current == prev:
                current_len += 1
            else:
                switches += 1
                if current_len > longest_len:
                    longest_len = current_len
                    longest_value = prev
                current_len = 1
        if current_len > longest_len:
            longest_len = current_len
            longest_value = sequence[-1]
        return longest_len, longest_value, switches

    def _cache_key(
        self,
        circuit: Circuit,
        noise: Optional[NoiseConfig],
        focus_qubit: Optional[int],
    ) -> Hashable:
        gate_fingerprint = tuple(
            (
                gate.name,
                tuple(gate.targets),
                tuple(gate.controls),
                tuple(gate.parameters),
            )
            for gate in circuit.gates
        )
        noise_tuple = (
            None
            if noise is None
            else (
                float(noise.depolarizing or 0.0),
                float(noise.amplitude_damping or 0.0),
                float(noise.phase_damping or 0.0),
            )
        )
        return (
            circuit.qubit_count,
            circuit.global_phase,
            gate_fingerprint,
            noise_tuple,
            focus_qubit,
        )

    async def _fetch_snapshots(
        self,
        circuit: Circuit,
        *,
        noise: Optional[NoiseConfig],
        focus_qubit: Optional[int],
        start_step: Optional[int],
    ) -> Tuple[Snapshot, ...]:
        key = self._cache_key(circuit, noise, focus_qubit)
        cached = self._snapshot_cache.get(key)
        if cached is not None:
            self._cache_hits += 1
            return cached if start_step is None else cached[start_step:]

        self._cache_misses += 1
        snapshots = await self._simulator.simulate(
            circuit,
            noise=noise,
            focus_qubit=focus_qubit,
        )
        cached_tuple = tuple(snapshots)
        self._snapshot_cache[key] = cached_tuple
        logger.debug(
            "Cached %d snapshots for key %s (focus=%s)",
            len(cached_tuple),
            hash(key),
            focus_qubit,
        )
        return cached_tuple if start_step is None else cached_tuple[start_step:]

    def cache_stats(self) -> dict[str, float | int]:
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total) if total else 1.0
        return {
            "entries": len(self._snapshot_cache),
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
        }
