from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.api import circuits, snapshots
from app.adapters.api.dependencies import connect_repository, disconnect_repository, get_snapshot_service

app = FastAPI(title="Bloch Sphere Simulation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(snapshots.router)
app.include_router(circuits.router)


@app.get("/health")
async def health() -> dict[str, object]:
    service = await get_snapshot_service()
    return {
        "status": "ok",
        "cache": service.cache_stats(),
    }


@app.on_event("startup")
async def on_startup() -> None:
    await connect_repository()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await disconnect_repository()
