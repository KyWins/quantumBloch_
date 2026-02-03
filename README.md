# Bloch Sphere Workbench

A full-stack quantum circuit visualization tool featuring an interactive Bloch sphere, multi-qubit simulation, and real-time state evolution powered by Qiskit.

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript)
![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Qiskit](https://img.shields.io/badge/Qiskit-1.2-6929C4?logo=qiskit)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)
![CI](https://github.com/KyWins/quantumBloch_/actions/workflows/ci.yml/badge.svg)

## Features

- **Interactive Bloch Sphere** - Plotly-based 3D visualization of qubit state evolution
- **Multi-Qubit Circuit Editor** - Build circuits with drag-and-drop gate placement
- **Timeline Scrubber** - Step through simulation snapshots to observe state changes
- **Measurement Histogram** - View probability distributions and measurement statistics
- **Undo/Redo Support** - Command pattern implementation for reversible edits
- **OpenQASM Export** - Export circuits to standard quantum assembly format

## Architecture

| Layer | Technology | Description |
|-------|------------|-------------|
| Frontend | React + TypeScript + Redux | Multi-lane canvas with command-driven state management |
| Backend | FastAPI + Qiskit | Hexagonal architecture with simulation ports/adapters |
| Visualization | Plotly | Interactive 3D Bloch sphere and metric charts |

## Quick Start

### Using Docker (Recommended)

```bash
# Run the full stack
docker compose up

# Or for development with hot-reload
docker compose --profile dev up backend-dev
```

Open http://localhost:3000 (production) or http://localhost:5173 (dev)

### Manual Setup

#### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

## Project Structure

```
quantumBloch_/
├── backend/                 # FastAPI + Qiskit simulation service
│   ├── app/
│   │   ├── domain/         # Core models and business logic
│   │   ├── adapters/       # Qiskit simulator, API routes
│   │   └── schemas/        # Pydantic request/response models
│   ├── Dockerfile
│   └── tests/
├── frontend/               # React + TypeScript SPA
│   ├── src/
│   │   ├── components/     # UI components (BlochPlot, CircuitCanvas, etc.)
│   │   ├── store/          # Redux slices
│   │   └── commands/       # Command pattern for undo/redo
│   ├── Dockerfile
│   └── tests/
├── docker-compose.yml      # Container orchestration
├── .github/workflows/      # CI/CD pipeline
├── docs/                   # Project documentation
└── app/                    # Legacy Streamlit prototype (reference)
```

## Configuration

Environment variables (prefix with `BLOCH_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `BLOCH_CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `BLOCH_NOISE_ENABLED` | `false` | Enable noise simulation by default |
| `BLOCH_DEFAULT_SHOTS` | `1024` | Default measurement shots |
| `BLOCH_MAX_SHOTS` | `4096` | Maximum allowed shots |

## Development

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Backend tests
cd backend && poetry run pytest -v

# Frontend tests
cd frontend && npm run test
```

### Linting

```bash
# Backend
cd backend && poetry run ruff check app && poetry run mypy app

# Frontend
cd frontend && npm run lint
```

## Documentation

- [Project Plan](docs/project_plan.md) - Milestones and roadmap
- [Dev Log](docs/devlog.md) - Chronological development notes
- [Visual Spec](docs/visual_spec.md) - Design tokens and component specs

## License

MIT
