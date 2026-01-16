import { useEffect, useMemo, useState, type DragEvent } from "react";

import { AddGateCommand } from "../commands/AddGateCommand";
import { SetQubitCountCommand } from "../commands/SetQubitCountCommand";
import { executeCommand } from "../store/store";
import { useAppDispatch, useAppSelector } from "../hooks/useRedux";

const PALETTE: { category: string; gates: { label: string; name: string }[] }[] = [
  {
    category: "Basic",
    gates: [
      { label: "I", name: "I" },
      { label: "X", name: "X" },
      { label: "Y", name: "Y" },
      { label: "Z", name: "Z" },
      { label: "H", name: "H" }
    ]
  },
  {
    category: "Rotations",
    gates: [
      { label: "Rx", name: "RX" },
      { label: "Ry", name: "RY" },
      { label: "Rz", name: "RZ" },
      { label: "Phase", name: "P" }
    ]
  },
  {
    category: "Controls",
    gates: [
      { label: "CX", name: "CX" },
      { label: "CZ", name: "CZ" }
    ]
  },
  {
    category: "Noise",
    gates: [
      { label: "Reset", name: "RESET" },
      { label: "Depol", name: "DEPOLARIZING" },
      { label: "AmpDamp", name: "AMP_DAMP" },
      { label: "PhaseDamp", name: "PHASE_DAMP" }
    ]
  },
  {
    category: "Measurement",
    gates: [
      { label: "MZ", name: "MEASURE_Z" },
      { label: "MX", name: "MEASURE_X" },
      { label: "MY", name: "MEASURE_Y" }
    ]
  }
];

const ROTATION_DEFAULTS: Record<string, number[]> = {
  RX: [Math.PI / 2],
  RY: [Math.PI / 2],
  RZ: [Math.PI / 2],
  P: [Math.PI / 2],
  DEPOLARIZING: [0.1],
  AMP_DAMP: [0.1],
  PHASE_DAMP: [0.1]
};

const CONTROL_GATES = new Set(["CX", "CZ"]);

export function CommandPalette() {
  const dispatch = useAppDispatch();
  const qubitCount = useAppSelector((state) => state.circuit.qubitCount);
  const [targetQubit, setTargetQubit] = useState(0);
  const [controlQubit, setControlQubit] = useState(0);

  const clampedTarget = useMemo(() => {
    if (targetQubit < 0) return 0;
    if (targetQubit >= qubitCount) return Math.max(0, qubitCount - 1);
    return targetQubit;
  }, [targetQubit, qubitCount]);

  const clampedControl = useMemo(() => {
    if (controlQubit < 0) return 0;
    if (controlQubit >= qubitCount) return Math.max(0, qubitCount - 1);
    return controlQubit;
  }, [controlQubit, qubitCount]);

  useEffect(() => {
    setTargetQubit((prev) => Math.min(Math.max(prev, 0), Math.max(0, qubitCount - 1)));
    setControlQubit((prev) => Math.min(Math.max(prev, 0), Math.max(0, qubitCount - 1)));
  }, [qubitCount]);

  const buildPayload = (name: string) => {
    const params = ROTATION_DEFAULTS[name] ?? [];
    let controlIndex = clampedControl;
    if (CONTROL_GATES.has(name) && controlIndex === clampedTarget) {
      controlIndex = (clampedTarget + 1) % Math.max(1, qubitCount);
    }
    const payload = {
      name,
      targets: [clampedTarget],
      controls: CONTROL_GATES.has(name) ? [controlIndex] : [],
      parameters: params
    };
    return payload;
  };

  const handleAdd = (name: string) => {
    const payload = buildPayload(name);
    const command = new AddGateCommand(payload);
    dispatch(executeCommand({ command }));
  };

  const handleDragStart = (event: DragEvent<HTMLButtonElement>, name: string) => {
    const payload = buildPayload(name);
    event.dataTransfer.effectAllowed = "copy";
    event.dataTransfer.setData(
      "application/json",
      JSON.stringify({ kind: "palette", payload })
    );
  };

  return (
    <div className="command-palette">
      <div className="palette-header">
        <h2>Gate Palette</h2>
        <div className="target-group">
          <label className="target-input">
            Qubits
            <input
              type="number"
              min={1}
              max={8}
              value={qubitCount}
              onChange={(event) => {
                const next = Number(event.target.value);
                if (Number.isFinite(next)) {
                  dispatch(executeCommand({ command: new SetQubitCountCommand(next) }));
                }
              }}
            />
          </label>
          <label className="target-input">
            Target q
            <input
              type="number"
              min={0}
              max={Math.max(0, qubitCount - 1)}
              value={clampedTarget}
              onChange={(event) => setTargetQubit(Number(event.target.value))}
            />
          </label>
          <label className="target-input">
            Control q
            <input
              type="number"
              min={0}
              max={Math.max(0, qubitCount - 1)}
              value={clampedControl}
              onChange={(event) => setControlQubit(Number(event.target.value))}
            />
          </label>
        </div>
      </div>
      {PALETTE.map((section) => (
        <div key={section.category} className="palette-section">
          <h3>{section.category}</h3>
          <div className="palette-grid">
            {section.gates.map((gate) => (
              <button
                key={gate.name}
                onClick={() => handleAdd(gate.name)}
                draggable
                onDragStart={(event) => handleDragStart(event, gate.name)}
              >
                {gate.label}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
