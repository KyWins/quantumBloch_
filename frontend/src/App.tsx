import { useEffect, useState } from "react";

import { CommandPalette } from "./components/CommandPalette";
import { CircuitCanvas } from "./components/CircuitCanvas";
import { ExampleModal } from "./components/ExampleModal";
import { ExportPanel } from "./components/ExportPanel";
import { ReadoutPanel } from "./components/ReadoutPanel";
import { TimelineScrubber } from "./components/TimelineScrubber";
import { useAppDispatch, useAppSelector } from "./hooks/useRedux";
import { runSimulation, setFocusQubit } from "./store/simulationSlice";
import { loadCircuitById } from "./store/persistenceSlice";
import { redo, undo } from "./store/store";
import { HealthOverlay } from "./components/HealthOverlay";

export default function App() {
  const dispatch = useAppDispatch();
  const qubitCount = useAppSelector((state) => state.circuit.qubitCount);
  const gates = useAppSelector((state) => state.circuit.gates);
  const history = useAppSelector((state) => state.circuit.history);
  const noise = useAppSelector((state) => state.simulation.noise);
  const focusQubit = useAppSelector((state) => state.simulation.focusQubit);
  const undoAvailable = history.undoStack.length > 0;
  const redoAvailable = history.redoStack.length > 0;
  const [isExportOpen, setExportOpen] = useState(false);
  const [isExampleOpen, setExampleOpen] = useState(false);
  const [isEmbed, setIsEmbed] = useState(false);

  useEffect(() => {
    const maxIndex = Math.max(0, qubitCount - 1);
    if (focusQubit > maxIndex) {
      dispatch(setFocusQubit({ focus: maxIndex, qubitCount }));
    }
  }, [dispatch, qubitCount, focusQubit]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sharedId = params.get("circuit");
    const embedParam = params.get("embed");
    setIsEmbed(embedParam === "1");
    if (sharedId) {
      dispatch(loadCircuitById(sharedId))
        .unwrap()
        .then((response) => {
          const nextFocus = response.focus_qubit ?? 0;
          dispatch(setFocusQubit({ focus: nextFocus, qubitCount: response.circuit.qubit_count }));
          dispatch(runSimulation());
        })
        .catch(() => {
          // swallow errors; invalid share id will leave the current circuit untouched
        });
    }
  }, [dispatch]);

  useEffect(() => {
    dispatch(runSimulation());
  }, [
    dispatch,
    qubitCount,
    gates,
    noise.enabled,
    noise.depolarizing,
    noise.amplitudeDamping,
    noise.phaseDamping,
    focusQubit
  ]);

  if (isEmbed) {
    return (
      <div className="embed-shell">
        <main className="embed-main">
          <ReadoutPanel />
          <TimelineScrubber />
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Bloch Sphere Workbench</h1>
        <div className="header-actions">
          <button disabled={!undoAvailable} onClick={() => dispatch(undo())}>
            Undo
          </button>
          <button disabled={!redoAvailable} onClick={() => dispatch(redo())}>
            Redo
          </button>
          <button onClick={() => setExampleOpen(true)}>Examples</button>
          <button onClick={() => setExportOpen(true)}>Export</button>
        </div>
      </header>

      <div className="app-body">
        <aside className="panel-left">
          <CommandPalette />
        </aside>
        <main className="panel-center">
          <CircuitCanvas />
          <TimelineScrubber />
        </main>
        <aside className="panel-right">
          <ReadoutPanel />
        </aside>
      </div>

      <ExportPanel isOpen={isExportOpen} onClose={() => setExportOpen(false)} />
      <ExampleModal isOpen={isExampleOpen} onClose={() => setExampleOpen(false)} />
      {import.meta.env.DEV && <HealthOverlay />}
    </div>
  );
}
