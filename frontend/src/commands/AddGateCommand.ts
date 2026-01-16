import type { CircuitState } from "../store/types";
import { generateId } from "../utils/id";
import type { Command } from "./Command";

export interface AddGatePayload {
  name: string;
  targets: number[];
  controls?: number[];
  parameters?: number[];
  id?: string;
  index?: number;
}

export class AddGateCommand implements Command<CircuitState> {
  static readonly TYPE = "command/addGate";

  readonly type = AddGateCommand.TYPE;

  private gateId: string;
  private insertIndex: number | null;

  constructor(private readonly payload: AddGatePayload) {
    this.gateId = payload.id ?? generateId();
    this.insertIndex = typeof payload.index === "number" ? payload.index : null;
  }

  execute(state: CircuitState): CircuitState {
    const gate = {
      id: this.gateId,
      name: this.payload.name,
      targets: this.payload.targets,
      controls: this.payload.controls ?? [],
      parameters: this.payload.parameters ?? []
    };
    const gates = [...state.gates];
    if (this.insertIndex !== null && this.insertIndex >= 0 && this.insertIndex <= gates.length) {
      gates.splice(this.insertIndex, 0, gate);
    } else {
      gates.push(gate);
      this.insertIndex = gates.length - 1;
    }
    return {
      ...state,
      gates
    };
  }

  undo(state: CircuitState): CircuitState {
    return {
      ...state,
      gates: state.gates.filter((gate) => gate.id !== this.gateId)
    };
  }

  serialize(): Record<string, unknown> {
    return {
      payload: {
        ...this.payload,
        controls: this.payload.controls ?? [],
        id: this.gateId,
        index: this.insertIndex ?? undefined
      }
    };
  }
}
