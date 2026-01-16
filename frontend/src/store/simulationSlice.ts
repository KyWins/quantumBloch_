import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

import { simulateCircuit } from "../services/api";
import type { SimulateResponse } from "../types/schemas";
import type { RootState } from "./store";
import type { NoiseState, SimulationState } from "./types";

const initialState: SimulationState = {
  status: "idle",
  snapshots: [],
  error: null,
  selectedStep: null,
  noise: {
    enabled: false,
    depolarizing: 0,
    amplitudeDamping: 0,
    phaseDamping: 0
  },
  focusQubit: 0
};

export const runSimulation = createAsyncThunk<
  SimulateResponse,
  void,
  { state: RootState }
>("simulation/run", async (_, { getState }) => {
  const { circuit, simulation } = getState();
  const circuitPayload = {
    qubit_count: circuit.qubitCount,
    global_phase: null,
    gates: circuit.gates.map((gate) => ({
      name: gate.name,
      targets: gate.targets,
      controls: gate.controls ?? [],
      parameters: gate.parameters,
      metadata: {}
    }))
  };
  const noise = simulation.noise;
  const hasNoise =
    noise.enabled &&
    (noise.depolarizing > 0 || noise.amplitudeDamping > 0 || noise.phaseDamping > 0);

  const requestPayload = {
    circuit: circuitPayload,
    noise: hasNoise
      ? {
          depolarizing: noise.depolarizing || null,
          amplitude_damping: noise.amplitudeDamping || null,
          phase_damping: noise.phaseDamping || null
        }
      : null,
    focus_qubit: simulation.focusQubit,
  };
  return await simulateCircuit(requestPayload);
});

const simulationSlice = createSlice({
  name: "simulation",
  initialState,
  reducers: {
    setSelectedStep(state, action: PayloadAction<number | null>) {
      if (action.payload === null) {
        state.selectedStep = null;
        return;
      }
      const maxIndex = Math.max(0, state.snapshots.length - 1);
      state.selectedStep = Math.min(Math.max(action.payload, 0), maxIndex);
    },
    setNoiseEnabled(state, action: PayloadAction<boolean>) {
      state.noise.enabled = action.payload;
    },
    setNoiseValue(
      state,
      action: PayloadAction<{ key: keyof NoiseState; value: number }>
    ) {
      const { key, value } = action.payload;
      if (key === "enabled") {
        state.noise.enabled = Boolean(value);
        return;
      }
      const clamped = Math.min(Math.max(value, 0), 1);
      if (key === "depolarizing") state.noise.depolarizing = clamped;
      if (key === "amplitudeDamping") state.noise.amplitudeDamping = clamped;
      if (key === "phaseDamping") state.noise.phaseDamping = clamped;
    },
    setFocusQubit(state, action: PayloadAction<{ focus: number; qubitCount: number }>) {
      const { focus, qubitCount } = action.payload;
      const maxIndex = Math.max(0, qubitCount - 1);
      const desired = Math.max(0, Math.min(Math.floor(focus), maxIndex));
      state.focusQubit = desired;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(runSimulation.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(runSimulation.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.snapshots = action.payload.snapshots ?? [];
        state.selectedStep = state.snapshots.length ? state.snapshots.length - 1 : null;
      })
      .addCase(runSimulation.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message ?? "Simulation failed";
      });
  }
});

export const { setSelectedStep, setNoiseEnabled, setNoiseValue, setFocusQubit } = simulationSlice.actions;
export const simulationReducer = simulationSlice.reducer;
