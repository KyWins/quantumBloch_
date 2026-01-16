from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, model_validator


class GateSchema(BaseModel):
  name: str
  targets: Tuple[int, ...] = Field(min_length=1)
  controls: Tuple[int, ...] = ()
  parameters: Tuple[float, ...] = ()
  metadata: Dict[str, str] = Field(default_factory=dict)


class CircuitSchema(BaseModel):
  qubit_count: int = Field(ge=1)
  gates: List[GateSchema] = Field(default_factory=list)
  global_phase: Optional[float] = None

  @model_validator(mode="after")
  def validate_targets(self) -> "CircuitSchema":
    for gate in self.gates:
      for qubit in (*gate.targets, *gate.controls):
        if qubit < 0 or qubit >= self.qubit_count:
          raise ValueError(f"Gate {gate.name} references invalid qubit {qubit}")
    return self
