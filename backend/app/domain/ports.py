from __future__ import annotations

from typing import Iterable, Protocol, Sequence

from .models import Circuit, CircuitSummary, Snapshot
from .noise import NoiseConfig


class SimulationPort(Protocol):
    """Simulation engine interface (e.g., Qiskit adapter)."""

    async def simulate(
        self,
        circuit: Circuit,
        *,
        noise: NoiseConfig | None = None,
        focus_qubit: int | None = None,
    ) -> Sequence[Snapshot]:
        ...

    async def simulate_partial(
        self,
        circuit: Circuit,
        *,
        start_step: int,
        noise: NoiseConfig | None = None,
        focus_qubit: int | None = None,
    ) -> Sequence[Snapshot]:
        ...


class CircuitRepositoryPort(Protocol):
    """Persistence boundary for saved circuits and snapshots."""

    async def save(
        self,
        circuit: Circuit,
        snapshots: Iterable[Snapshot],
        *,
        name: str | None = None,
        focus_qubit: int | None = None,
    ) -> str:
        ...

    async def load(
        self,
        circuit_id: str
    ) -> tuple[Circuit, Sequence[Snapshot], str | None, int | None]:
        ...

    async def list(self) -> Sequence[CircuitSummary]:
        ...


class ExportPort(Protocol):
    """Transform circuits/snapshots into export formats (QASM, JSON, etc.)."""

    async def export_qasm(self, circuit: Circuit) -> str:
        ...

    async def export_json(self, snapshots: Sequence[Snapshot]) -> str:
        ...
