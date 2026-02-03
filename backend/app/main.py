from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.api import circuits, snapshots
from app.adapters.api.dependencies import (
    connect_repository,
    disconnect_repository,
    get_snapshot_service,
)
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    await connect_repository()
    yield
    await disconnect_repository()


settings = get_settings()

app = FastAPI(title="Bloch Sphere Simulation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
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
