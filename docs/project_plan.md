# Interactive Bloch Sphere Visualizer – Rebuild Plan

## Vision

Deliver a Quirk-inspired, production-grade Bloch sphere workbench with:

- **Front end:** React + TypeScript SPA featuring drag/drop circuit editing,
  timeline scrubbing, keyboard shortcuts, and responsive Bloch visualizations.
- **Backend:** FastAPI service backed by Qiskit for statevector simulations,
  noise models, measurement sampling, and snapshot caching.
- **Shared Protocol:** Structured snapshot payloads (statevector, density
  matrix, Bloch metrics, fidelity, noise annotations) plus OpenQASM-compatible
  circuit export.
- **Embeddable Client:** Lightweight JS widget to display saved circuits.

## Guiding Principles

1. **Teaching-first UX:** Every interaction should surface intuition (e.g.,
   Bloch arcs, expectation charts, tooltips with plain-language definitions).
2. **Responsiveness:** Sub‑100 ms scrub latency for single-qubit circuits;
   progressive refinement for heavier workloads.
3. **Extensibility:** Clear seams for adding multi-qubit visuals, parameter
   sweeps, tomography, and entanglement analytics.
4. **Traceability:** Document every architectural decision, interface contract,
   and implementation milestone (maintain `docs/devlog.md`).

## High-Level Milestones

| Milestone | Summary | Primary Deliverables |
|-----------|---------|----------------------|
| M0 – Foundation | Repo hygiene, docs, baseline CI | Project plan, devlog scaffold, TODO backlogs |
| M1 – Architecture & Design | UX wireframes, API contracts, data schemas | Figma/Excalidraw mocks, OpenAPI draft, TypeScript types |
| M2 – Backend Core | FastAPI service with circuit ingestion, snapshot engine, caching, noise hooks | `/simulate`, `/circuits` endpoints, unit tests |
| M3 – Frontend Shell | React app skeleton with layout, state store, timeline & keyboard scaffolds | Palette UI, canvas prototype, router, global theme |
| M4 – Bloch Visualization | WebGL Bloch component (Plotly/Three), linked charts, measurement axes | Sphere component, geodesic interpolation, tests |
| M5 – Measurements & Noise | Sampling workflows, histograms, noise toggles, fidelity metrics | REST integration tests, UI controls, docs |
| M6 – Export & Share | OpenQASM/JSON/PNG export, share URLs, embed client | API endpoints, frontend export modals, embed package |
| M7 – Polish & QA | Accessibility, performance tuning, CI/CD, regression tests | Audit fixes, benchmarking, deployment guide |

## Next Actions (v0.1)

~1. Stand up a `frontend/` (React + Vite) and `backend/` (FastAPI) workspace.~ ✔️
~4. Establish devlog discipline (`docs/devlog.md`) – append entry per change.~ ✔️

Upcoming:

1. ✅ Configure tooling: Prettier/ESLint, mypy/ruff, pytest, Docker compose.
2. ✅ Build gate palette drag/drop interactions and extend command catalog (controls, noise, measurement).
3. ✅ Integrate backend simulation fully (streaming updates, error handling) and display linked charts.
4. ✅ Produce Figma mockups aligned with `docs/ux_wireframe.md` / `docs/visual_spec.md` and link assets. (mock HTML provided; Figma still pending)
5. ✅ Implement measurement/noise panels and REST persistence.
6. ✅ Add focus-qubit partial trace support across backend/front-end so multi-qubit circuits can target any qubit for Bloch metrics.
7. Stretch goals (post-MVP): advanced noise modelling via Qiskit Aer channels, export/report automation, and optional AI insight generation (documented only—implementation deferred until after core release).

## Open Questions

- What’s the ceiling for live multi-qubit support in version 1 (3 qubits with focus mode vs. general N)?
- Should we port a lightweight simulator to run directly in the browser for instant feedback, falling back to server Qiskit when fidelity/noise is required?
- How aggressively do we enforce undo/redo persistence (session-only vs. shareable history)?
- Do we need auth for saved circuits in MVP, or are public share tokens sufficient?

Track answers and decisions in the devlog as the implementation progresses.
