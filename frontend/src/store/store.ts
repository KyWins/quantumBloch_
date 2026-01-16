import { configureStore, createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

import type { Command } from "../commands/Command";
import { commandRegistry } from "../commands/registry";
import "../commands";
import { generateId } from "../utils/id";
import type { CircuitState, CommandHistoryEntry } from "./types";
import { simulationReducer } from "./simulationSlice";
import { persistenceReducer } from "./persistenceSlice";

const initialCircuitState: CircuitState = {
  qubitCount: 1,
  gates: [],
  history: { undoStack: [], redoStack: [] }
};

interface ExecuteCommandPayload {
  command: Command<CircuitState>;
  metadata?: Record<string, unknown>;
}

const circuitSlice = createSlice({
  name: "circuit",
  initialState: initialCircuitState,
  reducers: {
    executeCommand(state, action: PayloadAction<ExecuteCommandPayload>) {
      const { command } = action.payload;
      const userMetadata = action.payload.metadata ?? {};
      const nextState = command.execute(state);
      if (nextState === state) {
        return state;
      }
      const serialized = command.serialize();
      const entry: CommandHistoryEntry = {
        type: command.type,
        metadata: { ...serialized, userMetadata }
      };
      return {
        ...nextState,
        history: {
          undoStack: [...nextState.history.undoStack, entry],
          redoStack: []
        }
      };
    },
    replaceCircuit(state, action: PayloadAction<{ qubit_count: number; gates: { name: string; targets: number[]; controls?: number[]; parameters?: number[] }[] }>) {
      const dto = action.payload;
      return {
        qubitCount: dto.qubit_count,
        gates: dto.gates.map((gate) => ({
          id: generateId(),
          name: gate.name,
          targets: [...gate.targets],
          controls: [...(gate.controls ?? [])],
          parameters: [...(gate.parameters ?? [])]
        })),
        history: { undoStack: [], redoStack: [] }
      };
    },
    // Placeholder undo/redo hooks; actual implementation will require
    // a command registry to reconstruct command instances.
    undo(state) {
      if (!state.history.undoStack.length) return state;
      const undoStack = [...state.history.undoStack];
      const last = undoStack.pop()!;
      const command = commandRegistry.create(
        last.type,
        ((last.metadata ?? {}) as Record<string, unknown>)
      );
      if (!command) return state;
      const updated = command.undo(state);
      return {
        ...updated,
        history: {
          undoStack,
          redoStack: [...state.history.redoStack, last]
        }
      };
    },
    redo(state) {
      if (!state.history.redoStack.length) return state;
      const redoStack = [...state.history.redoStack];
      const nextEntry = redoStack.pop()!;
      const command = commandRegistry.create(
        nextEntry.type,
        ((nextEntry.metadata ?? {}) as Record<string, unknown>)
      );
      if (!command) return state;
      const updated = command.execute(state);
      return {
        ...updated,
        history: {
          undoStack: [...state.history.undoStack, nextEntry],
          redoStack
        }
      };
    }
  }
});

export const { executeCommand, undo, redo, replaceCircuit } = circuitSlice.actions;

export const store = configureStore({
  reducer: {
    circuit: circuitSlice.reducer,
    simulation: simulationReducer,
    persistence: persistenceReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
