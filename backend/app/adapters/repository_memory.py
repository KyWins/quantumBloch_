from __future__ import annotations

from copy import deepcopy
from typing import Dict, Iterable, Sequence, Tuple
from uuid import uuid4

from app.domain.models import Circuit, CircuitSummary, Snapshot
from app.domain.ports import CircuitRepositoryPort


class InMemoryCircuitRepository(CircuitRepositoryPort):
    """Simple in-memory store for prototypes and tests."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[str | None, Circuit, Sequence[Snapshot], str]] = {}

    async def save(
        self,
        circuit: Circuit,
        snapshots: Iterable[Snapshot],
        name: str | None = None,
    ) -> str:
        circuit_id = uuid4().hex
        self._store[circuit_id] = (
            name,
            deepcopy(circuit),
            tuple(deepcopy(list(snapshots))),
            "in-memory",
        )
        return circuit_id

    async def load(self, circuit_id: str) -> tuple[Circuit, Sequence[Snapshot], str | None]:
        if circuit_id not in self._store:
            raise KeyError(f"Circuit {circuit_id} not found")
        name, circuit, snapshots, _ = self._store[circuit_id]
        return deepcopy(circuit), tuple(deepcopy(list(snapshots))), name

    async def list(self) -> Sequence[CircuitSummary]:
        summaries: list[CircuitSummary] = []
        for circuit_id, (name, circuit, snapshots, _) in self._store.items():
            summaries.append(
                CircuitSummary(
                    id=circuit_id,
                    name=name,
                    qubit_count=circuit.qubit_count,
                    gate_count=len(circuit.gates),
                    updated_at="in-memory",
                )
            )
        return summaries
