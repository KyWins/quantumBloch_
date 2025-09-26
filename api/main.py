from __future__ import annotations

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils.gate_utils import sequence_to_bloch_path

app = FastAPI(title="Bloch Sphere API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://127.0.0.1:8501", "http://localhost:8000", "http://localhost:8501"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["content-type"],
)


class SequenceRequest(BaseModel):
    sequence: List[str]


@app.post("/bloch-path")
async def bloch_path(req: SequenceRequest):
    path = sequence_to_bloch_path(req.sequence)
    return {"path": path}


# Serve static client
app.mount("/", StaticFiles(directory="web_client", html=True), name="static")
