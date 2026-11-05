# HypothesisLab AI — Frontend

This is the frontend client for **HypothesisLab AI**, a scientific hypothesis and multi-agent research discovery platform.

Developed in React + Vite, Tailwind CSS, Watermelon UI architecture, DaisyUI, Motion, Recharts, and React Flow (@xyflow/react).

---

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK=true
```

- When `VITE_USE_MOCK=true`: Runs with the built-in scientific mock adapter for offline preview and UI development.
- When `VITE_USE_MOCK=false`: Connects directly to the Python FastAPI backend.

### 3. Start Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`.

### 4. Build for Production
```bash
npm run build
```

---

## Application Routes

- `/` — Research Creation & Recent Workspaces.
- `/research/:projectId` — Research Workspace (with internal tabs: Overview, Sources & Evidence, Comparative Analysis, Research Discoveries, Hypotheses, Experiments).

---

## Teammate Backend Integration

See [`API_CONTRACT.md`](./API_CONTRACT.md) for the exact REST endpoints, request payloads, multipart upload contracts, and JSON response models required by the FastAPI service.

