import type { Command } from "./Command";
import type { CircuitState, GateInstance } from "../store/types";

export interface RemoveGatePayload {
  id: string;
  // Optional data for reconstruction
  gate?: GateInstance;
  index?: number;
}

export class RemoveGateCommand implements Command<CircuitState> {
  static readonly TYPE = "command/removeGate";

  readonly type = RemoveGateCommand.TYPE;

  private removedGate: GateInstance | null;
  private removedIndex: number;

  constructor(private readonly payload: RemoveGatePayload) {
    this.removedGate = payload.gate ?? null;
    this.removedIndex = payload.index ?? -1;
  }

  execute(state: CircuitState): CircuitState {
    const index = state.gates.findIndex((gate) => gate.id === this.payload.id);
    if (index === -1) {
      return state;
    }

    const gate = state.gates[index];
    this.removedGate = {
      ...gate,
      targets: [...gate.targets],
      controls: [...(gate.controls ?? [])],
      parameters: [...gate.parameters]
    };
    this.removedIndex = index;

    return {
      ...state,
      gates: state.gates.filter((g) => g.id !== gate.id)
    };
  }

  undo(state: CircuitState): CircuitState {
    if (!this.removedGate) {
      return state;
    }
    const gates = [...state.gates];
    const insertIndex = this.removedIndex < 0 ? gates.length : this.removedIndex;
    gates.splice(insertIndex, 0, this.removedGate);
    return {
      ...state,
      gates
    };
  }

  serialize(): Record<string, unknown> {
    const gate = this.removedGate ?? this.payload.gate;
    return {
      payload: {
        id: this.payload.id,
        gate: gate
          ? {
              ...gate,
              targets: [...gate.targets],
              controls: [...gate.controls],
              parameters: [...gate.parameters]
            }
          : undefined,
        index: this.removedIndex >= 0 ? this.removedIndex : this.payload.index
      }
    };
  }
}
