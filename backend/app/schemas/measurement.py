from __future__ import annotations

from typing import Dict, Optional, Tuple

from pydantic import BaseModel, Field

from .circuit import CircuitSchema


class MeasurementRequest(BaseModel):
  circuit: CircuitSchema
  basis: str = Field(pattern="^[XYZxyz]$")
  shots: int = Field(ge=1, le=4096)
  seed: Optional[int] = None
  noise: Optional[Dict[str, Optional[float]]] = None
  focus_qubit: Optional[int] = None


class MeasurementResponse(BaseModel):
  step: int
  basis: str
  shots: int
  counts: Dict[str, int]
  probabilities: Dict[str, float]
  overlay_vector: Tuple[float, float, float]
  samples: Tuple[str, ...]
  mean: float
  standard_deviation: float
  longest_run: int
  longest_symbol: str
  switches: int
