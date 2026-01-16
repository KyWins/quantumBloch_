from __future__ import annotations

from typing import Dict, Optional, Tuple

from pydantic import BaseModel, Field


class BlochSchema(BaseModel):
  x: float
  y: float
  z: float


class SnapshotSchema(BaseModel):
  step: int
  bloch: Optional[BlochSchema] = None
  probabilities: Optional[Tuple[float, ...]] = None
  global_phase: Optional[float] = None
  purity: Optional[float] = None
  radius: Optional[float] = None
  focus_qubit: Optional[int] = None
  metadata: Dict[str, str] = Field(default_factory=dict)
