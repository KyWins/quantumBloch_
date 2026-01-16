from __future__ import annotations

from fastapi import APIRouter, Depends

from app.domain.models import Circuit, Gate
from app.domain.noise import NoiseConfig
from app.domain.services import SnapshotService

from .dependencies import get_repository, get_snapshot_service
from ...schemas.circuit import CircuitSchema
from ...schemas.persistence import (
    CircuitSummarySchema,
    SaveCircuitRequest,
    SaveCircuitResponse,
    SavedCircuitResponse,
)
from ...schemas.export import ExportRequest, ExportResponse
from ...schemas.snapshot import BlochSchema, SnapshotSchema

router = APIRouter(prefix="/circuits", tags=["circuits"])


@router.post("/save", response_model=SaveCircuitResponse)
async def save_circuit(payload: SaveCircuitRequest, service: SnapshotService = Depends(get_snapshot_service)):
    circuit = Circuit(qubit_count=payload.circuit.qubit_count, global_phase=payload.circuit.global_phase)
    for gate in payload.circuit.gates:
        circuit.append(
            Gate(
                name=gate.name,
                targets=gate.targets,
                controls=gate.controls,
                parameters=gate.parameters,
                metadata=gate.metadata,
            )
        )
    snapshots = await service.generate(circuit, focus_qubit=payload.focus_qubit)
    circuit_id = await service.save(
        circuit,
        snapshots,
        name=payload.name,
        focus_qubit=payload.focus_qubit,
    )
    return SaveCircuitResponse(id=circuit_id)


@router.get("", response_model=list[CircuitSummarySchema])
async def list_circuits(repository=Depends(get_repository)):
    summaries = await repository.list()
    return [
        CircuitSummarySchema(
            id=item.id,
            name=item.name,
            qubit_count=item.qubit_count,
            gate_count=item.gate_count,
            updated_at=item.updated_at,
        )
        for item in summaries
    ]


@router.get("/{circuit_id}", response_model=SavedCircuitResponse)
async def load_circuit(circuit_id: str, service: SnapshotService = Depends(get_snapshot_service)):
    circuit, snapshots, name, focus_qubit = await service.load(circuit_id)
    gates = [
        {
            "name": gate.name,
            "targets": list(gate.targets),
            "controls": list(gate.controls),
            "parameters": list(gate.parameters),
            "metadata": gate.metadata,
        }
        for gate in circuit.gates
    ]
    circuit_schema = CircuitSchema(
        qubit_count=circuit.qubit_count,
        global_phase=circuit.global_phase,
        gates=gates,
    )
    snapshot_schema = [
        SnapshotSchema(
            step=snap.step,
            bloch=None
            if snap.bloch is None
            else BlochSchema(x=snap.bloch.x, y=snap.bloch.y, z=snap.bloch.z),
            probabilities=snap.probabilities,
            global_phase=snap.global_phase,
            purity=snap.purity,
            radius=snap.bloch_radius,
            focus_qubit=snap.focus_qubit,
            metadata=snap.metadata,
        )
        for snap in snapshots
    ]
    return SavedCircuitResponse(
        id=circuit_id,
        name=name,
        circuit=circuit_schema,
        snapshots=snapshot_schema,
        focus_qubit=focus_qubit,
    )


@router.post("/export", response_model=ExportResponse)
async def export_circuit(payload: ExportRequest, service: SnapshotService = Depends(get_snapshot_service)):
    circuit = Circuit(
        qubit_count=payload.circuit.qubit_count,
        global_phase=payload.circuit.global_phase,
    )
    for gate in payload.circuit.gates:
        circuit.append(
            Gate(
                name=gate.name,
                targets=gate.targets,
                controls=gate.controls,
                parameters=gate.parameters,
                metadata=gate.metadata,
            )
        )

    qasm, snapshot_json, share_id, snapshots = await service.export(
        circuit,
        noise=NoiseConfig.from_dict(payload.noise),
        focus_qubit=payload.focus_qubit,
        share=payload.share,
        name=payload.name,
    )
    return ExportResponse(
        qasm=qasm,
        snapshot_json=snapshot_json,
        snapshot_count=len(snapshots),
        share_id=share_id,
    )
