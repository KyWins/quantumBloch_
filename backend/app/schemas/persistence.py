from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .circuit import CircuitSchema
from .snapshot import SnapshotSchema


class SaveCircuitRequest(BaseModel):
  name: Optional[str] = Field(default=None, max_length=120)
  circuit: CircuitSchema
  focus_qubit: Optional[int] = Field(default=None, ge=0)


class SaveCircuitResponse(BaseModel):
  id: str


class CircuitSummarySchema(BaseModel):
  id: str
  name: Optional[str]
  qubit_count: int
  gate_count: int
  updated_at: str


class SavedCircuitResponse(BaseModel):
  id: str
  name: Optional[str]
  circuit: CircuitSchema
  snapshots: List[SnapshotSchema]
  focus_qubit: Optional[int] = None
