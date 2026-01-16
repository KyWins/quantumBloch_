import type { Command } from "./Command";
import type { CircuitState, GateInstance } from "../store/types";

export interface MoveGatePayload {
  id: string;
  newTarget: number;
  newIndex: number;
  newControls?: number[];
}

interface PreviousState {
  index: number;
  targets: number[];
  controls: number[];
}

export class MoveGateCommand implements Command<CircuitState> {
  static readonly TYPE = "command/moveGate";

  readonly type = MoveGateCommand.TYPE;

  private previous: PreviousState | null = null;

  constructor(private readonly payload: MoveGatePayload) {}

  execute(state: CircuitState): CircuitState {
    const currentIndex = state.gates.findIndex((gate) => gate.id === this.payload.id);
    if (currentIndex === -1) {
      return state;
    }

    const gate = state.gates[currentIndex];
    const nextControls = (this.payload.newControls ?? gate.controls ?? []).filter(
      (control) => control !== this.payload.newTarget
    );

    if (!this.previous) {
      this.previous = {
        index: currentIndex,
        targets: [...gate.targets],
        controls: [...(gate.controls ?? [])]
      };
    }

    const gates: GateInstance[] = state.gates.map((g) => ({
      ...g,
      targets: [...g.targets],
      controls: [...(g.controls ?? [])]
    }));

    const [removed] = gates.splice(currentIndex, 1);
    let insertIndex = this.payload.newIndex;
    if (currentIndex < insertIndex) {
      insertIndex = Math.max(0, insertIndex - 1);
    }
    insertIndex = Math.min(Math.max(insertIndex, 0), gates.length);

    const updatedGate: GateInstance = {
      ...removed,
      targets: [this.payload.newTarget],
      controls: nextControls,
      parameters: [...removed.parameters]
    };

    gates.splice(insertIndex, 0, updatedGate);

    return {
      ...state,
      gates
    };
  }

  undo(state: CircuitState): CircuitState {
    if (!this.previous) {
      return state;
    }
    const currentIndex = state.gates.findIndex((gate) => gate.id === this.payload.id);
    if (currentIndex === -1) {
      return state;
    }

    const gates: GateInstance[] = state.gates.map((g) => ({
      ...g,
      targets: [...g.targets],
      controls: [...(g.controls ?? [])]
    }));

    const [removed] = gates.splice(currentIndex, 1);
    const restored: GateInstance = {
      ...removed,
      targets: [...this.previous.targets],
      controls: [...this.previous.controls]
    };

    const insertIndex = Math.min(Math.max(this.previous.index, 0), gates.length);
    gates.splice(insertIndex, 0, restored);

    return {
      ...state,
      gates
    };
  }

  serialize(): Record<string, unknown> {
    return {
      payload: {
        id: this.payload.id,
        newTarget: this.payload.newTarget,
        newIndex: this.payload.newIndex,
        newControls: this.payload.newControls ?? undefined
      }
    };
  }
}
