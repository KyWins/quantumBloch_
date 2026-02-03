import { useEffect, useState, useCallback } from "react";

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

  // Keyboard shortcuts handler
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Check for modifier key (Cmd on Mac, Ctrl on Windows/Linux)
      const isMod = event.metaKey || event.ctrlKey;

      if (isMod && event.key === "z" && !event.shiftKey && undoAvailable) {
        event.preventDefault();
        dispatch(undo());
      } else if (isMod && event.key === "z" && event.shiftKey && redoAvailable) {
        event.preventDefault();
        dispatch(redo());
      } else if (isMod && event.key === "y" && redoAvailable) {
        event.preventDefault();
        dispatch(redo());
      } else if (isMod && event.key === "e") {
        event.preventDefault();
        setExportOpen((prev) => !prev);
      }
    },
    [dispatch, undoAvailable, redoAvailable]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

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
    focusQubit,
  ]);

  if (isEmbed) {
    return (
      <div className="embed-shell" role="application" aria-label="Bloch Sphere Embed">
        <main className="embed-main">
          <ReadoutPanel />
          <TimelineScrubber />
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {/* Skip link for keyboard navigation */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <header className="app-header" role="banner">
        <h1>Bloch Sphere Workbench</h1>
        <nav className="header-actions" aria-label="Main actions">
          <button
            disabled={!undoAvailable}
            onClick={() => dispatch(undo())}
            aria-label="Undo last action"
            data-tooltip="Undo (Ctrl+Z)"
          >
            Undo
          </button>
          <button
            disabled={!redoAvailable}
            onClick={() => dispatch(redo())}
            aria-label="Redo last undone action"
            data-tooltip="Redo (Ctrl+Shift+Z)"
          >
            Redo
          </button>
          <button
            onClick={() => setExampleOpen(true)}
            aria-label="View example circuits"
            aria-haspopup="dialog"
          >
            Examples
          </button>
          <button
            onClick={() => setExportOpen(true)}
            aria-label="Export circuit"
            aria-haspopup="dialog"
            data-tooltip="Export (Ctrl+E)"
          >
            Export
          </button>
        </nav>
      </header>

      <div className="app-body" id="main-content">
        <aside className="panel-left" aria-label="Gate palette">
          <CommandPalette />
        </aside>
        <main className="panel-center" role="main" aria-label="Circuit editor">
          <CircuitCanvas />
          <TimelineScrubber />
        </main>
        <aside className="panel-right" aria-label="Readout panel">
          <ReadoutPanel />
        </aside>
      </div>

      <ExportPanel isOpen={isExportOpen} onClose={() => setExportOpen(false)} />
      <ExampleModal isOpen={isExampleOpen} onClose={() => setExampleOpen(false)} />
      {import.meta.env.DEV && <HealthOverlay />}
    </div>
  );
}
