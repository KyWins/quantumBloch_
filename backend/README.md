# Backend (Hexagonal Architecture)

This service exposes the simulation domain through adapters (FastAPI, websocket,
batch exporters). The core logic lives in pure Python modules under
`backend/app/domain/` and must be framework-agnostic to stay testable and
swappable.

## Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    Adapters (FastAPI, WS)                     │
├──────────────────────────────────────────────────────────────┤
│ Ports (SimulationPort, CircuitRepositoryPort, ExportPort, …) │
├──────────────────────────────────────────────────────────────┤
│                 Domain (Circuit, Snapshot, Noise)             │
└──────────────────────────────────────────────────────────────┘
```

- **Domain:** gate definitions, circuit mutations, snapshot engine, fidelity
  calculators, noise pipelines. No framework imports. Pure functions/classes
  with dependency injection via ports.
- **Ports:** abstract protocols (Pydantic or `typing.Protocol`) describing the
  services the domain requires (e.g., simulation backends, storage, telemetry).
- **Adapters:** FastAPI controllers, Qiskit simulator adapter, persistence
  adapters, export encoders. They implement the ports and translate IO to/from
  the domain.

## Immediate TODOs

1. Scaffold `app/domain/` with base models (`Circuit`, `Gate`, `Snapshot`,
   `NoiseModel`) and port interfaces.
2. Draft Pydantic schemas mirroring domain models for API responses.
3. Set up FastAPI entry point (`backend/app/main.py`) wiring dependency
   injection (likely via `fastapi.Depends` or a custom container).
4. Configure tooling: `poetry` or `uv`, `ruff`, `mypy`, `pytest`, `pre-commit`.
