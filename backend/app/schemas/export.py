from __future__ import annotations

from typing import Optional, Dict

from pydantic import BaseModel, Field

from .circuit import CircuitSchema


class ExportRequest(BaseModel):
    circuit: CircuitSchema
    noise: Optional[Dict[str, Optional[float]]] = Field(default=None)
    share: bool = False
    name: Optional[str] = Field(default=None, max_length=120)
    focus_qubit: Optional[int] = Field(default=None, ge=0)


class ExportResponse(BaseModel):
    qasm: str
    snapshot_json: str
    snapshot_count: int
    share_id: Optional[str] = None
