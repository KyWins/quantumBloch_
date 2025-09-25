# Bloch Sphere Visualizer

A sleek, single‑page Streamlit app to explore quantum gate operations and qubit evolution on the Bloch sphere using Qiskit and animated Plotly.

## Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app/main.py --server.address 127.0.0.1 --server.headless true --server.port 8501
```
Open http://127.0.0.1:8501

## Features
- Animated Bloch trajectory (Plotly) with crisp styling
- Gate sequence input (e.g., `H, Rz(pi/2), H`)
- Live final-state metrics: x, y, z, θ, φ
- Backed by Qiskit statevector simulation

## Usage Tips
- Rotation gates: `Rx(angle)`, `Ry(angle)`, `Rz(angle)`; angle supports `pi`, `pi/2`, numeric, etc.
- Useful sequences:
  - `H` (equator |+⟩)
  - `H, Rz(pi/2), H` (Y-rotation equivalent)
  - `Rx(pi/2), Rz(pi/2)`

## Optional Integrations (Advanced)
- QuTiP Bloch (not required; install later if desired)
- Cirq Web, bloch-sphere: adapters exist, but Streamlit + Plotly is the primary product

## Tech
- Python, Qiskit, Plotly, Streamlit

## License
MIT
