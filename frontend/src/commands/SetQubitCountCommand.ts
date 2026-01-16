import type { Command } from "./Command";
import type { CircuitState, GateInstance } from "../store/types";

export class SetQubitCountCommand implements Command<CircuitState> {
  static readonly TYPE = "command/setQubitCount";

  readonly type = SetQubitCountCommand.TYPE;

  private previousCount: number | null = null;
  private previousGates: GateInstance[] | null = null;

  constructor(private readonly nextCount: number) {}

  execute(state: CircuitState): CircuitState {
    if (this.nextCount < 1) {
      return state;
    }
    if (this.nextCount === state.qubitCount) {
      return state;
    }
    if (this.previousCount === null) {
      this.previousCount = state.qubitCount;
      this.previousGates = state.gates.map((gate) => ({
        ...gate,
        targets: [...gate.targets],
        controls: [...(gate.controls ?? [])],
        parameters: [...gate.parameters]
      }));
    }
    const filteredGates = state.gates
      .filter((gate) => [...gate.targets, ...(gate.controls ?? [])].every((q) => q < this.nextCount))
      .map((gate) => ({
        ...gate,
        targets: [...gate.targets],
        controls: [...(gate.controls ?? [])],
        parameters: [...gate.parameters]
      }));
    return {
      ...state,
      qubitCount: this.nextCount,
      gates: filteredGates
    };
  }

  undo(state: CircuitState): CircuitState {
    if (this.previousCount === null || this.previousGates === null) {
      return state;
    }
    return {
      ...state,
      qubitCount: this.previousCount,
      gates: this.previousGates.map((gate) => ({
        ...gate,
        targets: [...gate.targets],
        controls: [...(gate.controls ?? [])],
        parameters: [...gate.parameters]
      }))
    };
  }

  serialize(): Record<string, unknown> {
    return {
      payload: {
        nextCount: this.nextCount,
        previousCount: this.previousCount ?? undefined
      }
    };
  }
}
