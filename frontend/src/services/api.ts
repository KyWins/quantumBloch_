import type {
  CircuitDto,
  CircuitSummary,
  ExportRequestDto,
  ExportResponseDto,
  MeasurementResponse,
  SavedCircuitResponse,
  SimulateRequestDto,
  SimulateResponse
} from "../types/schemas";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function simulateCircuit(payload: SimulateRequestDto): Promise<SimulateResponse> {
  const response = await fetch(`${BASE_URL}/circuits/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Simulation failed (${response.status})`);
  }

  return (await response.json()) as SimulateResponse;
}

export async function measureCircuit(
  payload: {
    circuit: CircuitDto;
    basis: string;
    shots: number;
    seed?: number;
    noise?: Record<string, number | null>;
    focus_qubit?: number | null;
  }
): Promise<MeasurementResponse> {
  const response = await fetch(`${BASE_URL}/circuits/measure`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Measurement failed (${response.status})`);
  }

  return (await response.json()) as MeasurementResponse;
}

export async function saveCircuitApi(payload: {
  name?: string | null;
  circuit: CircuitDto;
  focus_qubit?: number | null;
}): Promise<{ id: string }> {
  const response = await fetch(`${BASE_URL}/circuits/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error(`Save failed (${response.status})`);
  }
  return (await response.json()) as { id: string };
}

export async function listCircuits(): Promise<CircuitSummary[]> {
  const response = await fetch(`${BASE_URL}/circuits`);
  if (!response.ok) {
    throw new Error(`Failed to load circuits (${response.status})`);
  }
  return (await response.json()) as CircuitSummary[];
}

export async function loadCircuit(id: string): Promise<SavedCircuitResponse> {
  const response = await fetch(`${BASE_URL}/circuits/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to load circuit (${response.status})`);
  }
  return (await response.json()) as SavedCircuitResponse;
}

export async function exportCircuitApi(payload: ExportRequestDto): Promise<ExportResponseDto> {
  const response = await fetch(`${BASE_URL}/circuits/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Export failed (${response.status})`);
  }

  return (await response.json()) as ExportResponseDto;
}
