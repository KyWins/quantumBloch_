# Visual Design Specification (v0.1)

> NOTE: High-fidelity mockups are being tracked in Figma (workspace link will be
> added here once assets are exported). This document captures all decisions,
> component specs, and styling tokens so the Figma handoff is unambiguous.

## Layout Overview

| Region            | Spec                                                                        |
|-------------------|-----------------------------------------------------------------------------|
| Header            | 72px height, slate-900 background, white text, Inter 20pt bold, icon set TBD |
| Left Palette      | 280px width, scrollable categories with sticky category header tabs          |
| Center Canvas     | Flexible width. Each wire lane: 56px label + 1fr content. Background `#F8FAFF` with dashed drop targets. 16px gap between lanes |
| Timeline          | 56px height below canvas, solid white, timeline badges 28x28 pill buttons     |
| Right Readouts    | 320px width, tabbed interface (State / Measurement / Export). Plot area 320x320, charts stacked below |

See `docs/ux_wireframe.md` for ASCII wireframe and interaction annotations.

## Color & Typography Tokens

| Token              | Value       | Usage                                               |
|--------------------|-------------|-----------------------------------------------------|
| `color.bg`         | `#F5F6FA`   | App background                                      |
| `color.panel`      | `#FFFFFF`   | Content panels, cards                               |
| `color.accent`     | `#2563EB`   | Active timeline step, primary buttons               |
| `color.accent-muted` | `#E0F2FE` | Inactive timeline badges, drop-zone highlights      |
| `color.warning`    | `#F87171`   | Gate remove button, destructive actions             |
| `color.success`    | `#22C55E`   | Measurement overlay highlight                       |
| `font.primary`     | `Inter`, sans-serif | All text                                     |
| Heading sizes      | 24 / 18 / 16 / 14 px | H1/H2/H3/body                                  |

## Component Specs

### Header
- Height 72px, horizontal padding 32px.
- Title left-aligned. Action buttons grouped (Undo, Redo, Examples, Export, Theme toggle) with 12px gap.
- Buttons: 36px height, pill corners (18px radius), hover lighten 8%.

### Gate Palette
- Search bar (planned, currently not implemented) 36px height, radius 10px.
- Categories displayed as collapsible sections.
- Gate buttons 64x40 with subtle shadow; drag handles appear on hover.
- Control/Target inputs stacked with qubit count input.

### Canvas
- Each lane: label (semi-bold 16px) + drop-zone container.
- Drop-zone width 6px, gradient highlight on drag over (blue → transparent).
- Gate card: grid layout `[index | name | target text | parameter (optional) | remove button]` with 12px vertical padding.
- Parameter field uses inline numeric input with unit badge (“rad” for rotations, “p” for probabilities).

### Readout Panel
- Tabs (State / Measurement / Export) 44px height, underline on active.
- Plotly Bloch plot sized to 320x320; below it KPI grid (x,y,z, |0⟩, |1⟩, measurement probabilities).
- Measurement controls: basis dropdown, shot input, “Sample” button, result chip.
- Future charts: sparkline area height 120px each (⟨X⟩, ⟨Y⟩, ⟨Z⟩, Fidelity) with shared x-axis bound to snapshots.

## Interaction States

- **Drag**: Palette button drag shows ghost of gate label; drop-zone glows accent color.
- **Undo/Redo**: Buttons disabled when stacks empty; tooltip reveals shortcut (⌘Z / ⇧⌘Z).
- **Measurement**: Sampling triggers toast “Sampled basis X (shots: n)”; overlay marker drops onto Bloch sphere.
- **Timeline**: Active step badge uses primary color; on hover show tooltip “Step N – Gate Name”.

## Mockups & Figma Tracking

- File: `Bloch Sphere Workbench – v0.1` (Figma workspace).
  - Page 1: Light theme desktop
  - Page 2: Dark theme desktop
  - Page 3: Component states (drag/drop, measurement)
- Static HTML mockups (rendered from the spec) live in `frontend/public/mocks/`:
  - [Light theme](../frontend/public/mocks/light.html)
  - [Dark theme](../frontend/public/mocks/dark.html)
- When the Figma file is shared publicly, add the share URL here.

## Outstanding Visual Tasks

- Dark theme variants (mirror tokens with 8% contrast adjustments).
- Iconography: Evaluate Lucide vs Heroicons; ensure consistent stroke weight.
- Animations: micro fade-in for lanes, scale pulse on drop success, timeline step smooth scroll.
- Accessibility pass: contrast verification, focus rings, ARIA labels for Plotly embed.
