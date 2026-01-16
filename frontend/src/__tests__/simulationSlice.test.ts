import { describe, expect, it } from "vitest";

import {
  runSimulation,
  setNoiseEnabled,
  setNoiseValue,
  setFocusQubit,
  simulationReducer
} from "../store/simulationSlice";

describe("simulation reducer", () => {
  it("enables and updates noise parameters", () => {
    let state = simulationReducer(undefined, { type: "init" });
    expect(state.noise.enabled).toBe(false);
    state = simulationReducer(state, setNoiseEnabled(true));
    expect(state.noise.enabled).toBe(true);
    state = simulationReducer(
      state,
      setNoiseValue({ key: "depolarizing", value: 0.5 })
    );
    expect(state.noise.depolarizing).toBeCloseTo(0.5);
  });

  it("resets status on runSimulation pending", () => {
    let state = simulationReducer(undefined, { type: "init" });
    state = {
      ...state,
      status: "failed",
      error: "err"
    };
    state = simulationReducer(state, runSimulation.pending("", undefined));
    expect(state.status).toBe("loading");
    expect(state.error).toBeNull();
  });

  it("clamps focus qubit within available range", () => {
    let state = simulationReducer(undefined, { type: "init" });
    state = simulationReducer(state, setFocusQubit({ focus: 3, qubitCount: 2 }));
    expect(state.focusQubit).toBe(1);
    state = simulationReducer(state, setFocusQubit({ focus: -1, qubitCount: 4 }));
    expect(state.focusQubit).toBe(0);
  });
});
