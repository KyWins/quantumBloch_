from __future__ import annotations

from typing import Optional

from app.adapters.exporter_qiskit import QiskitExportAdapter
from app.adapters.repository_sqlite import SQLiteCircuitRepository
from app.adapters.simulator_qiskit import QiskitSimulationAdapter
from app.domain.services import SnapshotService

_repository = SQLiteCircuitRepository()
_service: Optional[SnapshotService] = None
_exporter = QiskitExportAdapter()


async def connect_repository() -> None:
    await _repository.connect()


async def disconnect_repository() -> None:
    await _repository.disconnect()


async def get_repository() -> SQLiteCircuitRepository:
    if not _repository.is_connected:
        await _repository.connect()
    return _repository


async def get_snapshot_service() -> SnapshotService:
    global _service
    if _service is None:
        simulator = QiskitSimulationAdapter()
        repo = await get_repository()
        _service = SnapshotService(simulator=simulator, repository=repo, exporter=_exporter)
    return _service
