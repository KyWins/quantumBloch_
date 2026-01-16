from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils.gate_utils import (
    GateParseError,
    SimulationResult,
    cartesian_to_spherical,
    simulate_sequence,
)

app = FastAPI(title="Bloch Sphere API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://127.0.0.1:8501", "http://localhost:8000", "http://localhost:8501"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["content-type"],
)


class SequenceRequest(BaseModel):
    sequence: Optional[List[str]] = None
    sequence_text: Optional[str] = None
    preset: Optional[str] = "|0>"


def _normalize_preset(preset: Optional[str]) -> str:
    if not preset:
        return "|0>"
    preset = preset.strip()
    aliases = {
        "|0⟩": "|0>",
        "|+⟩": "|+>",
        "|i⟩": "|i>",
    }
    normalized = aliases.get(preset, preset)
    if normalized not in {"|0>", "|+>", "|i>"}:
        raise HTTPException(status_code=422, detail=f"Unsupported preset '{preset}'")
    return normalized


def _format_gate(gate: tuple[str, Optional[float]]) -> str:
    name, angle = gate
    return f"{name}({angle:.6f})" if angle is not None else name


def _state_probabilities(state: tuple[complex, complex]) -> tuple[float, float]:
    p0 = float(abs(state[0]) ** 2)
    p1 = float(abs(state[1]) ** 2)
    return p0, p1


def _to_snapshots(result: SimulationResult) -> List[dict]:
    snapshots: List[dict] = []
    for idx, coord in enumerate(result.coordinates):
        state = result.states[idx]
        p0, p1 = _state_probabilities(state)
        theta, phi = cartesian_to_spherical(*coord)

        gate_info = None
        if idx > 0 and idx - 1 < len(result.gates):
            gate_info = result.gates[idx - 1]

        snapshots.append(
            {
                "step": idx,
                "label": "initial" if gate_info is None else _format_gate(gate_info),
                "bloch": [coord[0], coord[1], coord[2]],
                "probabilities": {"|0⟩": p0, "|1⟩": p1},
                "theta": theta,
                "phi": phi,
                "statevector": [
                    {"label": "|0⟩", "real": float(state[0].real), "imag": float(state[0].imag)},
                    {"label": "|1⟩", "real": float(state[1].real), "imag": float(state[1].imag)},
                ],
            }
        )
    return snapshots


@app.post("/bloch-path")
async def bloch_path(req: SequenceRequest):
    preset = _normalize_preset(req.preset)
    if req.sequence_text is not None:
        seq_text = req.sequence_text
    else:
        seq_tokens = req.sequence or []
        seq_text = ", ".join(seq_tokens)
    try:
        result = simulate_sequence(preset, seq_text)
    except GateParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    snapshots = _to_snapshots(result)
    gates_payload = [
        {"name": name, "angle": angle, "display": _format_gate((name, angle))}
        for name, angle in result.gates
    ]
    response = {
        "preset": preset,
        "gates": gates_payload,
        "path": [snapshot["bloch"] for snapshot in snapshots[1:]],
        "snapshots": snapshots,
        "final": snapshots[-1] if snapshots else None,
    }
    return response


# Serve static client
app.mount("/", StaticFiles(directory="web_client", html=True), name="static")
