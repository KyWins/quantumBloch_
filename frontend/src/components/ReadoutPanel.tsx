import { useEffect, useMemo, useState } from "react";

import { useAppDispatch, useAppSelector } from "../hooks/useRedux";
import { setNoiseEnabled, setNoiseValue, setFocusQubit } from "../store/simulationSlice";
import { measureCircuit } from "../services/api";
import type { CircuitDto } from "../types/schemas";
import { BlochPlot } from "./BlochPlot";
import { CircuitLibrary } from "./CircuitLibrary";
import { MetricChart } from "./MetricChart";
import { MeasurementHistogram } from "./MeasurementHistogram";

const BASIS_AXES: Record<string, { x: number; y: number; z: number }> = {
  Z: { x: 0, y: 0, z: 1 },
  X: { x: 1, y: 0, z: 0 },
  Y: { x: 0, y: 1, z: 0 }
};

function projectProbability(bloch: { x: number; y: number; z: number }, basis: keyof typeof BASIS_AXES) {
  const axis = BASIS_AXES[basis];
  const dot = bloch.x * axis.x + bloch.y * axis.y + bloch.z * axis.z;
  const plus = (1 + dot) / 2;
  return {
    plus,
    minus: 1 - plus,
    axis
  };
}

export function ReadoutPanel() {
  const dispatch = useAppDispatch();
  const simulation = useAppSelector((state) => state.simulation);
  const circuit = useAppSelector((state) => state.circuit);
  const noise = simulation.noise;
  const focusQubit = simulation.focusQubit;
  const [basis, setBasis] = useState<keyof typeof BASIS_AXES>("Z");
  const [shots, setShots] = useState(256);
  const [measurementOverlay, setMeasurementOverlay] = useState<{ x: number; y: number; z: number } | null>(
    null
  );
  const [measurementResult, setMeasurementResult] = useState<
    {
      outcome: string;
      counts: Record<string, number>;
      mean: number;
      standardDeviation: number;
      samples: string[];
      longestRun: number;
      longestSymbol: string;
      switches: number;
    } | null
  >(null);
  const [samplingStatus, setSamplingStatus] = useState<"idle" | "loading" | "failed">("idle");
  const [samplingError, setSamplingError] = useState<string | null>(null);

  const latest = useMemo(() => {
    if (!simulation.snapshots.length) return null;
    const selected = simulation.selectedStep ?? simulation.snapshots.length - 1;
    return simulation.snapshots[Math.min(selected, simulation.snapshots.length - 1)];
  }, [simulation.snapshots, simulation.selectedStep]);

  const basisProbabilities = latest?.bloch ? projectProbability(latest.bloch, basis) : null;

  useEffect(() => {
    setMeasurementOverlay(null);
    setMeasurementResult(null);
    setSamplingStatus("idle");
    setSamplingError(null);
  }, [
    basis,
    simulation.selectedStep,
    simulation.snapshots,
    noise.depolarizing,
    noise.amplitudeDamping,
    noise.phaseDamping,
    focusQubit
  ]);

  const handleSample = async () => {
    if (!latest) return;
    try {
      const clampedShots = Number.isFinite(shots) ? Math.max(1, Math.min(4096, shots)) : 1;
      setShots(clampedShots);
      setSamplingStatus("loading");
      setSamplingError(null);

      const circuitDto: CircuitDto = {
        qubit_count: circuit.qubitCount,
        global_phase: null,
        gates: circuit.gates.map((gate) => ({
          name: gate.name,
          targets: gate.targets,
          controls: gate.controls ?? [],
          parameters: gate.parameters,
          metadata: {}
        }))
      };

      const hasNoise =
        noise.depolarizing > 0 || noise.amplitudeDamping > 0 || noise.phaseDamping > 0;

      const response = await measureCircuit({
        circuit: circuitDto,
        basis,
        shots: clampedShots,
        noise: hasNoise
          ? {
              depolarizing: noise.depolarizing || null,
              amplitude_damping: noise.amplitudeDamping || null,
              phase_damping: noise.phaseDamping || null
            }
          : undefined,
        focus_qubit: focusQubit
      });

      const overlay = response.overlay_vector;
      setMeasurementOverlay({ x: overlay[0], y: overlay[1], z: overlay[2] });
      setMeasurementResult({
        outcome: response.counts.plus >= response.counts.minus ? "+" : "-",
        counts: response.counts,
        mean: response.mean,
        standardDeviation: response.standard_deviation,
        samples: response.samples ?? [],
        longestRun: response.longest_run,
        longestSymbol: response.longest_symbol,
        switches: response.switches
      });
      setSamplingStatus("idle");
    } catch (error) {
      setSamplingStatus("failed");
      setSamplingError(error instanceof Error ? error.message : "Measurement failed");
    }
  };

  const steps = useMemo(() => simulation.snapshots.map((snapshot) => snapshot.step), [simulation.snapshots]);

  const blochSeries = useMemo(
    () => [
      { name: "⟨X⟩", values: simulation.snapshots.map((snap) => snap.bloch?.x ?? null), color: "#2563EB" },
      { name: "⟨Y⟩", values: simulation.snapshots.map((snap) => snap.bloch?.y ?? null), color: "#16A34A" },
      { name: "⟨Z⟩", values: simulation.snapshots.map((snap) => snap.bloch?.z ?? null), color: "#F97316" }
    ],
    [simulation.snapshots]
  );

  const probabilitySeries = useMemo(
    () => [
      {
        name: "|0⟩",
        values: simulation.snapshots.map((snap) => snap.probabilities?.[0] ?? null),
        color: "#6366F1"
      },
      {
        name: "|1⟩",
        values: simulation.snapshots.map((snap) => snap.probabilities?.[1] ?? null),
        color: "#F43F5E"
      }
    ],
    [simulation.snapshots]
  );

  const focusOptions = useMemo(
    () => Array.from({ length: circuit.qubitCount }, (_, index) => index),
    [circuit.qubitCount]
  );

  return (
    <div className="readout-panel">
      <h2>Readouts</h2>
      {simulation.status === "loading" && <p className="placeholder">Simulating…</p>}
      {simulation.status === "failed" && (
        <p className="error">{simulation.error ?? "Simulation failed"}</p>
      )}
      {latest ? (
        <>
          <BlochPlot
            snapshots={simulation.snapshots}
            selectedStep={simulation.selectedStep ?? simulation.snapshots.length - 1}
            measurementOverlay={measurementOverlay}
          />
          <div className="metrics-grid">
            <div>
              <h4>Bloch</h4>
              <ul>
                <li>x: {latest.bloch?.x.toFixed(3)}</li>
                <li>y: {latest.bloch?.y.toFixed(3)}</li>
                <li>z: {latest.bloch?.z.toFixed(3)}</li>
              </ul>
            </div>
            <div>
              <h4>Z Probabilities</h4>
              <ul>
                <li>|0⟩: {latest.probabilities?.[0]?.toFixed(3)}</li>
                <li>|1⟩: {latest.probabilities?.[1]?.toFixed(3)}</li>
              </ul>
            </div>
            <div>
              <h4>State Metrics</h4>
              <ul>
                <li>Radius: {latest.radius?.toFixed(3)}</li>
                <li>Purity: {latest.purity?.toFixed(3)}</li>
              </ul>
            </div>
            <div>
              <h4>Measurement</h4>
              <div className="measurement-controls">
                <label>
                  Focus qubit
                  <select
                    value={focusQubit}
                    onChange={(event) =>
                      dispatch(
                        setFocusQubit({
                          focus: Number(event.target.value),
                          qubitCount: circuit.qubitCount
                        })
                      )
                    }
                  >
                    {focusOptions.map((option) => (
                      <option key={option} value={option}>
                        q[{option}]
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Basis
                  <select value={basis} onChange={(event) => setBasis(event.target.value as keyof typeof BASIS_AXES)}>
                    <option value="Z">Z</option>
                    <option value="X">X</option>
                    <option value="Y">Y</option>
                  </select>
                </label>
                <label>
                  Shots
                  <input
                    type="number"
                    min={1}
                    max={4096}
                    value={shots}
                    onChange={(event) => setShots(Number(event.target.value))}
                  />
                </label>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={noise.enabled}
                    onChange={(event) => dispatch(setNoiseEnabled(event.target.checked))}
                  />
                  Apply noise to simulation
                </label>
                <div className="noise-grid">
                  <label>
                    Depolarizing
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={Math.round(noise.depolarizing * 100)}
                      onChange={(event) =>
                        dispatch(
                          setNoiseValue({ key: "depolarizing", value: Number(event.target.value) / 100 })
                        )
                      }
                    />
                  </label>
                  <label>
                    Amplitude
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={Math.round(noise.amplitudeDamping * 100)}
                      onChange={(event) =>
                        dispatch(
                          setNoiseValue({
                            key: "amplitudeDamping",
                            value: Number(event.target.value) / 100
                          })
                        )
                      }
                    />
                  </label>
                  <label>
                    Phase
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={Math.round(noise.phaseDamping * 100)}
                      onChange={(event) =>
                        dispatch(
                          setNoiseValue({
                            key: "phaseDamping",
                            value: Number(event.target.value) / 100
                          })
                        )
                      }
                    />
                  </label>
                </div>
                <button onClick={handleSample}>Sample</button>
                {basisProbabilities && (
                  <ul>
                    <li>P(+): {basisProbabilities.plus.toFixed(3)}</li>
                    <li>P(-): {basisProbabilities.minus.toFixed(3)}</li>
                  </ul>
                )}
                {samplingStatus === "loading" && <p className="muted">Sampling…</p>}
                {samplingStatus === "failed" && samplingError && <p className="error">{samplingError}</p>}
                {measurementResult && (
                  <div className="measurement-result">
                    <p>
                      Outcome: {measurementResult.outcome} (counts +:{" "}
                      {measurementResult.counts.plus} , -:{" "}
                      {measurementResult.counts.minus})
                    </p>
                    <MeasurementHistogram
                      counts={measurementResult.counts}
                      samples={measurementResult.samples}
                      shots={shots}
                    />
                    <p className="muted">
                      ⟨σ⟩ ≈ {measurementResult.mean.toFixed(3)} · σ = {measurementResult.standardDeviation.toFixed(3)}
                    </p>
                    <p className="muted">
                      Longest run: {measurementResult.longestRun} × {measurementResult.longestSymbol === "plus" ? "+" : measurementResult.longestSymbol === "minus" ? "-" : "?"} · switches {measurementResult.switches}
                    </p>
                    <p className="muted">
                      Noise → depol {Math.round(noise.depolarizing * 100)}%, amp {Math.round(noise.amplitudeDamping * 100)}%, phase {Math.round(noise.phaseDamping * 100)}%
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
          {steps.length > 1 && (
            <div className="chart-grid">
              <MetricChart steps={steps} series={blochSeries} title="Bloch expectations" />
              <MetricChart steps={steps} series={probabilitySeries} title="Measurement probabilities" />
            </div>
          )}
          <CircuitLibrary />
        </>
      ) : (
        <p className="placeholder">Add gates to view simulation metrics.</p>
      )}
    </div>
  );
}
