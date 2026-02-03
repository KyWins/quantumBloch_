import { useEffect, useMemo, useState, useId, type DragEvent } from "react";

import { AddGateCommand } from "../commands/AddGateCommand";
import { SetQubitCountCommand } from "../commands/SetQubitCountCommand";
import { executeCommand } from "../store/store";
import { useAppDispatch, useAppSelector } from "../hooks/useRedux";

const PALETTE: { category: string; gates: { label: string; name: string; description: string }[] }[] = [
  {
    category: "Basic",
    gates: [
      { label: "I", name: "I", description: "Identity gate - no operation" },
      { label: "X", name: "X", description: "Pauli-X gate - bit flip" },
      { label: "Y", name: "Y", description: "Pauli-Y gate - bit and phase flip" },
      { label: "Z", name: "Z", description: "Pauli-Z gate - phase flip" },
      { label: "H", name: "H", description: "Hadamard gate - superposition" },
    ],
  },
  {
    category: "Rotations",
    gates: [
      { label: "Rx", name: "RX", description: "Rotation around X axis" },
      { label: "Ry", name: "RY", description: "Rotation around Y axis" },
      { label: "Rz", name: "RZ", description: "Rotation around Z axis" },
      { label: "Phase", name: "P", description: "Phase rotation gate" },
    ],
  },
  {
    category: "Controls",
    gates: [
      { label: "CX", name: "CX", description: "Controlled-X (CNOT) gate" },
      { label: "CZ", name: "CZ", description: "Controlled-Z gate" },
    ],
  },
  {
    category: "Noise",
    gates: [
      { label: "Reset", name: "RESET", description: "Reset qubit to |0⟩" },
      { label: "Depol", name: "DEPOLARIZING", description: "Depolarizing noise channel" },
      { label: "AmpDamp", name: "AMP_DAMP", description: "Amplitude damping noise" },
      { label: "PhaseDamp", name: "PHASE_DAMP", description: "Phase damping noise" },
    ],
  },
  {
    category: "Measurement",
    gates: [
      { label: "MZ", name: "MEASURE_Z", description: "Measure in Z basis" },
      { label: "MX", name: "MEASURE_X", description: "Measure in X basis" },
      { label: "MY", name: "MEASURE_Y", description: "Measure in Y basis" },
    ],
  },
];

const ROTATION_DEFAULTS: Record<string, number[]> = {
  RX: [Math.PI / 2],
  RY: [Math.PI / 2],
  RZ: [Math.PI / 2],
  P: [Math.PI / 2],
  DEPOLARIZING: [0.1],
  AMP_DAMP: [0.1],
  PHASE_DAMP: [0.1],
};

const CONTROL_GATES = new Set(["CX", "CZ"]);

export function CommandPalette() {
  const dispatch = useAppDispatch();
  const qubitCount = useAppSelector((state) => state.circuit.qubitCount);
  const [targetQubit, setTargetQubit] = useState(0);
  const [controlQubit, setControlQubit] = useState(0);
  const headingId = useId();

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
      parameters: params,
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
    <div className="command-palette" role="region" aria-labelledby={headingId}>
      <div className="palette-header">
        <h2 id={headingId}>Gate Palette</h2>
        <div className="target-group" role="group" aria-label="Qubit configuration">
          <label className="target-input">
            <span>Qubits</span>
            <input
              type="number"
              min={1}
              max={8}
              value={qubitCount}
              aria-label="Number of qubits"
              onChange={(event) => {
                const next = Number(event.target.value);
                if (Number.isFinite(next)) {
                  dispatch(executeCommand({ command: new SetQubitCountCommand(next) }));
                }
              }}
            />
          </label>
          <label className="target-input">
            <span>Target</span>
            <input
              type="number"
              min={0}
              max={Math.max(0, qubitCount - 1)}
              value={clampedTarget}
              aria-label="Target qubit index"
              onChange={(event) => setTargetQubit(Number(event.target.value))}
            />
          </label>
          <label className="target-input">
            <span>Control</span>
            <input
              type="number"
              min={0}
              max={Math.max(0, qubitCount - 1)}
              value={clampedControl}
              aria-label="Control qubit index"
              onChange={(event) => setControlQubit(Number(event.target.value))}
            />
          </label>
        </div>
      </div>
      {PALETTE.map((section) => (
        <fieldset key={section.category} className="palette-section">
          <legend>
            <h3>{section.category}</h3>
          </legend>
          <div className="palette-grid" role="group" aria-label={`${section.category} gates`}>
            {section.gates.map((gate) => (
              <button
                key={gate.name}
                onClick={() => handleAdd(gate.name)}
                draggable
                onDragStart={(event) => handleDragStart(event, gate.name)}
                aria-label={`Add ${gate.label} gate: ${gate.description}`}
                data-tooltip={gate.description}
              >
                {gate.label}
              </button>
            ))}
          </div>
        </fieldset>
      ))}
    </div>
  );
}
