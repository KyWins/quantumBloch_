# Development Log

## 2025-10-10 – Assistant

- Established rebuild direction: React + TypeScript frontend plus FastAPI + Qiskit backend; hexagonal architecture defined (domain models/ports vs adapters) and command-driven React store.
- Bootstrapped backend domain (`app/domain/models.py`, ports, services) with in-memory persistence; created FastAPI entrypoint and measurement API.
- Scaffolded frontend: Vite/React/TypeScript app, Redux store, initial commands/layout; added shared circuit/snapshot schemas for consistent client/server data.
- Implemented multi-lane command system: `AddGate`, `MoveGate`, `RemoveGate`, `UpdateGateParameters`, `SetQubitCount`; native drag/drop for qubit lanes; timeline linked to simulation snapshots.
- Connected frontend to Qiskit simulation/measurement endpoints; Plotly Bloch trajectory plus expectation/probability charts; measurement panel shows counts and overlays.
- Persistence: SQLite repository with `/circuits/save`, `/circuits`, `/circuits/{id}` endpoints; front-end library component allows naming/saving/loading circuits and re-running simulations.
- Measurement refinement: `/circuits/measure` accepts noise parameters, seeds; backend sampling uses Bloch projections; frontend noise sliders adjust depolarizing, amplitude, phase contributions.
- Docs: `docs/project_plan.md` updated with completed steps + stretch goals (advanced noise, export/share, AI insights). `docs/visual_spec.md` links to mock HTML (light/dark) in `frontend/public/mocks/`; `AGENTS.md` summarizes repo structure, commands, conventions.

## Next Steps (handoff)

1. **Noise modelling (stretch)** – Replace simple attenuation with full Qiskit Aer noise channels; expose purity/radius metrics in snapshots and UI.
2. **Export/share workflow** – Implement export adapters (OpenQASM 3, JSON snapshot dump, Plotly PNG) and add frontend actions for download/shareable links.
3. **Tooling & polishing** – Wire ESLint/Prettier + Vitest, align UI styling with mockups (palette search, theme toggle, gate card icons), add regression tests covering persistence & measurement flows.
4. **(Future stretch)** AI-driven insights/reporting noted in plan but intentionally deferred.

Everything else—simulation, measurement, persistence, docs/mocks—is in place, so the next engineer can focus on these finishing touches.

## 2025-10-11 – Assistant

- Extended backend simulator to optional Aer-style noise channels using density-matrix evolution; snapshots now include Bloch radius and purity metrics for UI display.
- Added export adapter with OpenQASM 3 + JSON payloads, plus new `/circuits/export` endpoint supporting shareable persistence ids.
- React client updated with noise controls tied to Redux state, export modal (download/share workflows), and purity/radius readouts.
- Added example circuit modal and catalog for instant onboarding scenarios (superposition, spiral, reset), wired into the Redux circuit loader.
- Introduced focus-qubit selection: backend partial traces snapshots/measurements via optional focus parameter; frontend exposes selector in readouts/export and routes focus through simulation, measurement, and share flows.
- Timeline scrubber now surfaces gate names/targets for each snapshot and supports keyboard navigation, relying on new snapshot metadata produced by the simulator.
- Measurement API returns per-shot samples plus statistics; frontend renders a quick histogram/expectation preview alongside counts for richer feedback.
- Snapshot service now memoizes results by (circuit, noise, focus) so repeated simulations and measurements reuse cached timelines, improving responsiveness.
- `/health` reports cache stats and the frontend dev overlay polls it, giving engineers visibility into hit/miss rates while tuning simulations.
- Wired ESLint + Prettier + Vitest tooling (configs, scripts, sample test); backend `ruff`/`mypy` config tightened for linting.
- Documented new flows in `frontend/README.md`; dev UI now auto-loads shared circuits via `?circuit=` query parameter.
- Measurement timeline strip added to Readout panel, visualising early shot outcomes for quick anomaly detection.
- Measurement response now reports longest run and switch count, allowing the UI to highlight streaky behaviour alongside the timeline.
- Export panel now emits iframe embed snippets so circuits can be dropped into external docs; app honours `?embed=1` to render a compact readout timeline.
- Gate cards now surface parameter fields per gate (supporting multi-parameter ops) with undo/redo-compatible updates.
- Timeline scrubber updated to spec: pill badges, gate labels, step counts, and improved focus states.
