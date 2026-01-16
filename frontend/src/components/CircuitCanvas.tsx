import { Fragment, useCallback, useMemo, useState, type DragEvent } from "react";

import { AddGateCommand } from "../commands/AddGateCommand";
import { MoveGateCommand } from "../commands/MoveGateCommand";
import { RemoveGateCommand } from "../commands/RemoveGateCommand";
import { UpdateGateParametersCommand } from "../commands/UpdateGateParametersCommand";
import { useAppDispatch, useAppSelector } from "../hooks/useRedux";
import { executeCommand } from "../store/store";

const PARAMETRIC_GATES = new Set(["RX", "RY", "RZ", "P", "DEPOLARIZING", "AMP_DAMP", "PHASE_DAMP"]);

const PARAMETER_LABELS: Record<string, string[]> = {
  RX: ["θ"],
  RY: ["θ"],
  RZ: ["θ"],
  P: ["φ"],
  DEPOLARIZING: ["p"],
  AMP_DAMP: ["γ"],
  PHASE_DAMP: ["λ"],
};

export function CircuitCanvas() {
  const dispatch = useAppDispatch();
  const gates = useAppSelector((state) => state.circuit.gates);
  const qubitCount = useAppSelector((state) => state.circuit.qubitCount);
  const [drafts, setDrafts] = useState<Record<string, Record<number, string>>>({});

  const handleRemove = (id: string) => {
    dispatch(executeCommand({ command: new RemoveGateCommand({ id }) }));
  };

  const handleDraftChange = (id: string, index: number, value: string) => {
    setDrafts((prev) => {
      const gateDraft = { ...(prev[id] ?? {}) };
      gateDraft[index] = value;
      return { ...prev, [id]: gateDraft };
    });
  };

  const handleParameterCommit = (id: string, paramIndex: number) => {
    const gate = gates.find((g) => g.id === id);
    if (!gate) return;
    const draftValue = drafts[id]?.[paramIndex];
    const parsed = parseFloat(draftValue ?? "");
    if (!Number.isFinite(parsed)) {
      return;
    }
    const updated = [...gate.parameters];
    while (updated.length <= paramIndex) {
      updated.push(0);
    }
    updated[paramIndex] = parsed;
    const command = new UpdateGateParametersCommand({ id, parameters: updated });
    dispatch(executeCommand({ command }));
    setDrafts((prev) => {
      const next = { ...prev };
      const entry = { ...(next[id] ?? {}) };
      delete entry[paramIndex];
      if (Object.keys(entry).length) {
        next[id] = entry;
      } else {
        delete next[id];
      }
      return next;
    });
  };

  const handleGateDragStart = useCallback((gateId: string, event: DragEvent<HTMLDivElement>) => {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ kind: "existing", gateId })
    );
  }, []);

  const handleDrop = useCallback(
    (lane: number, index: number, event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      event.stopPropagation();
      try {
        const data = event.dataTransfer.getData("application/json");
        if (!data) return;
        const parsed = JSON.parse(data) as
          | { kind: "palette"; payload: { name: string; targets: number[]; controls?: number[]; parameters?: number[] } }
          | { kind: "existing"; gateId: string };

        if (parsed.kind === "palette") {
          const payload = parsed.payload;
          const controls = (payload.controls ?? []).filter((q) => q !== lane);
          const command = new AddGateCommand({
            name: payload.name,
            targets: [lane],
            controls,
            parameters: payload.parameters ?? [],
            index
          });
          dispatch(executeCommand({ command }));
        } else if (parsed.kind === "existing") {
          const command = new MoveGateCommand({
            id: parsed.gateId,
            newTarget: lane,
            newIndex: index
          });
          dispatch(executeCommand({ command }));
        }
      } catch (err) {
        console.error("Drop failed", err);
      }
    },
    [dispatch]
  );

  const handleDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  }, []);

  const lanes = useMemo(() => Array.from({ length: qubitCount }, (_, lane) => lane), [qubitCount]);

  return (
    <section className="circuit-canvas">
      <h2>Circuit Canvas</h2>
      {gates.length === 0 ? <p className="placeholder">Drag gates into the lanes to begin.</p> : null}
      <div className="lane-container">
        {lanes.map((lane) => (
          <div key={lane} className="lane">
            <div className="lane-label">q[{lane}]</div>
            <div
              className="lane-content"
              onDragOver={handleDragOver}
              onDrop={(event) => handleDrop(lane, gates.length, event)}
            >
              {Array.from({ length: gates.length + 1 }, (_, index) => {
                const gate = index < gates.length ? gates[index] : null;
                return (
                  <Fragment key={`entry-${lane}-${index}-${gate?.id ?? "empty"}`}>
                    <DropZone
                      onDragOver={handleDragOver}
                      onDrop={(event) => handleDrop(lane, index, event)}
                    />
                    {gate && gate.targets.includes(lane) && (
                      <GateCard
                        index={index}
                        name={gate.name}
                        targets={gate.targets}
                        controls={gate.controls ?? []}
                        isParametric={PARAMETRIC_GATES.has(gate.name.toUpperCase())}
                        parameters={gate.parameters}
                        drafts={drafts[gate.id] ?? {}}
                        onChange={(paramIndex, value) => handleDraftChange(gate.id, paramIndex, value)}
                        onCommit={(paramIndex) => handleParameterCommit(gate.id, paramIndex)}
                        onRemove={() => handleRemove(gate.id)}
                        onDragStart={(event) => handleGateDragStart(gate.id, event)}
                      />
                    )}
                  </Fragment>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

interface GateCardProps {
  index: number;
  name: string;
  targets: number[];
  controls: number[];
  isParametric: boolean;
  parameters: number[];
  drafts: Record<number, string>;
  onChange(paramIndex: number, value: string): void;
  onCommit(paramIndex: number): void;
  onRemove(): void;
}

function GateCard({
  index,
  name,
  targets,
  controls,
  isParametric,
  parameters,
  drafts,
  onChange,
  onCommit,
  onRemove,
  onDragStart
}: GateCardProps & { onDragStart: (event: DragEvent<HTMLDivElement>) => void }) {
  const baseLabels = PARAMETER_LABELS[name.toUpperCase()] ?? [];
  const paramInputs = isParametric ? Math.max(parameters.length, baseLabels.length, 1) : 0;
  return (
    <div className="gate-card" draggable onDragStart={onDragStart}>
      <span className="gate-index">{index + 1}</span>
      <span className="gate-name">{name}</span>
      <span className="gate-targets">q[{targets.join(", ")}]{controls.length > 0 && <span className="gate-controls"> • ctrl q[{controls.join(", ")}]</span>}</span>
      {isParametric && (
        <div className="gate-parameter">
          {Array.from({ length: paramInputs }).map((_, paramIndex) => {
            const label = baseLabels[paramIndex] ?? `θ${paramIndex}`;
            const currentValue = drafts[paramIndex] ?? (parameters[paramIndex] !== undefined ? parameters[paramIndex].toFixed(3) : "");
            return (
              <label key={`${name}-param-${paramIndex}`}>
                {label}:
                <input
                  value={currentValue}
                  onChange={(event) => onChange(paramIndex, event.target.value)}
                  onBlur={() => onCommit(paramIndex)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      onCommit(paramIndex);
                    }
                  }}
                />
              </label>
            );
          })}
        </div>
      )}
      <button className="gate-remove" onClick={onRemove}>
        Remove
      </button>
    </div>
  );
}

interface DropZoneProps {
  onDragOver: (event: DragEvent<HTMLDivElement>) => void;
  onDrop: (event: DragEvent<HTMLDivElement>) => void;
}

function DropZone({ onDragOver, onDrop }: DropZoneProps) {
  return <div className="drop-zone" onDragOver={onDragOver} onDrop={onDrop} />;
}
