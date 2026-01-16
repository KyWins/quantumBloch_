import { useEffect, useMemo, useState } from "react";

import { saveCircuit, fetchCircuitSummaries, loadCircuitById } from "../store/persistenceSlice";
import { replaceCircuit } from "../store/store";
import { useAppDispatch, useAppSelector } from "../hooks/useRedux";
import type { CircuitDto } from "../types/schemas";
import { runSimulation, setFocusQubit } from "../store/simulationSlice";

export function CircuitLibrary() {
  const dispatch = useAppDispatch();
  const summaries = useAppSelector((state) => state.persistence.summaries);
  const status = useAppSelector((state) => state.persistence.status);
  const circuit = useAppSelector((state) => state.circuit);
  const focusQubit = useAppSelector((state) => state.simulation.focusQubit);
  const [name, setName] = useState("");
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchCircuitSummaries());
  }, [dispatch]);

  const circuitDto: CircuitDto = useMemo(
    () => ({
      qubit_count: circuit.qubitCount,
      global_phase: null,
      gates: circuit.gates.map((gate) => ({
        name: gate.name,
        targets: gate.targets,
        controls: gate.controls ?? [],
        parameters: gate.parameters,
        metadata: {}
      }))
    }),
    [circuit]
  );

  const handleSave = async () => {
    try {
      setError(null);
      const circuitName = name.trim() || `Circuit ${summaries.length + 1}`;
      await dispatch(
        saveCircuit({ name: circuitName, circuit: circuitDto, focus_qubit: focusQubit })
      ).unwrap();
      setName("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  const handleLoad = async (id: string) => {
    try {
      setLoadingId(id);
      setError(null);
      const response = await dispatch(loadCircuitById(id)).unwrap();
      dispatch(replaceCircuit(response.circuit));
      const nextFocus = response.focus_qubit ?? 0;
      dispatch(
        setFocusQubit({ focus: nextFocus, qubitCount: response.circuit.qubit_count })
      );
      await dispatch(runSimulation());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Load failed");
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="library">
      <h3>Library</h3>
      <div className="library-save">
        <input
          type="text"
          placeholder="Circuit name"
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
        <button onClick={handleSave} disabled={status === "loading"}>
          Save
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      <ul className="library-list">
        {summaries.map((item) => (
          <li key={item.id}>
            <button onClick={() => handleLoad(item.id)} disabled={loadingId === item.id}>
              {item.name ?? item.id.slice(0, 6)}
            </button>
            <span className="library-meta">q={item.qubit_count} · gates={item.gate_count}</span>
          </li>
        ))}
        {summaries.length === 0 && <li className="muted">No saved circuits yet.</li>}
      </ul>
    </div>
  );
}
