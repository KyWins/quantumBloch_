export interface GateDto {
  name: string;
  targets: number[];
  controls?: number[];
  parameters?: number[];
  metadata?: Record<string, string>;
}

export interface CircuitDto {
  qubit_count: number;
  gates: GateDto[];
  global_phase?: number | null;
}

export interface SnapshotDto {
  step: number;
  bloch?: { x: number; y: number; z: number } | null;
  probabilities?: number[] | null;
  global_phase?: number | null;
  radius?: number | null;
  purity?: number | null;
  focus_qubit?: number | null;
  metadata?: Record<string, string>;
}

export interface SimulateResponse {
  snapshots: SnapshotDto[];
}

export interface NoiseConfigDto {
  depolarizing?: number | null;
  amplitude_damping?: number | null;
  phase_damping?: number | null;
}

export interface SimulateRequestDto {
  circuit: CircuitDto;
  noise?: NoiseConfigDto | null;
  focus_qubit?: number | null;
}

export interface MeasurementResponse {
  step: number;
  basis: string;
  shots: number;
  counts: Record<string, number>;
  probabilities: Record<string, number>;
  overlay_vector: [number, number, number];
  samples: string[];
  mean: number;
  standard_deviation: number;
  longest_run: number;
  longest_symbol: string;
  switches: number;
}

export interface CircuitSummary {
  id: string;
  name: string | null;
  qubit_count: number;
  gate_count: number;
  updated_at: string;
}

export interface SavedCircuitResponse {
  id: string;
  name: string | null;
  circuit: CircuitDto;
  snapshots: SnapshotDto[];
  focus_qubit?: number | null;
}

export interface ExportRequestDto extends SimulateRequestDto {
  share?: boolean;
  name?: string | null;
}

export interface ExportResponseDto {
  qasm: string;
  snapshot_json: string;
  snapshot_count: number;
  share_id: string | null;
}
