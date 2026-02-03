from __future__ import annotations

import json
from datetime import datetime
from typing import Iterable, Sequence
from uuid import uuid4

from databases import Database

from app.domain.models import BlochVector, Circuit, CircuitSummary, Gate, Snapshot
from app.domain.ports import CircuitRepositoryPort


class SQLiteCircuitRepository(CircuitRepositoryPort):
    """SQLite-backed circuit persistence using the databases async client."""

    def __init__(self, database_url: str = "sqlite:///./circuits.db") -> None:
        self._database = Database(database_url)
        self._connected = False
        self._init_query = (
            """
            CREATE TABLE IF NOT EXISTS circuits (
                id TEXT PRIMARY KEY,
                name TEXT,
                qubit_count INTEGER NOT NULL,
                global_phase REAL,
                gates TEXT NOT NULL,
                snapshots TEXT NOT NULL,
                focus_qubit INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        if self._connected:
            return
        await self._database.connect()
        await self._database.execute(self._init_query)
        await self._ensure_focus_column()
        self._connected = True

    async def disconnect(self) -> None:
        if not self._connected:
            return
        await self._database.disconnect()
        self._connected = False

    async def save(
        self,
        circuit: Circuit,
        snapshots: Iterable[Snapshot],
        *,
        name: str | None = None,
        focus_qubit: int | None = None,
    ) -> str:
        circuit_id = uuid4().hex
        gates_payload = [
            {
                "name": gate.name,
                "targets": list(gate.targets),
                "controls": list(gate.controls),
                "parameters": list(gate.parameters),
                "metadata": gate.metadata,
            }
            for gate in circuit.gates
        ]
        snapshot_payload = []
        for snap in snapshots:
            serialized_state = (
                [
                    {"re": float(complex(val).real), "im": float(complex(val).imag)}
                    for val in snap.statevector
                ]
                if snap.statevector is not None
                else None
            )
            serialized_density = (
                [
                    {"re": float(complex(val).real), "im": float(complex(val).imag)}
                    for val in snap.density_matrix
                ]
                if snap.density_matrix is not None
                else None
            )
            snapshot_payload.append(
                {
                    "step": snap.step,
                    "statevector": serialized_state,
                    "density_matrix": serialized_density,
                    "bloch": None
                    if snap.bloch is None
                    else {"x": snap.bloch.x, "y": snap.bloch.y, "z": snap.bloch.z},
                    "probabilities": snap.probabilities,
                    "global_phase": snap.global_phase,
                    "purity": snap.purity,
                    "radius": snap.bloch_radius,
                    "focus_qubit": snap.focus_qubit,
                    "metadata": snap.metadata,
                }
            )
        query = (
            "INSERT INTO circuits "
            "(id, name, qubit_count, global_phase, gates, snapshots, focus_qubit) "
            "VALUES "
            "(:id, :name, :qubit_count, :global_phase, :gates, :snapshots, :focus_qubit)"
        )
        await self._database.execute(
            query,
            {
                "id": circuit_id,
                "name": name,
                "qubit_count": circuit.qubit_count,
                "global_phase": circuit.global_phase,
                "gates": json.dumps(gates_payload),
                "snapshots": json.dumps(snapshot_payload),
                "focus_qubit": focus_qubit,
            },
        )
        return circuit_id

    async def load(
        self, circuit_id: str
    ) -> tuple[Circuit, Sequence[Snapshot], str | None, int | None]:
        query = (
            "SELECT name, qubit_count, global_phase, gates, snapshots, focus_qubit "
            "FROM circuits WHERE id = :id"
        )
        row = await self._database.fetch_one(query, {"id": circuit_id})
        if row is None:
            raise KeyError(f"Circuit {circuit_id} not found")

        name = row["name"]
        gates_payload = json.loads(row["gates"])
        snapshots_payload = json.loads(row["snapshots"])

        circuit = Circuit(qubit_count=row["qubit_count"], global_phase=row["global_phase"])
        for gate in gates_payload:
            circuit.append(
                Gate(
                    name=gate["name"],
                    targets=tuple(gate["targets"]),
                    controls=tuple(gate.get("controls", [])),
                    parameters=tuple(gate.get("parameters", [])),
                    metadata=gate.get("metadata", {}),
                )
            )

        snapshots: list[Snapshot] = []
        for snap in snapshots_payload:
            bloch_payload = snap.get("bloch")
            bloch = (
                None
                if bloch_payload is None
                else BlochVector(
                    x=bloch_payload.get("x", 0.0),
                    y=bloch_payload.get("y", 0.0),
                    z=bloch_payload.get("z", 0.0),
                )
            )
            statevector_payload = snap.get("statevector")
            statevector = (
                tuple(
                    complex(item.get("re", 0.0), item.get("im", 0.0))
                    for item in statevector_payload
                )
                if statevector_payload
                else None
            )
            density_payload = snap.get("density_matrix")
            density_matrix = (
                tuple(
                    complex(item.get("re", 0.0), item.get("im", 0.0))
                    for item in density_payload
                )
                if density_payload
                else None
            )
            snapshots.append(
                Snapshot(
                    step=snap["step"],
                    statevector=statevector,
                    density_matrix=density_matrix,
                    bloch=bloch,
                    probabilities=tuple(snap.get("probabilities", [])) or None,
                    global_phase=snap.get("global_phase"),
                    purity=snap.get("purity"),
                    bloch_radius=snap.get("radius"),
                    focus_qubit=snap.get("focus_qubit"),
                    metadata=snap.get("metadata", {}),
                )
            )
        return circuit, snapshots, name, row["focus_qubit"]

    async def list(self) -> Sequence[CircuitSummary]:
        query = (
            "SELECT id, name, qubit_count, gates, updated_at "
            "FROM circuits ORDER BY updated_at DESC"
        )
        rows = await self._database.fetch_all(query)
        summaries: list[CircuitSummary] = []
        for row in rows:
            gates_payload = json.loads(row["gates"])
            updated_at = row["updated_at"]
            if isinstance(updated_at, datetime):
                updated = updated_at.isoformat()
            else:
                updated = str(updated_at)
            summaries.append(
                CircuitSummary(
                    id=row["id"],
                    name=row["name"],
                    qubit_count=row["qubit_count"],
                    gate_count=len(gates_payload),
                    updated_at=updated,
                )
            )
        return summaries

    async def _ensure_focus_column(self) -> None:
        info_rows = await self._database.fetch_all("PRAGMA table_info(circuits)")
        if not any(row["name"] == "focus_qubit" for row in info_rows):
            await self._database.execute("ALTER TABLE circuits ADD COLUMN focus_qubit INTEGER")
