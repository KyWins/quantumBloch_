# UX Wireframe Summary

The high-level layout mirrors the Quirk-inspired structure discussed earlier.
This textual wireframe will guide the actual Figma design (to be produced).

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Header: Title | Theme toggle | Undo/Redo | Examples | Export | Share          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Palette (Left)        │ Circuit Canvas & Timeline (Center) │ Readouts (Right)│
│-----------------------│-------------------------------------│----------------│
│ - Search box          │  ┌───────────────┐                 │ Bloch sphere    │
│ - Categories tabs     │  │ Wire lanes    │                 │ metrics (x,y,z) │
│   • Basic             │  │ Drag/drop     │                 │ Amplitudes      │
│   • Rotations         │  │ Ghost preview │                 │ Expectation ⟨σ⟩ │
│   • Controls          │  └───────────────┘                 │ Fidelity        │
│   • Noise             │  Timeline scrubber with play/pause │ Measurement UI  │
│   • Measurement       │  step markers, brushed selections │ Noise toggles   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Key Interaction Zones

- **Palette:** drag/drop, keyboard shortcuts, inline tooltips.
- **Canvas:** horizontal wires, step ruler, selection state, multi-select handles.
- **Scrubber:** play/pause, speed dropdown, timeline brushing, heatline overlay for sweeps.
- **Right Panel Tabs:**
  - Gate Properties (sliders/inputs, symbol binding).
  - State Readouts (Bloch + amplitudes + expectation values).
  - Measurement lab (basis selection, shot sampling, histograms).

### Next Steps
- Translate this textual layout into Figma frames.
- Annotate component boundaries matching the React component structure created earlier.
- Validate accessibility (focus order, keyboard operations) during detailed design.

## Design Decisions (Draft)

- **Color & Theme:** Base palette aligns with Tailwind slate/sky hues (see current CSS) with plans for light/dark toggle; maintain WCAG AA contrast, especially on timeline badges and action buttons.
- **Typography:** Continue using Inter/system stack for clarity; primary hierarchy via weight and size (~20px header, 16px body).
- **Component Boundaries:** Palette (left) maps to `<CommandPalette>`; canvas lane to `<CircuitCanvas>`; timeline remains `<TimelineScrubber>`; readouts split into tabs to be implemented (`ReadoutPanel`).
- **Interactions:** Buttons transition to custom React-dnd interactions later; interim click-to-add ensures command pipeline works before investing in canvas drag/drop.
- **Icons/Feedback:** Plan to integrate Lucide or Heroicons for removal/actions, with tooltip overlays explaining keyboard shortcuts.

These decisions will guide upcoming Figma mockups; once created, link exported images/screens here.

See also `docs/visual_spec.md` for full color/spacing tokens and component specs.
