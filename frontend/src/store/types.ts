import type { CircuitSummary } from "../types/schemas";

export interface GateInstance {
  id: string;
  name: string;
  targets: number[];
  controls: number[];
  parameters: number[];
}

export interface CommandHistoryEntry {
  type: string;
  metadata?: Record<string, unknown>;
}

export interface CommandHistory {
  undoStack: CommandHistoryEntry[];
  redoStack: CommandHistoryEntry[];
}

export interface CircuitState {
  qubitCount: number;
  gates: GateInstance[];
  history: CommandHistory;
}

export interface SimulationSnapshot {
  step: number;
  bloch?: { x: number; y: number; z: number } | null;
  probabilities?: number[] | null;
  global_phase?: number | null;
  radius?: number | null;
  purity?: number | null;
  focus_qubit?: number | null;
  metadata?: Record<string, string>;
}

export interface NoiseState {
  enabled: boolean;
  depolarizing: number;
  amplitudeDamping: number;
  phaseDamping: number;
}

export interface SimulationState {
  status: "idle" | "loading" | "succeeded" | "failed";
  snapshots: SimulationSnapshot[];
  error: string | null;
  selectedStep: number | null;
  noise: NoiseState;
  focusQubit: number;
}

export interface AppState {
  circuit: CircuitState;
  simulation: SimulationState;
  persistence: {
    status: "idle" | "loading" | "succeeded" | "failed";
    error: string | null;
    summaries: CircuitSummary[];
    lastSavedId: string | null;
  };
}
