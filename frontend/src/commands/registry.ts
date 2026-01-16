import type { CircuitState } from "../store/types";
import type { Command } from "./Command";

export type CommandMetadata = Record<string, unknown>;

export type CommandFactory<TMeta extends CommandMetadata = CommandMetadata> = (
  metadata: TMeta
) => Command<CircuitState>;

class CommandRegistry {
  private registry = new Map<string, CommandFactory>();

  register<TMeta extends CommandMetadata>(type: string, factory: CommandFactory<TMeta>) {
    this.registry.set(type, factory as CommandFactory);
  }

  create(type: string, metadata: CommandMetadata): Command<CircuitState> | undefined {
    const factory = this.registry.get(type);
    return factory ? factory(metadata) : undefined;
  }
}

export const commandRegistry = new CommandRegistry();
