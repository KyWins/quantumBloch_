from __future__ import annotations

from typing import Optional, Dict

from pydantic import BaseModel, Field

from .circuit import CircuitSchema


class SimulateRequest(BaseModel):
    circuit: CircuitSchema
    noise: Optional[Dict[str, Optional[float]]] = Field(default=None)
    focus_qubit: Optional[int] = Field(default=None, ge=0)
