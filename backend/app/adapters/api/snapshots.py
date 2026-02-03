from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.domain.models import Circuit, Gate
from app.domain.noise import NoiseConfig
from app.domain.services import SnapshotService

from ...config import get_settings
from ...schemas.measurement import MeasurementRequest, MeasurementResponse
from ...schemas.simulate import SimulateRequest
from ...schemas.snapshot import BlochSchema, SnapshotSchema
from .dependencies import get_snapshot_service

router = APIRouter(prefix="/circuits", tags=["circuits"])


@router.post("/simulate", response_model=dict[str, list[SnapshotSchema]])
async def simulate(
    payload: SimulateRequest,
    service: SnapshotService = Depends(get_snapshot_service),
):
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
                metadata=dict(gate.metadata),
            )
        )

    try:
        snapshots = await service.generate(
            circuit,
            noise=NoiseConfig.from_dict(payload.noise),
            focus_qubit=payload.focus_qubit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    schema_snapshots: list[SnapshotSchema] = []
    for snap in snapshots:
        schema_snapshots.append(
            SnapshotSchema(
                step=snap.step,
                bloch=BlochSchema(x=snap.bloch.x, y=snap.bloch.y, z=snap.bloch.z)
                if snap.bloch
                else None,
                probabilities=snap.probabilities,
                global_phase=snap.global_phase,
                purity=snap.purity,
                radius=snap.bloch_radius,
                focus_qubit=snap.focus_qubit,
                metadata=snap.metadata,
            )
        )

    return {"snapshots": [schema.model_dump() for schema in schema_snapshots]}


@router.post("/measure", response_model=MeasurementResponse)
async def measure(
    payload: MeasurementRequest,
    service: SnapshotService = Depends(get_snapshot_service),
):
    settings = get_settings()
    if payload.shots > settings.max_shots:
        raise HTTPException(status_code=400, detail=f"shots must be <= {settings.max_shots}")

    circuit = Circuit(qubit_count=payload.circuit.qubit_count)
    for gate in payload.circuit.gates:
        circuit.append(
            Gate(
                name=gate.name,
                targets=gate.targets,
                controls=gate.controls,
                parameters=gate.parameters,
                metadata=dict(gate.metadata),
            )
        )

    result = await service.measure(
        circuit,
        basis=payload.basis,
        shots=payload.shots,
        seed=payload.seed,
        noise=NoiseConfig.from_dict(payload.noise),
        focus_qubit=payload.focus_qubit,
    )
    return MeasurementResponse(
        step=result.step,
        basis=result.basis,
        shots=result.shots,
        counts=result.counts,
        probabilities=result.probabilities,
        overlay_vector=result.overlay_vector,
        samples=result.samples,
        mean=result.mean,
        standard_deviation=result.standard_deviation,
        longest_run=result.longest_run,
        longest_symbol=result.longest_symbol,
        switches=result.switches,
    )
