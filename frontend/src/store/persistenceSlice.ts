import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import type { CircuitDto, CircuitSummary } from "../types/schemas";
import {
  listCircuits,
  loadCircuit,
  saveCircuitApi
} from "../services/api";

interface PersistenceState {
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
  summaries: CircuitSummary[];
  lastSavedId: string | null;
}

const initialState: PersistenceState = {
  status: "idle",
  error: null,
  summaries: [],
  lastSavedId: null
};

export const fetchCircuitSummaries = createAsyncThunk(
  "persistence/fetchSummaries",
  async () => {
    return await listCircuits();
  }
);

export const saveCircuit = createAsyncThunk(
  "persistence/save",
  async (
    payload: { name?: string | null; circuit: CircuitDto; focus_qubit?: number | null },
    thunkAPI
  ) => {
    const response = await saveCircuitApi(payload);
    await thunkAPI.dispatch(fetchCircuitSummaries());
    return response.id;
  }
);

export const loadCircuitById = createAsyncThunk(
  "persistence/loadById",
  async (circuitId: string) => {
    return await loadCircuit(circuitId);
  }
);

const persistenceSlice = createSlice({
  name: "persistence",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchCircuitSummaries.fulfilled, (state, action) => {
        state.summaries = action.payload;
      })
      .addCase(saveCircuit.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(saveCircuit.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.lastSavedId = action.payload;
      })
      .addCase(saveCircuit.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message ?? "Save failed";
      });
  }
});

export const persistenceReducer = persistenceSlice.reducer;
