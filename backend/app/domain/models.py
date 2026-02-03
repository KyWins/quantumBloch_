from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

QubitIndex = int
Radians = float
Probability = float


@dataclass(frozen=True)
class Gate:
    """Pure representation of a gate instruction."""

    name: str
    targets: Tuple[QubitIndex, ...]
    controls: Tuple[QubitIndex, ...] = ()
    parameters: Tuple[float, ...] = ()
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class Circuit:
    """Mutable circuit composed of a list of gates and qubit count."""

    qubit_count: int
    gates: List[Gate] = field(default_factory=list)
    global_phase: Optional[Radians] = None

    def append(self, gate: Gate) -> None:
        self.gates.append(gate)

    def insert(self, index: int, gate: Gate) -> None:
        self.gates.insert(index, gate)

    def remove(self, index: int) -> Gate:
        return self.gates.pop(index)


@dataclass(frozen=True)
class BlochVector:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Snapshot:
    """State of the circuit after a given step."""

    step: int
    statevector: Optional[Tuple[complex, ...]] = None
    density_matrix: Optional[Tuple[complex, ...]] = None
    bloch: Optional[BlochVector] = None
    probabilities: Optional[Tuple[Probability, ...]] = None
    fidelity_to_target: Optional[float] = None
    global_phase: Optional[Radians] = None
    purity: Optional[float] = None
    bloch_radius: Optional[float] = None
    focus_qubit: Optional[int] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MeasurementResult:
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


@dataclass(frozen=True)
class CircuitSummary:
    id: str
    name: Optional[str]
    qubit_count: int
    gate_count: int
    updated_at: str
