import { AddGateCommand } from "./AddGateCommand";
import type { AddGatePayload } from "./AddGateCommand";
import { RemoveGateCommand } from "./RemoveGateCommand";
import type { RemoveGatePayload } from "./RemoveGateCommand";
import { UpdateGateParametersCommand } from "./UpdateGateParametersCommand";
import type { UpdateGateParametersPayload } from "./UpdateGateParametersCommand";
import { SetQubitCountCommand } from "./SetQubitCountCommand";
import { MoveGateCommand } from "./MoveGateCommand";
import type { MoveGatePayload } from "./MoveGateCommand";
import { commandRegistry } from "./registry";

commandRegistry.register(AddGateCommand.TYPE, (metadata) => {
  const payload = metadata.payload as AddGatePayload;
  return new AddGateCommand(payload);
});

commandRegistry.register(RemoveGateCommand.TYPE, (metadata) => {
  const payload = metadata.payload as RemoveGatePayload;
  return new RemoveGateCommand(payload);
});

commandRegistry.register(UpdateGateParametersCommand.TYPE, (metadata) => {
  const payload = metadata.payload as UpdateGateParametersPayload;
  return new UpdateGateParametersCommand(payload);
});

commandRegistry.register(SetQubitCountCommand.TYPE, (metadata) => {
  const payload = metadata.payload as { nextCount: number };
  return new SetQubitCountCommand(payload.nextCount);
});

commandRegistry.register(MoveGateCommand.TYPE, (metadata) => {
  const payload = metadata.payload as MoveGatePayload;
  return new MoveGateCommand(payload);
});

export { AddGateCommand } from "./AddGateCommand";
export { RemoveGateCommand } from "./RemoveGateCommand";
export { UpdateGateParametersCommand } from "./UpdateGateParametersCommand";
export { SetQubitCountCommand } from "./SetQubitCountCommand";
export { MoveGateCommand } from "./MoveGateCommand";
