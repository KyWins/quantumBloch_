export interface Command<TState> {
  readonly type: string;
  execute(state: TState): TState;
  undo(state: TState): TState;
  serialize(): Record<string, unknown>;
}
