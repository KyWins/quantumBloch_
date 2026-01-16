import type { Command } from "./Command";
import type { CircuitState } from "../store/types";

export interface UpdateGateParametersPayload {
  id: string;
  parameters: number[];
  previousParameters?: number[];
}

export class UpdateGateParametersCommand implements Command<CircuitState> {
  static readonly TYPE = "command/updateGateParameters";

  readonly type = UpdateGateParametersCommand.TYPE;

  private previousParameters: number[] | null;

  constructor(private readonly payload: UpdateGateParametersPayload) {
    this.previousParameters = payload.previousParameters ?? null;
  }

  execute(state: CircuitState): CircuitState {
    const gates = state.gates.map((gate) => {
      if (gate.id !== this.payload.id) {
        return gate;
      }
      if (!this.previousParameters) {
        this.previousParameters = gate.parameters;
      }
      return {
        ...gate,
        controls: gate.controls ?? [],
        parameters: [...this.payload.parameters]
      };
    });
    return {
      ...state,
      gates
    };
  }

  undo(state: CircuitState): CircuitState {
    if (!this.previousParameters) {
      return state;
    }
    const gates = state.gates.map((gate) =>
      gate.id === this.payload.id
        ? { ...gate, parameters: [...this.previousParameters!] }
        : gate
    );
    return {
      ...state,
      gates
    };
  }

  serialize(): Record<string, unknown> {
    return {
      payload: {
        id: this.payload.id,
        parameters: [...this.payload.parameters],
        previousParameters: this.previousParameters ? [...this.previousParameters] : undefined
      }
    };
  }
}
