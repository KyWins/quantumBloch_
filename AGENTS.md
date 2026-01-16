# Repository Guidelines

## Project Structure & Module Organization
- **backend/** – FastAPI hexagonal service (domain models/ports in `app/domain/`, adapters in `app/adapters/`, config in `app/config.py`).
- **frontend/** – React + TypeScript SPA (components under `src/components/`, Redux slices in `src/store/`, commands in `src/commands/`, shared DTOs in `src/types/`).
- **app/** (legacy) – Streamlit prototype retained for reference.
- **docs/** – Project plan, devlog, UX wireframes, and visual spec; HTML mockups live in `frontend/public/mocks/`.
- **tests/** – Python test suite targeting gate utilities and geometry helpers.

## Build, Test, and Development Commands
- **Backend**: from `backend/`
  - `python3 -m pip install -r requirements.txt` – install server dependencies.
  - `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000` – launch API.
  - `python3 -m pytest` – run backend unit tests.
- **Frontend**: from `frontend/`
  - `npm install` – install client dependencies.
  - `npm run dev` – start Vite dev server (defaults to http://127.0.0.1:5173).
  - `npm run lint` / `npm run test` – lint and unit test the React app (configure as tooling lands).

## Coding Style & Naming Conventions
- Python: PEP8, type hints preferred, single responsibility modules; domain classes use dataclasses (see `app/domain/models.py`).
- TypeScript: 2-space indentation, camelCase for variables/functions, PascalCase for components/commands.
- Redux slices live in `src/store/`, commands in `src/commands/` with `Command` interface implementations.
- Keep environment variables prefixed with `BLOCH_` (backend) or `VITE_` (frontend).

## Testing Guidelines
- Backend tests use `pytest`; place new tests in `tests/` matching module names (`test_<module>.py`).
- Frontend testing will adopt Vitest/Jest; mirror component structure in `src/__tests__/`.
- Ensure simulations with additional cases (noise, measurement) have deterministic seeds for regression.

## Commit & Pull Request Guidelines
- Follow conventional, descriptive messages (e.g., `feat(frontend): add Bloch plot chart` or `fix(backend): clamp measurement shots`).
- PRs should include: summary, linked issues, screenshots of UI changes (attach front-end mock comparisons where applicable), and updated docs/tests.
- Run relevant lint/test commands before opening a PR; note any failing checks with context.

## Security & Configuration Tips
- Store secrets in environment files (`backend/.env`, `frontend/.env`); never commit credentials.
- Default persistence is in-memory (`InMemoryCircuitRepository`); swap adapters carefully when introducing external stores.

