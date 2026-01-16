import type { CircuitDto } from "../types/schemas";

export interface ExampleCircuit {
  id: string;
  name: string;
  description: string;
  circuit: CircuitDto;
}

export const exampleCircuits: ExampleCircuit[] = [
  {
    id: "bloch-equator",
    name: "Equator Superposition",
    description: "Hadamard followed by a Z phase push to land on the equator with a +X bias.",
    circuit: {
      qubit_count: 1,
      global_phase: null,
      gates: [
        { name: "H", targets: [0], controls: [], parameters: [], metadata: {} },
        { name: "RZ", targets: [0], controls: [], parameters: [Math.PI / 2], metadata: {} }
      ]
    }
  },
  {
    id: "bloch-spiral",
    name: "Bloch Spiral",
    description: "RX, RY, and RZ sequence that walks the Bloch vector toward the equator with azimuthal drift.",
    circuit: {
      qubit_count: 1,
      global_phase: null,
      gates: [
        { name: "RX", targets: [0], controls: [], parameters: [Math.PI / 4], metadata: {} },
        { name: "RY", targets: [0], controls: [], parameters: [Math.PI / 3], metadata: {} },
        { name: "RZ", targets: [0], controls: [], parameters: [Math.PI / 2], metadata: {} }
      ]
    }
  },
  {
    id: "bloch-reset",
    name: "Reset & Rotate",
    description: "Reset ensures a clean |0⟩ followed by a Y rotation to tilt toward +Y.",
    circuit: {
      qubit_count: 1,
      global_phase: null,
      gates: [
        { name: "RESET", targets: [0], controls: [], parameters: [], metadata: {} },
        { name: "RY", targets: [0], controls: [], parameters: [Math.PI / 2], metadata: {} }
      ]
    }
  }
];
