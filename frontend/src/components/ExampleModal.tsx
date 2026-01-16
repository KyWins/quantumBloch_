import { useEffect, useMemo, useState } from "react";

import { useAppDispatch } from "../hooks/useRedux";
import { exampleCircuits } from "../data/examples";
import { replaceCircuit } from "../store/store";
import { runSimulation } from "../store/simulationSlice";

export interface ExampleModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ExampleModal({ isOpen, onClose }: ExampleModalProps) {
  const dispatch = useAppDispatch();
  const [selectedId, setSelectedId] = useState<string>(exampleCircuits[0]?.id ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selected = useMemo(
    () => exampleCircuits.find((item) => item.id === selectedId),
    [selectedId]
  );

  useEffect(() => {
    if (isOpen) {
      setSelectedId(exampleCircuits[0]?.id ?? "");
      setError(null);
      setLoading(false);
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  const handleApply = async () => {
    if (!selected) return;
    try {
      setLoading(true);
      setError(null);
      dispatch(replaceCircuit(selected.circuit));
      await dispatch(runSimulation());
      setLoading(false);
      onClose();
    } catch (err) {
      setLoading(false);
      setError(err instanceof Error ? err.message : "Unable to load example.");
    }
  };

  return (
    <div className="export-backdrop">
      <div className="export-panel">
        <header className="export-header">
          <h3>Example Circuits</h3>
          <button className="text-button" onClick={onClose}>
            Close
          </button>
        </header>
        <div className="export-content">
          <p className="muted">
            Choose a sample circuit to explore common Bloch trajectories. Applying an example will
            replace the current circuit.
          </p>
          <div className="example-list">
            {exampleCircuits.map((item) => (
              <label key={item.id} className={item.id === selectedId ? "example-card active" : "example-card"}>
                <input
                  type="radio"
                  name="example-circuit"
                  value={item.id}
                  checked={item.id === selectedId}
                  onChange={() => setSelectedId(item.id)}
                />
                <div>
                  <h4>{item.name}</h4>
                  <p>{item.description}</p>
                </div>
              </label>
            ))}
          </div>
          {selected && (
            <div className="muted">
              Qubits: {selected.circuit.qubit_count} · Gates: {selected.circuit.gates.length}
            </div>
          )}
          {error && <p className="error">{error}</p>}
          <button onClick={handleApply} disabled={loading}>
            {loading ? "Loading…" : "Use this example"}
          </button>
        </div>
      </div>
    </div>
  );
}
