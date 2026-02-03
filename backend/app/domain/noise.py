from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class NoiseConfig:
    amplitude_damping: Optional[float] = None
    phase_damping: Optional[float] = None
    depolarizing: Optional[float] = None

    @property
    def enabled(self) -> bool:
        return any(
            value is not None and value > 0.0
            for value in (self.amplitude_damping, self.phase_damping, self.depolarizing)
        )

    @classmethod
    def from_dict(cls, payload: dict[str, float | None] | None) -> "NoiseConfig | None":
        if not payload:
            return None
        return cls(
            amplitude_damping=payload.get("amplitude_damping"),
            phase_damping=payload.get("phase_damping"),
            depolarizing=payload.get("depolarizing"),
        )
